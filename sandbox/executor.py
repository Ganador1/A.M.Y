"""
Sandbox Executor — Run experiments safely.

Executes code in an isolated environment to test hypotheses.
Uses subprocess with timeouts as a basic sandbox.
Docker isolation can be enabled for stronger security.
"""
import asyncio
import os
import re
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
        self.allow_network = config.get("allow_network", False)
        self.allow_subprocess = config.get("allow_subprocess", False)
        self.allow_sensitive_env = config.get("allow_sensitive_env", False)
        # Ensure allowed dirs exist
        for d in _ALLOWED_WRITE_DIRS:
            d.mkdir(parents=True, exist_ok=True)

    async def execute(self, code: str, language: str = "python") -> dict:
        """Execute code in a sandboxed environment. language: 'python' or 'bash'."""
        safety_block = self._safety_block(code, language)
        if safety_block:
            return safety_block

        if language == "bash":
            return await self._execute_bash(code)
        
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
        
        if self.use_docker:
            return await self._execute_docker(code, language=language)
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

        if not self.allow_subprocess and re.search(
            r"\b(import\s+subprocess|from\s+subprocess|os\.system|popen\(|pty\.|exec\(|eval\(|__import__\()",
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

        # Write script to sandbox dir
        scripts_dir = Path("sandbox/scripts")
        scripts_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".sh", dir=scripts_dir, delete=False
        ) as f:
            f.write("#!/bin/bash\nset -e\n")
            f.write(script)
            script_path = f.name

        Path(script_path).chmod(0o700)
        try:
            proc = await asyncio.create_subprocess_exec(
                "bash", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(Path.cwd()),
                env=self._sandbox_env(),
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
            proc.kill()
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Bash script timed out after {self.max_time}s",
                "return_code": -1,
            }
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "return_code": -1}
        finally:
            Path(script_path).unlink(missing_ok=True)

    async def _execute_subprocess(self, code: str) -> dict:
        """Execute in a subprocess with timeout."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            script_path = f.name

        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._sandbox_env(),
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
            proc.kill()
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {self.max_time}s",
                "return_code": -1,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
            }
        finally:
            Path(script_path).unlink(missing_ok=True)

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
