"""Trace ID utilities for correlating logs, feedback and metrics.
Lightweight: stores trace_id in an object context passed explicitly (no contextvars overhead yet).
Future: can evolve to contextvars or OpenTelemetry integration.
"""
from __future__ import annotations
import uuid
from typing import MutableMapping

TRACE_KEY = "trace_id"


def get_or_create_trace(context: MutableMapping[str, str] | None, fallback: str | None = None) -> str:
    if context is None:
        if fallback:
            return fallback
        return str(uuid.uuid4())
    if TRACE_KEY not in context or not context[TRACE_KEY]:
        context[TRACE_KEY] = fallback or str(uuid.uuid4())
    return context[TRACE_KEY]


# --- Optional OpenTelemetry initialization (defensive) ---

def init_tracing(app) -> bool:
    """
    Initialize OpenTelemetry tracing if enabled and dependencies are available.
    - Instruments FastAPI app and optionally httpx client.
    - Uses OTLP exporter if endpoint provided, otherwise console exporter.
    Returns True if instrumentation was initialized, False otherwise.
    """
    try:
        from app.core.config import settings
        if not getattr(settings, "enable_otel", False):
            return False

        # Lazy imports to avoid ImportError when OTEL is not installed
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        except Exception:
            # OTEL not installed
            return False

        # Tracer provider with service name
        service_name = getattr(settings, "otel_service_name", "axiom-meta4")
        sampler_ratio = float(getattr(settings, "otel_sampler_ratio", 1.0))

        # Sampler configuration (parent-based + ratio)
        try:
            from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
            sampler = ParentBased(TraceIdRatioBased(sampler_ratio))
        except Exception:
            sampler = None

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource, sampler=sampler)

        # Exporter selection
        processor = None
        try:
            otlp_endpoint = getattr(settings, "otel_exporter_otlp_endpoint", None)
            if otlp_endpoint:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HttpOTLPExporter
                exporter = HttpOTLPExporter(endpoint=otlp_endpoint)
            else:
                exporter = ConsoleSpanExporter()
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)
        except Exception:
            # Fallback to console exporter if OTLP HTTP exporter not available
            try:
                exporter = ConsoleSpanExporter()
                processor = BatchSpanProcessor(exporter)
                provider.add_span_processor(processor)
            except Exception:
                pass

        trace.set_tracer_provider(provider)

        # Instrument FastAPI
        try:
            FastAPIInstrumentor.instrument_app(app)
        except Exception:
            # As a last resort try global instrumentation
            try:
                FastAPIInstrumentor().instrument()
            except Exception:
                pass

        # Optional httpx instrumentation
        try:
            from app.core.config import settings as _s
            if getattr(_s, "otel_instrument_httpx", True):
                try:
                    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
                    HTTPXClientInstrumentor().instrument()
                except Exception:
                    pass
        except Exception:
            pass

        return True
    except Exception:
        return False
