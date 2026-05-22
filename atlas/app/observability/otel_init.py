from __future__ import annotations

import os
from typing import Optional

# OpenTelemetry imports - made conditional
try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    # Create dummy classes/functions for when opentelemetry is not available
    class DummyTracerProvider:
        pass
    
    class DummyTrace:
        def set_tracer_provider(self, provider):
            pass
    
    trace = DummyTrace()

from app.core.config import settings
from app.config import settings


def init_tracing(app=None) -> Optional[TracerProvider]:
    """Initialize OpenTelemetry tracing if enabled by environment.

    Env vars (suggested):
      - OTEL_EXPORTER_OTLP_ENDPOINT (e.g., http://localhost:4318)
      - OTEL_SERVICE_NAME
      - OTEL_ENABLED=true|false
    """
    if not OPENTELEMETRY_AVAILABLE:
        return None
        
    enabled = settings.OTEL_ENABLED, "false").lower() == "true"
    if not enabled:
        return None

    service_name = settings.OTEL_SERVICE_NAME, "axiom-meta4")
    endpoint = settings.OTEL_EXPORTER_OTLP_ENDPOINT, "http://localhost:4318")

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Instrument FastAPI if app provided
    if app is not None:
        try:
            FastAPIInstrumentor.instrument_app(app)
            # Ensure ASGI-level coverage as well
            app.add_middleware(OpenTelemetryMiddleware)
        except Exception:
            pass

    # Instrument httpx outbound
    try:
        HTTPXClientInstrumentor().instrument()
    except Exception:
        pass

    return provider
