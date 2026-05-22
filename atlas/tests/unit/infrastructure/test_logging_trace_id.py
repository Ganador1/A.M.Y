"""Test that LoggingMiddleware añade trace_id en los logs."""

import io
import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware import TraceIdMiddleware, LoggingMiddleware
from app.logging_config import logger


def _build_app():
    app = FastAPI()
    app.add_middleware(TraceIdMiddleware)
    app.add_middleware(LoggingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    return app


def test_logging_includes_trace_id():
    # Capturar logs en memoria
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    try:
        app = _build_app()
        with TestClient(app) as client:
            r = client.get("/ping")
            assert r.status_code == 200
        handler.flush()
        contents = log_stream.getvalue()
        # Debe contener la clave trace_id=
        assert "trace_id=" in contents
    finally:
        logger.removeHandler(handler)