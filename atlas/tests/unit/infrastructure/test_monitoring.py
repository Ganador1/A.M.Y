#!/usr/bin/env python3
"""
Unit tests for AXIOM Advanced Monitoring System
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.monitoring import (
    MonitoringSystem,
    AlertManager,
    MetricsCollector,
    AlertRule,
    Alert,
    AlertSeverity,
    AlertStatus,
    Metric,
    SystemMetrics,
    ApplicationMetrics
)


class TestMetricsCollector:
    """Test cases for MetricsCollector"""

    @pytest.fixture
    def collector(self):
        return MetricsCollector()

    @pytest.mark.asyncio
    async def test_collect_system_metrics(self, collector):
        """Test collection of system metrics"""
        with patch('psutil.cpu_percent', return_value=45.5), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk, \
             patch('psutil.net_io_counters') as mock_net, \
             patch('psutil.getloadavg', return_value=(1.5, 1.2, 1.0)):

            # Mock memory
            mock_memory.return_value = Mock()
            mock_memory.return_value.percent = 60.0
            mock_memory.return_value.used = 6 * (1024**3)  # 6GB
            mock_memory.return_value.total = 16 * (1024**3)  # 16GB

            # Mock disk
            mock_disk.return_value = Mock()
            mock_disk.return_value.percent = 75.0
            mock_disk.return_value.used = 75 * (1024**3)  # 75GB
            mock_disk.return_value.total = 100 * (1024**3)  # 100GB

            # Mock network
            mock_net.return_value = Mock()
            mock_net.return_value.bytes_sent = 1000000
            mock_net.return_value.bytes_recv = 2000000

            metrics = await collector.collect_system_metrics()

            assert metrics.cpu_percent == 45.5
            assert metrics.memory_percent == 60.0
            assert metrics.memory_used_gb == 6.0
            assert metrics.memory_total_gb == 16.0
            assert metrics.disk_percent == 75.0
            assert metrics.disk_used_gb == 75.0
            assert metrics.disk_total_gb == 100.0
            assert metrics.network_bytes_sent == 1000000
            assert metrics.network_bytes_recv == 2000000
            assert metrics.load_average == (1.5, 1.2, 1.0)

    @pytest.mark.asyncio
    async def test_collect_application_metrics(self, collector):
        """Test collection of application metrics"""
        metrics = await collector.collect_application_metrics()

        # Should return default values since not implemented yet
        assert metrics.active_connections == 0
        assert metrics.total_requests == 0
        assert metrics.error_rate == 0.0
        assert metrics.avg_response_time == 0.0
        assert metrics.throughput == 0.0
        assert metrics.cache_hit_rate == 0.0
        assert metrics.gpu_memory_used == 0.0
        assert metrics.gpu_memory_total == 0.0


class TestAlertManager:
    """Test cases for AlertManager"""

    @pytest.fixture
    def alert_manager(self):
        return AlertManager()

    def test_add_alert_rule(self, alert_manager):
        """Test adding alert rules"""
        rule = AlertRule(
            name="test_rule",
            description="Test alert rule",
            metric_name="cpu_percent",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.HIGH
        )

        alert_manager.add_alert_rule(rule)
        assert "test_rule" in alert_manager.alert_rules
        assert alert_manager.alert_rules["test_rule"] == rule

    def test_remove_alert_rule(self, alert_manager):
        """Test removing alert rules"""
        rule = AlertRule(
            name="test_rule",
            description="Test alert rule",
            metric_name="cpu_percent",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.HIGH
        )

        alert_manager.add_alert_rule(rule)
        assert "test_rule" in alert_manager.alert_rules

        alert_manager.remove_alert_rule("test_rule")
        assert "test_rule" not in alert_manager.alert_rules

    @pytest.mark.asyncio
    async def test_check_alerts_trigger(self, alert_manager):
        """Test alert triggering"""
        rule = AlertRule(
            name="high_cpu",
            description="High CPU usage",
            metric_name="cpu_percent",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.HIGH
        )

        alert_manager.add_alert_rule(rule)

        # Should trigger alert
        metrics = {"cpu_percent": 85.0}
        await alert_manager.check_alerts(metrics)

        assert len(alert_manager.active_alerts) == 1
        alert = list(alert_manager.active_alerts.values())[0]
        assert alert.rule_name == "high_cpu"
        assert alert.value == 85.0
        assert alert.threshold == 80.0

    @pytest.mark.asyncio
    async def test_check_alerts_resolve(self, alert_manager):
        """Test alert resolution"""
        rule = AlertRule(
            name="high_cpu",
            description="High CPU usage",
            metric_name="cpu_percent",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.HIGH
        )

        alert_manager.add_alert_rule(rule)

        # Trigger alert
        metrics = {"cpu_percent": 85.0}
        await alert_manager.check_alerts(metrics)
        assert len(alert_manager.active_alerts) == 1

        # Resolve alert
        metrics = {"cpu_percent": 70.0}
        await alert_manager.check_alerts(metrics)
        assert len(alert_manager.active_alerts) == 0

    def test_acknowledge_alert(self, alert_manager):
        """Test alert acknowledgment"""
        rule = AlertRule(
            name="high_cpu",
            description="High CPU usage",
            metric_name="cpu_percent",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.HIGH
        )

        alert_manager.add_alert_rule(rule)
        alert_manager.active_alerts["test_key"] = Alert(
            id="test_alert",
            rule_name="high_cpu",
            description="High CPU usage",
            severity=AlertSeverity.HIGH,
            status=AlertStatus.ACTIVE,
            value=85.0,
            threshold=80.0,
            created_at=datetime.now()
        )

        alert_manager.acknowledge_alert("test_alert", "test_user")

        alert = alert_manager.active_alerts["test_key"]
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "test_user"


class TestMonitoringSystem:
    """Test cases for MonitoringSystem"""

    @pytest.fixture
    def monitoring_system(self):
        return MonitoringSystem()

    @pytest.mark.asyncio
    async def test_start_stop(self, monitoring_system):
        """Test starting and stopping monitoring system"""
        assert not monitoring_system._running

        await monitoring_system.start()
        assert monitoring_system._running

        await monitoring_system.stop()
        assert not monitoring_system._running

    @pytest.mark.asyncio
    async def test_get_current_metrics(self, monitoring_system):
        """Test getting current metrics"""
        with patch.object(monitoring_system.metrics_collector, 'collect_system_metrics', new_callable=AsyncMock) as mock_sys, \
             patch.object(monitoring_system.metrics_collector, 'collect_application_metrics', new_callable=AsyncMock) as mock_app:

            # Mock system metrics
            sys_metrics = SystemMetrics(
                cpu_percent=50.0,
                memory_percent=60.0,
                memory_used_gb=6.0,
                memory_total_gb=16.0,
                disk_percent=70.0,
                disk_used_gb=70.0,
                disk_total_gb=100.0,
                network_bytes_sent=1000,
                network_bytes_recv=2000,
                load_average=(1.0, 1.0, 1.0)
            )

            # Mock application metrics
            app_metrics = ApplicationMetrics(
                active_connections=10,
                total_requests=100,
                error_rate=2.5,
                avg_response_time=150.0,
                throughput=50.0,
                cache_hit_rate=85.0,
                gpu_memory_used=2.0,
                gpu_memory_total=8.0
            )

            mock_sys.return_value = sys_metrics
            mock_app.return_value = app_metrics

            metrics = await monitoring_system.get_current_metrics()

            assert metrics["system"]["cpu_percent"] == 50.0
            assert metrics["system"]["memory_percent"] == 60.0
            assert metrics["application"]["active_connections"] == 10
            assert metrics["application"]["error_rate"] == 2.5

    def test_get_metrics_history(self, monitoring_system):
        """Test getting metrics history"""
        # Add some test metrics
        now = datetime.now()
        metrics = [
            Metric("cpu_percent", 50.0, now - timedelta(minutes=30)),
            Metric("cpu_percent", 60.0, now - timedelta(minutes=15)),
            Metric("cpu_percent", 70.0, now)
        ]
        monitoring_system.metrics_history = metrics

        history = monitoring_system.get_metrics_history("cpu_percent", 1)
        assert len(history) == 3
        assert all(m.name == "cpu_percent" for m in history)

    @pytest.mark.asyncio
    async def test_get_monitoring_status(self, monitoring_system):
        """Test getting monitoring status"""
        with patch.object(monitoring_system, 'get_current_metrics', new_callable=AsyncMock) as mock_metrics:
            mock_metrics.return_value = {
                "system": {"cpu_percent": 50.0},
                "application": {"active_connections": 10}
            }

            status = await monitoring_system.get_monitoring_status()

            assert "status" in status
            assert "timestamp" in status
            assert "current_metrics" in status
            assert "alerts" in status
            assert "metrics_history" in status


class TestAlertRule:
    """Test cases for AlertRule dataclass"""

    def test_alert_rule_creation(self):
        """Test creating alert rules"""
        rule = AlertRule(
            name="test_rule",
            description="Test description",
            metric_name="cpu_percent",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.HIGH,
            enabled=True,
            cooldown_minutes=10,
            labels={"env": "prod"}
        )

        assert rule.name == "test_rule"
        assert rule.description == "Test description"
        assert rule.metric_name == "cpu_percent"
        assert rule.condition == ">"
        assert rule.threshold == 80.0
        assert rule.severity == AlertSeverity.HIGH
        assert rule.enabled
        assert rule.cooldown_minutes == 10
        assert rule.labels == {"env": "prod"}


class TestAlert:
    """Test cases for Alert dataclass"""

    def test_alert_creation(self):
        """Test creating alerts"""
        created_at = datetime.now()
        alert = Alert(
            id="test_id",
            rule_name="test_rule",
            description="Test alert",
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.ACTIVE,
            value=85.0,
            threshold=80.0,
            created_at=created_at,
            labels={"source": "test"}
        )

        assert alert.id == "test_id"
        assert alert.rule_name == "test_rule"
        assert alert.description == "Test alert"
        assert alert.severity == AlertSeverity.MEDIUM
        assert alert.status == AlertStatus.ACTIVE
        assert alert.value == 85.0
        assert alert.threshold == 80.0
        assert alert.created_at == created_at
        assert alert.labels == {"source": "test"}


if __name__ == "__main__":
    pytest.main([__file__])
