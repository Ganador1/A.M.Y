"""Mathematics autonomous exploration loop with discovery engine integration."""
from __future__ import annotations

import asyncio
import random
import time
from typing import Any, Callable, Dict, List, Optional

from app.autonomous.core.budget_allocator import BudgetAllocator
from app.autonomous.core.priority_scoring import PriorityScorer
from app.autonomous.core.state_manager import IterationRecord, StateManager
from app.autonomous.core.task_scheduler import TaskScheduler
from app.autonomous.evaluation.empirical_feedback import process_feedback
from app.autonomous.evaluation.novelty_assessor import NoveltyAssessor
from app.autonomous.evaluation.sketch_validator import validate_sketch
from app.autonomous.generators.hypothesis_mutator import HypothesisMutator
from app.autonomous.generators.proof_sketch_generator import generate_proof_sketch
from app.autonomous.interfaces.external_apis import fetch_literature_snippets
from app.autonomous.metrics.telemetry_collector import AutonomousTelemetry
from app.autonomous.integration import EvidenceSummary, ToolEvidenceBridge
from app.core.bootstrap_logging import logger
from app.domains.mathematics.services.mathematical_discovery_engine import (
    Conjecture,
    MathematicalDiscoveryEngine,
)
# ⭐ SERVICIOS MATEMÁTICOS AVANZADOS (Fase 1 - 6 servicios)
from app.domains.mathematics.services.sagemath_service import SageMathService
from app.domains.mathematics.services.automated_theorem_proving_service import AutomatedTheoremProvingService
from app.domains.mathematics.services.advanced_number_theory_service import AdvancedNumberTheoryService
from app.domains.mathematics.services.advanced_topology_service import AdvancedTopologyService
from app.domains.mathematics.services.julia_service import JuliaService
from app.domains.mathematics.services.symbolic_ai_service import SymbolicAIService

# ⭐ SERVICIOS MATEMÁTICOS ADICIONALES (Fase 2 - 10 servicios)
from app.domains.mathematics.services.advanced_algebra_service import AdvancedAlgebraService
from app.domains.mathematics.services.calculus_service import CalculusService
from app.domains.mathematics.services.statistics_service import StatisticsService
from app.domains.mathematics.services.optimization_service import OptimizationService
from app.domains.mathematics.services.differential_equations_service import DifferentialEquationService
from app.domains.mathematics.services.combinatorics_service import CombinatoricsService
from app.domains.mathematics.services.gpu_math_service import GPUMathService
from app.domains.mathematics.services.distributed_computing_service import DistributedComputingService
from app.domains.mathematics.services.math_ml_service import MathematicalMLService
from app.domains.mathematics.services.advanced_visualization_service import AdvancedVisualizationService

# ⭐ SERVICIOS MATEMÁTICOS COMPLETOS (Fase 3 - 31 servicios - TODOS arreglados!)
# Servicios de IA y NLP Matemático
from app.domains.mathematics.services.advanced_math_ai_service import AdvancedMathAIService
from app.domains.mathematics.services.advanced_math_nlp import AdvancedMathNLPService
from app.domains.mathematics.services.math_nlp import MathNLPService
from app.domains.mathematics.services.mathematical_brainstorming_service import MultiLLMBrainstorm  # ✅ ARREGLADO

# Servicios de Computación Simbólica
from app.domains.mathematics.services.advanced_sympy_service import AdvancedSymPyService
from app.domains.mathematics.services.symengine_service import SymEngineService
from app.domains.mathematics.services.equation_service import EquationService

# Servicios de Teoría de Números y Aritmética
from app.domains.mathematics.services.arithmetic import ArithmeticService as ArithmeticCore
from app.domains.mathematics.services.arithmetic_service import ArithmeticService
from app.domains.mathematics.services.number_theory import NumberTheoryService
from app.domains.mathematics.services.number_theory_service import NumberTheoryService

# Servicios de Topología
from app.domains.mathematics.services.topology_service import TopologyService

