"""
AXIOM Logging Configuration - Enhanced Version
Advanced logging system for the AXIOM ATLAS platform

Features:
- Multiple log levels and handlers
- Log rotation and retention
- Structured logging with JSON format
- Performance logging
- Security event logging
- Development vs production configurations
- Enhanced error handling and context
"""

import logging
import logging.handlers
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import asyncio

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


class CustomFormatter(logging.Formatter):
    """Custom formatter with colors for development"""

    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m',
    }

    def format(self, record):
        if settings.debug:
            timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
            level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset_color = self.COLORS['RESET']

            formatted_message = f"[{timestamp}] {level_color}{record.levelname}{reset_color} - {record.getMessage()}"

            if record.levelno == logging.DEBUG:
                formatted_message += f" ({record.filename}:{record.lineno})"

            return formatted_message
        else:
            return super().format(record)


class SecurityFormatter(logging.Formatter):
    """Specialized formatter for security events"""

    def format(self, record):
        security_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "SECURITY",
            "event_type": getattr(record, 'event_type', 'unknown'),
            "user_id": getattr(record, 'user_id', None),
            "ip_address": getattr(record, 'ip_address', None),
            "user_agent": getattr(record, 'user_agent', None),
            "resource": getattr(record, 'resource', None),
            "action": getattr(record, 'action', None),
            "message": record.getMessage(),
        }

        return json.dumps(security_entry, default=str)


class PerformanceFormatter(logging.Formatter):
    """Specialized formatter for performance metrics"""

    def format(self, record):
        perf_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "PERFORMANCE",
            "operation": getattr(record, 'operation', 'unknown'),
            "duration_ms": getattr(record, 'duration_ms', 0),
            "database_queries": getattr(record, 'database_queries', 0),
            "cache_hits": getattr(record, 'cache_hits', 0),
            "cache_misses": getattr(record, 'cache_misses', 0),
            "message": record.getMessage(),
        }

        return json.dumps(perf_entry, default=str)


class SecurityFilter(logging.Filter):
    def filter(self, record):
        return hasattr(record, 'event_type') or 'security' in record.getMessage().lower()


class PerformanceFilter(logging.Filter):
    def filter(self, record):
        return (hasattr(record, 'operation') or
                hasattr(record, 'duration_ms') or
                'performance' in record.getMessage().lower())


def get_log_level(level_str: str) -> int:
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return levels.get(level_str.upper(), logging.INFO)


def setup_logging(
    app_name: str = "axiom",
    log_level: Optional[str] = None,
    log_to_file: Optional[bool] = None,
    enable_json_logging: Optional[bool] = None,
) -> logging.Logger:
    """Setup enhanced logging configuration"""

    log_level = log_level or settings.log_level
    log_to_file = log_to_file if log_to_file is not None else getattr(settings, 'log_to_file', True)
    enable_json_logging = enable_json_logging if enable_json_logging is not None else getattr(settings, 'enable_json_logging', False)

    numeric_level = get_log_level(log_level)

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    lg = logging.getLogger(app_name)
    lg.setLevel(numeric_level)
    lg.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(JSONFormatter() if enable_json_logging else CustomFormatter())
    lg.addHandler(console_handler)

    if log_to_file:
        _setup_file_handlers(lg, log_dir, enable_json_logging)

    _setup_specific_loggers()
    _configure_third_party_logging(numeric_level)

    return lg


def _setup_file_handlers(lg: logging.Logger, log_dir: Path, enable_json_logging: bool) -> None:
    main_log_file = log_dir / "axiom_atlas.log"
    main_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    main_handler.setLevel(logging.DEBUG)
    main_handler.setFormatter(JSONFormatter() if enable_json_logging else logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    lg.addHandler(main_handler)

    error_log_file = log_dir / "axiom_atlas_error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter() if enable_json_logging else logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
        'File: %(pathname)s:%(lineno)d\n'
        'Function: %(funcName)s\n'
        '%(exc_text)s\n',
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    lg.addHandler(error_handler)

    security_log_file = log_dir / "axiom_atlas_security.log"
    security_handler = logging.handlers.RotatingFileHandler(
        security_log_file,
        maxBytes=1 * 1024 * 1024,
        backupCount=10
    )
    security_handler.setLevel(logging.INFO)
    security_handler.addFilter(SecurityFilter())
    security_handler.setFormatter(SecurityFormatter())
    lg.addHandler(security_handler)

    perf_log_file = log_dir / "axiom_atlas_performance.log"
    perf_handler = logging.handlers.RotatingFileHandler(
        perf_log_file,
        maxBytes=2 * 1024 * 1024,
        backupCount=5
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.addFilter(PerformanceFilter())
    perf_handler.setFormatter(PerformanceFormatter())
    lg.addHandler(perf_handler)


def _setup_specific_loggers() -> None:
    db_logger = logging.getLogger('app.core.database')
    db_logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    adapter_logger = logging.getLogger('app.adapters')
    adapter_logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    medical_logger = logging.getLogger('app.domains.medicine')
    medical_logger.setLevel(logging.INFO)

    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)

    perf_logger = logging.getLogger('performance')
    perf_logger.setLevel(logging.INFO)


def _configure_third_party_logging(base_level: int) -> None:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('redis').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)


