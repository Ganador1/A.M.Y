"""
Synthesis Equipment Service - AXIOM META 4
Automated synthesis equipment simulation con scheduling y estimación de costos.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

from app.core.bootstrap_logging import logger
from app.services.base_service import BaseService
from app.exceptions.domain.biology import BiologyError


class SynthesisEquipmentType(Enum):
    """Tipos de equipos de síntesis"""
    LIQUID_HANDLER = "liquid_handler"
    BATCH_REACTOR = "batch_reactor"
    FLOW_REACTOR = "flow_reactor"
    PARALLEL_REACTOR = "parallel_reactor"


@dataclass
class ReactionParameters:
    """Parámetros de reacción para síntesis"""
    temperature: float
    pressure: float
    duration_minutes: float
    stirring_rpm: Optional[float] = None
    solvent: Optional[str] = None
    atmosphere: Optional[str] = None
    scale_mmol: Optional[float] = None


@dataclass
class SynthesisTask:
    """Definición de tarea de síntesis"""
    task_id: str
    equipment_id: str
    equipment_type: SynthesisEquipmentType
    recipe_name: str
    reagents: List[Dict[str, Any]]
    parameters: ReactionParameters
    priority: int = 5  # 1 más alta
    status: str = "queued"
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    cost_usd: Optional[float] = None


@dataclass
class EquipmentSpec:
    """Especificaciones de equipo"""
    equipment_id: str
    equipment_type: SynthesisEquipmentType
    name: str
    max_temp: float
    max_pressure: float
    max_parallel: int
    throughput_score: float
    status: str = "idle"


class SynthesisEquipmentService(BaseService):
    """Servicio de síntesis automatizada con scheduler interno"""

    def __init__(self):
        super().__init__("SynthesisEquipmentService")
        self.equipment: Dict[str, EquipmentSpec] = self._init_equipment()
        self.tasks: Dict[str, SynthesisTask] = {}
        self.queue: List[str] = []  # almacena task_ids
        # Scheduler en background (no bloquea el event loop principal)
        import os

        if os.getenv("PYTEST_RUNNING", "0").lower() in {"1", "true", "yes"}:
            # Evitar crear tasks durante la colección/ejecución de tests
            self._scheduler_task = None
        else:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._run_scheduler())
                    self._scheduler_task = None
                else:
                    self._scheduler_task = loop.create_task(self._run_scheduler())
            except Exception:
                # Entornos sin loop activo (tests o procesos limitados) pueden iniciar manualmente el scheduler
                self._scheduler_task = None
        logger.info("✅ SynthesisEquipmentService initialized")

    def _init_equipment(self) -> Dict[str, EquipmentSpec]:
        equipment: Dict[str, EquipmentSpec] = {
            "lh_01": EquipmentSpec(
                equipment_id="lh_01",
                equipment_type=SynthesisEquipmentType.LIQUID_HANDLER,
                name="Liquid Handler A",
                max_temp=60.0,
                max_pressure=1.5,
                max_parallel=96,
                throughput_score=0.9,
            ),
            "br_01": EquipmentSpec(
                equipment_id="br_01",
                equipment_type=SynthesisEquipmentType.BATCH_REACTOR,
                name="Batch Reactor 1L",
                max_temp=200.0,
                max_pressure=20.0,
                max_parallel=1,
                throughput_score=0.5,
            ),
            "fr_01": EquipmentSpec(
                equipment_id="fr_01",
                equipment_type=SynthesisEquipmentType.FLOW_REACTOR,
                name="Flow Reactor Micro",
                max_temp=150.0,
                max_pressure=50.0,
                max_parallel=1,
                throughput_score=0.8,
            ),
            "pr_08": EquipmentSpec(
                equipment_id="pr_08",
                equipment_type=SynthesisEquipmentType.PARALLEL_REACTOR,
                name="Parallel Reactor 8x50mL",
                max_temp=180.0,
                max_pressure=10.0,
                max_parallel=8,
                throughput_score=0.7,
            ),
        }
        return equipment

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            action = request_data.get("action", "")
            if action == "list_equipment":
                return await self.list_equipment()
            if action == "submit_task":
                return await self.submit_task(request_data)
            if action == "batch_submit":
                return await self.batch_submit(request_data)
            if action == "get_task":
                return await self.get_task(request_data)
            if action == "cancel_task":
                return await self.cancel_task(request_data)
            if action == "scheduler_status":
                return await self.scheduler_status()
            return {"success": False, "error": f"Unknown action: {action}"}
        except BiologyError as e:
            return self.handle_error(e, "process_request")

    async def list_equipment(self) -> Dict[str, Any]:
        items = [
            {
                "equipment_id": spec.equipment_id,
                "type": spec.equipment_type.value,
                "name": spec.name,
                "max_temp": spec.max_temp,
                "max_pressure": spec.max_pressure,
                "max_parallel": spec.max_parallel,
                "throughput_score": spec.throughput_score,
                "status": spec.status,
            }
            for spec in self.equipment.values()
        ]
        return {"success": True, "equipment": items, "count": len(items)}

    async def submit_task(self, request: Dict[str, Any]) -> Dict[str, Any]:
        data = request.get("task", {})
        try:
            task = SynthesisTask(
                task_id=data.get("task_id") or f"syn_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                equipment_id=data["equipment_id"],
                equipment_type=SynthesisEquipmentType(data["equipment_type"]),
                recipe_name=data.get("recipe_name", "generic_synthesis"),
                reagents=data.get("reagents", []),
                parameters=ReactionParameters(**data["parameters"]),
                priority=int(data.get("priority", 5)),
            )
        except BiologyError as e:
            return {"success": False, "error": f"Invalid task: {e}"}

        if task.equipment_id not in self.equipment:
            return {"success": False, "error": f"Unknown equipment_id {task.equipment_id}"}

        self.tasks[task.task_id] = task
        self._enqueue(task)
        logger.info(f"🧪 Task queued: {task.task_id} on {task.equipment_id}")
        return {"success": True, "task_id": task.task_id, "status": task.status}

    async def batch_submit(self, request: Dict[str, Any]) -> Dict[str, Any]:
        tasks = request.get("tasks", [])
        results: List[Dict[str, Any]] = []
        for t in tasks:
            res = await self.submit_task({"task": t})
            results.append(res)
        return {"success": True, "results": results, "submitted": len(results)}

    async def get_task(self, request: Dict[str, Any]) -> Dict[str, Any]:
        task_id = request.get("task_id")
        task = self.tasks.get(task_id)
        if not task:
            return {"success": False, "error": f"Task {task_id} not found"}
        return {"success": True, "task": self._task_to_dict(task)}

    async def cancel_task(self, request: Dict[str, Any]) -> Dict[str, Any]:
        task_id = request.get("task_id")
        task = self.tasks.get(task_id)
        if not task:
            return {"success": False, "error": f"Task {task_id} not found"}
        if task.status not in ("queued", "running"):
            return {"success": False, "error": f"Cannot cancel task in status {task.status}"}
        task.status = "cancelled"
        logger.info(f"⛔ Task cancelled: {task_id}")
        return {"success": True, "task_id": task_id, "status": task.status}

    async def scheduler_status(self) -> Dict[str, Any]:
        return {
            "success": True,
            "queue_length": len(self.queue),
            "running": any(t.status == "running" for t in self.tasks.values()),
            "tasks_total": len(self.tasks),
        }

    def _enqueue(self, task: SynthesisTask) -> None:
        # Insertar por prioridad (número menor = mayor prioridad)
        inserted = False
        for i, task_id in enumerate(self.queue):
            queued = self.tasks[task_id]
            if task.priority < queued.priority:
                self.queue.insert(i, task.task_id)
                inserted = True
                break
        if not inserted:
            self.queue.append(task.task_id)

    async def _run_scheduler(self) -> None:
        # Scheduler secuencial simple (puede extenderse a paralelo por equipo)
        while True:
            try:
                if not self.queue:
                    await asyncio.sleep(0.1)
                    continue
                task_id = self.queue.pop(0)
                task = self.tasks.get(task_id)
                if not task or task.status == "cancelled":
                    continue
                spec = self.equipment[task.equipment_id]
                # Validación de límites de equipo
                if (task.parameters.temperature > spec.max_temp) or (task.parameters.pressure > spec.max_pressure):
                    task.status = "failed"
                    task.error = "Parameter limits exceeded"
                    logger.warning(f"⚠️ Task failed (limits): {task.task_id}")
                    continue
                # Ejecutar tarea (simulado)
                task.status = "running"
                task.started_at = datetime.utcnow()
                exec_time = min(task.parameters.duration_minutes / 600.0, 2.0)  # escala tiempo
                await asyncio.sleep(exec_time)
                # Simular resultados
                yield_percent = float(np.clip(np.random.normal(82, 10), 30, 98))
                purity_percent = float(np.clip(np.random.normal(95, 3), 80, 99.9))
                task.cost_usd = self._estimate_cost(task)
                task.completed_at = datetime.utcnow()
                task.status = "completed"
                task.result = {
                    "yield_percent": yield_percent,
                    "purity_percent": purity_percent,
                    "byproducts": int(max(0, np.random.poisson(1.2) - 1)),
                }
                logger.info(f"✅ Task completed: {task.task_id} ({yield_percent:.1f}% yield)")
            except BiologyError as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(0.2)

    def _task_to_dict(self, task: SynthesisTask) -> Dict[str, Any]:
        return {
            "task_id": task.task_id,
            "equipment_id": task.equipment_id,
            "equipment_type": task.equipment_type.value,
            "recipe_name": task.recipe_name,
            "reagents": task.reagents,
            "parameters": task.parameters.__dict__,
            "priority": task.priority,
            "status": task.status,
            "submitted_at": task.submitted_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error": task.error,
            "cost_usd": task.cost_usd,
        }

    def _estimate_cost(self, task: SynthesisTask) -> float:
        # Modelo de costos simple: reactivos + tiempo + factor de equipo
        reagents_cost = 0.0
        for r in task.reagents:
            qty = float(r.get("quantity", 1.0))
            unit_cost = float(r.get("unit_cost", 1.0))
            reagents_cost += qty * unit_cost
        time_cost = (task.parameters.duration_minutes / 60.0) * 25.0  # $/hora
        equipment_factor = {
            SynthesisEquipmentType.LIQUID_HANDLER: 1.1,
            SynthesisEquipmentType.BATCH_REACTOR: 1.3,
            SynthesisEquipmentType.FLOW_REACTOR: 1.5,
            SynthesisEquipmentType.PARALLEL_REACTOR: 1.4,
        }[task.equipment_type]
        return round((reagents_cost + time_cost) * equipment_factor, 2)


