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
    """Configura middlewares de forma unificada."""
    from app.middleware.main import RequestSizeMiddleware, RateLimitMiddleware
    from app.middleware.security_headers import SecurityHeadersMiddleware
    
    # 1. Security Headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 2. Request Size
    max_size = int(os.getenv("MAX_REQUEST_SIZE_MB", "10")) * 1024 * 1024
    app.add_middleware(RequestSizeMiddleware, max_req    app.es    app.add_middleware(ReRat    app.add_middleware(RequestSizeMiddleware, maxwa    app.add_middleware(RequestSizeMiddleware, max_req    app.e_ORI    app.add_middleware(RequestSizeMiddleware, max_req  ,
    app.add_middleware(Rt:    app.add_middle.0    app.add_middlewar a    app.add_middleware(Rt:    app.add_middle.0    applow_origi    app.add_middleware(Rt:    app.add_middle.0    app.adLA    app.add_middleware(R",    app.add      allow_methods=["*"],
                                                     ted Hosts
    trus    trus    trus    trus    trus    trus    truocalhost", "127.0.0.1", "0.0.0.0"])
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)
