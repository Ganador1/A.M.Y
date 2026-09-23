"""Stub for conjecture contracts to satisfy test imports."""
from dataclasses import dataclass
from enum import Enum


class NormalizationStatus(str, Enum):
    NORMALIZED = "normalized"
    PENDING = "pending"
    FAILED = "failed"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    FAILED = "failed"
    OPEN = "open"


@dataclass
class ConjecturePayload:
    statement: str
    domain: str = "mathematics"
    metadata: dict | None = None


def build_normalization_result(payload: ConjecturePayload, status: NormalizationStatus = NormalizationStatus.NORMALIZED):
    return {"payload": payload, "status": status, "normalized_statement": payload.statement}


def build_verification_result(payload: ConjecturePayload, status: VerificationStatus = VerificationStatus.OPEN):
    return {"payload": payload, "status": status}
