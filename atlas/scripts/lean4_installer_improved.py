"""
Shim module to allow direct import of AdvancedLean4InstallerService
without needing the full package path. This re-exports the service
from `app.services.lean4_installer_improved` to satisfy standalone tests.
"""

from app.services.lean4_installer_improved import AdvancedLean4InstallerService

__all__ = ["AdvancedLean4InstallerService"]