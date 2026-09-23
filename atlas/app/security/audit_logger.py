"""
Audit Logging Module - AXIOM ATLAS
===================================

Módulo para logging de auditoría de seguridad.
Registra eventos críticos para compliance y forensics.

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import hashlib
import uuid

# Configurar logger de auditoría (logging.Logger interno)
_audit_log = logging.getLogger("audit")
_audit_log.setLevel(logging.INFO)

# Handler para archivo de auditoría
audit_handler = logging.FileHandler("logs/audit.log")
audit_handler.setLevel(logging.INFO)

# Formatter para logs de auditoría
audit_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
audit_handler.setFormatter(audit_formatter)

_audit_log.addHandler(audit_handler)


class AuditLogger:
    """Logger de auditoría de seguridad"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self._log = _audit_log  # Usar el logger interno
    
    def log_access(self, user_id: str, resource: str, action: str = "access", 
                   details: Optional[Dict[str, Any]] = None):
        """Registrar acceso a recursos"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "access",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "session_id": self.session_id,
            "details": details or {}
        }
        
        self._log.info(json.dumps(event))
    
    def log_authentication(self, user_id: str, success: bool, 
                          method: str = "password", details: Optional[Dict[str, Any]] = None):
        """Registrar eventos de autenticación"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "authentication",
            "user_id": user_id,
            "success": success,
            "method": method,
            "session_id": self.session_id,
            "details": details or {}
        }
        
        self._log.info(json.dumps(event))
    
    def log_authorization(self, user_id: str, resource: str, action: str,
                          success: bool, details: Optional[Dict[str, Any]] = None):
        """Registrar eventos de autorización"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "authorization",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "success": success,
            "session_id": self.session_id,
            "details": details or {}
        }
        
        self._log.info(json.dumps(event))
    
    def log_data_access(self, user_id: str, data_type: str, operation: str,
                       record_count: int, details: Optional[Dict[str, Any]] = None):
        """Registrar acceso a datos"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "data_access",
            "user_id": user_id,
            "data_type": data_type,
            "operation": operation,
            "record_count": record_count,
            "session_id": self.session_id,
            "details": details or {}
        }
        
        self._log.info(json.dumps(event))
    
    def log_security_event(self, event_type: str, severity: str, 
                           description: str, details: Optional[Dict[str, Any]] = None):
        """Registrar eventos de seguridad"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "security_event",
            "security_event_type": event_type,
            "severity": severity,
            "description": description,
            "session_id": self.session_id,
            "details": details or {}
        }
        
        self._log.info(json.dumps(event))
    
    def log_system_event(self, component: str, action: str, 
                        success: bool, details: Optional[Dict[str, Any]] = None):
        """Registrar eventos del sistema"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "system_event",
            "component": component,
            "action": action,
            "success": success,
            "session_id": self.session_id,
            "details": details or {}
        }
        
        self._log.info(json.dumps(event))
    
    def log_ethics_evaluation(self, domain: str, description: str, decision: str,
                             risk_score: float, allowed: bool, requires_signature: bool,
                             escalation_reasons: list, user_id: str = "system",
                             metadata: Optional[Dict[str, Any]] = None):
        """Registrar evaluaciones éticas"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "ethics_evaluation",
            "domain": domain,
            "description": description,
            "decision": decision,
            "risk_score": risk_score,
            "allowed": allowed,
            "requires_signature": requires_signature,
            "escalation_reasons": escalation_reasons,
            "user_id": user_id,
            "session_id": self.session_id,
            "metadata": metadata or {}
        }
        
        self._log.info(json.dumps(event))


# Instancia global
audit_logger = AuditLogger()


# Decoradores para logging automático
def audit_access(resource: str):
    """Decorador para logging automático de acceso"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extraer user_id del request si está disponible
            user_id = "anonymous"
            if args and hasattr(args[0], 'state'):
                user_id = getattr(args[0].state, 'user_id', 'anonymous')
            
            audit_logger.log_access(user_id, resource, func.__name__)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def audit_data_access(data_type: str, operation: str):
    """Decorador para logging automático de acceso a datos"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_id = "anonymous"
            if args and hasattr(args[0], 'state'):
                user_id = getattr(args[0].state, 'user_id', 'anonymous')
            
            # Ejecutar función y obtener resultado
            result = func(*args, **kwargs)
            
            # Contar registros si es posible
            record_count = 0
            if isinstance(result, list):
                record_count = len(result)
            elif isinstance(result, dict) and 'count' in result:
                record_count = result['count']
            
            audit_logger.log_data_access(user_id, data_type, operation, record_count)
            return result
        return wrapper
    return decorator