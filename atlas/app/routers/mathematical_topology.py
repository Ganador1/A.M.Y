from __future__ import annotations

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.routers.auth import require_scopes
from app.domains.mathematics.services.mathematical_computation_laboratory import MathematicalComputationLaboratory
from app.exceptions.domain.mathematics import MathematicsError


class MathematicalTopologyReportRequest(BaseModel):
    points: List[Dict[str, float]]
    epsilon: float = Field(0.2, gt=0, le=10)
    epsilon_range: Tuple[float, float] = Field((0.1, 1.0))
    num_steps: int = Field(20, ge=5, le=200)
    max_dimension: int = Field(2, ge=1, le=3)
    include_images: bool = True
    generate_conjecture: bool = True


router = APIRouter(prefix="/api/mathematics/topology", tags=["mathematical-topology"])


@router.post("/report-insights")
async def report_insights(
    req: MathematicalTopologyReportRequest,
    user=Depends(require_scopes(["mathematics:analysis"]))
) -> Dict[str, Any]:
    try:
        async with MathematicalComputationLaboratory() as lab:
            await lab.start_analysis_session("Topology report via Mathematical Laboratory")
            result = await lab.analyze_point_cloud_topology(
                points=req.points,
                epsilon=req.epsilon,
                epsilon_range=req.epsilon_range,
                num_steps=req.num_steps,
                max_dimension=req.max_dimension,
                include_images=req.include_images,
                generate_conjecture_flag=req.generate_conjecture,
            )
            await lab.end_analysis_session()
            return {
                "epsilon": req.epsilon,
                "epsilon_range": req.epsilon_range,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


