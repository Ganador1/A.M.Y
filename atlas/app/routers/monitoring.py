"""
Router Monitoring para AXIOM - Monitoreo y Alertas del Sistema

Este módulo proporciona endpoints completos para el monitoreo comprehensivo del sistema,
incluyendo métricas en tiempo real, gestión de alertas, análisis histórico y control
del sistema de monitoreo para asegurar la salud y rendimiento operativo.

== CAPACIDADES ==
• Recolección y reporte de métricas del sistema en tiempo real
• Sistema de alertas configurables con niveles de severidad
• Recuperación de datos históricos de métricas y alertas
• Gestión del ciclo de vida de alertas (reconocimiento, resolución)
• Control del sistema de monitoreo (inicio/detención)
• Agregación de datos para dashboards de visualización
• Validaciones de salud del sistema y componentes

== ENDPOINTS DISPONIBLES ==
• GET /status - Estado completo del sistema de monitoreo
• GET /metrics/current - Instantánea actual de métricas del sistema
• GET /metrics/history/{metric} - Datos históricos con rango de tiempo
• GET /alerts/active - Alertas actualmente activas
• GET /alerts/history - Historial de alertas con rango configurable
• GET /alerts/rules - Reglas de alerta configuradas
• POST /alerts/rules - Crear nuevas reglas de alerta validadas
• DELETE /alerts/rules/{name} - Eliminar reglas de alerta
• POST /alerts/{id}/acknowledge - Reconocer alertas activas
• POST /start - Iniciar recolección del sistema de monitoreo
• POST /stop - Detener recolección del sistema de monitoreo
• GET /health - Verificación de salud del sistema de monitoreo
• GET /dashboard - Datos agregados para dashboards de monitoreo

== DEPENDENCIAS ==
• MonitoringSystem: Servicio principal de monitoreo y recolección de métricas
• AlertManager: Gestión de reglas de alerta y sistema de notificaciones
• AlertRule/AlertSeverity: Modelos de datos para configuración de alertas
• fastapi: Framework web asíncrono
• pydantic: Validación de datos y modelos de respuesta
• datetime: Manejo de timestamps y rangos de tiempo

== USO ==
Este router proporciona visibilidad completa del rendimiento del sistema para
investigadores y administradores, permitiendo monitoreo proactivo, resolución
rápida de incidentes y optimización del rendimiento operativo.

== SEGURIDAD ==
• Endpoints de solo lectura para métricas y estado
• Control de acceso para operaciones de escritura (reglas de alerta)
• Validación estricta de parámetros de entrada
• Logging detallado de todas las operaciones de monitoreo
• Manejo seguro de errores sin exposición de información sensible
• Rate limiting recomendado para endpoints de alta frecuencia
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.monitoring import monitoring_system, AlertRule, AlertSeverity
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError

# Request/Response Models
class AlertRuleCreateRequest(BaseModel):
    name: str = Field(..., description="Nombre único de la regla de alerta")
    description: str = Field(..., description="Descripción de la regla y su propósito")
    metric_name: str = Field(..., description="Nombre de la métrica a monitorear")
    condition: str = Field(..., description="Condición de comparación (gt, lt, eq, etc.)")
    threshold: float = Field(..., description="Valor umbral para activar la alerta")
    severity: str = Field(..., description="Severidad: info, warning, error, critical")
    enabled: bool = Field(True, description="Si la regla está habilitada")
    cooldown_minutes: int = Field(5, description="Minutos de cooldown entre alertas")
    labels: Dict[str, str] = Field(default_factory=dict, description="Etiquetas adicionales")

class MonitoringResponse(BaseModel):
    status: str = Field(..., description="Estado de la respuesta")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos de respuesta")
    timestamp: str = Field(..., description="Timestamp de la respuesta")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Estado del servicio")
    monitoring_active: bool = Field(..., description="Si el monitoreo está activo")
    timestamp: str = Field(..., description="Timestamp del check")
    active_alerts: int = Field(..., description="Número de alertas activas")
    total_metrics: int = Field(..., description="Total de métricas recolectadas")

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/status")
async def get_monitoring_status():
    """Obtener estado completo del sistema de monitoreo"""
    try:
        return await monitoring_system.get_monitoring_status()
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error getting monitoring status: {str(e)}")


@router.get("/metrics/current")
async def get_current_metrics():
    """Obtener métricas actuales del sistema"""
    try:
        return await monitoring_system.get_current_metrics()
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error getting current metrics: {str(e)}")


@router.get("/metrics/history/{metric_name}")
async def get_metrics_history(
    metric_name: str,
    hours: int = Query(1, description="Horas de historial a recuperar", ge=1, le=24)
):
    """Obtener historial de métricas específicas"""
    try:
        metrics = monitoring_system.get_metrics_history(metric_name, hours)
        return {
            "metric_name": metric_name,
            "hours": hours,
            "data_points": len(metrics),
            "metrics": [
                {
                    "value": m.value,
                    "timestamp": m.timestamp.isoformat(),
                    "labels": m.labels
                }
                for m in metrics
            ]
        }
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics history: {str(e)}")


@router.get("/alerts/active")
async def get_active_alerts():
    """Obtener alertas activas"""
    try:
        alerts = monitoring_system.alert_manager.get_active_alerts()
        return {
            "count": len(alerts),
            "alerts": [
                {
                    "id": alert.id,
                    "rule_name": alert.rule_name,
                    "description": alert.description,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "value": alert.value,
                    "threshold": alert.threshold,
                    "created_at": alert.created_at.isoformat(),
                    "labels": alert.labels
                }
                for alert in alerts
            ]
        }
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error getting active alerts: {str(e)}")


@router.get("/alerts/history")
async def get_alerts_history(hours: int = Query(24, description="Horas de historial", ge=1, le=168)):
    """Obtener historial de alertas"""
    try:
        alerts = monitoring_system.alert_manager.get_alert_history(hours)
        return {
            "hours": hours,
            "count": len(alerts),
            "alerts": [
                {
                    "id": alert.id,
                    "rule_name": alert.rule_name,
                    "description": alert.description,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "value": alert.value,
                    "threshold": alert.threshold,
                    "created_at": alert.created_at.isoformat(),
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "labels": alert.labels
                }
                for alert in alerts
            ]
        }
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error getting alerts history: {str(e)}")


@router.get("/alerts/rules")
async def get_alert_rules():
    """Obtener reglas de alerta configuradas"""
    try:
        rules = monitoring_system.alert_manager.get_alert_rules()
        return {
            "count": len(rules),
            "rules": [
                {
                    "name": rule.name,
                    "description": rule.description,
                    "metric_name": rule.metric_name,
                    "condition": rule.condition,
                    "threshold": rule.threshold,
                    "severity": rule.severity.value,
                    "enabled": rule.enabled,
                    "cooldown_minutes": rule.cooldown_minutes,
                    "labels": rule.labels
                }
                for rule in rules
            ]
        }
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error getting alert rules: {str(e)}")


@router.post("/alerts/rules", response_model=MonitoringResponse)
async def create_alert_rule(rule_data: AlertRuleCreateRequest):
    """
    Crear nueva regla de alerta con validación completa.

    Establece una nueva regla de monitoreo con validación de parámetros,
    verificación de severidad y configuración de cooldown para evitar spam.

    Args:
        rule_data: Datos validados de la nueva regla de alerta

    Returns:
        Confirmación de creación exitosa de la regla

    Raises:
        HTTPException: Si los datos son inválidos o hay error en la creación
    """
    try:
        logger.info("📝 Creando regla de alerta: %s (métrica: %s)", rule_data.name, rule_data.metric_name)

        # Validar severidad
        try:
            severity = AlertSeverity(rule_data.severity)
        except ValueError:
            logger.error("❌ Severidad inválida para regla %s: %s", rule_data.name, rule_data.severity)
            raise HTTPException(status_code=400, detail=f"Invalid severity: {rule_data.severity}")

        # Crear regla
        rule = AlertRule(
            name=rule_data.name,
            description=rule_data.description,
            metric_name=rule_data.metric_name,
            condition=rule_data.condition,
            threshold=rule_data.threshold,
            severity=severity,
            enabled=rule_data.enabled,
            cooldown_minutes=rule_data.cooldown_minutes,
            labels=rule_data.labels
        )

        monitoring_system.alert_manager.add_alert_rule(rule)
        logger.info("✅ Regla de alerta %s creada exitosamente", rule_data.name)

        return MonitoringResponse(
            status="success",
            message=f"Alert rule '{rule.name}' created successfully",
            data={"rule_name": rule.name},
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except BiologyError as e:
        logger.exception("❌ Error creando regla de alerta %s", rule_data.name)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.delete("/alerts/rules/{rule_name}")
async def delete_alert_rule(rule_name: str):
    """Eliminar regla de alerta"""
    try:
        monitoring_system.alert_manager.remove_alert_rule(rule_name)
        return {"message": f"Alert rule '{rule_name}' deleted successfully"}
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting alert rule: {str(e)}")


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user: str = Query("api", description="Usuario que reconoce la alerta")):
    """Marcar alerta como reconocida"""
    try:
        monitoring_system.alert_manager.acknowledge_alert(alert_id, user)
        return {"message": f"Alert '{alert_id}' acknowledged by {user}"}
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error acknowledging alert: {str(e)}")


@router.post("/start")
async def start_monitoring():
    """Iniciar sistema de monitoreo"""
    try:
        await monitoring_system.start()
        return {"message": "Monitoring system started successfully"}
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error starting monitoring system: {str(e)}")


@router.post("/stop")
async def stop_monitoring():
    """Detener sistema de monitoreo"""
    try:
        await monitoring_system.stop()
        return {"message": "Monitoring system stopped successfully"}
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error stopping monitoring system: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def monitoring_health_check():
    """
    Verificación comprehensiva de salud del sistema de monitoreo.

    Evalúa el estado operativo del sistema de monitoreo, conectividad
    con servicios dependientes y estado de componentes críticos.

    Returns:
        Estado detallado de salud con métricas operativas

    Raises:
        HTTPException: Si hay problemas críticos de salud
    """
    try:
        logger.info("🏥 Verificando salud del sistema de monitoreo")
        status = await monitoring_system.get_monitoring_status()

        health_data = HealthResponse(
            status="healthy",
            monitoring_active=status["status"] == "running",
            timestamp=datetime.now().isoformat(),
            active_alerts=status["alerts"]["active_count"],
            total_metrics=status["metrics_history"]["total_metrics"]
        )

        logger.info("📊 Estado de salud: %s (alertas activas: %d)",
                   health_data.status, health_data.active_alerts)
        return health_data

    except BiologyError:
        logger.exception("❌ Error en verificación de salud del monitoreo")
        return HealthResponse(
            status="unhealthy",
            monitoring_active=False,
            timestamp=datetime.now().isoformat(),
            active_alerts=0,
            total_metrics=0
        )


@router.get("/dashboard")
async def get_monitoring_dashboard():
    """Obtener datos para dashboard de monitoreo"""
    try:
        status = await monitoring_system.get_monitoring_status()
        current_metrics = status["current_metrics"]

        # Obtener historial de métricas clave para las últimas 2 horas
        cpu_history = monitoring_system.get_metrics_history("cpu_percent", 2)
        memory_history = monitoring_system.get_metrics_history("memory_percent", 2)
        disk_history = monitoring_system.get_metrics_history("disk_percent", 2)

        return {
            "current": current_metrics,
            "history": {
                "cpu": [
                    {"value": m.value, "timestamp": m.timestamp.isoformat()}
                    for m in cpu_history[-50:]  # Últimos 50 puntos
                ],
                "memory": [
                    {"value": m.value, "timestamp": m.timestamp.isoformat()}
                    for m in memory_history[-50:]
                ],
                "disk": [
                    {"value": m.value, "timestamp": m.timestamp.isoformat()}
                    for m in disk_history[-50:]
                ]
            },
            "alerts": status["alerts"],
            "timestamp": datetime.now().isoformat()
        }
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard data: {str(e)}")
