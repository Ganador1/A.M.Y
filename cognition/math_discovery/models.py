"""Typed domain objects for mathematical discovery campaigns."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any
from uuid import uuid4


class ClaimStatus(StrEnum):
    PROPOSED = "proposed"
    COMPUTATIONALLY_SUPPORTED = "computationally_supported"
    LITERATURE_CHECKED = "literature_checked"
    ADVERSARIALLY_SURVIVED = "adversarially_survived"
    INDEPENDENTLY_REDERIVED = "independently_rederived"
    FORMALLY_VERIFIED = "formally_verified"
    EXPERT_REVIEW_PENDING = "expert_review_pending"
    RELEASE_CANDIDATE = "release_candidate"
    REFUTED = "refuted"
    DUPLICATE = "duplicate"
    UNSUPPORTED = "unsupported"
    STALLED = "stalled"
    WITHDRAWN = "withdrawn"


TERMINAL_STATUSES = {
    ClaimStatus.RELEASE_CANDIDATE,
    ClaimStatus.REFUTED,
    ClaimStatus.DUPLICATE,
    ClaimStatus.UNSUPPORTED,
    ClaimStatus.STALLED,
    ClaimStatus.WITHDRAWN,
}


class ResearchRole(StrEnum):
    EXPLORER = "explorer"
    CONSTRUCTOR = "constructor"
    FALSIFIER = "falsifier"
    SYNTHESIZER = "synthesizer"
    HOSTILE_REFEREE = "hostile_referee"
    INDEPENDENT_REDERIVER = "independent_rederiver"
    FORMALIZER = "formalizer"
    NOVELTY_AUDITOR = "novelty_auditor"


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


JOB_TERMINAL_STATUSES = {
    JobStatus.COMPLETED,
    JobStatus.FAILED,
    JobStatus.CANCELLED,
}


@dataclass(frozen=True)
class ResearchJob:
    objective: str
    role: ResearchRole
    phase: str
    model: str
    job_id: str = field(default_factory=lambda: f"job_{uuid4().hex}")
    agent_id: str = field(default_factory=lambda: f"agent_{uuid4().hex}")
    branch_id: str = "main"
    dependencies: tuple[str, ...] = ()
    allowed_artifact_hashes: tuple[str, ...] = ()
    priority: int = 100
    max_attempts: int = 2
    max_tokens: int = 16384
    num_ctx: int = 1_000_000
    temperature: float = 0.7
    think: bool | str = True
    output_mode: str = "direct_json"
    capsule_max_tokens: int = 8192

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("job objective cannot be empty")
        for value, label, prefix in (
            (self.job_id, "job_id", "job_"),
            (self.agent_id, "agent_id", "agent_"),
        ):
            if not value.startswith(prefix):
                raise ValueError(f"{label} must start with {prefix}")
        if not self.phase.strip() or not self.model.strip() or not self.branch_id.strip():
            raise ValueError("phase, model and branch_id cannot be empty")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        if self.max_tokens < 1 or self.num_ctx < 1 or self.capsule_max_tokens < 1:
            raise ValueError("token and context budgets must be positive")
        if self.output_mode not in {"direct_json", "reason_then_capsule"}:
            raise ValueError("output_mode must be direct_json or reason_then_capsule")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        if self.job_id in self.dependencies:
            raise ValueError("job cannot depend on itself")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["role"] = self.role.value
        value["dependencies"] = list(self.dependencies)
        value["allowed_artifact_hashes"] = list(self.allowed_artifact_hashes)
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ResearchJob":
        payload = dict(value)
        payload["role"] = ResearchRole(payload["role"])
        payload["dependencies"] = tuple(payload.get("dependencies", ()))
        payload["allowed_artifact_hashes"] = tuple(
            payload.get("allowed_artifact_hashes", ())
        )
        return cls(**payload)


@dataclass(frozen=True)
class JobResult:
    job_id: str
    agent_id: str
    role: ResearchRole
    parsed: dict[str, Any]
    output_artifact: dict[str, Any]
    provenance_event_hash: str
    attempt: int

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["role"] = self.role.value
        return value


@dataclass(frozen=True)
class Claim:
    statement: str
    domain: str
    created_by_job: str
    claim_id: str = field(default_factory=lambda: f"clm_{uuid4().hex}")
    quantifiers: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    parent_claim_ids: tuple[str, ...] = ()
    status: ClaimStatus = ClaimStatus.PROPOSED
    supporting_artifact_hashes: tuple[str, ...] = ()
    contradicting_artifact_hashes: tuple[str, ...] = ()
    confidence: float | None = None
    truth_verified: bool = False
    verification_method: str | None = None

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("claim statement cannot be empty")
        if not self.domain.strip():
            raise ValueError("claim domain cannot be empty")
        if not self.created_by_job.strip():
            raise ValueError("created_by_job cannot be empty")
        if not self.claim_id.startswith("clm_"):
            raise ValueError("claim_id must start with clm_")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.truth_verified and self.verification_method is None:
            raise ValueError("truth_verified claims require a verification_method")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        for key in (
            "quantifiers",
            "assumptions",
            "parent_claim_ids",
            "supporting_artifact_hashes",
            "contradicting_artifact_hashes",
        ):
            value[key] = list(value[key])
        return value
