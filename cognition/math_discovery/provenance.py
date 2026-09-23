"""Full-trajectory provenance for model and tool work in one campaign."""
from __future__ import annotations

from typing import Any

from cognition.math_discovery.storage import CampaignStore


class CampaignProvenance:
    def __init__(self, store: CampaignStore):
        self.store = store

    def record_llm_call(
        self,
        *,
        job_id: str,
        agent_id: str,
        role: str,
        phase: str,
        model: str,
        model_digest: str,
        parameters: dict[str, Any],
        system_prompt: str,
        user_prompt: str,
        raw_response: str,
        normalized_response: str | None,
        usage: dict[str, Any],
        latency_seconds: float,
        attempt: int,
    ) -> dict[str, Any]:
        artifacts = [
            self.store.artifacts.write(
                f"{job_id}-system-prompt.txt",
                system_prompt.encode("utf-8"),
                "text/plain",
            ),
            self.store.artifacts.write(
                f"{job_id}-user-prompt.txt",
                user_prompt.encode("utf-8"),
                "text/plain",
            ),
            self.store.artifacts.write(
                f"{job_id}-raw-response.txt",
                raw_response.encode("utf-8"),
                "text/plain",
            ),
        ]
        if normalized_response is not None:
            artifacts.append(
                self.store.artifacts.write(
                    f"{job_id}-normalized-response.json",
                    normalized_response.encode("utf-8"),
                    "application/json",
                )
            )
        return self.store.event_log.append(
            "llm_call",
            {
                "job_id": job_id,
                "agent_id": agent_id,
                "role": role,
                "phase": phase,
                "model": model,
                "model_digest": model_digest,
                "parameters": parameters,
                "usage": usage,
                "latency_seconds": latency_seconds,
                "attempt": attempt,
                "artifacts": artifacts,
                "truth_verified": False,
            },
            actor=agent_id,
        )

    def record_tool_call(
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
        result_status: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        artifacts = [
            self.store.artifacts.write(f"{job_id}-stdin.bin", stdin, "application/octet-stream"),
            self.store.artifacts.write(f"{job_id}-stdout.bin", stdout, "application/octet-stream"),
            self.store.artifacts.write(f"{job_id}-stderr.bin", stderr, "application/octet-stream"),
        ]
        return self.store.event_log.append(
            "tool_call",
            {
                "job_id": job_id,
                "agent_id": agent_id,
                "tool_name": tool_name,
                "command": command,
                "exit_code": exit_code,
                "duration_seconds": duration_seconds,
                "result_status": result_status,
                "metadata": metadata or {},
                "artifacts": artifacts,
                "truth_verified": False,
            },
            actor=agent_id,
        )

    def verify(self) -> dict[str, Any]:
        from cognition.math_discovery.ledger import CampaignLedger

        manifest_result = self.store.verify_manifest()
        event_result = self.store.event_log.verify()
        ledger_result = CampaignLedger(self.store).verify()
        artifact_errors: list[str] = []
        artifact_count = 0
        if event_result["integrity_verified"]:
            for event in self.store.event_log.records():
                for artifact in event.get("payload", {}).get("artifacts", []):
                    artifact_count += 1
                    valid, error = self.store.artifacts.verify(artifact)
                    if not valid:
                        artifact_errors.append(
                            f"event {event.get('sequence')} artifact {artifact.get('path')}: {error}"
                        )
        integrity = (
            manifest_result["integrity_verified"]
            and event_result["integrity_verified"]
            and ledger_result["integrity_verified"]
            and not artifact_errors
        )
        return {
            "integrity_verified": integrity,
            "manifest": manifest_result,
            "event_chain": event_result,
            "ledger_chain": ledger_result,
            "artifact_count": artifact_count,
            "artifact_errors": artifact_errors,
            "truth_verified": False,
        }
