"""Shared conversion from one tool execution to retained campaign evidence."""
from __future__ import annotations

from typing import Any

from cognition.math_discovery.provenance import CampaignProvenance
from cognition.math_discovery.storage import CampaignStore
from cognition.math_discovery.tools.models import ToolResult, VerificationStatus


class ToolRecorder:
    def __init__(self, store: CampaignStore):
        self.provenance = CampaignProvenance(store)

    def record(
        self,
        *,
        job_id: str,
        agent_id: str,
        tool_name: str,
        command: str,
        stdin: bytes,
        stdout: bytes,
        stderr: bytes,
        exit_code: int | None,
        duration_seconds: float,
        status: VerificationStatus,
        summary: str,
        counterexample: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> ToolResult:
        retained_metadata = dict(metadata or {})
        retained_metadata["summary"] = summary
        retained_metadata["counterexample"] = counterexample
        # A tool may prove its exact input without proving the campaign's broader
        # natural-language claim. Claim truth is promoted only by the ledger gates.
        retained_metadata["result_verified"] = status is VerificationStatus.PROVEN
        retained_metadata["counterexample_verified"] = (
            status is VerificationStatus.DISPROVEN and counterexample is not None
        )
        retained_metadata["result_decisive"] = status in {
            VerificationStatus.PROVEN,
            VerificationStatus.DISPROVEN,
        }
        retained_metadata.setdefault("truth_verified", False)
        event = self.provenance.record_tool_call(
            job_id=job_id,
            agent_id=agent_id,
            tool_name=tool_name,
            command=command,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration_seconds=duration_seconds,
            result_status=status.value,
            metadata=retained_metadata,
        )
        return ToolResult(
            tool_name=tool_name,
            status=status,
            job_id=job_id,
            agent_id=agent_id,
            summary=summary,
            event_hash=event["event_hash"],
            artifacts=tuple(event["payload"]["artifacts"]),
            exit_code=exit_code,
            duration_seconds=duration_seconds,
            counterexample=counterexample,
            metadata=retained_metadata,
        )
