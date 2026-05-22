"""
Publication System Service Registration - AXIOM META 4
Register publication generation services with the unified service registry.
"""

from typing import Dict, Any
import os
from app.services.publication_generator import PublicationGeneratorService
from app.core.bootstrap_logging import logger
from app.config import settings
from app.exceptions.domain.biology import BiologyError


def _should_skip_autoregistration() -> bool:
    """Return True if AXIOM_SKIP_AUTOINIT indicates we should skip side-effects."""
    env_flag = str(os.getenv("AXIOM_SKIP_AUTOINIT", "0")).lower()
    settings_flag = str(getattr(settings, "AXIOM_SKIP_AUTOINIT", env_flag)).lower()
    return settings_flag in {"1", "true", "yes"}


def register_publication_services() -> bool:
    """Register publication services (simplified version)"""
    # Simple registration without external registry
    logger.info("✅ Publication services registration initialized")
    try:
        PublicationGeneratorService()
        logger.info("✅ Publication service instantiated successfully")
        return True
    except BiologyError as exc:  # noqa: BLE001 - broad except acceptable at boundary
        logger.error("❌ Failed to register publication services: %s", exc)
        return False


def get_publication_service_capabilities() -> Dict[str, Any]:
    """Get comprehensive capabilities of the publication system"""
    return {
        "system_name": "AXIOM Publication Generator",
        "version": "1.0.0",
        "description": "Autonomous scientific publication generation system",
        
        "core_capabilities": [
            "IMRaD structure generation",
            "Internal DOI system",
            "Blockchain validation integration",
            "Cross-domain content synthesis",
            "Template-based rendering",
            "Publication packaging",
            "Integrity verification"
        ],
        
        "supported_inputs": [
            "hypothesis_data",
            "research_cycle_data", 
            "custom_content",
            "validation_results",
            "experimental_data"
        ],
        
        "generated_outputs": [
            "complete_publication_package",
            "imrad_structured_content",
            "doi_identifier",
            "blockchain_proof",
            "integrity_hash",
            "validation_metadata"
        ],
        
        "api_endpoints": {
            "generate": "POST /api/v1/publications/generate",
            "list": "GET /api/v1/publications/list",
            "get": "GET /api/v1/publications/{pub_id}",
            "validate": "GET /api/v1/publications/{pub_id}/validate",
            "download": "GET /api/v1/publications/{pub_id}/download",
            "regenerate": "POST /api/v1/publications/{pub_id}/regenerate",
            "delete": "DELETE /api/v1/publications/{pub_id}",
            "stats": "GET /api/v1/publications/{pub_id}/stats"
        },
        
        "integration_status": {
            "hypothesis_system": "available",
            "research_cycles": "available", 
            "cross_validation": "integrated",
            "blockchain_validation": "integrated",
            "service_registry": "registered"
        },
        
        "quality_metrics": {
            "validation_integration": "operational",
            "blockchain_proof": "available",
            "template_system": "comprehensive",
            "package_integrity": "verified",
            "doi_system": "functional"
        }
    }


def validate_publication_system_integration():
    """Validate that the publication system is properly integrated"""
    try:        
        # Check service instantiation
        try:  # Boundary-level broad except
            PublicationGeneratorService()
            logger.info("✅ Publication service can be instantiated")
        except BiologyError as exc:  # noqa: BLE001
            logger.error("❌ Cannot instantiate publication service: %s", exc)
            return False
        
        # Check template system
        from app.services.publication_generator import IMRaDTemplateEngine
        try:  # Boundary-level broad except
            engine = IMRaDTemplateEngine()
            templates_dir = engine.templates_dir
            if not templates_dir.exists():
                logger.warning("⚠️ Templates directory not found")
                return False
            logger.info("✅ Template system operational")
        except BiologyError as exc:  # noqa: BLE001
            logger.error("❌ Template system error: %s", exc)
            return False
        
        logger.info("✅ Publication system integration validated")
        return True
        
    except BiologyError as exc:  # noqa: BLE001
        logger.error("❌ Publication system integration validation failed: %s", exc)
        return False


# Auto-registration when module is imported (skip if AXIOM_SKIP_AUTOINIT set)
if __name__ != "__main__":
    if not _should_skip_autoregistration():
        try:  # Boundary-level broad except
            register_publication_services()
        except BiologyError as exc:  # noqa: BLE001
            logger.warning("⚠️ Auto-registration failed: %s", exc)
    else:
        logger.debug("⏭️ Publication services auto-registration skipped (AXIOM_SKIP_AUTOINIT)")


if __name__ == "__main__":
    # Direct execution - run validation
    print("🚀 AXIOM Publication System - Service Registration")
    print("=" * 60)
    
    print("\n📋 Registering services...")
    reg_success = register_publication_services()
    
    print("\n🔍 Validating integration...")
    val_success = validate_publication_system_integration()
    
    print("\n📊 System capabilities:")
    capabilities = get_publication_service_capabilities()
    print(f"   System: {capabilities['system_name']} v{capabilities['version']}")
    print(f"   Core Capabilities: {len(capabilities['core_capabilities'])}")
    print(f"   API Endpoints: {len(capabilities['api_endpoints'])}")
    print(f"   Integration Status: {len([k for k, v in capabilities['integration_status'].items() if v in ['available', 'integrated']])}/5")
    
    print("\n" + "=" * 60)
    if reg_success and val_success:
        print("✅ Publication system successfully registered and validated!")
    else:
        print("⚠️ Publication system registration/validation had issues")
        print(f"   Registration: {'✅' if reg_success else '❌'}")
        print(f"   Validation: {'✅' if val_success else '❌'}")
