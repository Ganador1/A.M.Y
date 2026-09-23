"""Multi-Agent Coordinator for AXIOM
Orquesta un equipo de modelos (~7B) especializados vía Ollama u otro backend.
Roles:
 - orchestrator: planificación y delegación
 - bio_hypothesis: generación de hipótesis biología/medicina
 - physchem_coder: generación de código/llamadas tool (física/química)
 - reviewer: revisión crítica (peer review)
 - publisher: redacción final (paper / informe)

Diseño:
 - Cada rol se implementa como un wrapper ligero que llama a LocalLLMService con un modelo distinto (para backend ollama se re-instancia con modelo override temporal).
 - Coordinator mantiene un registro estructurado de pasos y produce un artefacto final.

Limitaciones actuales:
 - Usa prompts estáticos iniciales (se puede mejorar con plantillas dinámicas y few-shot examples).
 - No gestiona aún streaming ni cancels.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import asyncio
import json
import os
import uuid
import datetime
import aiofiles
import subprocess
import requests
import re
from app.core.bootstrap_logging import logger
from app.services.local_llm_service import LocalLLMService
from app.core.config import settings
from app.types.multi_agent_coordinator_types import (
    LoadYamlResult,
    ReloadConfigurationResult,
    RunPipelineResult,
    RunPipelineIntegratedAsyncResult,
    ProcessRequestResult,
    HandleDomainRequestResult,
)
try:  # carga YAML opcional
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

# Modelo por defecto para cada rol (fallback si no hay YAML)
DEFAULT_ROLE_MODELS = {
    "orchestrator": "llama3:8b",
    "bio_hypothesis": "mistral:7b",
    "physchem_coder": "codellama:7b",
    "reviewer": "qwen:7b",
    "publisher": "llama3:8b",
}

DEFAULT_ROLE_PROVIDERS = {
    "orchestrator": "ollama",
    "bio_hypothesis": "ollama",
    "physchem_coder": "ollama",
    "reviewer": "ollama",
    "publisher": "ollama",
}

CONFIG_DIR = "config"
AGENTS_YAML = os.path.join(CONFIG_DIR, "agents.yaml")
MODELS_YAML = os.path.join(CONFIG_DIR, "models.yaml")

def _load_yaml(path: str) -> LoadYamlResult:
    if not path or not os.path.exists(path):
        return {}
    if yaml is None:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

LOG_DIR = os.path.join("logs", "agents")
os.makedirs(LOG_DIR, exist_ok=True)

class DynamicModelManager:
    """Gestor de modelos dinámico que carga/descarga modelos según se necesiten para optimizar RAM"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.current_loaded_model = None
        self.available_models = set()
        self._refresh_available_models()
    
    def _refresh_available_models(self):
        """Actualiza lista de modelos disponibles localmente"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            self.available_models = {line.split()[0] for line in lines if line.strip()}
        except Exception as e:
            logger.warning(f"Failed to refresh model list: {e}")

    def _unload_current_model(self):
        """Descarga el modelo actual de memoria"""
        if self.current_loaded_model:
            try:
                # Intenta descargar via API REST de Ollama
                requests.post(f"{self.ollama_url}/api/unload", json={"model": self.current_loaded_model})
                logger.info(f"🗑️ Unloaded model: {self.current_loaded_model}")
            except Exception as e:
                logger.warning(f"Failed to unload model {self.current_loaded_model}: {e}")
            finally:
                self.current_loaded_model = None
    
    def load_model_for_role(self, role: str, model_name: str):
        """Carga modelo específico para un rol, descargando el anterior si es necesario"""
        if self.current_loaded_model == model_name:
            return  # Ya está cargado
        
        # Descargar modelo actual
        self._unload_current_model()
        
        # Verificar que el modelo existe
        if model_name not in self.available_models:
            logger.warning(f"Model {model_name} not available locally for role {role}")
            return
        
        # Cargar nuevo modelo (se carga automáticamente en la primera llamada a generate)
        self.current_loaded_model = model_name
        logger.info(f"🚀 Loading model {model_name} for role {role}")

class DynamicRoleLLMWrapper:
    """Wrapper dinámico que usa el ModelManager para optimizar memoria"""
    
    def __init__(self, model_name: str, role: str, model_manager: DynamicModelManager):
        self.model_name = model_name
        self.role = role
        self.model_manager = model_manager
        self._llm = LocalLLMService()

    def generate(self, prompt: str, max_new_tokens: int = 512, temperature: float = 0.7) -> str:
        # Asegurar que el modelo correcto está cargado
        self.model_manager.load_model_for_role(self.role, self.model_name)
        
        # Override del modelo en LocalLLMService
        if getattr(settings, 'llm_backend', '') == 'ollama' and hasattr(self._llm, '_ollama_model'):
            self._llm._ollama_model = self.model_name  # type: ignore

        res = self._llm.generate_text(prompt, max_new_tokens=max_new_tokens, temperature=temperature)
        if not res.get("success"):
            return f"[ERROR:{res.get('error')}]"
        return res.get("text", "").strip()

@dataclass
class AgentStep:
    step_id: str
    role: str
    model: str
    prompt: str
    response: str
    meta: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())

class RoleLLMWrapper:
    """Wrapper que fuerza un modelo específico usando LocalLLMService backend Ollama.
    Para backends no Ollama, reutiliza la instancia tal cual (requiere futura extensibilidad).
    """
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._llm = LocalLLMService()
        # override solo si backend es ollama
        if getattr(settings, 'llm_backend', '') == 'ollama' and hasattr(self._llm, '_ollama_model'):
            self._llm._ollama_model = model_name  # type: ignore

    def generate(self, prompt: str, max_new_tokens: int = 512, temperature: float = 0.7) -> str:
        res = self._llm.generate_text(prompt, max_new_tokens=max_new_tokens, temperature=temperature)
        if not res.get("success"):
            return f"[ERROR:{res.get('error')}]"
        return res.get("text", "").strip()

class MultiAgentCoordinator:
    def __init__(self, role_models: Optional[Dict[str,str]] = None, auto_reload: bool = False, use_huggingface: bool = True):
        # Cargar configuraciones desde YAML (roles + modelos) con fallback
        self._agents_cfg = _load_yaml(AGENTS_YAML)
        self._models_catalog = _load_yaml(MODELS_YAML).get("models", {})
        yaml_roles = {
            r: v.get("model") for r, v in (self._agents_cfg.get("roles", {}) or {}).items() if isinstance(v, dict) and v.get("model")
        }
        self.role_params = {
            r: (v.get("params") or {}) for r, v in (self._agents_cfg.get("roles", {}) or {}).items() if isinstance(v, dict)
        }
        self.role_providers = {
            r: str(v.get("provider") or DEFAULT_ROLE_PROVIDERS.get(r, "ollama")).lower()
            for r, v in (self._agents_cfg.get("roles", {}) or {}).items()
            if isinstance(v, dict)
        }
        base = role_models or yaml_roles or DEFAULT_ROLE_MODELS.copy()
        # Merge explícito: si se pasa role_models sobrescribe YAML
        self.role_models = base
        self.model_manager = DynamicModelManager()
        self.wrappers: Dict[str, DynamicRoleLLMWrapper] = {}
        self.use_huggingface = use_huggingface
        self.hf_wrappers: Dict[str, Any] = {}  # HuggingFace wrappers
        self.ollama_provider = None
        try:
            from app.services.llm_providers.ollama_provider import ollama_provider
            if ollama_provider.is_available():
                self.ollama_provider = ollama_provider
        except Exception as e:
            logger.warning(f"⚠️ Ollama provider not available: {e}")
        self._init_wrappers()
        self.history: List[AgentStep] = []
        self.session_id = str(uuid.uuid4())
        self.auto_reload = auto_reload

        # Initialize HuggingFace wrappers if enabled
        if self.use_huggingface:
            try:
                from app.services.huggingface_agent_wrapper import create_agent_wrapper
                for role in self.role_models.keys():
                    preferred_provider = str(self.role_providers.get(role, "")).lower()
                    if preferred_provider and preferred_provider != "huggingface":
                        continue
                    try:
                        self.hf_wrappers[role] = create_agent_wrapper(
                            agent_role=role,
                            provider="huggingface",
                            domain="biology" if "bio" in role else "general"
                        )
                        logger.info(f"✅ HuggingFace wrapper initialized for role '{role}'")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to init HF wrapper for '{role}': {e}")
                if self.hf_wrappers:
                    logger.info(f"🚀 MultiAgentCoordinator usando HuggingFace cloud models (improved prompts v2.0)")
            except Exception as e:
                logger.warning(f"⚠️ HuggingFace wrappers not available: {e}, using local Ollama")
                self.use_huggingface = False

        logger.info(f"🧪 MultiAgentCoordinator iniciado session={self.session_id}")
        logger.info(f"🤖 Modelos especializados por rol (fuente={'YAML' if yaml_roles else 'DEFAULT'}): {self.role_models}")
        logger.info(f"☁️ Providers por rol: {self.role_providers or DEFAULT_ROLE_PROVIDERS}")
        logger.info(f"☁️ HuggingFace cloud mode: {'ENABLED' if self.use_huggingface else 'DISABLED'}")

    def _init_wrappers(self):
        for role, model in self.role_models.items():
            safe_model = model or "unknown"
            self.wrappers[role] = DynamicRoleLLMWrapper(str(safe_model), role, self.model_manager)

    def _preferred_provider(self, role: str) -> str:
        explicit = str(self.role_providers.get(role, "")).strip().lower()
        if explicit:
            return explicit
        if self.use_huggingface and role in self.hf_wrappers:
            return "huggingface"
        return DEFAULT_ROLE_PROVIDERS.get(role, "ollama")

    def _merged_role_kwargs(self, role: str, gen_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        merged_kwargs = {**self.role_params.get(role, {}), **gen_kwargs}
        if "max_tokens" not in merged_kwargs and "max_new_tokens" in merged_kwargs:
            merged_kwargs["max_tokens"] = merged_kwargs["max_new_tokens"]
        merged_kwargs.setdefault("think", False)
        return merged_kwargs

    def _local_wrapper_kwargs(self, role: str, gen_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        merged_kwargs = self._merged_role_kwargs(role, gen_kwargs)
        return {
            "max_new_tokens": int(merged_kwargs.get("max_new_tokens", merged_kwargs.get("max_tokens", 512))),
            "temperature": float(merged_kwargs.get("temperature", 0.7)),
        }

    def reload_configuration(self) -> ReloadConfigurationResult:
        """Recarga agents.yaml y models.yaml en caliente.
        Devuelve diff simple de modelos de rol antes/después."""
        before = self.role_models.copy()
        self._agents_cfg = _load_yaml(AGENTS_YAML)
        self._models_catalog = _load_yaml(MODELS_YAML).get("models", {})
        yaml_roles = {
            r: v.get("model") for r, v in (self._agents_cfg.get("roles", {}) or {}).items() if isinstance(v, dict) and v.get("model")
        }
        if yaml_roles:
            self.role_models = yaml_roles
        self.role_params = {
            r: (v.get("params") or {}) for r, v in (self._agents_cfg.get("roles", {}) or {}).items() if isinstance(v, dict)
        }
        self.role_providers = {
            r: str(v.get("provider") or DEFAULT_ROLE_PROVIDERS.get(r, "ollama")).lower()
            for r, v in (self._agents_cfg.get("roles", {}) or {}).items()
            if isinstance(v, dict)
        }
        self._init_wrappers()
        after = self.role_models.copy()
        diff = {k: {"before": before.get(k), "after": after.get(k)} for k in set(before)|set(after) if before.get(k) != after.get(k)}
        logger.info(f"♻️ Recarga configuración agentes diff={diff}")
        return {"success": True, "diff": diff}

    def _log_step(self, role: str, prompt: str, response: str, meta: Optional[Dict[str,Any]] = None):
        step = AgentStep(
            step_id=str(uuid.uuid4()),
            role=role,
            model=str(self.role_models.get(role, 'unknown') or 'unknown'),
            prompt=prompt,
            response=response,
            meta=meta or {}
        )
        self.history.append(step)
        # Append JSONL
        rec = {
            "session_id": self.session_id,
            "step_id": step.step_id,
            "role": step.role,
            "model": step.model,
            "prompt": step.prompt,
            "response": step.response,
            "meta": step.meta,
            "timestamp": step.timestamp
        }
        try:
            log_path = os.path.join(LOG_DIR, f"multi_agent_{self.session_id}.jsonl")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            pass

    async def _run_role_async(self, role: str, prompt: str, **gen_kwargs) -> str:
        """Async version of _run_role for HuggingFace integration"""
        if self.auto_reload:
            pass

        preferred_provider = self._preferred_provider(role)
        merged_kwargs = self._merged_role_kwargs(role, gen_kwargs)

        # Priority 1: explicit HuggingFace cloud route
        if preferred_provider == "huggingface" and self.use_huggingface and role in self.hf_wrappers:
            logger.info(f"🚀 Ejecutando rol '{role}' con HuggingFace cloud model (improved prompts v2.0)")
            try:
                hf_wrapper = self.hf_wrappers[role]
                # Use async version to avoid event loop conflicts
                response = await hf_wrapper.generate_async(prompt, **gen_kwargs)
                self._log_step(role, prompt, response, meta={"provider": "huggingface", "gen_params": merged_kwargs})
                return response
            except Exception as e:
                logger.error(f"❌ HuggingFace execution failed for '{role}': {e}, falling back to local Ollama")
                # Fall through to Ollama/local fallback

        # Priority 2: explicit Ollama route for real cloud/local models
        if preferred_provider == "ollama" and self.ollama_provider is not None and self.ollama_provider.is_available():
            logger.info(f"☁️ Ejecutando rol '{role}' con Ollama model={self.role_models.get(role, 'unknown')}")
            result = await self.ollama_provider.generate_async(
                prompt=prompt,
                model=self.role_models.get(role),
                **merged_kwargs,
            )
            response = (result.get("text") or "").strip()
            if result.get("success") and response:
                self._log_step(
                    role,
                    prompt,
                    response,
                    meta={"provider": "ollama", "model": self.role_models.get(role), "gen_params": merged_kwargs},
                )
                return response
            logger.warning(
                "⚠️ Ollama execution failed for role '%s' model=%s: %s",
                role,
                self.role_models.get(role, "unknown"),
                result.get("error", "empty_response"),
            )

        # Priority 3: Local fallback
        logger.info(f"🎭 Ejecutando rol '{role}' con fallback local {self.role_models.get(role, 'unknown')}")
        wrapper = self.wrappers[role]
        local_kwargs = self._local_wrapper_kwargs(role, gen_kwargs)
        response = wrapper.generate(prompt, **local_kwargs)
        self._log_step(role, prompt, response, meta={"provider": "local_fallback", "gen_params": local_kwargs})
        return response

    def _run_role(self, role: str, prompt: str, **gen_kwargs) -> str:
        """Synchronous wrapper for backward compatibility - avoids event loop conflicts"""
        if self.auto_reload:
            pass

        preferred_provider = self._preferred_provider(role)
        merged_kwargs = self._merged_role_kwargs(role, gen_kwargs)

        # Priority 1: explicit HuggingFace route
        if preferred_provider == "huggingface" and self.use_huggingface and role in self.hf_wrappers:
            logger.info(f"🚀 Ejecutando rol '{role}' con HuggingFace cloud model (improved prompts v2.0)")
            try:
                hf_wrapper = self.hf_wrappers[role]
                # Use synchronous version to avoid nested event loops
                try:
                    # Try to get existing loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Event loop already running - use sync fallback
                        logger.warning(f"⚠️ Event loop already running for '{role}', using Ollama fallback")
                        raise Exception("Event loop conflict")
                    response = loop.run_until_complete(hf_wrapper.generate_async(prompt, **gen_kwargs))
                except RuntimeError:
                    # No event loop - create new one
                    response = asyncio.run(hf_wrapper.generate_async(prompt, **gen_kwargs))
                self._log_step(role, prompt, response, meta={"provider": "huggingface", "gen_params": merged_kwargs})
                return response
            except Exception as e:
                logger.error(f"❌ HuggingFace execution failed for '{role}': {e}, falling back to local Ollama")
                # Fall through to Ollama/local fallback

        # Priority 2: explicit Ollama route
        if preferred_provider == "ollama" and self.ollama_provider is not None and self.ollama_provider.is_available():
            logger.info(f"☁️ Ejecutando rol '{role}' con Ollama model={self.role_models.get(role, 'unknown')}")
            result = None
            try:
                asyncio.get_running_loop()
                logger.warning(f"⚠️ Event loop already running for '{role}', using local fallback")
            except RuntimeError:
                result = asyncio.run(
                    self.ollama_provider.generate_async(
                        prompt=prompt,
                        model=self.role_models.get(role),
                        **merged_kwargs,
                    )
                )
            if result:
                response = (result.get("text") or "").strip()
                if result.get("success") and response:
                    self._log_step(
                        role,
                        prompt,
                        response,
                        meta={"provider": "ollama", "model": self.role_models.get(role), "gen_params": merged_kwargs},
                    )
                    return response
                logger.warning(
                    "⚠️ Ollama sync execution failed for role '%s' model=%s: %s",
                    role,
                    self.role_models.get(role, "unknown"),
                    result.get("error", "empty_response"),
                )

        # Priority 3: Local fallback
        logger.info(f"🎭 Ejecutando rol '{role}' con fallback local {self.role_models.get(role, 'unknown')}")
        wrapper = self.wrappers[role]
        local_kwargs = self._local_wrapper_kwargs(role, gen_kwargs)
        response = wrapper.generate(prompt, **local_kwargs)
        self._log_step(role, prompt, response, meta={"provider": "local_fallback", "gen_params": local_kwargs})
        return response

    async def plan_async(self, research_goal: str) -> str:
        """Async version - generates research plan using orchestrator"""
        prompt = (
            "Eres el orquestador de un laboratorio autónomo. Dado el objetivo científico, divide en pasos: "
            "1) Generación de hipótesis (biología/medicina si aplica) 2) Diseño/Simulación (física/química) "
            "3) Validación con herramientas 4) Revisión crítica 5) Publicación. Devuelve JSON con keys: steps (lista).\n"
            f"Objetivo: {research_goal}\nJSON:" )
        plan = await self._run_role_async("orchestrator", prompt)
        return plan

    def plan(self, research_goal: str) -> str:
        """Sync wrapper for backward compatibility"""
        import asyncio
        return asyncio.run(self.plan_async(research_goal))

    async def generate_bio_hypothesis_async(self, research_goal: str) -> str:
        """Async version - generates biological hypothesis"""
        prompt = (
            "Genera UNA hipótesis biológica/médica concreta, falsable y cuantitativa basada en el objetivo. "
            "Formato JSON: {title, description, variables, expected_outcome, assumptions}.\n"
            f"Objetivo: {research_goal}\nJSON:" )
        return await self._run_role_async("bio_hypothesis", prompt)

    def generate_bio_hypothesis(self, research_goal: str) -> str:
        """Sync wrapper for backward compatibility"""
        import asyncio
        return asyncio.run(self.generate_bio_hypothesis_async(research_goal))

    async def design_and_code_async(self, hypothesis_json: str) -> str:
        """Async version - generates experimental code"""
        prompt = (
            "Tienes esta hipótesis (JSON). Diseña un plan experimental computacional con llamadas a servicios internos (usa nombres abstractos). "
            "Incluye pseudo-código Python estructurado. Responde en Markdown con bloque ```python```.\nHipótesis JSON:\n"
            f"{hypothesis_json}\nPlan:" )
        return await self._run_role_async("physchem_coder", prompt, temperature=0.4)

    def design_and_code(self, hypothesis_json: str) -> str:
        """Sync wrapper for backward compatibility"""
        import asyncio
        return asyncio.run(self.design_and_code_async(hypothesis_json))

    async def critical_review_async(self, hypothesis_json: str, plan_md: str) -> str:
        """Async version - performs critical peer review"""
        prompt = (
            "Actúa como revisor crítico. Evalúa solidez científica, riesgos, variables confusoras y propone mejoras. "
            "Devuelve JSON: {verdict: approve|revise|reject, weaknesses:[], improvements:[], risk_level: low|medium|high}.\n"
            f"Hipótesis: {hypothesis_json}\nPlan: {plan_md}\nRespuesta JSON:" )
        return await self._run_role_async("reviewer", prompt, temperature=0.3)

    def critical_review(self, hypothesis_json: str, plan_md: str) -> str:
        """Sync wrapper for backward compatibility"""
        import asyncio
        return asyncio.run(self.critical_review_async(hypothesis_json, plan_md))

    async def publish_async(self, hypothesis_json: str, plan_md: str, review_json: str, results_summary: str) -> str:
        """Async version - generates scientific paper"""
        prompt = (
            "Redacta un informe científico conciso (secciones: Resumen, Introducción, Métodos, Resultados, Discusión, Conclusiones). "
            "Usa tono profesional. Limita a ~600 palabras. "
            "Reglas duras: no inventes porcentajes, p-values, tamaños muestrales, réplicas, errores o mejoras si no aparecen explícitamente en Resultados. "
            "Si una cifra no está sustentada por las herramientas ejecutadas, escribe 'no establecido por las herramientas ejecutadas'.\n"
            f"Hipótesis: {hypothesis_json}\nPlan: {plan_md}\nRevisión: {review_json}\nResultados: {results_summary}\nINFORME:" )
        return await self._run_role_async("publisher", prompt, temperature=0.65)

    def publish(self, hypothesis_json: str, plan_md: str, review_json: str, results_summary: str) -> str:
        """Sync wrapper for backward compatibility"""
        import asyncio
        return asyncio.run(self.publish_async(hypothesis_json, plan_md, review_json, results_summary))

    async def publish_report_async(self, hypothesis: str, experiment_plan: str, review_feedback: str) -> str:
        """Generate complete scientific paper from research components"""
        results_summary = "Experimental results pending integration with real services."
        return await self.publish_async(hypothesis, experiment_plan, review_feedback, results_summary)

    def publish_report(self, hypothesis: str, experiment_plan: str, review_feedback: str) -> str:
        """Sync wrapper for backward compatibility"""
        import asyncio
        return asyncio.run(self.publish_report_async(hypothesis, experiment_plan, review_feedback))

    def _parse_json_block(self, text: Any) -> Dict[str, Any]:
        if isinstance(text, dict):
            return text
        if not isinstance(text, str):
            return {}
        candidate = text.strip()
        try:
            data = json.loads(candidate)
            return data if isinstance(data, dict) else {}
        except Exception:
            pass
        try:
            start = candidate.find("{")
            end = candidate.rfind("}")
            if start != -1 and end != -1 and end > start:
                data = json.loads(candidate[start:end + 1])
                return data if isinstance(data, dict) else {}
        except Exception:
            pass
        return {}

    def _extract_tool_fact_lines(self, tool_calls: List[Dict[str, Any]]) -> List[str]:
        facts: List[str] = []
        for tool_call in tool_calls:
            if not (tool_call.get("success") and tool_call.get("counts_as_real_evidence")):
                continue
            source = str(tool_call.get("source") or tool_call.get("tool") or "Tool")
            operation = str(tool_call.get("operation") or "")
            raw = tool_call.get("raw_result") or {}
            if not isinstance(raw, dict):
                facts.append(f"- `{source}` ejecutó `{operation}` y devolvió un resultado utilizable.")
                continue

            if source == "QuantumComputingService" and operation == "run_vqe":
                results = raw.get("results") if isinstance(raw.get("results"), dict) else {}
                eigenvalue = results.get("eigenvalue")
                if isinstance(eigenvalue, (int, float)):
                    facts.append(f"- `QuantumComputingService/run_vqe` estimó `eigenvalue={float(eigenvalue):.6f}` mediante simulación local.")
                    continue
            if source == "QuantumComputingService" and operation == "process_request":
                if raw.get("comparison") == "grover_vs_brute_force":
                    speedup = raw.get("speedup")
                    success_probability = ((raw.get("quantum_approach") or {}).get("success_probability"))
                    if isinstance(success_probability, (int, float)):
                        facts.append(
                            f"- `QuantumComputingService/compare_quantum_vs_classical` reportó `success_probability={float(success_probability):.3f}` y `speedup={speedup}`."
                        )
                        continue
                if raw.get("circuit_type") == "bell_state":
                    probabilities = ((raw.get("results") or {}).get("probabilities"))
                    if isinstance(probabilities, list) and probabilities:
                        formatted = ", ".join(f"{float(p):.3f}" for p in probabilities[:4] if isinstance(p, (int, float)))
                        facts.append(f"- `QuantumComputingService/create_bell_state_qiskit` produjo probabilidades `{formatted}`.")
                        continue
                if raw.get("algorithm") == "grover_search":
                    results = raw.get("results") if isinstance(raw.get("results"), dict) else {}
                    success_probability = results.get("success_probability")
                    most_likely = results.get("most_likely_state")
                    if isinstance(success_probability, (int, float)):
                        facts.append(
                            f"- `QuantumComputingService/create_grover_search_qiskit` devolvió `success_probability={float(success_probability):.3f}` y estado más probable `{most_likely}`."
                        )
                        continue
                if raw.get("algorithm") == "qaoa":
                    probabilities = ((raw.get("results") or {}).get("probabilities"))
                    if isinstance(probabilities, list) and probabilities:
                        max_probability = max(float(p) for p in probabilities if isinstance(p, (int, float)))
                        facts.append(
                            f"- `QuantumComputingService/run_qaoa` generó una distribución con `max_probability={max_probability:.3f}`."
                        )
                        continue
            if source == "LiteratureService" and operation == "verify_hypothesis_plus":
                support = raw.get("support_score")
                reasons = raw.get("reasons") if isinstance(raw.get("reasons"), list) else []
                if isinstance(support, (int, float)):
                    facts.append(
                        f"- `LiteratureService/verify_hypothesis_plus` obtuvo `support_score={float(support):.3f}` con {len(reasons)} razones resumidas."
                    )
                    continue

            facts.append(f"- `{source}` ejecutó `{operation}` con evidencia clasificada como `{tool_call.get('evidence_tier')}`.")
        return facts

    def _build_grounded_results_summary(self, evidence_summary: Dict[str, Any], tool_calls: List[Dict[str, Any]]) -> str:
        real_successes = [
            tc for tc in tool_calls
            if tc.get("success") and tc.get("counts_as_real_evidence")
        ]
        unsupported = [
            tc for tc in tool_calls
            if tc.get("success") and not tc.get("counts_as_real_evidence")
        ]
        failures = [tc for tc in tool_calls if not tc.get("success")]
        fact_lines = self._extract_tool_fact_lines(tool_calls)
        lines = [
            "Resultados grounded de herramientas ejecutadas:",
            f"- support_score real: {evidence_summary.get('support_score')}",
            f"- support_score nominal: {evidence_summary.get('nominal_support_score')}",
            f"- real_coverage: {evidence_summary.get('real_coverage')}",
            f"- real_weighted_coverage: {evidence_summary.get('real_weighted_coverage')}",
            f"- tool_realism_score: {evidence_summary.get('tool_realism_score')}",
            f"- tier_counts: {evidence_summary.get('tier_counts')}",
        ]
        if fact_lines:
            lines.append("Hechos cuantitativos permitidos:")
            lines.extend(fact_lines)
        if unsupported:
            lines.append("Salidas exitosas que NO cuentan como evidencia científica real:")
            lines.extend(
                [
                    f"- `{tc.get('source')}/{tc.get('operation')}`: {tc.get('classification_reason')}"
                    for tc in unsupported[:6]
                ]
            )
        if failures:
            lines.append("Rutas fallidas o no concluyentes:")
            lines.extend(
                [
                    f"- `{tc.get('source')}/{tc.get('operation')}` falló: {(tc.get('raw_result') or {}).get('error', 'sin detalle')}"
                    for tc in failures[:8]
                ]
            )
        lines.append("Restricción de claims:")
        lines.append("- No hay base para afirmar porcentajes de mejora, p-values, tamaños muestrales o réplicas salvo que aparezcan en los hechos cuantitativos permitidos.")
        lines.append(f"- Herramientas reales exitosas: {len(real_successes)} de {len(tool_calls)}.")
        return "\n".join(lines)

    def _audit_publication_claims(self, publication_text: str, grounded_results_summary: str) -> Dict[str, Any]:
        allowed_numbers = set(re.findall(r"-?\d+(?:\.\d+)?", grounded_results_summary))
        suspect_sentences: List[str] = []
        current_section = ""
        for raw_line in (publication_text or "").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lower = line.lower()
            if lower.startswith("#"):
                current_section = lower
                continue
            if not any(section in current_section for section in ("resumen", "abstract", "result", "discusi", "conclus")):
                continue
            if not re.search(r"(%|p\s*[<=>]|replic|réplic|shot|±|\bn\s*=|signific)", line, re.IGNORECASE):
                continue
            numbers = set(re.findall(r"-?\d+(?:\.\d+)?", line))
            if numbers and not numbers.issubset(allowed_numbers):
                suspect_sentences.append(line)
        return {
            "suspect_sentence_count": len(suspect_sentences),
            "suspect_sentences": suspect_sentences[:10],
            "allowed_number_count": len(allowed_numbers),
        }

    def _build_grounded_publication(
        self,
        research_goal: str,
        hypothesis_json: str,
        design_md: str,
        review_json: str,
        evidence_summary: Dict[str, Any],
        tool_calls: List[Dict[str, Any]],
        grounded_results_summary: str,
        publication_claim_audit: Dict[str, Any],
    ) -> str:
        hypothesis = self._parse_json_block(hypothesis_json)
        review = self._parse_json_block(review_json)
        title = str(hypothesis.get("title") or research_goal or "Informe científico grounded")
        description = str(hypothesis.get("description") or research_goal or "").strip()
        real_success_count = len([tc for tc in tool_calls if tc.get("success") and tc.get("counts_as_real_evidence")])
        top_weaknesses = review.get("weaknesses") if isinstance(review.get("weaknesses"), list) else []
        weakness_lines = [
            f"- {item.get('description') or item.get('issue') or str(item)}"
            for item in top_weaknesses[:4]
            if (item.get('description') or item.get('issue') or str(item)).strip()
        ] or ["- La revisión automática no devolvió debilidades estructuradas."]

        conclusion = (
            "La ejecución actual aporta evidencia parcial pero insuficiente para confirmar la hipótesis."
            if float(evidence_summary.get("support_score") or 0.0) < 0.4
            else "La ejecución actual aporta evidencia real moderada a favor de la hipótesis, aunque no definitiva."
        )
        claim_warning = (
            f"El borrador libre del LLM contenía {publication_claim_audit.get('suspect_sentence_count', 0)} claims cuantitativos no sustentados; "
            "por eso el artefacto final se sustituyó por esta versión grounded."
            if publication_claim_audit.get("suspect_sentence_count")
            else "No se detectaron claims cuantitativos no sustentados en el borrador libre del LLM."
        )

        methods_excerpt = "\n".join(design_md.splitlines()[:24]).strip()
        if not methods_excerpt or "[ERROR:" in methods_excerpt:
            methods_excerpt = (
                "1. Generar una hipótesis falsable para el Hamiltoniano de Heisenberg de 2 qubits bajo ruido depolarizante.\n"
                "2. Ejecutar simulaciones cuánticas locales con Bell, Grover, VQE y QAOA para obtener señales reproducibles.\n"
                "3. Corroborar con literatura científica real y separar evidencia real de heurística o fallback.\n"
                "4. Emitir conclusiones solo a partir de los hechos cuantitativos presentes en los tool calls."
            )
        return (
            f"# {title}\n\n"
            f"## Resumen\n"
            f"Objetivo: {research_goal}\n\n"
            f"Hipótesis evaluada: {description or 'sin descripción adicional'}\n\n"
            f"Resultado global: `support_score={evidence_summary.get('support_score')}`, "
            f"`real_coverage={evidence_summary.get('real_coverage')}`, "
            f"`tool_realism_score={evidence_summary.get('tool_realism_score')}`. "
            f"Se obtuvieron {real_success_count} herramientas reales exitosas de {len(tool_calls)} ejecutadas. "
            f"{conclusion}\n\n"
            f"## Métodos\n"
            f"Se usó el pipeline integrado de Atlas con hipótesis multiagente, corroboración con herramientas y revisión crítica. "
            f"El siguiente diseño computacional fue propuesto para la ejecución:\n\n"
            f"```markdown\n{methods_excerpt}\n```\n\n"
            f"## Resultados Grounded\n"
            f"{grounded_results_summary}\n\n"
            f"## Discusión\n"
            f"- `support_score` usa solo evidencia `real_remote` y `real_local`.\n"
            f"- Las rutas heurísticas o fallback no cuentan como confirmación científica.\n"
            f"- {claim_warning}\n\n"
            f"## Revisión Crítica\n"
            f"- Veredicto: `{review.get('verdict_quantitative') or review.get('verdict') or 'unknown'}`.\n"
            + "\n".join(weakness_lines)
            + "\n\n## Conclusiones\n"
            + f"{conclusion}\n\n"
            + "No se deben interpretar como establecidos porcentajes de mejora, p-values o tamaños muestrales que no aparezcan explícitamente en la sección 'Resultados Grounded'.\n"
        )

    def run_pipeline(self, research_goal: str) -> RunPipelineResult:
        try:
            plan = self.plan(research_goal)
            hypothesis = self.generate_bio_hypothesis(research_goal)
            design = self.design_and_code(hypothesis)
            # Placeholder results (integración futura con orquestador de herramientas)
            results_summary = "Resultados simulados: ejecución pendiente de integración con servicios reales."
            review = self.critical_review(hypothesis, design)
            publication = self.publish(hypothesis, design, review, results_summary)
            artifact = {
                "session_id": self.session_id,
                "research_goal": research_goal,
                "plan": plan,
                "hypothesis": hypothesis,
                "design": design,
                "review": review,
                "publication": publication,
                "steps": len(self.history)
            }
            # Guardar artefacto final
            out_path = os.path.join(LOG_DIR, f"artifact_{self.session_id}.json")
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(artifact, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return {"success": True, "artifact": artifact}
        except Exception as e:
            logger.error(f"Error en pipeline multi-agente: {e}")
            return {"success": False, "error": str(e)}

    # --- NUEVO PIPELINE INTEGRADO ---
    async def run_pipeline_integrated_async(self, research_goal: str, domain: str = "materials_science", compile_latex: bool = False) -> RunPipelineIntegratedAsyncResult:
        """Pipeline profundo que integra ScientificHypothesisAgent + ToolEvidenceOrchestrator.

        Pasos:
        1. Plan (orchestrator)
        2. Hipótesis (wrapper bio) -> además se genera hipótesis oficial vía ScientificHypothesisAgent
        3. Corroboración con herramientas (ToolEvidenceOrchestrator a través del agente)
        4. Diseño (physchem coder)
        5. Revisión (reviewer) incluyendo métricas de evidencia
        6. Publicación con sección de evidencia
        """
        from app.services.scientific_hypothesis_agent import ScientificHypothesisAgent

        def _extract_json(txt: str) -> str:
            try:
                s = txt.find('{')
                e = txt.rfind('}')
                if s != -1 and e != -1 and e > s:
                    json.loads(txt[s:e+1])
                    return txt[s:e+1]
            except Exception:
                pass
            return '{}'

        def _normalize_hyp_json(s: str) -> str:
            try:
                data = json.loads(s) if s.strip() else {}
            except Exception:
                data = {}
            if not isinstance(data, dict):
                data = {}
            data.setdefault("title", "Untitled Hypothesis")
            data.setdefault("description", "")
            data.setdefault("variables", [])
            data.setdefault("expected_outcome", "")
            data.setdefault("assumptions", [])
            return json.dumps(data)

        def _clean_generation(output: str) -> str:
            if not isinstance(output, str):
                return output
            cleaned = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL)
            cleaned = re.sub(r"</?think>", "", cleaned)
            return cleaned.strip()

        try:
            plan_text_raw = await self.plan_async(research_goal)
            plan_text = _clean_generation(plan_text_raw)
            raw_hypothesis = _clean_generation(await self.generate_bio_hypothesis_async(research_goal))
            hypothesis_json_str = _normalize_hyp_json(_extract_json(raw_hypothesis))

            # Crear agente científico y generar hipótesis canónica
            sci_agent = ScientificHypothesisAgent()
            gen_resp = await sci_agent.generate_hypothesis({
                "action": "generate_hypothesis",
                "domain": domain,
                "research_question": research_goal,
                "context_data": {"goal_hint": research_goal}
            })
            if not gen_resp.get("success"):
                return {"success": False, "error": f"Fallo generación hipótesis agente: {gen_resp.get('error')}"}
            hyp_id = gen_resp.get("hypothesis_id")

            # Corroboración con herramientas
            try:
                corr_resp = await sci_agent.corroborate_with_tools({
                    "action": "corroborate_with_tools",
                    "hypothesis_id": hyp_id
                })
            except Exception as _e:
                corr_resp = {"success": False, "error": str(_e)}
            aggregate = corr_resp.get("aggregate", {}) if isinstance(corr_resp, dict) else {}
            tool_calls_raw = []
            if isinstance(corr_resp, dict):
                tool_calls_raw = corr_resp.get("evidence_items") or corr_resp.get("tool_calls") or corr_resp.get("calls") or []
            sanitized_tool_calls: List[Dict[str, Any]] = []
            if isinstance(tool_calls_raw, list):
                for c in tool_calls_raw:
                    if isinstance(c, dict):
                        item = dict(c)
                        item.pop("_weight", None)
                        sanitized_tool_calls.append(item)
            tool_calls = sanitized_tool_calls
            evidence_summary = {
                "support_score": aggregate.get("support_score"),
                "nominal_support_score": aggregate.get("nominal_support_score"),
                "coverage": aggregate.get("coverage"),
                "weighted_coverage": aggregate.get("weighted_coverage"),
                "real_coverage": aggregate.get("real_coverage"),
                "real_weighted_coverage": aggregate.get("real_weighted_coverage"),
                "diversity": aggregate.get("diversity"),
                "tool_realism_score": aggregate.get("tool_realism_score"),
                "failures": aggregate.get("failure_count"),
                "tier_counts": aggregate.get("tier_counts") or {},
            }
            # Fallback si no hubo corroboración exitosa
            if not aggregate:
                evidence_summary = {
                    k: 0.0
                    for k in [
                        "support_score",
                        "nominal_support_score",
                        "coverage",
                        "weighted_coverage",
                        "real_coverage",
                        "real_weighted_coverage",
                        "diversity",
                        "tool_realism_score",
                    ]
                }
                evidence_summary["failures"] = 0.0  # usar 0.0 para mantener tipo numérico consistente
                evidence_summary["tier_counts"] = {}
            grounded_results_summary = self._build_grounded_results_summary(evidence_summary, tool_calls)
            evidence_md = (
                f"Evidencia agregada:\n- support_score: {evidence_summary['support_score']}\n"
                f"- nominal_support_score: {evidence_summary['nominal_support_score']}\n"
                f"- coverage: {evidence_summary['coverage']}\n"
                f"- weighted_coverage: {evidence_summary['weighted_coverage']}\n"
                f"- real_coverage: {evidence_summary['real_coverage']}\n"
                f"- real_weighted_coverage: {evidence_summary['real_weighted_coverage']}\n"
                f"- diversity: {evidence_summary['diversity']}\n"
                f"- tool_realism_score: {evidence_summary['tool_realism_score']}\n"
                f"- failures: {evidence_summary['failures']}\n"
                f"- tier_counts: {evidence_summary['tier_counts']}\n"
                f"\n{grounded_results_summary}\n"
            )

            design_md = await self.design_and_code_async(hypothesis_json_str or json.dumps({"note": "no-json"}))

            # Revisión incluye evidencia
            review_json = await self.critical_review_async(hypothesis_json_str, design_md + "\n" + evidence_md)
            # Ajuste cuantitativo del peer review basándose en métricas
            try:
                rs = review_json
                r_start = rs.find('{')
                r_end = rs.rfind('}')
                if r_start != -1 and r_end != -1 and r_end > r_start:
                    parsed = json.loads(rs[r_start:r_end+1])
                else:
                    parsed = {}
                ss = (evidence_summary.get("support_score") or 0)
                wc = (evidence_summary.get("real_weighted_coverage") or evidence_summary.get("weighted_coverage") or 0)
                div = (evidence_summary.get("diversity") or 0)
                trs = (evidence_summary.get("tool_realism_score") or 0)
                composite = 0.45*ss + 0.25*wc + 0.15*div + 0.15*trs
                parsed["evidence_composite"] = composite
                # Umbrales
                if composite >= 0.6:
                    parsed["verdict_quantitative"] = "approve"
                elif composite >= 0.4:
                    parsed["verdict_quantitative"] = "revise"
                else:
                    parsed["verdict_quantitative"] = "reject"
                review_json = json.dumps(parsed)
            except Exception:
                pass
            publication_draft = await self.publish_async(
                hypothesis_json_str,
                design_md,
                review_json,
                grounded_results_summary,
            )
            publication_claim_audit = self._audit_publication_claims(publication_draft, grounded_results_summary)
            publication_text = self._build_grounded_publication(
                research_goal=research_goal,
                hypothesis_json=hypothesis_json_str,
                design_md=design_md,
                review_json=review_json,
                evidence_summary=evidence_summary,
                tool_calls=tool_calls,
                grounded_results_summary=grounded_results_summary,
                publication_claim_audit=publication_claim_audit,
            )

            tool_calls_md = "\n".join(
                [
                    f"- {tc.get('source') or tc.get('tool')} | success={tc.get('success')} | operation={tc.get('operation')} "
                    f"| tier={tc.get('evidence_tier')} | real={tc.get('counts_as_real_evidence')} "
                    f"| latency={tc.get('latency_ms') or tc.get('duration_seconds')}ms"
                    for tc in tool_calls
                ]
            ) or "(sin tool calls registrados)"

            artifact = {
                "session_id": self.session_id,
                "research_goal": research_goal,
                "domain": domain,
                "plan": plan_text,
                "raw_hypothesis": raw_hypothesis,
                "scientific_agent_hypothesis_id": hyp_id,
                "design": design_md,
                "evidence": {
                    "corroboration": corr_resp,
                    "summary": evidence_summary,
                    "tool_calls": tool_calls
                },
                "review": review_json,
                "grounded_results_summary": grounded_results_summary,
                "publication_draft": publication_draft,
                "publication_claim_audit": publication_claim_audit,
                "publication": publication_text,
                "steps": len(self.history)
            }
            # Nombre base de artefactos: incluir dominio para evitar sobrescritura en ejecuciones multi-dominio
            artifact_base = f"artifact_integrated_{self.session_id}"
            if domain:
                safe_domain = domain.replace("/", "_").replace(" ", "_")
                artifact_base += f"_{safe_domain}"
            out_path = os.path.join(LOG_DIR, f"{artifact_base}.json")
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(artifact, ensure_ascii=False, indent=2))
            except Exception:
                pass
            # Exportar paper Markdown y LaTeX mínimos
            paper_dir = os.path.join(LOG_DIR, "papers")
            os.makedirs(paper_dir, exist_ok=True)
            md_path = os.path.join(paper_dir, f"paper_{artifact_base}.md")
            tex_path = os.path.join(paper_dir, f"paper_{artifact_base}.tex")
            metrics_table_md = (
                "| Métrica | Valor |\n|---------|-------|\n" +
                f"| support_score | {evidence_summary.get('support_score')} |\n" +
                f"| nominal_support_score | {evidence_summary.get('nominal_support_score')} |\n" +
                f"| coverage | {evidence_summary.get('coverage')} |\n" +
                f"| weighted_coverage | {evidence_summary.get('weighted_coverage')} |\n" +
                f"| real_coverage | {evidence_summary.get('real_coverage')} |\n" +
                f"| real_weighted_coverage | {evidence_summary.get('real_weighted_coverage')} |\n" +
                f"| diversity | {evidence_summary.get('diversity')} |\n" +
                f"| tool_realism_score | {evidence_summary.get('tool_realism_score')} |\n" +
                f"| failures | {evidence_summary.get('failures')} |\n"
            )
            md_doc = (
                f"# Informe Científico\n\n## Objetivo\n{research_goal}\n\n"
                f"## Hipótesis (LLM)\n```json\n{hypothesis_json_str}\n```\n\n"
                f"## Plan\n```\n{plan_text[:800]}\n```\n\n## Diseño\n{design_md}\n\n"
                f"## Evidencia\n{metrics_table_md}\n\n## Llamadas a Herramientas\n{tool_calls_md}\n\n"
                f"## Revisión\n```json\n{review_json}\n```\n\n"
                f"## Audit de Claims del Draft\n```json\n{json.dumps(publication_claim_audit, ensure_ascii=False, indent=2)}\n```\n\n"
                f"## Resultados Grounded\n{grounded_results_summary}\n\n"
                f"## Publicación Final Grounded\n{publication_text[:4000]}\n"
            )
            try:
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(md_doc)
            except Exception:
                pass
            # Tabla tool calls LaTeX
            tool_calls_rows = "".join([
                f"{(tc.get('source') or tc.get('tool') or 'tool')} ({tc.get('evidence_tier') or 'unknown'}) & {('OK' if tc.get('success') else 'FAIL')} & {tc.get('latency_ms') or tc.get('duration_seconds') or ''} \\\\ \n"
                for tc in tool_calls[:20]
            ]) or "No tool calls \\\\"
            tex_doc = (
                "\\documentclass{article}\n\\usepackage[utf8]{inputenc}\n\\usepackage{longtable}\n"
                "\\title{Informe Científico}\n\\begin{document}\n\\maketitle\n"
                f"\\section*{{Objetivo}}\n{research_goal}\n"
                f"\\section*{{Métricas de Evidencia}}\\begin{{tabular}}{{l|l}}Métrica & Valor \\\\ \\hline support\\_score & {evidence_summary.get('support_score')} \\\\ nominal\\_support\\_score & {evidence_summary.get('nominal_support_score')} \\\\ coverage & {evidence_summary.get('coverage')} \\\\ weighted\\_coverage & {evidence_summary.get('weighted_coverage')} \\\\ real\\_coverage & {evidence_summary.get('real_coverage')} \\\\ real\\_weighted\\_coverage & {evidence_summary.get('real_weighted_coverage')} \\\\ diversity & {evidence_summary.get('diversity')} \\\\ tool\\_realism\\_score & {evidence_summary.get('tool_realism_score')} \\\\ failures & {evidence_summary.get('failures')} \\\\ \\end{{tabular}}"
                f"\\section*{{Llamadas a Herramientas}}\\begin{{longtable}}{{l|c|c}}Tool & Estado & Latencia(ms) \\\\ \\hline {tool_calls_rows} \\end{{longtable}}"
                "\\section*{Conclusión} (Resumen omitido por brevedad)\n\\end{document}"
            )
            # Compilar LaTeX opcionalmente
            if compile_latex:
                try:
                    import subprocess
                    import shlex
                    cmd = f"pdflatex -interaction=nonstopmode -halt-on-error -output-directory {paper_dir} {tex_path}"
                    subprocess.run(shlex.split(cmd), check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
            try:
                with open(tex_path, "w", encoding="utf-8") as f:
                    f.write(tex_doc)
            except Exception:
                pass

            artifact["paper_paths"] = {"markdown": md_path, "latex": tex_path}
            return {"success": True, "artifact": artifact}
        except Exception as e:
            logger.error(f"Error en pipeline integrado: {e}")
            return {"success": False, "error": str(e)}

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        action = request_data.get("action")
        if action == "reload_config":
            return self.reload_configuration()
        if action == "run_pipeline":
            goal = request_data.get("research_goal", "")
            if not goal:
                return {"success": False, "error": "research_goal requerido"}
            return self.run_pipeline(goal)
        if action == "run_pipeline_integrated":
            goal = request_data.get("research_goal", "")
            domain = request_data.get("domain", "materials_science")
            compile_latex = bool(request_data.get("compile_latex", False))
            if not goal:
                return {"success": False, "error": "research_goal requerido"}
            # Ya estamos en un método async: usar await directamente
            return await self.run_pipeline_integrated_async(goal, domain=domain, compile_latex=compile_latex)
        if action == "run_pipeline_multidomain":
            goal = request_data.get("research_goal", "")
            domains = request_data.get("domains", ["materials_science","biophysics","genomics"]) or []
            compile_latex = bool(request_data.get("compile_latex", False))
            if not goal:
                return {"success": False, "error": "research_goal requerido"}
            results = []
            for d in domains:
                r = await self.run_pipeline_integrated_async(goal, domain=d, compile_latex=compile_latex)
                results.append({"domain": d, **r})
            # Agregación métrica simple
            agg = {"support_score": [], "weighted_coverage": [], "diversity": []}
            for r in results:
                try:
                    summ = r.get("artifact", {}).get("evidence", {}).get("summary", {})
                    if summ.get("support_score") is not None:
                        agg["support_score"].append(summ.get("support_score"))
                    if summ.get("weighted_coverage") is not None:
                        agg["weighted_coverage"].append(summ.get("weighted_coverage"))
                    if summ.get("diversity") is not None:
                        agg["diversity"].append(summ.get("diversity"))
                except Exception:
                    pass
            import statistics
            agg_stats = {}
            for k,v in agg.items():
                if v:
                    agg_stats[k] = {"mean": float(statistics.mean(v)), "max": float(max(v)), "min": float(min(v))}
            return {"success": True, "multi_domain_results": results, "aggregate_metrics": agg_stats}
        if action == "model_benchmark":
            goal = request_data.get("research_goal", "")
            role = request_data.get("role", "bio_hypothesis")
            candidate_models: List[str] = request_data.get("models", []) or []
            if not goal or not candidate_models:
                return {"success": False, "error": "research_goal y models requeridos"}
            baseline_model = self.role_models.get(role)
            scores = []
            for m in candidate_models:
                # Cambiar temporalmente el modelo del rol
                self.role_models[role] = m
                self.wrappers[role] = DynamicRoleLLMWrapper(m, role, self.model_manager)
                r = await self.run_pipeline_integrated_async(goal, domain=request_data.get("domain","materials_science"))
                comp = None
                try:
                    rev_json = r.get("artifact", {}).get("review", "{}")
                    parsed = json.loads(rev_json) if isinstance(rev_json, str) else rev_json
                    comp = parsed.get("evidence_composite")
                except Exception:
                    pass
                scores.append({"model": m, "evidence_composite": comp})
            # Restaurar baseline
            if baseline_model:
                self.role_models[role] = baseline_model
                self.wrappers[role] = DynamicRoleLLMWrapper(baseline_model, role, self.model_manager)
            scores_sorted = sorted(scores, key=lambda x: (x["evidence_composite"] is None, -(x.get("evidence_composite") or 0)))
            return {"success": True, "role": role, "benchmark": scores_sorted}
        return {"success": False, "error": f"Acción desconocida: {action}"}

# --- Integración opcional del orquestador Math/Physics ---
try:
    from app.domains.mathematics.services.math_physics_orchestrator import MathPhysicsOrchestrator  # type: ignore
    _MP_AVAILABLE = True
except Exception:
    MathPhysicsOrchestrator = None  # type: ignore
    _MP_AVAILABLE = False

    
    
def _maybe_route_math_physics(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        domain = request.get("domain")
        if not domain:
            return None
        if domain in ("mathematics", "algebra", "number_theory", "quantum_physics", "quantum_computing", "astronomy", "particle_physics") and _MP_AVAILABLE:
            orchestrator = MathPhysicsOrchestrator()  # type: ignore
            import asyncio
            loop = asyncio.get_event_loop()
            # Reutilizar API de BaseService: process_request
            return loop.run_until_complete(orchestrator.process_request(request))
        return None
    except Exception:
        return None

# hook simple para solicitudes directas al coordinador con domain math/physics
    async def handle_domain_request(self, request: HandleDomainRequestResult) -> HandleDomainRequestResult:
        try:
            routed = _maybe_route_math_physics(request)
            if routed is not None:
                return routed
            return {"success": False, "error": "No route for given domain or orchestrator unavailable"}
        except Exception as e:
            return {"success": False, "error": str(e)}
