"""
Real-time Anomaly Monitoring Module

This module provides real-time monitoring capabilities for PINN solutions,
integrating anomaly detection with security metrics and providing automated
alerting and reporting.

Key Features:
- Real-time metric monitoring
- Automated anomaly detection
- Alert generation and management
- Integration with security services
- Performance tracking and reporting

Author: AXIOM Research Team
Date: September 2025
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from app.algorithms.anomaly_detection import AnomalyDetectionService
from app.quality.uncertainty_quantification import UncertaintyQuantificationService
from app.quality.robustness_metrics import RobustnessMetricsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics being monitored"""
    UNCERTAINTY = "uncertainty"
    ROBUSTNESS = "robustness"
    PERFORMANCE = "performance"
    SECURITY = "security"
    SYSTEM = "system"


@dataclass
class MetricData:
    """Container for metric data"""
    timestamp: datetime
    metric_type: MetricType
    metric_name: str
    value: float
    metadata: Dict[str, Any]


@dataclass
class Alert:
    """Alert container"""
    id: str
    timestamp: datetime
    level: AlertLevel
    title: str
    description: str
    metric_type: MetricType
    metric_name: str
    threshold_value: float
    actual_value: float
    recommendations: List[str]
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class MonitoringConfig:
    """Configuration for real-time monitoring"""
    alert_thresholds: Dict[str, float]
    enabled_metrics: List[MetricType]
    monitoring_interval: int = 30  # seconds
    anomaly_detection_enabled: bool = True
    alert_cooldown: int = 300  # seconds between similar alerts
    max_alerts_history: int = 1000
    data_retention_days: int = 7


