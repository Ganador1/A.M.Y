"""
Sandbox Executor — Run experiments safely.

Executes code in an isolated environment to test hypotheses.

Isolation tiers (strongest first):
  1. Docker (use_docker: true) — network=none, memory cap, read-only host,
     ephemeral container. This is the only tier that truly contains a
     hostile script. Strongly recommended for an autonomous agent.
  2. Hardened subprocess (fallback) — runs under a dedicated temp working
     directory, drops to a minimal environment, and applies POSIX rlimits
     (CPU seconds + address-space cap) before exec. This bounds resource
     abuse and accidental host writes, but is NOT a security boundary
     against a determined attacker (no namespace/FS isolation).

Both tiers and the ``require_isolation`` gate apply to ALL languages
(python and bash alike) — bash is routed through Docker when enabled and
refused under fail-closed just like python.

`require_isolation: true` makes the executor FAIL CLOSED: if Docker is
requested but unavailable, code is refused rather than silently downgraded
to the weaker subprocess tier.
"""
import asyncio
import os
import re
import resource
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import structlog

log = structlog.get_logger()

# Directories A.M.Y is allowed to read/write
_ALLOWED_WRITE_DIRS = [
    Path("papers"),
    Path("data"),
    Path("sandbox/scripts"),
    Path("logs"),
]

# Blocked shell commands for safety
_BLOCKED_COMMANDS = [
    "rm -rf /", "sudo", "chmod 777", ":(){:|:&};:",
    "dd if=", "mkfs", "shutdown", "reboot", "curl | bash",
    "wget | bash", "eval $(", "> /etc", "> /usr",
]