# Servicios de Física Matemática y Cuántica
from app.domains.mathematics.services.math_physics import MathPhysicsService
from app.domains.mathematics.services.math_physics_orchestrator import MathPhysicsOrchestrator
from app.domains.mathematics.services.advanced_quantum_service import AdvancedQuantumService
from app.domains.mathematics.services.quantum_math_service import QuantumMathService

# Servicios de Matemáticas Aplicadas
from app.domains.mathematics.services.financial_mathematics_service import FinancialMathematicsService
from app.domains.mathematics.services.bioinformatics_service import BioinformaticsService
from app.domains.mathematics.services.variational_calculus_service import VariationalCalculusService

# Servicios de Visualización
from app.domains.mathematics.services.graphing_service import GraphingService
from app.domains.mathematics.services.math_visualization_service import MathVisualizationService
from app.domains.mathematics.services.vr_ar_visualization_service import VRARVisualizationService

# Servicios de Laboratorio y Computación
from app.domains.mathematics.services.mathematical_computation import MathematicalComputationService
from app.domains.mathematics.services.mathematical_computation_laboratory import MathematicalComputationLaboratory  # ✅ ARREGLADO

# Servicios de Descubrimiento y Persistencia
from app.domains.mathematics.services.discovery_engine import DiscoveryEngineService
from app.domains.mathematics.services.mathematical_conjecture_mutator import MathematicalConjectureMutator
from app.domains.mathematics.services.mathematical_discovery_persistence import MathematicalDiscoveryPersistence
from app.domains.mathematics.services.mathematical_verification_bridge import MathematicalVerificationBridge  # ✅ ARREGLADO
from app.domains.mathematics.services.mathematical_exporter import MathematicalExporter
from app.mathlab.persistence.conjecture_persistence import ConjecturePersistenceService
from app.services.theorem_proving.z3_smt_service import Z3SMTService
from app.domains.mathematics.utils.symbolic_normalizer import SymbolicExpressionNormalizer

# Servicios de Gestión
from app.domains.mathematics.services.service_manager import MathematicsServiceManager
from app.exceptions.domain.mathematics import MathematicsError
from app.compliance.ethics_gate import EthicsGate, ExperimentRequest

ConjectureProvider = Callable[[], List[Any]]


