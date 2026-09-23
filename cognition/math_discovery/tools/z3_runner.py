"""Z3 subprocess adapter with explicit UNSAT-as-proof semantics."""
from __future__ import annotations

import asyncio
import hashlib
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from cognition.math_discovery.storage import CampaignStore
from cognition.math_discovery.tools.models import ToolResult, VerificationStatus
from cognition.math_discovery.tools.recording import ToolRecorder


_FORBIDDEN_COMMANDS = re.compile(
    r"\((check-sat|get-model|get-proof|exit|reset|push|pop|set-option|include)\b",
    flags=re.IGNORECASE,
)
_RESULT_TOKENS = {"sat", "unsat", "unknown"}


class Z3Runner:
    def __init__(
        self,
        store: CampaignStore,
        *,
        binary: str | None = None,
        timeout_seconds: float = 10.0,
        memory_mb: int = 256,
    ):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if memory_mb < 32:
            raise ValueError("memory_mb must be at least 32")
        self.recorder = ToolRecorder(store)
        self.binary = binary or shutil.which("z3")
        self.timeout_seconds = float(timeout_seconds)
        self.memory_mb = int(memory_mb)

    async def prove_unsat(
        self,
        smt2_assertions: str,
        *,
        job_id: str,
        agent_id: str,
    ) -> ToolResult:
        validation_error = self._validate(smt2_assertions)
        binary_available = self.binary is not None and Path(self.binary).is_file()
        if validation_error or not binary_available:
            summary = validation_error or "z3 executable is unavailable"
            return self.recorder.record(
                job_id=job_id,
                agent_id=agent_id,
                tool_name="z3_unsat_check",
                command=self.binary or "z3 (unavailable)",
                stdin=smt2_assertions.encode(),
                stdout=b"",
                stderr=summary.encode(),
                exit_code=None,
                duration_seconds=0.0,
                status=VerificationStatus.ERROR,
                summary=summary,
                metadata={"proof_semantics": "negated claim must be UNSAT"},
            )

        timeout_ms = max(1, int(self.timeout_seconds * 1000))
        base = (
            f"(set-option :timeout {timeout_ms})\n"
            f"(set-option :memory_max_size {self.memory_mb})\n"
            f"{smt2_assertions.rstrip()}\n"
        )
        started = time.monotonic()
        first = await self._invoke(base + "(check-sat)\n")
        combined_stdout = first[0]
        combined_stderr = first[1]
        exit_code = first[2]
        timed_out = first[3]
        token = self._result_token(combined_stdout)
        counterexample = None
        if not timed_out and token == "sat":
            second = await self._invoke(base + "(check-sat)\n(get-model)\n")
            combined_stdout += b"\n--- model rerun ---\n" + second[0]
            combined_stderr += b"\n" + second[1]
            exit_code = second[2]
            timed_out = second[3]
            if not timed_out:
                counterexample = second[0].decode(errors="replace").strip()
        duration = time.monotonic() - started

        if timed_out:
            status = VerificationStatus.UNKNOWN
            summary = "z3 timed out; satisfiability is unknown"
        elif token == "unsat" and exit_code == 0:
            status = VerificationStatus.PROVEN
            summary = "negated claim is UNSAT"
        elif token == "sat" and exit_code == 0:
            status = VerificationStatus.DISPROVEN
            summary = "negated claim is SAT; counterexample model retained"
        elif token == "unknown" and exit_code == 0:
            status = VerificationStatus.UNKNOWN
            summary = "z3 returned unknown"
        else:
            status = VerificationStatus.ERROR
            summary = "z3 returned an invalid or failed result"

        binary_path = Path(self.binary)
        digest = hashlib.sha256()
        try:
            with binary_path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            binary_digest = digest.hexdigest()
        except OSError:
            binary_digest = "unknown"
        version = "unknown"
        if not timed_out:
            try:
                version = subprocess.run(
                    [self.binary, "-version"],
                    capture_output=True,
                    check=False,
                    text=True,
                    timeout=2,
                    env={key: os.environ[key] for key in ("PATH",) if key in os.environ},
                ).stdout.strip()
            except (OSError, subprocess.SubprocessError):
                pass
        return self.recorder.record(
            job_id=job_id,
            agent_id=agent_id,
            tool_name="z3_unsat_check",
            command=f"{self.binary} -in -smt2",
            stdin=(base + "(check-sat)\n").encode(),
            stdout=combined_stdout,
            stderr=combined_stderr,
            exit_code=exit_code,
            duration_seconds=duration,
            status=status,
            summary=summary,
            counterexample=counterexample,
            metadata={
                "proof_semantics": "negated claim must be UNSAT",
                "binary_sha256": binary_digest,
                "version": version,
                "timeout_seconds": self.timeout_seconds,
                "memory_mb": self.memory_mb,
                "caller_assertions_sha256": hashlib.sha256(
                    smt2_assertions.encode()
                ).hexdigest(),
                "model_query_sha256": (
                    hashlib.sha256((base + "(check-sat)\n(get-model)\n").encode()).hexdigest()
                    if token == "sat"
                    else None
                ),
                "network": "tool has no network interface",
            },
        )

    @staticmethod
    def _validate(source: str) -> str | None:
        if not source.strip() or len(source.encode()) > 1_000_000:
            return "SMT-LIB assertions must contain 1-1,000,000 bytes"
        match = _FORBIDDEN_COMMANDS.search(source)
        if match:
            return f"caller-supplied command is forbidden: {match.group(1).lower()}"
        return None

    @staticmethod
    def _result_token(stdout: bytes) -> str:
        """Extract one solver result while retaining harmless diagnostic lines.

        Some Z3 builds print ``unsupported`` before ``unknown`` when they ignore a
        logic declaration. Conflicting or repeated result tokens remain invalid.
        """
        tokens = [
            line.strip().lower()
            for line in stdout.decode(errors="replace").splitlines()
            if line.strip().lower() in _RESULT_TOKENS
        ]
        return tokens[0] if len(tokens) == 1 else ""

    async def _invoke(self, source: str) -> tuple[bytes, bytes, int | None, bool]:
        run_dir = tempfile.mkdtemp(prefix="amy_z3_")
        env = {
            key: value
            for key, value in os.environ.items()
            if key in {"PATH", "LANG", "LC_ALL"}
        }
        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                self.binary,
                "-in",
                "-smt2",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=run_dir,
                env=env,
                start_new_session=os.name == "posix",
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(source.encode()),
                timeout=self.timeout_seconds + 1.0,
            )
            return stdout, stderr, proc.returncode, False
        except asyncio.TimeoutError:
            if proc is not None:
                if os.name == "posix":
                    os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
                await proc.wait()
            return b"", b"process timeout", None, True
        finally:
            shutil.rmtree(run_dir, ignore_errors=True)
