"""
Compatibility shim for domain services expecting app.domains.mathematics.services.base_service.BaseService
This module re-exports the core BaseService used across the application.
"""
from app.services.base_service import BaseService as BaseService

__all__ = ["BaseService"]