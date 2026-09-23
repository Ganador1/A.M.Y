"""Real ASGI requests; run with the Atlas optional dependencies installed."""
from pathlib import Path
import sys
import pytest
pytest.importorskip('fastapi')
pytest.importorskip('slowapi')
pytest.importorskip('redis')
pytest.importorskip('psutil')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'atlas'))
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from app.middleware.setup import configure_security_middleware


def test_real_middleware_requests(monkeypatch):
    monkeypatch.setenv('ATLAS_ALLOWED_HOSTS','localhost')
    monkeypatch.setenv('ATLAS_CORS_ORIGINS','https://allowed.example')
    monkeypatch.setenv('MAX_REQUEST_SIZE_MB','1')
    monkeypatch.setenv('CORS_ALLOW_CREDENTIALS','false')
    app=FastAPI()
    @app.get('/health')
    def health():return JSONResponse({'status':'ok'},headers={'server':'private-server','x-powered-by':'private-framework'})
    configure_security_middleware(app)
    with TestClient(app,base_url='http://localhost') as client:
        r=client.get('/health')
        assert r.status_code==200
        assert r.headers['x-content-type-options']=='nosniff'
        assert 'server' not in r.headers and 'x-powered-by' not in r.headers
        assert client.get('/health',headers={'host':'untrusted.example'}).status_code==400
        assert client.post('/health',headers={'content-length':'2000000'}).status_code==413
        r=client.options('/health',headers={'origin':'https://allowed.example','access-control-request-method':'GET'})
        assert r.status_code==200 and r.headers['access-control-allow-origin']=='https://allowed.example'
        assert client.options('/health',headers={'origin':'https://untrusted.example','access-control-request-method':'GET'}).status_code==400
