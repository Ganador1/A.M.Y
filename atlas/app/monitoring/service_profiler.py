"""
Service Profiler - Sistema de profiling de servicios para AXIOM ATLAS
====================================================================

Este módulo implementa un sistema de profiling para monitorear el rendimiento
de los servicios de la plataforma AXIOM. Proporciona métricas detalladas de
tiempo de ejecución, uso de memoria, CPU y otros indicadores de rendimiento.

Funcionalidades:
- Profiling automático de métodos de servicios
- Métricas de tiempo de ejecución
- Monitoreo de uso de memoria
- Análisis de CPU y recursos del sistema
- Generación de reportes de rendimiento
- Alertas automáticas por umbrales
- Integración con sistemas de observabilidad

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

import time
import psutil
import threading
import asyncio
from functools import wraps
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import logging
from pathlib import Path
import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento de un método o servicio."""
    
    method_name: str
    service_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceProfile:
    """Perfil de rendimiento de un servicio completo."""
    
    service_name: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    avg_execution_time: float
    min_execution_time: float
    max_execution_time: float
    avg_memory_usage: float
    avg_cpu_usage: float
    error_rate: float
    last_updated: datetime
    methods: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class ServiceProfiler:
    """Profiler principal para servicios de AXIOM."""
    
    def __init__(self, 
                 max_metrics: int = 10000,
                 report_interval: int = 300,  # 5 minutos
                 alert_thresholds: Optional[Dict[str, float]] = None,
                 output_dir: str = "logs/profiling"):
        """
        Inicializar el Service Profiler.
        
        Args:
            max_metrics: Número máximo de métricas a mantener en memoria
            report_interval: Intervalo en segundos para generar reportes
            alert_thresholds: Umbrales para alertas de rendimiento
            output_dir: Directorio para guardar reportes
        """
        self.max_metrics = max_metrics
        self.report_interval = report_interval
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Umbrales por defecto
        self.alert_thresholds = alert_thresholds or {
            "execution_time": 5.0,  # 5 segundos
            "memory_usage": 1000.0,  # 1GB
            "cpu_usage": 80.0,  # 80%
            "error_rate": 0.1  # 10%
        }
        
        # Almacenamiento de métricas
        self.metrics: deque = deque(maxlen=max_metrics)
        self.service_profiles: Dict[str, ServiceProfile] = {}
        self.method_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "calls": 0,
            "total_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "errors": 0
        })
        
        # Lock para thread safety
        self._lock = threading.Lock()
        
        # Proceso de reporte en background
        self._report_thread = None
        self._running = False
        
        # Callbacks para alertas
        self.alert_callbacks: List[Callable] = []
        
        logger.info("Service Profiler initialized")
    
    def start(self):
        """Iniciar el profiler y el proceso de reporte en background."""
        if self._running:
            return
        
        self._running = True
        self._report_thread = threading.Thread(target=self._report_loop, daemon=True)
        self._report_thread.start()
        logger.info("Service Profiler started")
    
    def stop(self):
        """Detener el profiler."""
        self._running = False
        if self._report_thread:
            self._report_thread.join(timeout=5)
        logger.info("Service Profiler stopped")
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Agregar callback para alertas de rendimiento."""
        self.alert_callbacks.append(callback)
    
    def profile_method(self, 
                      service_name: str,
                      method_name: Optional[str] = None,
                      track_memory: bool = True,
                      track_cpu: bool = True):
        """
        Decorator para profiling automático de métodos.
        
        Args:
            service_name: Nombre del servicio
            method_name: Nombre del método (opcional, se detecta automáticamente)
            track_memory: Si rastrear uso de memoria
            track_cpu: Si rastrear uso de CPU
        """
        def decorator(func):
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self._profile_sync(
                    func, service_name, method_name or func.__name__,
                    track_memory, track_cpu, *args, **kwargs
                )
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._profile_async(
                    func, service_name, method_name or func.__name__,
                    track_memory, track_cpu, *args, **kwargs
                )
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def _profile_sync(self, 
                     func: Callable,
                     service_name: str,
                     method_name: str,
                     track_memory: bool,
                     track_cpu: bool,
                     *args, **kwargs):
        """Profiling para funciones síncronas."""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.Process().cpu_percent()
        
        success = True
        error_message = None
        result = None
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            end_cpu = psutil.Process().cpu_percent()
            
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory if track_memory else 0.0
            cpu_usage = end_cpu - start_cpu if track_cpu else 0.0
            
            # Calcular tamaños de entrada y salida
            input_size = self._calculate_size(args, kwargs)
            output_size = self._calculate_size(result) if result is not None else 0
            
            self._record_metrics(
                method_name, service_name, execution_time,
                memory_usage, cpu_usage, success, error_message,
                input_size, output_size
            )
    
    async def _profile_async(self, 
                           func: Callable,
                           service_name: str,
                           method_name: str,
                           track_memory: bool,
                           track_cpu: bool,
                           *args, **kwargs):
        """Profiling para funciones asíncronas."""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.Process().cpu_percent()
        
        success = True
        error_message = None
        result = None
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            end_cpu = psutil.Process().cpu_percent()
            
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory if track_memory else 0.0
            cpu_usage = end_cpu - start_cpu if track_cpu else 0.0
            
            # Calcular tamaños de entrada y salida
            input_size = self._calculate_size(args, kwargs)
            output_size = self._calculate_size(result) if result is not None else 0
            
            self._record_metrics(
                method_name, service_name, execution_time,
                memory_usage, cpu_usage, success, error_message,
                input_size, output_size
            )
    
    def _calculate_size(self, *objects) -> int:
        """Calcular el tamaño aproximado de objetos en bytes."""
        try:
            return len(json.dumps(objects, default=str).encode('utf-8'))
        except Exception  # TODO: Change to JSONDecodeError or ValueError:
            return 0
    
    def _record_metrics(self, 
                       method_name: str,
                       service_name: str,
                       execution_time: float,
                       memory_usage: float,
                       cpu_usage: float,
                       success: bool,
                       error_message: Optional[str],
                       input_size: int,
                       output_size: int):
        """Registrar métricas de rendimiento."""
        with self._lock:
            # Crear métrica
            metric = PerformanceMetrics(
                method_name=method_name,
                service_name=service_name,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                timestamp=datetime.now(),
                success=success,
                error_message=error_message,
                input_size=input_size,
                output_size=output_size
            )
            
            # Agregar a la cola
            self.metrics.append(metric)
            
            # Actualizar estadísticas del método
            method_key = f"{service_name}.{method_name}"
            stats = self.method_stats[method_key]
            stats["calls"] += 1
            stats["total_time"] += execution_time
            stats["min_time"] = min(stats["min_time"], execution_time)
            stats["max_time"] = max(stats["max_time"], execution_time)
            stats["memory_usage"] += memory_usage
            stats["cpu_usage"] += cpu_usage
            if not success:
                stats["errors"] += 1
            
            # Verificar umbrales de alerta
            self._check_alert_thresholds(metric)
    
    def _check_alert_thresholds(self, metric: PerformanceMetrics):
        """Verificar si se han superado los umbrales de alerta."""
        alerts = []
        
        if metric.execution_time > self.alert_thresholds["execution_time"]:
            alerts.append({
                "type": "execution_time",
                "value": metric.execution_time,
                "threshold": self.alert_thresholds["execution_time"],
                "service": metric.service_name,
                "method": metric.method_name
            })
        
        if metric.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "type": "memory_usage",
                "value": metric.memory_usage,
                "threshold": self.alert_thresholds["memory_usage"],
                "service": metric.service_name,
                "method": metric.method_name
            })
        
        if metric.cpu_usage > self.alert_thresholds["cpu_usage"]:
            alerts.append({
                "type": "cpu_usage",
                "value": metric.cpu_usage,
                "threshold": self.alert_thresholds["cpu_usage"],
                "service": metric.service_name,
                "method": metric.method_name
            })
        
        # Enviar alertas
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert["type"], alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
    
    def _report_loop(self):
        """Loop principal para generar reportes periódicos."""
        while self._running:
            try:
                await asyncio.sleep(self.report_interval)
                if self._running:
                    self._generate_report()
            except Exception as e:
                logger.error(f"Error in report loop: {e}")
    
    def _generate_report(self):
        """Generar reporte de rendimiento."""
        try:
            with self._lock:
                # Actualizar perfiles de servicios
                self._update_service_profiles()
                
                # Generar reporte
                report = {
                    "timestamp": datetime.now().isoformat(),
                    "total_metrics": len(self.metrics),
                    "services": {}
                }
                
                for service_name, profile in self.service_profiles.items():
                    report["services"][service_name] = {
                        "total_calls": profile.total_calls,
                        "successful_calls": profile.successful_calls,
                        "failed_calls": profile.failed_calls,
                        "avg_execution_time": profile.avg_execution_time,
                        "min_execution_time": profile.min_execution_time,
                        "max_execution_time": profile.max_execution_time,
                        "avg_memory_usage": profile.avg_memory_usage,
                        "avg_cpu_usage": profile.avg_cpu_usage,
                        "error_rate": profile.error_rate,
                        "methods": profile.methods
                    }
                
                # Guardar reporte
                report_file = self.output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with aiofiles.open(report_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                logger.info(f"Performance report generated: {report_file}")
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
    
    def _update_service_profiles(self):
        """Actualizar perfiles de servicios basados en métricas recientes."""
        # Agrupar métricas por servicio
        service_metrics = defaultdict(list)
        for metric in self.metrics:
            service_metrics[metric.service_name].append(metric)
        
        # Actualizar perfiles
        for service_name, metrics in service_metrics.items():
            if not metrics:
                continue
            
            total_calls = len(metrics)
            successful_calls = sum(1 for m in metrics if m.success)
            failed_calls = total_calls - successful_calls
            
            execution_times = [m.execution_time for m in metrics]
            memory_usages = [m.memory_usage for m in metrics]
            cpu_usages = [m.cpu_usage for m in metrics]
            
            # Agrupar por método
            method_stats = defaultdict(lambda: {
                "calls": 0,
                "total_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "memory_usage": 0.0,
                "cpu_usage": 0.0,
                "errors": 0
            })
            
            for metric in metrics:
                method_stats[metric.method_name]["calls"] += 1
                method_stats[metric.method_name]["total_time"] += metric.execution_time
                method_stats[metric.method_name]["min_time"] = min(
                    method_stats[metric.method_name]["min_time"], metric.execution_time
                )
                method_stats[metric.method_name]["max_time"] = max(
                    method_stats[metric.method_name]["max_time"], metric.execution_time
                )
                method_stats[metric.method_name]["memory_usage"] += metric.memory_usage
                method_stats[metric.method_name]["cpu_usage"] += metric.cpu_usage
                if not metric.success:
                    method_stats[metric.method_name]["errors"] += 1
            
            # Calcular promedios para métodos
            for method_name, stats in method_stats.items():
                if stats["calls"] > 0:
                    stats["avg_time"] = stats["total_time"] / stats["calls"]
                    stats["avg_memory"] = stats["memory_usage"] / stats["calls"]
                    stats["avg_cpu"] = stats["cpu_usage"] / stats["calls"]
                    stats["error_rate"] = stats["errors"] / stats["calls"]
            
            # Crear perfil del servicio
            profile = ServiceProfile(
                service_name=service_name,
                total_calls=total_calls,
                successful_calls=successful_calls,
                failed_calls=failed_calls,
                avg_execution_time=sum(execution_times) / len(execution_times),
                min_execution_time=min(execution_times),
                max_execution_time=max(execution_times),
                avg_memory_usage=sum(memory_usages) / len(memory_usages),
                avg_cpu_usage=sum(cpu_usages) / len(cpu_usages),
                error_rate=failed_calls / total_calls,
                last_updated=datetime.now(),
                methods=dict(method_stats)
            )
            
            self.service_profiles[service_name] = profile
    
    def get_service_profile(self, service_name: str) -> Optional[ServiceProfile]:
        """Obtener perfil de rendimiento de un servicio."""
        with self._lock:
            return self.service_profiles.get(service_name)
    
    def get_method_stats(self, service_name: str, method_name: str) -> Optional[Dict[str, Any]]:
        """Obtener estadísticas de un método específico."""
        method_key = f"{service_name}.{method_name}"
        return self.method_stats.get(method_key)
    
    def get_recent_metrics(self, 
                          service_name: Optional[str] = None,
                          method_name: Optional[str] = None,
                          limit: int = 100) -> List[PerformanceMetrics]:
        """Obtener métricas recientes con filtros opcionales."""
        with self._lock:
            filtered_metrics = []
            for metric in reversed(self.metrics):
                if service_name and metric.service_name != service_name:
                    continue
                if method_name and metric.method_name != method_name:
                    continue
                
                filtered_metrics.append(metric)
                if len(filtered_metrics) >= limit:
                    break
            
            return filtered_metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtener resumen de rendimiento del sistema."""
        with self._lock:
            if not self.metrics:
                return {"message": "No metrics available"}
            
            recent_metrics = list(self.metrics)[-100:]  # Últimas 100 métricas
            
            total_calls = len(recent_metrics)
            successful_calls = sum(1 for m in recent_metrics if m.success)
            failed_calls = total_calls - successful_calls
            
            execution_times = [m.execution_time for m in recent_metrics]
            memory_usages = [m.memory_usage for m in recent_metrics]
            cpu_usages = [m.cpu_usage for m in recent_metrics]
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "error_rate": failed_calls / total_calls if total_calls > 0 else 0,
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "min_execution_time": min(execution_times),
                "max_execution_time": max(execution_times),
                "avg_memory_usage": sum(memory_usages) / len(memory_usages),
                "avg_cpu_usage": sum(cpu_usages) / len(cpu_usages),
                "services": list(self.service_profiles.keys())
            }
    
    def clear_metrics(self):
        """Limpiar todas las métricas almacenadas."""
        with self._lock:
            self.metrics.clear()
            self.service_profiles.clear()
            self.method_stats.clear()
            logger.info("All metrics cleared")


# Instancia global del profiler
service_profiler = ServiceProfiler()

# Decorator de conveniencia
def profile_service(service_name: str, method_name: Optional[str] = None):
    """Decorator de conveniencia para profiling de servicios."""
    return service_profiler.profile_method(service_name, method_name)


# Función de utilidad para alertas
def log_alert(alert_type: str, alert_data: Dict[str, Any]):
    """Callback por defecto para alertas de rendimiento."""
    logger.warning(f"Performance alert - {alert_type}: {alert_data}")


# Configurar callback por defecto
service_profiler.add_alert_callback(log_alert)
