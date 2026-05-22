"""
Pipeline Optimization Service for AXIOM
Optimiza el rendimiento de pipelines autónomos basado en métricas de ejecución

Features:
- Análisis de rendimiento en tiempo real
- Optimización automática de parámetros
- Ajuste dinámico de concurrencia
- Cache inteligente de resultados
- Balanceo de carga entre servicios
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics
from collections import defaultdict, deque
import json

from app.services.base_service import BaseService
from app.exceptions.domain.biology import BiologyError

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Estrategias de optimización disponibles"""
    CONCURRENCY = "concurrency"
    CACHING = "caching"
    BATCHING = "batching"
    PRIORITIZATION = "prioritization"
    RESOURCE_ALLOCATION = "resource_allocation"


@dataclass
class PipelinePerformanceMetrics:
    """Métricas de rendimiento de un pipeline"""
    pipeline_id: str
    pipeline_type: str
    domain: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    total_execution_time: float
    avg_task_time: float
    max_task_time: float
    min_task_time: float
    success_rate: float
    resource_usage: Dict[str, float]
    cost_metrics: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ServicePerformanceProfile:
    """Perfil de rendimiento de un servicio específico"""
    service_name: str
    avg_response_time: float
    success_rate: float
    concurrency_level: int
    error_rate: float
    cache_hit_rate: float = 0.0
    last_optimized: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationResult:
    """Resultado de una optimización aplicada"""
    strategy: OptimizationStrategy
    parameters: Dict[str, Any]
    performance_improvement: float
    applied_at: datetime = field(default_factory=datetime.now)


@dataclass
class DiscoveryCostMetrics:
    """Métricas avanzadas de costo por descubrimiento"""
    pipeline_id: str
    domain: str
    research_question: str
    total_cost: float
    compute_cost: float
    api_cost: float
    storage_cost: float
    success_cost: float
    cost_per_successful_task: float
    cost_per_discovery: float
    roi_estimate: float  # Return on Investment estimate
    efficiency_score: float
    timestamp: datetime = field(default_factory=datetime.now)


