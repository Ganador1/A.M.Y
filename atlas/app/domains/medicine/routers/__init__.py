"""
🏥 Routers del Dominio Médico - AXIOM v4.1

Este módulo exporta todos los routers del dominio médico, tanto el router
unificado como los routers especializados para compatibilidad.

Routers disponibles:
- unified_medical_router: Router principal unificado para todos los servicios médicos
- alphafold3_router: Router especializado para predicción de estructuras proteicas
- clinicalbert_router: Router especializado para procesamiento de texto clínico
- personalized_medicine_router: Router especializado para farmacogenómica
- legacy_api_router: Router de API legacy para compatibilidad

Uso recomendado:
    from app.domains.medicine.routers import unified_medical_router

    # Usar el router unificado para nuevas implementaciones
    app.include_router(unified_medical_router.router)

Uso legacy (compatibilidad):
    from app.domains.medicine.routers import (
        alphafold3_router,
        clinicalbert_router,
        personalized_medicine_router,
        api_router
    )

Configuración de routing:
- El router unificado maneja automáticamente el routing a servicios específicos
- Los routers especializados mantienen compatibilidad con integraciones existentes
- Todos los routers implementan autenticación y validación estándar
"""

# Router principal unificado (RECOMENDADO)
from .unified_medical_router import router as unified_router

# Routers especializados (para compatibilidad)
from .alphafold3 import router as alphafold3_router
from .clinicalbert import router as clinicalbert_router  
from .personalized_medicine import router as personalized_medicine_router
from .api import router as api_router

# Exportaciones principales
__all__ = [
    # Router principal (RECOMENDADO)
    "unified_router",
    
    # Routers especializados
    "alphafold3_router",
    "clinicalbert_router", 
    "personalized_medicine_router",
    
    # Router legacy
    "api_router"
]

# Configuración de routers
MEDICAL_ROUTERS = {
    "unified": {
        "router": unified_router,
        "prefix": "/medical",
        "tags": ["Unified Medical Services"],
        "description": "Router principal unificado para todos los servicios médicos"
    },
    "alphafold3": {
        "router": alphafold3_router,
        "prefix": "/medical/alphafold3",
        "tags": ["AlphaFold3", "Protein Structure"],
        "description": "Predicción de estructuras proteicas con AlphaFold 3"
    },
    "clinicalbert": {
        "router": clinicalbert_router,
        "prefix": "/medical/clinicalbert",
        "tags": ["ClinicalBERT", "Medical NLP"],
        "description": "Procesamiento de texto clínico y NLP médico"
    },
    "personalized_medicine": {
        "router": personalized_medicine_router,
        "prefix": "/medical/personalized",
        "tags": ["Personalized Medicine", "Pharmacogenomics"],
        "description": "Farmacogenómica y medicina personalizada"
    },
    "api": {
        "router": api_router,
        "prefix": "/api/medicine",
        "tags": ["Medicine API"],
        "description": "API genérica del dominio médico (legacy)"
    }
}

def get_all_medical_routers():
    """
    Obtiene todos los routers médicos configurados
    
    Returns:
        Dict con configuración de todos los routers médicos
    """
    return MEDICAL_ROUTERS

def get_unified_router():
    """
    Obtiene el router unificado principal
    
    Returns:
        Router unificado para servicios médicos
    """
    return unified_router

def get_legacy_routers():
    """
    Obtiene los routers legacy para compatibilidad
    
    Returns:
        Dict con routers legacy
    """
    return {
        "alphafold3": alphafold3_router,
        "clinicalbert": clinicalbert_router,
        "personalized_medicine": personalized_medicine_router,
        "api": api_router
    }