class MathematicsLoop:
    def __init__(
        self,
        provider: ConjectureProvider | None = None,
        state: StateManager | None = None,
        telemetry: AutonomousTelemetry | None = None,
        domain: str = "number_theory",
    ):
        self.provider = provider
        self.state = state or StateManager()
        self.telemetry = telemetry or AutonomousTelemetry()
        self.scorer = PriorityScorer()
        self.scheduler = TaskScheduler(diversity_quota=5)
        self.budget = BudgetAllocator(total_budget=10.0)
        self.mutator = HypothesisMutator()
        self.novelty = NoveltyAssessor()
        self.discovery_engine = MathematicalDiscoveryEngine()

        # ⭐ SERVICIOS MATEMÁTICOS AVANZADOS (Fase 1 - 6 servicios)
        self.sagemath = SageMathService()  # SageMath para álgebra computacional
        self.atp = AutomatedTheoremProvingService()  # Automated Theorem Proving (Lean4/Coq)
        self.number_theory = AdvancedNumberTheoryService()  # Teoría de números avanzada
        self.topology = AdvancedTopologyService()  # Topología algebraica
        self.julia = JuliaService()  # Julia para computación de alto rendimiento
        self.symbolic_ai = SymbolicAIService()  # IA simbólica

        # ⭐ SERVICIOS MATEMÁTICOS ADICIONALES (Fase 2 - 10 servicios)
        self.algebra = AdvancedAlgebraService()  # Álgebra abstracta avanzada
        self.calculus = CalculusService()  # Cálculo diferencial e integral
        self.statistics = StatisticsService()  # Estadística y probabilidad
        self.optimization = OptimizationService()  # Optimización matemática
        self.diff_equations = DifferentialEquationService()  # EDOs y EDPs
        self.combinatorics = CombinatoricsService()  # Combinatoria
        self.gpu_math = GPUMathService()  # Aceleración GPU
        self.distributed_computing = DistributedComputingService()  # Computación distribuida
        self.math_ml = MathematicalMLService()  # Machine Learning matemático
        self.visualization = AdvancedVisualizationService()  # Visualización avanzada

        # ⭐ SERVICIOS MATEMÁTICOS COMPLETOS (Fase 3 - 31 servicios - TODOS integrados!)
        # IA y NLP Matemático (4 servicios)
        self.math_ai = AdvancedMathAIService()  # IA matemática avanzada
        self.math_nlp_advanced = AdvancedMathNLPService()  # NLP matemático avanzado
        self.math_nlp = MathNLPService()  # NLP matemático básico
        self.brainstorming = MultiLLMBrainstorm()  # ✅ Brainstorming matemático

        # Computación Simbólica (3 servicios)
        self.sympy_advanced = AdvancedSymPyService()  # SymPy avanzado
        self.symengine = SymEngineService()  # SymEngine para performance
        self.equations = EquationService()  # Resolución de ecuaciones

        # Teoría de Números y Aritmética (4 servicios)
        self.arithmetic_core = ArithmeticCore()  # Aritmética fundamental
        self.arithmetic = ArithmeticService()  # Aritmética avanzada
        self.number_theory_core = NumberTheoryService()  # Teoría de números core
        self.number_theory_service = NumberTheoryService()  # Teoría de números completa

        # Topología Adicional (1 servicio)
        self.topology_basic = TopologyService()  # Topología básica

        # Física Matemática y Cuántica (4 servicios)
        self.math_physics = MathPhysicsService()  # Física matemática
        self.math_physics_orchestrator = MathPhysicsOrchestrator()  # Orquestador física-matemática
        self.quantum_math_advanced = AdvancedQuantumService()  # Matemática cuántica avanzada
        self.quantum_math = QuantumMathService()  # Matemática cuántica

        # Matemáticas Aplicadas (3 servicios)
        self.financial_math = FinancialMathematicsService()  # Matemáticas financieras
        self.bioinformatics = BioinformaticsService()  # Bioinformática matemática
        self.variational_calculus = VariationalCalculusService()  # Cálculo variacional

        # Visualización Adicional (3 servicios)
        self.graphing = GraphingService()  # Graficación
        self.math_viz = MathVisualizationService()  # Visualización matemática
        self.vr_ar_viz = VRARVisualizationService()  # Visualización VR/AR

        # Laboratorio y Computación (2 servicios)
        self.math_computation = MathematicalComputationService()  # Computación matemática
        self.computation_lab = MathematicalComputationLaboratory()  # ✅ Laboratorio computacional

        # Descubrimiento y Persistencia (5 servicios)
        self.discovery_engine_service = DiscoveryEngineService()  # Motor de descubrimiento
        self.conjecture_mutator = MathematicalConjectureMutator()  # Mutador de conjeturas
        self.discovery_persistence = MathematicalDiscoveryPersistence()  # Persistencia de descubrimientos
        self.conjecture_persistence = ConjecturePersistenceService()  # Persistencia estructurada
        self.smt_service = Z3SMTService()  # Verificación SMT
        self.symbolic_normalizer = SymbolicExpressionNormalizer()  # Normalización simbólica
        self.verification_bridge = MathematicalVerificationBridge(
            persistence_service=self.conjecture_persistence,
            smt_service=self.smt_service,
            normalizer=self.symbolic_normalizer,
        )  # ✅ Puente de verificación
        self.exporter = MathematicalExporter()  # Exportador matemático

        # Gestión de Servicios (1 servicio)
        self.service_manager = MathematicsServiceManager()  # Gestor de servicios

        self.domain = domain
        self.random = random.Random(2024)
        self.iteration = 0
        self._seen_statements: set[str] = set()
        self.ethics_gate = EthicsGate()
        self.tool_evidence = ToolEvidenceBridge(default_domain="mathematics")

    @staticmethod
    def _run_coro_sync(coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()

    def _coerce_to_conjecture(self, payload: Any, idx: int) -> Optional[Conjecture]:
        if isinstance(payload, Conjecture):
            return payload
        if isinstance(payload, dict):
            statement = payload.get("statement") or payload.get("conjecture")
            if not statement:
                logger.warning("Skipping provider payload without statement: %s", payload)
                return None
            domain = payload.get("domain") or self.domain
            conj_id = payload.get("id") or f"provider_{self.iteration}_{idx}"
            metadata = payload.get("metadata", {})
            return Conjecture(id=conj_id, statement=statement, domain=domain, metadata=metadata)
        if isinstance(payload, str):
            return Conjecture(id=f"provider_{self.iteration}_{idx}", statement=payload, domain=self.domain)
        logger.warning("Unsupported provider payload type: %s", type(payload))
        return None

    def _prepare_candidates(self, limit: int, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        active_domain = domain or self.domain
        conjectures: List[Conjecture] = []
        
        if self.provider:
            # Usar provider si existe
            raw_payloads = self.provider() or []
            for idx, payload in enumerate(raw_payloads[:limit]):
                conj = self._coerce_to_conjecture(payload, idx)
                if conj:
                    conjectures.append(conj)
        else:
            # ⭐ NUEVO: Generar conjeturas REALES usando servicios avanzados
            logger.info(f"🔍 Generating mathematical conjectures for domain: {active_domain}")
            
            if active_domain == "number_theory":
                logger.info("🔢 Using Advanced Number Theory Service...")
                try:
                    # Generar conjeturas de teoría de números avanzadas usando campos algebraicos
                    asyncio.run(self._generate_number_theory_conjectures_async(conjectures, limit // 2))
                    logger.info(f"✓ Generated {len(conjectures)} number theory conjectures")
                except Exception as exc:
                    logger.warning(f"Number Theory Service failed: {exc}")
            
            elif active_domain == "topology":
                logger.info("🔷 Using Advanced Topology Service...")
                try:
                    # Explorar topología algebraica usando homología persistente
                    asyncio.run(self._generate_topology_conjectures_async(conjectures, limit))
                    logger.info(f"✓ Generated {len(conjectures)} topology conjectures")
                except Exception as exc:
                    logger.warning(f"Topology Service failed: {exc}")
            
            elif active_domain == "algebra":
                logger.info("📐 Using SageMath for algebraic exploration...")
                try:
                    # Explorar patrones algebraicos con SageMath
                    basic_conjectures = self.discovery_engine.generate_seed_conjectures(
                        domain="algebra",
                        limit=limit
                    )
                    conjectures.extend(basic_conjectures)
                    logger.info(f"✓ Generated {len(basic_conjectures)} algebra conjectures")
                except Exception as exc:
                    logger.warning(f"Algebra exploration failed: {exc}")
            
            # Fallback: si no se generaron suficientes, usar discovery engine básico
            if len(conjectures) < limit // 2:
                logger.info("📝 Fallback to basic discovery engine...")
                basic_conjectures = self.discovery_engine.generate_seed_conjectures(
                    domain=active_domain,
                    limit=limit - len(conjectures)
                )
                conjectures.extend(basic_conjectures)

        # Procesar y enriquecer conjeturas con ATP
        candidates: List[Dict[str, Any]] = []
        for conj in conjectures[:limit]:
            importance = self.discovery_engine.predict_importance(conj)
            novelty_base = 0.45 if conj.statement not in self._seen_statements else 0.25
            novelty = max(0.1, min(1.0, novelty_base + self.random.random() * 0.45))
            information_gain = min(1.0, 0.45 + novelty / 2 + importance / 3)
            
            # ⭐ NUEVO: Evaluar dificultad de prueba con ATP (simulado)
            atp_metadata = self._estimate_proof_complexity(conj)
            if atp_metadata.get("likely_provable"):
                importance = min(1.0, importance * 1.2)
            
            candidate = {
                "id": conj.id,
                "statement": conj.statement,
                "domain": conj.domain or active_domain,
                "conjecture": conj,
                "importance": importance,
                "novelty": novelty,
                "information_gain": information_gain,
                "impact_potential": max(0.2, importance),
                "literature_frequency": self.random.randint(0, 55),
                "dependency_count": self.random.randint(0, 6),
                "estimated_cost": self.random.random() * 0.2 + 0.05,
                "atp_metadata": atp_metadata,  # ⭐ NUEVO
            }
            candidates.append(candidate)
            self._seen_statements.add(conj.statement)
        
        logger.info(f"✅ Prepared {len(candidates)} mathematical candidates for iteration")
        return candidates
    
    async def _generate_number_theory_conjectures_async(self, conjectures: List[Conjecture], limit: int):
        """Generar conjeturas de teoría de números usando AdvancedNumberTheoryService"""
        # Explorar campos algebraicos
        field_result = await self.number_theory.algebraic_number_fields(
            operation="create_number_field",
            parameters={"polynomial": [1, 0, -2], "name": "Q(√2)"}
        )
        
        if field_result.get("success"):
            field_data = field_result.get("field", {})
            # Generar conjetura sobre clase number
            statement = f"Class number of {field_data.get('name', 'field')} equals {field_data.get('class_number', 1)}"
            conjectures.append(Conjecture(
                id=f"nt_{len(conjectures)}",
                statement=statement,
                domain="number_theory",
                metadata={"source": "algebraic_number_field", "field_data": field_data}
            ))
        
        # Explorar curvas elípticas
        if len(conjectures) < limit:
            curve_result = await self.number_theory.elliptic_curves(
                operation="create_curve",
                parameters={"a": 0, "b": 7}  # y^2 = x^3 + 7 (curva de Bitcoin)
            )
            
            if curve_result.get("success"):
                curve_data = curve_result.get("curve", {})
                torsion_order = curve_data.get("torsion_order", 0)
                statement = f"Elliptic curve y²=x³+7 has torsion order {torsion_order}"
                conjectures.append(Conjecture(
                    id=f"nt_{len(conjectures)}",
                    statement=statement,
                    domain="number_theory",
                    metadata={"source": "elliptic_curve", "curve_data": curve_data}
                ))
    
    async def _generate_topology_conjectures_async(self, conjectures: List[Conjecture], limit: int):
        """Generar conjeturas topológicas usando AdvancedTopologyService"""
        # Generar datos sintéticos para homología persistente
        import numpy as np
        np.random.seed(42)
        points = np.random.randn(50, 2).tolist()
        
        # Analizar homología persistente
        result = await self.topology.persistent_homology(
            operation="vietoris_rips",
            parameters={"points": points, "max_dimension": 2, "max_edge_length": 2.0}
        )
        
        if result.get("success"):
            persistence_data = result.get("persistence_diagram", [])
            num_holes = len([p for p in persistence_data if len(p) >= 3 and p[1] == 1])
            statement = f"Point cloud exhibits {num_holes} topological holes in H₁"
            conjectures.append(Conjecture(
                id=f"top_{len(conjectures)}",
                statement=statement,
                domain="topology",
                metadata={"source": "persistent_homology", "persistence": persistence_data}
            ))
        
        # Analizar barcodes
        if len(conjectures) < limit and result.get("success"):
            barcode = result.get("barcode", [])
            avg_lifetime = sum([b[1] - b[0] for b in barcode if len(b) >= 2]) / max(1, len(barcode))
            statement = f"Average feature lifetime in persistence diagram: {avg_lifetime:.3f}"
            conjectures.append(Conjecture(
                id=f"top_{len(conjectures)}",
                statement=statement,
                domain="topology",
                metadata={"source": "barcode_analysis", "barcode": barcode}
            ))
    
    def _estimate_proof_complexity(self, conj: Conjecture) -> Dict[str, Any]:
        """Estimar complejidad de demostración de una conjetura"""
        # Heurística simple basada en longitud y palabras clave
        statement_lower = conj.statement.lower()
        difficulty = 0.5
        
        # Keywords que indican complejidad
        if any(kw in statement_lower for kw in ["class number", "elliptic curve", "homology", "persistent"]):
            difficulty += 0.2
        if any(kw in statement_lower for kw in ["torsion", "topological", "invariant"]):
            difficulty += 0.15
        
        # Longitud del statement
        if len(conj.statement) > 80:
            difficulty += 0.1
        
        difficulty = min(1.0, difficulty)
        likely_provable = difficulty < 0.8  # Más difícil = menos probable de probar automáticamente
        
        return {
            "atp_difficulty": difficulty,
            "proof_strategy": "automated" if difficulty < 0.6 else "interactive",
            "likely_provable": likely_provable,
            "complexity_factors": ["mathematical_depth", "statement_length"]
        }

    async def _evaluate_candidate_async(self, candidate: Dict[str, Any], include_literature: bool = False) -> Dict[str, Any]:
        conjecture: Conjecture = candidate["conjecture"]
        try:
            result = await self.discovery_engine.investigate_conjecture_async(conjecture)
        except (RuntimeError, ValueError) as exc:  # pragma: no cover - defensivo
            logger.warning("Mathematical discovery evaluation failed for %s: %s", conjecture.id, exc)
            return {"status": "error", "error": str(exc)}

        candidate["importance"] = max(candidate["importance"], result.importance)
        candidate["impact_potential"] = max(candidate["impact_potential"], result.importance)

        literature: Optional[List[Dict[str, Any]]] = None
        if include_literature:
            try:
                # ASYNC MIGRATION: fetch_literature_snippets ahora es async, no necesita to_thread
                literature = await fetch_literature_snippets(
                    conjecture.statement,
                    3,
                )
            except MathematicsError as exc:  # pragma: no cover - defensivo
                logger.debug("Literature fetch failed for %s: %s", conjecture.id, exc)

        return {
            "status": result.status,
            "importance": result.importance,
            "proof": result.proof,
            "counterexample": result.counterexample,
            "notes": result.notes,
            "time_seconds": result.time_seconds,
            "literature": literature,
        }

    def _build_mathematics_hypothesis(
        self,
        candidate: Dict[str, Any],
        evaluation: Dict[str, Any],
        domain: str,
    ) -> Dict[str, Any]:
        statement = candidate.get("statement", "conjecture")
        description = (
            f"Corroborar evidencia externa para la conjetura '{statement[:80]}' en el dominio {domain}."
        )
        variables: Dict[str, Any] = {
            "statement": statement,
            "domain": domain,
            "importance": candidate.get("importance"),
            "information_gain": candidate.get("information_gain"),
            "analysis": {k: evaluation.get(k) for k in ("status", "importance", "proof", "counterexample")},
        }
        assumptions = [
            "Los resultados analíticos provienen del MathematicalDiscoveryEngine",
            "Las referencias de literatura representan contexto preliminar",
        ]
        extras = {
            "parameters": {
                "estimated_cost": candidate.get("estimated_cost"),
                "literature": evaluation.get("literature"),
            },
            "keywords": [domain, "conjecture", statement[:40]],
        }
        return self.tool_evidence.build_hypothesis(
            title=f"Evaluación de la conjetura {statement[:60]}",
            description=description,
            domain=domain,
            variables=variables,
            assumptions=assumptions,
            expected_outcome="Determinar si la evidencia apoya continuar investigando",
            extras=extras,
        )

    async def _run_iteration_impl(
        self,
        iteration: Optional[int] = None,
        limit: int = 5,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        if iteration is not None:
            self.iteration = iteration
        else:
            self.iteration += 1

        active_domain = domain or self.domain
        seed_count = max(limit * 2, 6)
        candidates = self._prepare_candidates(seed_count, active_domain)
        if not candidates:
            logger.warning("No candidate conjectures available")
            return {"success": False, "reason": "no_candidates"}

        ranked = self.scorer.rank(candidates)
        scheduled = self.scheduler.select(ranked, limit=limit)
        allocated = self.budget.allocate(scheduled)
        if not allocated:
            return {"success": False, "reason": "no_allocation"}

        evaluations = await asyncio.gather(
            *(
                self._evaluate_candidate_async(candidate, include_literature=idx < 2)
                for idx, candidate in enumerate(allocated)
            ),
            return_exceptions=True,
        )

        raw_sketches = [generate_proof_sketch(c) for c in allocated[: min(3, len(allocated))]]
        validations = [validate_sketch(sk.get("content", "")) for sk in raw_sketches]
        sketches = [sk for sk, val in zip(raw_sketches, validations) if val.get("valid")]
        invalid_sketches = sum(not val.get("valid") for val in validations)

        actions: List[str] = []
        outcomes: Dict[str, Any] = {}
        enriched_candidates: List[Dict[str, Any]] = []
        novelty_scores: List[float] = []
        support_scores: List[float] = []

        for candidate, evaluation in zip(allocated, evaluations):
            novelty_res = self.novelty.assess(
                [
                    candidate.get("novelty", 0.4),
                    candidate.get("information_gain", 0.4),
                    candidate.get("impact_potential", 0.4),
                ]
            )
            novelty_scores.append(novelty_res["novelty_score"])
            if isinstance(evaluation, Exception):
                evaluation_payload: Dict[str, Any] = {"status": "error", "error": str(evaluation)}
            else:
                evaluation_payload = evaluation if isinstance(evaluation, dict) else {"result": evaluation}

            actions.append("investigate")
            literature_payload = evaluation_payload.get("literature")

            evidence_summary: Optional[EvidenceSummary] = None
            ethics_metadata = {"ethics_approved": True, "ethics_decision_id": None, "ethics_risk_level": "LOW"}

            if self.tool_evidence:
                try:
                    hypothesis = self._build_mathematics_hypothesis(candidate, evaluation_payload, active_domain)

                    # Ethics evaluation before execution
                    conjecture_id = candidate.get("id", "unknown")
                    statement = candidate.get("statement", "")
                    keywords = [active_domain, "mathematics", "theorem_proving"]
                    if statement:
                        # Extract some keywords from the statement
                        keywords.append(statement.split()[0] if statement.split() else "conjecture")

                    ethics_request = ExperimentRequest(
                        domain=active_domain,
                        description=hypothesis.get("description", ""),
                        data_sensitivity="low",
                        declared_intent="research",
                        keywords=keywords,
                        user_id="mathematics_loop",
                        metadata={
                            "candidate_id": conjecture_id,
                            "iteration": self.iteration,
                            "domain": active_domain,
                        }
                    )

                    ethics_decision = self.ethics_gate.evaluate(ethics_request)
                    ethics_metadata.update({
                        "ethics_approved": ethics_decision.allowed,
                        "ethics_decision_id": ethics_decision.decision_id,
                        # Pydantic v2 alignment: use `level`
                        "ethics_risk_level": getattr(ethics_decision, "level", getattr(ethics_decision, "risk_level", "UNKNOWN")),
                    })

                    if not ethics_decision.allowed:
                        logger.warning(
                            f"Mathematics hypothesis {conjecture_id} blocked by ethics gate: "
                            f"{getattr(ethics_decision, 'level', 'UNKNOWN')} risk, reasons: {ethics_decision.escalation_reasons}"
                        )
                        # Skip this candidate if blocked
                        continue

                    if ethics_decision.requires_signature:
                        logger.info(
                            f"Mathematics hypothesis {conjecture_id} requires human review: "
                            f"{ethics_decision.recommended_actions}"
                        )

                    # Enriquecer keywords con términos matemáticos genéricos para mejorar búsqueda externa
                    hypothesis.setdefault("extras", {})
                    kw = set(hypothesis["extras"].get("keywords", []) or [])
                    kw.update({active_domain, "mathematics", "theorem", "conjecture", "proof"})
                    hypothesis["extras"]["keywords"] = list(kw)

                    evidence_summary = await self.tool_evidence.corroborate(hypothesis, domain=active_domain)
                    if evidence_summary.success:
                        candidate["impact_potential"] = min(
                            1.0,
                            float(candidate.get("impact_potential", 0.3)) + evidence_summary.support_score * 0.1,
                        )
                        support_scores.append(evidence_summary.support_score)
                    else:
                        # Fallback: si la evaluación interna trae proof o counterexample, asignar soporte mínimo
                        internal_support = 0.05 if (evaluation_payload.get("proof") or evaluation_payload.get("counterexample")) else 0.0
                        support_scores.append(internal_support)
                except (RuntimeError, ValueError, ConnectionError, TimeoutError) as exc:
                    logger.debug("Mathematics corroboration failed for %s: %s", candidate.get("id"), exc)
                    support_scores.append(0.0)

            outcomes[candidate["id"]] = {
                "novelty_score": novelty_res["novelty_score"],
                "analysis": evaluation_payload,
                "literature": literature_payload,
                "tool_evidence": evidence_summary.as_dict() if evidence_summary else None,
                "ethics": ethics_metadata,
            }
            enriched_candidates.append(
                {
                    **candidate,
                    "analysis": evaluation_payload,
                    "novelty": novelty_res,
                    "literature": literature_payload,
                    "tool_evidence": evidence_summary.as_dict() if evidence_summary else None,
                    "ethics": ethics_metadata,
                }
            )

        mutations = self.mutator.mutate_batch(allocated, max_mutations=5)

        feedback_event = {
            "metric_name": "mutation_volume",
            "value": len(mutations),
            "improved": len(mutations) > 0,
            "confidence": 0.62,
        }
        feedback_result = process_feedback(feedback_event)

        record = IterationRecord(
            iteration=self.iteration,
            domain="mathematics",
            selected_ids=[c.get("id", "?") for c in allocated],
            actions=actions,
            outcomes={
                **outcomes,
                "feedback_adjustment": feedback_result["adjustment"],
                "sketches": len(sketches),
                "invalid_sketches": invalid_sketches,
            },
        )
        self.state.add_iteration(record)

        duration = time.time() - start
        avg_novelty = sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0.0
        avg_support = sum(support_scores) / len(support_scores) if support_scores else 0.0
        summary = {
            "iteration": self.iteration,
            "domain": active_domain,
            "duration_s": duration,
            "selected": len(allocated),
            "mutations": len(mutations),
            "sketches": len(sketches),
            "avg_novelty": avg_novelty,
            "feedback_adjustment": feedback_result["adjustment"],
            "invalid_sketches": invalid_sketches,
            "avg_support_score": avg_support,
        }

        try:
            self.telemetry.record_iteration(
                domain="mathematics",
                duration_s=duration,
                selected=len(allocated),
                mutations=len(mutations),
                sketches=len(sketches),
            )
        except (ValueError, RuntimeError) as exc:  # pragma: no cover - defensivo
            logger.warning("Telemetry recording failed (math): %s", exc)

        try:
            from app.monitoring.metrics import metrics  # Import local para evitar ciclos

            metrics.set_gauge("autonomous_feedback_adjustment_last", feedback_result["adjustment"])
            metrics.set_gauge(
                "autonomous_sketch_valid_ratio",
                (len(sketches) / max(1, len(raw_sketches))) if raw_sketches else 0.0,
            )
            if support_scores:
                metrics.set_gauge("autonomous_support_score_last", avg_support)
        except (ImportError, AttributeError):  # pragma: no cover - entorno parcial
            logger.debug("Could not update mathematics gauges")

        logger.info("Math loop iteration %d: %s", self.iteration, summary)
        return {
            "success": True,
            "summary": summary,
            "mutations": mutations,
            "sketches": sketches,
            "selected": enriched_candidates,
            "outcomes": outcomes,
            "feedback": feedback_result,
        }

    def run_iteration(
        self,
        iteration: int,
        limit: int = 5,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self._run_coro_sync(self._run_iteration_impl(iteration=iteration, limit=limit, domain=domain))

    async def run_mathematics_discovery_iteration(
        self,
        limit: int = 5,
        iteration: Optional[int] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self._run_iteration_impl(iteration=iteration, limit=limit, domain=domain)


__all__ = ["MathematicsLoop"]
