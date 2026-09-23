"""
Structural Database Router
Endpoints para obtener PDB/UniProt/AlphaFold DB.

ASYNC MIGRATION: Todos los endpoints ahora son async.
Ver: ROADMAP_5_PHASE2_2_DETAILED_ANALYSIS.md
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.structural_database_service import StructuralDatabaseService
from app.types.structural_db_types import (
    GetPdbResult,
    GetUniprotResult,
    GetAlphafoldResult,
    SequenceSearchResult,
)


router = APIRouter()

svc = StructuralDatabaseService()


@router.get("/pdb/{pdb_id}")
async def get_pdb(pdb_id: str) -> GetPdbResult:
    """Fetch PDB file (async)."""
    res = await svc.fetch_pdb(pdb_id)
    if not res.get('success'):
        raise HTTPException(status_code=404, detail=res.get('error', 'PDB no encontrado'))
    return res


@router.get("/uniprot/{accession}")
async def get_uniprot(accession: str) -> GetUniprotResult:
    """Fetch UniProt metadata (async)."""
    res = await svc.fetch_uniprot(accession)
    if not res.get('success'):
        raise HTTPException(status_code=404, detail=res.get('error', 'UniProt no encontrado'))
    return res


@router.get("/alphafold/{uniprot_id}")
async def get_alphafold(uniprot_id: str) -> GetAlphafoldResult:
    """Fetch AlphaFold prediction (async)."""
    res = await svc.fetch_alphafold_prediction(uniprot_id)
    if not res.get('success'):
        raise HTTPException(status_code=404, detail=res.get('error', 'AlphaFold DB no disponible'))
    return res


class SequenceSearchRequest(BaseModel):
    sequence: str = Field(..., description="Secuencia de aminoácidos (>=10 aa)")
    identity_cutoff: float = Field(0.3, ge=0.0, le=1.0)
    max_results: int = Field(10, ge=1, le=100)


@router.post("/sequence-search")
async def sequence_search(req: SequenceSearchRequest) -> SequenceSearchResult:
    """Search similar structures by sequence (async)."""
    res = await svc.search_similar_structures(req.sequence, req.identity_cutoff, req.max_results)
    if not res.get('success'):
        raise HTTPException(status_code=400, detail=res.get('error', 'Búsqueda fallida'))
    return res
