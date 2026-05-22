#!/usr/bin/env python3
"""
FASE 8.2 - COMPARACIÓN DE MODELOS EN LOOPS AUTÓNOMOS
Ejecuta múltiples configuraciones de modelos en diferentes dominios científicos
"""

import sys
import json
import importlib
import time
import inspect
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from copy import deepcopy
from dataclasses import is_dataclass, asdict

try:
    import yaml
except ImportError:  # pragma: no cover - script guard
    print("PyYAML es requerido para actualizar config/agents.yaml. Instálalo con 'pip install pyyaml'.")
    raise

sys.path.insert(0, str(Path(__file__).parent))

# Colores para terminal
class C:
    HEADER = '\033[95m'
    OK = '\033[92m'
    FAIL = '\033[91m'
    INFO = '\033[96m'
    WARN = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg):
    print(f"\n{C.HEADER}{C.BOLD}{'='*80}{C.END}")
    print(f"{C.HEADER}{C.BOLD}{msg:^80}{C.END}")
    print(f"{C.HEADER}{C.BOLD}{'='*80}{C.END}\n")

def print_ok(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.OK}[{ts}] ✅ {msg}{C.END}")

def print_fail(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.FAIL}[{ts}] ❌ {msg}{C.END}")

def print_info(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.INFO}[{ts}] ℹ️  {msg}{C.END}")

def print_warn(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.WARN}[{ts}] ⚠️  {msg}{C.END}")


# ==========================================================================
# HELPERS
# ==========================================================================

def normalize_outcomes(raw_outcomes: Any) -> List[Dict[str, Any]]:
    """Normaliza outcomes provenientes de dict (id->payload) o lista.

    Retorna lista de dicts; cualquier valor no dict se ignora.
    """
    if isinstance(raw_outcomes, dict):
        values = list(raw_outcomes.values())
    elif isinstance(raw_outcomes, list):
        values = raw_outcomes
    else:
        values = []
    return [o for o in values if isinstance(o, dict)]


def json_safe(obj: Any) -> Any:
    """Convierte recursivamente objetos en estructuras JSON-serializables.

    Reglas:
    - Tipos primitivos pasan directo
    - dict/list/tuple/set se normalizan recursivamente
    - Pydantic v2: usa model_dump()
    - Pydantic v1: usa .dict()
    - Dataclasses: asdict()
    - Objetos con to_dict(): se usa
    - Objetos genéricos: expone atributos públicos (vars)
    - Fallback final: str(obj)
    """
    # Primitivos y None
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # Mapas
    if isinstance(obj, dict):
        return {str(json_safe(k)): json_safe(v) for k, v in obj.items()}

    # Secuencias y conjuntos
    if isinstance(obj, (list, tuple, set)):
        return [json_safe(x) for x in obj]

    # Pydantic v2
    if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
        try:
            return json_safe(obj.model_dump())
        except Exception:
            pass

    # Pydantic v1
    if hasattr(obj, "dict") and callable(getattr(obj, "dict")):
        try:
            return json_safe(obj.dict())
        except Exception:
            pass

    # Dataclasses
    if is_dataclass(obj) and not isinstance(obj, type):
        try:
            return json_safe(asdict(obj))  # type: ignore[arg-type]
        except Exception:
            pass

    # API to_dict
    if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict", None)):
        try:
            return json_safe(obj.to_dict())  # type: ignore[attr-defined]
        except Exception:
            pass

    # Atributos públicos
    if hasattr(obj, "__dict__"):
        try:
            data = {k: v for k, v in vars(obj).items() if not callable(v) and not k.startswith("_")}
            return json_safe(data)
        except Exception:
            pass

    # Fallback: representación string
    return str(obj)


def build_call_kwargs(
    signature: inspect.Signature,
    iteration: int,
    default_args: Dict[str, Any],
    domain_name: str,
    config_key: str,
) -> Dict[str, Any]:
    """Construye kwargs para run_iteration a partir de su firma.

    Soporta parámetros: iteration, top_n, limit, domain, iteration_data, config_key.
    Lanza TypeError si existe un parámetro requerido no reconocido.
    """
    call_kwargs: Dict[str, Any] = {}
    for param in signature.parameters.values():
        if param.name == "self" or param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue

        if param.name == "iteration":
            value = iteration
        elif param.name == "top_n":
            value = default_args.get("top_n", 5)
        elif param.name == "limit":
            if "limit" in default_args:
                value = default_args["limit"]
            elif param.default is inspect.Signature.empty:
                value = 5
            else:
                # tiene default, no es necesario incluirlo
                continue
        elif param.name == "domain":
            value = default_args.get("domain", domain_name)
        elif param.name == "iteration_data":
            value = default_args.get("iteration_data")
        elif param.name == "config_key":
            value = config_key
        else:
            if param.default is inspect.Signature.empty:
                raise TypeError(
                    f"run_iteration de {domain_name} requiere parámetro '{param.name}' sin valor predeterminado"
                )
            continue

        call_kwargs[param.name] = value

    return call_kwargs

