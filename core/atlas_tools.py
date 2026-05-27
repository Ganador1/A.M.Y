"""
Atlas Tools — Acceso directo a las herramientas científicas de Atlas desde A.M.Y.

Expone búsqueda de literatura real (arXiv, PubMed, Semantic Scholar, Patents)
y herramientas de experimentación (SymPy, NumPy, BioPython, etc.) sin necesidad
de pasar por el ciclo completo de peer review.

A.M.Y usa esto para:
- Verificar hipótesis con literatura real antes de formalizar un paper
- Ejecutar cálculos matemáticos y simulaciones
- Buscar evidencia que falsifique o corrobore sus teorías
"""
import asyncio
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import structlog

log = structlog.get_logger()

ATLAS_ROOT = Path(__file__).parent.parent / "atlas"
ATLAS_VENV_PYTHON = ATLAS_ROOT / ".venv_new" / "bin" / "python3"
ATLAS_RESULT_MARKER = "__ATLAS_RESULT__"

UNUSABLE_TOOL_OUTPUT_MARKERS = (
    "atlas no disponible",
    "tool not found",
    "not found. available:",
    "unknown operation",
    "error executing",
    "traceback",
    "not implemented",
    "placeholder",
    "mock",
    "mock implementation",
    "mock output",
    "dummy",
)

WEAK_EVIDENCE_TOOLS = {
    "gnome_materials": "placeholder materials service; useful only as a demo lookup",
    "validate_hypothesis": "heuristic validator; useful for triage, not evidence",
}

_ATLAS_MISUSE_MODULE = None


