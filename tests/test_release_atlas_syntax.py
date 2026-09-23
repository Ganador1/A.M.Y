"""Release blockers: legacy syntax and reconstructed middleware configuration."""
from pathlib import Path
import ast
import importlib.util
import sys
import types
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_atlas_python_sources_parse():
    for path in (ROOT / 'atlas/app').rglob('*.py'):
        ast.parse(path.read_text(), filename=str(path.relative_to(ROOT)))


@pytest.fixture
def middleware(monkeypatch):
    for key in ('MAX_REQUEST_SIZE_MB', 'CORS_ORIGINS', 'CORS_ALLOW_CREDENTIALS', 'TRUSTED_HOSTS', 'ATLAS_ALLOWED_HOSTS', 'ATLAS_CORS_ORIGINS'):
        monkeypatch.delenv(key, raising=False)
    # Unit-test configuration assembly without importing the optional ASGI stack.
    for name, cls in [('fastapi', 'FastAPI'), ('fastapi.middleware.cors', 'CORSMiddleware'), ('fastapi.middleware.trustedhost', 'TrustedHostMiddleware')]:
        stub = types.ModuleType(name)
        setattr(stub, cls, type(cls, (), {}))
        monkeypatch.setitem(sys.modules, name, stub)
    main = types.ModuleType('app.middleware.main')
    main.RequestSizeMiddleware = type('RequestSizeMiddleware', (), {})
    main.RateLimitMiddleware = type('RateLimitMiddleware', (), {})
    headers = types.ModuleType('app.middleware.security_headers')
    headers.SecurityHeadersMiddleware = type('SecurityHeadersMiddleware', (), {})
    monkeypatch.setitem(sys.modules, main.__name__, main)
    monkeypatch.setitem(sys.modules, headers.__name__, headers)
    spec = importlib.util.spec_from_file_location('release_middleware_setup', ROOT / 'atlas/app/middleware/setup.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    class App:
        def __init__(self): self.calls = []
        def add_middleware(self, cls, **kwargs): self.calls.append((cls.__name__, kwargs))
    return module, App()


def test_middleware_installs_limits_and_host_checks(middleware, monkeypatch):
    module, app = middleware
    monkeypatch.setenv('MAX_REQUEST_SIZE_MB', '2')
    monkeypatch.setenv('CORS_ORIGINS', 'https://example.org, https://example.com')
    monkeypatch.setenv('CORS_ALLOW_CREDENTIALS', 'true')
    module.configure_security_middleware(app)
    calls = dict(app.calls)
    assert calls['RequestSizeMiddleware']['max_request_bytes'] == 2 * 1024 * 1024
    assert calls['CORSMiddleware']['allow_origins'] == ['https://example.org', 'https://example.com']
    assert calls['CORSMiddleware']['allow_credentials'] is True
    assert calls['TrustedHostMiddleware']['allowed_hosts'] == ['localhost', '127.0.0.1', '0.0.0.0']
    assert 'RateLimitMiddleware' in calls and 'SecurityHeadersMiddleware' in calls


@pytest.mark.parametrize('settings', [dict(MAX_REQUEST_SIZE_MB='0'), dict(CORS_ORIGINS='*', CORS_ALLOW_CREDENTIALS='true')])
def test_invalid_middleware_config_fails_before_registration(middleware, monkeypatch, settings):
    module, app = middleware
    for key, value in settings.items(): monkeypatch.setenv(key, value)
    with pytest.raises(ValueError): module.configure_security_middleware(app)
    assert not app.calls
