"""
Router de Métricas Éticas - Monitoreo y Gobernanza Ética

Módulo FastAPI para exposición de métricas éticas y monitoreo del sistema de gobernanza ética.
Proporciona endpoints REST API para monitoreo de decisiones éticas, métricas de cumplimiento
y estado del sistema de ética computacional.

Capacidades principales:
- Métricas éticas estilo Prometheus: exposición de métricas para Grafana/Prometheus
- Health checks éticos: verificación del estado del sistema de ética
- Gestión de políticas: consulta y recarga de políticas éticas
- Monitoreo de decisiones: seguimiento de decisiones procesadas
- Integración opcional con Prometheus: métricas estándar cuando disponible

Catálogo de Endpoints:
- GET /ethics/metrics: Métricas éticas estilo Prometheus para monitoreo
- GET /ethics/health: Health check completo del sistema ético
- GET /ethics/policy/current: Consulta de política ética actual (datos seguros)
- POST /ethics/policy/reload: Recarga en caliente de política ética

Dependencias:
- EthicsGate: Motor central de gobernanza ética
- prometheus_client: Cliente Prometheus para métricas (opcional)
- logging: Sistema de logging para errores y eventos
- FastAPI Response: Para respuestas con tipos de contenido personalizados

Uso del Servicio:
    El router proporciona monitoreo integral del sistema ético.
    Las métricas incluyen conteo de decisiones, estado de políticas y
    información de salud del sistema. Soporta integración opcional con
    Prometheus para dashboards avanzados. Los health checks verifican
    la carga de políticas, disponibilidad de métricas y procesamiento de decisiones.
"""
from fastapi import APIRouter, HTTPException, Response
import logging

from app.compliance.ethics_gate import EthicsGate
from app.exceptions.domain.biology import BiologyError

logger = logging.getLogger(__name__)

# Opcional: integración con prometheus_client
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    generate_latest = None  # type: ignore
    CONTENT_TYPE_LATEST = "text/plain"

router = APIRouter(prefix="/ethics", tags=["ethics"])

@router.get("/metrics")
async def get_ethics_metrics():
    """Endpoint métricas estilo Prometheus para Ethics Gate"""
    if not PROMETHEUS_AVAILABLE or generate_latest is None:
        # Fallback: métricas JSON básicas
        gate = EthicsGate()
        return {
            "prometheus_unavailable": True,
            "decisions_count": len(gate.decisions_log),
            "note": "Install prometheus_client for full metrics exposition"
        }
    
    try:
        # Genera métricas Prometheus estándar
        metrics_output = generate_latest()
        return Response(
            content=metrics_output,
            media_type=CONTENT_TYPE_LATEST
        )
    except BiologyError as e:
        logger.error(f"Metrics generation failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics unavailable")

@router.get("/health")
async def ethics_health():
    """Health check del sistema ético"""
    gate = EthicsGate()
    
    return {
        "status": "healthy",
        "policy_loaded": bool(gate.policy),
        "metrics_available": gate.metrics is not None,
        "decisions_processed": len(gate.decisions_log),
        "public_key": gate.export_public_key()
    }

@router.get("/policy/current")
async def get_current_policy():
    """Retorna política ética actual (sin secretos)"""
    gate = EthicsGate()
    
    # Sanitizar información sensible
    safe_policy = {
        "thresholds": gate.thresholds,
        "domain_weights": gate.domain_weights,
        "signature_levels": list(gate.signature_required_levels)
    }
    
    return {
        "policy": safe_policy,
        "source": "ethics_policy.yaml" if gate.policy else "defaults"
    }

@router.post("/policy/reload")
async def reload_policy():
    """Hot-reload de política (requiere autenticación en producción)"""
    try:
        gate = EthicsGate(policy_path="config/ethics_policy.yaml")
        return {
            "status": "reloaded",
            "thresholds": gate.thresholds,
            "domains_count": len(gate.domain_weights)
        }
    except BiologyError as e:
        logger.error(f"Policy reload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")
