#!/usr/bin/env python3
"""
AXIOM Advanced Monitoring System
Sistema avanzado de monitoreo con alertas y métricas detalladas
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import psutil

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Severidad de las alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Estado de las alertas"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


class MetricType(Enum):
    """Tipos de métricas"""
    GAUGE = "gauge"  # Valor absoluto
    COUNTER = "counter"  # Valor incremental
    HISTOGRAM = "histogram"  # Distribución de valores
    SUMMARY = "summary"  # Estadísticas resumidas


@dataclass
class Metric:
    """Métrica individual"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class AlertRule:
    """Regla de alerta"""
    name: str
    description: str
    metric_name: str
    condition: str  # ">", "<", ">=", "<=", "==", "!="
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 5
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """Alerta activa"""
    id: str
    rule_name: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    value: float
    threshold: float
    created_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    load_average: tuple
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApplicationMetrics:
    """Métricas de aplicación"""
    active_connections: int
    total_requests: int
    error_rate: float
    avg_response_time: float
    throughput: float
    cache_hit_rate: float
    gpu_memory_used: float
    gpu_memory_total: float
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """Recolección de métricas del sistema"""

    def __init__(self):
        self._last_network_bytes = None
        self._collection_interval = 30  # segundos

    async def collect_system_metrics(self) -> SystemMetrics:
        """Recopilar métricas del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memoria
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)

            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)

            # Red
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv

            # Load average
            load_average = psutil.getloadavg()

            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=memory_used_gb,
                memory_total_gb=memory_total_gb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                load_average=load_average
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_gb=0.0,
                memory_total_gb=0.0,
                disk_percent=0.0,
                disk_used_gb=0.0,
                disk_total_gb=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                load_average=(0.0, 0.0, 0.0)
            )

    async def collect_application_metrics(self) -> ApplicationMetrics:
        """Recopilar métricas de aplicación"""
        try:
            # Métricas básicas de aplicación
            active_connections = 0  # TODO: Implementar contador de conexiones activas
            total_requests = 0  # TODO: Implementar contador de requests
            error_rate = 0.0  # TODO: Implementar tasa de errores
            avg_response_time = 0.0  # TODO: Implementar tiempo de respuesta promedio
            throughput = 0.0  # TODO: Implementar throughput
            cache_hit_rate = 0.0  # TODO: Implementar hit rate de caché

            # GPU metrics (si está disponible)
            gpu_memory_used = 0.0
            gpu_memory_total = 0.0

            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory_used = torch.cuda.memory_allocated() / (1024**3)
                    gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            except ImportError:
                pass

            return ApplicationMetrics(
                active_connections=active_connections,
                total_requests=total_requests,
                error_rate=error_rate,
                avg_response_time=avg_response_time,
                throughput=throughput,
                cache_hit_rate=cache_hit_rate,
                gpu_memory_used=gpu_memory_used,
                gpu_memory_total=gpu_memory_total
            )
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return ApplicationMetrics(
                active_connections=0,
                total_requests=0,
                error_rate=0.0,
                avg_response_time=0.0,
                throughput=0.0,
                cache_hit_rate=0.0,
                gpu_memory_used=0.0,
                gpu_memory_total=0.0
            )


class AlertManager:
    """Gestión de alertas"""

    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self._alert_id_counter = 0

    def add_alert_rule(self, rule: AlertRule):
        """Agregar regla de alerta"""
        self.alert_rules[rule.name] = rule
        logger.info(f"Added alert rule: {rule.name}")

    def remove_alert_rule(self, rule_name: str):
        """Remover regla de alerta"""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            logger.info(f"Removed alert rule: {rule_name}")

    def get_alert_rules(self) -> List[AlertRule]:
        """Obtener todas las reglas de alerta"""
        return list(self.alert_rules.values())

    def get_active_alerts(self) -> List[Alert]:
        """Obtener alertas activas"""
        return list(self.active_alerts.values())

    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Obtener historial de alertas"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.created_at > cutoff]

    async def check_alerts(self, metrics: Dict[str, float]):
        """Verificar reglas de alerta contra métricas"""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue

            if rule.metric_name not in metrics:
                continue

            value = metrics[rule.metric_name]
            should_alert = self._evaluate_condition(value, rule.condition, rule.threshold)

            alert_key = f"{rule.name}_{rule.metric_name}"

            if should_alert:
                if alert_key not in self.active_alerts:
                    # Crear nueva alerta
                    alert = Alert(
                        id=str(self._alert_id_counter),
                        rule_name=rule.name,
                        description=rule.description,
                        severity=rule.severity,
                        status=AlertStatus.ACTIVE,
                        value=value,
                        threshold=rule.threshold,
                        created_at=datetime.now(),
                        labels=rule.labels.copy()
                    )
                    self.active_alerts[alert_key] = alert
                    self.alert_history.append(alert)
                    self._alert_id_counter += 1

                    logger.warning(f"Alert triggered: {rule.name} - {value} {rule.condition} {rule.threshold}")
                    await self._send_alert_notification(alert)
                else:
                    # Actualizar alerta existente
                    self.active_alerts[alert_key].value = value
            else:
                if alert_key in self.active_alerts:
                    # Resolver alerta
                    alert = self.active_alerts[alert_key]
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_at = datetime.now()
                    del self.active_alerts[alert_key]

                    logger.info(f"Alert resolved: {rule.name}")

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluar condición de alerta"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        return False

    async def _send_alert_notification(self, alert: Alert):
        """Enviar notificación de alerta"""
        # TODO: Implementar notificaciones (email, Slack, etc.)
        logger.info(f"Alert notification: {alert.description} (Severity: {alert.severity.value})")

    def acknowledge_alert(self, alert_id: str, user: str = "system"):
        """Marcar alerta como reconocida"""
        for alert in self.active_alerts.values():
            if alert.id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = user
                logger.info(f"Alert acknowledged: {alert_id} by {user}")
                break


class MonitoringSystem:
    """Sistema de monitoreo avanzado"""

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.metrics_history: List[Metric] = []
        self._running = False
        self._collection_task: Optional[asyncio.Task] = None
        self._alert_check_task: Optional[asyncio.Task] = None

        # Configurar reglas de alerta por defecto
        self._setup_default_alert_rules()

    def _setup_default_alert_rules(self):
        """Configurar reglas de alerta por defecto"""
        default_rules = [
            AlertRule(
                name="high_cpu_usage",
                description="Uso de CPU por encima del 90%",
                metric_name="cpu_percent",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.HIGH
            ),
            AlertRule(
                name="high_memory_usage",
                description="Uso de memoria por encima del 85%",
                metric_name="memory_percent",
                condition=">",
                threshold=85.0,
                severity=AlertSeverity.HIGH
            ),
            AlertRule(
                name="low_disk_space",
                description="Espacio en disco por debajo del 10%",
                metric_name="disk_percent",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL
            ),
            AlertRule(
                name="high_error_rate",
                description="Tasa de error por encima del 5%",
                metric_name="error_rate",
                condition=">",
                threshold=5.0,
                severity=AlertSeverity.MEDIUM
            )
        ]

        for rule in default_rules:
            self.alert_manager.add_alert_rule(rule)

    async def start(self):
        """Iniciar sistema de monitoreo"""
        if self._running:
            return

        self._running = True
        logger.info("Starting advanced monitoring system...")

        # Iniciar tareas de recolección
        self._collection_task = asyncio.create_task(self._collection_loop())
        self._alert_check_task = asyncio.create_task(self._alert_check_loop())

    async def stop(self):
        """Detener sistema de monitoreo"""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping advanced monitoring system...")

        if self._collection_task:
            self._collection_task.cancel()
        if self._alert_check_task:
            self._alert_check_task.cancel()

    async def _collection_loop(self):
        """Loop de recolección de métricas"""
        while self._running:
            try:
                # Recopilar métricas del sistema
                system_metrics = await self.metrics_collector.collect_system_metrics()
                app_metrics = await self.metrics_collector.collect_application_metrics()

                # Convertir a diccionario para alertas
                metrics_dict = {
                    "cpu_percent": system_metrics.cpu_percent,
                    "memory_percent": system_metrics.memory_percent,
                    "disk_percent": system_metrics.disk_percent,
                    "error_rate": app_metrics.error_rate
                }

                # Almacenar métricas
                self._store_metrics(system_metrics, app_metrics)

                # Verificar alertas
                await self.alert_manager.check_alerts(metrics_dict)

                await asyncio.sleep(self.metrics_collector._collection_interval)

            except Exception as e:
                logger.error(f"Error in monitoring collection loop: {e}")
                await asyncio.sleep(5)

    async def _alert_check_loop(self):
        """Loop de verificación de alertas"""
        while self._running:
            try:
                # Verificar alertas expiradas (cooldown)
                current_time = datetime.now()
                alerts_to_remove = []

                for alert_key, alert in self.alert_manager.active_alerts.items():
                    rule = self.alert_manager.alert_rules.get(alert.rule_name)
                    if rule and alert.created_at + timedelta(minutes=rule.cooldown_minutes) < current_time:
                        alerts_to_remove.append(alert_key)

                for alert_key in alerts_to_remove:
                    del self.alert_manager.active_alerts[alert_key]

                await asyncio.sleep(60)  # Verificar cada minuto

            except Exception as e:
                logger.error(f"Error in alert check loop: {e}")
                await asyncio.sleep(5)

    def _store_metrics(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Almacenar métricas en historial"""
        metrics = [
            Metric("cpu_percent", system_metrics.cpu_percent, system_metrics.timestamp),
            Metric("memory_percent", system_metrics.memory_percent, system_metrics.timestamp),
            Metric("memory_used_gb", system_metrics.memory_used_gb, system_metrics.timestamp),
            Metric("disk_percent", system_metrics.disk_percent, system_metrics.timestamp),
            Metric("network_bytes_sent", system_metrics.network_bytes_sent, system_metrics.timestamp),
            Metric("network_bytes_recv", system_metrics.network_bytes_recv, system_metrics.timestamp),
            Metric("active_connections", app_metrics.active_connections, app_metrics.timestamp),
            Metric("error_rate", app_metrics.error_rate, app_metrics.timestamp),
            Metric("avg_response_time", app_metrics.avg_response_time, app_metrics.timestamp),
            Metric("gpu_memory_used", app_metrics.gpu_memory_used, app_metrics.timestamp)
        ]

        self.metrics_history.extend(metrics)

        # Mantener solo las últimas 1000 métricas por tipo
        metric_counts = {}
        filtered_history = []

        for metric in reversed(self.metrics_history):
            if metric_counts.get(metric.name, 0) < 1000:
                filtered_history.append(metric)
                metric_counts[metric.name] = metric_counts.get(metric.name, 0) + 1

        self.metrics_history = list(reversed(filtered_history))

    async def get_current_metrics(self) -> Dict[str, Any]:
        """Obtener métricas actuales"""
        system_metrics = await self.metrics_collector.collect_system_metrics()
        app_metrics = await self.metrics_collector.collect_application_metrics()

        return {
            "system": {
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "memory_used_gb": round(system_metrics.memory_used_gb, 2),
                "memory_total_gb": round(system_metrics.memory_total_gb, 2),
                "disk_percent": system_metrics.disk_percent,
                "disk_used_gb": round(system_metrics.disk_used_gb, 2),
                "disk_total_gb": round(system_metrics.disk_total_gb, 2),
                "load_average": system_metrics.load_average,
                "timestamp": system_metrics.timestamp.isoformat()
            },
            "application": {
                "active_connections": app_metrics.active_connections,
                "total_requests": app_metrics.total_requests,
                "error_rate": app_metrics.error_rate,
                "avg_response_time": app_metrics.avg_response_time,
                "throughput": app_metrics.throughput,
                "cache_hit_rate": app_metrics.cache_hit_rate,
                "gpu_memory_used": round(app_metrics.gpu_memory_used, 2),
                "gpu_memory_total": round(app_metrics.gpu_memory_total, 2),
                "timestamp": app_metrics.timestamp.isoformat()
            }
        }

    def get_metrics_history(self, metric_name: str, hours: int = 1) -> List[Metric]:
        """Obtener historial de métricas"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics_history
                if m.name == metric_name and m.timestamp > cutoff]

    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema de monitoreo"""
        current_metrics = await self.get_current_metrics()

        return {
            "status": "running" if self._running else "stopped",
            "timestamp": datetime.now().isoformat(),
            "current_metrics": current_metrics,
            "alerts": {
                "active_count": len(self.alert_manager.active_alerts),
                "rules_count": len(self.alert_manager.alert_rules),
                "active_alerts": [
                    {
                        "id": alert.id,
                        "rule_name": alert.rule_name,
                        "description": alert.description,
                        "severity": alert.severity.value,
                        "status": alert.status.value,
                        "value": alert.value,
                        "threshold": alert.threshold,
                        "created_at": alert.created_at.isoformat()
                    }
                    for alert in self.alert_manager.get_active_alerts()
                ]
            },
            "metrics_history": {
                "total_metrics": len(self.metrics_history),
                "metric_types": list(set(m.name for m in self.metrics_history))
            }
        }


# Instancia global del sistema de monitoreo
monitoring_system = MonitoringSystem()
