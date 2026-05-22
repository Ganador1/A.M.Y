"""
AXIOM ATLAS - OpenTelemetry Enhanced Configuration
Configuración mejorada para distributed tracing con Jaeger
"""

import os
import logging
from typing import Optional
from opentelemetry import trace
from opentelemetry import metrics
from opentelemetry import baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.console import ConsoleSpanExporter, ConsoleMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from app.config import settings


logger = logging.getLogger(__name__)


class AxiomTelemetry:
    """Configuración centralizada de telemetría para AXIOM ATLAS"""

    def __init__(self):
        self.service_name = settings.SERVICE_NAME, "axiom-atlas")
        self.service_version = settings.SERVICE_VERSION, "1.0.0")
        self.environment = settings.SENTRY_ENVIRONMENT, "development")

        # Configuración de tracing
        self.traces_sample_rate = float(settings.SENTRY_TRACES_SAMPLE_RATE, "1.0"))
        self.profiles_sample_rate = float(settings.SENTRY_PROFILES_SAMPLE_RATE, "1.0"))

        # Configuración de exporters
        self.jaeger_enabled = settings.JAEGER_ENABLED, "true").lower() == "true"
        self.otlp_enabled = settings.OTLP_ENABLED, "false").lower() == "true"
        self.console_enabled = settings.CONSOLE_EXPORTER, "false").lower() == "true"

    def setup_tracing(self) -> TracerProvider:
        """Configurar tracing con múltiples exporters"""
        resource = Resource.create({
            SERVICE_NAME: self.service_name,
            SERVICE_VERSION: self.service_version,
            "environment": self.environment,
            "service.instance.id": settings.HOSTNAME, "localhost"),
        })

        tracer_provider = TracerProvider(resource=resource)

        # Configurar exporters
        exporters = []

        # Jaeger Exporter (principal para desarrollo)
        if self.jaeger_enabled:
            jaeger_host = settings.JAEGER_HOST, "localhost")
            jaeger_port = int(settings.JAEGER_PORT, "14268"))
            jaeger_exporter = JaegerExporter(
                agent_host_name=jaeger_host,
                agent_port=jaeger_port,
            )
            exporters.append(jaeger_exporter)
            logger.info(f"✅ Jaeger exporter configurado: {jaeger_host}:{jaeger_port}")

        # OTLP Exporter (para producción)
        if self.otlp_enabled:
            otlp_endpoint = settings.OTLP_ENDPOINT, "http://localhost:4317")
            otlp_exporter = OTLPSpanExporter(
                endpoint=otlp_endpoint,
                headers={"service.name": self.service_name}
            )
            exporters.append(otlp_exporter)
            logger.info(f"✅ OTLP exporter configurado: {otlp_endpoint}")

        # Console Exporter (para debugging)
        if self.console_enabled:
            console_exporter = ConsoleSpanExporter()
            exporters.append(console_exporter)
            logger.info("✅ Console exporter configurado")

        # Configurar span processors
        for exporter in exporters:
            span_processor = BatchSpanProcessor(
                exporter,
                max_export_batch_size=512,
                export_timeout_millis=30000,
                schedule_delay_millis=5000,
            )
            tracer_provider.add_span_processor(span_processor)

        trace.set_tracer_provider(tracer_provider)
        return tracer_provider

    def setup_metrics(self) -> MeterProvider:
        """Configurar métricas"""
        # OTLP Metric Exporter
        metric_readers = []

        if self.otlp_enabled:
            otlp_endpoint = settings.OTLP_ENDPOINT, "http://localhost:4317")
            otlp_metric_exporter = OTLPMetricExporter(
                endpoint=otlp_endpoint,
                headers={"service.name": self.service_name}
            )
            metric_reader = PeriodicExportingMetricReader(
                exporter=otlp_metric_exporter,
                export_interval_millis=15000
            )
            metric_readers.append(metric_reader)

        # Console Metric Exporter (opcional)
        if self.console_enabled:
            console_metric_exporter = ConsoleMetricExporter()
            metric_reader = PeriodicExportingMetricReader(
                exporter=console_metric_exporter,
                export_interval_millis=10000
            )
            metric_readers.append(metric_reader)

        resource = Resource.create({
            SERVICE_NAME: self.service_name,
            SERVICE_VERSION: self.service_version,
            "environment": self.environment,
        })

        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=metric_readers
        )
        metrics.set_meter_provider(meter_provider)

        return meter_provider

    def instrument_fastapi(self, app):
        """Instrumentar aplicación FastAPI"""
        FastAPIInstrumentor.instrument_app(
            app,
            server_request_hook=self._request_hook,
            client_request_hook=self._request_hook,
            excluded_urls="/health,/metrics",
        )

    def instrument_httpx(self):
        """Instrumentar HTTPX client"""
        HTTPXClientInstrumentor().instrument()

    def instrument_asyncpg(self):
        """Instrumentar AsyncPG"""
        try:
            AsyncPGInstrumentor().instrument()
            logger.info("✅ AsyncPG instrumentado")
        except Exception as e:
            logger.warning(f"AsyncPG no disponible: {e}")

    def instrument_redis(self):
        """Instrumentar Redis"""
        try:
            RedisInstrumentor().instrument()
            logger.info("✅ Redis instrumentado")
        except Exception as e:
            logger.warning(f"Redis no disponible: {e}")

    def instrument_sqlalchemy(self):
        """Instrumentar SQLAlchemy"""
        try:
            SQLAlchemyInstrumentor().instrument()
            logger.info("✅ SQLAlchemy instrumentado")
        except Exception as e:
            logger.warning(f"SQLAlchemy no disponible: {e}")

    def _request_hook(self, span, scope):
        """Hook para enriquecer spans con información adicional"""
        if span and span.is_recording():
            # Agregar información de usuario si está disponible
            request = scope.get("request")
            if request:
                user_agent = request.headers.get("user-agent", "")
                if user_agent:
                    span.set_attribute("http.user_agent", user_agent)

                # Agregar información de rate limiting
                rate_limit = request.headers.get("x-ratelimit-remaining", "")
                if rate_limit:
                    span.set_attribute("http.rate_limit_remaining", rate_limit)

    def get_tracer(self, name: str = "axiom-atlas"):
        """Obtener tracer configurado"""
        return trace.get_tracer(name, self.service_version)

    def get_meter(self, name: str = "axiom-atlas"):
        """Obtener meter configurado"""
        return metrics.get_meter(name, self.service_version)


# Instancia global
axiom_telemetry = AxiomTelemetry()


def setup_telemetry(app=None):
    """Función de conveniencia para configurar toda la telemetría"""
    logger.info("🚀 Configurando telemetría para AXIOM ATLAS...")

    # Configurar tracing
    tracer_provider = axiom_telemetry.setup_tracing()

    # Configurar métricas
    meter_provider = axiom_telemetry.setup_metrics()

    # Instrumentar componentes
    if app:
        axiom_telemetry.instrument_fastapi(app)

    axiom_telemetry.instrument_httpx()
    axiom_telemetry.instrument_asyncpg()
    axiom_telemetry.instrument_redis()
    axiom_telemetry.instrument_sqlalchemy()

    logger.info("✅ Telemetría configurada exitosamente")
    return tracer_provider, meter_provider


def get_tracer(name: str = "axiom-atlas"):
    """Obtener tracer configurado"""
    return axiom_telemetry.get_tracer(name)


def get_meter(name: str = "axiom-atlas"):
    """Obtener meter configurado"""
    return axiom_telemetry.get_meter(name)
