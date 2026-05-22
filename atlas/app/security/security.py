"""
AXIOM Advanced Security System
Comprehensive security framework for the Mathematics AI platform
"""

import hashlib
import hmac
import secrets
import time
import logging
import base64
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
import asyncio
from collections import defaultdict

from cryptography.fernet import Fernet

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from ..core.config import settings

# Original bearer security
_bearer_scheme = HTTPBearer(auto_error=False)

def require_bearer(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme)) -> str:
    """
    Guard dependency. When ENABLE_AUTH_ROUTES=true, require a Bearer token matching API_BEARER_TOKEN.
    When disabled, it becomes a no-op to keep local dev simple.
    Returns the token string if present/valid.
    """
    if not settings.enable_auth_routes:
        return ""

    expected = settings.api_bearer_token
    if not expected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth misconfigured")

    if not credentials or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    if token != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    return token

# --- JWT utilities (HS256) and scoped auth ---
# Scopes específicos del sistema AXIOM
SYSTEM_SCOPES = {
    # Core system access
    "system:read": "Read system metrics and status",
    "system:admin": "Full system administration access",
    "system:lineage": "Access data lineage and provenance",
    "system:slo": "Access SLO metrics and performance data",
    
    # Research and experimental access
    "research:execute": "Execute research workflows",
    "research:admin": "Manage research pipelines",
    "experimental:run": "Run experimental toolkits",
    "experimental:admin": "Manage experimental resources",
    
    # Lab equipment and scheduling
    "lab:equipment": "Access lab equipment interfaces",
    "lab:schedule": "Schedule lab equipment usage",
    "scheduler:policy": "Access policy-aware scheduling",
    "scheduler:admin": "Manage scheduling policies",
    
    # Multi-agent and orchestration
    "agent:orchestrate": "Orchestrate multi-agent workflows",
    "agent:admin": "Manage agent configurations",
    "knowledge:read": "Read knowledge graph data",
    "knowledge:write": "Write to knowledge graph",
    
    # Publication and reproducibility
    "publication:generate": "Generate scientific publications",
    "publication:admin": "Manage publication workflows",
    "reproducibility:verify": "Verify reproducibility requirements",
    "reproducibility:admin": "Manage reproducibility policies"
}

