"""Mathematical Conjecture Contracts

Modelos Pydantic versionados que proporcionan esquemas estables para:
- Payloads de conjeturas de entrada del laboratorio matemático
- Outputs de normalización (capa simbólica)
- Resultados de verificación (capa SMT)
- Artefactos de procesamiento end-to-end

Objetivos de diseño:
- Salida JSON determinística (claves ordenadas)
- Evolución compatible hacia atrás vía campo de versión semántica
- Ligero (sin deps pesadas además de pydantic / stdlib)
- Enumeraciones de estado explícitas para evitar magic strings dispersos
"""
from __future__ import annotations
import asyncio

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import json
import time

CONJECTURE_CONTRACT_VERSION = "1.0.0"


class ConjectureType(str, Enum):
    GENERIC = "generic"
    NUMBER_THEORY = "number_theory"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    SEQUENCE = "sequence"


class NormalizationStatus(str, Enum):
    OK = "OK"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class VerificationStatus(str, Enum):
    PROVEN = "PROVEN"
    REFUTED = "REFUTED"
    UNKNOWN = "UNKNOWN"
    Z3_UNAVAILABLE = "Z3_UNAVAILABLE"
    NORMALIZATION_FAILED = "NORMALIZATION_FAILED"
    ERROR = "ERROR"


class ConjecturePayload(BaseModel):
    id: str = Field(..., description="Unique conjecture identifier")
    statement: str = Field(..., description="Human or symbolic statement")
    domain: Dict[str, Any] = Field(default_factory=dict, description="Domain specification for variables")
    type: ConjectureType = Field(default=ConjectureType.GENERIC)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_ts: float = Field(default_factory=time.time)
    version: str = Field(default=CONJECTURE_CONTRACT_VERSION)


class NormalizationResult(BaseModel):
    status: NormalizationStatus
    ast_type: Optional[str] = None
    smt_script: Optional[str] = None
    variables: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class VerificationResult(BaseModel):
    verified: Optional[bool]
    status: VerificationStatus
    counterexample: Optional[Dict[str, Any]] = None
    proof_method: Optional[str] = None
    error: Optional[str] = None
    elapsed_ms: Optional[int] = None


class ConjectureProcessingResult(BaseModel):
    conjecture: ConjecturePayload
    normalization: NormalizationResult
    verification: VerificationResult
    processing_version: str = Field(default=CONJECTURE_CONTRACT_VERSION)
    elapsed_ms: int = Field(..., description="Processing elapsed time in milliseconds")

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="python"), ensure_ascii=False, sort_keys=True)


# Utility builders -----------------------------------------------------------------

def build_normalization_result(raw: Dict[str, Any]) -> NormalizationResult:
    return NormalizationResult(
        status=NormalizationStatus(raw.get("status", "ERROR")),
        ast_type=raw.get("ast_type"),
        smt_script=raw.get("smt_script"),
        variables=raw.get("variables", []) or [],
        error=raw.get("error"),
    )


def build_verification_result(raw: Dict[str, Any]) -> VerificationResult:
    return VerificationResult(
        verified=raw.get("verified"),
        status=VerificationStatus(raw.get("status", "UNKNOWN")),
        counterexample=raw.get("counterexample"),
        proof_method=raw.get("proof_method"),
        error=raw.get("error"),
    )


__all__ = [
    "ConjecturePayload",
    "NormalizationResult",
    "VerificationResult",
    "ConjectureProcessingResult",
    "build_normalization_result",
    "build_verification_result",
    "ConjectureType",
    "NormalizationStatus",
    "VerificationStatus",
]

# -----------------------------------------------------------------------------
# Contratos unificados (ConjectureResult, VerifiedStatement + ProofMeta)
# -----------------------------------------------------------------------------

class ConjectureStatusContract(str, Enum):
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    DISPROVEN = "disproven"
    PARTIALLY_VERIFIED = "partially_verified"
    ABANDONED = "abandoned"


class ProofMeta(BaseModel):
    version: str = Field(default=CONJECTURE_CONTRACT_VERSION)
    normalized_hash: Optional[str] = Field(
        default=None, description="Hash determinista de la forma normalizada"
    )
    solver: Optional[str] = Field(default="Z3", description="Solver utilizado")
    elapsed_ms: Optional[int] = Field(default=None, description="Tiempo de verificación en ms")
    ts: float = Field(default_factory=time.time, description="Timestamp de generación")


class VerifiedStatement(BaseModel):
    id: str = Field(..., description="Identificador de la afirmación/verificación")
    statement: str = Field(..., description="Enunciado original o formalizado")
    status: VerificationStatus = Field(..., description="Resultado de verificación")
    is_proven: Optional[bool] = Field(default=None)
    proof: Optional[str] = Field(default=None, description="Borrador/idea de prueba si aplica")
    counterexample: Optional[Dict[str, Any]] = Field(default=None)
    proof_meta: Optional[ProofMeta] = Field(default=None)

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="python"), ensure_ascii=False, sort_keys=True)


class ConjectureResult(BaseModel):
    id: str = Field(..., description="Identificador único de la conjetura")
    statement: str = Field(..., description="Enunciado humano o simbólico")
    source: str = Field(default="mathematics_lab", description="Origen de la conjetura")
    status: ConjectureStatusContract = Field(default=ConjectureStatusContract.PROPOSED)
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Evidencia asociada")
    novelty: float = Field(default=0.0, ge=0.0, le=1.0, description="Score de novedad")
    created_ts: float = Field(default_factory=time.time)
    updated_ts: float = Field(default_factory=time.time)
    version: str = Field(default=CONJECTURE_CONTRACT_VERSION)

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="python"), ensure_ascii=False, sort_keys=True)


# Exportar contratos unificados
__all__ += [
    "ConjectureStatusContract",
    "ProofMeta",
    "VerifiedStatement",
    "ConjectureResult",
]