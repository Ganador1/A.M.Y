import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def _env_flag(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}

def _csv_env(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]

def configure_security_middleware(app: FastAPI):
    """Install request limits, response headers, CORS and trusted-host checks."""
    from app.middleware.main import RequestSizeMiddleware, RateLimitMiddleware
    from app.middleware.security_headers import SecurityHeadersMiddleware

    max_size = int(os.getenv("MAX_REQUEST_SIZE_MB", "10")) * 1024 * 1024
    if max_size <= 0:
        raise ValueError("MAX_REQUEST_SIZE_MB must be positive")
    origins = _csv_env("ATLAS_CORS_ORIGINS", _csv_env("CORS_ORIGINS", ["http://localhost:3000"]))
    credentials = _env_flag("CORS_ALLOW_CREDENTIALS", False)
    if credentials and "*" in origins:
        raise ValueError("Credentialed CORS requires explicit origins")
    hosts = _csv_env("ATLAS_ALLOWED_HOSTS", _csv_env("TRUSTED_HOSTS", ["localhost", "127.0.0.1", "0.0.0.0"]))

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestSizeMiddleware, max_request_bytes=max_size)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(CORSMiddleware, allow_origins=origins,
                       allow_credentials=credentials, allow_methods=["*"],
                       allow_headers=["*"])
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)
