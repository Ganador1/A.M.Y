"""
Cost Metrics Service for AXIOM
Implementa tracking y análisis de costos por descubrimiento científico

Ethics & Safety:
- Transparencia total en el uso de recursos computacionales.
- Optimización automática para minimizar costos sin comprometer calidad.
- Alertas proactivas para prevenir gastos excesivos.
- Auditoría completa de todos los costos incurridos.

Ver ETHICS_AND_SAFETY.md para detalles y checklist.
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from collections import defaultdict, deque
import statistics

from app.services.base_service import BaseService
from app.exceptions.infrastructure.database import DatabaseError
from app.types.cost_metrics_service_types import (
    GetServiceInfoResult,
    GetBudgetStatusResult,
    HealthCheckResult,
)

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Tipos de recursos"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    API_CALLS = "api_calls"
    ML_INFERENCE = "ml_inference"
    DATABASE = "database"
    MEMORY = "memory"


class CostCategory(Enum):
    """Categorías de costo"""
    RESEARCH = "research"
    DISCOVERY = "discovery"
    ANALYSIS = "analysis"
    STORAGE = "storage"
    COMMUNICATION = "communication"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class ResourceUsage:
    """Uso de recursos"""
    resource_type: ResourceType
    amount: float
    unit: str
    cost_per_unit: float
    total_cost: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostEntry:
    """Entrada de costo"""
    id: str
    discovery_id: Optional[str]
    category: CostCategory
    resource_usage: List[ResourceUsage]
    total_cost: float
    start_time: datetime
    end_time: Optional[datetime]
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostBudget:
    """Presupuesto de costos"""
    name: str
    total_budget: float
    spent: float = 0.0
    remaining: float = 0.0
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    categories: Dict[CostCategory, float] = field(default_factory=dict)
    alerts_enabled: bool = True
    alert_thresholds: List[float] = field(default_factory=lambda: [0.5, 0.8, 0.95])


class CostMetricsService(BaseService):
    """
    Servicio de Métricas de Costo para AXIOM
    Rastrea, analiza y optimiza costos de descubrimientos científicos
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("CostMetrics")
        self.config = config or {}
        
        # Cost tracking
        self.cost_entries: List[CostEntry] = []
        self.active_sessions: Dict[str, CostEntry] = {}
        
        # Budgets
        self.budgets: Dict[str, CostBudget] = {}
        
        # Resource pricing (configurable)
        self.resource_pricing = {
            ResourceType.COMPUTE: {
                'cpu_hour': 0.10,
                'gpu_hour': 2.50,
                'tpu_hour': 8.00
            },
            ResourceType.STORAGE: {
                'gb_month': 0.023,
                'gb_transfer': 0.09
            },
            ResourceType.API_CALLS: {
                'openai_gpt4': 0.03,
                'openai_gpt3': 0.002,
                'anthropic_claude': 0.008,
                'google_palm': 0.001
            },
            ResourceType.ML_INFERENCE: {
                'small_model': 0.001,
                'medium_model': 0.01,
                'large_model': 0.1
            },
            ResourceType.DATABASE: {
                'query': 0.0001,
                'storage_gb': 0.10
            },
            ResourceType.MEMORY: {
                'gb_hour': 0.01
            },
            ResourceType.NETWORK: {
                'gb_transfer': 0.05
            }
        }
        
        # Cost optimization rules
        self.optimization_rules = {
            'auto_scale_down': True,
            'cache_expensive_operations': True,
            'batch_api_calls': True,
            'use_spot_instances': True,
            'compress_storage': True
        }
        
        # Metrics aggregation
        self.metrics_window = deque(maxlen=1000)  # Last 1000 operations
        self.hourly_costs = defaultdict(float)
        self.daily_costs = defaultdict(float)
        self.monthly_costs = defaultdict(float)
        
        # Alerts
        self.alert_callbacks: List[callable] = []
        
        # Lock for thread safety
        self.lock = threading.RLock()
        
        # Start background tasks
        asyncio.create_task(self._aggregate_metrics())
        asyncio.create_task(self._monitor_budgets())
    
    def get_service_info(self) -> GetServiceInfoResult:
        """Get information about cost metrics service"""
        return {
            "total_cost_entries": len(self.cost_entries),
            "active_sessions": len(self.active_sessions),
            "budgets_configured": len(self.budgets),
            "resource_types_tracked": [rt.value for rt in ResourceType],
            "cost_categories": [cc.value for cc in CostCategory],
            "optimization_rules": self.optimization_rules,
            "features": [
                "Real-time cost tracking",
                "Budget management",
                "Cost optimization",
                "Resource usage analytics",
                "Predictive cost modeling",
                "Automated alerts",
                "Multi-dimensional analysis"
            ]
        }
    
    def start_cost_session(self,
                          session_id: str,
                          discovery_id: Optional[str] = None,
                          category: CostCategory = CostCategory.RESEARCH,
                          tags: List[str] = None,
                          metadata: Dict[str, Any] = None) -> str:
        """
        Iniciar sesión de tracking de costos
        """
        
        with self.lock:
            if session_id in self.active_sessions:
                logger.warning(f"Cost session {session_id} already active")
                return session_id
            
            cost_entry = CostEntry(
                id=session_id,
                discovery_id=discovery_id,
                category=category,
                resource_usage=[],
                total_cost=0.0,
                start_time=datetime.now(),
                end_time=None,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            self.active_sessions[session_id] = cost_entry
            logger.info(f"Started cost session {session_id} for category {category.value}")
            
            return session_id
    
    def record_resource_usage(self,
                            session_id: str,
                            resource_type: ResourceType,
                            amount: float,
                            unit: str,
                            metadata: Dict[str, Any] = None) -> float:
        """
        Registrar uso de recursos
        """
        
        with self.lock:
            if session_id not in self.active_sessions:
                logger.error(f"Cost session {session_id} not found")
                return 0.0
            
            # Calculate cost
            cost_per_unit = self._get_resource_cost(resource_type, unit)
            total_cost = amount * cost_per_unit
            
            # Create resource usage entry
            usage = ResourceUsage(
                resource_type=resource_type,
                amount=amount,
                unit=unit,
                cost_per_unit=cost_per_unit,
                total_cost=total_cost,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            # Add to session
            cost_entry = self.active_sessions[session_id]
            cost_entry.resource_usage.append(usage)
            cost_entry.total_cost += total_cost
            
            # Update metrics
            self._update_metrics(cost_entry.category, total_cost)
            
            # Check budget alerts
            self._check_budget_alerts(cost_entry.category, total_cost)
            
            logger.debug(f"Recorded {amount} {unit} of {resource_type.value} "
                        f"for session {session_id}, cost: ${total_cost:.4f}")
            
            return total_cost
    
    def end_cost_session(self, session_id: str) -> Optional[CostEntry]:
        """
        Finalizar sesión de tracking de costos
        """
        
        with self.lock:
            if session_id not in self.active_sessions:
                logger.error(f"Cost session {session_id} not found")
                return None
            
            cost_entry = self.active_sessions.pop(session_id)
            cost_entry.end_time = datetime.now()
            
            # Store completed entry
            self.cost_entries.append(cost_entry)
            
            # Log summary
            duration = (cost_entry.end_time - cost_entry.start_time).total_seconds()
            logger.info(f"Ended cost session {session_id}: "
                       f"${cost_entry.total_cost:.4f} over {duration:.1f}s")
            
            # Trigger optimization suggestions
            self._suggest_optimizations(cost_entry)
            
            return cost_entry
    
    def _get_resource_cost(self, resource_type: ResourceType, unit: str) -> float:
        """Obtener costo por unidad de recurso"""
        
        pricing = self.resource_pricing.get(resource_type, {})
        return pricing.get(unit, 0.0)
    
    def _update_metrics(self, category: CostCategory, cost: float):
        """Actualizar métricas agregadas"""
        
        now = datetime.now()
        hour_key = now.strftime("%Y-%m-%d-%H")
        day_key = now.strftime("%Y-%m-%d")
        month_key = now.strftime("%Y-%m")
        
        self.hourly_costs[hour_key] += cost
        self.daily_costs[day_key] += cost
        self.monthly_costs[month_key] += cost
        
        # Add to metrics window
        self.metrics_window.append({
            'timestamp': now,
            'category': category,
            'cost': cost
        })
    
    def create_budget(self,
                     name: str,
                     total_budget: float,
                     period_days: int = 30,
                     categories: Dict[CostCategory, float] = None,
                     alert_thresholds: List[float] = None) -> CostBudget:
        """
        Crear presupuesto de costos
        """
        
        budget = CostBudget(
            name=name,
            total_budget=total_budget,
            period_start=datetime.now(),
            period_end=datetime.now() + timedelta(days=period_days),
            categories=categories or {},
            alert_thresholds=alert_thresholds or [0.5, 0.8, 0.95]
        )
        
        budget.remaining = total_budget
        
        self.budgets[name] = budget
        logger.info(f"Created budget {name}: ${total_budget} for {period_days} days")
        
        return budget
    
    def _check_budget_alerts(self, category: CostCategory, cost: float):
        """Verificar alertas de presupuesto"""
        
        for budget_name, budget in self.budgets.items():
            if not budget.alerts_enabled:
                continue
            
            # Update budget spent
            budget.spent += cost
            budget.remaining = budget.total_budget - budget.spent
            
            # Check category budget if specified
            if category in budget.categories:
                category_spent = sum(
                    entry.total_cost for entry in self.cost_entries
                    if entry.category == category and
                    entry.start_time >= budget.period_start
                )
                
                category_budget = budget.categories[category]
                category_usage = category_spent / category_budget
                
                if category_usage >= 0.9:
                    self._trigger_budget_alert(
                        f"Category {category.value} budget 90% used",
                        budget_name, category_usage
                    )
            
            # Check total budget
            usage_percentage = budget.spent / budget.total_budget
            
            for threshold in budget.alert_thresholds:
                if usage_percentage >= threshold and usage_percentage < threshold + 0.05:
                    self._trigger_budget_alert(
                        f"Budget {budget_name} {threshold*100}% used",
                        budget_name, usage_percentage
                    )
    
    def _trigger_budget_alert(self, message: str, budget_name: str, usage: float):
        """Disparar alerta de presupuesto"""
        
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'budget_name': budget_name,
            'usage_percentage': usage,
            'severity': 'high' if usage >= 0.9 else 'medium'
        }
        
        logger.warning(f"BUDGET ALERT: {message}")
        
        # Call registered alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except DatabaseError as e:
                logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: callable):
        """Agregar callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def get_cost_analysis(self,
                         discovery_id: Optional[str] = None,
                         category: Optional[CostCategory] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Obtener análisis de costos
        """
        
        # Filter entries
        filtered_entries = self.cost_entries.copy()
        
        if discovery_id:
            filtered_entries = [e for e in filtered_entries if e.discovery_id == discovery_id]
        
        if category:
            filtered_entries = [e for e in filtered_entries if e.category == category]
        
        if start_date:
            filtered_entries = [e for e in filtered_entries if e.start_time >= start_date]
        
        if end_date:
            filtered_entries = [e for e in filtered_entries if e.start_time <= end_date]
        
        if not filtered_entries:
            return {'total_cost': 0.0, 'entries': 0, 'analysis': {}}
        
        # Calculate metrics
        total_cost = sum(entry.total_cost for entry in filtered_entries)
        avg_cost = total_cost / len(filtered_entries)
        
        costs = [entry.total_cost for entry in filtered_entries]
        median_cost = statistics.median(costs)
        
        # Cost by category
        cost_by_category = defaultdict(float)
        for entry in filtered_entries:
            cost_by_category[entry.category.value] += entry.total_cost
        
        # Cost by resource type
        cost_by_resource = defaultdict(float)
        for entry in filtered_entries:
            for usage in entry.resource_usage:
                cost_by_resource[usage.resource_type.value] += usage.total_cost
        
        # Time analysis
        durations = []
        for entry in filtered_entries:
            if entry.end_time:
                duration = (entry.end_time - entry.start_time).total_seconds()
                durations.append(duration)
        
        avg_duration = statistics.mean(durations) if durations else 0
        
        return {
            'total_cost': total_cost,
            'average_cost': avg_cost,
            'median_cost': median_cost,
            'entries_count': len(filtered_entries),
            'cost_by_category': dict(cost_by_category),
            'cost_by_resource': dict(cost_by_resource),
            'average_duration_seconds': avg_duration,
            'cost_per_second': total_cost / sum(durations) if durations else 0,
            'date_range': {
                'start': min(entry.start_time for entry in filtered_entries).isoformat(),
                'end': max(entry.end_time or entry.start_time for entry in filtered_entries).isoformat()
            }
        }
    
    def predict_costs(self,
                     discovery_type: str,
                     estimated_duration_hours: float,
                     resource_requirements: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Predecir costos para un descubrimiento
        """
        
        # Get historical data for similar discoveries
        similar_entries = [
            entry for entry in self.cost_entries
            if discovery_type.lower() in str(entry.metadata).lower()
        ]
        
        if similar_entries:
            # Use historical average
            avg_cost = sum(entry.total_cost for entry in similar_entries) / len(similar_entries)
            avg_duration = statistics.mean([
                (entry.end_time - entry.start_time).total_seconds() / 3600
                for entry in similar_entries if entry.end_time
            ])
            
            # Scale by duration
            predicted_cost = avg_cost * (estimated_duration_hours / avg_duration) if avg_duration > 0 else avg_cost
        else:
            # Use resource requirements
            predicted_cost = 0.0
            
            if resource_requirements:
                for resource, amount in resource_requirements.items():
                    # Find matching resource type and unit
                    for resource_type in ResourceType:
                        pricing = self.resource_pricing.get(resource_type, {})
                        if resource in pricing:
                            predicted_cost += amount * pricing[resource]
                            break
        
        # Add confidence interval
        confidence = len(similar_entries) / 10.0  # More data = higher confidence
        confidence = min(confidence, 1.0)
        
        margin = predicted_cost * (0.5 - 0.4 * confidence)  # 10-50% margin based on confidence
        
        return {
            'predicted_cost': predicted_cost,
            'confidence': confidence,
            'cost_range': {
                'min': max(0, predicted_cost - margin),
                'max': predicted_cost + margin
            },
            'based_on_entries': len(similar_entries),
            'estimated_duration_hours': estimated_duration_hours,
            'breakdown': resource_requirements or {}
        }
    
    def _suggest_optimizations(self, cost_entry: CostEntry):
        """Sugerir optimizaciones de costo"""
        
        suggestions = []
        
        # Analyze resource usage
        resource_costs = defaultdict(float)
        for usage in cost_entry.resource_usage:
            resource_costs[usage.resource_type] += usage.total_cost
        
        # High compute costs
        if resource_costs[ResourceType.COMPUTE] > cost_entry.total_cost * 0.5:
            suggestions.append({
                'type': 'compute_optimization',
                'message': 'Consider using spot instances or auto-scaling',
                'potential_savings': resource_costs[ResourceType.COMPUTE] * 0.3
            })
        
        # High API costs
        if resource_costs[ResourceType.API_CALLS] > cost_entry.total_cost * 0.3:
            suggestions.append({
                'type': 'api_optimization',
                'message': 'Consider caching API responses or batching calls',
                'potential_savings': resource_costs[ResourceType.API_CALLS] * 0.2
            })
        
        # High storage costs
        if resource_costs[ResourceType.STORAGE] > cost_entry.total_cost * 0.2:
            suggestions.append({
                'type': 'storage_optimization',
                'message': 'Consider data compression or archival policies',
                'potential_savings': resource_costs[ResourceType.STORAGE] * 0.4
            })
        
        if suggestions:
            logger.info(f"Cost optimization suggestions for {cost_entry.id}: {len(suggestions)} found")
            cost_entry.metadata['optimization_suggestions'] = suggestions
    
    async def _aggregate_metrics(self):
        """Agregar métricas periódicamente"""
        while True:
            try:
                # Clean old metrics
                cutoff = datetime.now() - timedelta(days=7)
                
                # Clean hourly costs older than 7 days
                old_hours = [k for k in self.hourly_costs.keys() 
                           if datetime.strptime(k, "%Y-%m-%d-%H") < cutoff]
                for hour in old_hours:
                    del self.hourly_costs[hour]
                
                await asyncio.sleep(3600)  # Run every hour
            
            except DatabaseError as e:
                logger.error(f"Metrics aggregation error: {e}")
                await asyncio.sleep(3600)
    
    async def _monitor_budgets(self):
        """Monitorear presupuestos periódicamente"""
        while True:
            try:
                now = datetime.now()
                
                for budget_name, budget in self.budgets.items():
                    # Check if budget period expired
                    if budget.period_end and now > budget.period_end:
                        logger.info(f"Budget {budget_name} period expired, resetting")
                        budget.spent = 0.0
                        budget.remaining = budget.total_budget
                        budget.period_start = now
                        budget.period_end = now + timedelta(days=30)  # Default 30 days
                
                await asyncio.sleep(3600)  # Check every hour
            
            except DatabaseError as e:
                logger.error(f"Budget monitoring error: {e}")
                await asyncio.sleep(3600)
    
    def get_budget_status(self, budget_name: Optional[str] = None) -> GetBudgetStatusResult:
        """Obtener estado de presupuestos"""
        
        if budget_name:
            budget = self.budgets.get(budget_name)
            if not budget:
                return {'error': f'Budget {budget_name} not found'}
            
            return {
                'name': budget.name,
                'total_budget': budget.total_budget,
                'spent': budget.spent,
                'remaining': budget.remaining,
                'usage_percentage': budget.spent / budget.total_budget,
                'period_start': budget.period_start.isoformat(),
                'period_end': budget.period_end.isoformat() if budget.period_end else None,
                'categories': {k.value: v for k, v in budget.categories.items()},
                'alerts_enabled': budget.alerts_enabled
            }
        else:
            return {
                'budgets': {
                    name: {
                        'total_budget': budget.total_budget,
                        'spent': budget.spent,
                        'remaining': budget.remaining,
                        'usage_percentage': budget.spent / budget.total_budget
                    }
                    for name, budget in self.budgets.items()
                },
                'total_budgets': len(self.budgets)
            }
    
    def export_cost_data(self,
                        format: str = 'json',
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> str:
        """
        Exportar datos de costo
        """
        
        # Filter entries
        entries = self.cost_entries.copy()
        
        if start_date:
            entries = [e for e in entries if e.start_time >= start_date]
        
        if end_date:
            entries = [e for e in entries if e.start_time <= end_date]
        
        # Convert to serializable format
        export_data = []
        for entry in entries:
            export_entry = {
                'id': entry.id,
                'discovery_id': entry.discovery_id,
                'category': entry.category.value,
                'total_cost': entry.total_cost,
                'start_time': entry.start_time.isoformat(),
                'end_time': entry.end_time.isoformat() if entry.end_time else None,
                'tags': entry.tags,
                'metadata': entry.metadata,
                'resource_usage': [
                    {
                        'resource_type': usage.resource_type.value,
                        'amount': usage.amount,
                        'unit': usage.unit,
                        'cost_per_unit': usage.cost_per_unit,
                        'total_cost': usage.total_cost,
                        'timestamp': usage.timestamp.isoformat(),
                        'metadata': usage.metadata
                    }
                    for usage in entry.resource_usage
                ]
            }
            export_data.append(export_entry)
        
        if format.lower() == 'json':
            return json.dumps(export_data, indent=2)
        else:
            # Could add CSV, Excel formats here
            return json.dumps(export_data, indent=2)
    
    async def health_check(self) -> HealthCheckResult:
        """Realizar health check del servicio"""
        
        return {
            'status': 'healthy',
            'active_sessions': len(self.active_sessions),
            'total_entries': len(self.cost_entries),
            'budgets_configured': len(self.budgets),
            'metrics_window_size': len(self.metrics_window),
            'last_24h_cost': sum(
                entry.total_cost for entry in self.cost_entries
                if entry.start_time >= datetime.now() - timedelta(days=1)
            ),
            'timestamp': datetime.now().isoformat()
        }