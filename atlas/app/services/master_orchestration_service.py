"""Master orchestration service (lightweight implementation for tests).

Provides:
- MasterOrchestrationService with async pipeline creation and simple execution simulation.
- PipelineStatus enum and Pipeline container type.
"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time
import logging

logger = logging.getLogger(__name__)


class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Pipeline:
    id: str
    name: str
    status: PipelineStatus = PipelineStatus.PENDING
    tasks: List[Any] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    success_rate: float = 0.0


class MasterOrchestrationService:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.active_pipelines: Dict[str, Pipeline] = {}
        self.pipeline_history: List[Pipeline] = []
        self.services: Dict[str, Any] = {}
        self.background_tasks_started = False

    async def create_autonomous_pipeline(self, question: str, domain: str, template: str, options: Dict[str, Any]) -> str:
        """Crea y dispara la ejecución de un pipeline autónomo (simulado)."""
        pipeline_id = str(uuid.uuid4())
        pipeline = Pipeline(id=pipeline_id, name=f"{template}:{domain}")

        # Build task list from registered services if available
        pipeline.tasks = list(self.services.keys()) if self.services else ["task"]
        pipeline.status = PipelineStatus.RUNNING
        self.active_pipelines[pipeline_id] = pipeline

        # Start async execution
        asyncio.create_task(self._run_pipeline(pipeline))

        return pipeline_id

    async def _run_pipeline(self, pipeline: Pipeline) -> None:
        try:
            # Simulate work: iterate tasks and call mock methods if available
            successes = 0
            total = max(1, len(pipeline.tasks))
            for t in pipeline.tasks:
                # If services were injected as mock objects, try calling a generic coroutine
                svc = self.services.get(t)
                if svc and hasattr(svc, 'orchestrate_research_cycle'):
                    try:
                        await svc.orchestrate_research_cycle()
                        successes += 1
                    except Exception:
                        logger.exception("Service task failed: %s", t)
                else:
                    # small sleep to simulate progress
                    await asyncio.sleep(0.01)
                    successes += 1

            pipeline.success_rate = successes / total
            pipeline.status = PipelineStatus.COMPLETED
        except Exception:
            logger.exception("Pipeline execution failed: %s", pipeline.id)
            pipeline.status = PipelineStatus.FAILED
        finally:
            # Move to history after brief delay so tests can detect it's run
            await asyncio.sleep(0.01)
            # Remove from active and append to history
            try:
                self.active_pipelines.pop(pipeline.id, None)
                self.pipeline_history.append(pipeline)
            except Exception:
                logger.exception("Failed to finalize pipeline %s", pipeline.id)


# Export a module-level instance for convenience
master_orchestration_service = MasterOrchestrationService()
