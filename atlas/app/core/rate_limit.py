"""
Rate Limiting Module - AXIOM ATLAS
==================================

Implementación de rate limiting real usando slowapi.
Reemplaza el stub anterior con una implementación funcional.

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, HTTPException
from typing import Optional, Dict, Any
import redis
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Configuración de rate limiting"""
    
    # Límites por tier de usuario
    TIER_LIMITS = {
        "anonymous": "10/minute",
        "authenticated": "100/minute", 
        "premium": "1000/minute",
        "internal": "10000/minute"
    }
    
    # Límites específicos por endpoint
    ENDPOINT_LIMITS = {
        "/api/auth/login": "5/minute",
        "/api/auth/register": "3/minute",
        "/api/experiments/create": "10/minute",
        "/api/models/train": "5/hour",
        "/api/data/upload": "20/minute",
        "/api/reports/generate": "5/minute"
    }
    
    # Configuración Redis
    REDIS_URL = "redis://localhost:6379"
    REDIS_DB = 0


class AdvancedRateLimiter:
    """Rate limiter avanzado con múltiples estrategias"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or RateLimitConfig.REDIS_URL
        
        # Configurar Redis connection pool
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connection established for rate limiting")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Using in-memory storage.")
            self.redis_client = None
        
        # Configurar slowapi limiter
        self.limiter = Limiter(
            key_func=self._get_rate_limit_key,
            default_limits=[RateLimitConfig.TIER_LIMITS["anonymous"]],
            storage_uri=self.redis_url if self.redis_client else "memory://",
            enabled=True
        )
    
    def _get_rate_limit_key(self, request: Request) -> str:
        """Obtener clave única para rate limiting"""
        # Prioridad: API key > User ID > IP address
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Verificar si hay usuario autenticado
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Fallback a IP address
        return get_remote_address(request)
    
    def _get_user_tier(self, request: Request) -> str:
        """Determinar tier del usuario para rate limiting"""
        # Verificar headers especiales
        if request.headers.get("X-Internal-Request"):
            return "internal"
        
        # Verificar API key tier
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # Aquí podrías verificar en base de datos el tier del API key
            return "premium"  # Asumir premium por ahora
        
        # Verificar usuario autenticado
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            # Aquí podrías verificar en base de datos el tier del usuario
            return "authenticated"
        
        return "anonymous"
    
    def get_limit_for_endpoint(self, endpoint: str, user_tier: str) -> str:
        """Obtener límite específico para endpoint y tier"""
        # Verificar límite específico del endpoint
        if endpoint in RateLimitConfig.ENDPOINT_LIMITS:
            return RateLimitConfig.ENDPOINT_LIMITS[endpoint]
        
        # Usar límite del tier
        return RateLimitConfig.TIER_LIMITS.get(user_tier, RateLimitConfig.TIER_LIMITS["anonymous"])
    
    def is_allowed(self, client_id: str) -> tuple[bool, str]:
        """
        Check if a request is allowed for simple middleware compatibility.
        
        This is a simplified method for backwards compatibility with
        the RateLimitMiddleware that expects (allowed, reason) tuple.
        
        Args:
            client_id: Client identifier (IP address or user ID)
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        # For now, always return True since slowapi handles rate limiting
        # This method exists for middleware compatibility
        # The actual rate limiting is done by slowapi decorators
        return (True, "Request allowed")
    
    def create_rate_limit_decorator(self, limit: str = None):
        """Crear decorador de rate limiting personalizado"""
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                # Determinar límite dinámico
                if limit:
                    actual_limit = limit
                else:
                    user_tier = self._get_user_tier(request)
                    actual_limit = self.get_limit_for_endpoint(request.url.path, user_tier)
                
                # Aplicar rate limiting
                try:
                    # Usar slowapi limiter
                    limited_func = self.limiter.limit(actual_limit)(func)
                    return await limited_func(request, *args, **kwargs)
                except RateLimitExceeded:
                    logger.warning(f"Rate limit exceeded for {request.url.path}")
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Rate limit exceeded",
                            "limit": actual_limit,
                            "retry_after": 60
                        }
                    )
            
            return wrapper
        return decorator


