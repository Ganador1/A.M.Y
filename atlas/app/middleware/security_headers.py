"""
Security Headers Middleware - AXIOM ATLAS
=========================================

Middleware para agregar headers de seguridad HTTP estándar.
Implementa las mejores prácticas de seguridad web.

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad HTTP"""

    def __init__(self, app, csp_policy: str = None):
        super().__init__(app)
        
        # Content Security Policy por defecto
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Procesar request y agregar headers de seguridad"""
        response = await call_next(request)
        
        # Headers de seguridad estándar
        security_headers = {
            # Prevenir MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevenir clickjacking
            "X-Frame-Options": "DENY",
            
            # Protección XSS (legacy pero aún útil)
            "X-XSS-Protection": "1; mode=block",
            
            # HTTPS Strict Transport Security
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Content Security Policy
            "Content-Security-Policy": self.csp_policy,
            
            # Control de referrer
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions Policy (anteriormente Feature Policy)
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=(), "
                "vibrate=(), "
                "fullscreen=(self), "
                "payment=(), "
                "accelerometer=(), "
                "ambient-light-sensor=(), "
                "autoplay=(), "
                "battery=(), "
                "display-capture=(), "
                "document-domain=(), "
                "encrypted-media=(), "
                "execution-while-not-rendered=(), "
                "execution-while-out-of-viewport=(), "
                "font-display-late-swap=(), "
                "layout-animations=(), "
                "legacy-image-formats=(), "
                "loading-frame-default-eager=(), "
                "loading-image-default-eager=(), "
                "loading-text-track-default-eager=(), "
                "media-playback-rate=(), "
                "notifications=(), "
                "oversized-images=(), "
                "picture-in-picture=(), "
                "publickey-credentials-get=(), "
                "screen-wake-lock=(), "
                "sync-script=(), "
                "sync-xhr=(), "
                "unoptimized-images=(), "
                "unsized-media=(), "
                "vertical-scroll=(), "
                "wake-lock=(), "
                "xr-spatial-tracking=()"
            ),
            
            # Cross-Origin Embedder Policy
            "Cross-Origin-Embedder-Policy": "require-corp",
            
            # Cross-Origin Opener Policy
            "Cross-Origin-Opener-Policy": "same-origin",
            
            # Cross-Origin Resource Policy
            "Cross-Origin-Resource-Policy": "same-origin",
            
            # Cache Control para respuestas sensibles
            "Cache-Control": "no-store, no-cache, must-revalidate, private",
            
            # Pragma para compatibilidad con HTTP/1.0
            "Pragma": "no-cache",
            
            # Expires para prevenir caché
            "Expires": "0"
        }
        
        # Agregar headers de seguridad
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Remover headers que pueden revelar información del servidor
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)
        
        # Log de headers agregados (solo en desarrollo)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Security headers added to {request.url.path}")
        
        return response


class SecurityHeadersConfig:
    """Configuración para headers de seguridad"""
    
    # CSP policies predefinidas
    CSP_POLICIES = {
        "strict": (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self'; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        ),
        
        "moderate": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        ),
        
        "development": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    }
    
    @classmethod
    def get_csp_policy(cls, environment: str = "production") -> str:
        """Obtener política CSP según el entorno"""
        return cls.CSP_POLICIES.get(environment, cls.CSP_POLICIES["moderate"])
    
    @classmethod
    def create_custom_csp(cls, **kwargs) -> str:
        """Crear política CSP personalizada"""
        directives = []
        
        for directive, sources in kwargs.items():
            if sources:
                if isinstance(sources, list):
                    sources_str = " ".join(sources)
                else:
                    sources_str = sources
                directives.append(f"{directive} {sources_str}")
        
        return "; ".join(directives)


# Función helper para configurar middleware
def setup_security_headers(app, environment: str = "production", custom_csp: str = None):
    """Configurar middleware de security headers"""
    
    # Determinar política CSP
    if custom_csp:
        csp_policy = custom_csp
    else:
        csp_policy = SecurityHeadersConfig.get_csp_policy(environment)
    
    # Agregar middleware
    app.add_middleware(SecurityHeadersMiddleware, csp_policy=csp_policy)
    
    logger.info(f"Security headers middleware configured for {environment} environment")
