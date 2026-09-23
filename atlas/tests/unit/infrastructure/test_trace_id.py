"""Tests for TraceIdMiddleware using a lightweight app to avoid heavy imports.

We intentionally don't import the full 'main' application because it triggers
initialization of many heavyweight services (ML, scientific domains, etc.) that
slow down or can interfere with unit test collection. The middleware contract
is self-contained, so a minimal FastAPI instance is sufficient here.
"""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.middleware import TraceIdMiddleware, TRACE_HEADER


def _build_app():
    app = FastAPI()
    app.add_middleware(TraceIdMiddleware)

    @app.get("/trace_id")
    async def get_trace_id(request: Request):  # pragma: no cover - thin wrapper
        return {"trace_id": getattr(request.state, "trace_id", None)}

    return app


def test_trace_id_generated():
    app = _build_app()
    with TestClient(app) as client:
        r = client.get("/trace_id")
        assert r.status_code == 200
        data = r.json()
        assert "trace_id" in data and data["trace_id"]
        assert TRACE_HEADER in r.headers


def test_trace_id_propagation_header():
    app = _build_app()
    with TestClient(app) as client:
        custom = "abc123-trace"
        r = client.get("/trace_id", headers={TRACE_HEADER: custom})
        assert r.status_code == 200
        data = r.json()
        assert data["trace_id"] == custom
        assert r.headers.get(TRACE_HEADER) == custom