# ============================================================================
# CONFIGURACIONES DE MODELOS
# ============================================================================

MODEL_CONFIG_SPECS = {
    "baseline_local": {
        "name": "Baseline Local (Ollama 7-8B)",
        "description": "Configuración original con modelos locales de 7B-8B.",
        "agents_overrides": None,
        "param_overrides": {},
        "notes": [
            "Referencia actual: utiliza los modelos definidos en config/agents.yaml antes de la comparación."
        ],
        "tags": ["baseline", "ollama"]
    },
    "hf_deepseek_v3": {
        "name": "DeepSeek-V3 Planner + Scientific Mix",
        "description": "DeepSeek-V3 para planificación y revisión, Qwen coder 32B y Meta-Llama 3.1 405B para publicación.",
        "agents_overrides": {
            "orchestrator": "deepseek-ai/DeepSeek-V3",
            "bio_hypothesis": "Qwen/Qwen2.5-72B-Instruct",
            "physchem_coder": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "reviewer": "deepseek-ai/DeepSeek-V3",
            "publisher": "meta-llama/Meta-Llama-3.1-405B-Instruct"
        },
        "param_overrides": {
            "orchestrator": {"temperature": 0.25, "max_new_tokens": 768},
            "bio_hypothesis": {"temperature": 0.55, "max_new_tokens": 896},
            "physchem_coder": {"temperature": 0.35, "max_new_tokens": 820},
            "reviewer": {"temperature": 0.25, "max_new_tokens": 640},
            "publisher": {"temperature": 0.60, "max_new_tokens": 900}
        },
        "notes": [
            "DeepSeek-V3 (Hugging Face, 2024-12): 671B totales / 37B activos con razonamiento reflejo distilado.",
            "Qwen2.5-72B y Meta-Llama 3.1 405B disponibles vía router.huggingface.co (Inference Providers, 2025-07)."
        ],
        "tags": ["huggingface", "deepseek", "sota"]
    },
    "hf_qwen72_science": {
        "name": "Qwen2.5 Science Max",
        "description": "Qwen2.5-72B para planificación/hipótesis/revisión, coder 32B y Meta-Llama 405B para síntesis.",
        "agents_overrides": {
            "orchestrator": "Qwen/Qwen2.5-72B-Instruct",
            "bio_hypothesis": "Qwen/Qwen2.5-72B-Instruct",
            "physchem_coder": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "reviewer": "Qwen/Qwen2.5-72B-Instruct",
            "publisher": "meta-llama/Meta-Llama-3.1-405B-Instruct"
        },
        "param_overrides": {
            "orchestrator": {"temperature": 0.30, "max_new_tokens": 820},
            "bio_hypothesis": {"temperature": 0.52, "max_new_tokens": 900},
            "physchem_coder": {"temperature": 0.32, "max_new_tokens": 820},
            "reviewer": {"temperature": 0.30, "max_new_tokens": 720},
            "publisher": {"temperature": 0.58, "max_new_tokens": 920}
        },
        "notes": [
            "Qwen2.5-72B (Hugging Face model card, 2024-07-23): soporte 128K contexto, mejoras en matemáticas/código.",
            "Meta-Llama 3.1 405B Instruct utilizado para reportes con estilo consistente."
        ],
        "tags": ["huggingface", "qwen", "sota"]
    },
    "hf_frontier_reflect": {
        "name": "Frontier Reflective Mix",
        "description": "Meta-Llama 405B para orquestación/publicación, DeepSeek reflejo 32B para revisión y Qwen coder.",
        "agents_overrides": {
            "orchestrator": "meta-llama/Meta-Llama-3.1-405B-Instruct",
            "bio_hypothesis": "Qwen/Qwen2.5-72B-Instruct",
            "physchem_coder": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "reviewer": "DeepSeek-R1-Distill-Qwen-32B",
            "publisher": "meta-llama/Meta-Llama-3.1-405B-Instruct"
        },
        "param_overrides": {
            "orchestrator": {"temperature": 0.28, "max_new_tokens": 780},
            "bio_hypothesis": {"temperature": 0.50, "max_new_tokens": 880},
            "physchem_coder": {"temperature": 0.33, "max_new_tokens": 820},
            "reviewer": {"temperature": 0.27, "max_new_tokens": 640},
            "publisher": {"temperature": 0.62, "max_new_tokens": 920}
        },
        "notes": [
            "DeepSeek-R1-Distill-Qwen-32B: razonamiento reflexivo destilado, reduce coste vs DeepSeek-V3 completo.",
            "Meta-Llama 3.1 405B Instruct (Meta AI, 2025-06) como 'Terminus' interno para redacción final."
        ],
        "tags": ["huggingface", "meta-llama", "deepseek", "hybrid"]
    }
}