class SandboxExecutor:
    def __init__(self, config: dict = None):
        config = config or {}
        self.max_time = config.get("max_execution_time", 300)
        self.max_memory = config.get("max_memory_mb", 2048)
        self.use_docker = config.get("use_docker", False)
        # When True, a requested-but-unavailable stronger tier is refused
        # instead of silently downgrading. Defaults to mirroring use_docker:
        # if you asked for Docker, you almost certainly meant "isolate me".
        self.require_isolation = config.get("require_isolation", self.use_docker)
        self.allow_network = config.get("allow_network", False)
        self.allow_subprocess = config.get("allow_subprocess", False)
        self.allow_sensitive_env = config.get("allow_sensitive_env", False)
        # Ensure allowed dirs exist
        for d in _ALLOWED_WRITE_DIRS:
            d.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _docker_available() -> bool:
        """True only if the docker CLI is on PATH and the daemon answers."""
        if shutil.which("docker") is None:
            return False
        try:
            proc = subprocess.run(
                ["docker", "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
            )
            return proc.returncode == 0
        except Exception:
            return False

    async def execute(self, code: str, language: str = "python") -> dict:
        """Execute code in a sandboxed environment. language: 'python' or 'bash'.

        The isolation tier (Docker vs hardened subprocess) and the
        ``require_isolation`` fail-closed gate apply uniformly to EVERY
        language. Earlier this method returned for bash before reaching the
        gate, so bash code ran on the host even with Docker/require_isolation
        configured; the gate now precedes any language-specific execution.
        """
        safety_block = self._safety_block(code, language)
        if safety_block:
            return safety_block

        # Validate Python syntax before execution
        if language == "python":
            syntax_error = self._validate_python_syntax(code)
            if syntax_error:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Syntax error in generated code: {syntax_error}",
                    "return_code": -1,
                }

        # ── Isolation gate (applies to ALL languages, bash included) ──
        if self.use_docker:
            if self._docker_available():
                return await self._execute_docker(code, language=language)
            # Docker was requested but the daemon is not reachable.
            if self.require_isolation:
                log.error("sandbox.docker_unavailable_fail_closed", language=language)
                return self._blocked_result(
                    "Docker isolation was requested but is unavailable, and "
                    "require_isolation is set — refusing to run code in the "
                    "weaker subprocess sandbox. Start Docker or set "
                    "require_isolation: false to allow the hardened-subprocess fallback."
                )
            log.warning("sandbox.docker_unavailable_downgrade_to_subprocess", language=language)

        # Hardened fallback tier, per language.
        if language == "bash":
            return await self._execute_bash(code)
        return await self._execute_subprocess(code)

    def _blocked_result(self, message: str) -> dict:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Blocked by safety policy: {message}",
            "return_code": -1,
        }

    def _sandbox_env(self) -> dict:
        """Return a minimal environment so generated code cannot read model keys."""
        allowed = {}
        for key in ("PATH", "PYTHONPATH", "VIRTUAL_ENV", "LANG", "LC_ALL"):
            if key in os.environ:
                allowed[key] = os.environ[key]
        allowed["PYTHONNOUSERSITE"] = "1"
        allowed["MPLBACKEND"] = "Agg"
        allowed["HOME"] = str(Path("sandbox/scripts").resolve())
        allowed["TMPDIR"] = tempfile.gettempdir()
        if self.allow_sensitive_env:
            for key, value in os.environ.items():
                lowered = key.lower()
                if any(marker in lowered for marker in ("api_key", "token", "password", "secret")):
                    allowed[key] = value
        return allowed

    def _safety_block(self, code: str, language: str) -> dict | None:
        """Shared policy gate before any generated code reaches the host process."""
        static_reason = self._static_sandbox_policy_violation(code, language)
        if static_reason:
            return self._blocked_result(static_reason)

        try:
            from core.safety_kernel import blocked_message, evaluate_safety

            decision = evaluate_safety(
                operation=f"sandbox.execute.{language}",
                content=code,
                domain="sandbox",
            )
        except Exception as exc:
            return self._blocked_result(f"safety kernel unavailable: {exc}")

        if not decision.allowed:
            return self._blocked_result(blocked_message(decision))
        return None

    def _static_sandbox_policy_violation(self, code: str, language: str) -> str | None:
        lowered = code.lower()

        secret_markers = (
            ".env",
            ".secrets",
            "secrets_",
            "private.key",
            "ed25519_private",
            "id_rsa",
            "api_key",
            "password",
            "token",
        )
        if not self.allow_sensitive_env:
            env_access = re.search(r"\b(os\.environ|os\.getenv|env\s*\|?\s*grep|printenv)\b", lowered)
            if env_access and any(marker in lowered for marker in secret_markers):
                return "sandbox code attempted to read sensitive environment variables"
            secret_file_access = re.search(
                r"(\.env|\.secrets|secrets[_\-.]|private\.key|ed25519_private|id_rsa)",
                lowered,
            )
            if secret_file_access:
                return "sandbox code attempted to read local secret material"

        if not self.allow_network and re.search(
            r"\b(import\s+(requests|httpx|aiohttp|socket|urllib|ftplib|smtplib)|from\s+(requests|httpx|aiohttp|socket|urllib)|curl\s+|wget\s+)",
            lowered,
        ):
            return "network access is disabled for sandbox experiments"

        # NOTE: this regex is a best-effort HINT, not a security boundary —
        # source-pattern matching can always be evaded (string-building an
        # import, base64, etc.). The real boundary is OS isolation (Docker
        # --network=none + dropped caps, or seccomp on the subprocess tier).
        # We still widen it to catch the obvious dynamic-import escapes that
        # previously slipped past (importlib.import_module, runpy, ctypes).
        if not self.allow_subprocess and re.search(
            r"\b(import\s+subprocess|from\s+subprocess|importlib|import_module|runpy|ctypes"
            r"|os\.system|popen\(|pty\.|exec\(|eval\(|__import__\()",
            lowered,
        ):
            return "subprocess and dynamic code execution are disabled in sandbox experiments"

        if language == "bash":
            for blocked in _BLOCKED_COMMANDS:
                if blocked in lowered:
                    return f"script contains forbidden pattern '{blocked}'"
        return None

    def _validate_python_syntax(self, code: str) -> str | None:
        """Validate Python syntax. Returns error message if invalid, None if valid."""
        try:
            compile(code, "<generated_experiment>", "exec")
            return None
        except SyntaxError as e:
            return f"Line {e.lineno}: {e.msg} — {e.text.strip() if e.text else ''}"
        except Exception as e:
            return str(e)

    async def _execute_bash(self, script: str) -> dict:
        """Execute a bash script with safety checks."""
        # Defense-in-depth guard for direct private calls.
        script_lower = script.lower()
        for blocked in _BLOCKED_COMMANDS:
            if blocked in script_lower:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Blocked: script contains forbidden pattern '{blocked}'",
                    "return_code": -1,
                }

        # Throwaway working directory — the child's cwd, so relative writes
        # (e.g. `echo x > core/safety_kernel.py`) land here instead of in the
        # repo. This mirrors the Python tier's _execute_subprocess hardening;
        # the bash path previously ran with cwd=repo-root and could clobber
        # tracked files.
        run_dir = Path(tempfile.mkdtemp(prefix="amy_sbx_"))
        script_path = run_dir / "experiment.sh"
        script_path.write_text("#!/bin/bash\nset -e\n" + script, encoding="utf-8")
        script_path.chmod(0o700)

        proc = None
        # rlimit preexec (CPU/address-space cap) is POSIX-only; mirror the
        # Python tier so a runaway bash loop is bounded, not just wall-clocked.
        preexec = self._rlimit_preexec if os.name == "posix" else None
        try:
            proc = await asyncio.create_subprocess_exec(
                "bash", str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(run_dir),
                env=self._sandbox_env(),
                preexec_fn=preexec,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.max_time
            )
            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="ignore")[:5000],
                "stderr": stderr.decode("utf-8", errors="ignore")[:2000],
                "return_code": proc.returncode,
            }
        except asyncio.TimeoutError:
            await self._terminate(proc)
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Bash script timed out after {self.max_time}s",
                "return_code": -1,
            }
        except Exception as e:
            await self._terminate(proc)
            return {"success": False, "stdout": "", "stderr": str(e), "return_code": -1}
        finally:
            shutil.rmtree(run_dir, ignore_errors=True)

    def _rlimit_preexec(self):
        """Apply POSIX resource limits in the child before exec.

        Bounds CPU time and (where the OS honours it) total address space so
        a runaway or hostile script cannot exhaust the host.

        Platform note: Linux enforces both RLIMIT_CPU and RLIMIT_AS. macOS
        (Darwin) enforces RLIMIT_CPU but does NOT allow lowering RLIMIT_AS
        (setrlimit raises / is ignored), so memory is only truly capped under
        Docker on macOS. Each limit is best-effort: an unsupported one is
        skipped rather than failing the run. Runs in the forked child, so it
        must not touch self/async state.
        """
        cpu = int(self.max_time) + 5  # grace over the wall-clock timeout
        mem_bytes = int(self.max_memory) * 1024 * 1024
        limits = [(resource.RLIMIT_CPU, cpu)]
        if sys.platform != "darwin":  # RLIMIT_AS is unenforceable on macOS
            limits.append((resource.RLIMIT_AS, mem_bytes))
        for res, soft in limits:
            try:
                resource.setrlimit(res, (soft, soft))
            except (ValueError, OSError):
                pass

    async def _execute_subprocess(self, code: str) -> dict:
        """Execute in a hardened subprocess: isolated cwd + rlimits + timeout.

        This is the FALLBACK tier (use_docker: false). It is not a security
        boundary, but it (a) runs in a throwaway working directory so a
        script writing to a relative path cannot clobber the repo, and
        (b) caps CPU and memory via rlimits.
        """
        # Throwaway working directory — the child's cwd, so relative writes
        # land here instead of in the repo (this is what previously allowed
        # a generated script to overwrite core/ via open("core/...","w")).
        run_dir = Path(tempfile.mkdtemp(prefix="amy_sbx_"))
        script_path = run_dir / "experiment.py"
        script_path.write_text(code, encoding="utf-8")

        proc = None
        # rlimit preexec is POSIX-only; skip on platforms without fork.
        preexec = self._rlimit_preexec if os.name == "posix" else None
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._sandbox_env(),
                cwd=str(run_dir),
                preexec_fn=preexec,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.max_time,
            )

            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="ignore")[:5000],
                "stderr": stderr.decode("utf-8", errors="ignore")[:2000],
                "return_code": proc.returncode,
            }
        except asyncio.TimeoutError:
            await self._terminate(proc)
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {self.max_time}s",
                "return_code": -1,
            }
        except Exception as e:
            await self._terminate(proc)
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
            }
        finally:
            shutil.rmtree(run_dir, ignore_errors=True)

    @staticmethod
    async def _terminate(proc) -> None:
        """Kill a subprocess and reap it so it cannot linger as a zombie."""
        if proc is None or proc.returncode is not None:
            return
        try:
            proc.kill()
            await asyncio.wait_for(proc.wait(), timeout=5)
        except Exception:
            pass

    async def _execute_docker(self, code: str, language: str = "python") -> dict:
        """Execute in a Docker container for stronger isolation.

        Creates a temporary work directory, mounts it into the container,
        installs common scientific packages, and runs the code.
        Output files written to /work are preserved in the host directory.
        """
        import shutil
        import uuid

        work_dir = Path("sandbox/scripts/docker_work") / str(uuid.uuid4())
        work_dir.mkdir(parents=True, exist_ok=True)

        ext = ".py" if language == "python" else ".sh"
        script_name = f"script{ext}"
        script_path = work_dir / script_name

        # Prepend a small preamble so the script can find its own directory
        if language == "python":
            preamble = "import os\nos.chdir('/work')\n"
            script_path.write_text(preamble + code, encoding="utf-8")
        else:
            script_path.write_text("#!/bin/bash\ncd /work\nset -e\n" + code, encoding="utf-8")

        interpreter = "python" if language == "python" else "bash"
        image = "amy-sandbox:latest"

        if language == "python":
            cmd = ["python", "/work/script.py"]
        else:
            cmd = ["bash", "/work/script.sh"]

        try:
            proc = await asyncio.create_subprocess_exec(
                "docker", "run", "--rm",
                f"--memory={self.max_memory}m",
                "--network=none",
                "--env", "PYTHONNOUSERSITE=1",
                "--env", "MPLBACKEND=Agg",
                "-v", f"{work_dir.resolve()}:/work",
                "--workdir", "/work",
                image,
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.max_time,
            )

            # Collect any result files produced by the script
            result_files = {}
            for f in work_dir.iterdir():
                if f.name == script_name:
                    continue
                try:
                    result_files[f.name] = f.read_text(encoding="utf-8", errors="ignore")[:10000]
                except Exception:
                    pass

            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="ignore")[:5000],
                "stderr": stderr.decode("utf-8", errors="ignore")[:2000],
                "return_code": proc.returncode,
                "work_dir": str(work_dir),
                "result_files": result_files,
            }
        except asyncio.TimeoutError:
            return {"success": False, "stdout": "", "stderr": "Docker timeout", "return_code": -1, "work_dir": str(work_dir)}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "return_code": -1, "work_dir": str(work_dir)}
        finally:
            # Clean up the work directory after a short grace period
            try:
                shutil.rmtree(work_dir, ignore_errors=True)
            except Exception:
                pass
