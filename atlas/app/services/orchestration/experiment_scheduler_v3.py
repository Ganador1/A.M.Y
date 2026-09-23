"""Experiment Scheduler V3 (consolidado y mejorado)

Objetivos:
 - Consolidar versiones previas (v1/v2) eliminando duplicación
 - Añadir heurística de impacto científico para priorización
 - Añadir backoff exponencial con jitter configurable
 - Métricas y trazabilidad (trace_id + decision events)
 - Mantener compatibilidad con el modelo ORM existente

Diseño simplificado: Evita acceder a columnas SQLAlchemy en memoria como si fueran Column objects.
Se traen instancias y se manipulan valores Python puros.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from uuid import uuid4

from sqlalchemy import update, and_

from app.core.database import get_db_session
from app.models.experiment_scheduler_models import ExperimentJobRecord, ExperimentJobState
from app.services.base_service import BaseService
from app.processing.async_processor import AdvancedAsyncProcessor
from app.core.bootstrap_logging import logger, log_decision_event
from app.middleware.trace_id_middleware import get_current_trace_id
from app.monitoring.metrics import inc, observe
from app.exceptions.domain.biology import BiologyError
from app.types.experiment_scheduler_v3_types import (
    ParsePayloadResult,
    GetSchedulerMetricsResult,
    ProcessRequestResult,
)


class ImpactPriority(int, Enum):
    """Niveles de prioridad (1=alta)."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class RetryStrategy(Enum):
    """Retry strategy options"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    NO_RETRY = "no_retry"


class SchedulingStrategy(Enum):
    """Job scheduling strategies"""
    PRIORITY_FIRST = "priority_first"          # Highest priority first
    IMPACT_WEIGHTED = "impact_weighted"        # Priority * impact score
    ROUND_ROBIN = "round_robin"               # Fair scheduling
    ADAPTIVE = "adaptive"                     # Dynamic based on performance


class ExperimentSchedulerV3(BaseService):
    """Scheduler consolidado con priorización por impacto científico y backoff."""

    def __init__(self, async_processor: Optional[AdvancedAsyncProcessor] = None):
        super().__init__("ExperimentSchedulerV3")
        self.async_processor = async_processor or AdvancedAsyncProcessor()
        self.max_concurrent_jobs = 10
        self.polling_interval = 5.0
        self.max_retry_attempts = 5
        self.base_retry_delay = 2.0  # segundos
        self.max_retry_delay = 600.0  # 10 minutos
        self.impact_weights = {
            "novelty": 0.3,
            "evidence_strength": 0.25,
            "potential_citations": 0.2,
            "interdisciplinary_score": 0.15,
            "reproducibility": 0.1,
        }
        self._execution_stats: Dict[str, List[float]] = {}
        self._failure_rates: Dict[str, List[bool]] = {}
        self._job_queue_metrics = {
            "total_submitted": 0,
            "total_completed": 0,
            "total_failed": 0,
        }
        self._scheduler_task: Optional[asyncio.Task] = None
        self._running = False
        self._job_handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self.scheduling_strategy = SchedulingStrategy.IMPACT_WEIGHTED
        self.retry_strategy = RetryStrategy.EXPONENTIAL_BACKOFF
        logger.info("ExperimentSchedulerV3 inicializado")
    
    def register_job_handler(self, job_type: str, handler: Callable) -> None:
        """Register a handler function for specific job types"""
        self._job_handlers[job_type] = handler
        logger.info(f"📋 Registered job handler for type: {job_type}")
    
    def calculate_scientific_impact(self, job_data: Dict[str, Any]) -> float:
        """
        Calculate scientific impact score using heuristic analysis.
        
        Args:
            job_data: Job payload containing research metadata
            
        Returns:
            Impact score between 0.0 and 1.0
        """
        try:
            # Extract impact factors from job data
            novelty = self._assess_novelty(job_data)
            evidence_strength = self._assess_evidence_strength(job_data)
            citation_potential = self._assess_citation_potential(job_data)
            interdisciplinary = self._assess_interdisciplinary_score(job_data)
            reproducibility = self._assess_reproducibility(job_data)
            
            # Calculate weighted impact score
            impact_score = (
                novelty * self.impact_weights["novelty"] +
                evidence_strength * self.impact_weights["evidence_strength"] +
                citation_potential * self.impact_weights["potential_citations"] +
                interdisciplinary * self.impact_weights["interdisciplinary_score"] +
                reproducibility * self.impact_weights["reproducibility"]
            )
            
            return min(1.0, max(0.0, impact_score))
        
        except BiologyError as e:
            logger.warning(f"Failed to calculate impact score: {e}")
            return 0.5  # Default moderate impact
    
    def _assess_novelty(self, job_data: Dict[str, Any]) -> float:
        """Assess novelty of research approach"""
        novelty_indicators = job_data.get("novelty_indicators", {})
        
        # Check for novel methods, datasets, or approaches
        novel_methods = len(novelty_indicators.get("new_methods", []))
        novel_datasets = len(novelty_indicators.get("new_datasets", []))
        novel_domains = len(novelty_indicators.get("cross_domain_elements", []))
        
        # Heuristic: more novel elements = higher novelty
        novelty_score = min(1.0, (novel_methods * 0.4 + novel_datasets * 0.3 + novel_domains * 0.3) / 3)
        
        return novelty_score
    
    def _assess_evidence_strength(self, job_data: Dict[str, Any]) -> float:
        """Assess strength of supporting evidence"""
        evidence = job_data.get("evidence_base", {})
        
        paper_count = len(evidence.get("supporting_papers", []))
        data_quality = evidence.get("data_quality_score", 0.5)
        statistical_power = evidence.get("statistical_power", 0.5)
        
        # Combine evidence factors
        evidence_score = (paper_count / 50.0 * 0.3 +  # Normalize to ~50 papers max
                         data_quality * 0.4 +
                         statistical_power * 0.3)
        
        return min(1.0, evidence_score)
    
    def _assess_citation_potential(self, job_data: Dict[str, Any]) -> float:
        """Assess potential for citations and impact"""
        metadata = job_data.get("research_metadata", {})
        
        domain_activity = metadata.get("domain_activity_score", 0.5)  # How active is this research area
        author_h_index = metadata.get("author_h_index", 0)
        journal_impact = metadata.get("target_journal_impact", 1.0)
        
        # Heuristic for citation potential
        citation_score = (domain_activity * 0.4 +
                         min(1.0, author_h_index / 20.0) * 0.3 +  # Normalize h-index
                         min(1.0, journal_impact / 10.0) * 0.3)   # Normalize impact factor
        
        return min(1.0, citation_score)
    
    def _assess_interdisciplinary_score(self, job_data: Dict[str, Any]) -> float:
        """Assess interdisciplinary nature of research"""
        domains = job_data.get("research_domains", [])
        collaborations = job_data.get("cross_domain_collaborations", [])
        
        # More domains and collaborations = higher interdisciplinary score
        interdisciplinary_score = (len(domains) / 5.0 * 0.6 +  # Normalize to ~5 domains
                                 len(collaborations) / 3.0 * 0.4)  # Normalize to ~3 collaborations
        
        return min(1.0, interdisciplinary_score)
    
    def _assess_reproducibility(self, job_data: Dict[str, Any]) -> float:
        """Assess reproducibility factors"""
        repro_factors = job_data.get("reproducibility", {})
        
        code_availability = 1.0 if repro_factors.get("code_available") else 0.0
        data_availability = 1.0 if repro_factors.get("data_available") else 0.0
        method_clarity = repro_factors.get("method_clarity_score", 0.5)
        
        reproducibility_score = (code_availability * 0.4 +
                               data_availability * 0.4 +
                               method_clarity * 0.2)
        
        return reproducibility_score
    
    def submit_job(
        self,
        name: str,
        job_type: str,
        payload: Dict[str, Any],
        run_at: Optional[datetime] = None,
        priority: Optional[ImpactPriority] = None,
        max_retries: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Submit a new experiment job with enhanced prioritization.
        
        Args:
            name: Descriptive job name
            job_type: Type of job for handler routing
            payload: Job data and parameters
            run_at: Scheduled execution time (None = immediate)
            priority: Optional explicit priority level
            max_retries: Max retry attempts (uses default if None)
            tags: Optional metadata tags
            
        Returns:
            Job UUID for tracking
        """
        trace_id = get_current_trace_id()
        job_uuid = str(uuid4())

        # Impact / priority derivation
        if priority is None:
            impact_score = self.calculate_scientific_impact(payload)
            priority = self._impact_score_to_priority(impact_score)
        else:
            impact_score = self._priority_to_impact_score(priority)

        session = get_db_session()
        try:
            enhanced_payload = payload.copy()
            enhanced_payload.update({
                "impact_score": impact_score,
                "job_type": job_type,
                "tags": tags or {},
                "trace_id": trace_id,
            })
            job = ExperimentJobRecord(
                job_uuid=job_uuid,
                name=name,
                payload_json=json.dumps(enhanced_payload),
                state=ExperimentJobState.PENDING.value,
                run_at=run_at or datetime.utcnow(),
                priority=int(priority.value),
                max_retries=max_retries or self.max_retry_attempts,
                retry_count=0,
            )
            session.add(job)
            session.commit()
            self._job_queue_metrics["total_submitted"] += 1
            inc("atlas_scheduler_jobs_submitted_total", labels={"job_type": job_type, "priority": priority.name})
            log_decision_event(
                event_type="job_submitted",
                phase="scheduling",
                details={
                    "job_uuid": job_uuid,
                    "job_type": job_type,
                    "priority": priority.name,
                    "impact_score": impact_score,
                },
                outcome="scheduled",
                trace_id=trace_id,
            )
            logger.info(f"Job {job_uuid} registrado (impact={impact_score:.3f}, priority={priority.name})")
            return job_uuid
        except BiologyError as e:
            session.rollback()
            logger.error(f"Error al registrar job: {e}")
            raise
        finally:
            session.close()
    
    def _impact_score_to_priority(self, impact_score: float) -> ImpactPriority:
        """Convert impact score to priority level"""
        if impact_score >= 0.9:
            return ImpactPriority.CRITICAL
        elif impact_score >= 0.7:
            return ImpactPriority.HIGH
        elif impact_score >= 0.5:
            return ImpactPriority.MEDIUM
        elif impact_score >= 0.3:
            return ImpactPriority.LOW
        else:
            return ImpactPriority.BACKGROUND
    
    def _priority_to_impact_score(self, priority: ImpactPriority) -> float:
        """Convert priority level to approximate impact score"""
        mapping = {
            ImpactPriority.CRITICAL: 0.95,
            ImpactPriority.HIGH: 0.8,
            ImpactPriority.MEDIUM: 0.6,
            ImpactPriority.LOW: 0.4,
            ImpactPriority.BACKGROUND: 0.2
        }
        return mapping.get(priority, 0.5)
    
    async def start_scheduler(self) -> None:
        """Start the background scheduler task (reconstruido limpio)."""
        if self._running:
            logger.warning("Scheduler already running")
            return
        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("🚀 Started experiment scheduler v3")
    
    async def stop_scheduler(self) -> None:
        """Stop the background scheduler task"""
        if not self._running:
            logger.warning("Scheduler not running")
            return
        
        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("⏹️ Stopped experiment scheduler v3")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop with enhanced job selection"""
        logger.info("🔄 Scheduler loop started")
        
        while self._running:
            try:
                # Get jobs ready for execution
                ready_jobs = self._get_ready_jobs()
                
                if ready_jobs:
                    # Sort jobs by scheduling strategy
                    sorted_jobs = self._sort_jobs_by_strategy(ready_jobs)
                    
                    # Execute jobs up to concurrent limit
                    for job in sorted_jobs[:self.max_concurrent_jobs]:
                        asyncio.create_task(self._execute_job(job))
                
                # Update queue metrics
                self._update_queue_metrics()
                
                # Wait for next polling cycle
                await asyncio.sleep(self.polling_interval)
                
            except BiologyError as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(self.polling_interval)
        
        logger.info("🏁 Scheduler loop ended")
    
    def _get_ready_jobs(self) -> List[ExperimentJobRecord]:
        session = get_db_session()
        try:
            now = datetime.utcnow()
            jobs = (
                session.query(ExperimentJobRecord)
                .filter(
                    and_(
                        ExperimentJobRecord.state == ExperimentJobState.PENDING.value,
                        ExperimentJobRecord.run_at <= now,
                        ExperimentJobRecord.retry_count < ExperimentJobRecord.max_retries,
                    )
                )
                .limit(50)
                .all()
            )
            return jobs
        finally:
            session.close()
    
    def _sort_jobs_by_strategy(self, jobs: List[ExperimentJobRecord]) -> List[ExperimentJobRecord]:
        if self.scheduling_strategy == SchedulingStrategy.PRIORITY_FIRST:
            return sorted(jobs, key=lambda j: int(getattr(j, "priority", 5)))
        if self.scheduling_strategy == SchedulingStrategy.IMPACT_WEIGHTED:
            def score(job: ExperimentJobRecord) -> float:
                payload = {}
                try:
                    payload = json.loads(getattr(job, "payload_json", "{}") or "{}")
                except BiologyError:
                    pass
                impact = float(payload.get("impact_score", 0.5))
                return int(getattr(job, "priority", 5)) * (1.0 - impact)
            return sorted(jobs, key=score)
        if self.scheduling_strategy == SchedulingStrategy.ROUND_ROBIN:
            buckets: Dict[str, List[ExperimentJobRecord]] = {}
            for job in jobs:
                payload = {}
                try:
                    payload = json.loads(getattr(job, "payload_json", "{}") or "{}")
                except BiologyError:
                    pass
                jt = str(payload.get("job_type", "default"))
                buckets.setdefault(jt, []).append(job)
            result: List[ExperimentJobRecord] = []
            max_len = max(len(v) for v in buckets.values()) if buckets else 0
            for i in range(max_len):
                for lst in buckets.values():
                    if i < len(lst):
                        result.append(lst[i])
            return result
        if self.scheduling_strategy == SchedulingStrategy.ADAPTIVE:
            return sorted(jobs, key=lambda j: -self._calculate_adaptive_score(j))
        return sorted(jobs, key=lambda j: int(getattr(j, "priority", 5)))
    
    def _parse_payload(self, job: ExperimentJobRecord) -> ParsePayloadResult:
        try:
            return json.loads(getattr(job, "payload_json", "{}") or "{}")
        except BiologyError:
            return {}

    def _calculate_adaptive_score(self, job: ExperimentJobRecord) -> float:
        payload = self._parse_payload(job)
        job_type = payload.get("job_type", "default")
        avg_execution_time = 0.0
        success_rate = 1.0
        if job_type in self._execution_stats and self._execution_stats[job_type]:
            avg_execution_time = sum(self._execution_stats[job_type]) / len(self._execution_stats[job_type])
        if job_type in self._failure_rates and self._failure_rates[job_type]:
            success_rate = sum(self._failure_rates[job_type]) / len(self._failure_rates[job_type])
        impact_score = float(payload.get("impact_score", 0.5))
        priority_val = int(getattr(job, "priority", 5))
        priority_factor = 6 - priority_val
        return (
            priority_factor * 0.4 +
            impact_score * 0.3 +
            success_rate * 0.2 +
            (1.0 / max(0.1, avg_execution_time)) * 0.1
        )
    
    async def _execute_job(self, job: ExperimentJobRecord) -> None:
        start_time = datetime.utcnow()
        payload = {}
        try:
            payload = json.loads(getattr(job, "payload_json", "{}") or "{}")
        except BiologyError:
            pass
        trace_id = payload.get("trace_id", "unknown")
        job_uuid = str(getattr(job, "job_uuid"))
        self._update_job_state(job_uuid, ExperimentJobState.RUNNING)
        log_decision_event(
            event_type="job_execution_started",
            phase="execution",
            details={
                "job_uuid": job.job_uuid,
                "priority": getattr(job, "priority", None),
                "retry_count": getattr(job, "retry_count", 0),
            },
            outcome="started",
            trace_id=trace_id,
        )

        try:
            job_type = payload.get("job_type", "default")
            handler = self._job_handlers.get(job_type)
            if handler:
                await handler(payload)
            else:
                await asyncio.sleep(0.05)  # trabajo simulado

            exec_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_job_state(job_uuid, ExperimentJobState.COMPLETED)
            self._record_execution_stats(job_type, exec_time, True)
            self._job_queue_metrics["total_completed"] += 1
            inc("atlas_scheduler_jobs_completed_total", labels={"job_type": job_type})
            observe("atlas_scheduler_job_duration_seconds", exec_time)
            log_decision_event(
                event_type="job_execution_completed",
                phase="execution",
                details={
                    "job_uuid": job.job_uuid,
                    "execution_time_sec": exec_time,
                },
                outcome="success",
                trace_id=trace_id,
            )
            logger.info(f"Job {job.job_uuid} completado en {exec_time:.3f}s")
        except BiologyError as e:
            exec_time = (datetime.utcnow() - start_time).total_seconds()
            self._record_execution_stats(payload.get("job_type", "default"), exec_time, False)
            retry_count = getattr(job, "retry_count", 0)
            max_retries = getattr(job, "max_retries", 0)
            if retry_count < max_retries:
                delay = self._calculate_retry_delay(retry_count)
                retry_time = datetime.utcnow() + timedelta(seconds=delay)
                self._update_job_for_retry(job_uuid, retry_time, str(e))
                logger.warning(f"Job {job.job_uuid} fallo intento {retry_count+1}, reintento en {delay:.1f}s: {e}")
            else:
                self._update_job_state(job_uuid, ExperimentJobState.FAILED, error=str(e))
                self._job_queue_metrics["total_failed"] += 1
                inc("atlas_scheduler_jobs_failed_total")
                logger.error(f"Job {job.job_uuid} fallo definitivo: {e}")
            log_decision_event(
                event_type="job_execution_failed",
                phase="execution",
                details={
                    "job_uuid": job.job_uuid,
                    "error": str(e),
                    "retry_count": retry_count,
                    "will_retry": retry_count < max_retries,
                },
                outcome="failed",
                trace_id=trace_id,
            )
    
    def _calculate_retry_delay(self, retry_count: int) -> float:
        """Calculate retry delay based on strategy"""
        if self.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            # Exponential backoff with jitter
            delay = min(
                self.max_retry_delay,
                self.base_retry_delay * (2 ** retry_count) + random.uniform(0, 1)
            )
        elif self.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = min(
                self.max_retry_delay,
                self.base_retry_delay * (retry_count + 1)
            )
        elif self.retry_strategy == RetryStrategy.FIXED_INTERVAL:
            delay = self.base_retry_delay
        else:  # NO_RETRY
            delay = 0
        
        return delay
    
    def _update_job_state(self, job_uuid: str, state: ExperimentJobState, error: Optional[str] = None) -> None:
        session = get_db_session()
        try:
            values: Dict[str, Any] = {"state": state.value}
            if state == ExperimentJobState.COMPLETED:
                values["completed_at"] = datetime.utcnow()
            if state == ExperimentJobState.FAILED:
                values["error_message"] = error or ""
            session.execute(
                update(ExperimentJobRecord)
                .where(ExperimentJobRecord.job_uuid == job_uuid)
                .values(**values)
            )
            session.commit()
        finally:
            session.close()
    
    def _update_job_for_retry(self, job_uuid: str, retry_time: datetime, error: str) -> None:
        session = get_db_session()
        try:
            session.execute(
                update(ExperimentJobRecord)
                .where(ExperimentJobRecord.job_uuid == job_uuid)
                .values(
                    state=ExperimentJobState.PENDING.value,
                    run_at=retry_time,
                    retry_count=ExperimentJobRecord.retry_count + 1,
                    error_message=error,
                )
            )
            session.commit()
        finally:
            session.close()
    
    def _record_execution_stats(self, job_type: str, execution_time: float, success: bool) -> None:
        """Record execution statistics for adaptive scheduling"""
        if job_type not in self._execution_stats:
            self._execution_stats[job_type] = []
            self._failure_rates[job_type] = []
        
        self._execution_stats[job_type].append(execution_time)
        self._failure_rates[job_type].append(success)
        
        # Keep only recent stats
        max_history = 100
        if len(self._execution_stats[job_type]) > max_history:
            self._execution_stats[job_type] = self._execution_stats[job_type][-max_history:]
            self._failure_rates[job_type] = self._failure_rates[job_type][-max_history:]
    
    def _update_queue_metrics(self) -> None:
        """Update queue performance metrics"""
        session = get_db_session()
        try:
            # Count jobs by state
            pending_count = session.query(ExperimentJobRecord).filter(
                ExperimentJobRecord.state == ExperimentJobState.PENDING.value
            ).count()

            running_count = session.query(ExperimentJobRecord).filter(
                ExperimentJobRecord.state == ExperimentJobState.RUNNING.value
            ).count()
            
            # Update Prometheus metrics
            observe("atlas_scheduler_queue_size", pending_count)
            observe("atlas_scheduler_running_jobs", running_count)
        
        finally:
            session.close()
    
    def get_job_status(self, job_uuid: str) -> Optional[Dict[str, Any]]:
        session = get_db_session()
        try:
            job = (
                session.query(ExperimentJobRecord)
                .filter(ExperimentJobRecord.job_uuid == job_uuid)
                .first()
            )
            if not job:
                return None
            try:
                payload = json.loads(getattr(job, "payload_json", "{}") or "{}")
            except BiologyError:
                payload = {}
            return {
                "job_uuid": job.job_uuid,
                "name": job.name,
                "state": job.state,
                "priority": job.priority,
                "run_at": job.run_at.isoformat() if getattr(job, "run_at", None) else None,
                "retry_count": job.retry_count,
                "max_retries": job.max_retries,
                "impact_score": payload.get("impact_score"),
                "error_message": getattr(job, "error_message", None),
            }
        finally:
            session.close()
    
    def get_scheduler_metrics(self) -> GetSchedulerMetricsResult:
        """Get comprehensive scheduler metrics"""
        return {
            "queue_metrics": self._job_queue_metrics.copy(),
            "execution_stats": {
                job_type: {
                    "avg_execution_time": sum(times) / len(times) if times else 0,
                    "success_rate": sum(successes) / len(successes) if successes else 0,
                    "total_executions": len(times)
                }
                for job_type, times in self._execution_stats.items()
                for successes in [self._failure_rates.get(job_type, [])]
            },
            "configuration": {
                "max_concurrent_jobs": self.max_concurrent_jobs,
                "polling_interval": self.polling_interval,
                "scheduling_strategy": self.scheduling_strategy.value,
                "retry_strategy": self.retry_strategy.value,
                "max_retry_attempts": self.max_retry_attempts
            },
            "is_running": self._running
        }
    
    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        action = request_data.get("action")
        try:
            if action == "submit_job":
                job_uuid = self.submit_job(
                    name=request_data.get("name", ""),
                    job_type=request_data.get("job_type", "default"),
                    payload=request_data.get("payload", {}),
                    run_at=datetime.fromisoformat(request_data["run_at"]) if request_data.get("run_at") else None,
                    priority=ImpactPriority(request_data["priority"]) if request_data.get("priority") else None,
                    max_retries=request_data.get("max_retries"),
                    tags=request_data.get("tags"),
                )
                return {"success": True, "job_uuid": job_uuid}
            if action == "get_job_status":
                status = self.get_job_status(request_data.get("job_uuid", ""))
                return {"success": bool(status), "status": status}
            if action == "get_metrics":
                return {"success": True, "metrics": self.get_scheduler_metrics()}
            if action == "start_scheduler":
                await self.start_scheduler()
                return {"success": True}
            if action == "stop_scheduler":
                await self.stop_scheduler()
                return {"success": True}
            return {"success": False, "error": "unknown_action"}
        except BiologyError as e:
            return self.handle_error(e, "process_request")


# Global scheduler instance
_scheduler_v3 = None


def get_scheduler_v3() -> ExperimentSchedulerV3:
    global _scheduler_v3
    if _scheduler_v3 is None:
        _scheduler_v3 = ExperimentSchedulerV3()
    return _scheduler_v3
