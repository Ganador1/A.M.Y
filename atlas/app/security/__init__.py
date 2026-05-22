"""
Security modules
"""

from .auth import require_scopes
from .security import (
    require_bearer,
    create_access_token,
    create_refresh_token,
    decode_token,
    DataEncryption,
    InputValidation,
    SecurityAuditor,
    AdvancedRateLimiter,
    SecurityEvent,
)
from .rate_limiter import rate_limiter
from .input_validator import input_validator
from .data_encryptor import data_encryptor
from .misuse_guard import (
    MisuseDecision,
    MisuseGuard,
    evaluate_misuse,
    format_blocked_message,
    misuse_guard,
    require_safe_operation,
)

# System scopes compatibility
SYSTEM_SCOPES = ["admin", "read", "write", "execute", "manage"]

security_auditor = SecurityAuditor()

__all__ = [
    "require_scopes",
    "require_bearer",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "SYSTEM_SCOPES",
    "security_auditor",
    "rate_limiter",
    "input_validator",
    "data_encryptor",
    "DataEncryption",
    "InputValidation",
    "SecurityAuditor",
    "AdvancedRateLimiter",
    "SecurityEvent",
    "MisuseDecision",
    "MisuseGuard",
    "evaluate_misuse",
    "format_blocked_message",
    "misuse_guard",
    "require_safe_operation",
]
