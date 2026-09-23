"""
Router Registry - Sistema automático para AXIOM ATLAS
Genera automáticamente la configuración de routers FastAPI

Este archivo es generado automáticamente. NO EDITAR MANUALMENTE.
Para regenerar, ejecutar: python router_registry.py --create
"""

import importlib
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI
from app.exceptions.domain.biology import BiologyError
from app.types.router_registry_types import (
    GetRouterInfoResult,
)

logger = logging.getLogger(__name__)


def _resolve_router_attr(module: Any, router_config: Dict[str, Any]) -> tuple[Any, str]:
    """Resolver la variable de router en un módulo con soporte para alias.

    Busca primero la variable configurada y aplica fallbacks comunes como
    ``router`` cuando no está disponible. Devuelve una tupla con el router y
    el nombre del atributo utilizado.
    """

    router_var = router_config.get('router_var')

    if router_var and hasattr(module, router_var):
        return getattr(module, router_var), router_var

    # Fallbacks comunes
    fallback_candidates: List[str] = []

    # Algunos módulos sólo exponen `router`
    if hasattr(module, 'router'):
        fallback_candidates.append('router')

    # Otros pueden usar el nombre del router sin sufijo personalizado
    name_candidate = router_config.get('name')
    if name_candidate:
        normalized = name_candidate.replace('-', '_')
        if hasattr(module, normalized):
            fallback_candidates.append(normalized)
        normalized_router = f"{normalized}_router"
        if normalized_router != router_var and hasattr(module, normalized_router):
            fallback_candidates.append(normalized_router)

    for candidate in fallback_candidates:
        if hasattr(module, candidate):
            return getattr(module, candidate), candidate

    available = [attr for attr in dir(module) if attr.endswith('_router') or attr == 'router']
    raise AttributeError(
        f"Router variable '{router_var}' no encontrada en {module.__name__}. "
        f"Disponibles: {available or 'ninguna'}"
    )

