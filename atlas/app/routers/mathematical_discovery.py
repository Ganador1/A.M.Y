"""
Mathematical Discovery Router

FastAPI router for automated mathematical discovery and conjecture investigation.
Provides endpoints for heuristic-based mathematical exploration, conjecture testing,
and autonomous mathematical discovery using lightweight formal methods.

This router implements mathematical discovery capabilities for:
- Seed conjecture generation across mathematical domains
- Individual conjecture investigation and proof attempts
- Autonomous exploration cycles with iterative discovery
- Results persistence and statistical analysis
- Export functionality for documentation and publication

The router integrates with the MathematicalDiscoveryEngine to provide
researchers with tools for automated mathematical exploration and discovery,
focusing on heuristic approaches rather than full formal verification.

Endpoints:
- GET /seeds: Generate seed conjectures for mathematical domains
- POST /investigate: Investigate individual mathematical conjectures
- POST /autonomous: Run autonomous mathematical discovery cycles
- GET /results: Retrieve discovery results with export options

Dependencies:
- MathematicalDiscoveryEngine: Core discovery and investigation engine
- DiscoveryPersistence: Results storage and retrieval service
- MathematicalExporter: Export functionality for results
- Conjecture/InvestigationResult: Mathematical discovery data models

Usage:
    All endpoints support mathematical exploration across domains like algebra,
    analysis, geometry, and number theory. Results can be exported in multiple
    formats for documentation and further analysis.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.mathematical_discovery_engine import (
    MathematicalDiscoveryEngine,
    Conjecture,
    InvestigationResult,
)
from app.domains.mathematics.services.mathematical_discovery_persistence import DiscoveryPersistence
from app.services.mathematical_exporter import results_to_markdown, results_to_latex

router = APIRouter(prefix="/math/discovery", tags=["mathematical_discovery"])
_persistence = DiscoveryPersistence()
engine = MathematicalDiscoveryEngine(persistence=_persistence)


class InvestigateRequest(BaseModel):
    statement: str = Field(..., description="Enunciado de la conjetura, ej: (a+b)^2 = a^2 + 2*a*b + b^2")
    domain: str = Field("algebra", description="Dominio general")
    goal: str = Field("identity", description="Tipo de objetivo")


class AutonomousRequest(BaseModel):
    domain: str = Field("algebra")
    cycles: int = Field(2, ge=1, le=20)
    per_cycle: int = Field(3, ge=1, le=20)


@router.get("/seeds")
async def get_seed_conjectures(domain: str = "algebra", limit: int = 5):
    seeds = engine.generate_seed_conjectures(domain=domain, limit=limit)
    return {
        "domain": domain,
        "count": len(seeds),
        "conjectures": [c.__dict__ for c in seeds],
        "provers": list(engine.provers.keys()),
    }


@router.post("/investigate")
async def investigate_conjecture(req: InvestigateRequest):
    conjecture = Conjecture(
        id="api_manual",
        statement=req.statement,
        domain=req.domain,
        goal=req.goal,
        metadata={"source": "api"},
    )
    result = await engine.investigate_conjecture_async(conjecture)
    return {
        "status": result.status,
        "proof": result.proof,
        "counterexample": result.counterexample,
        "importance": result.importance,
        "attempts": result.attempts,
        "time_seconds": result.time_seconds,
    }


@router.post("/autonomous")
async def autonomous(req: AutonomousRequest):
    results = engine.autonomous_exploration(domain=req.domain, cycles=req.cycles, per_cycle=req.per_cycle)
    summary = engine.summarize_results(results)
    return {
        "summary": summary,
        "results": [
            {
                "conjecture": r.conjecture.statement,
                "status": r.status,
                "proof": r.proof,
                "counterexample": r.counterexample,
            }
            for r in results
        ],
    }


@router.get("/results")
async def list_results(limit: int = 50, export_format: str = "json"):
    data = _persistence.read_all(limit=limit)
    stats = _persistence.stats()

    if export_format in {"markdown", "latex"}:
        results_objs = []
        for item in data:
            c_raw = item.get("conjecture", {})
            c = Conjecture(
                id=c_raw.get("id", "unknown"),
                statement=c_raw.get("statement", ""),
                domain=c_raw.get("domain", "unknown"),
                goal=c_raw.get("goal", "identity"),
                metadata=c_raw.get("metadata", {}),
            )
            res = InvestigationResult(
                conjecture=c,
                status=item.get("status", "unknown"),
                proof=item.get("proof"),
                counterexample=item.get("counterexample"),
                importance=item.get("importance", 0.0),
                time_seconds=item.get("time_seconds", 0.0),
            )
            results_objs.append(res)
        content = results_to_markdown(results_objs) if export_format == "markdown" else results_to_latex(results_objs)
        return {"format": export_format, "content": content}

    return {"count": len(data), "limit": limit, "results": data, "stats": stats, "format": "json"}
