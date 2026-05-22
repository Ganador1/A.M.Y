"""
Compatibility wrapper for lab_automation_service
Re-exports from app.domains.engineering.services.lab_automation_service
"""

from app.domains.engineering.services.lab_automation_service import (
    LabAutomationService,
)

__all__ = [
    "LabAutomationService",
]