def log_performance(operation: str, duration_ms: float, **kwargs):
    logger_perf = logging.getLogger('performance')
    extra_data = {
        'operation': operation,
        'duration_ms': duration_ms,
        **kwargs
    }
    logger_perf.info(f"Performance: {operation} completed in {duration_ms}ms", extra=extra_data)


def log_security_event(event_type: str, message: str, **kwargs):
    logger_sec = logging.getLogger('security')
    extra_data = {
        'event_type': event_type,
        **kwargs
    }
    logger_sec.warning(f"Security: {message}", extra=extra_data)


def log_database_operation(operation: str, duration_ms: float, **kwargs):
    logger_db = logging.getLogger('app.core.database')
    extra_data = {
        'operation': operation,
        'duration_ms': duration_ms,
        **kwargs
    }
    logger_db.debug(f"Database operation: {operation} ({duration_ms}ms)", extra=extra_data)


def log_error_with_context(error: Exception, context: Dict[str, Any] | None = None):
    logger_core = logging.getLogger('app.core')
    if context is None:
        context = {}
    logger_core.error(
        f"Error occurred: {str(error)}",
        extra={
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            **context
        }
    )


def log_api_request(
    endpoint: str,
    method: str,
    status_code: int,
    duration: Optional[float] = None,
    trace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
):
    logger_core = logging.getLogger('app.core')
    extra_data = {
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code,
        'trace_id': trace_id,
        'user_id': user_id,
        'ip_address': ip_address
    }
    message = f"API Request: {method} {endpoint} - Status: {status_code}"
    if duration:
        message += f" - Duration: {duration:.2f}s"
    if trace_id:
        message += f" - trace_id={trace_id}"
    if status_code >= 400:
        logger_core.error(message, extra=extra_data)
    else:
        logger_core.info(message, extra=extra_data)


def log_computation(operation: str, complexity: str = "medium", duration: Optional[float] = None, **kwargs):
    logger_core = logging.getLogger('app.core')
    extra_data = {
        'operation': operation,
        'complexity': complexity,
        **kwargs
    }
    message = f"Computation: {operation} - Complexity: {complexity}"
    if duration:
        message += f" - Duration: {duration:.2f}s"
    logger_core.info(message, extra=extra_data)


def log_decision_event(
    event_type: str,
    phase: Optional[str] = None,
    details: Optional[dict] = None,
    outcome: Optional[str] = None,
    trace_id: Optional[str] = None
):
    logger_core = logging.getLogger('app.core')
    safe_details: Optional[Dict] = None
    if details:
        MAX_KEYS = 12
        trimmed = {k: details[k] for i, k in enumerate(details) if i < MAX_KEYS}
        if len(trimmed) < len(details):
            trimmed['__truncated__'] = True
        SAFE_LEN = 160
        safe_details = {k: (str(v)[:SAFE_LEN] + '…' if len(str(v)) > SAFE_LEN else str(v)) for k, v in trimmed.items()}
    extra_data = {
        'event_type': event_type,
        'phase': phase,
        'outcome': outcome,
        'trace_id': trace_id,
        'details': safe_details
    }
    parts = [f"event={event_type}"]
    if phase:
        parts.append(f"phase={phase}")
    if outcome:
        parts.append(f"outcome={outcome}")
    if trace_id:
        parts.append(f"trace_id={trace_id}")
    message = "DecisionEvent: " + " | ".join(parts)
    logger_core.info(message, extra=extra_data)


def log_error(error_type: str, message: str, traceback_str: Optional[str] = None):
    logger_core = logging.getLogger('app.core')
    full_message = f"{error_type}: {message}"
    if traceback_str:
        full_message += f"\nTraceback: {traceback_str}"
    logger_core.error(full_message)


# Global logger instance
logger = setup_logging()


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