# ============================================================================
# DOMINIOS CIENTÍFICOS
# ============================================================================

DOMAINS = {
    "neuroscience": {
        "module": "app.autonomous.pipelines.neuroscience_loop",
        "class": "NeuroscienceLoop",
        "description": "Análisis de neuroimagen multimodal",
        "expected_time": "~45s"
    },
    "mathematics": {
        "module": "app.autonomous.pipelines.mathematics_loop",
        "class": "MathematicsLoop",
        "description": "Generación de conjeturas matemáticas",
        "expected_time": "~40s"
    },
    "chemistry": {
        "module": "app.autonomous.pipelines.chemistry_loop",
        "class": "ChemistryLoop",
        "description": "Diseño molecular y optimización",
        "expected_time": "~50s"
    },
    "quantum": {
        "module": "app.autonomous.pipelines.quantum_loop",
        "class": "QuantumLoop",
        "description": "Optimización de algoritmos cuánticos",
        "expected_time": "~35s"
    }
}

DOMAIN_DEFAULT_ARGUMENTS = {
    "chemistry": {"top_n": 5},
    "neuroscience": {"top_n": 5},
    "mathematics": {"limit": 5, "domain": "number_theory"},
}

CONFIG_DIR = Path(__file__).parent / "config"
AGENTS_FILE = CONFIG_DIR / "agents.yaml"
ITERATIONS_PER_DOMAIN = 1
SLEEP_BETWEEN_RUNS = 2.0
SLEEP_BETWEEN_CONFIGS = 4.0


def load_agents_yaml() -> Dict[str, Any]:
    """Carga config/agents.yaml como diccionario"""
    if not AGENTS_FILE.exists():
        raise FileNotFoundError(f"No se encontró {AGENTS_FILE}")
    with AGENTS_FILE.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def write_agents_yaml(data: Dict[str, Any]) -> None:
    """Escribe config/agents.yaml preservando orden y UTF-8"""
    AGENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with AGENTS_FILE.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)


def build_agents_config(
    base_config: Dict[str, Any],
    model_overrides: Optional[Dict[str, str]],
    param_overrides: Optional[Dict[str, Dict[str, Any]]]
) -> Dict[str, Any]:
    """Genera nueva configuración de agents.yaml aplicando overrides sin mutar el original"""
    config = deepcopy(base_config)
    roles = config.get("roles", {})

    if model_overrides:
        for role, model in model_overrides.items():
            if role not in roles:
                raise KeyError(f"Rol '{role}' no existe en agents.yaml")
            roles[role]["model"] = model

    if param_overrides:
        for role, overrides in param_overrides.items():
            if role not in roles:
                raise KeyError(f"Rol '{role}' no existe en agents.yaml")
            params = roles[role].setdefault("params", {})
            params.update(overrides)

    return config


def extract_role_models(config: Dict[str, Any]) -> Dict[str, str]:
    """Devuelve mapa rol→modelo"""
    return {
        role: details.get("model", "(desconocido)")
        for role, details in (config.get("roles", {}) or {}).items()
    }