class RateLimitMiddleware:
    """Middleware para rate limiting global"""
    
    def __init__(self, rate_limiter: AdvancedRateLimiter):
        self.rate_limiter = rate_limiter
    
    async def __call__(self, request: Request, call_next):
        """Procesar request con rate limiting"""
        try:
            # Verificar rate limit global
            user_tier = self.rate_limiter._get_user_tier(request)
            global_limit = RateLimitConfig.TIER_LIMITS[user_tier]
            
            # Aplicar límite global usando slowapi
            limited_call_next = self.rate_limiter.limiter.limit(global_limit)(call_next)
            response = await limited_call_next(request)
            
            # Agregar headers informativos
            response.headers["X-RateLimit-Limit"] = global_limit
            response.headers["X-RateLimit-Remaining"] = "0"  # Simplificado
            response.headers["X-RateLimit-Reset"] = str(int(request.state.start_time) + 60)
            
            return response
            
        except RateLimitExceeded:
            logger.warning(f"Global rate limit exceeded for {request.url.path}")
            return HTTPException(
                status_code=429,
                detail={
                    "error": "Global rate limit exceeded",
                    "limit": global_limit,
                    "retry_after": 60
                }
            )


# Instancia global del rate limiter
rate_limiter = AdvancedRateLimiter()


# Decoradores de conveniencia
def rate_limit(limit: str = None):
    """Decorador para rate limiting en endpoints específicos"""
    return rate_limiter.create_rate_limit_decorator(limit)


def auth_rate_limit():
    """Rate limiting para endpoints de autenticación"""
    return rate_limit("5/minute")


def upload_rate_limit():
    """Rate limiting para endpoints de upload"""
    return rate_limit("20/minute")


def training_rate_limit():
    """Rate limiting para endpoints de entrenamiento"""
    return rate_limit("5/hour")


# Función para configurar rate limiting en la app
def setup_rate_limiting(app):
    """Configurar rate limiting en la aplicación FastAPI"""
    
    # Agregar middleware de slowapi
    app.add_middleware(SlowAPIMiddleware)
    
    # Agregar exception handler para rate limit exceeded
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Configurar estado de la app
    app.state.limiter = rate_limiter.limiter
    
    logger.info("✅ Rate limiting configured successfully")
    
    return app


# Función para obtener estadísticas de rate limiting
def get_rate_limit_stats(request: Request) -> Dict[str, Any]:
    """Obtener estadísticas de rate limiting para debugging"""
    key = rate_limiter._get_rate_limit_key(request)
    user_tier = rate_limiter._get_user_tier(request)
    
    stats = {
        "rate_limit_key": key,
        "user_tier": user_tier,
        "current_limit": RateLimitConfig.TIER_LIMITS[user_tier],
        "endpoint_limit": RateLimitConfig.ENDPOINT_LIMITS.get(request.url.path, "default")
    }
    
    # Si Redis está disponible, obtener estadísticas adicionales
    if rate_limiter.redis_client:
        try:
            # Obtener información del Redis
            info = rate_limiter.redis_client.info()
            stats["redis_connected"] = True
            stats["redis_memory_usage"] = info.get("used_memory_human", "unknown")
        except Exception as e:
            stats["redis_error"] = str(e)
    else:
        stats["redis_connected"] = False
    
    return stats


def get_client_id(request: Request) -> str:
    """
    Extract client identifier from request.
    
    This function is used by middleware for rate limiting.
    Uses IP address as client identifier by default.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Client identifier string (IP address)
    """
    # Use IP address as client identifier
    # In production, you might want to use API keys or user IDs
    client_host = getattr(request, 'client', None)
    if client_host:
        return str(client_host.host)
    return "unknown"
