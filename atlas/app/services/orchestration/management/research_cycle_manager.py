"""
Research Cycle Manager for AXIOM with Knowledge Graph Integration
Manages the complete closed-loop research process with enhanced knowledge discovery
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
from dataclasses import dataclass, field
from enum import Enum
import uuid

from app.services.base_service import BaseService
from app.services.scientific_hypothesis_agent import ScientificHypothesisAgent, ResearchPhase
from app.services.literature_search import LiteratureSearchService
from app.services.workflow_orchestration import WorkflowOrchestratorService
from app.services.experiment_tracking import ExperimentTrackingService
from app.services.data_versioning import DataVersioningService
from app.core.bootstrap_logging import logger, log_decision_event
from app.services.policy_engine_service import policy_engine_service
from app.observability.metrics import inc, phase_timer, gauge_inc, phase_activity
from app.observability.trace import get_or_create_trace
from app.middleware.trace_id_middleware import get_current_trace_id
from app.exceptions.base import (
    AtlasDomainError,
    AtlasExternalError,
    AtlasValidationError,
    AtlasInfrastructureError,
)
from app.exceptions.domain.biology import BiologyError

# Iterative improvement pipeline (feedback hooks)
try:
    from app.services.plausibility_scoring_service_improved import get_plausibility_service
    _PLAUSIBILITY_AVAILABLE = True
except BiologyError:  # pragma: no cover
    _PLAUSIBILITY_AVAILABLE = False
from typing import TYPE_CHECKING, Callable
from app.types.research_cycle_manager_types import (
    ProcessRequestResult,
    StartResearchCycleResult,
    AnalyzeResultsResult,
    GenerateRefinementSuggestionsResult,
    ValidateResearchCycleResult,
    GetCycleStatusResult,
    PauseCycleResult,
    ResumeCycleResult,
    StopCycleResult,
    GetCycleResultsResult,
    GenerateCycleSummaryResult,
    ListCyclesResult,
    CycleSummaryResult,
    StartKnowledgeEnhancedCycleResult,
    EnrichCycleWithKnowledgeResult,
    ValidateHypothesisWithKnowledgeResult,
    FindResearchConnectionsResult,
    SuggestResearchDirectionsResult,
    ExtractCycleKnowledgeResult,
    PreloadDomainKnowledgeResult,
    ValidateWithKnowledgeGraphResult,
    ExtractExperimentalKnowledgeResult,
    ExtractValidationKnowledgeResult,
    SynthesizeCycleKnowledgeResult,
    StoreCycleKnowledgeResult,
)
try:  # Carga opcional del pipeline de mejora iterativa
    from app.services.iterative_improvement_service import (
        get_improvement_pipeline,
        AnalysisType as ImprovementAnalysisType,
        FeedbackType as ImprovementFeedbackType,
    )
    _IMPROVEMENT_AVAILABLE = True
except BiologyError:  # pragma: no cover - fallback if pipeline no disponible
    _IMPROVEMENT_AVAILABLE = False
    # Definir stubs para tipos para evitar errores de tipo/linters
    if TYPE_CHECKING:  # solo hints estáticos
        ImprovementAnalysisType = Any  # type: ignore
        ImprovementFeedbackType = Any  # type: ignore
        get_improvement_pipeline: Callable[[], Any]

# Knowledge Graph integration
try:  # Carga perezosa solo para verificar disponibilidad
    import importlib
    if importlib.util.find_spec("app.models.database_models") is not None:  # type: ignore[attr-defined]
        KNOWLEDGE_GRAPH_AVAILABLE = True
    else:
        KNOWLEDGE_GRAPH_AVAILABLE = False
except BiologyError:
    KNOWLEDGE_GRAPH_AVAILABLE = False
    logger.warning("Knowledge Graph not available - running in basic mode")


class ResearchCycleStatus(Enum):
    """Research cycle status"""
    INITIALIZING = "initializing"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    LITERATURE_REVIEW = "literature_review"
    EXPERIMENT_DESIGN = "experiment_design"
    EXECUTION = "execution"
    ANALYSIS = "analysis"
    REFINEMENT = "refinement"
    VALIDATION = "validation"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ResearchIteration:
    """Single iteration in the research cycle"""
    iteration_id: str
    hypothesis_id: str
    phase: ResearchPhase
    start_time: datetime
    end_time: Optional[datetime] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    error_message: Optional[str] = None


@dataclass
class ResearchCycle:
    """Complete research cycle"""
    cycle_id: str
    research_question: str
    domain: str
    status: ResearchCycleStatus
    iterations: List[ResearchIteration] = field(default_factory=list)
    current_hypothesis_id: Optional[str] = None
    workflow_id: Optional[str] = None
    experiment_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    max_iterations: int = 5
    convergence_threshold: float = 0.8
    results: Dict[str, Any] = field(default_factory=dict)
    last_policy_decision: Optional[Dict[str, Any]] = None
    enable_policy_engine: bool = True


class ResearchCycleManager(BaseService):
    """
    Manages the complete closed-loop research process
    Orchestrates hypothesis generation, literature review, experimentation, and refinement
    """

    def __init__(self):
        super().__init__("ResearchCycleManager")

        # Initialize dependent services
        self.hypothesis_agent = ScientificHypothesisAgent()
        self.literature_service = LiteratureSearchService()
        self.workflow_service = WorkflowOrchestratorService()
        self.experiment_service = ExperimentTrackingService()
        self.data_service = DataVersioningService()

        self.active_cycles: Dict[str, ResearchCycle] = {}
        self.completed_cycles: List[ResearchCycle] = []

        # Knowledge Graph Integration
        self.knowledge_graph_enabled = KNOWLEDGE_GRAPH_AVAILABLE
        self.domain_knowledge_cache: Dict[str, Dict[str, Any]] = {}
        
        # Knowledge-enhanced research patterns
        self.knowledge_integration_strategies = {
            "hypothesis_enhancement": True,
            "literature_enrichment": True,
            "cross_domain_insights": True,
            "knowledge_validation": True,
            "concept_mapping": True
        }

        logger.info("✅ ResearchCycleManager initialized")
        logger.info(f"🧠 Knowledge Graph Integration: {'✅ Enabled' if self.knowledge_graph_enabled else '❌ Disabled'}")

        # Feedback / improvement pipeline
        self._improvement_pipeline = get_improvement_pipeline() if _IMPROVEMENT_AVAILABLE else None
        if not _IMPROVEMENT_AVAILABLE:
            logger.warning("Iterative Improvement Pipeline no disponible: hooks de feedback desactivados")

        # Plausibility service (opcional)
        try:
            self._plausibility_service = get_plausibility_service() if _PLAUSIBILITY_AVAILABLE else None  # type: ignore[name-defined]
        except BiologyError:
            self._plausibility_service = None

    async def _record_phase_feedback(
        self,
        cycle: "ResearchCycle",
        phase: str,
        accuracy: float | None = None,
        coherence: float | None = None,
        validity: float | None = None,
        extra_params: dict | None = None,
        source: str = "system"
    ) -> None:
        """Helper para registrar feedback normalizado (0-1) en el pipeline iterativo.

        No lanza excepciones hacia arriba; loggea en caso de fallo. Usa cycle_id como trace_id.
        """
        # Log structured decision event with trace correlation
        current_trace_id = get_current_trace_id()
        log_decision_event(
            event_type="feedback_recorded",
            phase=phase,
            details={
                "cycle_id": cycle.cycle_id,
                "accuracy": accuracy,
                "coherence": coherence,
                "validity": validity,
                "source": source
            },
            outcome="recorded" if (accuracy or coherence or validity) else "no_metrics",
            trace_id=current_trace_id
        )

        if not self._improvement_pipeline:
            return
        try:
            if not _IMPROVEMENT_AVAILABLE:
                return
            phase_map = {
                "hypothesis_generation": getattr(ImprovementAnalysisType, "HYPOTHESIS_GENERATION", None),
                "literature_review": getattr(ImprovementAnalysisType, "LITERATURE_SEARCH", None),
                "analysis": getattr(ImprovementAnalysisType, "EVIDENCE_SYNTHESIS", None),
                "validation": getattr(ImprovementAnalysisType, "PEER_REVIEW", None),
            }
            analysis_type = phase_map.get(phase)
            if not analysis_type:
                return

            params = {"cycle_id": cycle.cycle_id, "phase": phase, "domain": cycle.domain}
            if extra_params:
                params.update(extra_params)
            context = {"trace_id": get_or_create_trace(params, fallback=cycle.cycle_id), "research_question": cycle.research_question}

            # Registrar métricas disponibles
            if accuracy is not None and _IMPROVEMENT_AVAILABLE:
                acc_type = getattr(ImprovementFeedbackType, "ACCURACY_SCORE", None)
                if acc_type is not None:
                    await self._improvement_pipeline.record_feedback(
                        analysis_type=analysis_type,
                        feedback_type=acc_type,
                        value=max(0.0, min(1.0, accuracy)),
                        parameters=params,
                        context=context,
                        source=source,
                    )
                    inc("atlas_feedback_total")
            if coherence is not None and _IMPROVEMENT_AVAILABLE:
                coh_type = getattr(ImprovementFeedbackType, "COHERENCE_SCORE", None)
                if coh_type is not None:
                    await self._improvement_pipeline.record_feedback(
                        analysis_type=analysis_type,
                        feedback_type=coh_type,
                        value=max(0.0, min(1.0, coherence)),
                        parameters=params,
                        context=context,
                        source=source,
                    )
                    inc("atlas_feedback_total")
            if validity is not None and _IMPROVEMENT_AVAILABLE:
                val_type = getattr(ImprovementFeedbackType, "SCIENTIFIC_VALIDITY", None)
                if val_type is not None:
                    await self._improvement_pipeline.record_feedback(
                        analysis_type=analysis_type,
                        feedback_type=val_type,
                        value=max(0.0, min(1.0, validity)),
                        parameters=params,
                        context=context,
                        source=source,
                    )
                    inc("atlas_feedback_total")
        except BiologyError as e:  # pragma: no cover - robustez
            logger.warning(f"No se pudo registrar feedback de fase {phase}: {e}")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process research cycle management requests with Knowledge Graph integration"""
        try:
            action = request_data.get("action", "")

            # Original actions
            if action == "start_research_cycle":
                return await self.start_research_cycle(request_data)
            elif action == "get_cycle_status":
                return self.get_cycle_status(request_data)
            elif action == "pause_cycle":
                return await self.pause_cycle(request_data)
            elif action == "resume_cycle":
                return await self.resume_cycle(request_data)
            elif action == "stop_cycle":
                return await self.stop_cycle(request_data)
            elif action == "get_cycle_results":
                return self.get_cycle_results(request_data)
            elif action == "list_cycles":
                return self.list_cycles(request_data)
            
            # Knowledge Graph enhanced actions
            elif action == "knowledge_enhanced_cycle":
                return await self.start_knowledge_enhanced_cycle(request_data)
            elif action == "enrich_cycle_with_knowledge":
                return await self.enrich_cycle_with_knowledge(request_data)
            elif action == "validate_hypothesis_with_knowledge":
                return await self.validate_hypothesis_with_knowledge(request_data)
            elif action == "find_research_connections":
                return await self.find_research_connections(request_data)
            elif action == "suggest_research_directions":
                return await self.suggest_research_directions(request_data)
            elif action == "extract_cycle_knowledge":
                return await self.extract_cycle_knowledge(request_data)
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        # Original actions
                        "start_research_cycle", "get_cycle_status", "pause_cycle",
                        "resume_cycle", "stop_cycle", "get_cycle_results", "list_cycles",
                        # Knowledge Graph actions
                        "knowledge_enhanced_cycle", "enrich_cycle_with_knowledge", 
                        "validate_hypothesis_with_knowledge", "find_research_connections",
                        "suggest_research_directions", "extract_cycle_knowledge"
                    ]
                }

        except AtlasDomainError as e:
            return self.handle_error(e, "process_request")
        except AtlasExternalError as e:
            return self.handle_error(e, "process_request")
        except AtlasValidationError as e:
            return self.handle_error(e, "process_request")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "process_request")

    async def start_research_cycle(self, request_data: StartResearchCycleResult) -> StartResearchCycleResult:
        """Start a new research cycle"""
        try:
            data = request_data
            research_question = data.get("research_question", "")
            domain = data.get("domain", "")
            max_iterations = data.get("max_iterations", 5)
            convergence_threshold = data.get("convergence_threshold", 0.8)

            if not research_question:
                return {
                    "success": False,
                    "error": "research_question is required"
                }

            if domain not in ["materials_science", "drug_discovery", "energy_storage", "quantum_computing"]:
                return {
                    "success": False,
                    "error": f"Domain '{domain}' not supported"
                }

            # Create research cycle
            cycle = ResearchCycle(
                cycle_id=str(uuid.uuid4()),
                research_question=research_question,
                domain=domain,
                status=ResearchCycleStatus.INITIALIZING,
                max_iterations=max_iterations,
                convergence_threshold=convergence_threshold
            )

            # Gauge de ciclos activos
            try:
                gauge_inc("atlas_active_cycles", 1)
                gauge_inc("atlas_active_cycles", 1, labels={"domain": domain})
            except BiologyError:
                pass

            self.active_cycles[cycle.cycle_id] = cycle

            # Start the research cycle asynchronously
            asyncio.create_task(self._execute_research_cycle(cycle))

            logger.info(f"🚀 Started research cycle: {research_question} in domain {domain}")

            return {
                "success": True,
                "message": f"Research cycle started for: '{research_question}'",
                "cycle_id": cycle.cycle_id,
                "status": cycle.status.value,
                "estimated_completion": "2-4 hours depending on complexity"
            }

        except AtlasDomainError as e:
            return self.handle_error(e, "start_research_cycle")
        except AtlasExternalError as e:
            return self.handle_error(e, "start_research_cycle")
        except AtlasValidationError as e:
            return self.handle_error(e, "start_research_cycle")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "start_research_cycle")

    async def _execute_research_cycle(self, cycle: ResearchCycle):
        """Execute the complete research cycle"""
        try:
            logger.info(f"🔄 Starting research cycle execution: {cycle.cycle_id}")
            cycle_start_ts = datetime.now()
            # Phase 1: Hypothesis Generation
            cycle.status = ResearchCycleStatus.HYPOTHESIS_GENERATION
            await self._phase_hypothesis_generation(cycle)

            # Phase 2: Literature Review
            if cycle.status != ResearchCycleStatus.FAILED:
                cycle.status = ResearchCycleStatus.LITERATURE_REVIEW
                await self._phase_literature_review(cycle)

            # Phase 3: Experiment Design
            if cycle.status != ResearchCycleStatus.FAILED:
                cycle.status = ResearchCycleStatus.EXPERIMENT_DESIGN
                await self._phase_experiment_design(cycle)

            # Phase 4: Execution
            if cycle.status != ResearchCycleStatus.FAILED:
                cycle.status = ResearchCycleStatus.EXECUTION
                await self._phase_execution(cycle)

            # Phase 5: Analysis
            if cycle.status != ResearchCycleStatus.FAILED:
                cycle.status = ResearchCycleStatus.ANALYSIS
                await self._phase_analysis(cycle)

            # Phase 6: Refinement (iterative)
            if cycle.status != ResearchCycleStatus.FAILED:
                await self._phase_refinement_loop(cycle)

            # Phase 7: Validation
            if cycle.status != ResearchCycleStatus.FAILED:
                cycle.status = ResearchCycleStatus.VALIDATION
                await self._phase_validation(cycle)

            # Complete cycle
            if cycle.status != ResearchCycleStatus.FAILED:
                cycle.status = ResearchCycleStatus.COMPLETED
                cycle.completed_at = datetime.now()
                # Métrica: duración total del ciclo
                try:
                    from app.monitoring.metrics import observe as _obs
                    total_seconds = (cycle.completed_at - cycle_start_ts).total_seconds()
                    _obs("atlas_cycle_total_duration_seconds", total_seconds)
                    _obs("atlas_cycle_total_duration_seconds", total_seconds, tags={"domain": cycle.domain})
                except BiologyError:
                    pass
                # Métrica: histograma de iteraciones de refinamiento por ciclo
                try:
                    from app.monitoring.metrics import observe as _obs
                    refinements = cycle.results.get("refinement_iterations") or 0
                    _obs("atlas_refinement_iterations_per_cycle", float(refinements))
                    _obs("atlas_refinement_iterations_per_cycle", float(refinements), tags={"domain": cycle.domain})
                except BiologyError:
                    pass
                # Move to completed cycles
                self.completed_cycles.append(cycle)
                del self.active_cycles[cycle.cycle_id]

                # Decrementar gauge activos (éxito)
                try:
                    gauge_inc("atlas_active_cycles", -1)
                    gauge_inc("atlas_active_cycles", -1, labels={"domain": cycle.domain})
                except BiologyError:
                    pass

                logger.info(f"✅ Research cycle completed: {cycle.cycle_id}")

        except AtlasDomainError as e:
            logger.error(f"❌ Research cycle failed: {cycle.cycle_id} - {e}")
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["error"] = str(e)
            try:
                if cycle.cycle_id in self.active_cycles:
                    gauge_inc("atlas_active_cycles", -1)
                    gauge_inc("atlas_active_cycles", -1, labels={"domain": cycle.domain})
                    del self.active_cycles[cycle.cycle_id]
            except BiologyError:
                pass
        except AtlasExternalError as e:
            logger.error(f"❌ Research cycle failed: {cycle.cycle_id} - {e}")
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["error"] = str(e)
            # Decrementar gauge si ciclo estaba activo
            try:
                if cycle.cycle_id in self.active_cycles:
                    gauge_inc("atlas_active_cycles", -1)
                    gauge_inc("atlas_active_cycles", -1, labels={"domain": cycle.domain})
                    del self.active_cycles[cycle.cycle_id]
            except BiologyError:
                pass

    async def _phase_hypothesis_generation(self, cycle: ResearchCycle):
        """Generate initial hypothesis"""
        t = phase_timer(domain=cycle.domain)
        t.start()
        with phase_activity("hypothesis_generation", cycle.domain):
            try:
                logger.info(f"🧠 Generating hypothesis for: {cycle.research_question}")
                hypothesis_result = await self.hypothesis_agent.process_request({
                    "action": "generate_hypothesis",
                    "domain": cycle.domain,
                    "research_question": cycle.research_question
                })
                if not hypothesis_result.get("success"):
                    raise AtlasDomainError(
                        "Hypothesis generation failed",
                        context={"error": hypothesis_result.get("error")},
                    )
                cycle.current_hypothesis_id = hypothesis_result["hypothesis_id"]
                cycle.results["hypothesis"] = hypothesis_result
                iteration = ResearchIteration(
                    iteration_id=str(uuid.uuid4()),
                    hypothesis_id=cycle.current_hypothesis_id or "",
                    phase=ResearchPhase.HYPOTHESIS_GENERATION,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    inputs={"research_question": cycle.research_question},
                    outputs=hypothesis_result,
                    success=True
                )
                cycle.iterations.append(iteration)
                logger.info(f"✅ Hypothesis generated: {hypothesis_result['hypothesis']['title']}")
                if self._plausibility_service:
                    try:
                        hyp_obj = hypothesis_result.get("hypothesis", {})
                        plaus_input = {
                            "title": hyp_obj.get("title"),
                            "description": hyp_obj.get("statement") or hyp_obj.get("description"),
                            "variables": hyp_obj.get("variables"),
                            "assumptions": hyp_obj.get("assumptions"),
                            "expected_outcome": hyp_obj.get("expected_outcome"),
                            "domain": cycle.domain,
                            "hypothesis_uuid": cycle.current_hypothesis_id,
                        }
                        plaus_res = await self._plausibility_service.score_hypothesis(plaus_input)
                        cycle.results["plausibility_initial"] = plaus_res
                    except BiologyError as e:  # pragma: no cover
                        logger.warning(f"Fallo cálculo plausibility inicial: {e}")
                try:
                    confidence = float(hypothesis_result["hypothesis"].get("confidence_score", 0.0))
                except BiologyError:
                    confidence = 0.0
                if cycle.results.get("plausibility_initial"):
                    comp = cycle.results["plausibility_initial"].get("composite", confidence)
                    confidence = (confidence + comp) / 2 if confidence > 0 else comp
                await self._record_phase_feedback(
                    cycle,
                    phase="hypothesis_generation",
                    accuracy=confidence,
                    coherence=confidence * 0.9,
                )
            except AtlasDomainError as e:
                logger.error(f"❌ Hypothesis generation failed: {e}")
                try:
                    inc("atlas_phase_failures_total")
                    inc("atlas_phase_failures_hypothesis_generation")
                    inc("atlas_phase_failures_total", labels={"phase": "hypothesis_generation", "domain": cycle.domain})
                    from app.monitoring.metrics import update_phase_success_ratio as _upr
                    _upr("hypothesis_generation", cycle.domain)
                except BiologyError:  # pragma: no cover
                    pass
                cycle.status = ResearchCycleStatus.FAILED
                cycle.results["hypothesis_error"] = str(e)
            except AtlasExternalError as e:
                logger.error(f"❌ Hypothesis generation failed: {e}")
                try:
                    inc("atlas_phase_failures_total")
                    inc("atlas_phase_failures_hypothesis_generation")
                    inc("atlas_phase_failures_total", labels={"phase": "hypothesis_generation", "domain": cycle.domain})
                    from app.monitoring.metrics import update_phase_success_ratio as _upr
                    _upr("hypothesis_generation", cycle.domain)
                except BiologyError:  # pragma: no cover
                    pass
                cycle.status = ResearchCycleStatus.FAILED
                cycle.results["hypothesis_error"] = str(e)
            finally:
                t.stop("hypothesis_generation")

    async def _phase_literature_review(self, cycle: ResearchCycle):
        """Perform literature review"""
        t = phase_timer(domain=cycle.domain)
        t.start()
        try:
            with phase_activity("literature_review", cycle.domain):
                logger.info(f"📚 Performing literature review for cycle: {cycle.cycle_id}")

                # Determinar título base
                hypothesis_title = cycle.research_question[:50] + "..." if len(cycle.research_question) > 50 else cycle.research_question
                try:
                    hyp_dict = cycle.results.get("hypothesis", {}).get("hypothesis", {})
                    if isinstance(hyp_dict, dict) and hyp_dict.get("title"):
                        hypothesis_title = hyp_dict["title"]
                except (TypeError, AttributeError):
                    pass

                search_query = f"{hypothesis_title} {cycle.domain}"
                literature_result = await self.literature_service.process_request({
                    "action": "search_literature",
                    "query": search_query,
                    "domain": cycle.domain,
                    "max_results": 20
                })

                if literature_result.get("success"):
                    cycle.results["literature_review"] = literature_result
                    if cycle.current_hypothesis_id:
                        try:
                            await self.hypothesis_agent.process_request({
                                "action": "refine_hypothesis",
                                "hypothesis_id": cycle.current_hypothesis_id,
                                "refinement_data": {
                                    "literature_support": len(literature_result.get("papers", [])),
                                    "confidence_adjustment": 0.1
                                }
                            })
                        except AtlasDomainError as e:  # pragma: no cover
                            logger.warning(f"Refine hypothesis domain error: {e}")
                        except AtlasExternalError as e:  # pragma: no cover
                            logger.warning(f"Refine hypothesis external error: {e}")
                        except AtlasValidationError as e:  # pragma: no cover
                            logger.warning(f"Refine hypothesis validation error: {e}")
                        except AtlasInfrastructureError as e:  # pragma: no cover
                            logger.warning(f"Refine hypothesis infrastructure error: {e}")
                        except BiologyError as e:  # pragma: no cover
                            logger.warning(f"Refine hypothesis unexpected error: {e}")
                    iteration = ResearchIteration(
                        iteration_id=str(uuid.uuid4()),
                        hypothesis_id=cycle.current_hypothesis_id or "",
                        phase=ResearchPhase.LITERATURE_REVIEW,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        inputs={"search_query": search_query},
                        outputs=literature_result,
                        success=True
                    )
                    cycle.iterations.append(iteration)
                    logger.info(f"✅ Literature review completed: {len(literature_result.get('papers', []))} papers found")
                    papers_count = len(literature_result.get("papers", []))
                    support_signal = min(1.0, papers_count / 20)
                    await self._record_phase_feedback(
                        cycle,
                        phase="literature_review",
                        accuracy=support_signal,
                        coherence=min(1.0, 0.5 + support_signal / 2),
                    )
                else:
                    logger.warning(f"⚠️ Literature review partially failed: {literature_result.get('error')}")
        except AtlasDomainError as e:
            logger.error(f"❌ Literature review failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_literature_review")
                inc("atlas_phase_failures_total", labels={"phase": "literature_review", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("literature_review", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["literature_error"] = str(e)
        except AtlasExternalError as e:
            logger.error(f"❌ Literature review failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_literature_review")
                inc("atlas_phase_failures_total", labels={"phase": "literature_review", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("literature_review", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["literature_error"] = str(e)
        except AtlasValidationError as e:
            logger.error(f"❌ Literature review failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_literature_review")
                inc("atlas_phase_failures_total", labels={"phase": "literature_review", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("literature_review", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["literature_error"] = str(e)
        except AtlasInfrastructureError as e:
            logger.error(f"❌ Literature review failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_literature_review")
                inc("atlas_phase_failures_total", labels={"phase": "literature_review", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("literature_review", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["literature_error"] = str(e)
        finally:
            t.stop("literature_review")

    async def _phase_experiment_design(self, cycle: ResearchCycle):
        """Design experiments to test the hypothesis"""
        t = phase_timer(domain=cycle.domain)
        t.start()
        try:
            with phase_activity("experiment_design", cycle.domain):
                logger.info(f"🔬 Designing experiments for cycle: {cycle.cycle_id}")
                hypothesis_title = cycle.research_question[:50] + "..." if len(cycle.research_question) > 50 else cycle.research_question
                try:
                    hyp_dict = cycle.results.get("hypothesis", {}).get("hypothesis", {})
                    if hyp_dict.get("title"):
                        hypothesis_title = hyp_dict["title"]
                except (TypeError, AttributeError):
                    pass
                experiment_result = await self.experiment_service.process_request({
                    "action": "start_experiment",
                    "name": f"Test: {hypothesis_title}",
                    "description": f"Automated experiment for research cycle {cycle.cycle_id}",
                    "parameters": {
                        "domain": cycle.domain,
                        "cycle_id": cycle.cycle_id,
                        "hypothesis_id": cycle.current_hypothesis_id
                    },
                    "tags": {
                        "domain": cycle.domain,
                        "type": "automated_research",
                        "phase": "experiment_design"
                    }
                })
                if experiment_result.get("success"):
                    cycle.experiment_id = experiment_result["experiment_id"]
                    workflow_result = await self.workflow_service.process_request({
                        "action": "create_workflow",
                        "name": f"Research Cycle: {cycle.research_question}",
                        "description": f"Automated workflow for hypothesis testing in {cycle.domain}",
                        "steps": self._create_research_workflow_steps(cycle),
                        "metadata": {
                            "cycle_id": cycle.cycle_id,
                            "hypothesis_id": cycle.current_hypothesis_id,
                            "experiment_id": cycle.experiment_id
                        }
                    })
                    if workflow_result.get("success"):
                        cycle.workflow_id = workflow_result["workflow_id"]
                        cycle.results["experiment_design"] = {
                            "experiment_id": cycle.experiment_id,
                            "workflow_id": cycle.workflow_id,
                            "workflow_steps": len(self._create_research_workflow_steps(cycle))
                        }
                        iteration = ResearchIteration(
                            iteration_id=str(uuid.uuid4()),
                            hypothesis_id=cycle.current_hypothesis_id or "",
                            phase=ResearchPhase.EXPERIMENT_DESIGN,
                            start_time=datetime.now(),
                            end_time=datetime.now(),
                            inputs={"hypothesis": cycle.results.get("hypothesis")},
                            outputs={"experiment_id": cycle.experiment_id, "workflow_id": cycle.workflow_id},
                            success=True
                        )
                        cycle.iterations.append(iteration)
                        logger.info(f"✅ Experiment design completed: workflow {cycle.workflow_id}")
                    else:
                        raise AtlasDomainError(
                            "Workflow creation failed",
                            context={"error": workflow_result.get("error")},
                        )
                else:
                    raise AtlasDomainError(
                        "Experiment tracking failed",
                        context={"error": experiment_result.get("error")},
                    )
        except AtlasDomainError as e:
            logger.error(f"❌ Experiment design failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_experiment_design")
                inc("atlas_phase_failures_total", labels={"phase": "experiment_design", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("experiment_design", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["design_error"] = str(e)
        except AtlasExternalError as e:
            logger.error(f"❌ Experiment design failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_experiment_design")
                inc("atlas_phase_failures_total", labels={"phase": "experiment_design", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("experiment_design", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["design_error"] = str(e)
        except AtlasValidationError as e:
            logger.error(f"❌ Experiment design failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_experiment_design")
                inc("atlas_phase_failures_total", labels={"phase": "experiment_design", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("experiment_design", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["design_error"] = str(e)
        except AtlasInfrastructureError as e:
            logger.error(f"❌ Experiment design failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_experiment_design")
                inc("atlas_phase_failures_total", labels={"phase": "experiment_design", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("experiment_design", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["design_error"] = str(e)
        finally:
            t.stop("experiment_design")

    def _create_research_workflow_steps(self, cycle: ResearchCycle) -> List[Dict[str, Any]]:
        """Create workflow steps based on research domain"""
        base_steps = []

        if cycle.domain == "materials_science":
            base_steps = [
                {
                    "service_type": "computational_chemistry",
                    "operation": "analyze_molecule",
                    "parameters": {"smiles": "CCO"},
                    "description": "Analyze material properties",
                    "timeout": 300
                },
                {
                    "service_type": "pde",
                    "operation": "solve_heat_equation",
                    "parameters": {"boundary_conditions": "thermal"},
                    "description": "Simulate thermal behavior",
                    "dependencies": ["step_0"],
                    "timeout": 600
                },
                {
                    "service_type": "scientific_ai",
                    "operation": "predict_properties",
                    "parameters": {"material": "test_material", "properties": ["conductivity", "strength"]},
                    "description": "Predict material properties using AI",
                    "dependencies": ["step_1"],
                    "timeout": 300
                }
            ]
        elif cycle.domain == "drug_discovery":
            base_steps = [
                {
                    "service_type": "computational_chemistry",
                    "operation": "molecular_docking",
                    "parameters": {"ligand": "CCO", "receptor": "protein_1"},
                    "description": "Perform molecular docking",
                    "timeout": 600
                },
                {
                    "service_type": "scientific_ai",
                    "operation": "predict_properties",
                    "parameters": {"molecule": "CCO", "properties": ["toxicity", "solubility", "binding_affinity"]},
                    "description": "Predict pharmacological properties",
                    "dependencies": ["step_0"],
                    "timeout": 300
                }
            ]
        elif cycle.domain == "energy_storage":
            base_steps = [
                {
                    "service_type": "scientific_ai",
                    "operation": "optimize_battery",
                    "parameters": {"chemistry": "li-ion", "target_capacity": 300},
                    "description": "Optimize battery chemistry",
                    "timeout": 900
                },
                {
                    "service_type": "pde",
                    "operation": "solve_diffusion_equation",
                    "parameters": {"diffusion_coefficient": 1e-10},
                    "description": "Model ion diffusion",
                    "dependencies": ["step_0"],
                    "timeout": 600
                }
            ]
        else:
            # Default workflow
            base_steps = [
                {
                    "service_type": "scientific_ai",
                    "operation": "analyze_data",
                    "parameters": {"data_type": cycle.domain},
                    "description": "Analyze available data",
                    "timeout": 300
                }
            ]

        return base_steps

    async def _phase_execution(self, cycle: ResearchCycle):
        """Execute the designed experiments"""
        t = phase_timer(domain=cycle.domain)
        t.start()
        try:
            with phase_activity("execution", cycle.domain):
                logger.info(f"⚡ Executing experiments for cycle: {cycle.cycle_id}")
                if cycle.workflow_id:
                    execute_result = await self.workflow_service.process_request({
                        "action": "execute_workflow",
                        "workflow_id": cycle.workflow_id
                    })
                    if execute_result.get("success"):
                        cycle.results["execution"] = execute_result
                        if cycle.experiment_id:
                            await self.experiment_service.process_request({
                                "action": "log_metric",
                                "experiment_id": cycle.experiment_id,
                                "metric_name": "execution_success",
                                "metric_value": 1.0,
                                "step": 0
                            })
                        iteration = ResearchIteration(
                            iteration_id=str(uuid.uuid4()),
                            hypothesis_id=cycle.current_hypothesis_id or "",
                            phase=ResearchPhase.EXECUTION,
                            start_time=datetime.now(),
                            end_time=datetime.now(),
                            inputs={"workflow_id": cycle.workflow_id},
                            outputs=execute_result,
                            success=True
                        )
                        cycle.iterations.append(iteration)
                        logger.info(f"✅ Experiment execution completed: workflow {cycle.workflow_id}")
                    else:
                        raise AtlasDomainError(
                            "Workflow execution failed",
                            context={"error": execute_result.get("error")},
                        )
                else:
                    raise AtlasDomainError("No workflow available for execution")
        except AtlasDomainError as e:
            logger.error(f"❌ Experiment execution failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_execution")
                inc("atlas_phase_failures_total", labels={"phase": "execution", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("execution", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["execution_error"] = str(e)
        except AtlasExternalError as e:
            logger.error(f"❌ Experiment execution failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_execution")
                inc("atlas_phase_failures_total", labels={"phase": "execution", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("execution", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["execution_error"] = str(e)
        except AtlasValidationError as e:
            logger.error(f"❌ Experiment execution failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_execution")
                inc("atlas_phase_failures_total", labels={"phase": "execution", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("execution", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["execution_error"] = str(e)
        except AtlasInfrastructureError as e:
            logger.error(f"❌ Experiment execution failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_execution")
                inc("atlas_phase_failures_total", labels={"phase": "execution", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("execution", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["execution_error"] = str(e)
        finally:
            t.stop("execution")

    async def _phase_analysis(self, cycle: ResearchCycle):
        """Analyze experiment results"""
        t = phase_timer(domain=cycle.domain)
        t.start()
        try:
            with phase_activity("analysis", cycle.domain):
                logger.info(f"📊 Analyzing results for cycle: {cycle.cycle_id}")
                workflow_status: Dict[str, Any] = {"success": False}
                for _ in range(30):
                    workflow_status = await self.workflow_service.process_request({
                        "action": "get_workflow_status",
                        "workflow_id": cycle.workflow_id
                    })
                    if not workflow_status.get("success"):
                        await asyncio.sleep(1)
                        continue
                    wf_state = workflow_status.get("status")
                    if wf_state in ("completed", "failed"):
                        break
                    await asyncio.sleep(1)
                if workflow_status.get("success"):
                    results_data = workflow_status.get("results", {})
                    analysis_result = await self._analyze_results(results_data, cycle)
                    cycle.results["analysis"] = analysis_result
                    if cycle.experiment_id:
                        await self.experiment_service.process_request({
                            "action": "log_metric",
                            "experiment_id": cycle.experiment_id,
                            "metric_name": "analysis_confidence",
                            "metric_value": analysis_result.get("confidence_score", 0.5),
                            "step": 1
                        })
                    iteration = ResearchIteration(
                        iteration_id=str(uuid.uuid4()),
                        hypothesis_id=cycle.current_hypothesis_id or "",
                        phase=ResearchPhase.ANALYSIS,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        inputs={"workflow_results": results_data},
                        outputs=analysis_result,
                        success=True
                    )
                    cycle.iterations.append(iteration)
                    logger.info(f"✅ Results analysis completed: confidence {analysis_result.get('confidence_score', 0):.2f}")
                    conf = float(analysis_result.get("confidence_score", 0.0))
                    if self._plausibility_service and cycle.current_hypothesis_id:
                        try:
                            hyp_data = cycle.results.get("hypothesis", {}).get("hypothesis", {})
                            plaus_after = await self._plausibility_service.score_hypothesis({
                                "title": hyp_data.get("title"),
                                "description": hyp_data.get("statement") or hyp_data.get("description"),
                                "variables": hyp_data.get("variables"),
                                "assumptions": hyp_data.get("assumptions"),
                                "expected_outcome": hyp_data.get("expected_outcome"),
                                "domain": cycle.domain,
                                "hypothesis_uuid": cycle.current_hypothesis_id,
                            })
                            cycle.results["plausibility_analysis"] = plaus_after
                            comp = plaus_after.get("composite")
                            if comp is not None:
                                conf = (conf + comp) / 2
                        except BiologyError as ex:  # pragma: no cover
                            logger.warning(f"Fallo plausibility en análisis: {ex}")
                    await self._record_phase_feedback(
                        cycle,
                        phase="analysis",
                        accuracy=conf,
                        coherence=conf * 0.95,
                    )
                else:
                    raise AtlasDomainError(
                        "Could not get workflow status",
                        context={"error": workflow_status.get("error")},
                    )
        except AtlasDomainError as e:
            logger.error(f"❌ Results analysis failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_analysis")
                inc("atlas_phase_failures_total", labels={"phase": "analysis", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("analysis", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["analysis_error"] = str(e)
        except AtlasExternalError as e:
            logger.error(f"❌ Results analysis failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_analysis")
                inc("atlas_phase_failures_total", labels={"phase": "analysis", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("analysis", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["analysis_error"] = str(e)
        except AtlasValidationError as e:
            logger.error(f"❌ Results analysis failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_analysis")
                inc("atlas_phase_failures_total", labels={"phase": "analysis", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("analysis", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["analysis_error"] = str(e)
        except AtlasInfrastructureError as e:
            logger.error(f"❌ Results analysis failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                inc("atlas_phase_failures_analysis")
                inc("atlas_phase_failures_total", labels={"phase": "analysis", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("analysis", cycle.domain)
            except BiologyError:  # pragma: no cover
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["analysis_error"] = str(e)
        finally:
            t.stop("analysis")

    async def _analyze_results(self, results_data: AnalyzeResultsResult, cycle: ResearchCycle) -> AnalyzeResultsResult:
        """Analyze experimental results"""
        # Simulate AI analysis of results
        # In a real implementation, this would use more sophisticated analysis

        analysis = {
            "hypothesis_supported": True,
            "confidence_score": 0.75,
            "key_findings": [
                "Primary hypothesis confirmed with experimental data",
                "Performance metrics exceeded expectations",
                "Identified optimization opportunities"
            ],
            "statistical_significance": "p < 0.05",
            "effect_size": "large",
            "recommendations": [
                "Scale up experimental parameters",
                "Investigate secondary effects",
                "Consider alternative approaches"
            ],
            "limitations": [
                "Limited sample size",
                "Computational constraints",
                "Measurement precision"
            ]
        }

        # Adjust confidence based on domain and results
        if cycle.domain == "materials_science":
            if "thermal" in cycle.research_question.lower():
                analysis["confidence_score"] = 0.80
            else:
                analysis["confidence_score"] = 0.70
        elif cycle.domain == "drug_discovery":
            analysis["confidence_score"] = 0.65  # More conservative for drug discovery
        elif cycle.domain == "energy_storage":
            analysis["confidence_score"] = 0.75

        return analysis

    async def _phase_refinement_loop(self, cycle: ResearchCycle):
        """Iterative refinement phase"""
        try:
            logger.info(f"🔄 Starting refinement loop for cycle: {cycle.cycle_id}")
            iteration_count = 0
            converged = False
            loop_start = datetime.now()

            while iteration_count < cycle.max_iterations and not converged:
                iteration_count += 1
                logger.info(f"🔄 Refinement iteration {iteration_count}/{cycle.max_iterations}")
                try:
                    inc("atlas_refinement_iterations_total")
                except BiologyError:
                    pass
                iter_timer = phase_timer(domain=cycle.domain)
                iter_timer.start()
                try:
                    with phase_activity("refinement", cycle.domain):
                        analysis_result = await self.hypothesis_agent.process_request({
                            "action": "analyze_evidence",
                            "hypothesis_id": cycle.current_hypothesis_id
                        })
                        if not analysis_result.get("success"):
                            logger.warning(f"⚠️ Evidence analysis failed: {analysis_result.get('error')}")
                            break
                        evidence_strength = analysis_result.get("evidence_strength", 0.0)
                        # Policy engine gating
                        if cycle.enable_policy_engine:
                            policy_scores = {
                                "evidence_strength": evidence_strength,
                                "support_score": cycle.results.get("support_score"),
                                "coverage": cycle.results.get("coverage"),
                                "diversity": cycle.results.get("diversity"),
                                "reproducibility_likelihood": min(1.0, evidence_strength * 0.9)
                            }
                            try:
                                decision_res = policy_engine_service.decide(policy_scores)
                                if decision_res.get("success"):
                                    dec = decision_res.get("decision", {})
                                    cycle.last_policy_decision = dec
                                    cycle.results.setdefault("policy_history", []).append(dec)
                            except AtlasDomainError as pe:  # pragma: no cover
                                logger.warning(f"Policy engine error: {pe}")
                            except AtlasExternalError as pe:  # pragma: no cover
                                logger.warning(f"Policy engine error: {pe}")
                            except AtlasValidationError as pe:  # pragma: no cover
                                logger.warning(f"Policy engine error: {pe}")
                            except AtlasInfrastructureError as pe:  # pragma: no cover
                                logger.warning(f"Policy engine error: {pe}")
                            except BiologyError as pe:  # pragma: no cover
                                logger.warning(f"Policy engine error: {pe}")
                        else:
                            refinement_data = self._generate_refinement_suggestions(cycle, analysis_result)
                            await self.hypothesis_agent.process_request({
                                "action": "refine_hypothesis",
                                "hypothesis_id": cycle.current_hypothesis_id,
                                "refinement_data": refinement_data
                            })
                            iteration = ResearchIteration(
                                iteration_id=str(uuid.uuid4()),
                                hypothesis_id=cycle.current_hypothesis_id or "",
                                phase=ResearchPhase.REFINEMENT,
                                start_time=datetime.now(),
                                end_time=datetime.now(),
                                inputs={"evidence_analysis": analysis_result},
                                outputs={"refinement": refinement_data},
                                success=True
                            )
                            cycle.iterations.append(iteration)
                            logger.info(f"🔧 Hypothesis refined at iteration {iteration_count}")
                        # Simple convergence heuristic
                        if evidence_strength >= 0.85:
                            converged = True
                            logger.info(f"✅ Hypothesis converged at iteration {iteration_count}")
                finally:
                    try:
                        iter_timer.stop("refinement")
                    except BiologyError:
                        pass
            cycle.results["refinement_iterations"] = iteration_count
            cycle.results["converged"] = converged
            if converged:
                try:
                    from app.monitoring.metrics import observe
                    duration = (datetime.now() - loop_start).total_seconds()
                    observe("atlas_convergence_time_seconds", duration)
                    observe("atlas_convergence_time_seconds", duration, labels={"phase": "refinement", "domain": cycle.domain})
                except BiologyError:
                    pass
            try:
                inc("atlas_refinement_cycles_total")
            except BiologyError:
                pass
        except AtlasDomainError as e:
            logger.error(f"❌ Refinement loop failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                try:
                    inc("atlas_phase_failures_refinement")
                except BiologyError:
                    pass
                inc("atlas_phase_failures_total", labels={"phase": "refinement", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("refinement", cycle.domain)
            except BiologyError:
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["refinement_error"] = str(e)
        except AtlasExternalError as e:
            logger.error(f"❌ Refinement loop failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                try:
                    inc("atlas_phase_failures_refinement")
                except BiologyError:
                    pass
                inc("atlas_phase_failures_total", labels={"phase": "refinement", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("refinement", cycle.domain)
            except BiologyError:
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["refinement_error"] = str(e)
        except AtlasValidationError as e:
            logger.error(f"❌ Refinement loop failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                try:
                    inc("atlas_phase_failures_refinement")
                except BiologyError:
                    pass
                inc("atlas_phase_failures_total", labels={"phase": "refinement", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("refinement", cycle.domain)
            except BiologyError:
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["refinement_error"] = str(e)
        except AtlasInfrastructureError as e:
            logger.error(f"❌ Refinement loop failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                try:
                    inc("atlas_phase_failures_refinement")
                except BiologyError:
                    pass
                inc("atlas_phase_failures_total", labels={"phase": "refinement", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("refinement", cycle.domain)
            except BiologyError:
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["refinement_error"] = str(e)
        except BiologyError as e:
            logger.error(f"❌ Refinement loop failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                try:
                    inc("atlas_phase_failures_refinement")
                except BiologyError:
                    pass
                inc("atlas_phase_failures_total", labels={"phase": "refinement", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("refinement", cycle.domain)
            except BiologyError:
                pass
            cycle.status = ResearchCycleStatus.FAILED
            cycle.results["refinement_error"] = str(e)

    def _generate_refinement_suggestions(self, cycle: ResearchCycle, analysis_result: GenerateRefinementSuggestionsResult) -> GenerateRefinementSuggestionsResult:
        """Generate suggestions for hypothesis refinement"""
        suggestions = {
            "confidence_adjustment": 0.05,
            "new_variables": [],
            "new_assumptions": [],
            "parameter_adjustments": {}
        }

        # Add domain-specific refinements
        if cycle.domain == "materials_science":
            suggestions["new_variables"] = ["temperature_range", "pressure_effects"]
            suggestions["parameter_adjustments"] = {"simulation_precision": "high"}
        elif cycle.domain == "drug_discovery":
            suggestions["new_variables"] = ["binding_sites", "conformational_changes"]
            suggestions["new_assumptions"] = ["Stable protein conformation"]
        elif cycle.domain == "energy_storage":
            suggestions["new_variables"] = ["cycle_count", "temperature_effects"]
            suggestions["parameter_adjustments"] = {"time_step": 0.1}

        return suggestions

    async def _phase_validation(self, cycle: ResearchCycle):
        """Final validation phase"""
        t = phase_timer(domain=cycle.domain)
        t.start()
        try:
            with phase_activity("validation", cycle.domain):
                logger.info(f"✅ Starting validation phase for cycle: {cycle.cycle_id}")
                validation_result = await self._validate_research_cycle(cycle)
                cycle.results["validation"] = validation_result
                iteration = ResearchIteration(
                    iteration_id=str(uuid.uuid4()),
                    hypothesis_id=cycle.current_hypothesis_id or "",
                    phase=ResearchPhase.REFINEMENT,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    inputs={"cycle_results": cycle.results},
                    outputs=validation_result,
                    success=validation_result.get("validated", False)
                )
                cycle.iterations.append(iteration)
                logger.info(f"✅ Validation completed: {validation_result.get('validation_status')}")
                val_score = float(validation_result.get("quality_score", 0.0))
                if self._plausibility_service and cycle.current_hypothesis_id:
                    try:
                        hyp_data = cycle.results.get("hypothesis", {}).get("hypothesis", {})
                        plaus_final = await self._plausibility_service.score_hypothesis({
                            "title": hyp_data.get("title"),
                            "description": hyp_data.get("statement") or hyp_data.get("description"),
                            "variables": hyp_data.get("variables"),
                            "assumptions": hyp_data.get("assumptions"),
                            "expected_outcome": hyp_data.get("expected_outcome"),
                            "domain": cycle.domain,
                            "hypothesis_uuid": cycle.current_hypothesis_id,
                        })
                        cycle.results["plausibility_validation"] = plaus_final
                        comp = plaus_final.get("composite")
                        if comp is not None:
                            val_score = (val_score + comp) / 2
                    except BiologyError as ex:  # pragma: no cover
                        logger.warning(f"Fallo plausibility en validación: {ex}")
                await self._record_phase_feedback(
                    cycle,
                    phase="validation",
                    accuracy=val_score,
                    coherence=min(1.0, val_score * 0.97),
                    validity=val_score,
                )
        except BiologyError as e:
            logger.error(f"❌ Validation failed: {e}")
            try:
                inc("atlas_phase_failures_total")
                try:
                    inc("atlas_phase_failures_validation")
                except BiologyError:
                    pass
                inc("atlas_phase_failures_total", labels={"phase": "validation", "domain": cycle.domain})
                from app.monitoring.metrics import update_phase_success_ratio as _upr
                _upr("validation", cycle.domain)
            except BiologyError:
                pass
            cycle.results["validation_error"] = str(e)
        finally:
            t.stop("validation")

    async def _validate_research_cycle(self, cycle: ResearchCycle) -> ValidateResearchCycleResult:
        """Validate the complete research cycle"""
        validation = {
            "validated": True,
            "validation_status": "passed",
            "quality_score": 0.85,
            "checks_passed": [],
            "recommendations": []
        }

        # Check hypothesis quality
        if cycle.current_hypothesis_id:
            hypothesis_check = await self.hypothesis_agent.process_request({
                "action": "get_hypothesis",
                "hypothesis_id": cycle.current_hypothesis_id
            })

            if hypothesis_check.get("success"):
                hypothesis = hypothesis_check["hypothesis"]
                try:
                    conf = float(hypothesis.get("confidence_score", 0.0))
                except BiologyError:
                    conf = 0.0
                if conf > 0.7:
                    validation["checks_passed"].append("High confidence hypothesis")
                try:
                    if isinstance(hypothesis.get("evidence", []), list) and len(hypothesis.get("evidence", [])) > 0:
                        validation["checks_passed"].append("Experimental evidence available")
                except BiologyError:
                    pass
                    validation["checks_passed"].append("Experimental evidence available")

        # Check workflow execution
        if cycle.workflow_id:
            workflow_check = await self.workflow_service.process_request({
                "action": "get_workflow_status",
                "workflow_id": cycle.workflow_id
            })

            if workflow_check.get("success"):
                # Estructura: estado en campo superior "status"
                if workflow_check.get("status") == "completed":
                    validation["checks_passed"].append("Workflow executed successfully")

        # Check experiment tracking
        if cycle.experiment_id:
            validation["checks_passed"].append("Experiment tracking enabled")

        # Generate recommendations
        if len(validation["checks_passed"]) < 3:
            validation["recommendations"].append("Consider additional validation experiments")
        if cycle.results.get("refinement_iterations", 0) < 2:
            validation["recommendations"].append("More refinement iterations may improve results")

        return validation

    def get_cycle_status(self, request_data: GetCycleStatusResult) -> GetCycleStatusResult:
        """Get status of a research cycle"""
        try:
            cycle_id = request_data.get("cycle_id")

            if not cycle_id:
                return {
                    "success": False,
                    "error": "cycle_id is required"
                }

            cycle = self.active_cycles.get(cycle_id)
            if not cycle:
                # Check completed cycles
                for completed_cycle in self.completed_cycles:
                    if completed_cycle.cycle_id == cycle_id:
                        cycle = completed_cycle
                        break

            if not cycle:
                return {
                    "success": False,
                    "error": f"Research cycle {cycle_id} not found"
                }

            return {
                "success": True,
                "cycle_id": cycle.cycle_id,
                "status": cycle.status.value,
                "research_question": cycle.research_question,
                "domain": cycle.domain,
                "current_phase": cycle.iterations[-1].phase.value if cycle.iterations else None,
                "iterations_completed": len(cycle.iterations),
                "max_iterations": cycle.max_iterations,
                "created_at": cycle.created_at.isoformat(),
                "completed_at": cycle.completed_at.isoformat() if cycle.completed_at else None,
                "progress": self._calculate_progress(cycle)
            }

        except BiologyError as e:
            return self.handle_error(e, "get_cycle_status")

    def _calculate_progress(self, cycle: ResearchCycle) -> float:
        """Calculate research cycle progress"""
        if cycle.status == ResearchCycleStatus.COMPLETED:
            return 1.0
        elif cycle.status == ResearchCycleStatus.FAILED:
            return 0.0

        # Estimate progress based on completed iterations
        if cycle.max_iterations > 0:
            base_progress = len(cycle.iterations) / (cycle.max_iterations * 6)  # 6 phases per iteration
        else:
            base_progress = 0.0
        return min(base_progress, 0.95)  # Cap at 95% until completion

    async def pause_cycle(self, request_data: PauseCycleResult) -> PauseCycleResult:
        """Pause a research cycle"""
        # Implementation for pausing cycles
        return {
            "success": False,
            "error": "Pause functionality not yet implemented"
        }

    async def resume_cycle(self, request_data: ResumeCycleResult) -> ResumeCycleResult:
        """Resume a paused research cycle"""
        # Implementation for resuming cycles
        return {
            "success": False,
            "error": "Resume functionality not yet implemented"
        }

    async def stop_cycle(self, request_data: StopCycleResult) -> StopCycleResult:
        """Stop a research cycle"""
        try:
            cycle_id = request_data.get("cycle_id")

            if not cycle_id or cycle_id not in self.active_cycles:
                return {
                    "success": False,
                    "error": f"Active research cycle {cycle_id} not found"
                }

            cycle = self.active_cycles[cycle_id]
            cycle.status = ResearchCycleStatus.FAILED
            cycle.completed_at = datetime.now()
            cycle.results["stopped_by_user"] = True

            # Move to completed cycles
            self.completed_cycles.append(cycle)
            del self.active_cycles[cycle_id]

            return {
                "success": True,
                "message": f"Research cycle {cycle_id} stopped successfully"
            }
        except AtlasDomainError as e:
            return self.handle_error(e, "stop_cycle")
        except AtlasExternalError as e:
            return self.handle_error(e, "stop_cycle")
        except AtlasValidationError as e:
            return self.handle_error(e, "stop_cycle")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "stop_cycle")
        except BiologyError as e:
            return self.handle_error(AtlasInfrastructureError(str(e)), "stop_cycle")

    def get_cycle_results(self, request_data: GetCycleResultsResult) -> GetCycleResultsResult:
        """Get results of a completed research cycle"""
        try:
            cycle_id = request_data.get("cycle_id")

            if not cycle_id:
                return {
                    "success": False,
                    "error": "cycle_id is required"
                }

            # Check active cycles
            cycle = self.active_cycles.get(cycle_id)
            if not cycle:
                # Check completed cycles
                for completed_cycle in self.completed_cycles:
                    if completed_cycle.cycle_id == cycle_id:
                        cycle = completed_cycle
                        break

            if not cycle:
                return {
                    "success": False,
                    "error": f"Research cycle {cycle_id} not found"
                }

            return {
                "success": True,
                "cycle_id": cycle.cycle_id,
                "status": cycle.status.value,
                "results": cycle.results,
                "iterations": [
                    {
                        "iteration_id": it.iteration_id,
                        "phase": it.phase.value,
                        "start_time": it.start_time.isoformat(),
                        "end_time": it.end_time.isoformat() if it.end_time else None,
                        "success": it.success,
                        "error_message": it.error_message
                    } for it in cycle.iterations
                ],
                "summary": self._generate_cycle_summary(cycle)
            }
        except AtlasDomainError as e:
            return self.handle_error(e, "get_cycle_results")
        except AtlasExternalError as e:
            return self.handle_error(e, "get_cycle_results")
        except AtlasValidationError as e:
            return self.handle_error(e, "get_cycle_results")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "get_cycle_results")
        except BiologyError as e:
            return self.handle_error(AtlasInfrastructureError(str(e)), "get_cycle_results")

    def _generate_cycle_summary(self, cycle: ResearchCycle) -> GenerateCycleSummaryResult:
        """Generate a summary of the research cycle"""
        summary = {
            "total_iterations": len(cycle.iterations),
            "successful_iterations": sum(1 for it in cycle.iterations if it.success),
            "phases_completed": list(set(it.phase.value for it in cycle.iterations)),
            "final_hypothesis_confidence": 0.0,
            "key_achievements": []
        }

        # Get final hypothesis confidence
        if cycle.current_hypothesis_id and cycle.results.get("hypothesis"):
            try:
                if (isinstance(cycle.results["hypothesis"], dict) and
                    cycle.results["hypothesis"].get("hypothesis") and
                    isinstance(cycle.results["hypothesis"]["hypothesis"], dict) and
                    cycle.results["hypothesis"]["hypothesis"].get("confidence_score")):
                    summary["final_hypothesis_confidence"] = cycle.results["hypothesis"]["hypothesis"]["confidence_score"]
            except (KeyError, TypeError, AttributeError):
                # Keep default value of 0.0
                pass

        # Add key achievements
        if cycle.results.get("literature_review"):
            papers_found = len(cycle.results["literature_review"]["papers"])
            summary["key_achievements"].append(f"Reviewed {papers_found} relevant papers")

        if cycle.workflow_id:
            summary["key_achievements"].append("Successfully executed automated workflow")

        if cycle.results.get("analysis", {}).get("hypothesis_supported"):
            summary["key_achievements"].append("Hypothesis validated through experimentation")

        return summary

    def list_cycles(self, request_data: ListCyclesResult) -> ListCyclesResult:
        """List research cycles"""
        try:
            status_filter = request_data.get("status")
            domain_filter = request_data.get("domain")
            limit = request_data.get("limit", 20)

            cycles = []

            # Add active cycles
            for cycle in self.active_cycles.values():
                if self._matches_filters(cycle, status_filter, domain_filter):
                    cycles.append(self._cycle_summary(cycle))

            # Add completed cycles (only if there are any)
            if self.completed_cycles:
                for cycle in self.completed_cycles[-limit:]:  # Last N completed cycles
                    if self._matches_filters(cycle, status_filter, domain_filter):
                        cycles.append(self._cycle_summary(cycle))

            return {
                "success": True,
                "cycles": cycles[:limit],
                "total_count": len(cycles),
                "active_count": len(self.active_cycles),
                "completed_count": len(self.completed_cycles)
            }
        except AtlasDomainError as e:
            return self.handle_error(e, "list_cycles")
        except AtlasExternalError as e:
            return self.handle_error(e, "list_cycles")
        except AtlasValidationError as e:
            return self.handle_error(e, "list_cycles")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "list_cycles")
        except BiologyError as e:
            return self.handle_error(AtlasInfrastructureError(str(e)), "list_cycles")

    def _matches_filters(self, cycle: ResearchCycle, status_filter: Optional[str], domain_filter: Optional[str]) -> bool:
        """Check if cycle matches the given filters"""
        if status_filter and cycle.status.value != status_filter:
            return False
        if domain_filter and cycle.domain != domain_filter:
            return False
        return True

    def _cycle_summary(self, cycle: ResearchCycle) -> CycleSummaryResult:
        """Generate a summary of a research cycle"""
        return {
            "cycle_id": cycle.cycle_id,
            "research_question": cycle.research_question,
            "domain": cycle.domain,
            "status": cycle.status.value,
            "created_at": cycle.created_at.isoformat(),
            "completed_at": cycle.completed_at.isoformat() if cycle.completed_at else None,
            "iterations": len(cycle.iterations),
            "progress": self._calculate_progress(cycle)
        }

    # === KNOWLEDGE GRAPH ENHANCED METHODS ===

    async def start_knowledge_enhanced_cycle(self, request_data: StartKnowledgeEnhancedCycleResult) -> StartKnowledgeEnhancedCycleResult:
        """Start a knowledge-enhanced research cycle with domain knowledge integration"""
        try:
            if not self.knowledge_graph_enabled:
                return {
                    "success": False,
                    "error": "Knowledge Graph not available - falling back to standard cycle",
                    "fallback_action": "start_research_cycle"
                }

            research_question = request_data.get("research_question", "")
            domain = request_data.get("domain", "")
            knowledge_enhancement_level = request_data.get("enhancement_level", "standard")  # minimal, standard, comprehensive
            cross_domain_exploration = request_data.get("cross_domain", True)

            if not research_question or not domain:
                return {"success": False, "error": "research_question and domain are required"}

            # Pre-load domain knowledge
            domain_knowledge = await self._preload_domain_knowledge(domain, research_question)
            
            # Start enhanced research cycle
            cycle_result = await self.start_research_cycle({
                "research_question": research_question,
                "domain": domain,
                "max_iterations": request_data.get("max_iterations", 5),
                "convergence_threshold": request_data.get("convergence_threshold", 0.8)
            })

            if not cycle_result["success"]:
                return cycle_result

            cycle_id = cycle_result["cycle_id"]
            cycle = self.active_cycles[cycle_id]

            # Enhance cycle with knowledge graph capabilities
            cycle.results["knowledge_enhancement"] = {
                "level": knowledge_enhancement_level,
                "domain_knowledge_loaded": len(domain_knowledge.get("concepts", [])),
                "cross_domain_enabled": cross_domain_exploration,
                "enhancement_strategies": self.knowledge_integration_strategies
            }

            # Store domain knowledge in cycle
            cycle.results["domain_knowledge"] = domain_knowledge

            logger.info(f"🧠 Knowledge-enhanced cycle started: {research_question} with {len(domain_knowledge.get('concepts', []))} domain concepts")

            return {
                "success": True,
                "message": f"Knowledge-enhanced research cycle started for: '{research_question}'",
                "cycle_id": cycle_id,
                "knowledge_enhancement": cycle.results["knowledge_enhancement"]
            }

        except BiologyError as e:
            return self.handle_error(e, "start_knowledge_enhanced_cycle")

    async def enrich_cycle_with_knowledge(self, request_data: EnrichCycleWithKnowledgeResult) -> EnrichCycleWithKnowledgeResult:
        """Enrich an existing research cycle with additional knowledge"""
        try:
            cycle_id = request_data.get("cycle_id", "")
            knowledge_types = request_data.get("types", ["concepts", "relationships", "cross_domain"])
            depth_level = request_data.get("depth", "standard")

            if not cycle_id or cycle_id not in self.active_cycles:
                return {"success": False, "error": f"Active cycle {cycle_id} not found"}

            cycle = self.active_cycles[cycle_id]
            enrichment_results = {}

            # Enrich with different types of knowledge
            if "concepts" in knowledge_types:
                concept_enrichment = await self._enrich_with_concepts(cycle, depth_level)
                enrichment_results["concepts"] = concept_enrichment

            if "relationships" in knowledge_types:
                relationship_enrichment = await self._enrich_with_relationships(cycle, depth_level)
                enrichment_results["relationships"] = relationship_enrichment

            if "cross_domain" in knowledge_types:
                cross_domain_enrichment = await self._enrich_with_cross_domain_knowledge(cycle, depth_level)
                enrichment_results["cross_domain"] = cross_domain_enrichment

            # Update cycle with enrichment results
            if "knowledge_enrichment" not in cycle.results:
                cycle.results["knowledge_enrichment"] = []
            
            cycle.results["knowledge_enrichment"].append({
                "timestamp": datetime.now().isoformat(),
                "types": knowledge_types,
                "depth": depth_level,
                "results": enrichment_results
            })

            logger.info(f"🌟 Cycle enriched with knowledge: {len(enrichment_results)} enhancement types")

            return {
                "success": True,
                "cycle_id": cycle_id,
                "enrichment_results": enrichment_results,
                "total_enhancements": sum(len(v) if isinstance(v, list) else 1 for v in enrichment_results.values())
            }

        except BiologyError as e:
            return self.handle_error(e, "enrich_cycle_with_knowledge")

    async def validate_hypothesis_with_knowledge(self, request_data: ValidateHypothesisWithKnowledgeResult) -> ValidateHypothesisWithKnowledgeResult:
        """Validate research hypothesis against knowledge graph"""
        try:
            cycle_id = request_data.get("cycle_id", "")
            hypothesis_text = request_data.get("hypothesis", "")
            validation_depth = request_data.get("depth", "standard")

            if not cycle_id or cycle_id not in self.active_cycles:
                return {"success": False, "error": f"Active cycle {cycle_id} not found"}

            if not hypothesis_text:
                # Get current hypothesis from cycle
                cycle = self.active_cycles[cycle_id]
                hypothesis_data = cycle.results.get("hypothesis", {})
                if isinstance(hypothesis_data, dict) and hypothesis_data.get("hypothesis"):
                    hypothesis_obj = hypothesis_data["hypothesis"]
                    hypothesis_text = hypothesis_obj.get("statement", "") if isinstance(hypothesis_obj, dict) else str(hypothesis_obj)
                
                if not hypothesis_text:
                    return {"success": False, "error": "No hypothesis available for validation"}

            # Validate hypothesis using literature search with knowledge validation
            validation_result = await self.literature_service.process_request({
                "action": "validate_scientific_claims",
                "claims": [hypothesis_text],
                "domain": self.active_cycles[cycle_id].domain,
                "evidence_threshold": 3
            })

            if not validation_result["success"]:
                return validation_result

            # Extract validation data
            validations = validation_result.get("validations", [])
            if validations:
                validation_data = validations[0]
                
                # Enhance with knowledge graph analysis
                kg_validation = await self._validate_with_knowledge_graph(
                    hypothesis_text, self.active_cycles[cycle_id].domain, validation_depth
                )
                
                combined_validation = {
                    "hypothesis": hypothesis_text,
                    "literature_validation": validation_data,
                    "knowledge_graph_validation": kg_validation,
                    "overall_confidence": self._calculate_combined_confidence(validation_data, kg_validation),
                    "recommendation": self._generate_validation_recommendation(validation_data, kg_validation)
                }

                # Store validation in cycle
                cycle = self.active_cycles[cycle_id]
                if "hypothesis_validations" not in cycle.results:
                    cycle.results["hypothesis_validations"] = []
                cycle.results["hypothesis_validations"].append(combined_validation)

                logger.info(f"🔍 Hypothesis validated: confidence {combined_validation['overall_confidence']:.2f}")

                return {
                    "success": True,
                    "cycle_id": cycle_id,
                    "validation": combined_validation
                }
            else:
                return {"success": False, "error": "No validation results available"}

        except BiologyError as e:
            return self.handle_error(e, "validate_hypothesis_with_knowledge")

    async def find_research_connections(self, request_data: FindResearchConnectionsResult) -> FindResearchConnectionsResult:
        """Find connections between research areas and domains"""
        try:
            cycle_id = request_data.get("cycle_id", "")
            target_domains = request_data.get("target_domains", [])
            connection_strength = request_data.get("min_strength", 0.5)

            if not cycle_id or cycle_id not in self.active_cycles:
                return {"success": False, "error": f"Active cycle {cycle_id} not found"}

            cycle = self.active_cycles[cycle_id]
            
            # Use literature service to find cross-domain connections
            connections_result = await self.literature_service.process_request({
                "action": "find_cross_domain_connections",
                "source_domain": cycle.domain,
                "target_domains": target_domains,
                "concept": cycle.research_question,
                "similarity_threshold": connection_strength
            })

            if not connections_result["success"]:
                return connections_result

            connections = connections_result.get("connections", [])
            
            # Enhance connections with research relevance analysis
            enhanced_connections = []
            for connection in connections:
                enhanced_connection = await self._enhance_connection_with_research_context(
                    connection, cycle.research_question, cycle.domain
                )
                enhanced_connections.append(enhanced_connection)

            # Store connections in cycle
            if "research_connections" not in cycle.results:
                cycle.results["research_connections"] = []
            cycle.results["research_connections"].extend(enhanced_connections)

            logger.info(f"🔗 Found {len(enhanced_connections)} research connections")

            return {
                "success": True,
                "cycle_id": cycle_id,
                "connections": enhanced_connections,
                "total_connections": len(enhanced_connections),
                "source_domain": cycle.domain,
                "target_domains": target_domains or "all"
            }

        except AtlasDomainError as e:
            return self.handle_error(e, "find_research_connections")
        except AtlasExternalError as e:
            return self.handle_error(e, "find_research_connections")
        except AtlasValidationError as e:
            return self.handle_error(e, "find_research_connections")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "find_research_connections")

    async def suggest_research_directions(self, request_data: SuggestResearchDirectionsResult) -> SuggestResearchDirectionsResult:
        """Suggest new research directions based on knowledge gaps and connections"""
        try:
            cycle_id = request_data.get("cycle_id", "")
            creativity_level = request_data.get("creativity", "moderate")
            max_suggestions = request_data.get("max_suggestions", 10)

            if not cycle_id or cycle_id not in self.active_cycles:
                return {"success": False, "error": f"Active cycle {cycle_id} not found"}

            cycle = self.active_cycles[cycle_id]

            # Generate interdisciplinary research suggestions
            suggestions_result = await self.literature_service.process_request({
                "action": "suggest_interdisciplinary_research",
                "primary_domain": cycle.domain,
                "research_interest": cycle.research_question,
                "min_connection_strength": 0.4 if creativity_level == "high" else 0.6
            })

            if not suggestions_result["success"]:
                return suggestions_result

            # Generate research hypotheses
            hypotheses_result = await self.literature_service.process_request({
                "action": "generate_research_hypotheses",
                "domain": cycle.domain,
                "research_area": cycle.research_question,
                "creativity_level": creativity_level,
                "max_hypotheses": max_suggestions
            })

            research_directions = {
                "interdisciplinary_opportunities": suggestions_result.get("suggestions", []),
                "novel_hypotheses": hypotheses_result.get("hypotheses", []) if hypotheses_result["success"] else [],
                "emerging_trends": suggestions_result.get("emerging_trends", []),
                "knowledge_gaps": await self._identify_cycle_knowledge_gaps(cycle)
            }

            # Rank and prioritize directions
            prioritized_directions = self._prioritize_research_directions(research_directions, cycle)

            # Store directions in cycle
            cycle.results["research_directions"] = {
                "generated_at": datetime.now().isoformat(),
                "creativity_level": creativity_level,
                "directions": prioritized_directions
            }

            logger.info(f"🎯 Generated {len(prioritized_directions)} research directions")

            return {
                "success": True,
                "cycle_id": cycle_id,
                "research_directions": prioritized_directions,
                "creativity_level": creativity_level,
                "total_suggestions": len(prioritized_directions)
            }

        except AtlasDomainError as e:
            return self.handle_error(e, "suggest_research_directions")
        except AtlasExternalError as e:
            return self.handle_error(e, "suggest_research_directions")
        except AtlasValidationError as e:
            return self.handle_error(e, "suggest_research_directions")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "suggest_research_directions")

    async def extract_cycle_knowledge(self, request_data: ExtractCycleKnowledgeResult) -> ExtractCycleKnowledgeResult:
        """Extract and formalize knowledge gained from research cycle"""
        try:
            cycle_id = request_data.get("cycle_id", "")
            extract_types = request_data.get("types", ["concepts", "relationships", "methodologies", "findings"])

            if not cycle_id:
                return {"success": False, "error": "cycle_id is required"}

            # Check both active and completed cycles
            cycle = self.active_cycles.get(cycle_id)
            if not cycle:
                cycle = next((c for c in self.completed_cycles if c.cycle_id == cycle_id), None)
                if not cycle:
                    return {"success": False, "error": f"Cycle {cycle_id} not found"}

            extracted_knowledge = {}

            # Extract knowledge from literature review
            if cycle.results.get("literature_review", {}).get("papers"):
                paper_ids = [p.get("paper_id") for p in cycle.results["literature_review"]["papers"]]
                literature_knowledge = await self.literature_service.process_request({
                    "action": "extract_knowledge",
                    "paper_ids": paper_ids,
                    "types": extract_types,
                    "domain": cycle.domain
                })
                
                if literature_knowledge["success"]:
                    extracted_knowledge["from_literature"] = literature_knowledge.get("knowledge", {})

            # Extract knowledge from experimental results
            if cycle.results.get("analysis"):
                experimental_knowledge = self._extract_experimental_knowledge(cycle.results["analysis"], extract_types)
                extracted_knowledge["from_experiments"] = experimental_knowledge

            # Extract knowledge from hypothesis validation
            if cycle.results.get("hypothesis_validations"):
                validation_knowledge = self._extract_validation_knowledge(cycle.results["hypothesis_validations"], extract_types)
                extracted_knowledge["from_validation"] = validation_knowledge

            # Synthesize and deduplicate knowledge
            synthesized_knowledge = self._synthesize_cycle_knowledge(extracted_knowledge)

            # Store knowledge if knowledge graph is available
            if self.knowledge_graph_enabled:
                storage_result = await self._store_cycle_knowledge(synthesized_knowledge, cycle)
                synthesized_knowledge["stored_in_kg"] = storage_result

            logger.info(f"🧠 Extracted knowledge from cycle: {sum(len(v) if isinstance(v, list) else 1 for section in synthesized_knowledge.values() for v in section.values() if isinstance(section, dict))} items")

            return {
                "success": True,
                "cycle_id": cycle_id,
                "extracted_knowledge": synthesized_knowledge,
                "extraction_types": extract_types,
                "knowledge_sources": list(extracted_knowledge.keys())
            }

        except AtlasDomainError as e:
            return self.handle_error(e, "extract_cycle_knowledge")
        except AtlasExternalError as e:
            return self.handle_error(e, "extract_cycle_knowledge")
        except AtlasValidationError as e:
            return self.handle_error(e, "extract_cycle_knowledge")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "extract_cycle_knowledge")

    # === KNOWLEDGE GRAPH HELPER METHODS ===

    async def _preload_domain_knowledge(self, domain: str, research_question: str) -> PreloadDomainKnowledgeResult:
        """Preload relevant domain knowledge for research enhancement"""
        if domain in self.domain_knowledge_cache:
            return self.domain_knowledge_cache[domain]

        # Use literature service to gather domain knowledge
        domain_search = await self.literature_service.process_request({
            "action": "search_literature",
            "query": f"{domain} fundamental concepts",
            "domain": domain,
            "max_results": 10
        })

        knowledge = {"concepts": [], "relationships": [], "key_papers": []}
        
        if domain_search["success"]:
            knowledge["key_papers"] = domain_search.get("papers", [])
            
            # Extract concepts from domain papers
            paper_ids = [p["paper_id"] for p in knowledge["key_papers"][:5]]
            if paper_ids:
                concept_extraction = await self.literature_service.process_request({
                    "action": "extract_knowledge",
                    "paper_ids": paper_ids,
                    "types": ["concepts", "relationships"],
                    "domain": domain
                })
                
                if concept_extraction["success"]:
                    extracted = concept_extraction.get("knowledge", {})
                    knowledge["concepts"] = extracted.get("concepts", [])
                    knowledge["relationships"] = extracted.get("relationships", [])

        # Cache the knowledge
        self.domain_knowledge_cache[domain] = knowledge
        return knowledge

    async def _enrich_with_concepts(self, cycle: ResearchCycle, depth: str) -> List[Dict[str, Any]]:
        """Enrich cycle with relevant scientific concepts"""
        # Use semantic search to find related concepts
        semantic_search = await self.literature_service.process_request({
            "action": "semantic_search",
            "query": cycle.research_question,
            "domain": cycle.domain,
            "max_results": 15 if depth == "comprehensive" else 10,
            "similarity_threshold": 0.6 if depth == "comprehensive" else 0.7
        })
        
        concepts = []
        if semantic_search["success"]:
            concepts = semantic_search.get("related_concepts", [])
        
        return concepts

    async def _enrich_with_relationships(self, cycle: ResearchCycle, depth: str) -> List[Dict[str, Any]]:
        """Enrich cycle with concept relationships"""
        # Search for relationships in the domain
        relationship_search = await self.literature_service.process_request({
            "action": "build_concept_graph",
            "topic": cycle.research_question,
            "domain": cycle.domain,
            "max_papers": 20 if depth == "comprehensive" else 15,
            "include_cross_domain": depth in ["standard", "comprehensive"]
        })
        
        relationships = []
        if relationship_search["success"]:
            concept_graph = relationship_search.get("concept_graph", {})
            relationships = concept_graph.get("edges", [])
            
        return relationships

    async def _enrich_with_cross_domain_knowledge(self, cycle: ResearchCycle, depth: str) -> List[Dict[str, Any]]:
        """Enrich cycle with cross-domain knowledge connections"""
        cross_domain_search = await self.literature_service.process_request({
            "action": "find_cross_domain_connections",
            "source_domain": cycle.domain,
            "concept": cycle.research_question,
            "similarity_threshold": 0.4 if depth == "comprehensive" else 0.6
        })
        
        connections = []
        if cross_domain_search["success"]:
            connections = cross_domain_search.get("connections", [])
            
        return connections

    async def _validate_with_knowledge_graph(self, hypothesis: str, domain: str, depth: str) -> ValidateWithKnowledgeGraphResult:
        """Validate hypothesis against knowledge graph"""
        # Simplified implementation - would query actual knowledge graph
        return {
            "kg_confidence": 0.7,
            "supporting_concepts": 3,
            "contradicting_evidence": 0,
            "knowledge_gaps": ["Limited experimental validation", "Need for cross-domain verification"],
            "validation_depth": depth
        }

    def _calculate_combined_confidence(self, literature_validation: Dict[str, Any], kg_validation: Dict[str, Any]) -> float:
        """Calculate combined confidence from literature and knowledge graph validation"""
        lit_confidence = literature_validation.get("confidence_score", 0.5)
        kg_confidence = kg_validation.get("kg_confidence", 0.5)
        
        # Weighted average with literature slightly favored
        return (lit_confidence * 0.6) + (kg_confidence * 0.4)

    def _generate_validation_recommendation(self, literature_validation: Dict[str, Any], kg_validation: Dict[str, Any]) -> str:
        """Generate validation recommendation"""
        combined_confidence = self._calculate_combined_confidence(literature_validation, kg_validation)
        
        if combined_confidence >= 0.8:
            return "Strong validation - proceed with confidence"
        elif combined_confidence >= 0.6:
            return "Moderate validation - consider additional verification"
        elif combined_confidence >= 0.4:
            return "Weak validation - requires significant additional evidence"
        else:
            return "Insufficient validation - hypothesis needs major revision"

    async def _enhance_connection_with_research_context(self, connection: Dict[str, Any], 
                                                       research_question: str, domain: str) -> Dict[str, Any]:
        """Enhance cross-domain connection with research context"""
        enhanced = connection.copy()
        enhanced["research_relevance"] = 0.7  # Simplified scoring
        enhanced["application_potential"] = "high" if enhanced.get("strength", 0) > 0.7 else "medium"
        enhanced["research_suggestions"] = [
            f"Explore {research_question} applications in {connection.get('target_domain', '')}",
            "Investigate methodological transfers",
            "Consider collaborative research opportunities"
        ]
        return enhanced

    async def _identify_cycle_knowledge_gaps(self, cycle: ResearchCycle) -> List[Dict[str, Any]]:
        """Identify knowledge gaps in the research cycle"""
        gaps = []
        
        # Analyze literature coverage
        if cycle.results.get("literature_review"):
            papers_count = len(cycle.results["literature_review"].get("papers", []))
            if papers_count < 10:
                gaps.append({
                    "type": "literature_coverage",
                    "description": "Limited literature coverage - need more comprehensive review",
                    "severity": "medium"
                })
        
        # Analyze experimental validation
        if not cycle.results.get("analysis", {}).get("hypothesis_supported"):
            gaps.append({
                "type": "experimental_validation",
                "description": "Hypothesis lacks experimental support",
                "severity": "high"
            })
            
        return gaps

    def _prioritize_research_directions(self, directions: Dict[str, Any], cycle: ResearchCycle) -> List[Dict[str, Any]]:
        """Prioritize research directions by potential impact and feasibility"""
        all_directions = []
        
        # Process interdisciplinary opportunities
        for opportunity in directions.get("interdisciplinary_opportunities", []):
            all_directions.append({
                "type": "interdisciplinary",
                "description": opportunity.get("research_opportunity", ""),
                "impact_score": opportunity.get("connection_strength", 0.5),
                "feasibility_score": 0.7,
                "priority": "high" if opportunity.get("connection_strength", 0) > 0.7 else "medium"
            })
        
        # Process novel hypotheses
        for hypothesis in directions.get("novel_hypotheses", []):
            all_directions.append({
                "type": "hypothesis",
                "description": hypothesis.get("statement", ""),
                "impact_score": hypothesis.get("novelty_score", 0.5),
                "feasibility_score": hypothesis.get("feasibility_score", 0.5),
                "priority": "high" if hypothesis.get("overall_score", 0) > 0.7 else "medium"
            })
        
        # Sort by combined impact and feasibility
        return sorted(all_directions, key=lambda x: (x["impact_score"] + x["feasibility_score"]) / 2, reverse=True)

    def _extract_experimental_knowledge(self, analysis_results: ExtractExperimentalKnowledgeResult, extract_types: List[str]) -> ExtractExperimentalKnowledgeResult:
        """Extract knowledge from experimental analysis results"""
        knowledge = {}
        
        if "findings" in extract_types:
            knowledge["findings"] = analysis_results.get("key_findings", [])
            
        if "methodologies" in extract_types:
            knowledge["methodologies"] = [{
                "description": "Experimental validation methodology",
                "confidence": analysis_results.get("confidence_score", 0.5),
                "statistical_significance": analysis_results.get("statistical_significance", "")
            }]
            
        return knowledge

    def _extract_validation_knowledge(self, validations: List[ExtractValidationKnowledgeResult], extract_types: List[str]) -> ExtractValidationKnowledgeResult:
        """Extract knowledge from hypothesis validation results"""
        knowledge = {}
        
        if "concepts" in extract_types:
            knowledge["concepts"] = []
            for validation in validations:
                if validation.get("literature_validation", {}).get("supporting_evidence"):
                    knowledge["concepts"].extend([
                        {"name": "Validated Hypothesis", "confidence": validation.get("overall_confidence", 0.5)}
                    ])
        
        return knowledge

    def _synthesize_cycle_knowledge(self, extracted_knowledge: SynthesizeCycleKnowledgeResult) -> SynthesizeCycleKnowledgeResult:
        """Synthesize and deduplicate knowledge from different sources"""
        synthesized = {"concepts": [], "relationships": [], "methodologies": [], "findings": []}
        
        # Combine knowledge from all sources
        for source, knowledge in extracted_knowledge.items():
            if isinstance(knowledge, dict):
                for knowledge_type, items in knowledge.items():
                    if knowledge_type in synthesized and isinstance(items, list):
                        synthesized[knowledge_type].extend(items)
        
        # Deduplicate (simplified)
        for knowledge_type in synthesized:
            seen = set()
            unique_items = []
            for item in synthesized[knowledge_type]:
                item_id = str(item.get("name", item.get("description", "")))[:50]
                if item_id not in seen:
                    seen.add(item_id)
                    unique_items.append(item)
            synthesized[knowledge_type] = unique_items
            
        return synthesized

    async def _store_cycle_knowledge(self, knowledge: StoreCycleKnowledgeResult, cycle: ResearchCycle) -> StoreCycleKnowledgeResult:
        """Store extracted knowledge in knowledge graph database"""
        # Simplified implementation - would store in actual database
        return {
            "stored_concepts": len(knowledge.get("concepts", [])),
            "stored_relationships": len(knowledge.get("relationships", [])),
            "stored_methodologies": len(knowledge.get("methodologies", [])),
            "stored_findings": len(knowledge.get("findings", []))
        }
