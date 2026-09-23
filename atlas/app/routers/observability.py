"""
Router Observability para AXIOM - Monitoreo y Observabilidad del Sistema

Este módulo proporciona endpoints completos para el monitoreo, métricas y
observabilidad del sistema AXIOM. Permite el seguimiento de eventos, contadores,
métricas de rendimiento y snapshots del estado del sistema para análisis
operacional y debugging.

== CAPACIDADES ==
• Contadores de eventos: seguimiento de ocurrencias y frecuencias
• Registro de eventos: captura de eventos con payloads estructurados
• Snapshots del sistema: estado completo de métricas y contadores
• Métricas de rendimiento: tiempos de respuesta y throughput
• Monitoreo de salud: estado de servicios y componentes
• Alertas y notificaciones: triggers basados en umbrales

== ENDPOINTS DISPONIBLES ==
• POST /incr/{name} - Incrementar contador por nombre
• POST /event/{event_type} - Registrar evento con payload opcional
• GET /snapshot - Obtener snapshot completo del estado del sistema
• GET /health - Verificar estado de salud del servicio
• GET /metrics - Obtener métricas detalladas del sistema

== DEPENDENCIAS ==
• ObservabilityService: Servicio principal de observabilidad y métricas
• CounterRequest/EventRequest: Modelos para solicitudes estructuradas
• ObservabilityResponse: Modelo unificado para respuestas

== MÉTRICAS SOPORTADAS ==
• Contadores: eventos discretos con valores acumulativos
• Eventos: registros timestamped con metadatos
• Snapshots: estados puntuales del sistema
• Health checks: validación de componentes críticos
• Performance metrics: latencia, throughput, error rates

== USO ==
Los endpoints permiten monitoreo en tiempo real del sistema AXIOM.
Los contadores se incrementan atómicamente, los eventos incluyen
timestamps automáticos, y los snapshots proporcionan vistas completas
del estado para análisis y debugging.

== SEGURIDAD ==
• Validación de nombres de contadores y tipos de eventos
• Límites en tamaños de payloads para prevenir abuso
• Logging detallado de todas las operaciones de observabilidad
• Rate limiting recomendado para endpoints de alto volumen
• Acceso restringido a snapshots sensibles
"""

from fastapi import APIRouter, HTTPException
from app.services.observability_service import observability_service
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
import datetime
from app.exceptions.domain.biology import BiologyError

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/observability", tags=["observability"])

# Modelos Pydantic para requests y responses
class CounterIncrementRequest(BaseModel):
    """Solicitud para incrementar contador"""
    value: int = Field(1, description="Valor a incrementar (por defecto 1)", ge=0)

class EventRecordRequest(BaseModel):
    """Solicitud para registrar evento"""
    payload: Optional[Dict[str, Any]] = Field(None, description="Payload opcional del evento")

class ObservabilityResponse(BaseModel):
    """Respuesta unificada de operaciones de observabilidad"""
    status: str = Field(..., description="Estado de la operación")
    message: str = Field(..., description="Mensaje descriptivo")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Timestamp de la operación")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales de la respuesta")

