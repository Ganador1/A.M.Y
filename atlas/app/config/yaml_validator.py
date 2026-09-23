"""
Pydantic schemas para validar archivos de configuración YAML de AXIOM
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import yaml
from pathlib import Path

# Schema para agents.yaml
class AgentParams(BaseModel):
    temperature: float = Field(ge=0.0, le=2.0, description="Temperature for text generation")
    max_new_tokens: int = Field(ge=1, le=4096, description="Maximum new tokens to generate")

class AgentRole(BaseModel):
    description: str = Field(min_length=10, description="Role description")
    model: str = Field(min_length=1, description="Model identifier")
    params: AgentParams

class AgentsConfig(BaseModel):
    roles: Dict[str, AgentRole]
    domain_overrides: Dict[str, Any] = Field(default_factory=dict)

# Schema para models.yaml
class ModelInfo(BaseModel):
    provider: str = Field(min_length=1, description="Model provider")
    family: str = Field(min_length=1, description="Model family")
    size: str = Field(min_length=1, description="Model size")
    capability: str = Field(min_length=1, description="Model capability")

class ModelsConfig(BaseModel):
    models: Dict[str, ModelInfo]

# Schema para plausibility.yaml
class ComponentWeights(BaseModel):
    title_length: float = Field(ge=0.0, le=10.0)
    description_length: float = Field(ge=0.0, le=10.0)
    variables_coverage: float = Field(ge=0.0, le=10.0)
    quant_elements: float = Field(ge=0.0, le=10.0)
    assumptions_present: float = Field(ge=0.0, le=10.0)
    duplication_penalty: float = Field(ge=0.0, le=10.0)

class DomainWeights(BaseModel):
    biology: float = Field(ge=0.0, le=2.0)
    chemistry: float = Field(ge=0.0, le=2.0)
    physics: float = Field(ge=0.0, le=2.0)
    materials: float = Field(ge=0.0, le=2.0)
    medicine: float = Field(ge=0.0, le=2.0)

class EvidenceAdjustment(BaseModel):
    enabled: bool
    alpha: float = Field(ge=0.0, le=1.0)
    support_score_weight: float = Field(ge=0.0, le=1.0)

class Thresholds(BaseModel):
    high: float = Field(ge=0.0, le=1.0)
    medium: float = Field(ge=0.0, le=1.0)

class PlausibilityConfig(BaseModel):
    component_weights: ComponentWeights
    domain_weights: DomainWeights
    evidence_adjustment: EvidenceAdjustment
    thresholds: Thresholds

# Schema para policy_engine_config.yaml
class PolicyEngineConfig(BaseModel):
    # Este schema se puede expandir según la estructura real del archivo
    policies: Dict[str, Any] = Field(default_factory=dict)

# Schema para ethics_policy.yaml
class EthicsPolicyConfig(BaseModel):
    # Este schema se puede expandir según la estructura real del archivo
    policies: Dict[str, Any] = Field(default_factory=dict)

# Schema para improvements_config.yaml
class ImprovementsConfig(BaseModel):
    # Este schema se puede expandir según la estructura real del archivo
    improvements: Dict[str, Any] = Field(default_factory=dict)

# Schema para prompts/hypothesis_agent.yaml
class HypothesisAgentConfig(BaseModel):
    # Este schema se puede expandir según la estructura real del archivo
    prompts: Dict[str, Any] = Field(default_factory=dict)

class YAMLConfigValidator:
    """Validador para archivos de configuración YAML"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.schemas = {
            'agents.yaml': AgentsConfig,
            'models.yaml': ModelsConfig,
            'plausibility.yaml': PlausibilityConfig,
            'policy_engine_config.yaml': PolicyEngineConfig,
            'ethics_policy.yaml': EthicsPolicyConfig,
            'improvements_config.yaml': ImprovementsConfig,
            'prompts/hypothesis_agent.yaml': HypothesisAgentConfig,
        }
    
    def validate_file(self, filename: str) -> tuple[bool, str, Any]:
        """
        Valida un archivo YAML específico
        Returns: (is_valid, error_message, validated_data)
        """
        if filename not in self.schemas:
            return False, f"Schema no definido para {filename}", None
        
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            return False, f"Archivo no encontrado: {file_path}", None
        
        try:
            # Cargar YAML
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Validar con Pydantic
            schema_class = self.schemas[filename]
            validated_data = schema_class(**data)
            
            return True, "Validación exitosa", validated_data
            
        except yaml.YAMLError as e:
            return False, f"Error de sintaxis YAML: {e}", None
        except Exception as e:
            return False, f"Error de validación: {e}", None
    
    def validate_all(self) -> Dict[str, tuple[bool, str, Any]]:
        """
        Valida todos los archivos YAML de configuración
        Returns: Dict con resultados de validación
        """
        results = {}
        
        for filename in self.schemas.keys():
            print(f"🔍 Validando {filename}...")
            is_valid, error_msg, data = self.validate_file(filename)
            
            if is_valid:
                print(f"✅ {filename}: Validación exitosa")
            else:
                print(f"❌ {filename}: {error_msg}")
            
            results[filename] = (is_valid, error_msg, data)
        
        return results
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de la validación"""
        results = self.validate_all()
        
        total_files = len(results)
        valid_files = sum(1 for is_valid, _, _ in results.values() if is_valid)
        invalid_files = total_files - valid_files
        
        return {
            'total_files': total_files,
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'success_rate': (valid_files / total_files) * 100 if total_files > 0 else 0,
            'results': results
        }

def validate_yaml_configs():
    """Función principal para validar configuraciones YAML"""
    config_dir = Path("./config")
    validator = YAMLConfigValidator(config_dir)
    
    print("🚀 Iniciando validación de archivos YAML de configuración...")
    print("=" * 60)
    
    summary = validator.get_validation_summary()
    
    print(f"\n📊 Resumen de validación:")
    print(f"   - Total de archivos: {summary['total_files']}")
    print(f"   - Archivos válidos: {summary['valid_files']}")
    print(f"   - Archivos con errores: {summary['invalid_files']}")
    print(f"   - Tasa de éxito: {summary['success_rate']:.1f}%")
    
    if summary['invalid_files'] > 0:
        print(f"\n❌ Archivos con errores:")
        for filename, (is_valid, error_msg, _) in summary['results'].items():
            if not is_valid:
                print(f"   - {filename}: {error_msg}")
    
    return summary

if __name__ == "__main__":
    validate_yaml_configs()
