"""
AXIOM Bootstrap Logging
Configuración básica de logging sin dependencias circulares para AXIOM
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


def setup_basic_logging() -> logging.Logger:
    """
    Configurar logging básico sin dependencias de config para evitar imports circulares
    
    Returns:
        logger: Logger configurado básicamente
    """
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Mantener este módulo libre de imports pesados.
    # Usar el entorno como fuente primaria para el nivel de log.
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Crear logger principal
    logger = logging.getLogger("axiom")
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Formatters
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )
    
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler - básico
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler básico
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "axiom.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Si no se puede crear el archivo, continuar con console logging
        logger.warning(f"No se pudo crear log file: {e}")
    
    return logger


def get_logger() -> logging.Logger:
    """Obtener logger configurado (lazy initialization)"""
    return setup_basic_logging()


# Funciones de utilidad básicas para compatibilidad
def log_api_request(endpoint: str, method: str, status_code: int, 
                   duration: Optional[float] = None, trace_id: Optional[str] = None):
    """Log API request - versión básica"""
    logger = get_logger()
    message = f"API: {method} {endpoint} - {status_code}"
    if duration:
        message += f" ({duration:.2f}s)"
    if trace_id:
        message += f" [trace:{trace_id}]"
    
    if status_code >= 400:
        logger.error(message)
    else:
        logger.info(message)


def log_computation(operation: str, complexity: str = "medium", 
                   duration: Optional[float] = None):
    """Log computation - versión básica"""
    logger = get_logger()
    message = f"Compute: {operation} ({complexity})"
    if duration:
        message += f" - {duration:.2f}s"
    logger.info(message)


def log_error(error_type: str, message: str, traceback: Optional[str] = None):
    """Log error - versión básica"""
    logger = get_logger()
    full_message = f"{error_type}: {message}"
    if traceback:
        logger.error(f"{full_message}\n{traceback}")
    else:
        logger.error(full_message)


def log_decision_event(event_type: str, phase: Optional[str] = None, 
                      details: Optional[dict] = None, outcome: Optional[str] = None, 
                      trace_id: Optional[str] = None):
    """Log decision event - versión básica"""
    logger = get_logger()
    parts = [f"event={event_type}"]
    if phase:
        parts.append(f"phase={phase}")
    if outcome:
        parts.append(f"outcome={outcome}")
    if trace_id:
        parts.append(f"trace_id={trace_id}")
    if details:
        # Versión simplificada de details
        details_str = str(details)[:200]
        if len(str(details)) > 200:
            details_str += "..."
        parts.append(f"details={details_str}")
    
    logger.info("DecisionEvent: " + " | ".join(parts))


# Logger global - inicialización lazy
logger = get_logger()
