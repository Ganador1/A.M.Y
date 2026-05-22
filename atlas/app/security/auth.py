"""
Authentication module for AXIOM ATLAS
Provides JWT-based authentication and authorization with dev/prod mode toggle
"""

import os
from typing import Dict, Any, Optional, Callable, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime

# Import settings for configuration
try:
    from app.config import settings
    ENABLE_AUTH = getattr(settings, 'enable_auth_routes', os.getenv('ENABLE_AUTH', 'false').lower() == 'true')
    SECRET_KEY = getattr(settings, 'secret_key', os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'))
    ALGORITHM = "HS256"
except Exception:
    # Fallback if settings not available
    ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
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
