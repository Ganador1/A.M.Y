# 🛡 Middleware

The `app/middleware` directory contains FastAPI middleware components that process requests and responses globally.

## Stack

1.  **Trace ID (`trace_id_middleware.py`)**: Injects a unique `X-Request-ID` into every request for distributed tracing.
2.  **Security Headers (`security_headers.py`)**: Adds essential HTTP security headers (HSTS, CSP, X-Frame-Options) to protect against common web vulnerabilities.
3.  **Authentication (`auth_middleware.py`)**: Validates JWTs on protected routes and populates the request context with user information.
4.  **Profiling (`profiling.py`)**: (Optional) Middleware that captures performance profiles for requests in development or debugging modes.

## Configuration
Middleware is configured and mounted in `app/main.py` (or `app/middleware/main.py`), wrapping the core application instance.
