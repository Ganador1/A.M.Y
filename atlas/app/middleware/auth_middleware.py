"""
Authentication Middleware for AXIOM ATLAS
Validates JWT tokens and enforces authentication on protected endpoints.
"""

from typing import Optional, Dict, Any
import logging

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.core.jwt_handler import verify_token

logger = logging.getLogger(__name__)

# HTTP Bearer scheme for JWT
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user from JWT token.

    Usage:
        @router.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            user_id = current_user['sub']
            role = current_user['role']
            ...

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        User data from JWT payload

    Raises:
        HTTPException: If token is invalid or missing
    """
    if not credentials:
        logger.warning("No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = verify_token(token)

        if not payload:
            logger.warning("Token verification returned None")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate token type is access token
        if payload.get("type") != "access":
            logger.warning("Invalid token type: %s", payload.get("type"))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        logger.error("JWT validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_optional_user(
    request: Request
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, None otherwise.

    Useful for endpoints that are public but provide enhanced features
    when authenticated.

    Usage:
        @router.get("/public-or-enhanced")
        async def public_route(current_user: Optional[dict] = Depends(get_optional_user)):
            if current_user:
                # Authenticated - provide enhanced features
                ...
            else:
                # Public - basic features
                ...

    Args:
        request: FastAPI request object

    Returns:
        User data if authenticated, None otherwise
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")

    try:
        payload = verify_token(token)

        if payload and payload.get("type") == "access":
            return payload

    except JWTError:
        # Silent fail for optional authentication
        pass

    return None


def extract_token_from_header(authorization: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        Token string or None
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    return authorization.replace("Bearer ", "")


async def verify_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Verify refresh token specifically.

    Used in token refresh endpoint to validate refresh tokens.

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        User data from refresh token

    Raises:
        HTTPException: If refresh token is invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
        )

    token = credentials.credentials

    try:
        payload = verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Validate token type is refresh token
        if payload.get("type") != "refresh":
            logger.warning("Invalid token type for refresh: %s", payload.get("type"))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Refresh token required.",
            )

        return payload

    except JWTError as e:
        logger.error("Refresh token validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from e
