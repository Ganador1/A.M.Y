"""
Rate Limiting Integration for FastAPI Application
Integrates slowapi rate limiter with the main FastAPI app.
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
import logging

from app.core.rate_limiter import limiter, ip_limiter, configure_redis_storage
from app.core.config import settings

logger = logging.getLogger(__name__)


def setup_rate_limiting(app: FastAPI) -> None:
    """
    Configure rate limiting for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Example:
        ```python
        from app.core.rate_limit_setup import setup_rate_limiting
        
        app = FastAPI()
        setup_rate_limiting(app)
        ```
    """
    # Add rate limiter to app state
    app.state.limiter = limiter
    
    # Add exception handler for rate limit exceeded
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore[arg-type]
    
    # Configure Redis if available
    if hasattr(settings, 'redis_url') and settings.redis_url:
        logger.info("Configuring rate limiter with Redis: %s", settings.redis_url)
        configure_redis_storage(settings.redis_url)
    else:
        logger.info("Using in-memory rate limiting (suitable for single-worker deployment)")
    
    logger.info("Rate limiting configured successfully")


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    
    Returns JSON response with retry information.
    
    Args:
        request: FastAPI request
        exc: Rate limit exception
        
    Returns:
        JSON response with 429 status code
    """
    logger.warning(
        "Rate limit exceeded for %s on %s",
        request.client.host if request.client else "unknown",
        request.url.path
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail),
            "retry_after": getattr(exc, "retry_after", None)
        },
        headers={
            "Retry-After": str(getattr(exc, "retry_after", 60))
        }
    )


# Export limiters and constants for use in routers
__all__ = [
    "setup_rate_limiting",
    "limiter",
    "ip_limiter",
    "rate_limit_exceeded_handler"
]
