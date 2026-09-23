"""
Compatibility shim for legacy imports: app.logging_config
Re-exports logging utilities from app.core.logging_config
"""

from app.core.logging_config import (
    logger,
    setup_logging,
    log_api_request,
    log_computation,
    log_error,
    log_decision_event,
    log_performance,
    log_security_event,
)

__all__ = [
    "logger",
    "setup_logging",
    "log_api_request",
    "log_computation",
    "log_error",
    "log_decision_event",
    "log_performance",
    "log_security_event",
]