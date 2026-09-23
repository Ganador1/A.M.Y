"""Restartable dependency scheduler for three mathematical research slots."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from cognition.math_discovery.models import (
    JOB_TERMINAL_STATUSES,
    JobResult,
    JobStatus,
    ResearchJob,
)
from cognition.math_discovery.policies import ROLE_POLICIES
from cognition.math_discovery.storage import CampaignStore


@dataclass
class JobState:
    job: ResearchJob
    status: JobStatus = JobStatus.PENDING
    attempts: int = 0
    result: dict[str, Any] | None = None
    error: str | None = None


class CampaignScheduler:
    def __init__(
        self,
        store: CampaignStore,
        worker: Any,
        *,
        max_slots: int = 3,
        scheduler_id: str = "scheduler",
    ):
        if not 1 <= max_slots <= 3:
            raise ValueError("max_slots must be between 1 and 3")
        self.store = store
        self.worker = worker
        self.max_slots = max_slots
        self.scheduler_id = scheduler_id
        self.peak_active = 0
        self._active_count = 0

    def submit(self, jobs: list[ResearchJob]) -> None:
        existing = self.states()
        combined = {**{job_id: state.job for job_id, state in existing.items()}}
        for job in jobs:
            prior = combined.get(job.job_id)
            if prior is not None:
                if prior != job:
                    raise ValueError(f"conflicting definition for {job.job_id}")
                continue
            combined[job.job_id] = job
        for job in jobs:
            missing = [dep for dep in job.dependencies if dep not in combined]
            if missing:
                raise ValueError(f"{job.job_id} has unknown dependencies: {missing}")
        self._assert_acyclic(combined)
        for job in jobs:
            if job.job_id not in existing:
                self.store.event_log.append(
                    "job_created",
                    {"job": job.to_dict()},
                    actor=self.scheduler_id,
                )

    @staticmethod
    def _assert_acyclic(jobs: dict[str, ResearchJob]) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(job_id: str) -> None:
            if job_id in visiting:
                raise ValueError(f"job dependency cycle at {job_id}")
            if job_id in visited:
                return
            visiting.add(job_id)
            for dependency in jobs[job_id].dependencies:
                visit(dependency)
            visiting.remove(job_id)
            visited.add(job_id)

        for job_id in jobs:
            visit(job_id)

    def states(self) -> dict[str, JobState]:
        states: dict[str, JobState] = {}
        for event in self.store.event_log.records():
            event_type = event.get("event_type")
            payload = event.get("payload", {})
            if event_type == "job_created":
                job = ResearchJob.from_dict(payload["job"])
                if job.job_id in states:
                    raise ValueError(f"duplicate job creation: {job.job_id}")
                states[job.job_id] = JobState(job=job)
            elif event_type == "job_started":
                state = states[payload["job_id"]]
                if state.status is not JobStatus.PENDING:
                    raise ValueError(f"cannot start {state.job.job_id} from {state.status}")
                state.status = JobStatus.RUNNING
                state.attempts = int(payload["attempt"])
            elif event_type == "job_requeued":
                state = states[payload["job_id"]]
                if state.status is not JobStatus.RUNNING:
                    raise ValueError(f"cannot requeue {state.job.job_id} from {state.status}")
                state.status = JobStatus.PENDING
                state.error = payload.get("error")
            elif event_type == "job_completed":
                state = states[payload["job_id"]]
                if state.status is not JobStatus.RUNNING:
                    raise ValueError(f"cannot complete {state.job.job_id} from {state.status}")
                state.status = JobStatus.COMPLETED
                state.result = payload["result"]
            elif event_type == "job_failed":
                state = states[payload["job_id"]]
                if state.status is not JobStatus.RUNNING:
                    raise ValueError(f"cannot fail {state.job.job_id} from {state.status}")
                state.status = JobStatus.FAILED
                state.error = payload.get("error")
            elif event_type == "job_cancelled":
                state = states[payload["job_id"]]
                if state.status in JOB_TERMINAL_STATUSES:
                    raise ValueError(f"cannot cancel terminal job {state.job.job_id}")
                state.status = JobStatus.CANCELLED
                state.error = payload.get("reason")
        return states

    def recover_interrupted(self) -> int:
        recovered = 0
        for state in self.states().values():
            if state.status is JobStatus.RUNNING:
                if state.attempts >= state.job.max_attempts:
                    self.store.event_log.append(
                        "job_failed",
                        {
                            "job_id": state.job.job_id,
                            "attempt": state.attempts,
                            "error": "interrupted attempt exhausted retry budget",
                        },
                        actor=self.scheduler_id,
                    )
                else:
                    self.store.event_log.append(
                        "job_requeued",
                        {
                            "job_id": state.job.job_id,
                            "attempt": state.attempts,
                            "error": "scheduler restarted before terminal event",
                        },
                        actor=self.scheduler_id,
                    )
                    recovered += 1
        return recovered

    async def run(self) -> dict[str, Any]:
        recovered = self.recover_interrupted()
        active: dict[asyncio.Task, str] = {}
        while True:
            states = self.states()
            self._cancel_blocked_dependencies(states)
            states = self.states()
            ready = sorted(
                (
                    state
                    for state in states.values()
                    if state.status is JobStatus.PENDING
                    and all(
                        states[dep].status is JobStatus.COMPLETED
                        for dep in state.job.dependencies
                    )
                ),
                key=lambda state: (state.job.priority, state.job.job_id),
            )
            while ready and len(active) < self.max_slots:
                state = ready.pop(0)
                task = asyncio.create_task(self._execute(state.job))
                active[task] = state.job.job_id
            if not active:
                final_states = self.states()
                pending = [
                    state.job.job_id
                    for state in final_states.values()
                    if state.status is JobStatus.PENDING
                ]
                if pending:
                    raise RuntimeError(f"scheduler deadlock; pending jobs: {pending}")
                return self.summary(recovered=recovered)
            done, _pending = await asyncio.wait(
                active,
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in done:
                active.pop(task)
                # _execute retains failures as events; unexpected scheduler defects
                # still surface and stop the campaign.
                await task

    async def _execute(self, job: ResearchJob) -> None:
        state = self.states()[job.job_id]
        attempt = state.attempts + 1
        self.store.event_log.append(
            "job_started",
            {"job_id": job.job_id, "attempt": attempt},
            actor=job.agent_id,
        )
        dependency_hashes = self._dependency_artifact_hashes(job)
        self._active_count += 1
        self.peak_active = max(self.peak_active, self._active_count)
        try:
            result: JobResult = await self.worker.run(
                job,
                attempt=attempt,
                dependency_artifact_hashes=dependency_hashes,
            )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            if attempt < job.max_attempts:
                self.store.event_log.append(
                    "job_requeued",
                    {"job_id": job.job_id, "attempt": attempt, "error": error},
                    actor=self.scheduler_id,
                )
            else:
                self.store.event_log.append(
                    "job_failed",
                    {"job_id": job.job_id, "attempt": attempt, "error": error},
                    actor=self.scheduler_id,
                )
            return
        finally:
            self._active_count -= 1
        self.store.event_log.append(
            "job_completed",
            {"job_id": job.job_id, "attempt": attempt, "result": result.to_dict()},
            actor=job.agent_id,
        )
        if (
            result.parsed.get("refutes_branch") is True
            and ROLE_POLICIES[job.role].may_refute_branch
        ):
            self.cancel_branch(
                job.branch_id,
                exclude={job.job_id},
                reason=f"branch refuted by {job.job_id}",
            )

    def _dependency_artifact_hashes(self, job: ResearchJob) -> tuple[str, ...]:
        states = self.states()
        hashes = []
        for dependency in job.dependencies:
            result = states[dependency].result or {}
            artifact = result.get("output_artifact", {})
            if artifact.get("sha256"):
                hashes.append(artifact["sha256"])
        return tuple(hashes)

    def _cancel_blocked_dependencies(self, states: dict[str, JobState]) -> None:
        for state in states.values():
            if state.status is not JobStatus.PENDING:
                continue
            blockers = [
                dep
                for dep in state.job.dependencies
                if states[dep].status in {JobStatus.FAILED, JobStatus.CANCELLED}
            ]
            if blockers:
                self.store.event_log.append(
                    "job_cancelled",
                    {
                        "job_id": state.job.job_id,
                        "reason": f"dependency did not complete: {', '.join(blockers)}",
                    },
                    actor=self.scheduler_id,
                )

    def cancel_branch(
        self,
        branch_id: str,
        *,
        exclude: set[str] | None = None,
        reason: str,
    ) -> int:
        excluded = exclude or set()
        cancelled = 0
        for state in self.states().values():
            if (
                state.job.branch_id == branch_id
                and state.job.job_id not in excluded
                and state.status is JobStatus.PENDING
            ):
                self.store.event_log.append(
                    "job_cancelled",
                    {"job_id": state.job.job_id, "reason": reason},
                    actor=self.scheduler_id,
                )
                cancelled += 1
        return cancelled

    def summary(self, *, recovered: int = 0) -> dict[str, Any]:
        states = self.states()
        counts = {
            status.value: sum(state.status is status for state in states.values())
            for status in JobStatus
        }
        return {
            "campaign_id": self.store.campaign_id,
            "jobs": len(states),
            "status_counts": counts,
            "peak_scheduler_slots": self.peak_active,
            "recovered_interrupted_jobs": recovered,
            "integrity_verified": self.store.event_log.verify()["integrity_verified"],
            "truth_verified": False,
        }

