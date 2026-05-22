"""
Ethics Policy Management - Carga y gestión de políticas YAML
"""

import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class PolicyThresholds(BaseModel):
    """Umbrales de scoring para niveles de riesgo"""
    low: int = 3
    medium: int = 7
    high: int = 11
    critical: int = 15


class PolicyDomainWeights(BaseModel):
    """Pesos por dominio científico"""
    # Matemáticas y computación (bajo riesgo)
    algebra: int = 0
    calculus: int = 0
    statistics: int = 1
    optimization: int = 1
    cryptography: int = 2
    
    # Física y química (riesgo bajo-medio)
    quantum_physics: int = 3
    computational_chemistry: int = 4
    plasma_physics: int = 5
    quantum_chemistry: int = 6
    
    # Medicina y biología (riesgo medio-alto)
    medical_imaging: int = 6
    computational_biology: int = 7
    neuro_simulation: int = 7
    clinical_validation: int = 7
    molecular_dynamics: int = 7
    
    # Biología avanzada (riesgo alto)
    genomics: int = 8
    metabolic_networks: int = 8
    systems_biology: int = 8
    
    # Alto riesgo dual-use
    synthetic_biology: int = 9
    biosecurity_assessment: int = 10
    gain_of_function: int = 10


class PolicyKeywords(BaseModel):
    """Keywords bloqueadas y sensibles"""
    blocked_keywords: List[str] = Field(default_factory=lambda: [
        "bioweapon", "dual-use weaponization", "gain-of-function pathogen",
        "weaponized virus", "chemical weapon synthesis", "explosive device design",
        "unauthorized human experimentation"
    ])
    
    sensitive_keywords: Dict[str, List[str]] = Field(default_factory=lambda: {
        "biology": ["pathogen", "virus", "bacteria", "infection", "biosafety", "contagion", "epidemic"],
        "chemistry": ["toxic", "hazard", "explosive", "flammable", "carcinogenic", "mutagenic"],
        "clinical": ["patient", "clinical trial", "diagnosis", "treatment", "human subject"],
        "materials": ["nuclear", "radioactive", "fissile"]
    })


class PolicyDataSensitivity(BaseModel):
    """Pesos por sensibilidad de datos"""
    none: int = 0
    low: int = 1
    medium: int = 3
    high: int = 5
    critical: int = 8


class PolicyIntentWeights(BaseModel):
    """Pesos por intención declarada"""
    research: int = 0
    education: int = 0
    commercial: int = 1
    defense: int = 3
    dual_use: int = 5


class EthicsPolicy(BaseModel):
    """Política completa de ética"""
    version: str = "1.0"
    thresholds: PolicyThresholds = Field(default_factory=PolicyThresholds)
    domain_weights: PolicyDomainWeights = Field(default_factory=PolicyDomainWeights)
    signature_levels: List[str] = Field(default_factory=lambda: ["HIGH", "CRITICAL"])
    keywords: PolicyKeywords = Field(default_factory=PolicyKeywords)
    data_sensitivity_weights: PolicyDataSensitivity = Field(default_factory=PolicyDataSensitivity)
    intent_weights: PolicyIntentWeights = Field(default_factory=PolicyIntentWeights)


class EthicsPolicyManager:
    """Gestor de políticas de ética con hot-reload"""
    
    def __init__(self, policy_path: Optional[str] = None):
        self.policy_path = policy_path or "config/ethics_policy.yaml"
        self._policy: Optional[EthicsPolicy] = None
        self._last_modified: Optional[float] = None
        self._load_policy()
    
    def _load_policy(self) -> None:
        """Cargar política desde archivo YAML"""
        try:
            policy_file = Path(self.policy_path)
            if not policy_file.exists():
                logger.warning(f"Policy file not found: {self.policy_path}, using defaults")
                self._policy = EthicsPolicy()
                return
            
            # Verificar si el archivo ha cambiado
            current_modified = policy_file.stat().st_mtime
            if self._last_modified == current_modified and self._policy is not None:
                return
            
            with open(policy_file, 'r', encoding='utf-8') as f:
                policy_data = yaml.safe_load(f)
            
            # Validar estructura
            self._policy = EthicsPolicy(**policy_data)
            self._last_modified = current_modified
            
            logger.info(f"Ethics policy loaded from {self.policy_path}")
            
        except Exception as e:
            logger.error(f"Error loading ethics policy: {e}")
            # Fallback a política por defecto
            self._policy = EthicsPolicy()
    
    def get_policy(self) -> EthicsPolicy:
        """Obtener política actual (con hot-reload)"""
        self._load_policy()  # Verificar cambios
        return self._policy
    
    def get_domain_weight(self, domain: str) -> int:
        """Obtener peso de un dominio específico"""
        policy = self.get_policy()
        domain_weights = policy.domain_weights.dict()
        return domain_weights.get(domain, 1)  # Default weight = 1
    
    def get_data_sensitivity_weight(self, sensitivity: str) -> int:
        """Obtener peso por sensibilidad de datos"""
        policy = self.get_policy()
        weights = policy.data_sensitivity_weights.dict()
        return weights.get(sensitivity, 0)
    
    def get_intent_weight(self, intent: str) -> int:
        """Obtener peso por intención declarada"""
        policy = self.get_policy()
        weights = policy.intent_weights.dict()
        return weights.get(intent, 0)
    
    def get_blocked_keywords(self) -> List[str]:
        """Obtener keywords bloqueadas"""
        policy = self.get_policy()
        return policy.keywords.blocked_keywords
    
    def get_sensitive_keywords(self) -> Dict[str, List[str]]:
        """Obtener keywords sensibles por categoría"""
        policy = self.get_policy()
        return policy.keywords.sensitive_keywords
    
    def get_signature_levels(self) -> List[str]:
        """Obtener niveles que requieren firma"""
        policy = self.get_policy()
        return policy.signature_levels
    
    def get_thresholds(self) -> PolicyThresholds:
        """Obtener umbrales de scoring"""
        policy = self.get_policy()
        return policy.thresholds
    
    def export_policy(self) -> Dict[str, Any]:
        """Exportar política efectiva como dict"""
        policy = self.get_policy()
        return policy.dict()
    
    def validate_policy(self) -> List[str]:
        """Validar política y retornar errores"""
        errors = []
        try:
            policy = self.get_policy()
            
            # Validar umbrales
            thresholds = policy.thresholds
            if not (thresholds.low < thresholds.medium < thresholds.high < thresholds.critical):
                errors.append("Thresholds must be in ascending order: low < medium < high < critical")
            
            # Validar que no hay keywords bloqueadas vacías
            if not policy.keywords.blocked_keywords:
                errors.append("Blocked keywords list cannot be empty")
            
            # Validar que hay al menos un nivel de firma
            if not policy.signature_levels:
                errors.append("At least one signature level must be defined")
            
        except Exception as e:
            errors.append(f"Policy validation error: {e}")
        
        return errors


# Instancia global
policy_manager = EthicsPolicyManager()
