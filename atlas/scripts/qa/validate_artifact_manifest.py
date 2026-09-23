#!/usr/bin/env python3
"""
Artifact Manifest Validator CLI - AXIOM META 4

Validador de línea de comandos para manifiestos de artefactos.
Utiliza el esquema JSON y modelos Pydantic para validación completa.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
import os

# Agregar el directorio padre al path para importar app
sys.path.append(str(Path(__file__).parent.parent))

try:
    from app.models.artifacts.manifest_models import ArtifactManifest, ArtifactItem
    from app.logging_config import logger
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("⚠️  Modelos Pydantic no disponibles. Usando validación básica.")

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("⚠️  jsonschema no disponible. Instalar con: pip install jsonschema")


class ManifestValidator:
    """Validador de manifiestos de artefactos"""
    
    def __init__(self, schema_path: Optional[Path] = None):
        self.schema_path = schema_path or Path(__file__).parent.parent / "models" / "manifest.schema.json"
        self.schema = self._load_schema()
        
    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """Cargar esquema JSON"""
        if not self.schema_path.exists():
            print(f"❌ Esquema no encontrado: {self.schema_path}")
            return None
            
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error cargando esquema: {e}")
            return None
    
    def validate_manifest_file(self, manifest_path: Path) -> Dict[str, Any]:
        """Validar archivo de manifiesto"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "manifest_path": str(manifest_path),
            "validation_methods": []
        }
        
        if not manifest_path.exists():
            result["errors"].append(f"Archivo no encontrado: {manifest_path}")
            return result
        
        # Cargar manifiesto
        try:
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
        except json.JSONDecodeError as e:
            result["errors"].append(f"JSON inválido: {e}")
            return result
        except Exception as e:
            result["errors"].append(f"Error leyendo archivo: {e}")
            return result
        
        # Validación con JSONSchema
        if JSONSCHEMA_AVAILABLE and self.schema:
            schema_result = self._validate_with_jsonschema(manifest_data)
            result["errors"].extend(schema_result["errors"])
            result["warnings"].extend(schema_result["warnings"])
            result["validation_methods"].append("jsonschema")
        
        # Validación con Pydantic
        if PYDANTIC_AVAILABLE:
            pydantic_result = self._validate_with_pydantic(manifest_data)
            result["errors"].extend(pydantic_result["errors"])
            result["warnings"].extend(pydantic_result["warnings"])
            result["validation_methods"].append("pydantic")
        
        # Validación de integridad de archivos
        integrity_result = self._validate_file_integrity(manifest_data, manifest_path.parent)
        result["errors"].extend(integrity_result["errors"])
        result["warnings"].extend(integrity_result["warnings"])
        result["validation_methods"].append("file_integrity")
        
        # Validación de HMAC si está presente
        if "hashes" in manifest_data and "manifest_sha256" in manifest_data["hashes"]:
            hmac_result = self._validate_manifest_hash(manifest_data)
            result["errors"].extend(hmac_result["errors"])
            result["warnings"].extend(hmac_result["warnings"])
            result["validation_methods"].append("manifest_hash")
        
        result["valid"] = len(result["errors"]) == 0
        return result
    
    def _validate_with_jsonschema(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar con JSONSchema"""
        result = {"errors": [], "warnings": []}
        
        try:
            jsonschema.validate(instance=manifest_data, schema=self.schema)
        except jsonschema.ValidationError as e:
            result["errors"].append(f"JSONSchema: {e.message} (path: {'.'.join(str(p) for p in e.path)})")
        except jsonschema.SchemaError as e:
            result["errors"].append(f"Esquema inválido: {e.message}")
        except Exception as e:
            result["errors"].append(f"Error en validación JSONSchema: {e}")
        
        return result
    
    def _validate_with_pydantic(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar con modelos Pydantic"""
        result = {"errors": [], "warnings": []}
        
        try:
            manifest = ArtifactManifest.from_dict(manifest_data)
            
            # Validaciones adicionales específicas de Pydantic
            if len(manifest.artifacts) == 0:
                result["warnings"].append("Manifiesto sin artefactos")
            
            # Verificar unicidad de paths
            paths = [artifact.path for artifact in manifest.artifacts]
            if len(paths) != len(set(paths)):
                result["errors"].append("Paths de artefactos duplicados")
            
            # Verificar que hay al menos un modelo
            model_artifacts = manifest.get_artifacts_by_type("model")
            if not model_artifacts:
                result["warnings"].append("No se encontraron artefactos de tipo 'model'")
            
        except Exception as e:
            result["errors"].append(f"Pydantic: {e}")
        
        return result
    
    def _validate_file_integrity(self, manifest_data: Dict[str, Any], base_path: Path) -> Dict[str, Any]:
        """Validar integridad de archivos referenciados"""
        result = {"errors": [], "warnings": []}
        
        artifacts = manifest_data.get("artifacts", [])
        
        for artifact in artifacts:
            artifact_path = base_path / artifact["path"]
            expected_hash = artifact["hash_sha256"]
            
            if not artifact_path.exists():
                result["errors"].append(f"Archivo no encontrado: {artifact['path']}")
                continue
            
            # Calcular hash SHA256
            try:
                actual_hash = self._calculate_file_hash(artifact_path)
                
                if actual_hash != expected_hash:
                    result["errors"].append(
                        f"Hash mismatch en {artifact['path']}: "
                        f"esperado {expected_hash}, actual {actual_hash}"
                    )
                
                # Verificar tamaño si está especificado
                if "size_bytes" in artifact:
                    actual_size = artifact_path.stat().st_size
                    expected_size = artifact["size_bytes"]
                    
                    if actual_size != expected_size:
                        result["warnings"].append(
                            f"Tamaño diferente en {artifact['path']}: "
                            f"esperado {expected_size}, actual {actual_size}"
                        )
                        
            except Exception as e:
                result["errors"].append(f"Error calculando hash para {artifact['path']}: {e}")
        
        return result
    
    def _validate_manifest_hash(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar hash del manifiesto"""
        result = {"errors": [], "warnings": []}
        
        try:
            expected_hash = manifest_data["hashes"]["manifest_sha256"]
            
            # Crear copia sin hashes para calcular
            manifest_copy = manifest_data.copy()
            manifest_copy.pop("hashes", None)
            manifest_copy.pop("signatures", None)  # También excluir firmas
            
            # Calcular hash
            manifest_json = json.dumps(manifest_copy, sort_keys=True, ensure_ascii=False)
            actual_hash = hashlib.sha256(manifest_json.encode()).hexdigest()
            
            if actual_hash != expected_hash:
                result["errors"].append(
                    f"Hash del manifiesto inválido: esperado {expected_hash}, actual {actual_hash}"
                )
                
        except KeyError as e:
            result["warnings"].append(f"Campo de hash faltante: {e}")
        except Exception as e:
            result["errors"].append(f"Error validando hash del manifiesto: {e}")
        
        return result
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcular hash SHA256 de un archivo"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def validate_directory(self, directory: Path, pattern: str = "*.manifest.json") -> Dict[str, Any]:
        """Validar todos los manifiestos en un directorio"""
        results = {
            "directory": str(directory),
            "pattern": pattern,
            "manifests": [],
            "summary": {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "errors": 0,
                "warnings": 0
            }
        }
        
        if not directory.exists():
            results["error"] = f"Directorio no encontrado: {directory}"
            return results
        
        # Buscar archivos de manifiesto
        manifest_files = list(directory.glob(pattern))
        
        for manifest_file in manifest_files:
            validation_result = self.validate_manifest_file(manifest_file)
            results["manifests"].append(validation_result)
            
            results["summary"]["total"] += 1
            if validation_result["valid"]:
                results["summary"]["valid"] += 1
            else:
                results["summary"]["invalid"] += 1
            
            results["summary"]["errors"] += len(validation_result["errors"])
            results["summary"]["warnings"] += len(validation_result["warnings"])
        
        return results


def print_validation_result(result: Dict[str, Any], verbose: bool = False):
    """Imprimir resultado de validación"""
    manifest_path = result["manifest_path"]
    
    if result["valid"]:
        print(f"✅ {manifest_path}")
        if verbose and result["warnings"]:
            for warning in result["warnings"]:
                print(f"   ⚠️  {warning}")
    else:
        print(f"❌ {manifest_path}")
        for error in result["errors"]:
            print(f"   🚫 {error}")
        
        if verbose and result["warnings"]:
            for warning in result["warnings"]:
                print(f"   ⚠️  {warning}")
    
    if verbose:
        methods = ", ".join(result["validation_methods"])
        print(f"   📋 Métodos: {methods}")


def print_directory_summary(results: Dict[str, Any]):
    """Imprimir resumen de validación de directorio"""
    summary = results["summary"]
    
    print(f"\n📊 Resumen de validación:")
    print(f"   Directorio: {results['directory']}")
    print(f"   Patrón: {results['pattern']}")
    print(f"   Total: {summary['total']}")
    print(f"   ✅ Válidos: {summary['valid']}")
    print(f"   ❌ Inválidos: {summary['invalid']}")
    print(f"   🚫 Errores: {summary['errors']}")
    print(f"   ⚠️  Advertencias: {summary['warnings']}")


def main():
    parser = argparse.ArgumentParser(
        description="Validador de manifiestos de artefactos AXIOM META 4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Validar un manifiesto específico
  python validate_artifact_manifest.py models/plausibility_v4_rf.manifest.json
  
  # Validar todos los manifiestos en un directorio
  python validate_artifact_manifest.py --directory models/
  
  # Validar con patrón específico
  python validate_artifact_manifest.py --directory models/ --pattern "*.manifest.json"
  
  # Modo verbose
  python validate_artifact_manifest.py --verbose models/plausibility_v4_rf.manifest.json
        """
    )
    
    parser.add_argument(
        "manifest",
        nargs="?",
        help="Archivo de manifiesto a validar"
    )
    
    parser.add_argument(
        "--directory", "-d",
        type=Path,
        help="Directorio con manifiestos a validar"
    )
    
    parser.add_argument(
        "--pattern", "-p",
        default="*.manifest.json",
        help="Patrón de archivos a buscar (default: *.manifest.json)"
    )
    
    parser.add_argument(
        "--schema", "-s",
        type=Path,
        help="Ruta al esquema JSON (default: models/manifest.schema.json)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mostrar información detallada"
    )
    
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Salida en formato JSON"
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.manifest and not args.directory:
        parser.error("Debe especificar un manifiesto o un directorio")
    
    if args.manifest and args.directory:
        parser.error("No puede especificar tanto manifiesto como directorio")
    
    # Crear validador
    validator = ManifestValidator(args.schema)
    
    if not validator.schema and JSONSCHEMA_AVAILABLE:
        print("⚠️  No se pudo cargar el esquema JSON")
    
    # Ejecutar validación
    if args.manifest:
        # Validar archivo individual
        manifest_path = Path(args.manifest)
        result = validator.validate_manifest_file(manifest_path)
        
        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            print_validation_result(result, args.verbose)
        
        sys.exit(0 if result["valid"] else 1)
        
    else:
        # Validar directorio
        results = validator.validate_directory(args.directory, args.pattern)
        
        if args.json_output:
            print(json.dumps(results, indent=2))
        else:
            for manifest_result in results["manifests"]:
                print_validation_result(manifest_result, args.verbose)
            
            print_directory_summary(results)
        
        sys.exit(0 if results["summary"]["invalid"] == 0 else 1)


if __name__ == "__main__":
    main()