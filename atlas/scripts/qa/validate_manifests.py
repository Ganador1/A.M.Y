#!/usr/bin/env python
"""Validador de manifests de modelos y artefactos.

Uso:
  python scripts/validate_manifests.py --models-dir models --schema models/manifest.schema.json --output reports/manifest_validation_report.json

Comportamiento:
- Busca archivos *.manifest.json o manifest.json dentro de subdirectorios.
- Si existe schema (JSON Schema draft 7+), valida cada manifest.
- Calcula hash SHA-256 de cada manifest y lo añade al reporte.
- Devuelve código 0 si todas las validaciones pasan, 1 si hay errores estructurales.
- Si no hay schema, genera advertencia pero no falla (modo permissive inicial).
"""
from __future__ import annotations
import argparse
import json
import sys
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import jsonschema  # type: ignore
except ImportError:  # pragma: no cover
    jsonschema = None  # fallback: sin validación formal


def load_schema(schema_path: Path) -> Dict[str, Any] | None:
    if not schema_path.exists():
        return None
    with schema_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_manifests(models_dir: Path) -> List[Path]:
    primary = list(models_dir.rglob("*.manifest.json"))
    secondary = [p for p in models_dir.rglob("manifest.json") if p not in primary]
    return primary + secondary


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

# helper functions for payload hashing (exclude signatures)

def compute_payload_bytes(manifest: Dict[str, Any]) -> bytes:
    clone = {k: v for k, v in manifest.items() if k != "signatures"}
    return json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()


def sha256_payload(manifest: Dict[str, Any]) -> str:
    return hashlib.sha256(compute_payload_bytes(manifest)).hexdigest()


def validate_manifest(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if jsonschema is None:
        return ["jsonschema no instalado - validación estructural omitida"]
    validator = jsonschema.Draft7Validator(schema)  # type: ignore[attr-defined]
    for err in validator.iter_errors(data):
        path_str = ".".join([str(x) for x in err.path]) or "<root>"
        errors.append(f"{path_str}: {err.message}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models-dir", default="models", help="Directorio base de modelos/artefactos")
    parser.add_argument("--schema", default="models/manifest.schema.json", help="Ruta al JSON Schema de manifest")
    parser.add_argument("--output", default="reports/manifest_validation_report.json", help="Archivo JSON de reporte")
    parser.add_argument("--fail-on-warn", action="store_true", help="Falla si no hay schema o jsonschema no instalado")
    parser.add_argument("--fail-on-error", action="store_true", help="Falla si existe cualquier manifest inválido o error estructural (gate estricto)")
    return parser.parse_args()


def load_manifest(path: Path) -> Tuple[Dict[str, Any] | None, str | None]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f), None
    except (OSError, json.JSONDecodeError) as e:  # pragma: no cover
        return None, str(e)


def build_report(manifests: List[Path], schema: Dict[str, Any] | None) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "schema_present": schema is not None,
        "jsonschema_available": jsonschema is not None,
        "total_manifests": len(manifests),
        "results": [],
        "errors": [],
        "warnings": [],
    }
    if schema is None:
        report["warnings"].append("Schema ausente")
    if jsonschema is None:
        report["warnings"].append("jsonschema no instalado")
    for mf in manifests:
        data, err = load_manifest(mf)
        if err:
            report["errors"].append(f"{mf}: {err}")
            continue
        errors_list: List[str] = []
        if data and schema and jsonschema is not None:
            errors_list = validate_manifest(data, schema)  # type: ignore[arg-type]
        entry = {
            "path": str(mf),
            "file_sha256": sha256_file(mf),
            "payload_sha256": sha256_payload(data) if data else None,
            "stored_manifest_sha256": ((data or {}).get("hashes") or {}).get("manifest_sha256") if data else None,
            "manifest_hash_matches": ((((data or {}).get("hashes") or {}).get("manifest_sha256") == sha256_payload(data)) if data else False),
            "errors": errors_list,
            "valid": not errors_list,
            "artifact_id": (data or {}).get("id") or (data or {}).get("name"),
            "version": (data or {}).get("version"),
        }
        report["results"].append(entry)
    return report


def finalize_report(report: Dict[str, Any], output_path: Path, fail_on_warn: bool, fail_on_error: bool) -> int:
    structural_errors = report["errors"]
    manifest_errors = [r for r in report["results"] if not r["valid"]]
    exit_code = 0
    if fail_on_error and (structural_errors or manifest_errors):
        exit_code = 1
    if (not report["schema_present"] or not report["jsonschema_available"]) and fail_on_warn:
        exit_code = 1
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps({
        "summary": {
            "schema_present": report["schema_present"],
            "jsonschema_available": report["jsonschema_available"],
            "total": report["total_manifests"],
            "invalid": len(manifest_errors),
            "structural_errors": len(structural_errors),
            "warnings": len(report["warnings"]),
        },
        "output": str(output_path)
    }, indent=2, ensure_ascii=False))
    return exit_code


def main() -> int:
    args = parse_args()
    models_dir = Path(args.models_dir)
    schema_path = Path(args.schema)
    schema = load_schema(schema_path)
    manifests = iter_manifests(models_dir)
    report = build_report(manifests, schema)
    return finalize_report(report, Path(args.output), args.fail_on_warn, args.fail_on_error)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())


# new helper functions for payload hashing (exclude signatures)

def compute_payload_bytes(manifest: Dict[str, Any]) -> bytes:
    clone = {k: v for k, v in manifest.items() if k != "signatures"}
    return json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()


def sha256_payload(manifest: Dict[str, Any]) -> str:
    return hashlib.sha256(compute_payload_bytes(manifest)).hexdigest()