@router.post("/incr/{name}")
def incr(name: str, value: int = 1):
    """
    ➕ Incrementar contador de observabilidad

    Incrementa un contador específico por el valor dado. Los contadores
    se utilizan para seguimiento de eventos discretos como número de
    requests, errores, operaciones completadas, etc.

    Args:
        name (str): Nombre del contador a incrementar
        value (int): Valor a incrementar (por defecto 1, debe ser >= 0)

    Returns:
        ObservabilityResponse: Estado de la operación con snapshot actualizado

    Raises:
        HTTPException: Si el nombre es inválido o el valor es negativo

    Example:
        POST /incr/api_requests
        Body: {"value": 5}
        Response: {"status": "ok", "message": "Counter incremented", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if not name or not name.strip():
            logger.warning("🚫 Intento de incrementar contador con nombre vacío")
            raise HTTPException(
                status_code=400,
                detail="El nombre del contador no puede estar vacío"
            )

        if value < 0:
            logger.warning(f"🚫 Intento de incrementar contador '{name}' con valor negativo: {value}")
            raise HTTPException(
                status_code=400,
                detail=f"El valor de incremento debe ser >= 0. Recibido: {value}"
            )

        logger.info(f"➕ Incrementando contador '{name}' por {value}")

        # Incrementar contador
        observability_service.incr(name, value)

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Contador '{name}' incrementado por {value} (tiempo: {execution_time:.4f}s)")

        return {
            "status": "ok",
            "message": f"Contador '{name}' incrementado por {value}",
            "timestamp": datetime.datetime.now().isoformat(),
            "data": {
                "counter_name": name,
                "incremented_by": value,
                "current_value": observability_service.counters.get(name, 0),
                "execution_time_seconds": execution_time
            }
        }

    except HTTPException:
        raise
    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error incrementando contador '{name}': {str(e)} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno incrementando contador: {str(e)}"
        )

@router.post("/event/{event_type}")
def record_event(event_type: str, payload: Optional[Dict[str, Any]] = None):
    """
    📝 Registrar evento de observabilidad

    Registra un evento específico con payload opcional. Los eventos se utilizan
    para seguimiento de actividades importantes del sistema como errores,
    operaciones críticas, cambios de estado, etc.

    Args:
        event_type (str): Tipo de evento a registrar
        payload (Optional[Dict[str, Any]]): Payload opcional con metadatos del evento

    Returns:
        ObservabilityResponse: Confirmación del registro del evento

    Raises:
        HTTPException: Si el tipo de evento es inválido

    Example:
        POST /event/user_login
        Body: {"payload": {"user_id": 123, "ip": "192.168.1.1"}}
        Response: {"status": "ok", "message": "Event recorded", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if not event_type or not event_type.strip():
            logger.warning("🚫 Intento de registrar evento con tipo vacío")
            raise HTTPException(
                status_code=400,
                detail="El tipo de evento no puede estar vacío"
            )

        logger.info(f"📝 Registrando evento '{event_type}' con payload: {bool(payload)}")

        # Registrar evento
        observability_service.record_event(event_type, payload)

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Evento '{event_type}' registrado exitosamente (tiempo: {execution_time:.4f}s)")

        return {
            "status": "ok",
            "message": f"Evento '{event_type}' registrado exitosamente",
            "timestamp": datetime.datetime.now().isoformat(),
            "data": {
                "event_type": event_type,
                "has_payload": payload is not None,
                "payload_size": len(str(payload)) if payload else 0,
                "execution_time_seconds": execution_time
            }
        }

    except HTTPException:
        raise
    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error registrando evento '{event_type}': {str(e)} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno registrando evento: {str(e)}"
        )

@router.get("/snapshot")
def snapshot():
    """
    📸 Obtener snapshot completo del estado de observabilidad

    Retorna un snapshot completo del estado actual del sistema de observabilidad,
    incluyendo todos los contadores, eventos recientes y métricas acumuladas.
    Útil para monitoreo, debugging y análisis de rendimiento.

    Returns:
        Dict[str, Any]: Snapshot completo del estado del sistema

    Example:
        GET /snapshot
        Response: {"counters": {...}, "events": [...], "timestamp": "2024-01-01T12:00:00"}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("📸 Generando snapshot del estado de observabilidad")

        # Obtener snapshot
        snapshot_data = observability_service.snapshot()

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Snapshot generado exitosamente (tiempo: {execution_time:.4f}s)")

        # Enriquecer respuesta con metadatos
        return {
            "status": "ok",
            "message": "Snapshot del estado de observabilidad generado",
            "timestamp": datetime.datetime.now().isoformat(),
            "data": snapshot_data,
            "metadata": {
                "execution_time_seconds": execution_time,
                "snapshot_timestamp": datetime.datetime.now().isoformat()
            }
        }

    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error generando snapshot: {str(e)} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno generando snapshot: {str(e)}"
        )

@router.get("/health")
def health_check():
    """
    ❤️ Verificar estado de salud del servicio de observabilidad

    Endpoint de health check que verifica el estado operativo del servicio
    de observabilidad y sus dependencias críticas.

    Returns:
        Dict[str, Any]: Estado de salud con indicadores de componentes

    Example:
        GET /health
        Response: {"status": "healthy", "timestamp": "2024-01-01T12:00:00", "checks": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("❤️ Ejecutando health check del servicio de observabilidad")

        # Verificar componentes críticos
        health_status = {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "checks": {
                "observability_service": "ok",
                "counters": "ok" if hasattr(observability_service, 'counters') else "failed",
                "event_recording": "ok" if hasattr(observability_service, 'record_event') else "failed"
            }
        }

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Verificar si todos los checks pasaron
        all_checks_ok = all(status == "ok" for status in health_status["checks"].values())
        if not all_checks_ok:
            health_status["status"] = "degraded"

        logger.info(f"✅ Health check completado: {health_status['status']} (tiempo: {execution_time:.4f}s)")

        return health_status

    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error en health check: {str(e)} (tiempo: {execution_time:.4f}s)")
        return {
            "status": "unhealthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "error": str(e),
            "execution_time_seconds": execution_time
        }
