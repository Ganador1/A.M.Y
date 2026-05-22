"""
Synthesis Equipment Router - AXIOM META 4
API endpoints para equipos de síntesis automatizada con scheduling.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.bootstrap_logging import logger
from app.security import require_scopes
from app.domains.engineering.services.synthesis_equipment import (
    ReactionParameters,
    SynthesisEquipmentService,
    SynthesisEquipmentType,
)

router = APIRouter(
    prefix="/api/v1/synthesis-equipment",
    tags=["Synthesis Equipment"],
    dependencies=[Depends(require_scopes(["lab-equipment"]))],
)

_service = SynthesisEquipmentService()


class ReactionParametersModel(BaseModel):
    temperature: float
    pressure: float
    duration_minutes: float
    stirring_rpm: Optional[float] = None
    solvent: Optional[str] = None
    atmosphere: Optional[str] = None
    scale_mmol: Optional[float] = None


class SynthesisTaskModel(BaseModel):
    equipment_id: str
    equipment_type: str
    recipe_name: str = Field(default="generic_synthesis")
    reagents: List[Dict[str, Any]] = Field(default_factory=list)
    parameters: ReactionParametersModel
    priority: int = Field(default=5, ge=1, le=10)


@router.get("/equipment", summary="List synthesis equipment")
async def list_equipment():
    return await _service.list_equipment()


@router.post("/submit", summary="Submit synthesis task")
async def submit_task(task: SynthesisTaskModel):
    result = await _service.submit_task({"task": task.dict()})
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/batch-submit", summary="Submit synthesis tasks in batch")
async def batch_submit(tasks: List[SynthesisTaskModel]):
    result = await _service.batch_submit({"tasks": [t.dict() for t in tasks]})
    return result


@router.get("/task/{task_id}", summary="Get synthesis task status")
async def get_task(task_id: str):
    result = await _service.get_task({"task_id": task_id})
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@router.delete("/task/{task_id}", summary="Cancel synthesis task")
async def cancel_task(task_id: str):
    result = await _service.cancel_task({"task_id": task_id})
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/scheduler", summary="Get scheduler status")
async def scheduler_status():
    return await _service.scheduler_status()


@router.get("/types", summary="List synthesis equipment types")
async def equipment_types():
    return {
        "success": True,
        "types": [t.value for t in SynthesisEquipmentType],
    }