# Configuración automática de routers por dominio
ROUTER_CONFIG = {
    'mathematics': [
        {
            'name': 'arithmetic',
            'module': 'app.routers.arithmetic',
            'router_var': 'arithmetic_router',
            'prefix': '/api/mathematics/arithmetic',
            'tags': ['arithmetic', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'calculus',
            'module': 'app.routers.calculus',
            'router_var': 'calculus_router',
            'prefix': '/api/mathematics/calculus',
            'tags': ['calculus', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'equations',
            'module': 'app.routers.equations',
            'router_var': 'equations_router',
            'prefix': '/api/mathematics/equations',
            'tags': ['equations', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'statistics',
            'module': 'app.routers.statistics',
            'router_var': 'statistics_router',
            'prefix': '/api/mathematics/statistics',
            'tags': ['statistics', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'graphing',
            'module': 'app.routers.graphing',
            'router_var': 'graphing_router',
            'prefix': '/api/mathematics/graphing',
            'tags': ['graphing', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'advanced_algebra',
            'module': 'app.routers.advanced_algebra',
            'router_var': 'advanced_algebra_router',
            'prefix': '/api/mathematics/advanced-algebra',
            'tags': ['advanced_algebra', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'differential_equations',
            'module': 'app.routers.differential_equations',
            'router_var': 'differential_equations_router',
            'prefix': '/api/mathematics/differential-equations',
            'tags': ['differential_equations', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'analytical_geometry',
            'module': 'app.routers.analytical_geometry',
            'router_var': 'analytical_geometry_router',
            'prefix': '/api/mathematics/analytical-geometry',
            'tags': ['analytical_geometry', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'number_theory',
            'module': 'app.routers.number_theory',
            'router_var': 'number_theory_router',
            'prefix': '/api/mathematics/number-theory',
            'tags': ['number_theory', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'optimization',
            'module': 'app.routers.optimization',
            'router_var': 'optimization_router',
            'prefix': '/api/mathematics/optimization',
            'tags': ['optimization', 'mathematics'],
            'lazy_load': True,
            'aliases': ['/api/optimization', '/api/v1/optimization']
        },
        {
            'name': 'math_nlp',
            'module': 'app.routers.math_nlp',
            'router_var': 'math_nlp_router',
            'prefix': '/api/mathematics/math-nlp',
            'tags': ['math_nlp', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'combinatorics',
            'module': 'app.routers.combinatorics',
            'router_var': 'combinatorics_router',
            'prefix': '/api/mathematics/combinatorics',
            'tags': ['combinatorics', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'advanced_math_nlp',
            'module': 'app.routers.advanced_math_nlp',
            'router_var': 'advanced_math_nlp_router',
            'prefix': '/api/mathematics/advanced-math-nlp',
            'tags': ['advanced_math_nlp', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'pde',
            'module': 'app.routers.pde',
            'router_var': 'pde_router',
            'prefix': '/api/mathematics/pde',
            'tags': ['pde', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'transform',
            'module': 'app.routers.transform',
            'router_var': 'transform_router',
            'prefix': '/api/mathematics/transform',
            'tags': ['transform', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'variational_calculus',
            'module': 'app.routers.variational_calculus',
            'router_var': 'variational_calculus_router',
            'prefix': '/api/mathematics/variational-calculus',
            'tags': ['variational_calculus', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'complex_analysis',
            'module': 'app.routers.complex_analysis',
            'router_var': 'complex_analysis_router',
            'prefix': '/api/mathematics/complex-analysis',
            'tags': ['complex_analysis', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'polynomial',
            'module': 'app.routers.polynomial',
            'router_var': 'polynomial_router',
            'prefix': '/api/mathematics/polynomial',
            'tags': ['polynomial', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'graph_theory',
            'module': 'app.routers.graph_theory',
            'router_var': 'graph_theory_router',
            'prefix': '/api/mathematics/graph-theory',
            'tags': ['graph_theory', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'cryptography',
            'module': 'app.routers.cryptography',
            'router_var': 'cryptography_router',
            'prefix': '/api/mathematics/cryptography',
            'tags': ['cryptography', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'advanced_algorithms',
            'module': 'app.routers.advanced_algorithms',
            'router_var': 'advanced_algorithms_router',
            'prefix': '/api/mathematics/advanced-algorithms',
            'tags': ['advanced_algorithms', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'sequence_oeis',
            'module': 'app.routers.sequence_oeis',
            'router_var': 'router',
            'prefix': '/api/sequences/oeis',
            'tags': ['sequences', 'mathematics'],
            'lazy_load': True
        }
    ],
    'cloud_models': [
        {
            'name': 'huggingface_models',
            'module': 'app.routers.huggingface_models',
            'router_var': 'router',
            'prefix': '/api/huggingface',
            'tags': ['Hugging Face', 'Cloud Models', 'AI', 'Multi-Agent'],
            'lazy_load': True
        }
    ],
    'scientific': [
        {
            'name': 'scientific_ai',
            'module': 'app.routers.scientific_ai',
            'router_var': 'scientific_ai_router',
            'prefix': '/api/scientific/scientific-ai',
            'tags': ['scientific_ai', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'biomedical_nlp',
            'module': 'app.routers.biomedical_nlp',
            'router_var': 'biomedical_nlp_router',
            'prefix': '/api/scientific/biomedical-nlp',
            'tags': ['biomedical_nlp', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'alphafold3',
            'module': 'app.routers.alphafold3',
            'router_var': 'alphafold3_router',
            'prefix': '/api/scientific/alphafold3',
            'tags': ['alphafold3', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'protgpt2_router',
            'module': 'app.routers.protgpt2_router',
            'router_var': 'protgpt2_router',
            'prefix': '/api/scientific/protgpt2',
            'tags': ['protgpt2', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'biogpt',
            'module': 'app.routers.biogpt',
            'router_var': 'biogpt_router',
            'prefix': '/api/scientific/biogpt',
            'tags': ['biogpt', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'clinicalbert',
            'module': 'app.routers.clinicalbert',
            'router_var': 'clinicalbert_router',
            'prefix': '/api/scientific/clinicalbert',
            'tags': ['clinicalbert', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'matscibert',
            'module': 'app.routers.matscibert',
            'router_var': 'matscibert_router',
            'prefix': '/api/scientific/matscibert',
            'tags': ['matscibert', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'scibert',
            'module': 'app.routers.scibert',
            'router_var': 'scibert_router',
            'prefix': '/api/scientific/scibert',
            'tags': ['scibert', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'dnabert2',
            'module': 'app.routers.dnabert2',
            'router_var': 'dnabert2_router',
            'prefix': '/api/scientific/dnabert2',
            'tags': ['dnabert2', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'gnome_materials',
            'module': 'app.routers.gnome_materials',
            'router_var': 'gnome_materials_router',
            'prefix': '/api/scientific/gnome-materials',
            'tags': ['gnome_materials', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'digital_twins',
            'module': 'app.routers.digital_twins_router',
            'router_var': 'router',
            'prefix': '/api/scientific/digital-twins',
            'tags': ['digital_twins', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'lab_automation',
            'module': 'app.routers.lab_automation',
            'router_var': 'router',
            'prefix': '/api/scientific/lab-automation',
            'tags': ['lab_automation', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'computational_chemistry',
            'module': 'app.routers.computational_chemistry',
            'router_var': 'computational_chemistry_router',
            'prefix': '/api/scientific/computational-chemistry',
            'tags': ['computational_chemistry', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'quantum_physics',
            'module': 'app.routers.quantum_physics',
            'router_var': 'quantum_physics_router',
            'prefix': '/api/quantum-physics',
            'tags': ['quantum_physics', 'scientific'],
            'lazy_load': True,
            'aliases': ['/api/scientific/quantum-physics', '/api/v1/quantum-physics']
        },
        {
            'name': 'quantum_computing',
            'module': 'app.routers.quantum_computing',
            'router_var': 'quantum_computing_router',
            'prefix': '/api/quantum-computing',
            'tags': ['quantum_computing', 'scientific'],
            'lazy_load': True,
            'aliases': ['/api/scientific/quantum-computing', '/api/v1/quantum-computing']
        },
        {
            'name': 'quantum_algorithms',
            'module': 'app.routers.quantum_algorithms',
            'router_var': 'quantum_algorithms_router',
            'prefix': '/api/quantum-algorithms',
            'tags': ['quantum_algorithms', 'scientific'],
            'lazy_load': True,
            'aliases': ['/api/scientific/quantum-algorithms', '/api/v1/quantum-algorithms']
        },
        {
            'name': 'ai_scientist_router',
            'module': 'app.routers.ai_scientist_router',
            'router_var': 'ai_scientist_router',
            'prefix': '/api/scientific/ai-scientist',
            'tags': ['ai_scientist', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'causal_discovery',
            'module': 'app.routers.causal_discovery',
            'router_var': 'causal_discovery_router',
            'prefix': '/api/scientific/causal-discovery',
            'tags': ['causal_discovery', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'federated_learning',
            'module': 'app.routers.federated_learning',
            'router_var': 'federated_learning_router',
            'prefix': '/api/scientific/federated-learning',
            'tags': ['federated_learning', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'synthetic_data',
            'module': 'app.routers.synthetic_data',
            'router_var': 'synthetic_data_router',
            'prefix': '/api/scientific/synthetic-data',
            'tags': ['synthetic_data', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'multimodal_reasoning',
            'module': 'app.routers.multimodal_reasoning',
            'router_var': 'multimodal_reasoning_router',
            'prefix': '/api/scientific/multimodal-reasoning',
            'tags': ['multimodal_reasoning', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'scientific_hypothesis',
            'module': 'app.routers.scientific_hypothesis',
            'router_var': 'scientific_hypothesis_router',
            'prefix': '/api/scientific/scientific-hypothesis',
            'tags': ['scientific_hypothesis', 'scientific'],
            'lazy_load': True,
            'aliases': ['/api/scientific-hypothesis', '/api/v1/scientific-hypothesis']
        },
        {
            'name': 'scientific_evaluation',
            'module': 'app.routers.scientific_evaluation',
            'router_var': 'scientific_evaluation_router',
            'prefix': '/api/scientific/scientific-evaluation',
            'tags': ['scientific_evaluation', 'scientific'],
            'lazy_load': True
        },
        {
            'name': 'literature_search',
            'module': 'app.routers.literature_search',
            'router_var': 'literature_search_router',
            'prefix': '/api/scientific/literature-search',
            'tags': ['literature_search', 'scientific'],
            'lazy_load': True,
            'aliases': ['/api/literature-search', '/api/v1/literature-search']
        },
        {
            'name': 'research_cycle',
            'module': 'app.routers.research_cycle',
            'router_var': 'research_cycle_router',
            'prefix': '/api/research-cycle',
            'tags': ['research_cycle', 'scientific'],
            'lazy_load': True,
            'aliases': ['/api/scientific/research-cycle', '/api/v1/research-cycle']
        }
    ],
    'infrastructure': [
        {
            'name': 'cache',
            'module': 'app.routers.cache',
            'router_var': 'cache_router',
            'prefix': '/api/infrastructure/cache',
            'tags': ['cache', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'gpu_accelerator',
            'module': 'app.routers.gpu_accelerator',
            'router_var': 'gpu_accelerator_router',
            'prefix': '/api/infrastructure/gpu-accelerator',
            'tags': ['gpu_accelerator', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'async_processor',
            'module': 'app.routers.async_processor',
            'router_var': 'async_processor_router',
            'prefix': '/api/infrastructure/async-processor',
            'tags': ['async_processor', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'performance_profiler',
            'module': 'app.routers.performance_profiler',
            'router_var': 'performance_profiler_router',
            'prefix': '/api/infrastructure/performance-profiler',
            'tags': ['performance_profiler', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'scalability',
            'module': 'app.routers.scalability',
            'router_var': 'scalability_router',
            'prefix': '/api/infrastructure/scalability',
            'tags': ['scalability', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'monitoring',
            'module': 'app.routers.monitoring',
            'router_var': 'monitoring_router',
            'prefix': '/api/infrastructure/monitoring',
            'tags': ['monitoring', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'experiment_scheduler',
            'module': 'app.routers.experiment_scheduler',
            'router_var': 'experiment_scheduler_router',
            'prefix': '/api/infrastructure/experiment-scheduler',
            'tags': ['experiment_scheduler', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'sandbox_executor',
            'module': 'app.routers.sandbox_executor',
            'router_var': 'sandbox_executor_router',
            'prefix': '/api/infrastructure/sandbox-executor',
            'tags': ['sandbox_executor', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'mlflow_registry',
            'module': 'app.routers.mlflow_registry',
            'router_var': 'mlflow_registry_router',
            'prefix': '/api/infrastructure/mlflow-registry',
            'tags': ['mlflow_registry', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'knowledge_graph_router',
            'module': 'app.routers.knowledge_graph_router',
            'router_var': 'knowledge_graph_router',
            'prefix': '/api/infrastructure/knowledge-graph',
            'tags': ['knowledge_graph', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'mathlab',
            'module': 'app.routers.mathlab',
            'router_var': 'mathlab_router',
            'prefix': '/api/infrastructure/mathlab',
            'tags': ['mathlab', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'mathematical_verification_router',
            'module': 'app.routers.mathematical_verification_router',
            'router_var': 'mathematical_verification_router',
            'prefix': '/api/mathematics/verification',
            'tags': ['mathematical_verification', 'mathematics'],
            'lazy_load': True
        },
        {
            'name': 'workflow_orchestration',
            'module': 'app.routers.workflow_orchestration',
            'router_var': 'workflow_orchestration_router',
            'prefix': '/api/infrastructure/workflow-orchestration',
            'tags': ['workflow_orchestration', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'experiment_tracking',
            'module': 'app.routers.experiment_tracking',
            'router_var': 'experiment_tracking_router',
            'prefix': '/api/infrastructure/experiment-tracking',
            'tags': ['experiment_tracking', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'data_versioning',
            'module': 'app.routers.data_versioning',
            'router_var': 'data_versioning_router',
            'prefix': '/api/infrastructure/data-versioning',
            'tags': ['data_versioning', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'provenance',
            'module': 'app.routers.provenance',
            'router_var': 'provenance_router',
            'prefix': '/api/infrastructure/provenance',
            'tags': ['provenance', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'reproducibility',
            'module': 'app.routers.reproducibility',
            'router_var': 'reproducibility_router',
            'prefix': '/api/infrastructure/reproducibility',
            'tags': ['reproducibility', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'hypothesis_persistence',
            'module': 'app.routers.hypothesis_persistence',
            'router_var': 'hypothesis_persistence_router',
            'prefix': '/api/infrastructure/hypothesis-persistence',
            'tags': ['hypothesis_persistence', 'infrastructure'],
            'lazy_load': True
        },
        {
            'name': 'integrity',
            'module': 'app.routers.integrity',
            'router_var': 'integrity_router',
            'prefix': '/api/infrastructure/integrity',
            'tags': ['integrity', 'infrastructure'],
            'lazy_load': True
        }
    ],
    'medical': [
        {
            'name': 'publications',
            'module': 'app.routers.publications',
            'router_var': 'publications_router',
            'prefix': '/api/medical/publications',
            'tags': ['publications', 'medical'],
            'lazy_load': True
        },
        {
            'name': 'scientific_figures',
            'module': 'app.routers.scientific_figures',
            'router_var': 'scientific_figures_router',
            'prefix': '/api/medical/scientific-figures',
            'tags': ['scientific_figures', 'medical'],
            'lazy_load': True
        },
        {
            'name': 'journal_formatter',
            'module': 'app.routers.journal_formatter',
            'router_var': 'journal_formatter_router',
            'prefix': '/api/medical/journal-formatter',
            'tags': ['journal_formatter', 'medical'],
            'lazy_load': True
        },
        {
            'name': 'supplementary_materials',
            'module': 'app.routers.supplementary_materials',
            'router_var': 'supplementary_materials_router',
            'prefix': '/api/medical/supplementary-materials',
            'tags': ['supplementary_materials', 'medical'],
            'lazy_load': True
        },
        {
            'name': 'perturbation_engine',
            'module': 'app.routers.perturbation_engine',
            'router_var': 'perturbation_engine_router',
            'prefix': '/api/medical/perturbation-engine',
            'tags': ['perturbation_engine', 'medical'],
            'lazy_load': True
        },
        {
            'name': 'advanced_spectrometers',
            'module': 'app.routers.advanced_spectrometers',
            'router_var': 'advanced_spectrometers_router',
            'prefix': '/api/medical/advanced-spectrometers',
            'tags': ['advanced_spectrometers', 'medical'],
            'lazy_load': True
        },
        {
            'name': 'validation_matrix',
            'module': 'app.routers.validation_matrix',
            'router_var': 'validation_matrix_router',
            'prefix': '/api/medical/validation-matrix',
            'tags': ['validation_matrix', 'medical'],
            'lazy_load': True
        },
        {
            'name': 'advanced_gpu_scaling',
            'module': 'app.routers.advanced_gpu_scaling',
            'router_var': 'advanced_gpu_scaling_router',
            'prefix': '/api/medical/advanced-gpu-scaling',
            'tags': ['advanced_gpu_scaling', 'medical'],
            'lazy_load': True
        }
    ]
}


def register_routers(app: FastAPI, config: Optional[Dict[str, Any]] = None) -> None:
    """
    Registrar routers en la aplicación FastAPI de forma automática

    Args:
        app: Instancia de FastAPI
        config: Configuración opcional para filtrar routers
    """
    logger.info("🚀 Iniciando registro automático de routers...")

    # Configuración por defecto
    if config is None:
        config = {}

    domains_to_load = config.get('domains', list(ROUTER_CONFIG.keys()))
    lazy_load = config.get('lazy_load', True)
    preferred_prefix_variants: Dict[str, str] = config.get('preferred_prefix_variants', {})

    logger.info(f"📁 Dominios a cargar: {domains_to_load}")

    total_routers = 0
    included_prefixes: set[str] = set()

    # Pre-validación: duplicados de prefijos en configuración
    dup_issues = validate_duplicate_prefixes()
    if dup_issues:
        for msg in dup_issues:
            logger.warning(f"⚠️ {msg}")

    # Detectar conflictos con prefijos ya presentes en la app (por registro manual en main.py)
    app_conflicts = validate_app_prefix_conflicts(app)
    if app_conflicts:
        for msg in app_conflicts:
            logger.warning(f"⚠️ Conflicto con prefijo ya presente en la app: {msg}")

    # Conjunto de paths ya presentes en la app para detección de duplicados finos
    try:
        existing_paths = {getattr(route, 'path', '') for route in getattr(app, 'routes', []) if hasattr(route, 'path')}
    except BiologyError:
        existing_paths = set()

    # Registrar routers por dominio
    for domain in domains_to_load:
        if domain not in ROUTER_CONFIG:
            logger.warning(f"❌ Dominio no encontrado: {domain}")
            continue

        domain_routers = ROUTER_CONFIG[domain]
        logger.info(f"📂 Registrando {len(domain_routers)} routers del dominio {domain}")

        for router_config in domain_routers:
            try:
                configured_prefix = router_config['prefix']
                name = router_config['name']
                aliases = router_config.get('aliases', [])

                if lazy_load:
                    # Lazy loading: importar solo cuando se necesita
                    module = importlib.import_module(router_config['module'])
                    router, used_attr = _resolve_router_attr(module, router_config)

                    expected_attr = router_config.get('router_var')
                    if expected_attr and used_attr != expected_attr:
                        logger.warning(
                            "⚠️ Router %s usa alias '%s' en lugar de '%s'",  # noqa: G004
                            name,
                            used_attr,
                            expected_attr
                        )
                else:
                    # Importar directamente (no recomendado para producción)
                    module = importlib.import_module(router_config['module'])
                    router, _ = _resolve_router_attr(module, router_config)

                # Registrar bajo prefijo principal y aliases (si existen)
                for cfg_prefix in [configured_prefix] + aliases:
                    # Calcular prefijo efectivo para evitar duplicados
                    router_prefix = getattr(router, 'prefix', '') or ''
                    effective_prefix = cfg_prefix

                    if router_prefix:
                        # Si el router ya define prefijo que empieza por /api o /api/v*, no añadir otro prefijo
                        if router_prefix.startswith('/api'):
                            effective_prefix = ''
                        else:
                            # Evitar duplicar el último segmento (p.ej. /api/infrastructure/monitoring + /monitoring)
                            rp_last = router_prefix.strip('/').split('/')[-1]
                            cp_last = cfg_prefix.strip('/').split('/')[-1] if cfg_prefix else ''
                            if rp_last and cp_last and rp_last == cp_last:
                                # Usar el prefijo de dominio sin el último segmento
                                segments = cfg_prefix.strip('/').split('/')
                                if len(segments) > 1:
                                    effective_prefix = '/' + '/'.join(segments[:-1])
                                else:
                                    effective_prefix = ''
                            else:
                                # Mantener prefijo configurado
                                effective_prefix = cfg_prefix
                    else:
                        effective_prefix = cfg_prefix

                    # Evitar inclusión si la app ya tiene rutas con este prefijo efectivo
                    try:
                        conflict_prefix = cfg_prefix or effective_prefix
                        if conflict_prefix and any(getattr(route, 'path', '').startswith(conflict_prefix) for route in getattr(app, 'routes', [])):
                            logger.info(f"  ⏭️ Saltando {name}: prefijo {conflict_prefix} ya presente en la app")
                            continue
                    except BiologyError:
                        # Defensivo: continuar si la inspección falla
                        pass

                    # Evitar duplicados por paths ya existentes (caso effective_prefix='')
                    try:
                        router_paths = {getattr(r, 'path', '') for r in getattr(router, 'routes', []) if hasattr(r, 'path')}
                        # Construir paths completos aplicando el prefijo efectivo para evitar falsos positivos
                        prefixed_paths = {(effective_prefix + p) if effective_prefix else p for p in router_paths}
                        if prefixed_paths and any((p in existing_paths) for p in prefixed_paths):
                            logger.info(f"  ⏭️ Saltando {name}: rutas ya presentes en la app (con prefijo), evitando duplicados")
                            continue
                    except BiologyError:
                        pass

                    # Evitar duplicados de prefijo dentro de este registro (solo para prefijos no vacíos)
                    if effective_prefix and (effective_prefix in included_prefixes):
                        preferred_name = preferred_prefix_variants.get(effective_prefix)
                        if preferred_name and preferred_name == name:
                            logger.info(f"  ✅ Usando variante preferida para {effective_prefix}: {name}")
                        else:
                            logger.info(f"  ⏭️ Saltando {name}: prefijo duplicado {effective_prefix}")
                            continue

                    # Registrar router
                    app.include_router(
                        router,
                        prefix=effective_prefix,
                        tags=router_config['tags']
                    )

                    if effective_prefix:
                        included_prefixes.add(effective_prefix)
                    # Actualizar conjunto de rutas existentes
                    try:
                        for r in getattr(router, 'routes', []) if hasattr(router, 'routes') else []:
                            p = getattr(r, 'path', None)
                            if p:
                                existing_paths.add(p if not effective_prefix else effective_prefix + p)
                    except BiologyError:
                        pass

                    total_routers += 1
                    logger.info(f"  ✅ {name} -> {effective_prefix or router_prefix}")

            except BiologyError as e:
                logger.error(f"❌ Error registrando router {router_config.get('name', '?')}: {e}")
                continue

    logger.info(f"🎉 Registro completado: {total_routers} routers registrados exitosamente")


def get_router_info() -> GetRouterInfoResult:
    """Obtener información de todos los routers disponibles"""
    total_routers = sum(len(routers) for routers in ROUTER_CONFIG.values())

    return {
        'total_routers': total_routers,
        'domains': list(ROUTER_CONFIG.keys()),
        'config': ROUTER_CONFIG,
        'routers_by_domain': {
            domain: len(routers) for domain, routers in ROUTER_CONFIG.items()
        }
    }


def validate_router_config() -> List[str]:
    """Validar configuración de routers"""
    issues = []

    for domain, routers in ROUTER_CONFIG.items():
        for router in routers:
            # Verificar que el módulo existe
            try:
                importlib.import_module(router['module'])
            except ImportError:
                issues.append(f"Módulo no encontrado: {router['module']}")

            # Verificar que la variable del router existe
            try:
                module = importlib.import_module(router['module'])
                _resolve_router_attr(module, router)
            except AttributeError as exc:
                issues.append(
                    f"Router variable no encontrada para {domain}:{router.get('name')}: {exc}"
                )

    # Añadir chequeo de prefijos duplicados en la configuración
    issues.extend(validate_duplicate_prefixes())

    return issues


def validate_duplicate_prefixes() -> List[str]:
    """Detecta prefijos duplicados en ROUTER_CONFIG y devuelve mensajes de issues"""
    prefix_map: Dict[str, List[str]] = {}
    for domain, routers in ROUTER_CONFIG.items():
        for r in routers:
            prefix = r.get('prefix')
            name = r.get('name')
            if not prefix:
                continue
            owners = prefix_map.setdefault(prefix, [])
            owners.append(f"{domain}:{name}")

    issues: List[str] = []
    for prefix, owners in prefix_map.items():
        if len(owners) > 1:
            issues.append(f"Prefijo duplicado '{prefix}' usado por: {', '.join(owners)}")
    return issues


def validate_app_prefix_conflicts(app: FastAPI) -> List[str]:
    """Detecta prefijos en ROUTER_CONFIG que ya están presentes en rutas de la app"""
    conflicts: List[str] = []
    try:
        existing_paths = [getattr(route, 'path', '') for route in getattr(app, 'routes', [])]
        for domain, routers in ROUTER_CONFIG.items():
            for r in routers:
                prefix = r.get('prefix')
                name = r.get('name')
                if not prefix:
                    continue
                if any(path.startswith(prefix) for path in existing_paths):
                    conflicts.append(f"{domain}:{name} -> {prefix}")
    except BiologyError:
        # Si la inspección de app falla, retornamos sin conflictos
        return conflicts
    return conflicts