class AlertManager:
    """Manages alerts and notifications"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alerts = []
        self.active_alerts = {}
        self.alert_cooldowns = {}
        self.logger = logging.getLogger(__name__)

    def add_alert(self, alert: Alert) -> None:
        """Add a new alert"""
        try:
            # Check cooldown
            alert_key = f"{alert.metric_type.value}_{alert.metric_name}_{alert.level.value}"
            if alert_key in self.alert_cooldowns:
                if datetime.now() < self.alert_cooldowns[alert_key]:
                    return  # Skip alert due to cooldown

            # Set cooldown
            self.alert_cooldowns[alert_key] = datetime.now() + timedelta(seconds=self.config.alert_cooldown)

            # Add alert
            self.alerts.append(alert)
            self.active_alerts[alert.id] = alert

            # Keep only recent alerts
            if len(self.alerts) > self.config.max_alerts_history:
                self.alerts = self.alerts[-self.config.max_alerts_history:]

            # Log alert
            self._log_alert(alert)

        except Exception as e:
            logger.error(f"Failed to add alert: {str(e)}")

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            return True
        return False

    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.active_alerts.values() if not alert.resolved]

    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """Get alerts by severity level"""
        return [alert for alert in self.alerts if alert.level == level]

    def _log_alert(self, alert: Alert) -> None:
        """Log alert based on severity"""
        message = f"[{alert.level.value.upper()}] {alert.title}: {alert.description}"

        if alert.level == AlertLevel.CRITICAL:
            self.logger.critical(message)
        elif alert.level == AlertLevel.ERROR:
            self.logger.error(message)
        elif alert.level == AlertLevel.WARNING:
            self.logger.warning(message)
        else:
            self.logger.info(message)


class MetricCollector:
    """Collects metrics from various services"""

    def __init__(self):
        self.uncertainty_service = UncertaintyQuantificationService()
        self.robustness_service = RobustnessMetricsService()
        self.anomaly_service = AnomalyDetectionService()
        self.metric_history = []
        self.logger = logging.getLogger(__name__)

    async def collect_uncertainty_metrics(self) -> List[MetricData]:
        """Collect uncertainty quantification metrics"""
        metrics = []

        try:
            # Get uncertainty metrics
            result = await self.uncertainty_service.process_request({
                'method': 'fiducial',
                'pde_type': 'heat',
                'num_samples': 100
            })

            if result['status'] == 'success':
                metrics.extend([
                    MetricData(
                        timestamp=datetime.now(),
                        metric_type=MetricType.UNCERTAINTY,
                        metric_name='reliability_score',
                        value=result['reliability_score'],
                        metadata={'method': 'fiducial', 'pde_type': 'heat'}
                    ),
                    MetricData(
                        timestamp=datetime.now(),
                        metric_type=MetricType.UNCERTAINTY,
                        metric_name='coverage_probability',
                        value=result['coverage_probability'],
                        metadata={'method': 'fiducial', 'pde_type': 'heat'}
                    )
                ])

        except Exception as e:
            self.logger.error(f"Failed to collect uncertainty metrics: {str(e)}")

        return metrics

    async def collect_robustness_metrics(self) -> List[MetricData]:
        """Collect robustness metrics"""
        metrics = []

        try:
            # Get robustness metrics
            result = await self.robustness_service.evaluate_model_robustness({
                'pde_type': 'heat',
                'num_test_points': 100
            })

            if result['status'] == 'success':
                metrics.extend([
                    MetricData(
                        timestamp=datetime.now(),
                        metric_type=MetricType.ROBUSTNESS,
                        metric_name='stability_score',
                        value=result['stability_score'],
                        metadata={'pde_type': 'heat'}
                    ),
                    MetricData(
                        timestamp=datetime.now(),
                        metric_type=MetricType.ROBUSTNESS,
                        metric_name='convergence_rate',
                        value=result['convergence_rate'],
                        metadata={'pde_type': 'heat'}
                    ),
                    MetricData(
                        timestamp=datetime.now(),
                        metric_type=MetricType.ROBUSTNESS,
                        metric_name='sensitivity_index',
                        value=result['sensitivity_index'],
                        metadata={'pde_type': 'heat'}
                    ),
                    MetricData(
                        timestamp=datetime.now(),
                        metric_type=MetricType.ROBUSTNESS,
                        metric_name='boundary_satisfaction',
                        value=result['boundary_condition_satisfaction'],
                        metadata={'pde_type': 'heat'}
                    ),
                    MetricData(
                        timestamp=datetime.now(),
                        metric_type=MetricType.ROBUSTNESS,
                        metric_name='robustness_score',
                        value=result['robustness_score'],
                        metadata={'pde_type': 'heat'}
                    )
                ])

        except Exception as e:
            self.logger.error(f"Failed to collect robustness metrics: {str(e)}")

        return metrics

    async def collect_system_metrics(self) -> List[MetricData]:
        """Collect system performance metrics"""
        metrics = []

        try:
            import psutil

            # CPU usage
            metrics.append(MetricData(
                timestamp=datetime.now(),
                metric_type=MetricType.SYSTEM,
                metric_name='cpu_usage',
                value=psutil.cpu_percent(interval=1),
                metadata={'unit': 'percent'}
            ))

            # Memory usage
            memory = psutil.virtual_memory()
            metrics.append(MetricData(
                timestamp=datetime.now(),
                metric_type=MetricType.SYSTEM,
                metric_name='memory_usage',
                value=memory.percent,
                metadata={'unit': 'percent', 'used': memory.used, 'total': memory.total}
            ))

            # Disk usage
            disk = psutil.disk_usage('/')
            metrics.append(MetricData(
                timestamp=datetime.now(),
                metric_type=MetricType.SYSTEM,
                metric_name='disk_usage',
                value=disk.percent,
                metadata={'unit': 'percent', 'used': disk.used, 'total': disk.total}
            ))

        except ImportError:
            # Fallback if psutil not available
            metrics.extend([
                MetricData(
                    timestamp=datetime.now(),
                    metric_type=MetricType.SYSTEM,
                    metric_name='cpu_usage',
                    value=50.0,  # Mock value
                    metadata={'unit': 'percent', 'mock': True}
                ),
                MetricData(
                    timestamp=datetime.now(),
                    metric_type=MetricType.SYSTEM,
                    metric_name='memory_usage',
                    value=60.0,  # Mock value
                    metadata={'unit': 'percent', 'mock': True}
                )
            ])

        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {str(e)}")

        return metrics

    async def collect_all_metrics(self) -> List[MetricData]:
        """Collect all available metrics"""
        all_metrics = []

        # Collect metrics concurrently
        tasks = [
            self.collect_uncertainty_metrics(),
            self.collect_robustness_metrics(),
            self.collect_system_metrics()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Error collecting metrics: {str(result)}")
            elif isinstance(result, list):
                all_metrics.extend(result)

        # Store in history
        self.metric_history.extend(all_metrics)

        # Keep only recent history (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metric_history = [m for m in self.metric_history if m.timestamp > cutoff_time]

        return all_metrics


class RealTimeMonitoringService:
    """Main service for real-time monitoring and anomaly detection"""

    def __init__(self):
        self.config = MonitoringConfig(
            enabled_metrics=[MetricType.UNCERTAINTY, MetricType.ROBUSTNESS, MetricType.SYSTEM],
            alert_thresholds={
                'uncertainty_reliability_score': 0.9,
                'robustness_stability_score': 0.95,
                'robustness_robustness_score': 0.95,
                'system_cpu_usage': 80.0,
                'system_memory_usage': 85.0
            }
        )

        self.metric_collector = MetricCollector()
        self.alert_manager = AlertManager(self.config)
        self.anomaly_detector = AnomalyDetectionService()
        self.monitoring_active = False
        self.monitoring_task = None
        self.logger = logging.getLogger(__name__)

    async def start_monitoring(self) -> Dict[str, Any]:
        """Start real-time monitoring"""
        try:
            if self.monitoring_active:
                return {'status': 'error', 'message': 'Monitoring already active'}

            self.monitoring_active = True

            # Start monitoring loop
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())

            # Start anomaly detection monitoring
            if self.config.anomaly_detection_enabled:
                anomaly_config = {
                    'method': 'z_score',
                    'threshold': 3.0,
                    'window_size': 50,
                    'update_interval': self.config.monitoring_interval
                }
                await self.anomaly_detector.start_monitoring(anomaly_config)

            self.logger.info("Real-time monitoring started")
            return {
                'status': 'success',
                'message': 'Real-time monitoring started',
                'config': {
                    'monitoring_interval': self.config.monitoring_interval,
                    'enabled_metrics': [m.value for m in self.config.enabled_metrics],
                    'anomaly_detection': self.config.anomaly_detection_enabled
                }
            }

        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop real-time monitoring"""
        try:
            self.monitoring_active = False

            if self.monitoring_task:
                self.monitoring_task.cancel()
                self.monitoring_task = None

            # Stop anomaly detection
            await self.anomaly_detector.stop_monitoring()

            self.logger.info("Real-time monitoring stopped")
            return {'status': 'success', 'message': 'Real-time monitoring stopped'}

        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        try:
            while self.monitoring_active:
                start_time = datetime.now()

                # Collect metrics
                metrics = await self.metric_collector.collect_all_metrics()

                # Check for alerts
                alerts = await self._check_alerts(metrics)
                for alert in alerts:
                    self.alert_manager.add_alert(alert)

                # Log monitoring cycle
                cycle_time = (datetime.now() - start_time).total_seconds()
                self.logger.debug(f"Monitoring cycle completed in {cycle_time:.2f}s")

                # Wait for next cycle
                await asyncio.sleep(self.config.monitoring_interval)

        except asyncio.CancelledError:
            self.logger.info("Monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Monitoring loop failed: {str(e)}")
            self.monitoring_active = False

    async def _check_alerts(self, metrics: List[MetricData]) -> List[Alert]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []

        try:
            for metric in metrics:
                threshold_key = f"{metric.metric_type.value}_{metric.metric_name}"
                threshold = self.config.alert_thresholds.get(threshold_key)

                if threshold is not None:
                    if metric.metric_type in [MetricType.UNCERTAINTY, MetricType.ROBUSTNESS]:
                        # For these metrics, lower values trigger alerts
                        if metric.value < threshold:
                            alert_level = self._determine_alert_level(metric.value, threshold)
                            alert = Alert(
                                id=f"{metric.metric_name}_{int(metric.timestamp.timestamp())}",
                                timestamp=metric.timestamp,
                                level=alert_level,
                                title=f"Low {metric.metric_name.replace('_', ' ').title()}",
                                description=f"{metric.metric_name} is {metric.value:.3f}, below threshold {threshold:.3f}",
                                metric_type=metric.metric_type,
                                metric_name=metric.metric_name,
                                threshold_value=threshold,
                                actual_value=metric.value,
                                recommendations=self._generate_recommendations(metric)
                            )
                            alerts.append(alert)
                    else:
                        # For system metrics, higher values trigger alerts
                        if metric.value > threshold:
                            alert_level = self._determine_alert_level(threshold, metric.value, reverse=True)
                            alert = Alert(
                                id=f"{metric.metric_name}_{int(metric.timestamp.timestamp())}",
                                timestamp=metric.timestamp,
                                level=alert_level,
                                title=f"High {metric.metric_name.replace('_', ' ').title()}",
                                description=f"{metric.metric_name} is {metric.value:.1f}%, above threshold {threshold:.1f}%",
                                metric_type=metric.metric_type,
                                metric_name=metric.metric_name,
                                threshold_value=threshold,
                                actual_value=metric.value,
                                recommendations=self._generate_system_recommendations(metric)
                            )
                            alerts.append(alert)

        except Exception as e:
            self.logger.error(f"Failed to check alerts: {str(e)}")

        return alerts

    def _determine_alert_level(self, value: float, threshold: float, reverse: bool = False) -> AlertLevel:
        """Determine alert level based on deviation from threshold"""
        if reverse:
            # For system metrics (higher = worse)
            deviation = (value - threshold) / threshold
        else:
            # For quality metrics (lower = worse)
            deviation = (threshold - value) / threshold

        if deviation > 0.5:
            return AlertLevel.CRITICAL
        elif deviation > 0.3:
            return AlertLevel.ERROR
        elif deviation > 0.1:
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO

    def _generate_recommendations(self, metric: MetricData) -> List[str]:
        """Generate recommendations based on metric type and value"""
        recommendations = []

        if metric.metric_type == MetricType.UNCERTAINTY:
            if metric.metric_name == 'reliability_score':
                recommendations.extend([
                    "Review uncertainty quantification method",
                    "Consider increasing sample size for uncertainty estimation",
                    "Check model calibration and validation"
                ])
            elif metric.metric_name == 'coverage_probability':
                recommendations.extend([
                    "Adjust confidence intervals",
                    "Review uncertainty bounds calculation",
                    "Consider alternative uncertainty methods"
                ])

        elif metric.metric_type == MetricType.ROBUSTNESS:
            if metric.metric_name == 'stability_score':
                recommendations.extend([
                    "Check numerical stability of the model",
                    "Review regularization parameters",
                    "Consider gradient clipping or normalization"
                ])
            elif metric.metric_name == 'convergence_rate':
                recommendations.extend([
                    "Adjust learning rate or optimizer",
                    "Review convergence criteria",
                    "Consider early stopping or learning rate scheduling"
                ])
            elif metric.metric_name == 'sensitivity_index':
                recommendations.extend([
                    "Implement data augmentation",
                    "Add noise robustness to the model",
                    "Review input preprocessing and normalization"
                ])

        return recommendations

    def _generate_system_recommendations(self, metric: MetricData) -> List[str]:
        """Generate system-related recommendations"""
        recommendations = []

        if metric.metric_name == 'cpu_usage':
            recommendations.extend([
                "Monitor CPU-intensive processes",
                "Consider optimizing computational bottlenecks",
                "Review parallel processing configuration"
            ])
        elif metric.metric_name == 'memory_usage':
            recommendations.extend([
                "Check for memory leaks",
                "Optimize data structures and memory usage",
                "Consider increasing system memory or implementing memory pooling"
            ])
        elif metric.metric_name == 'disk_usage':
            recommendations.extend([
                "Clean up temporary files and logs",
                "Implement log rotation",
                "Consider disk space optimization or expansion"
            ])

        return recommendations

    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        try:
            return {
                'monitoring_active': self.monitoring_active,
                'active_alerts': len(self.alert_manager.get_active_alerts()),
                'total_alerts': len(self.alert_manager.alerts),
                'metrics_collected': len(self.metric_collector.metric_history),
                'anomaly_detection_active': self.config.anomaly_detection_enabled,
                'last_update': datetime.now().isoformat(),
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Failed to get monitoring status: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def get_alerts_summary(self) -> Dict[str, Any]:
        """Get alerts summary"""
        try:
            active_alerts = self.alert_manager.get_active_alerts()

            summary = {
                'total_active': len(active_alerts),
                'by_level': {},
                'by_type': {},
                'recent_alerts': [],
                'status': 'success'
            }

            # Group by level
            for level in AlertLevel:
                level_alerts = self.alert_manager.get_alerts_by_level(level)
                summary['by_level'][level.value] = len(level_alerts)

            # Group by metric type
            for alert in active_alerts:
                metric_type = alert.metric_type.value
                if metric_type not in summary['by_type']:
                    summary['by_type'][metric_type] = 0
                summary['by_type'][metric_type] += 1

            # Recent alerts (last 5)
            summary['recent_alerts'] = [
                {
                    'id': alert.id,
                    'timestamp': alert.timestamp.isoformat(),
                    'level': alert.level.value,
                    'title': alert.title,
                    'description': alert.description
                }
                for alert in self.alert_manager.alerts[-5:]
            ]

            return summary

        except Exception as e:
            self.logger.error(f"Failed to get alerts summary: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def acknowledge_alert(self, alert_id: str) -> Dict[str, Any]:
        """Acknowledge an alert"""
        try:
            success = self.alert_manager.acknowledge_alert(alert_id)
            return {
                'status': 'success' if success else 'error',
                'message': 'Alert acknowledged' if success else 'Alert not found',
                'alert_id': alert_id
            }

        except Exception as e:
            self.logger.error(f"Failed to acknowledge alert: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def get_metrics_history(self, metric_type: Optional[MetricType] = None,
                                hours: int = 24) -> Dict[str, Any]:
        """Get metrics history"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Filter metrics
            filtered_metrics = [
                m for m in self.metric_collector.metric_history
                if m.timestamp > cutoff_time and
                (metric_type is None or m.metric_type == metric_type)
            ]

            # Group by metric name
            metrics_data = {}
            for metric in filtered_metrics:
                key = f"{metric.metric_type.value}_{metric.metric_name}"
                if key not in metrics_data:
                    metrics_data[key] = []

                metrics_data[key].append({
                    'timestamp': metric.timestamp.isoformat(),
                    'value': metric.value,
                    'metadata': metric.metadata
                })

            return {
                'metrics': metrics_data,
                'total_points': len(filtered_metrics),
                'time_range': f"{hours} hours",
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(f"Failed to get metrics history: {str(e)}")
            return {'status': 'error', 'error': str(e)}


# Export main service
__all__ = ['RealTimeMonitoringService', 'MonitoringConfig', 'AlertManager', 'MetricCollector']