def create_access_token(subject: str, scopes: Optional[List[str]] = None,
                        expires_minutes: Optional[int] = None, 
                        refresh: bool = False) -> str:
    """Create a signed JWT access token with scopes and expiration.

    Args:
        subject: Subject identifier (e.g., user id or service id)
        scopes: List of scope strings granted to the token
        expires_minutes: Minutes until expiration; defaults to settings.access_token_expire_minutes
        refresh: If True, create a refresh token with longer expiration

    Returns:
        Encoded JWT string
    """
    if scopes is None:
        scopes = []

    # Validate scopes against defined system scopes
    valid_scopes = []
    for scope in scopes:
        if scope in SYSTEM_SCOPES:
            valid_scopes.append(scope)
        else:
            logging.warning(f"Invalid scope requested: {scope}")

    # Use longer expiration for refresh tokens
    default_minutes = settings.refresh_token_expire_minutes if refresh else settings.access_token_expire_minutes
    expire_delta = timedelta(minutes=expires_minutes or default_minutes)
    expire_at = datetime.utcnow() + expire_delta
    
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "scopes": valid_scopes,
        "exp": expire_at,
        "token_type": "refresh" if refresh else "access",
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16)  # Unique token ID
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(subject: str, scopes: Optional[List[str]] = None) -> str:
    """Create a refresh token with extended expiration."""
    return create_access_token(subject, scopes, refresh=True)

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_scopes(required_scopes: List[str]):
    """Factory that returns a FastAPI dependency enforcing JWT + required scopes.

    Usage:
        dependencies=[Depends(require_scopes(["scheduler"]))]
    """

    def _dependency(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme)) -> Dict[str, Any]:
        if not settings.enable_auth_routes:
            # Auth disabled -> noop (keeps local dev simple)
            return {"sub": "anonymous", "scopes": []}

        if not credentials or credentials.scheme.lower() != "bearer" or not credentials.credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        token = credentials.credentials
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        token_scopes = payload.get("scopes", [])
        if not isinstance(token_scopes, list):
            token_scopes = []

        if not set(required_scopes).issubset(set(token_scopes)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient scopes")

        return payload

    return _dependency

# Advanced security system
@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_type: str
    severity: str
    source_ip: str
    user_agent: str
    endpoint: str
    user_id: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime

@dataclass
class RateLimitRule:
    """Rate limiting rule"""
    endpoint: str
    max_requests: int
    window_seconds: int
    block_duration: int

class DataEncryption:
    """Advanced data encryption utilities"""

    @staticmethod
    def generate_key() -> str:
        """Generate a 64-character hex key (32 bytes) for compatibility with tests"""
        return secrets.token_hex(32)

    @staticmethod
    def _normalize_key(key: str) -> str:
        """Normalize provided key to a Fernet-compatible urlsafe base64 key.
        Accepts either a 64-char hex string or an existing Fernet key.
        """
        # If it looks like 64-char hex, convert to urlsafe base64
        try:
            if isinstance(key, str) and len(key) == 64:
                int(key, 16)  # validate hex
                raw = bytes.fromhex(key)
                return base64.urlsafe_b64encode(raw).decode()
        except Exception:
            pass
        # Assume it's already a valid Fernet key
        return key

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """Hash password with salt using PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(16)

        # Use PBKDF2 with SHA-256
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )

        return key.hex(), salt

    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash"""
        expected_hash, _ = DataEncryption.hash_password(password, salt)
        return hmac.compare_digest(expected_hash, hashed)

    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        """Encrypt data using Fernet symmetric encryption"""
        fernet_key = DataEncryption._normalize_key(key)
        f = Fernet(fernet_key.encode())
        return f.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_data(encrypted_data: str, key: str) -> str:
        """Decrypt data using Fernet symmetric encryption"""
        fernet_key = DataEncryption._normalize_key(key)
        f = Fernet(fernet_key.encode())
        return f.decrypt(encrypted_data.encode()).decode()

class InputValidation:
    """Advanced input validation and sanitization"""

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r';\s*--',  # Semicolon followed by comment
        r';\s*/\*',  # Semicolon followed by block comment
        r'union\s+select',  # UNION SELECT
        r'/\*.*\*/',  # Block comments
        r'--.*',  # Line comments
        r';\s*drop',  # DROP statements
        r';\s*delete',  # DELETE statements
        r';\s*update',  # UPDATE statements
        r';\s*insert',  # INSERT statements
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'on\w+\s*=',  # Event handlers
        r'<iframe[^>]*>.*?</iframe>',  # Iframe tags
        r'<object[^>]*>.*?</object>',  # Object tags
        r'<embed[^>]*>.*?</embed>',  # Embed tags
    ]

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input to prevent XSS attacks"""
        if not isinstance(input_str, str):
            return str(input_str)

        # Remove HTML tags
        sanitized = re.sub(r'<[^>]+>', '', input_str)

        # Remove JavaScript URLs
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)

        # Remove event handlers
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)

        return sanitized.strip()

    @staticmethod
    def validate_sql_input(query: str) -> bool:
        """Check for potential SQL injection attacks"""
        query_lower = query.lower()

        for pattern in InputValidation.SQL_INJECTION_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False

        return True

    @staticmethod
    def validate_math_expression(expr: str) -> bool:
        """Validate mathematical expressions for security"""
        # Allow only safe mathematical characters and common variable names
        allowed_chars = set('0123456789+-*/(). x^sqrtlogsincoetanpiabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        expr_chars = set(expr.lower())

        # Check for dangerous characters
        dangerous_chars = expr_chars - allowed_chars
        if dangerous_chars:
            return False

        # Check for potential code injection
        if any(keyword in expr.lower() for keyword in ['import', 'exec', 'eval', '__']):
            return False

        return True

class SecurityAuditor:
    """Security auditing and monitoring system"""

    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.alert_thresholds = {
            'failed_login': 5,
            'suspicious_request': 10,
            'rate_limit_exceeded': 3
        }

    def log_security_event(self, event: SecurityEvent):
        """Log a security event"""
        self.events.append(event)

        # Log to security logger
        security_logger = logging.getLogger('security')
        security_logger.log(
            getattr(logging, event.severity.upper(), logging.INFO),
            f"Security Event: {event.event_type} from {event.source_ip} - {event.details}"
        )

        # Check for alerts
        self._check_alerts(event)

    def _check_alerts(self, event: SecurityEvent):
        """Check if event triggers security alerts"""
        recent_events = [
            e for e in self.events
            if e.timestamp > datetime.now() - timedelta(minutes=5)
        ]

        # Check failed login attempts
        if event.event_type == 'failed_login':
            failed_logins = [
                e for e in recent_events
                if e.event_type == 'failed_login' and e.source_ip == event.source_ip
            ]
            if len(failed_logins) >= self.alert_thresholds['failed_login']:
                self._trigger_alert('multiple_failed_logins', event.source_ip)

        # Check suspicious requests
        if event.event_type == 'suspicious_request':
            suspicious_requests = [
                e for e in recent_events
                if e.event_type == 'suspicious_request' and e.source_ip == event.source_ip
            ]
            if len(suspicious_requests) >= self.alert_thresholds['suspicious_request']:
                self._trigger_alert('multiple_suspicious_requests', event.source_ip)

    def _trigger_alert(self, alert_type: str, source_ip: str):
        """Trigger security alert"""
        alert_logger = logging.getLogger('security_alerts')
        alert_logger.warning(f"SECURITY ALERT: {alert_type.upper()} from IP {source_ip}")

    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report"""
        now = datetime.now()
        last_24h = [e for e in self.events if e.timestamp > now - timedelta(hours=24)]

        return {
            'total_events': len(self.events),
            'events_last_24h': len(last_24h),
            'events_by_type': defaultdict(int),
            'events_by_severity': defaultdict(int),
            'top_source_ips': defaultdict(int),
            'recent_events': [
                {
                    'type': e.event_type,
                    'severity': e.severity,
                    'source_ip': e.source_ip,
                    'timestamp': e.timestamp.isoformat()
                }
                for e in last_24h[-10:]  # Last 10 events
            ]
        }