def extract_role_params(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Devuelve parámetros por rol"""
    return {
        role: details.get("params", {})
        for role, details in (config.get("roles", {}) or {}).items()
    }


def validate_agents_config(config_dict: Dict[str, Any], config_key: str) -> None:
    """Valida estructura usando schema oficial"""
    try:
        from app.config.yaml_validator import AgentsConfig

        AgentsConfig(**config_dict)
        print_ok(f"agents.yaml validado para configuración '{config_key}'")
    except Exception as exc:  # pragma: no cover - validación defensiva
        print_fail(f"Validación de agents.yaml falló para '{config_key}': {exc}")
        raise


def apply_agents_configuration(
    base_config: Dict[str, Any],
    spec: Dict[str, Any],
    config_key: str
) -> tuple[Dict[str, Any], Dict[str, str], Dict[str, Dict[str, Any]]]:
    """Construye, valida y aplica agents.yaml para una configuración concreta"""
    prepared = build_agents_config(
        base_config,
        spec.get("agents_overrides"),
        spec.get("param_overrides")
    )

    validate_agents_config(prepared, config_key)
    write_agents_yaml(prepared)
    importlib.invalidate_caches()

    # Intentar refrescar MultiAgentCoordinator para nuevas asignaciones
    try:
        from app.services.multi_agent_coordinator import MultiAgentCoordinator

        coordinator = MultiAgentCoordinator(auto_reload=True, use_huggingface=True)
        coordinator.reload_configuration()
        print_ok("MultiAgentCoordinator recargó la configuración actualizada")
    except (ImportError, AttributeError, RuntimeError) as exc:  # pragma: no cover - ambientes parciales
        print_warn(f"No se pudo recargar coordinator automáticamente: {exc}")

    return prepared, extract_role_models(prepared), extract_role_params(prepared)

# ============================================================================
# EJECUCIÓN DE LOOPS
# ============================================================================

def run_loop_iteration(
    domain_name: str,
    config_key: str,
    config_meta: Dict[str, Any],
    iteration: int,
    role_models: Dict[str, str],
    role_params: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Ejecuta una iteración de un loop con una configuración específica"""

    domain = DOMAINS[domain_name]
    print_info(f"{domain_name.upper()} | {config_meta['name']} | Iteración {iteration}")

    start_time = time.time()

    try:
        module = importlib.import_module(domain["module"])
        LoopClass = getattr(module, domain["class"])
        loop = LoopClass()

        run_iteration_callable = getattr(loop, "run_iteration")
        signature = inspect.signature(run_iteration_callable)

        default_args = DOMAIN_DEFAULT_ARGUMENTS.get(domain_name, {})
        call_kwargs = build_call_kwargs(
            signature=signature,
            iteration=iteration,
            default_args=default_args,
            domain_name=domain_name,
            config_key=config_key,
        )

        result = run_iteration_callable(**call_kwargs)
        duration = time.time() - start_time

        raw_outcomes = result.get("outcomes", [])
        metrics = result.get("metrics", {})
        outcomes_iter = normalize_outcomes(raw_outcomes)

        # Mapeo de campos de score según dominio (diferentes loops usan diferentes nombres)
        score_fields = ["score", "novelty_score", "avg_score", "fitness"]
        evidence_fields = ["evidence_support", "avg_evidence", "support_score"]

        scores = []
        for o in outcomes_iter:
            if isinstance(o, dict):
                for field in score_fields:
                    if field in o and o[field] is not None:
                        scores.append(float(o[field]))
                        break
        avg_score = sum(scores) / len(scores) if scores else 0

        evidence_supports = []
        for o in outcomes_iter:
            if isinstance(o, dict):
                for field in evidence_fields:
                    if field in o and o[field] is not None:
                        evidence_supports.append(float(o[field]))
                        break
        avg_evidence = sum(evidence_supports) / len(evidence_supports) if evidence_supports else 0

        print_ok(
            f"Completado en {duration:.1f}s - Score: {avg_score:.3f}, Evidence: {avg_evidence:.3f}"
        )

        return {
            "domain": domain_name,
            "config": config_key,
            "config_name": config_meta["name"],
            "iteration": iteration,
            "success": True,
            "duration_seconds": duration,
            "outcomes_count": len(outcomes_iter),
            "avg_score": avg_score,
            "avg_evidence_support": avg_evidence,
            "metrics": metrics,
            "result": result,
            "role_models": role_models,
            "config_tags": config_meta.get("tags", []),
            "config_description": config_meta.get("description"),
            "role_params": role_params,
            "timestamp": datetime.now().isoformat()
        }

    except (TypeError, AttributeError, RuntimeError, ValueError) as exc:  # pragma: no cover - logging informativo
        duration = time.time() - start_time
        print_fail(f"Error ejecutando {domain_name} con {config_meta['name']}: {exc}")

        return {
            "domain": domain_name,
            "config": config_key,
            "config_name": config_meta["name"],
            "iteration": iteration,
            "success": False,
            "duration_seconds": duration,
            "error": str(exc),
            "role_models": role_models,
            "config_tags": config_meta.get("tags", []),
            "config_description": config_meta.get("description"),
            "role_params": role_params,
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# COMPARACIÓN COMPLETA
# ============================================================================

def run_full_comparison(domain_filter: Optional[List[str]] = None):
    """Ejecuta la comparación completa de modelos

    Args:
        domain_filter: Lista opcional de dominios a ejecutar. Si es None, se ejecutan todos.
    """

    print_header("FASE 8.2 - COMPARACIÓN DE MODELOS EN LOOPS AUTÓNOMOS")

    print_info("Configuraciones a probar:")
    for key, spec in MODEL_CONFIG_SPECS.items():
        print(f"  • [{key}] {spec['name']}: {spec['description']}")
        for note in spec.get("notes", [])[:2]:
            print(f"      - {note}")
        if len(spec.get("notes", [])) > 2:
            print("      - ...")

    print_info("\nDominios científicos:")
    selected_domains = list(DOMAINS.keys()) if not domain_filter else [d for d in domain_filter if d in DOMAINS]
    if domain_filter and not selected_domains:
        print_warn("No se encontraron dominios válidos en el filtro proporcionado; se ejecutarán todos.")
        selected_domains = list(DOMAINS.keys())
    for name in selected_domains:
        domain = DOMAINS[name]
        print(f"  • {name.capitalize()}: {domain['description']} ({domain['expected_time']})")

    if sys.stdin.isatty():
        input("\nPresiona ENTER para comenzar... ")

    base_agents_config = load_agents_yaml()
    backup_path = AGENTS_FILE.with_suffix(".backup")
    with backup_path.open("w", encoding="utf-8") as backup_handle:
        yaml.safe_dump(base_agents_config, backup_handle, sort_keys=False, allow_unicode=True)
    print_info(f"Respaldo de agents.yaml creado en {backup_path}")

    all_results: List[Dict[str, Any]] = []
    total_start = time.time()

    try:
        for config_idx, (config_key, spec) in enumerate(MODEL_CONFIG_SPECS.items(), start=1):
            print_header(f"CONFIGURACIÓN {config_idx}/{len(MODEL_CONFIG_SPECS)}: {spec['name']}")

            _, role_models, role_params = apply_agents_configuration(
                base_agents_config,
                spec,
                config_key
            )

            print_info("Modelos por rol:")
            for role, model in role_models.items():
                print(f"  • {role}: {model}")

            print_info("Parámetros por rol:")
            for role, params in role_params.items():
                if params:
                    print(f"  • {role}: {params}")

            for domain_name in selected_domains:
                print_header(f"DOMINIO: {domain_name.upper()} | {spec['name']}")

                for iteration in range(1, ITERATIONS_PER_DOMAIN + 1):
                    result = run_loop_iteration(
                        domain_name,
                        config_key,
                        spec,
                        iteration,
                        role_models,
                        role_params
                    )
                    all_results.append(result)

                    time.sleep(SLEEP_BETWEEN_RUNS)

            if config_idx < len(MODEL_CONFIG_SPECS):
                print_info(f"Esperando {SLEEP_BETWEEN_CONFIGS:.0f}s antes de la siguiente configuración...")
                time.sleep(SLEEP_BETWEEN_CONFIGS)

    finally:
        write_agents_yaml(base_agents_config)
        importlib.invalidate_caches()
        print_warn("agents.yaml restaurado a la configuración original")

    total_duration = time.time() - total_start

    print_header("ANÁLISIS DE RESULTADOS")

    by_domain: Dict[str, List[Dict[str, Any]]] = {}
    by_config: Dict[str, List[Dict[str, Any]]] = {}

    for result in all_results:
        domain_results = by_domain.setdefault(result["domain"], [])
        config_results = by_config.setdefault(result["config"], [])
        if result["success"]:
            domain_results.append(result)
            config_results.append(result)

    print("\n" + "=" * 110)
    print(f"{'Dominio':<15} {'Config':<18} {'Iter':<6} {'Status':<8} {'Duración':<12} {'Score':<10} {'Evidence':<10} {'Outcomes':<10}")
    print("=" * 110)

    domain_stats: Dict[str, Dict[str, Any]] = {}
    config_stats: Dict[str, Dict[str, Any]] = {}

    for result in all_results:
        status = "✅ OK" if result["success"] else "❌ FALLO"
        print(f"{result['domain'].capitalize():<15} {result['config_name']:<18.18} {result['iteration']:<6} {status:<8} "
              f"{result['duration_seconds']:>6.1f}s{'':5} {result.get('avg_score', 0):<10.3f} "
              f"{result.get('avg_evidence_support', 0):<10.3f} {result.get('outcomes_count', 0):<10}")

    print("=" * 110)

    for domain_name, domain_results_list in by_domain.items():
        scores = [r['avg_score'] for r in domain_results_list]
        evidences = [r['avg_evidence_support'] for r in domain_results_list]
        durations = [r['duration_seconds'] for r in domain_results_list]

        domain_stats[domain_name] = {
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "avg_evidence": sum(evidences) / len(evidences) if evidences else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "iterations": len(domain_results_list)
        }

    for config_key, config_results_list in by_config.items():
        scores = [r['avg_score'] for r in config_results_list]
        evidences = [r['avg_evidence_support'] for r in config_results_list]
        durations = [r['duration_seconds'] for r in config_results_list]
        config_stats[config_key] = {
            "name": MODEL_CONFIG_SPECS[config_key]['name'],
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "avg_evidence": sum(evidences) / len(evidences) if evidences else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "successful_runs": len(config_results_list),
            "role_models": config_results_list[-1]['role_models'] if config_results_list else {},
            "role_params": config_results_list[-1]['role_params'] if config_results_list else {}
        }

    print("\n" + "=" * 80)
    print("RESUMEN EJECUTIVO")
    print("=" * 80)

    successful = [r for r in all_results if r['success']]
    failed = [r for r in all_results if not r['success']]

    print(f"\n✅ Ejecuciones exitosas: {len(successful)}/{len(all_results)}")
    print(f"❌ Ejecuciones fallidas: {len(failed)}/{len(all_results)}")
    print(f"⏱️  Tiempo total: {total_duration/60:.1f} minutos ({total_duration:.0f}s)")

    if domain_stats:
        print("\n📊 PROMEDIOS POR DOMINIO:")
        for domain_name, stats in domain_stats.items():
            print(f"  {domain_name.capitalize()}: score={stats['avg_score']:.3f}, evidence={stats['avg_evidence']:.3f}, tiempo={stats['avg_duration']:.1f}s, iter={stats['iterations']}")

    if config_stats:
        print("\n🧠 PROMEDIOS POR CONFIGURACIÓN:")
        for config_key, stats in config_stats.items():
            print(f"  {stats['name']}: score={stats['avg_score']:.3f}, evidence={stats['avg_evidence']:.3f}, tiempo={stats['avg_duration']:.1f}s, runs={stats['successful_runs']}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"model_comparison_phase8_{timestamp}.json"

    payload = {
        "phase": "FASE 8.2 - Model Comparison",
        "execution_date": datetime.now().isoformat(),
        "total_duration_seconds": total_duration,
        "configs_tested": MODEL_CONFIG_SPECS,
        "domains": DOMAINS,
        "results": all_results,
        "summary": {
            "by_domain": domain_stats,
            "by_config": config_stats,
            "successful": len(successful),
            "failed": len(failed),
            "total": len(all_results)
        }
    }

    with open(output_file, 'w', encoding='utf-8') as handle:
        json.dump(json_safe(payload), handle, indent=2)

    print(f"\n💾 Resultados guardados en: {output_file}\n")

    return all_results

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        # CLI mínima para filtrar dominios: --domains chemistry,quantum
        import argparse

        parser = argparse.ArgumentParser(description="FASE 8.2 - Comparación de modelos")
        parser.add_argument(
            "--domains",
            type=str,
            default=None,
            help="Lista separada por comas de dominios a ejecutar (p.ej., chemistry,mathematics,quantum,neuroscience)",
        )
        args = parser.parse_args()

        domain_filter = None
        if args.domains:
            domain_filter = [d.strip().lower() for d in args.domains.split(",") if d.strip()]

        results = run_full_comparison(domain_filter=domain_filter)
        print_ok("Comparación completada exitosamente")
    except KeyboardInterrupt:
        print_warn("\nEjecución interrumpida por el usuario")
        sys.exit(1)
    except (ValueError, RuntimeError, ImportError, OSError) as e:
        print_fail(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
