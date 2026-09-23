"""Common result vocabulary for exact and formal tools."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class VerificationStatus(StrEnum):
    PROVEN = "PROVEN"
    DISPROVEN = "DISPROVEN"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    status: VerificationStatus
    job_id: str
    agent_id: str
    summary: str
    event_hash: str
    artifacts: tuple[dict[str, Any], ...]
    exit_code: int | None
    duration_seconds: float
    counterexample: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def evidence_hashes(self) -> tuple[str, ...]:
        return tuple(
            artifact["sha256"]
            for artifact in self.artifacts
            if artifact.get("sha256")
        )

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        value["artifacts"] = list(self.artifacts)
        value["evidence_hashes"] = list(self.evidence_hashes)
        return value
