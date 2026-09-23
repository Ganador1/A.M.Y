"""
Authentication module for AXIOM ATLAS
Provides JWT-based authentication and authorization with dev/prod mode toggle
"""

import os
import secrets
from typing import Dict, Any, Optional, Callable, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime

WEAK_SECRET_SENTINELS = {
    "",
    "changeme",
    "change-me",
    "secret",
    "dev-" + "secret-key-change-in-production",
}


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_production_mode() -> bool:
    return os.getenv("ATLAS_ENV", os.getenv("ENVIRONMENT", "development")).strip().lower() in {
        "prod",
        "production",
    }


def _resolve_enable_auth(settings_obj: Any = None) -> bool:
    explicit = os.getenv("ENABLE_AUTH") or os.getenv("ENABLE_AUTH_ROUTES")
    if explicit is not None:
        explicit_enabled = explicit.strip().lower() in {"1", "true", "yes", "on"}
        if _is_production_mode() and not explicit_enabled:
            return False if _env_flag("ATLAS_ALLOW_AUTH_DISABLED_IN_PRODUCTION", False) else True
        return explicit_enabled

    configured = getattr(settings_obj, "enable_auth_routes", None)
    if configured is not None and bool(configured):
        return True
    if _is_production_mode() and not _env_flag("ATLAS_ALLOW_AUTH_DISABLED_IN_PRODUCTION", False):
        return True
    return bool(configured) if configured is not None else False


def _resolve_secret_key(settings_obj: Any = None) -> str:
    configured = os.getenv("SECRET_KEY") or getattr(settings_obj, "secret_key", None)
    if configured and str(configured) not in WEAK_SECRET_SENTINELS:
        return str(configured)
    if _is_production_mode():
        raise RuntimeError("SECRET_KEY must be explicitly configured in production")
    return secrets.token_urlsafe(32)


# Import settings for configuration.
try:
    from app.config import settings
except Exception:
    settings = None  # type: ignore

ENABLE_AUTH = _resolve_enable_auth(settings)
SECRET_KEY = _resolve_secret_key(settings)
ALGORITHM = "HS256"

# Security scheme
security = HTTPBearer(auto_error=False)


def validate_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate JWT token and return decoded payload.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            return None
            
        return payload
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    
    In development mode (ENABLE_AUTH=false), returns a mock admin user.
    In production mode, validates JWT token.
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        
    Returns:
        User information dict with username and scopes
        
    Raises:
        HTTPException: 401 if authentication fails (production only)
    """
    # Development mode - return mock admin user
    if not ENABLE_AUTH:
        return {
            "sub": "dev_user",
            "username": "dev_user",
            "scopes": ["system:admin", "system:read", "research:execute", 
                      "lab:equipment", "sandbox:execute", "metrics:read"],
        }
    
    # Production mode - validate token
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = validate_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


def require_scopes(required_scopes: List[str]) -> Callable:
    """
    Dependency function to require specific scopes.
    
    In development mode, always succeeds.
    In production mode, validates token and checks scopes.
    
    Args:
        required_scopes: List of required scope strings
        
    Returns:
        FastAPI dependency function
        
    Example:
        @router.get("/admin", dependencies=[Depends(require_scopes(["system:admin"]))])
        async def admin_endpoint():
            ...
    """
    async def dependency(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        # Development mode - always allow
        if not ENABLE_AUTH:
            return current_user
        
        # Production mode - check scopes
        user_scopes = current_user.get("scopes", [])
        
        # Check if user has all required scopes
        for scope in required_scopes:
            if scope not in user_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required scope: {scope}",
                )
        
        return current_user
    
    return dependency


__all__ = [
    "security",
    "validate_token",
    "get_current_user",
    "require_scopes",
    "ENABLE_AUTH",
]
