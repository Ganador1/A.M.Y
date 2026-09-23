"""Finite integer enumeration using a validated expression and isolated Python."""
from __future__ import annotations

import ast
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from typing import Any

from cognition.math_discovery.storage import CampaignStore, canonical_json_bytes
from cognition.math_discovery.tools.models import ToolResult, VerificationStatus
from cognition.math_discovery.tools.recording import ToolRecorder
from sandbox.executor import SandboxExecutor


_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Mod,
    ast.FloorDiv,
    ast.UnaryOp,
    ast.Not,
    ast.USub,
    ast.UAdd,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Name,
    ast.Load,
    ast.Constant,
)


@dataclass(frozen=True)
class FiniteEnumerationSpec:
    predicate: str
    lower: int
    upper: int
    variable: str = "n"
    max_cases: int = 1_000_000

    def __post_init__(self) -> None:
        if not self.variable.isidentifier() or self.variable.startswith("_"):
            raise ValueError("variable must be a public Python identifier")
        if self.upper < self.lower:
            raise ValueError("upper must be greater than or equal to lower")
        cases = self.upper - self.lower + 1
        if self.max_cases < 1 or cases > self.max_cases:
            raise ValueError(f"enumeration has {cases} cases; maximum is {self.max_cases}")
        if not self.predicate.strip() or len(self.predicate) > 2000:
            raise ValueError("predicate must contain 1-2000 characters")
        tree = ast.parse(self.predicate, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, _ALLOWED_NODES):
                raise ValueError(f"predicate contains forbidden syntax: {type(node).__name__}")
            if isinstance(node, ast.Name) and node.id != self.variable:
                raise ValueError(f"predicate may only reference {self.variable!r}")
            if isinstance(node, ast.Constant) and not isinstance(node.value, (int, bool)):
                raise ValueError("predicate constants must be integers or booleans")


class ExactComputationRunner:
    def __init__(
        self,
        store: CampaignStore,
        *,
        executor: Any | None = None,
        timeout_seconds: float = 30.0,
        memory_mb: int = 256,
    ):
        self.recorder = ToolRecorder(store)
        self.timeout_seconds = float(timeout_seconds)
        self.memory_mb = int(memory_mb)
        self.executor = executor or SandboxExecutor(
            {
                "max_execution_time": self.timeout_seconds,
                "max_memory_mb": self.memory_mb,
                "use_docker": True,
                "require_isolation": True,
                "allow_network": False,
                "allow_subprocess": False,
            }
        )

    async def run(
        self,
        spec: FiniteEnumerationSpec,
        *,
        job_id: str,
        agent_id: str,
    ) -> ToolResult:
        script = self._script(spec)
        spec_bytes = canonical_json_bytes(asdict(spec))
        started = time.monotonic()
        execution = await self.executor.execute(script, language="python")
        duration = time.monotonic() - started
        stdout = str(execution.get("stdout", "")).encode()
        stderr = str(execution.get("stderr", "")).encode()
        status, summary, counterexample = self._interpret(execution)
        return self.recorder.record(
            job_id=job_id,
            agent_id=agent_id,
            tool_name="exact_python_finite_enumeration",
            command=(
                "docker run --rm --network=none --cpus=1 --pids-limit=128 "
                "--cap-drop=ALL --security-opt=no-new-privileges --read-only "
                f"--memory={self.memory_mb}m amy-sandbox:latest python /work/script.py"
            ),
            stdin=script.encode(),
            stdout=stdout,
            stderr=stderr,
            exit_code=execution.get("return_code"),
            duration_seconds=duration,
            status=status,
            summary=summary,
            counterexample=counterexample,
            metadata={
                "scope": "finite_integer_interval",
                "lower": spec.lower,
                "upper": spec.upper,
                "checked_cases": spec.upper - spec.lower + 1,
                "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
                "harness_sha256": hashlib.sha256(script.encode()).hexdigest(),
                "isolation": "docker",
                "network": "none",
                "image": execution.get("image", "amy-sandbox:latest"),
                "image_id": execution.get("image_id", "unknown"),
                "universal_claim_verified": False,
            },
        )

    @staticmethod
    def _script(spec: FiniteEnumerationSpec) -> str:
        return (
            "import json\n"
            f"for {spec.variable} in range({spec.lower!r}, {spec.upper + 1!r}):\n"
            f"    if not ({spec.predicate}):\n"
            "        print(json.dumps({'status': 'DISPROVEN', "
            f"'counterexample': {{{spec.variable!r}: {spec.variable}}}, "
            "'summary': 'counterexample found'}, sort_keys=True))\n"
            "        raise SystemExit(0)\n"
            "print(json.dumps({'status': 'PROVEN', 'counterexample': None, "
            "'summary': 'all bounded cases passed'}, sort_keys=True))\n"
        )

    @staticmethod
    def _interpret(execution: dict[str, Any]) -> tuple[VerificationStatus, str, Any]:
        stdout = str(execution.get("stdout", ""))
        if execution.get("success"):
            try:
                payload = json.loads(stdout.strip().splitlines()[-1])
                status = VerificationStatus(payload["status"])
                if status not in {VerificationStatus.PROVEN, VerificationStatus.DISPROVEN}:
                    raise ValueError("unexpected exact result")
                return status, str(payload["summary"]), payload.get("counterexample")
            except (IndexError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                return VerificationStatus.ERROR, f"invalid harness output: {exc}", None
        error = str(execution.get("stderr", ""))
        if "timeout" in error.lower():
            return VerificationStatus.UNKNOWN, error or "exact computation timed out", None
        return VerificationStatus.ERROR, error or "exact computation failed", None
