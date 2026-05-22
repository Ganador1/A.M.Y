"""Storage Exceptions"""

from app.exceptions.base import AtlasInfrastructureError


class StorageError(AtlasInfrastructureError):
    """Base storage error"""
    pass


class FileNotFoundStorageError(StorageError):
    """File not found in storage"""
    pass


class PermissionDeniedStorageError(StorageError):
    """Insufficient permissions for storage operation"""
    pass