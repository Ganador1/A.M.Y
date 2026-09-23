"""
Compatibility shim for domain services expecting app.domains.biology.services.base_service.BaseService

This module re-exports the core BaseService used across the application.
All biology domain services should inherit from this BaseService which provides:
- Abstract process_request() method for unified service interface
- Service name and logging infrastructure
- Integration with autonomous research loops

Legacy biology-specific helpers (validate_request, check_ethics_compliance, log_operation)
have been moved to BiologyServiceMixin for services that need them.
"""
from app.services.base_service import BaseService as BaseService

# Optional mixin for biology-specific functionality (backwards compatibility)
from typing import Dict, Any, Optional
from datetime import datetime


class BiologyServiceMixin:
    """
    Optional mixin providing biology-specific helpers.
    Use with BaseService: class MyService(BaseService, BiologyServiceMixin)
    """
    
    domain: str = "biology"
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get basic service information"""
        return {
            "service_name": self.__class__.__name__,
            "domain": getattr(self, "domain", "biology"),
            "created_at": getattr(self, "created_at", datetime.utcnow()).isoformat(),
            "version": "1.0.0"
        }

    async def validate_biology_request(self, request_data: Dict[str, Any]) -> bool:
        """Validate that the request is appropriate for the domain"""
        required_fields = ["timestamp"]
        for field in required_fields:
            if field not in request_data:
                return False
        return True

    async def check_ethics_compliance(self, operation: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check ethical compliance of the operation"""
        # Basic implementation - in production use EthicsGate
        return {
            "compliant": True,
            "warnings": [],
            "recommendations": []
        }

    def log_biology_operation(self, operation: str, user_id: Optional[str] = None, **kwargs):
        """Log operation for audit"""
        from app.core.bootstrap_logging import logger
        logger.info(f"[BIOLOGY] Operation: {operation}, User: {user_id}, Time: {datetime.utcnow()}")


__all__ = ["BaseService", "BiologyServiceMixin"]






