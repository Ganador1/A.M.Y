"""
AXIOM Middleware
Custom middleware for the Mathematics AI Engine
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import gzip
import hashlib
from app.core.rate_limit import rate_limiter, get_client_id
from app.core.bootstrap_logging import log_api_request
from app.monitoring.health import health_checker


class CompressionMiddleware(BaseHTTPMiddleware):
    """Response compression middleware"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Check if client accepts gzip compression
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding:
            return response

        # Only compress JSON responses and responses larger than 1KB
        if (hasattr(response, 'body') and
            response.headers.get("content-type", "").startswith("application/json") and
            len(response.body) > 1024):

            # Compress the response body
            compressed_body = gzip.compress(response.body)

            # Create new response with compressed body
            compressed_response = Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=dict(response.headers)
            )

            # Update headers
            compressed_response.headers["Content-Encoding"] = "gzip"
            compressed_response.headers["Content-Length"] = str(len(compressed_body))

            return compressed_response

        return response


class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    """Circuit breaker middleware for external service calls"""

    def __init__(self, app, failure_threshold: int = 5, recovery_timeout: int = 60):
        super().__init__(app)
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def dispatch(self, request: Request, call_next):
        # Check if circuit breaker is open
        if self.state == "OPEN":
            current_time = time.time()
            if current_time - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": "Service Unavailable",
                        "message": "Circuit breaker is open. Service temporarily unavailable.",
                        "retry_after": int(self.recovery_timeout - (current_time - self.last_failure_time))
                    }
                )

        try:
            response = await call_next(request)

            # Success - reset circuit breaker
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            elif self.state == "CLOSED":
                self.failure_count = max(0, self.failure_count - 1)

            return response

        except Exception:
            # Failure - increment counter
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"

            raise


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limits maximum request size using Content-Length header.

    Mitigación de DoS por formularios/multipart excesivos cuando no se dispone aún
    de versiones parcheadas de dependencias. Rechaza con 413 si el tamaño supera el límite.
    """

    def __init__(self, app, max_request_bytes: int = 5 * 1024 * 1024):
        super().__init__(app)
        self.max_request_bytes = max_request_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        try:
            if content_length is not None and int(content_length) > self.max_request_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "Request Too Large",
                        "message": "Payload exceeds server limit",
                        "limit_bytes": self.max_request_bytes,
                    },
                )
        except ValueError:
            # Si el header es inválido, continúa y deja que Starlette gestione
            pass

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static files
        if request.url.path.startswith(("/health", "/static", "/docs", "/redoc", "/openapi.json")):
            return await call_next(request)

        client_id = get_client_id(request)
        allowed, reason = rate_limiter.is_allowed(client_id)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": reason,
                    "retry_after": 60
                }
            )

        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Increment request counter
        health_checker.increment_request()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log successful request
            trace_id = getattr(request.state, "trace_id", None)
            log_api_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration,
                trace_id=trace_id
            )

            return response

        except Exception:
            duration = time.time() - start_time
            health_checker.increment_error()

            # Log error
            trace_id = getattr(request.state, "trace_id", None)
            log_api_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=500,
                duration=duration,
                trace_id=trace_id
            )

            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers (baseline)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # HSTS: 2 años + preload
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        # Referrer y permisos modernos
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )
        # COOP/CORP para aislar contexto
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # CSP (compat con tests actuales): mantener valor base
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


# --- API Versioning Alias Middleware ---
class VersionPrefixMiddleware(BaseHTTPMiddleware):
    """
    Permite introducir la versión canónica /api/v1 sin romper compatibilidad:
    - Reescribe internamente peticiones a /api/v1/* -> /api/* para aprovechar routers actuales
    - Añade cabecera X-API-Version: v1 a las respuestas de rutas versionadas
    - Marca el alias /api/* como deprecado mediante header Deprecation
    """

    async def dispatch(self, request: Request, call_next):
        original_path = request.scope.get("path", "")
        v1_prefix = "/api/v1"
        used_v1 = False

        # Si viene por /api/v1 o /api/v1/*, reescribir a /api/*
        if original_path == v1_prefix:
            new_path = "/api"
            used_v1 = True
        elif original_path.startswith(v1_prefix + "/"):
            new_path = "/api" + original_path[len(v1_prefix):]
            used_v1 = True
        else:
            new_path = original_path

        if new_path != original_path:
            # Reescribir path y raw_path
            request.scope["path"] = new_path
            request.scope["raw_path"] = new_path.encode()

        response = await call_next(request)

        # Señalizar versión utilizada y deprecación del alias /api
        if used_v1:
            response.headers["X-API-Version"] = "v1"
        elif original_path.startswith("/api/") or original_path == "/api":
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = "Sat, 31 May 2025 23:59:59 GMT"
            response.headers["Link"] = "</api/v1>; rel=alternate"

        return response


class CacheMiddleware(BaseHTTPMiddleware):
    """Advanced response caching middleware with Redis support"""

    def __init__(self, app):
        super().__init__(app)
        from app.core.cache import cache as global_cache
        self.cache = global_cache

    def _get_cache_key(self, request: Request) -> str:
        """Generate cache key from request using SHA-256 (non-crypto security)."""
        key_data = f"{request.method}:{request.url.path}:{request.url.query}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _is_cacheable(self, request: Request) -> bool:
        """Check if request should be cached"""
        # Only cache GET requests
        if request.method != "GET":
            return False

        # Don't cache health checks, docs, or admin endpoints
        non_cacheable_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/static", "/metrics", "/stats"]
        if any(request.url.path.startswith(path) for path in non_cacheable_paths):
            return False

        return True

    async def dispatch(self, request: Request, call_next):
        if not self._is_cacheable(request):
            return await call_next(request)

        cache_key = self._get_cache_key(request)

        # Check if we have a cached response
        cached_data = self.cache.get(cache_key)
        if cached_data:
            # Return cached response
            return Response(
                content=cached_data["content"],
                status_code=cached_data["status_code"],
                headers=cached_data["headers"]
            )

        # Get fresh response
        response = await call_next(request)

        # Cache the response if successful
        if response.status_code == 200 and hasattr(response, 'body'):
            try:
                cache_data = {
                    "content": response.body,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
                self.cache.set(cache_key, cache_data)
            except Exception:
                # If caching fails, just continue without caching
                pass

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Enhanced error handling middleware"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except HTTPException as http_exc:
            # Handle HTTP exceptions with proper JSON response
            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "error": "HTTP Exception",
                    "message": http_exc.detail,
                    "status_code": http_exc.status_code
                }
            )

        except ValueError as val_exc:
            # Handle validation errors
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation Error",
                    "message": str(val_exc),
                    "status_code": 400
                }
            )

        except Exception:
            # Handle unexpected errors
            health_checker.increment_error()

            # Log the error
            trace_id = getattr(request.state, "trace_id", None)
            log_api_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=500,
                duration=0,
                trace_id=trace_id
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "status_code": 500
                }
            )


# Backwards-compatible alias expected by some imports
RequestSizeMiddleware = RequestSizeLimitMiddleware