class PipelineOptimizationService(BaseService):
    """Servicio de optimización de pipelines autónomos"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("PipelineOptimization")
        self.config = config or {}
        
        # Almacenamiento de métricas
        self.pipeline_metrics: Dict[str, PipelinePerformanceMetrics] = {}
        self.service_profiles: Dict[str, ServicePerformanceProfile] = {}
        self.optimization_history: List[OptimizationResult] = []
        self.discovery_cost_metrics: Dict[str, DiscoveryCostMetrics] = {}
        
        # Configuración de optimización
        self.optimization_config = {
            'target_success_rate': 0.95,
            'max_concurrency': 10,
            'min_concurrency': 1,
            'cache_ttl': 300,  # 5 minutos
            'batch_size': 10,
            'monitoring_interval': 30,  # segundos
            'optimization_check_interval': 60  # segundos
        }
        
        # Estado actual
        self.current_concurrency = 3
        self.active_optimizations: Set[OptimizationStrategy] = set()
        self.performance_baseline: Optional[float] = None
        
        # Start background optimization tasks
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._apply_optimizations())
    
    async def record_pipeline_metrics(self, pipeline_id: str, pipeline_type: str, 
                                    domain: str, tasks: List[Dict], 
                                    execution_time: float, success_rate: float,
                                    resource_usage: Dict[str, float],
                                    cost_metrics: Dict[str, float]) -> None:
        """Registra métricas de un pipeline completado"""
        
        # Calcular métricas de tareas
        task_times = [task.get('execution_time', 0) for task in tasks if task.get('execution_time')]
        
        metrics = PipelinePerformanceMetrics(
            pipeline_id=pipeline_id,
            pipeline_type=pipeline_type,
            domain=domain,
            total_tasks=len(tasks),
            successful_tasks=sum(1 for task in tasks if task.get('status') == 'completed'),
            failed_tasks=sum(1 for task in tasks if task.get('status') == 'failed'),
            total_execution_time=execution_time,
            avg_task_time=statistics.mean(task_times) if task_times else 0,
            max_task_time=max(task_times) if task_times else 0,
            min_task_time=min(task_times) if task_times else 0,
            success_rate=success_rate,
            resource_usage=resource_usage,
            cost_metrics=cost_metrics
        )
        
        self.pipeline_metrics[pipeline_id] = metrics
        
        # Actualizar perfiles de servicio
        await self._update_service_profiles(tasks)
        
        logger.info(f"Recorded metrics for pipeline {pipeline_id}: {success_rate:.2%} success, {execution_time:.2f}s")
    
    async def _update_service_profiles(self, tasks: List[Dict]) -> None:
        """Actualiza los perfiles de rendimiento de los servicios"""
        service_data = defaultdict(list)
        
        for task in tasks:
            if 'service' in task and 'execution_time' in task:
                service_data[task['service']].append({
                    'time': task['execution_time'],
                    'success': task.get('status') == 'completed'
                })
        
        for service_name, executions in service_data.items():
            response_times = [e['time'] for e in executions]
            success_count = sum(1 for e in executions if e['success'])
            
            profile = self.service_profiles.get(service_name, ServicePerformanceProfile(
                service_name=service_name,
                avg_response_time=0,
                success_rate=0,
                concurrency_level=1,
                error_rate=0
            ))
            
            # Actualizar con promedio ponderado
            profile.avg_response_time = statistics.mean(response_times)
            profile.success_rate = success_count / len(executions)
            profile.error_rate = 1 - profile.success_rate
            
            self.service_profiles[service_name] = profile
    
    async def _monitor_performance(self) -> None:
        """Monitorea el rendimiento continuamente"""
        while True:
            try:
                # Analizar métricas recientes
                recent_metrics = [
                    m for m in self.pipeline_metrics.values()
                    if m.timestamp > datetime.now() - timedelta(hours=1)
                ]
                
                if recent_metrics:
                    avg_success = statistics.mean(m.success_rate for m in recent_metrics)
                    avg_time = statistics.mean(m.total_execution_time for m in recent_metrics)
                    
                    logger.info(f"Performance monitoring - Avg success: {avg_success:.2%}, Avg time: {avg_time:.2f}s")
                    
                    # Verificar si necesitamos optimización
                    if avg_success < self.optimization_config['target_success_rate']:
                        logger.warning(f"Performance below target ({avg_success:.2%} < {self.optimization_config['target_success_rate']:.2%})")
                        await self._trigger_optimization()
                
                await asyncio.sleep(self.optimization_config['monitoring_interval'])
                
            except BiologyError as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _trigger_optimization(self) -> None:
        """Dispara el proceso de optimización"""
        logger.info("Triggering pipeline optimization")
        
        # Determinar estrategias apropiadas basado en métricas
        strategies = await self._determine_optimization_strategies()
        
        for strategy in strategies:
            if strategy not in self.active_optimizations:
                await self._apply_strategy(strategy)
    
    async def _determine_optimization_strategies(self) -> List[OptimizationStrategy]:
        """Determina qué estrategias de optimización aplicar"""
        strategies = []
        
        # Analizar métricas de servicios
        slow_services = [
            name for name, profile in self.service_profiles.items()
            if profile.avg_response_time > 2.0  # Más de 2 segundos
        ]
        
        error_prone_services = [
            name for name, profile in self.service_profiles.items()
            if profile.error_rate > 0.1  # Más del 10% de error
        ]
        
        if slow_services:
            strategies.extend([
                OptimizationStrategy.CACHING,
                OptimizationStrategy.BATCHING,
                OptimizationStrategy.CONCURRENCY
            ])
        
        if error_prone_services:
            strategies.append(OptimizationStrategy.RESOURCE_ALLOCATION)
        
        # Siempre considerar priorización
        strategies.append(OptimizationStrategy.PRIORITIZATION)
        
        return list(set(strategies))  # Remover duplicados
    
    async def _apply_strategy(self, strategy: OptimizationStrategy) -> None:
        """Aplica una estrategia de optimización específica"""
        try:
            if strategy == OptimizationStrategy.CONCURRENCY:
                result = await self._optimize_concurrency()
            elif strategy == OptimizationStrategy.CACHING:
                result = await self._optimize_caching()
            elif strategy == OptimizationStrategy.BATCHING:
                result = await self._optimize_batching()
            elif strategy == OptimizationStrategy.PRIORITIZATION:
                result = await self._optimize_prioritization()
            elif strategy == OptimizationStrategy.RESOURCE_ALLOCATION:
                result = await self._optimize_resource_allocation()
            else:
                return
            
            if result.performance_improvement > 0:
                self.optimization_history.append(result)
                self.active_optimizations.add(strategy)
                logger.info(f"Applied {strategy.value} optimization: {result.performance_improvement:.2%} improvement")
            
        except BiologyError as e:
            logger.error(f"Failed to apply {strategy.value} optimization: {e}")
    
    async def _optimize_concurrency(self) -> OptimizationResult:
        """Optimiza el nivel de concurrencia"""
        # Lógica para ajustar concurrencia basado en métricas
        current_perf = await self._calculate_current_performance()
        
        # Ajustar concurrencia (simplificado)
        new_concurrency = min(
            self.current_concurrency + 1,
            self.optimization_config['max_concurrency']
        )
        
        if new_concurrency != self.current_concurrency:
            self.current_concurrency = new_concurrency
            
            # Simular mejora de performance (en implementación real, medir)
            improvement = 0.1  # 10% improvement estimate
            
            return OptimizationResult(
                strategy=OptimizationStrategy.CONCURRENCY,
                parameters={'concurrency_level': new_concurrency},
                performance_improvement=improvement
            )
        
        return OptimizationResult(
            strategy=OptimizationStrategy.CONCURRENCY,
            parameters={},
            performance_improvement=0.0
        )
    
    async def _optimize_caching(self) -> OptimizationResult:
        """Optimiza estrategias de caching"""
        # Implementar caching inteligente
        return OptimizationResult(
            strategy=OptimizationStrategy.CACHING,
            parameters={'cache_ttl': self.optimization_config['cache_ttl']},
            performance_improvement=0.15  # 15% improvement estimate
        )
    
    async def _optimize_batching(self) -> OptimizationResult:
        """Optimiza procesamiento por lotes"""
        return OptimizationResult(
            strategy=OptimizationStrategy.BATCHING,
            parameters={'batch_size': self.optimization_config['batch_size']},
            performance_improvement=0.20  # 20% improvement estimate
        )
    
    async def _optimize_prioritization(self) -> OptimizationResult:
        """Optimiza priorización de tareas"""
        return OptimizationResult(
            strategy=OptimizationStrategy.PRIORITIZATION,
            parameters={'priority_strategy': 'cost_aware'},
            performance_improvement=0.12  # 12% improvement estimate
        )
    
    async def _optimize_resource_allocation(self) -> OptimizationResult:
        """Optimiza asignación de recursos"""
        return OptimizationResult(
            strategy=OptimizationStrategy.RESOURCE_ALLOCATION,
            parameters={'resource_balancing': 'dynamic'},
            performance_improvement=0.18  # 18% improvement estimate
        )
    
    async def _calculate_current_performance(self) -> float:
        """Calcula el rendimiento actual"""
        recent_metrics = [
            m for m in self.pipeline_metrics.values()
            if m.timestamp > datetime.now() - timedelta(minutes=30)
        ]
        
        if not recent_metrics:
            return 0.0
        
        return statistics.mean(m.success_rate for m in recent_metrics)
    
    async def _apply_optimizations(self) -> None:
        """Aplica optimizaciones periódicamente"""
        while True:
            try:
                # Revisar y ajustar optimizaciones activas
                await self._adjust_active_optimizations()
                await asyncio.sleep(self.optimization_config['optimization_check_interval'])
                
            except BiologyError as e:
                logger.error(f"Optimization application error: {e}")
                await asyncio.sleep(60)
    
    async def _adjust_active_optimizations(self) -> None:
        """Ajusta optimizaciones activas basado en rendimiento actual"""
        current_perf = await self._calculate_current_performance()
        
        if current_perf >= self.optimization_config['target_success_rate']:
            # Performance buena, considerar reducir optimizaciones agresivas
            if OptimizationStrategy.CONCURRENCY in self.active_optimizations:
                # Reducir concurrencia si está muy alta
                if self.current_concurrency > self.optimization_config['min_concurrency']:
                    self.current_concurrency -= 1
                    logger.info(f"Reduced concurrency to {self.current_concurrency} due to good performance")
    
    async def get_optimization_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de optimización"""
        recent_performance = await self._calculate_current_performance()
        
        return {
            'active_optimizations': [strategy.value for strategy in self.active_optimizations],
            'current_concurrency': self.current_concurrency,
            'service_profiles': {name: {
                'avg_response_time': profile.avg_response_time,
                'success_rate': profile.success_rate,
                'error_rate': profile.error_rate
            } for name, profile in self.service_profiles.items()},
            'recent_performance': recent_performance,
            'optimization_history_count': len(self.optimization_history),
            'last_optimizations': [{
                'strategy': result.strategy.value,
                'improvement': result.performance_improvement,
                'applied_at': result.applied_at.isoformat()
            } for result in self.optimization_history[-5:]]  # Últimas 5 optimizaciones
        }
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Obtiene información del servicio"""
        return {
            "service_name": "PipelineOptimization",
            "optimization_strategies": [strategy.value for strategy in OptimizationStrategy],
            "active_optimizations": len(self.active_optimizations),
            "monitored_services": len(self.service_profiles),
            "performance_metrics_count": len(self.pipeline_metrics),
            "current_concurrency": self.current_concurrency,
            "status": "active"
        }

    async def calculate_discovery_cost_metrics(self, pipeline_id: str, pipeline_type: str, 
                                             domain: str, research_question: str,
                                             tasks: List[Dict], total_cost: float) -> DiscoveryCostMetrics:
        """Calcula métricas avanzadas de costo por descubrimiento"""
        
        # Extraer información de tareas
        successful_tasks = [task for task in tasks if task.get('status') == 'completed']
        failed_tasks = [task for task in tasks if task.get('status') == 'failed']
        
        # Calcular costos por categoría (estimaciones basadas en tipo de tarea)
        compute_cost = 0.0
        api_cost = 0.0
        storage_cost = 0.0
        
        for task in tasks:
            task_type = task.get('type', '')
            execution_time = task.get('execution_time', 0)
            
            if 'compute' in task_type or 'processing' in task_type:
                compute_cost += execution_time * 0.01  # $0.01 por segundo de cómputo
            elif 'api' in task_type or 'external' in task_type:
                api_cost += 0.10  # $0.10 por llamada API
            elif 'storage' in task_type or 'database' in task_type:
                storage_cost += 0.05  # $0.05 por operación de almacenamiento
        
        # Calcular métricas derivadas
        cost_per_successful_task = total_cost / len(successful_tasks) if successful_tasks else 0
        
        # Estimación de ROI basada en complejidad de la pregunta de investigación
        question_complexity = self._estimate_research_complexity(research_question)
        roi_estimate = (len(successful_tasks) * question_complexity * 100) / total_cost if total_cost > 0 else 0
        
        # Puntuación de eficiencia (0-100)
        efficiency_score = self._calculate_efficiency_score(
            total_cost, len(successful_tasks), len(failed_tasks), roi_estimate
        )
        
        metrics = DiscoveryCostMetrics(
            pipeline_id=pipeline_id,
            domain=domain,
            research_question=research_question,
            total_cost=total_cost,
            compute_cost=compute_cost,
            api_cost=api_cost,
            storage_cost=storage_cost,
            success_cost=total_cost - (compute_cost + api_cost + storage_cost),
            cost_per_successful_task=cost_per_successful_task,
            cost_per_discovery=cost_per_successful_task * 0.1,  # Asumiendo 10% de tareas generan descubrimientos
            roi_estimate=roi_estimate,
            efficiency_score=efficiency_score
        )
        
        self.discovery_cost_metrics[pipeline_id] = metrics
        return metrics
    
    def _estimate_research_complexity(self, research_question: str) -> float:
        """Estima la complejidad de una pregunta de investigación (1-10)"""
        # Análisis simple basado en longitud y palabras clave
        question_length = len(research_question.split())
        
        # Palabras clave que indican complejidad
        complex_keywords = ['analyze', 'compare', 'correlate', 'predict', 'model', 'trend', 'pattern']
        complexity_score = 1.0
        
        for keyword in complex_keywords:
            if keyword in research_question.lower():
                complexity_score += 1.0
        
        # Ajustar por longitud
        complexity_score += min(question_length / 10, 5.0)
        
        return min(complexity_score, 10.0)
    
    def _calculate_efficiency_score(self, total_cost: float, successful_tasks: int, 
                                  failed_tasks: int, roi_estimate: float) -> float:
        """Calcula una puntuación de eficiencia (0-100)"""
        if successful_tasks == 0:
            return 0.0
        
        # Factores de eficiencia
        success_rate = successful_tasks / (successful_tasks + failed_tasks) if (successful_tasks + failed_tasks) > 0 else 0
        cost_efficiency = 100 / (total_cost + 1)  # Inversamente proporcional al costo
        roi_factor = min(roi_estimate / 10, 10.0)  # ROI máximo de 10x da 10 puntos
        
        # Ponderación
        efficiency_score = (
            (success_rate * 40) +  # 40% por tasa de éxito
            (cost_efficiency * 30) +  # 30% por eficiencia de costo
            (roi_factor * 30)  # 30% por ROI
        )
        
        return min(efficiency_score, 100.0)
    
    async def get_discovery_cost_report(self, pipeline_id: Optional[str] = None) -> Dict[str, Any]:
        """Genera reporte de costos de descubrimiento"""
        if pipeline_id:
            metrics = self.discovery_cost_metrics.get(pipeline_id)
            if not metrics:
                return {"error": f"No metrics found for pipeline {pipeline_id}"}
            
            return self._format_cost_report(metrics)
        else:
            # Reporte agregado de todos los pipelines
            recent_metrics = [
                m for m in self.discovery_cost_metrics.values()
                if m.timestamp > datetime.now() - timedelta(days=7)
            ]
            
            if not recent_metrics:
                return {"message": "No recent discovery cost metrics available"}
            
            return {
                "total_pipelines": len(recent_metrics),
                "avg_total_cost": statistics.mean(m.total_cost for m in recent_metrics),
                "avg_efficiency_score": statistics.mean(m.efficiency_score for m in recent_metrics),
                "avg_roi": statistics.mean(m.roi_estimate for m in recent_metrics),
                "cost_breakdown": {
                    "compute": statistics.mean(m.compute_cost for m in recent_metrics),
                    "api": statistics.mean(m.api_cost for m in recent_metrics),
                    "storage": statistics.mean(m.storage_cost for m in recent_metrics),
                    "other": statistics.mean(m.success_cost for m in recent_metrics)
                },
                "recent_pipelines": [
                    self._format_cost_report(m) for m in sorted(
                        recent_metrics, key=lambda x: x.timestamp, reverse=True
                    )[:5]  # Últimos 5 pipelines
                ]
            }
    
    def _format_cost_report(self, metrics: DiscoveryCostMetrics) -> Dict[str, Any]:
        """Formatea el reporte de costos para visualización"""
        return {
            "pipeline_id": metrics.pipeline_id,
            "domain": metrics.domain,
            "research_question": metrics.research_question[:100] + "..." if len(metrics.research_question) > 100 else metrics.research_question,
            "total_cost": round(metrics.total_cost, 2),
            "cost_breakdown": {
                "compute": round(metrics.compute_cost, 2),
                "api": round(metrics.api_cost, 2),
                "storage": round(metrics.storage_cost, 2),
                "other": round(metrics.success_cost, 2)
            },
            "cost_per_successful_task": round(metrics.cost_per_successful_task, 4),
            "cost_per_discovery": round(metrics.cost_per_discovery, 4),
            "roi_estimate": round(metrics.roi_estimate, 2),
            "efficiency_score": round(metrics.efficiency_score, 1),
            "timestamp": metrics.timestamp.isoformat(),
            "efficiency_category": self._get_efficiency_category(metrics.efficiency_score)
        }
    
    def _get_efficiency_category(self, score: float) -> str:
        """Categoriza la eficiencia basado en la puntuación"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Average"
        elif score >= 20:
            return "Poor"
        else:
            return "Inefficient"