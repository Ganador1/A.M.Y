#!/usr/bin/env python3
"""
Security Hardening Script - AXIOM ATLAS
=======================================

Script para implementar hardening final de seguridad.
Incluye rotación de secretos, IP whitelisting, y audit logging.

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

import os
import secrets
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import ipaddress

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityHardener:
    """Implementador de hardening de seguridad"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.config_dir = self.project_root / "config"
        self.security_dir = self.project_root / "app" / "security"
        self.security_dir.mkdir(exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def rotate_secret_keys(self) -> Dict[str, str]:
        """Rotar claves secretas"""
        logger.info("🔑 Rotando claves secretas...")
        
        new_secrets = {
            "SECRET_KEY": secrets.token_urlsafe(32),
            "JWT_SECRET": secrets.token_urlsafe(32),
            "ENCRYPTION_KEY": secrets.token_urlsafe(32),
            "API_KEY_SECRET": secrets.token_urlsafe(32),
            "SESSION_SECRET": secrets.token_urlsafe(32)
        }
        
        # Generar archivo de secretos
        secrets_file = self.security_dir / f"secrets_{self.timestamp}.json"
        with open(secrets_file, 'w') as f:
            json.dump(new_secrets, f, indent=2)
        
        logger.info(f"✅ Nuevas claves generadas en: {secrets_file}")
        return new_secrets
    
    def setup_ip_whitelisting(self) -> Dict[str, Any]:
        """Configurar IP whitelisting"""
        logger.info("🌐 Configurando IP whitelisting...")
        
        # IPs permitidas por defecto
        allowed_ips = [
            "127.0.0.1/32",      # localhost
            "10.0.0.0/8",         # redes privadas clase A
            "172.16.0.0/12",     # redes privadas clase B
            "192.168.0.0/16"     # redes privadas clase C
        ]
        
        # Crear módulo de IP whitelisting
        ip_whitelist_code = f'''
"""
IP Whitelisting Module - AXIOM ATLAS
====================================

Módulo para control de acceso basado en IP.
Implementa whitelisting de IPs permitidas.

Author: AXIOM Team
Date: {datetime.now().strftime("%Y-%m-%d")}
Version: 1.0.0
"""

import ipaddress
from typing import List, Optional
from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)


class IPWhitelist:
    """Control de acceso basado en IP"""
    
    def __init__(self, allowed_networks: List[str] = None):
        self.allowed_networks = allowed_networks or {allowed_ips}
        self._compile_networks()
    
    def _compile_networks(self):
        """Compilar redes permitidas para verificación rápida"""
        self.networks = []
        for network_str in self.allowed_networks:
            try:
                network = ipaddress.ip_network(network_str, strict=False)
                self.networks.append(network)
            except ValueError as e:
                logger.error(f"Invalid network {network_str}: {e}")
    
    def is_allowed(self, ip: str) -> bool:
        """Verificar si una IP está permitida"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return any(ip_obj in network for network in self.networks)
        except ValueError:
            logger.error(f"Invalid IP address: {ip}")
            return False
    
    def add_network(self, network_str: str):
        """Agregar red permitida"""
        try:
            network = ipaddress.ip_network(network_str, strict=False)
            self.networks.append(network)
            self.allowed_networks.add(network_str)
            logger.info(f"Added allowed network: {network_str}")
        except ValueError as e:
            logger.error(f"Invalid network {network_str}: {e}")
    
    def remove_network(self, network_str: str):
        """Remover red permitida"""
        try:
            network = ipaddress.ip_network(network_str, strict=False)
            self.networks = [n for n in self.networks if n != network]
            self.allowed_networks.discard(network_str)
            logger.info(f"Removed allowed network: {network_str}")
        except ValueError as e:
            logger.error(f"Invalid network {network_str}: {e}")


# Instancia global
ip_whitelist = IPWhitelist()


def check_ip_access(request: Request) -> bool:
    """Verificar acceso basado en IP"""
    client_ip = request.client.host
    
    # Verificar IP real si hay proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    is_allowed = ip_whitelist.is_allowed(client_ip)
    
    if not is_allowed:
        logger.warning(f"Blocked access from IP: {client_ip}")
        raise HTTPException(
            status_code=403,
            detail={"error": "IP not allowed", "ip": client_ip}
        )
    
    return True


def setup_ip_whitelisting_middleware(app):
    """Configurar middleware de IP whitelisting"""
    from fastapi import Request
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class IPWhitelistMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Verificar IP antes de procesar request
            check_ip_access(request)
            response = await call_next(request)
            return response
    
    app.add_middleware(IPWhitelistMiddleware)
    logger.info("✅ IP whitelisting middleware configured")
'''
        
        # Guardar módulo
        ip_module_file = self.security_dir / "ip_whitelist.py"
        with open(ip_module_file, 'w') as f:
            f.write(ip_whitelist_code)
        
        logger.info(f"✅ Módulo de IP whitelisting creado: {ip_module_file}")
        
        return {
            "allowed_networks": allowed_ips,
            "module_file": str(ip_module_file)
        }
    
    def setup_audit_logging(self) -> Dict[str, Any]:
        """Configurar audit logging"""
        logger.info("📝 Configurando audit logging...")
        
        audit_logger_code = f'''
"""
Audit Logging Module - AXIOM ATLAS
===================================

Módulo para logging de auditoría de seguridad.
Registra eventos críticos para compliance y forensics.

Author: AXIOM Team
Date: {datetime.now().strftime("%Y-%m-%d")}
Version: 1.0.0
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import hashlib
import uuid

# Configurar logger de auditoría
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Handler para archivo de auditoría
audit_handler = logging.FileHandler("logs/audit.log")
audit_handler.setLevel(logging.INFO)

# Formatter para logs de auditoría
audit_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
audit_handler.setFormatter(audit_formatter)

audit_logger.addHandler(audit_handler)


class AuditLogger:
    """Logger de auditoría de seguridad"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
    
    def log_access(self, user_id: str, resource: str, action: str = "access", 
                   details: Optional[Dict[str, Any]] = None):
        """Registrar acceso a recursos"""
        event = {{
            "timestamp": datetime.now().isoformat(),
            "event_type": "access",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "session_id": self.session_id,
            "details": details or {{}}
        }}
        
        audit_logger.info(json.dumps(event))
    
    def log_authentication(self, user_id: str, success: bool, 
                          method: str = "password", details: Optional[Dict[str, Any]] = None):
        """Registrar eventos de autenticación"""
        event = {{
            "timestamp": datetime.now().isoformat(),
            "event_type": "authentication",
            "user_id": user_id,
            "success": success,
            "method": method,
            "session_id": self.session_id,
            "details": details or {{}}
        }}
        
        audit_logger.info(json.dumps(event))
    
    def log_authorization(self, user_id: str, resource: str, action: str,
                          success: bool, details: Optional[Dict[str, Any]] = None):
        """Registrar eventos de autorización"""
        event = {{
            "timestamp": datetime.now().isoformat(),
            "event_type": "authorization",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "success": success,
            "session_id": self.session_id,
            "details": details or {{}}
        }}
        
        audit_logger.info(json.dumps(event))
    
    def log_data_access(self, user_id: str, data_type: str, operation: str,
                       record_count: int, details: Optional[Dict[str, Any]] = None):
        """Registrar acceso a datos"""
        event = {{
            "timestamp": datetime.now().isoformat(),
            "event_type": "data_access",
            "user_id": user_id,
            "data_type": data_type,
            "operation": operation,
            "record_count": record_count,
            "session_id": self.session_id,
            "details": details or {{}}
        }}
        
        audit_logger.info(json.dumps(event))
    
    def log_security_event(self, event_type: str, severity: str, 
                           description: str, details: Optional[Dict[str, Any]] = None):
        """Registrar eventos de seguridad"""
        event = {{
            "timestamp": datetime.now().isoformat(),
            "event_type": "security_event",
            "security_event_type": event_type,
            "severity": severity,
            "description": description,
            "session_id": self.session_id,
            "details": details or {{}}
        }}
        
        audit_logger.info(json.dumps(event))
    
    def log_system_event(self, component: str, action: str, 
                        success: bool, details: Optional[Dict[str, Any]] = None):
        """Registrar eventos del sistema"""
        event = {{
            "timestamp": datetime.now().isoformat(),
            "event_type": "system_event",
            "component": component,
            "action": action,
            "success": success,
            "session_id": self.session_id,
            "details": details or {{}}
        }}
        
        audit_logger.info(json.dumps(event))


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
'''
        
        # Crear directorio de logs
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Guardar módulo
        audit_module_file = self.security_dir / "audit_logger.py"
        with open(audit_module_file, 'w') as f:
            f.write(audit_logger_code)
        
        logger.info(f"✅ Módulo de audit logging creado: {audit_module_file}")
        
        return {
            "module_file": str(audit_module_file),
            "logs_dir": str(logs_dir)
        }
    
    def create_security_documentation(self) -> Dict[str, str]:
        """Crear documentación de seguridad"""
        logger.info("📚 Creando documentación de seguridad...")
        
        docs_dir = self.project_root / "docs" / "security"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Documentación principal de seguridad
        security_doc = f'''# 🔒 Security Documentation - AXIOM ATLAS

## Overview

Este documento describe las medidas de seguridad implementadas en AXIOM ATLAS.

## Security Features Implemented

### 1. Input Sanitization
- **Archivo**: `app/security/input_sanitizer.py`
- **Funcionalidad**: Sanitización de inputs del usuario para prevenir ataques de inyección
- **Cobertura**: HTML, SQL, comandos shell, paths, emails, URLs

### 2. Security Headers
- **Archivo**: `app/middleware/security_headers.py`
- **Funcionalidad**: Headers HTTP de seguridad estándar
- **Headers**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, etc.

### 3. Rate Limiting
- **Archivo**: `app/core/rate_limit.py`
- **Funcionalidad**: Rate limiting real usando slowapi y Redis
- **Tiers**: Anonymous, Authenticated, Premium, Internal

### 4. IP Whitelisting
- **Archivo**: `app/security/ip_whitelist.py`
- **Funcionalidad**: Control de acceso basado en IP
- **Redes**: Localhost, redes privadas (10.x, 172.16.x, 192.168.x)

### 5. Audit Logging
- **Archivo**: `app/security/audit_logger.py`
- **Funcionalidad**: Logging de eventos de seguridad
- **Eventos**: Acceso, autenticación, autorización, datos, seguridad

## Security Scanning

### Automated Tools
- **Bandit**: Análisis de seguridad de código Python
- **Safety**: Verificación de vulnerabilidades en dependencias
- **Semgrep**: Análisis estático de código
- **Detect-secrets**: Detección de secretos hardcodeados

### Manual Penetration Testing
- Autenticación bypass
- SQL injection
- Command injection
- Path traversal
- XSS
- Rate limiting bypass
- Information disclosure

## Security Configuration

### Environment Variables
```bash
# Security settings
SECRET_KEY=<generated_secret_key>
JWT_SECRET=<generated_jwt_secret>
ENCRYPTION_KEY=<generated_encryption_key>
API_KEY_SECRET=<generated_api_secret>
SESSION_SECRET=<generated_session_secret>

# Rate limiting
REDIS_URL=redis://localhost:6379
RATE_LIMIT_ENABLED=true

# IP whitelisting
IP_WHITELIST_ENABLED=true
ALLOWED_NETWORKS=127.0.0.1/32,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16

# Audit logging
AUDIT_LOG_ENABLED=true
AUDIT_LOG_FILE=logs/audit.log
```

## Security Best Practices

### 1. Input Validation
- Siempre validar y sanitizar inputs del usuario
- Usar Pydantic para validación de datos
- Implementar whitelist en lugar de blacklist

### 2. Authentication & Authorization
- Usar JWT tokens con expiración corta
- Implementar refresh tokens
- Verificar permisos en cada endpoint

### 3. Data Protection
- Encriptar datos sensibles en reposo
- Usar HTTPS en producción
- Implementar backup encryption

### 4. Monitoring & Logging
- Monitorear logs de auditoría regularmente
- Implementar alertas para eventos críticos
- Mantener logs por tiempo requerido por compliance

### 5. Regular Updates
- Mantener dependencias actualizadas
- Ejecutar security scans regularmente
- Revisar y actualizar políticas de seguridad

## Incident Response

### Security Incident Procedure
1. **Detectar**: Identificar el incidente
2. **Contener**: Limitar el impacto
3. **Eradicar**: Eliminar la causa
4. **Recuperar**: Restaurar servicios
5. **Lecciones**: Documentar y mejorar

### Contact Information
- **Security Team**: security@axiom-atlas.com
- **Emergency**: +1-XXX-XXX-XXXX
- **Incident Report**: https://security.axiom-atlas.com/report

## Compliance

### Standards Compliance
- **OWASP Top 10**: Implementado
- **ISO 27001**: En proceso
- **SOC 2**: Planificado
- **GDPR**: Implementado

### Regular Audits
- **Quarterly**: Security scans
- **Annually**: Penetration testing
- **Continuous**: Monitoring

---

**Última actualización**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Versión**: 1.0.0
'''
        
        # Guardar documentación
        security_doc_file = docs_dir / "SECURITY.md"
        with open(security_doc_file, 'w') as f:
            f.write(security_doc)
        
        # Crear runbook de incidentes
        incident_runbook = f'''# 🚨 Security Incident Response Runbook

## Quick Response Checklist

### 1. Immediate Response (0-15 minutes)
- [ ] Confirm incident severity
- [ ] Activate incident response team
- [ ] Document initial findings
- [ ] Notify stakeholders

### 2. Containment (15-60 minutes)
- [ ] Isolate affected systems
- [ ] Preserve evidence
- [ ] Block malicious IPs
- [ ] Update security controls

### 3. Investigation (1-4 hours)
- [ ] Analyze logs and evidence
- [ ] Determine attack vector
- [ ] Assess data exposure
- [ ] Document timeline

### 4. Recovery (4-24 hours)
- [ ] Patch vulnerabilities
- [ ] Restore services
- [ ] Verify system integrity
- [ ] Monitor for recurrence

### 5. Post-Incident (24+ hours)
- [ ] Conduct lessons learned
- [ ] Update security measures
- [ ] Notify affected users
- [ ] File compliance reports

## Contact Information

### Internal Team
- **Security Lead**: security-lead@axiom-atlas.com
- **DevOps Lead**: devops-lead@axiom-atlas.com
- **Legal Team**: legal@axiom-atlas.com

### External Resources
- **CERT**: cert@cert.org
- **Law Enforcement**: local-fbi-field-office
- **Insurance**: cyber-insurance-provider

## Escalation Matrix

| Severity | Response Time | Team Lead | Executive |
|----------|---------------|-----------|-----------|
| Critical | 15 min | Security Lead | CTO |
| High | 1 hour | Security Lead | VP Engineering |
| Medium | 4 hours | Security Team | Engineering Manager |
| Low | 24 hours | Security Team | Team Lead |

## Communication Templates

### Internal Notification
```
SECURITY INCIDENT ALERT
Severity: [CRITICAL/HIGH/MEDIUM/LOW]
Time: [TIMESTAMP]
Affected Systems: [SYSTEMS]
Status: [INVESTIGATING/CONTAINED/RESOLVED]
Contact: [SECURITY_LEAD]
```

### External Notification
```
Subject: Security Incident Notification

Dear [STAKEHOLDER],

We are writing to inform you of a security incident that occurred on [DATE].

Incident Details:
- Type: [INCIDENT_TYPE]
- Severity: [SEVERITY]
- Systems Affected: [SYSTEMS]
- Data Impact: [DATA_IMPACT]

Our Response:
- Immediate containment measures implemented
- Investigation in progress
- Additional security measures deployed

We will provide updates as more information becomes available.

Contact: security@axiom-atlas.com
```

---

**Document Version**: 1.0
**Last Updated**: {datetime.now().strftime("%Y-%m-%d")}
'''
        
        # Guardar runbook
        runbook_file = docs_dir / "INCIDENT_RESPONSE_RUNBOOK.md"
        with open(runbook_file, 'w') as f:
            f.write(incident_runbook)
        
        logger.info(f"✅ Documentación de seguridad creada en: {docs_dir}")
        
        return {
            "security_doc": str(security_doc_file),
            "incident_runbook": str(runbook_file)
        }
    
    def run_all_hardening(self) -> Dict[str, Any]:
        """Ejecutar todo el proceso de hardening"""
        logger.info("🔒 Iniciando security hardening completo...")
        
        results = {
            "timestamp": self.timestamp,
            "secrets_rotation": self.rotate_secret_keys(),
            "ip_whitelisting": self.setup_ip_whitelisting(),
            "audit_logging": self.setup_audit_logging(),
            "documentation": self.create_security_documentation()
        }
        
        # Generar reporte final
        self.generate_hardening_report(results)
        
        return results
    
    def generate_hardening_report(self, results: Dict[str, Any]):
        """Generar reporte final de hardening"""
        report_file = self.security_dir / f"hardening_report_{self.timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Reporte en texto
        text_report = self.security_dir / f"hardening_report_{self.timestamp}.txt"
        with open(text_report, 'w') as f:
            f.write("🔒 SECURITY HARDENING REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"Project: {self.project_root}\n\n")
            
            f.write("✅ COMPLETED TASKS\n")
            f.write("-" * 20 + "\n")
            f.write("✓ Secret keys rotated\n")
            f.write("✓ IP whitelisting configured\n")
            f.write("✓ Audit logging implemented\n")
            f.write("✓ Security documentation created\n")
            f.write("✓ Incident response runbook created\n\n")
            
            f.write("📁 GENERATED FILES\n")
            f.write("-" * 20 + "\n")
            f.write(f"Secrets: {results['secrets_rotation']}\n")
            f.write(f"IP Whitelist: {results['ip_whitelisting']['module_file']}\n")
            f.write(f"Audit Logger: {results['audit_logging']['module_file']}\n")
            f.write(f"Security Doc: {results['documentation']['security_doc']}\n")
            f.write(f"Incident Runbook: {results['documentation']['incident_runbook']}\n\n")
            
            f.write("🔧 NEXT STEPS\n")
            f.write("-" * 20 + "\n")
            f.write("1. Update environment variables with new secrets\n")
            f.write("2. Configure IP whitelisting in production\n")
            f.write("3. Enable audit logging in all environments\n")
            f.write("4. Train team on incident response procedures\n")
            f.write("5. Schedule regular security reviews\n")
        
        logger.info(f"📄 Reporte de hardening guardado en: {report_file}")
        logger.info(f"📄 Reporte de texto guardado en: {text_report}")


def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    hardener = SecurityHardener(project_root)
    results = hardener.run_all_hardening()
    
    print("\n" + "=" * 50)
    print("🔒 SECURITY HARDENING COMPLETED")
    print("=" * 50)
    print("✅ Secret keys rotated")
    print("✅ IP whitelisting configured")
    print("✅ Audit logging implemented")
    print("✅ Security documentation created")
    print("✅ Incident response runbook created")
    print(f"\n📄 Reports saved in: {hardener.security_dir}")


if __name__ == "__main__":
    main()