def _load_atlas_misuse_guard_module():
    global _ATLAS_MISUSE_MODULE
    if _ATLAS_MISUSE_MODULE is not None:
        return _ATLAS_MISUSE_MODULE
    module_path = ATLAS_ROOT / "app" / "security" / "misuse_guard.py"
    spec = importlib.util.spec_from_file_location("_atlas_app_security_misuse_guard", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Atlas misuse guard from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _ATLAS_MISUSE_MODULE = module
    return module


def _evaluate_atlas_misuse_or_fail_closed(
    *, operation: str, content: str, domain: str = "", tool_name: str = ""
) -> dict:
    try:
        module = _load_atlas_misuse_guard_module()
        return module.misuse_guard.evaluate(
            operation=operation,
            content=content,
            domain=domain,
            tool_name=tool_name,
            actor_id=os.getenv("ATLAS_ACTOR_ID", "amy_atlas_tools"),
        ).to_dict()
    except Exception as exc:
        return {
            "allowed": False,
            "action": "block",
            "risk_level": "critical",
            "reasons": [f"Atlas misuse guard unavailable: {exc}"],
            "matched_rules": ["MISUSE_GUARD_UNAVAILABLE"],
            "decision_id": "fail-closed",
        }


def _atlas_misuse_blocked_message(decision: dict) -> str:
    try:
        module = _load_atlas_misuse_guard_module()
        return module.format_blocked_message(decision)
    except Exception:
        reasons = "; ".join(decision.get("reasons") or ["Misuse policy violation"])
        rules = ",".join(decision.get("matched_rules") or [])
        return f"Blocked by Atlas misuse policy: {reasons} (rules={rules}; decision_id={decision.get('decision_id')})"


def _evaluate_safety_or_fail_closed(
    *, operation: str, content: str, domain: str = "", tool_name: str = ""
) -> dict:
    try:
        from core.safety_kernel import evaluate_safety

        return evaluate_safety(
            operation=operation,
            content=content,
            domain=domain,
            tool_name=tool_name,
        ).to_dict()
    except Exception as exc:
        return {
            "allowed": False,
            "action": "block",
            "risk_level": "critical",
            "reasons": [f"safety kernel unavailable: {exc}"],
            "matched_rules": ["SAFETY_KERNEL_UNAVAILABLE"],
            "decision_id": "fail-closed",
        }


def _blocked_message(decision: dict) -> str:
    try:
        from core.safety_kernel import blocked_message

        return blocked_message(decision)
    except Exception:
        reasons = "; ".join(decision.get("reasons") or ["Safety policy violation"])
        return f"Blocked by safety policy: {reasons} (decision_id={decision.get('decision_id')})"


def assess_tool_output(output: object, tool_name: str | None = None) -> dict:
    """
    Classify whether an Atlas tool output is safe to treat as a real result.

    This is intentionally conservative for scientific provenance: operational
    failures, mocks, placeholders, and unimplemented tools are not evidence.
    """
    text = str(output or "")
    text_lower = text.lower()
    markers = [marker for marker in UNUSABLE_TOOL_OUTPUT_MARKERS if marker in text_lower]
    warnings = []
    evidence_level = "strong"

    if re.search(r"molecular weight of .+?:\s*0+(?:\.0+)?\s*g/mol", text_lower):
        markers.append("zero molecular weight")

    mixed_evidence_report = "toolevidenceorchestrator corroboration" in text_lower
    if mixed_evidence_report:
        real_success_match = re.search(r"real_success_count:\s*([0-9]+(?:\.[0-9]+)?)", text)
        real_success_count = 0.0
        if real_success_match:
            try:
                real_success_count = float(real_success_match.group(1))
            except ValueError:
                real_success_count = 0.0
        if real_success_count > 0:
            markers = [marker for marker in markers if marker != "mock"]
            evidence_level = "mixed"
            warnings.append("mixed evidence report")

    normalized_tool = (tool_name or "").strip().lower()
    if normalized_tool in WEAK_EVIDENCE_TOOLS:
        evidence_level = "weak"
        markers.append("known weak evidence tool")
    return {
        "usable": not markers and bool(text.strip()),
        "evidence_level": evidence_level,
        "markers": markers,
        "warnings": warnings,
        "preview": text[:500],
    }


class AtlasTools:
    """
    Interfaz ligera a las herramientas científicas de Atlas.
    Usa un worker persistente para evitar el overhead de inicialización.

    No lanza el ciclo completo de peer review — solo ejecuta herramientas específicas.
    """

    def __init__(self):
        self.available = ATLAS_VENV_PYTHON.exists() and ATLAS_ROOT.exists()
        self._worker = None
        self._lock = None
        if not self.available:
            log.warning("atlas_tools.unavailable")

    async def _ensure_worker(self):
        """Inicia el worker persistente si no está activo."""
        if self._worker is not None:
            return
        self._lock = asyncio.Lock()
        worker_script = Path(__file__).parent / "atlas_worker.py"
        self._worker = await asyncio.create_subprocess_exec(
            str(ATLAS_VENV_PYTHON), str(worker_script),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            cwd=str(ATLAS_ROOT),
            env={
                **os.environ,
                "ENABLE_REDIS_CACHE": "false",
                "MPLBACKEND": "Agg",
                "OLLAMA_BASE_URL": "https://ollama.com",
                "OLLAMA_API_KEY": os.getenv("OLLAMA_CLOUD_API_KEY_1", "") or os.getenv("OLLAMA_CLOUD_API_KEY_2", ""),
            },
        )
        # Verificar que el worker responda
        response = await self._send_request({"id": 0, "action": "ping"})
        if response.get("result") != "pong":
            log.warning("atlas_tools.worker_no_pong", response=response)
            self._worker = None

    async def _send_request(self, request: dict, timeout: float = 120.0) -> dict:
        """Envía un request al worker y espera respuesta, ignorando lineas basura."""
        if self._worker is None or self._worker.stdin.is_closing():
            self._worker = None
            await self._ensure_worker()
        async with self._lock:
            line = json.dumps(request) + "\n"
            self._worker.stdin.write(line.encode())
            await self._worker.stdin.drain()
            
            # Bucle para saltar logs u otras líneas hasta encontrar la respuesta al request
            start_time = asyncio.get_event_loop().time()
            while True:
                time_left = timeout - (asyncio.get_event_loop().time() - start_time)
                if time_left <= 0:
                    raise asyncio.TimeoutError("Timeout waiting for valid worker response")
                    
                response_bytes = await asyncio.wait_for(
                    self._worker.stdout.readline(), timeout=time_left
                )
                if not response_bytes:
                    error_output = await self._worker.stderr.read() if self._worker.stderr else b""
                    print(f"\n[DEBUG] Worker closed. Error output: {error_output.decode()}\n")
                    return {"id": request.get("id"), "error": "Worker closed output stream"}
                    
                response_str = response_bytes.decode().strip()
                if not response_str:
                    continue
                    
                try:
                    parsed = json.loads(response_str)
                    if "id" in parsed and parsed["id"] == request.get("id"):
                        return parsed
                except json.JSONDecodeError:
                    # Ignore non-JSON lines printed by native libraries (brian2, matplotlib, yt, warnings, etc.)
                    continue

    async def search_literature(
        self,
        query: str,
        domain: str = "medicine",
        max_results: int = 8,
    ) -> dict:
        """
        Busca literatura científica real usando las fuentes de Atlas:
        arXiv, PubMed, Semantic Scholar, OpenAlex.

        Returns: {"papers": [...], "support_score": float, "sources": [...]}
        """
        if not self.available:
            return {"papers": [], "error": "Atlas no disponible"}
        misuse_decision = _evaluate_atlas_misuse_or_fail_closed(
            operation="search_literature",
            content=query,
            domain=domain,
        )
        if not misuse_decision["allowed"]:
            return {
                "blocked": True,
                "error": "Blocked by Atlas misuse policy",
                "safety_decision": misuse_decision,
            }
        decision = _evaluate_safety_or_fail_closed(
            operation="search_literature",
            content=query,
            domain=domain,
        )
        if not decision["allowed"]:
            return {
                "blocked": True,
                "error": "Blocked by safety policy",
                "safety_decision": decision,
            }
        # Literature search usa su propio subprocess (no el worker)
        payload = {"query": query, "domain": domain, "max_results": max_results}
        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_literature_search, payload
        )

    async def verify_hypothesis(self, hypothesis: str, domain: str = "medicine") -> dict:
        """
        Verifica una hipótesis contra literatura real.
        Devuelve support_score (0-1), papers a favor, papers en contra.
        """
        if not self.available:
            return {"support_score": 0, "error": "Atlas no disponible"}
        misuse_decision = _evaluate_atlas_misuse_or_fail_closed(
            operation="verify_hypothesis",
            content=hypothesis,
            domain=domain,
        )
        if not misuse_decision["allowed"]:
            return {
                "blocked": True,
                "support_score": 0,
                "error": "Blocked by Atlas misuse policy",
                "safety_decision": misuse_decision,
            }
        decision = _evaluate_safety_or_fail_closed(
            operation="verify_hypothesis",
            content=hypothesis,
            domain=domain,
        )
        if not decision["allowed"]:
            return {
                "blocked": True,
                "support_score": 0,
                "error": "Blocked by safety policy",
                "safety_decision": decision,
            }
        payload = {"hypothesis": hypothesis, "domain": domain}
        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_hypothesis_verify, payload
        )

    async def run_scientific_tool(
        self, tool_name: str, tool_input: str, domain: str = "medicine"
    ) -> str:
        """
        Ejecuta una herramienta científica específica de Atlas.
        Ejemplos: sympy_solve_equation, evidence_corroborate_medicine,
                  number_theory_advanced, prime_gap_analysis, etc.
        """
        if not self.available:
            return "Atlas no disponible"
        misuse_decision = _evaluate_atlas_misuse_or_fail_closed(
            operation="run_scientific_tool",
            content=tool_input,
            domain=domain,
            tool_name=tool_name,
        )
        if not misuse_decision["allowed"]:
            log.warning(
                "atlas_tools.misuse_blocked",
                tool=tool_name,
                domain=domain,
                rules=misuse_decision.get("matched_rules", []),
            )
            return _atlas_misuse_blocked_message(misuse_decision)
        decision = _evaluate_safety_or_fail_closed(
            operation="run_scientific_tool",
            content=tool_input,
            domain=domain,
            tool_name=tool_name,
        )
        if not decision["allowed"]:
            log.warning(
                "atlas_tools.safety_blocked",
                tool=tool_name,
                domain=domain,
                rules=decision.get("matched_rules", []),
            )
            return _blocked_message(decision)
        await self._ensure_worker()
        response = await self._send_request({
            "id": hash(tool_name) & 0xFFFFFFFF,
            "action": "run_tool",
            "tool_name": tool_name,
            "tool_input": tool_input,
        })
        if "error" in response and response["error"]:
            return f"Error: {response['error']}"
        return response.get("result", "")

    async def list_tools(self, domain: str | None = None) -> list[str]:
        """Lista herramientas disponibles en Atlas, opcionalmente filtradas por dominio."""
        if not self.available:
            return []
        await self._ensure_worker()
        response = await self._send_request({
            "id": 0,
            "action": "list_tools",
            "domain": domain,
        })
        if "error" in response and response["error"]:
            log.warning("atlas_tools.list_error", error=response["error"])
            return []
        return response.get("result", [])

    async def describe_tools(self, domain: str | None = None) -> list[dict]:
        """Lista tools con name+domain+description+input_format.

        A.M.Y usa esto para que el LLM sepa qué herramienta elegir y
        cómo formatear el input — sin esto el modelo tiene que adivinar.
        """
        if not self.available:
            return []
        await self._ensure_worker()
        response = await self._send_request({
            "id": 0,
            "action": "describe_tools",
            "domain": domain,
        })
        if "error" in response and response["error"]:
            log.warning("atlas_tools.describe_error", error=response["error"])
            return []
        return response.get("result", [])

    def _run_subprocess(self, code: str, timeout: int = 120) -> str:
        """Ejecuta código Python en el venv de Atlas y retorna stdout."""
        amy_key1 = os.getenv("OLLAMA_CLOUD_API_KEY_1", "")
        amy_key2 = os.getenv("OLLAMA_CLOUD_API_KEY_2", "")
        env = os.environ.copy()
        env["OLLAMA_BASE_URL"] = "https://ollama.com"
        env["OLLAMA_API_KEY"] = amy_key1 or amy_key2
        env["ENABLE_REDIS_CACHE"] = "false"
        env["MPLBACKEND"] = "Agg"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            script = f.name

        try:
            proc = subprocess.run(
                [str(ATLAS_VENV_PYTHON), script],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=str(ATLAS_ROOT),
            )
            if proc.returncode != 0 and proc.stderr:
                return json.dumps({"error": proc.stderr[-500:], "stdout": proc.stdout[-300:]})
            return proc.stdout or "{}"
        except subprocess.TimeoutExpired:
            return json.dumps({"error": "timeout"})
        finally:
            Path(script).unlink(missing_ok=True)

    def _parse_json_output(self, out: str, default: dict | list) -> dict | list:
        """Parse Atlas JSON even when startup logs are printed before it."""
        candidates = [out]
        if ATLAS_RESULT_MARKER in out:
            candidates.insert(0, out.rsplit(ATLAS_RESULT_MARKER, 1)[-1])

        for candidate in candidates:
            candidate = candidate.strip()
            if not candidate:
                continue
            try:
                return json.loads(candidate)
            except Exception:
                pass

        return default

    def _run_literature_search(self, payload: dict) -> dict:
        request = {
            "action": "verify_hypothesis_plus",
            "topic": payload["query"],
            "domain": payload.get("domain", "medicine"),
            "k": payload.get("max_results", 8),
            "hypothesis": {
                "title": payload["query"],
                "domain": payload.get("domain", "medicine"),
            },
        }
        code = f"""
import sys, os, json, asyncio
sys.path.insert(0, {repr(str(ATLAS_ROOT))})
os.chdir({repr(str(ATLAS_ROOT))})
os.environ["ENABLE_REDIS_CACHE"] = "false"

from app.services.literature.literature_service import LiteratureService

async def main():
    svc = LiteratureService()
    result = await svc.process_request({repr(request)})
    print({repr(ATLAS_RESULT_MARKER)} + json.dumps(result, default=str))

asyncio.run(main())
"""
        out = self._run_subprocess(code, timeout=90)
        result = self._parse_json_output(out, {"papers": [], "raw": out[:500]})
        if isinstance(result, dict):
            return result
        return {"papers": [], "raw": out[:500]}

    def _run_hypothesis_verify(self, payload: dict) -> dict:
        request = {
            "action": "verify_hypothesis_plus",
            "topic": payload["hypothesis"],
            "domain": payload.get("domain", "medicine"),
            "k": 10,
            "hypothesis": {
                "title": payload["hypothesis"],
                "domain": payload.get("domain", "medicine"),
            },
        }
        code = f"""
import sys, os, json, asyncio
sys.path.insert(0, {repr(str(ATLAS_ROOT))})
os.chdir({repr(str(ATLAS_ROOT))})
os.environ["ENABLE_REDIS_CACHE"] = "false"

from app.services.literature.literature_service import LiteratureService

async def main():
    svc = LiteratureService()
    result = await svc.process_request({repr(request)})
    print({repr(ATLAS_RESULT_MARKER)} + json.dumps(result, default=str))

asyncio.run(main())
"""
        out = self._run_subprocess(code, timeout=120)
        result = self._parse_json_output(out, {"support_score": 0, "raw": out[:500]})
        if isinstance(result, dict):
            return result
        return {"support_score": 0, "raw": out[:500]}


# Global singleton
_atlas_tools: AtlasTools | None = None


def get_atlas_tools() -> AtlasTools:
    global _atlas_tools
    if _atlas_tools is None:
        _atlas_tools = AtlasTools()
    return _atlas_tools
