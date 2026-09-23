"""Lean verifier with placeholder rejection and fail-closed isolation policy."""
from __future__ import annotations

import asyncio
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Literal

from cognition.math_discovery.storage import CampaignStore
from cognition.math_discovery.tools.models import ToolResult, VerificationStatus
from cognition.math_discovery.tools.recording import ToolRecorder


_FORBIDDEN_LEAN = re.compile(
    r"\b(sorry|admit|axiom|unsafe)\b|#eval\b|run_cmd\b|\bIO\.|\bSystem\.",
    flags=re.IGNORECASE,
)


class LeanRunner:
    """Compile a named theorem without accepting placeholders as proof.

    Container execution is the safe default. Local execution must be explicitly
    enabled because a Lean source file can contain executable metaprogramming.
    """

    def __init__(
        self,
        store: CampaignStore,
        *,
        binary: str | None = None,
        lake_binary: str | None = None,
        local_project_dir: Path | str | None = None,
        container_image: str | None = None,
        container_profile: Literal["core", "mathlib"] = "mathlib",
        allow_local: bool = False,
        timeout_seconds: float = 30.0,
        memory_mb: int = 512,
    ):
        if container_profile not in {"core", "mathlib"}:
            raise ValueError("container_profile must be 'core' or 'mathlib'")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if memory_mb < 64:
            raise ValueError("memory_mb must be at least 64")
        self.recorder = ToolRecorder(store)
        self.binary = binary or shutil.which("lean")
        self.lake_binary = lake_binary or shutil.which("lake")
        self.local_project_dir = (
            Path(local_project_dir).resolve() if local_project_dir is not None else None
        )
        self.container_image = container_image
        self.container_profile = container_profile
        self.allow_local = allow_local
        self.timeout_seconds = float(timeout_seconds)
        self.memory_mb = int(memory_mb)

    async def verify(
        self,
        source: str,
        *,
        theorem_name: str,
        job_id: str,
        agent_id: str,
    ) -> ToolResult:
        validation_error = self._validate(source, theorem_name)
        isolation_error = self._isolation_error()
        if validation_error or isolation_error:
            summary = validation_error or isolation_error or "Lean unavailable"
            return self._record_unavailable(
                source,
                theorem_name=theorem_name,
                job_id=job_id,
                agent_id=agent_id,
                summary=summary,
            )

        audited_source = source.rstrip() + f"\n\n#print axioms {theorem_name}\n"
        started = time.monotonic()
        stdout, stderr, exit_code, timed_out, command = await self._invoke(audited_source)
        duration = time.monotonic() - started
        decoded = (stdout + b"\n" + stderr).decode(errors="replace")
        axioms = self._parse_axioms(decoded, theorem_name)
        if timed_out:
            status = VerificationStatus.UNKNOWN
            summary = "Lean compilation timed out"
        elif exit_code == 0 and "sorryAx" not in decoded:
            status = VerificationStatus.PROVEN
            summary = f"Lean compiled {theorem_name} without sorryAx"
        elif exit_code == 0:
            status = VerificationStatus.ERROR
            summary = "Lean output reports the forbidden sorryAx axiom"
        elif self.container_image and (
            exit_code == 125
            or "docker:" in decoded.lower()
            or "error response from daemon" in decoded.lower()
        ):
            status = VerificationStatus.ERROR
            summary = "isolated Lean environment failed before proof checking"
        else:
            status = VerificationStatus.UNKNOWN
            summary = "Lean did not compile the proposed proof"
        return self.recorder.record(
            job_id=job_id,
            agent_id=agent_id,
            tool_name="lean_compile",
            command=command,
            stdin=audited_source.encode(),
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration_seconds=duration,
            status=status,
            summary=summary,
            metadata={
                "theorem_name": theorem_name,
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "audited_source_sha256": hashlib.sha256(
                    audited_source.encode()
                ).hexdigest(),
                "isolation": "docker" if self.container_image else "explicit_local_opt_in",
                "network": "none" if self.container_image else "not isolated",
                "placeholder_policy": "reject sorry, admit, axiom, unsafe and sorryAx",
                "container_identity": self._container_identity(),
                "toolchain_identity": self._toolchain_identity(),
                "reported_axioms": axioms,
            },
        )

    @staticmethod
    def _validate(source: str, theorem_name: str) -> str | None:
        if not source.strip() or len(source.encode()) > 1_000_000:
            return "Lean source must contain 1-1,000,000 bytes"
        if not theorem_name.isidentifier() or theorem_name.startswith("_"):
            return "theorem_name must be a public identifier"
        forbidden = _FORBIDDEN_LEAN.search(source)
        if forbidden:
            return f"Lean source contains forbidden construct: {forbidden.group(0)}"
        declaration = re.compile(rf"\btheorem\s+{re.escape(theorem_name)}\b")
        if declaration.search(source) is None:
            return f"Lean source does not declare theorem {theorem_name}"
        return None

    def _isolation_error(self) -> str | None:
        if self.container_image:
            if shutil.which("docker") is None:
                return "Docker is unavailable for isolated Lean execution"
            return None
        if not self.allow_local:
            return "isolated Lean image is not configured; local execution refused"
        if self.binary is None:
            return "Lean executable is unavailable"
        if self.local_project_dir is not None:
            if not self.local_project_dir.is_dir():
                return "local Lean project directory is unavailable"
            if self.lake_binary is None:
                return "Lake executable is unavailable for the local Lean project"
        return None

    def _record_unavailable(
        self,
        source: str,
        *,
        theorem_name: str,
        job_id: str,
        agent_id: str,
        summary: str,
    ) -> ToolResult:
        return self.recorder.record(
            job_id=job_id,
            agent_id=agent_id,
            tool_name="lean_compile",
            command="lean (execution refused)",
            stdin=source.encode(),
            stdout=b"",
            stderr=summary.encode(),
            exit_code=None,
            duration_seconds=0.0,
            status=VerificationStatus.ERROR,
            summary=summary,
            metadata={
                "theorem_name": theorem_name,
                "isolation": "fail_closed",
                "truth_verified": False,
            },
        )

    async def _invoke(
        self,
        source: str,
    ) -> tuple[bytes, bytes, int | None, bool, str]:
        run_dir = Path(tempfile.mkdtemp(prefix="amy_lean_"))
        source_path = run_dir / "Main.lean"
        source_path.write_text(source, encoding="utf-8")
        if self.container_image:
            argv = [
                "docker",
                "run",
                "--rm",
                "--network=none",
                f"--memory={self.memory_mb}m",
                "--cpus=1",
                "--pids-limit=128",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--read-only",
                "--tmpfs=/tmp:rw,noexec,nosuid,size=64m",
                "-v",
                f"{run_dir.resolve()}:/work:ro",
                "--workdir",
                "/work",
                self.container_image,
            ]
            if self.container_profile == "mathlib":
                argv.extend(
                    ["lake", "--dir=/opt/mathlib", "env", "lean", "/work/Main.lean"]
                )
            else:
                argv.extend(["lean", "/work/Main.lean"])
            env = {key: os.environ[key] for key in ("PATH",) if key in os.environ}
        else:
            assert self.binary is not None
            if self.local_project_dir is not None:
                assert self.lake_binary is not None
                argv = [
                    self.lake_binary,
                    f"--dir={self.local_project_dir}",
                    "env",
                    "lean",
                    str(source_path),
                ]
            else:
                argv = [self.binary, str(source_path)]
            env = {
                key: os.environ[key]
                for key in ("PATH", "HOME", "LANG", "LC_ALL", "LEAN_PATH")
                if key in os.environ
            }
        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                *argv,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=run_dir,
                env=env,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout_seconds,
            )
            return stdout, stderr, proc.returncode, False, " ".join(argv)
        except asyncio.TimeoutError:
            if proc is not None:
                proc.kill()
                await proc.wait()
            return b"", b"process timeout", None, True, " ".join(argv)
        finally:
            shutil.rmtree(run_dir, ignore_errors=True)

    def _container_identity(self) -> str | None:
        if not self.container_image:
            return None
        try:
            result = subprocess.run(
                [
                    "docker",
                    "image",
                    "inspect",
                    self.container_image,
                    "--format={{.Id}}",
                ],
                capture_output=True,
                check=False,
                text=True,
                timeout=3,
            )
        except (OSError, subprocess.SubprocessError):
            return "unknown"
        return result.stdout.strip() or "unknown"

    def _toolchain_identity(self) -> dict[str, str | None]:
        if self.container_image:
            return {
                "execution": "container",
                "profile": self.container_profile,
                "image": self.container_image,
            }
        if not self.binary:
            return {"execution": "local", "binary": None, "sha256": None, "version": None}
        binary_path = Path(self.binary).resolve()
        digest = hashlib.sha256()
        try:
            with binary_path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            binary_sha = digest.hexdigest()
        except OSError:
            binary_sha = "unknown"
        try:
            version = subprocess.run(
                [self.binary, "--version"],
                capture_output=True,
                check=False,
                text=True,
                timeout=3,
                env={key: os.environ[key] for key in ("PATH",) if key in os.environ},
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            version = "unknown"
        return {
            "execution": "explicit_local_opt_in",
            "binary": str(binary_path),
            "sha256": binary_sha,
            "version": version,
            "project": self._project_identity(),
        }

    def _project_identity(self) -> dict[str, str] | None:
        if self.local_project_dir is None:
            return None
        identity: dict[str, str] = {"path": str(self.local_project_dir)}
        for name in ("lean-toolchain", "lakefile.toml", "lake-manifest.json"):
            path = self.local_project_dir / name
            try:
                identity[f"{name}_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                identity[f"{name}_sha256"] = "unavailable"
        return identity

    @staticmethod
    def _parse_axioms(output: str, theorem_name: str) -> list[str] | None:
        no_axioms = re.search(
            rf"['\u2018]?{re.escape(theorem_name)}['\u2019]? does not depend on any axioms",
            output,
        )
        if no_axioms:
            return []
        match = re.search(
            rf"['\u2018]?{re.escape(theorem_name)}['\u2019]? depends on axioms:\s*\[([^]]*)\]",
            output,
        )
        if not match:
            return None
        return [item.strip() for item in match.group(1).split(",") if item.strip()]
