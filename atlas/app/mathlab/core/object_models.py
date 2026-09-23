from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class MathematicalObject(BaseModel):
    """Modelo base para objetos matemáticos registrados en MathLab.

    La carga útil (payload) debe ser un JSON normalizado que describa el objeto
    en su forma canónica para asegurar hashing semántico determinista.
    """

    id: str = Field(..., description="Identificador único (UUID)")
    type: str = Field(..., description="Tipo de objeto (e.g., graph, sequence, elliptic_curve)")
    semantic_hash: str = Field(..., description="Hash semántico determinista del objeto")
    spec_version: str = Field("v1", description="Versión del esquema de objeto")
    payload_json: Dict[str, Any] = Field(..., description="Representación JSON del objeto en forma normalizada")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación UTC")


class InvariantRecord(BaseModel):
    """Registro de invariantes computados para un objeto."""

    object_id: str
    key: str
    value_numeric: Optional[float] = None
    value_json: Optional[Dict[str, Any]] = None
    source: str = "mathlab"
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class EmbeddingRecord(BaseModel):
    """Registro de embeddings asociados a un objeto."""

    object_id: str
    embedding_type: str
    vector: list[float]
    dim: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None