class AdvancedRateLimiter:
    """Advanced rate limiting with multiple strategies"""

    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = set()
        self.rules = self._load_default_rules()

    def _load_default_rules(self) -> List[RateLimitRule]:
        """Load default rate limiting rules"""
        return [
            RateLimitRule("/api/arithmetic/*", 100, 60, 300),  # 100 requests per minute
            RateLimitRule("/api/gpu/*", 50, 60, 600),  # 50 requests per minute
            RateLimitRule("/api/cache/*", 200, 60, 300),  # 200 requests per minute
            RateLimitRule("/api/async/*", 75, 60, 300),  # 75 requests per minute
            RateLimitRule("/api/performance/*", 150, 60, 300),  # 150 requests per minute
        ]

    def is_allowed(self, endpoint: str, client_ip: str) -> bool:
        """Check if request is allowed"""
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            return False

        # Find matching rule
        rule = self._find_matching_rule(endpoint)
        if not rule:
            return True  # No rule means no limit

        # Clean old requests
        self._clean_old_requests(client_ip, rule.window_seconds)

        # Check request count
        request_count = len(self.requests[client_ip])
        if request_count >= rule.max_requests:
            self.blocked_ips.add(client_ip)
            # Schedule unblock
            asyncio.create_task(self._schedule_unblock(client_ip, rule.block_duration))
            return False

        # Record request
        self.requests[client_ip].append(time.time())
        return True

    def _find_matching_rule(self, endpoint: str) -> Optional[RateLimitRule]:
        """Find matching rate limit rule"""
        for rule in self.rules:
            if self._matches_pattern(endpoint, rule.endpoint):
                return rule
        return None

    def _matches_pattern(self, endpoint: str, pattern: str) -> bool:
        """Check if endpoint matches pattern"""
        # Convert glob pattern to regex
        regex_pattern = pattern.replace('*', '.*')
        return re.match(regex_pattern, endpoint) is not None

    def _clean_old_requests(self, client_ip: str, window_seconds: int):
        """Clean old requests outside the window"""
        cutoff_time = time.time() - window_seconds
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff_time
        ]

    async def _schedule_unblock(self, client_ip: str, duration: int):
        """Schedule IP unblock"""
        await asyncio.sleep(duration)
        self.blocked_ips.discard(client_ip)

    def get_rate_limit_status(self, client_ip: str) -> Dict[str, Any]:
        """Get rate limit status for IP"""
        return {
            'blocked': client_ip in self.blocked_ips,
            'request_count': len(self.requests[client_ip]),
            'blocked_ips_count': len(self.blocked_ips)
        }

# Global security instances
security_auditor = SecurityAuditor()
rate_limiter = AdvancedRateLimiter()
input_validator = InputValidation()
data_encryptor = DataEncryption()

# Security decorators
def require_authentication(func: Callable) -> Callable:
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Authentication logic would go here
        # For now, just pass through
        return await func(*args, **kwargs)
    return wrapper

def audit_access(func: Callable) -> Callable:
    """Decorator to audit function access"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Audit logic would go here
        return await func(*args, **kwargs)
    return wrapper

def validate_input(func: Callable) -> Callable:
    """Decorator to validate function input"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Input validation logic would go here
        return await func(*args, **kwargs)
    return wrapper
