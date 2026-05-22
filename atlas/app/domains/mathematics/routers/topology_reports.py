from __future__ import annotations

import time
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.security.auth import require_scopes
from app.domains.mathematics.services.topology_service import TopologyService
from app.domains.mathematics.routers.topology import Point2D
from app.exceptions.domain.mathematics import MathematicsError


class TopologyReportRequest(BaseModel):
    points: List[Point2D] = Field(..., description="Puntos 2D para análisis topológico")
    epsilon: float = Field(0.2, gt=0, le=10, description="Radio ε para invariantes e histograma de grados")
    epsilon_range: Tuple[float, float] = Field((0.1, 1.0), description="Rango [min, max] de ε para persistencia")
    num_steps: int = Field(20, ge=5, le=200, description="Número de pasos en la filtración de persistencia")
    max_dimension: int = Field(2, ge=1, le=3, description="Dimensión máxima para homología")
    include_images: bool = Field(True, description="Incluir imágenes base64 (diagrama y curvas)")


class TopologyReportResponse(BaseModel):
    epsilon: float
    epsilon_range: Tuple[float, float]
    invariants: Dict[str, Any]
    persistence: Dict[str, Any]
    images: Optional[Dict[str, str]]
    execution_time_seconds: float
    timestamp: str


router = APIRouter(prefix="/api/topology", tags=["topology"])


@router.post("/report", response_model=TopologyReportResponse)
async def topology_report(
    request: TopologyReportRequest,
    current_user: dict = Depends(require_scopes(["topology:analysis"]))
) -> TopologyReportResponse:
    start = time.time()
    try:
        service = TopologyService()

        # Invariantes básicos a ε puntual
        inv = await service.calculate_invariants(
            points=[(p.x, p.y) for p in request.points],
            epsilon=request.epsilon
        )

        # Persistencia en rango de ε
        pers = await service.analyze_persistence(
            points=[(p.x, p.y) for p in request.points],
            epsilon_range=request.epsilon_range,
            num_steps=request.num_steps,
            max_dimension=request.max_dimension
        )

        images: Optional[Dict[str, str]] = None
        if request.include_images:
            import io
            import base64
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import numpy as np

            images = {}

            # Diagrama de persistencia mejorado
            fig1, ax1 = plt.subplots(figsize=(6, 5), dpi=120)
            diag = pers.get("persistence_diagram", [])
            colors = {0: "tab:blue", 1: "tab:orange", 2: "tab:green", 3: "tab:red"}
            labels = {0: "H₀ (componentes)", 1: "H₁ (ciclos)", 2: "H₂ (cavidades)", 3: "H₃+"}
            
            # Agregar puntos por dimensión con tamaño proporcional a persistencia
            plotted_dims = set()
            for item in diag:
                dim = int(item.get("dimension", 0))
                b = float(item.get("birth", 0.0))
                d = float(item.get("death", b))
                persistence = float(item.get("persistence", d - b))
                
                # Tamaño proporcional a persistencia (min 10, max 100)
                size = max(10, min(100, 20 + 80 * (persistence / max(1e-6, max(p.get("persistence", 0.1) for p in diag)))))
                
                label = labels.get(dim, f"H₄+") if dim not in plotted_dims else ""
                ax1.scatter(b, d, c=colors.get(dim, "black"), s=size, alpha=0.7, label=label)
                plotted_dims.add(dim)
            
            # Línea diagonal y configuración
            max_val = max([max(item.get("birth", 0), item.get("death", 0)) for item in diag] + [request.epsilon_range[1]])
            ax1.plot([0, max_val], [0, max_val], ls="--", c="gray", lw=1, alpha=0.5)
            ax1.set_xlabel("Birth")
            ax1.set_ylabel("Death")
            ax1.set_title(f"Persistence Diagram\n({len(diag)} features, entropy={pers.get('persistence_entropy', 0):.2f})")
            
            if plotted_dims:
                ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            ax1.grid(True, alpha=0.3)
            buf1 = io.BytesIO()
            plt.tight_layout()
            fig1.savefig(buf1, format="png", bbox_inches='tight')
            plt.close(fig1)
            buf1.seek(0)
            images["persistence_diagram_base64"] = base64.b64encode(buf1.read()).decode("ascii")

            # Curvas de Betti
            fig2, ax2 = plt.subplots(figsize=(5, 4), dpi=120)
            eps_vals = pers.get("epsilon_values", [])
            betti_curves = pers.get("betti_curves", {})
            for dim_str, values in betti_curves.items():
                ax2.plot(eps_vals, values, label=f"Betti {dim_str}")
            ax2.set_xlabel("epsilon")
            ax2.set_ylabel("Betti")
            ax2.set_title("Betti Curves")
            ax2.legend()
            buf2 = io.BytesIO()
            plt.tight_layout()
            fig2.savefig(buf2, format="png")
            plt.close(fig2)
            buf2.seek(0)
            images["betti_curves_base64"] = base64.b64encode(buf2.read()).decode("ascii")

            # Histograma de grados en ε puntual
            P = np.array([[p.x, p.y] for p in request.points], dtype=float)
            if len(P) > 0:
                D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(axis=2))
                A = (D <= request.epsilon).astype(int)
                np.fill_diagonal(A, 0)
                deg = A.sum(axis=1)
            else:
                deg = np.array([0])
            fig3, ax3 = plt.subplots(figsize=(5, 4), dpi=120)
            bins = range(0, int(deg.max()) + 2) if len(deg) > 0 else [0, 1]
            ax3.hist(deg, bins=bins, color="tab:blue", edgecolor="white")
            ax3.set_xlabel("grado")
            ax3.set_ylabel("frecuencia")
            ax3.set_title("Degree Histogram (ε=%.3f)" % request.epsilon)
            ax3.grid(alpha=0.2)
            buf3 = io.BytesIO()
            plt.tight_layout()
            fig3.savefig(buf3, format="png")
            plt.close(fig3)
            buf3.seek(0)
            images["degree_histogram_base64"] = base64.b64encode(buf3.read()).decode("ascii")

        exec_s = time.time() - start
        return TopologyReportResponse(
            epsilon=request.epsilon,
            epsilon_range=request.epsilon_range,
            invariants=inv,
            persistence={
                k: v for k, v in pers.items()
                if k in {"persistence_diagram", "betti_curves", "persistence_entropy", "epsilon_values"}
            },
            images=images,
            execution_time_seconds=exec_s,
            timestamp=datetime.now().isoformat()
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


