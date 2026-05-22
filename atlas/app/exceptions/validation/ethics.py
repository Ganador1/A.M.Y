"""Ethics & Safety Exceptions"""

from app.exceptions.base import AtlasSecurityError


class EthicsViolationError(AtlasSecurityError):
    """Violación de políticas éticas"""
    pass


class SafetyError(EthicsViolationError):
    """Error de seguridad/seguridad operacional"""
    pass


class ComplianceError(EthicsViolationError):
    """Regulatory or policy compliance validation failure."""
