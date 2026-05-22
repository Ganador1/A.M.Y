"""
Base service class for Mathematics AI services
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.core.bootstrap_logging import logger


class ScientificServiceMixin:
    """Mixin class for scientific services with common functionality"""

    def validate_scientific_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scientific input data"""
        if not isinstance(data, dict):
            return {"valid": False, "error": "Input must be a dictionary"}

        # Basic validation - can be extended by subclasses
        required_fields = getattr(self, 'required_input_fields', [])
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {"valid": False, "error": f"Missing required fields: {missing_fields}"}

        return {"valid": True}

    def format_scientific_output(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format scientific results with standard metadata"""
        import time
        return {
            "results": results,
            "service": getattr(self, 'name', 'unknown'),
            "timestamp": time.time()
        }


class BaseService(ABC):
    """Base class for all Mathematics AI services"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logger
        self.is_initialized = False

    def initialize(self) -> None:
        """Initialize the service"""
        self.logger.info("%s - Initializing...", self.name)
        self.is_initialized = True

    @abstractmethod
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a service request"""
        raise NotImplementedError("Subclasses must implement process_request")

    def log_request(self, request_data: Dict[str, Any]) -> None:
        """Log incoming request"""
        self.logger.info("%s - Processing request: %s", self.name, request_data)

    def log_response(self, response_data: Dict[str, Any]) -> None:
        """Log outgoing response"""
        self.logger.info("%s - Response: %s", self.name, response_data)

    def handle_error(self, error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
        """Handle and log errors"""
        error_msg = f"{self.name} - Error"
        if context:
            error_msg += f" in {context}"
        error_msg += f": {str(error)}"

        self.logger.error(error_msg)
        return {
            "success": False,
            "error": str(error),
            "service": self.name
        }