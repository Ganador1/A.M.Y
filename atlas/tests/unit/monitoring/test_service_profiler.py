"""
Tests para Service Profiler - Sistema de profiling de servicios
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import tempfile
import shutil
from pathlib import Path

from app.monitoring.service_profiler import (
    ServiceProfiler, PerformanceMetrics, ServiceProfile,
    profile_service, service_profiler
)


class TestServiceProfiler:
    """Tests para Service Profiler"""

    def setup_method(self):
        """Setup para cada test"""
        self.temp_dir = tempfile.mkdtemp()
        self.profiler = ServiceProfiler(
            max_metrics=1000,
            report_interval=1,
            output_dir=self.temp_dir
        )

    def teardown_method(self):
        """Cleanup después de cada test"""
        self.profiler.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test: Inicialización correcta del Service Profiler"""
        assert self.profiler.max_metrics == 1000
        assert self.profiler.report_interval == 1
        assert self.profiler.output_dir == Path(self.temp_dir)
        assert len(self.profiler.metrics) == 0
        assert len(self.profiler.service_profiles) == 0
        assert len(self.profiler.method_stats) == 0
        assert not self.profiler._running

    def test_start_stop(self):
        """Test: Inicio y parada del profiler"""
        # Iniciar
        self.profiler.start()
        assert self.profiler._running
        assert self.profiler._report_thread is not None
        assert self.profiler._report_thread.is_alive()
        
        # Parar
        self.profiler.stop()
        assert not self.profiler._running

    def test_profile_method_sync(self):
        """Test: Profiling de método síncrono"""
        @self.profiler.profile_method("test_service", "test_method")
        def test_function(x, y):
            time.sleep(0.1)  # Simular trabajo
            return x + y
        
        result = test_function(2, 3)
        
        assert result == 5
        assert len(self.profiler.metrics) == 1
        
        metric = self.profiler.metrics[0]
        assert metric.method_name == "test_method"
        assert metric.service_name == "test_service"
        assert metric.execution_time >= 0.1
        assert metric.success is True
        assert metric.error_message is None

    def test_profile_method_async(self):
        """Test: Profiling de método asíncrono"""
        @self.profiler.profile_method("test_service", "test_async_method")
        async def test_async_function(x, y):
            await asyncio.sleep(0.1)  # Simular trabajo asíncrono
            return x * y
        
        async def run_test():
            result = await test_async_function(2, 3)
            assert result == 6
            assert len(self.profiler.metrics) == 1
            
            metric = self.profiler.metrics[0]
            assert metric.method_name == "test_async_method"
            assert metric.service_name == "test_service"
            assert metric.execution_time >= 0.1
            assert metric.success is True
        
        asyncio.run(run_test())

    def test_profile_method_with_error(self):
        """Test: Profiling de método que falla"""
        @self.profiler.profile_method("test_service", "error_method")
        def error_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            error_function()
        
        assert len(self.profiler.metrics) == 1
        
        metric = self.profiler.metrics[0]
        assert metric.method_name == "error_method"
        assert metric.service_name == "test_service"
        assert metric.success is False
        assert metric.error_message == "Test error"

    def test_alert_thresholds(self):
        """Test: Verificación de umbrales de alerta"""
        alert_callback = Mock()
        self.profiler.add_alert_callback(alert_callback)
        
        # Simular métrica que excede umbral de tiempo
        metric = PerformanceMetrics(
            method_name="slow_method",
            service_name="test_service",
            execution_time=10.0,  # Excede umbral de 5.0
            memory_usage=100.0,
            cpu_usage=50.0,
            timestamp=datetime.now(),
            success=True
        )
        
        self.profiler._check_alert_thresholds(metric)
        
        # Verificar que se llamó el callback de alerta
        assert alert_callback.called
        call_args = alert_callback.call_args[0]
        assert call_args[0] == "execution_time"
        assert call_args[1]["value"] == 10.0
        assert call_args[1]["threshold"] == 5.0

    def test_memory_usage_alert(self):
        """Test: Alerta por uso de memoria"""
        alert_callback = Mock()
        self.profiler.add_alert_callback(alert_callback)
        
        # Simular métrica que excede umbral de memoria
        metric = PerformanceMetrics(
            method_name="memory_intensive_method",
            service_name="test_service",
            execution_time=1.0,
            memory_usage=2000.0,  # Excede umbral de 1000.0
            cpu_usage=50.0,
            timestamp=datetime.now(),
            success=True
        )
        
        self.profiler._check_alert_thresholds(metric)
        
        # Verificar que se llamó el callback de alerta
        assert alert_callback.called
        call_args = alert_callback.call_args[0]
        assert call_args[0] == "memory_usage"
        assert call_args[1]["value"] == 2000.0

    def test_cpu_usage_alert(self):
        """Test: Alerta por uso de CPU"""
        alert_callback = Mock()
        self.profiler.add_alert_callback(alert_callback)
        
        # Simular métrica que excede umbral de CPU
        metric = PerformanceMetrics(
            method_name="cpu_intensive_method",
            service_name="test_service",
            execution_time=1.0,
            memory_usage=100.0,
            cpu_usage=90.0,  # Excede umbral de 80.0
            timestamp=datetime.now(),
            success=True
        )
        
        self.profiler._check_alert_thresholds(metric)
        
        # Verificar que se llamó el callback de alerta
        assert alert_callback.called
        call_args = alert_callback.call_args[0]
        assert call_args[0] == "cpu_usage"
        assert call_args[1]["value"] == 90.0

    def test_error_rate_alert(self):
        """Test: Alerta por tasa de error"""
        alert_callback = Mock()
        self.profiler.add_alert_callback(alert_callback)
        
        # Simular múltiples métricas con alta tasa de error
        for i in range(10):
            metric = PerformanceMetrics(
                method_name="error_prone_method",
                service_name="test_service",
                execution_time=1.0,
                memory_usage=100.0,
                cpu_usage=50.0,
                timestamp=datetime.now(),
                success=(i < 2)  # Solo 2 de 10 exitosos (80% error rate)
            )
            self.profiler._record_metrics(
                metric.method_name, metric.service_name, metric.execution_time,
                metric.memory_usage, metric.cpu_usage, metric.success,
                metric.error_message, metric.input_size or 0, metric.output_size or 0
            )
        
        # Verificar que se generó alerta por tasa de error
        # (Esto se verificaría en el reporte, no en métricas individuales)

    def test_calculate_size(self):
        """Test: Cálculo de tamaño de objetos"""
        # Test con objetos simples
        size1 = self.profiler._calculate_size("test", 123, {"key": "value"})
        assert size1 > 0
        
        # Test con objetos complejos
        complex_obj = {
            "list": [1, 2, 3, 4, 5],
            "nested": {"a": 1, "b": 2},
            "string": "test string"
        }
        size2 = self.profiler._calculate_size(complex_obj)
        assert size2 > size1

    def test_get_service_profile(self):
        """Test: Obtener perfil de servicio"""
        # Agregar algunas métricas
        for i in range(5):
            metric = PerformanceMetrics(
                method_name="test_method",
                service_name="test_service",
                execution_time=1.0 + i * 0.1,
                memory_usage=100.0 + i * 10,
                cpu_usage=50.0 + i * 5,
                timestamp=datetime.now(),
                success=True
            )
            self.profiler._record_metrics(
                metric.method_name, metric.service_name, metric.execution_time,
                metric.memory_usage, metric.cpu_usage, metric.success,
                metric.error_message, metric.input_size or 0, metric.output_size or 0
            )
        
        # Actualizar perfiles
        self.profiler._update_service_profiles()
        
        # Obtener perfil
        profile = self.profiler.get_service_profile("test_service")
        assert profile is not None
        assert profile.service_name == "test_service"
        assert profile.total_calls == 5
        assert profile.successful_calls == 5
        assert profile.failed_calls == 0
        assert profile.error_rate == 0.0

    def test_get_method_stats(self):
        """Test: Obtener estadísticas de método"""
        # Agregar métricas para un método específico
        for i in range(3):
            metric = PerformanceMetrics(
                method_name="specific_method",
                service_name="test_service",
                execution_time=2.0 + i * 0.5,
                memory_usage=200.0 + i * 20,
                cpu_usage=60.0 + i * 10,
                timestamp=datetime.now(),
                success=True
            )
            self.profiler._record_metrics(
                metric.method_name, metric.service_name, metric.execution_time,
                metric.memory_usage, metric.cpu_usage, metric.success,
                metric.error_message, metric.input_size or 0, metric.output_size or 0
            )
        
        # Obtener estadísticas
        stats = self.profiler.get_method_stats("test_service", "specific_method")
        assert stats is not None
        assert stats["calls"] == 3
        assert stats["total_time"] == 7.5  # 2.0 + 2.5 + 3.0
        assert stats["min_time"] == 2.0
        assert stats["max_time"] == 3.0

    def test_get_recent_metrics(self):
        """Test: Obtener métricas recientes con filtros"""
        # Agregar métricas para diferentes servicios y métodos
        services = ["service1", "service2", "service1"]
        methods = ["method1", "method2", "method2"]
        
        for service, method in zip(services, methods):
            metric = PerformanceMetrics(
                method_name=method,
                service_name=service,
                execution_time=1.0,
                memory_usage=100.0,
                cpu_usage=50.0,
                timestamp=datetime.now(),
                success=True
            )
            self.profiler._record_metrics(
                metric.method_name, metric.service_name, metric.execution_time,
                metric.memory_usage, metric.cpu_usage, metric.success,
                metric.error_message, metric.input_size or 0, metric.output_size or 0
            )
        
        # Filtrar por servicio
        service1_metrics = self.profiler.get_recent_metrics(service_name="service1")
        assert len(service1_metrics) == 2
        
        # Filtrar por método
        method2_metrics = self.profiler.get_recent_metrics(method_name="method2")
        assert len(method2_metrics) == 2
        
        # Filtrar por servicio y método
        specific_metrics = self.profiler.get_recent_metrics(
            service_name="service1", method_name="method2"
        )
        assert len(specific_metrics) == 1

    def test_get_performance_summary(self):
        """Test: Obtener resumen de rendimiento"""
        # Agregar algunas métricas
        for i in range(5):
            metric = PerformanceMetrics(
                method_name="test_method",
                service_name="test_service",
                execution_time=1.0 + i * 0.1,
                memory_usage=100.0 + i * 10,
                cpu_usage=50.0 + i * 5,
                timestamp=datetime.now(),
                success=(i < 4)  # Una métrica fallida
            )
            self.profiler._record_metrics(
                metric.method_name, metric.service_name, metric.execution_time,
                metric.memory_usage, metric.cpu_usage, metric.success,
                metric.error_message, metric.input_size or 0, metric.output_size or 0
            )
        
        # Obtener resumen
        summary = self.profiler.get_performance_summary()
        
        assert "timestamp" in summary
        assert summary["total_calls"] == 5
        assert summary["successful_calls"] == 4
        assert summary["failed_calls"] == 1
        assert summary["error_rate"] == 0.2
        assert "avg_execution_time" in summary
        assert "min_execution_time" in summary
        assert "max_execution_time" in summary
        assert "avg_memory_usage" in summary
        assert "avg_cpu_usage" in summary
        assert "services" in summary

    def test_clear_metrics(self):
        """Test: Limpiar métricas"""
        # Agregar algunas métricas
        for i in range(3):
            metric = PerformanceMetrics(
                method_name="test_method",
                service_name="test_service",
                execution_time=1.0,
                memory_usage=100.0,
                cpu_usage=50.0,
                timestamp=datetime.now(),
                success=True
            )
            self.profiler._record_metrics(
                metric.method_name, metric.service_name, metric.execution_time,
                metric.memory_usage, metric.cpu_usage, metric.success,
                metric.error_message, metric.input_size or 0, metric.output_size or 0
            )
        
        # Verificar que hay métricas
        assert len(self.profiler.metrics) == 3
        
        # Limpiar
        self.profiler.clear_metrics()
        
        # Verificar que se limpiaron
        assert len(self.profiler.metrics) == 0
        assert len(self.profiler.service_profiles) == 0
        assert len(self.profiler.method_stats) == 0

    def test_max_metrics_limit(self):
        """Test: Límite máximo de métricas"""
        # Crear profiler con límite pequeño
        small_profiler = ServiceProfiler(max_metrics=3)
        
        # Agregar más métricas que el límite
        for i in range(5):
            metric = PerformanceMetrics(
                method_name="test_method",
                service_name="test_service",
                execution_time=1.0,
                memory_usage=100.0,
                cpu_usage=50.0,
                timestamp=datetime.now(),
                success=True
            )
            small_profiler._record_metrics(
                metric.method_name, metric.service_name, metric.execution_time,
                metric.memory_usage, metric.cpu_usage, metric.success,
                metric.error_message, metric.input_size or 0, metric.output_size or 0
            )
        
        # Verificar que solo se mantienen las últimas 3
        assert len(small_profiler.metrics) == 3
        
        small_profiler.stop()

    def test_report_generation(self):
        """Test: Generación de reportes"""
        # Agregar algunas métricas
        for i in range(3):
            metric = PerformanceMetrics(
                method_name="test_method",
                service_name="test_service",
                execution_time=1.0 + i * 0.1,
                memory_usage=100.0 + i * 10,
                cpu_usage=50.0 + i * 5,
                timestamp=datetime.now(),
                success=True
            )
            self.profiler._record_metrics(
                metric.method_name, metric.service_name, metric.execution_time,
                metric.memory_usage, metric.cpu_usage, metric.success,
                metric.error_message, metric.input_size or 0, metric.output_size or 0
            )
        
        # Generar reporte
        self.profiler._generate_report()
        
        # Verificar que se creó el archivo de reporte
        report_files = list(Path(self.temp_dir).glob("performance_report_*.json"))
        assert len(report_files) == 1
        
        # Verificar contenido del reporte
        with open(report_files[0]) as f:
            report = json.load(f)
        
        assert "timestamp" in report
        assert "total_metrics" in report
        assert "services" in report
        assert "test_service" in report["services"]

    def test_profile_service_decorator(self):
        """Test: Decorator de conveniencia profile_service"""
        @profile_service("test_service", "decorated_method")
        def decorated_function(x):
            return x * 2
        
        result = decorated_function(5)
        
        assert result == 10
        assert len(service_profiler.metrics) == 1
        
        metric = service_profiler.metrics[0]
        assert metric.method_name == "decorated_method"
        assert metric.service_name == "test_service"

    def test_thread_safety(self):
        """Test: Seguridad en hilos"""
        def add_metrics():
            for i in range(10):
                metric = PerformanceMetrics(
                    method_name="thread_method",
                    service_name="thread_service",
                    execution_time=1.0,
                    memory_usage=100.0,
                    cpu_usage=50.0,
                    timestamp=datetime.now(),
                    success=True
                )
                self.profiler._record_metrics(
                    metric.method_name, metric.service_name, metric.execution_time,
                    metric.memory_usage, metric.cpu_usage, metric.success,
                    metric.error_message, metric.input_size or 0, metric.output_size or 0
                )
        
        # Ejecutar en múltiples hilos
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=add_metrics)
            threads.append(thread)
            thread.start()
        
        # Esperar a que terminen
        for thread in threads:
            thread.join()
        
        # Verificar que se agregaron todas las métricas
        assert len(self.profiler.metrics) == 50  # 5 threads * 10 metrics each


