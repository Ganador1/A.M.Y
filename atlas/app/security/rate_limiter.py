"""
Shim de compatibilidad para rate limiting.

Este módulo mantiene el import histórico `app.security.rate_limiter`
delegando a la implementación consolidada en `app.core.rate_limit`.
"""

from app.core.rate_limit import (
    AdvancedRateLimiter,
    rate_limiter,
    rate_limit,
    auth_rate_limit,
    upload_rate_limit,
    training_rate_limit,
    setup_rate_limiting,
)

# Re-export for compatibility
__all__ = [
    "AdvancedRateLimiter",
    "rate_limiter",
    "rate_limit",
    "auth_rate_limit",
    "upload_rate_limit",
    "training_rate_limit",
    "setup_rate_limiting",
]

__all__ = [
    "rate_limiter",
    "rate_limit",
    "auth_rate_limit",
    "upload_rate_limit",
    "training_rate_limit",
    "setup_rate_limiting",
]