class TestPerformanceMetrics:
    """Tests para PerformanceMetrics"""

    def test_initialization(self):
        """Test: Inicialización de PerformanceMetrics"""
        metric = PerformanceMetrics(
            method_name="test_method",
            service_name="test_service",
            execution_time=1.5,
            memory_usage=200.0,
            cpu_usage=75.0,
            timestamp=datetime.now(),
            success=True,
            error_message=None,
            input_size=1000,
            output_size=500
        )
        
        assert metric.method_name == "test_method"
        assert metric.service_name == "test_service"
        assert metric.execution_time == 1.5
        assert metric.memory_usage == 200.0
        assert metric.cpu_usage == 75.0
        assert metric.success is True
        assert metric.error_message is None
        assert metric.input_size == 1000
        assert metric.output_size == 500

    def test_default_values(self):
        """Test: Valores por defecto de PerformanceMetrics"""
        metric = PerformanceMetrics(
            method_name="test_method",
            service_name="test_service",
            execution_time=1.0,
            memory_usage=100.0,
            cpu_usage=50.0,
            timestamp=datetime.now(),
            success=True
        )
        
        assert metric.error_message is None
        assert metric.input_size is None
        assert metric.output_size is None
        assert metric.metadata == {}


class TestServiceProfile:
    """Tests para ServiceProfile"""

    def test_initialization(self):
        """Test: Inicialización de ServiceProfile"""
        profile = ServiceProfile(
            service_name="test_service",
            total_calls=100,
            successful_calls=95,
            failed_calls=5,
            avg_execution_time=1.5,
            min_execution_time=0.1,
            max_execution_time=5.0,
            avg_memory_usage=200.0,
            avg_cpu_usage=60.0,
            error_rate=0.05,
            last_updated=datetime.now()
        )
        
        assert profile.service_name == "test_service"
        assert profile.total_calls == 100
        assert profile.successful_calls == 95
        assert profile.failed_calls == 5
        assert profile.avg_execution_time == 1.5
        assert profile.min_execution_time == 0.1
        assert profile.max_execution_time == 5.0
        assert profile.avg_memory_usage == 200.0
        assert profile.avg_cpu_usage == 60.0
        assert profile.error_rate == 0.05

    def test_default_values(self):
        """Test: Valores por defecto de ServiceProfile"""
        profile = ServiceProfile(
            service_name="test_service",
            total_calls=10,
            successful_calls=10,
            failed_calls=0,
            avg_execution_time=1.0,
            min_execution_time=0.5,
            max_execution_time=2.0,
            avg_memory_usage=100.0,
            avg_cpu_usage=50.0,
            error_rate=0.0,
            last_updated=datetime.now()
        )
        
        assert profile.methods == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
