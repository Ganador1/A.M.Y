"""
Scientific Copilot Interface for AXIOM Phase 3
Provides a unified interface for autonomous scientific research workflows
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from app.services.base_service import BaseService
from app.services.workflow_orchestration import WorkflowOrchestratorService
from app.services.scientific_hypothesis_agent import ScientificHypothesisAgent
from app.services.bayesian_optimization import BayesianOptimizationService
from app.services.surrogate_modeling import SurrogateModelingService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.scientific_copilot_types import (
    ProcessRequestResult,
    StartResearchSessionResult,
    AdvanceResearchPhaseResult,
    GetResearchStatusResult,
    GenerateHypothesesResult,
    DesignExperimentsResult,
    RunAutonomousCycleResult,
    AnalyzeResultsResult,
    PerformStatisticalAnalysisResult,
    GenerateInsightsResult,
    OptimizeParametersResult,
    CreateSurrogateModelResult,
    RefineHypothesesFromInsightsResult,
    GetResearchSummaryResult,
)


class ResearchPhase(Enum):
    """Phases of the scientific research cycle"""
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    EXPERIMENTAL_DESIGN = "experimental_design"
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    INTERPRETATION = "interpretation"
    ITERATION = "iteration"


@dataclass
class ResearchSession:
    """Active research session"""
    session_id: str
    research_topic: str
    current_phase: ResearchPhase = ResearchPhase.HYPOTHESIS_GENERATION
    hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    experiments: List[Dict[str, Any]] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    # Service instances
    workflow_service: Optional[WorkflowOrchestratorService] = None
    hypothesis_agent: Optional[ScientificHypothesisAgent] = None
    bayesian_optimizer: Optional[BayesianOptimizationService] = None
    surrogate_modeler: Optional[SurrogateModelingService] = None


@dataclass
class ResearchProgress:
    """Progress tracking for research session"""
    session_id: str
    phase: ResearchPhase
    progress_percentage: float
    current_task: str
    completed_tasks: List[str] = field(default_factory=list)
    pending_tasks: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


class ScientificCopilotService(BaseService):
    """
    Scientific Copilot Interface - Main entry point for AXIOM Phase 3
    Orchestrates autonomous scientific research workflows with iterative refinement
    """

    def __init__(self):
        super().__init__("ScientificCopilot")
        self.active_sessions: Dict[str, ResearchSession] = {}
        self.session_history: Dict[str, List[ResearchProgress]] = {}

        # Initialize core services
        self.workflow_service = WorkflowOrchestratorService()
        self.hypothesis_agent = ScientificHypothesisAgent()
        self.bayesian_optimizer = BayesianOptimizationService()
        self.surrogate_modeler = SurrogateModelingService()

        logger.info("✅ ScientificCopilotService initialized with all AXIOM Phase 3 services")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process scientific copilot requests"""
        try:
            action = request_data.get("action", "")

            if action == "start_research_session":
                return await self.start_research_session(request_data)
            elif action == "advance_research_phase":
                return await self.advance_research_phase(request_data)
            elif action == "get_research_status":
                return self.get_research_status(request_data)
            elif action == "generate_hypotheses":
                return await self.generate_hypotheses(request_data)
            elif action == "design_experiments":
                return await self.design_experiments(request_data)
            elif action == "run_autonomous_cycle":
                return await self.run_autonomous_cycle(request_data)
            elif action == "analyze_results":
                return await self.analyze_results(request_data)
            elif action == "generate_insights":
                return await self.generate_insights(request_data)
            elif action == "optimize_parameters":
                return await self.optimize_parameters(request_data)
            elif action == "create_surrogate_model":
                return await self.create_surrogate_model(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "start_research_session", "advance_research_phase", "get_research_status",
                        "generate_hypotheses", "design_experiments", "run_autonomous_cycle",
                        "analyze_results", "generate_insights", "optimize_parameters", "create_surrogate_model"
                    ]
                }

        except BiologyError as e:
            return self.handle_error(e, "process_request")

    async def start_research_session(self, request_data: StartResearchSessionResult) -> StartResearchSessionResult:
        """Start a new research session"""
        try:
            import uuid

            research_topic = request_data.get("research_topic", "")
            domain = request_data.get("domain", "general")
            initial_context = request_data.get("initial_context", {})

            if not research_topic:
                return {
                    "success": False,
                    "error": "research_topic is required"
                }

            session_id = str(uuid.uuid4())

            session = ResearchSession(
                session_id=session_id,
                research_topic=research_topic,
                current_phase=ResearchPhase.HYPOTHESIS_GENERATION,
                workflow_service=self.workflow_service,
                hypothesis_agent=self.hypothesis_agent,
                bayesian_optimizer=self.bayesian_optimizer,
                surrogate_modeler=self.surrogate_modeler
            )

            self.active_sessions[session_id] = session

            # Initialize progress tracking
            self.session_history[session_id] = []

            logger.info("✅ Started research session: %s - %s", session_id, research_topic)

            return {
                "success": True,
                "message": f"Research session started for topic: {research_topic}",
                "session_id": session_id,
                "current_phase": session.current_phase.value,
                "domain": domain,
                "initial_context": initial_context
            }

        except BiologyError as e:
            return self.handle_error(e, "start_research_session")

    async def advance_research_phase(self, request_data: AdvanceResearchPhaseResult) -> AdvanceResearchPhaseResult:
        """Advance to the next research phase"""
        try:
            session_id = request_data.get("session_id")

            if not session_id or session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Research session {session_id} not found"
                }

            session = self.active_sessions[session_id]
            current_phase = session.current_phase

            # Determine next phase
            phase_order = list(ResearchPhase)
            current_index = phase_order.index(current_phase)

            if current_index < len(phase_order) - 1:
                next_phase = phase_order[current_index + 1]
                session.current_phase = next_phase
                session.last_updated = datetime.now()

                logger.info("✅ Advanced session %s to phase: %s", session_id, next_phase.value)

                return {
                    "success": True,
                    "message": f"Advanced to research phase: {next_phase.value}",
                    "session_id": session_id,
                    "previous_phase": current_phase.value,
                    "current_phase": next_phase.value,
                    "phase_description": self._get_phase_description(next_phase)
                }
            else:
                return {
                    "success": False,
                    "error": "Already in final research phase",
                    "current_phase": current_phase.value
                }

        except BiologyError as e:
            return self.handle_error(e, "advance_research_phase")

    def _get_phase_description(self, phase: ResearchPhase) -> str:
        """Get description for a research phase"""
        descriptions = {
            ResearchPhase.HYPOTHESIS_GENERATION: "Generating and refining research hypotheses",
            ResearchPhase.EXPERIMENTAL_DESIGN: "Designing optimal experiments using Bayesian optimization",
            ResearchPhase.DATA_COLLECTION: "Collecting experimental data and observations",
            ResearchPhase.ANALYSIS: "Analyzing data using statistical and computational methods",
            ResearchPhase.INTERPRETATION: "Interpreting results and drawing conclusions",
            ResearchPhase.ITERATION: "Iterating on findings to refine hypotheses and design"
        }
        return descriptions.get(phase, "Unknown phase")

    def get_research_status(self, request_data: GetResearchStatusResult) -> GetResearchStatusResult:
        """Get status of a research session"""
        try:
            session_id = request_data.get("session_id")

            if not session_id or session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Research session {session_id} not found"
                }

            session = self.active_sessions[session_id]

            return {
                "success": True,
                "session_id": session_id,
                "research_topic": session.research_topic,
                "current_phase": session.current_phase.value,
                "phase_description": self._get_phase_description(session.current_phase),
                "hypotheses_count": len(session.hypotheses),
                "experiments_count": len(session.experiments),
                "results_count": len(session.results),
                "insights_count": len(session.insights),
                "created_at": session.created_at.isoformat(),
                "last_updated": session.last_updated.isoformat()
            }

        except BiologyError as e:
            return self.handle_error(e, "get_research_status")

    async def generate_hypotheses(self, request_data: GenerateHypothesesResult) -> GenerateHypothesesResult:
        """Generate research hypotheses"""
        try:
            session_id = request_data.get("session_id")
            context = request_data.get("context", {})
            domain_knowledge = request_data.get("domain_knowledge", {})

            if not session_id or session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Research session {session_id} not found"
                }

            session = self.active_sessions[session_id]

            # Generate multiple hypotheses for different aspects
            hypotheses = []
            domains_to_explore = ["materials_science", "chemistry", "optimization"]

            for domain in domains_to_explore:
                try:
                    # Use hypothesis agent to generate hypothesis for this domain
                    hypothesis_request = {
                        "action": "generate_hypothesis",
                        "domain": domain,
                        "research_question": session.research_topic,
                        "context_data": {**context, **domain_knowledge}
                    }

                    hypothesis_result = await session.hypothesis_agent.process_request(hypothesis_request)

                    if hypothesis_result.get("success"):
                        hyp_data = hypothesis_result.get("hypothesis", {})
                        hypotheses.append({
                            "id": hypothesis_result.get("hypothesis_id"),
                            "title": hyp_data.get("title"),
                            "description": hyp_data.get("description"),
                            "domain": domain,
                            "variables": hyp_data.get("variables", []),
                            "expected_outcome": hyp_data.get("expected_outcome"),
                            "confidence_score": hyp_data.get("confidence_score", 0.5)
                        })

                except BiologyError as e:
                    logger.warning("Failed to generate hypothesis for domain %s: %s", domain, e)
                    continue

            # Add generated hypotheses to session
            session.hypotheses.extend(hypotheses)

            logger.info("✅ Generated %d hypotheses for session %s", len(hypotheses), session_id)

            return {
                "success": True,
                "message": f"Generated {len(hypotheses)} hypotheses successfully",
                "hypotheses": hypotheses
            }

        except BiologyError as e:
            return self.handle_error(e, "generate_hypotheses")

    async def design_experiments(self, request_data: DesignExperimentsResult) -> DesignExperimentsResult:
        """Design experiments using Bayesian optimization"""
        try:
            session_id = request_data.get("session_id")
            hypothesis_id = request_data.get("hypothesis_id")
            parameter_bounds = request_data.get("parameter_bounds", {})

            if not session_id or session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Research session {session_id} not found"
                }

            session = self.active_sessions[session_id]

            # Find the hypothesis
            target_hypothesis = None
            for hyp in session.hypotheses:
                if hyp.get("id") == hypothesis_id:
                    target_hypothesis = hyp
                    break

            if not target_hypothesis:
                return {
                    "success": False,
                    "error": f"Hypothesis {hypothesis_id} not found"
                }

            # Create Bayesian optimizer for experimental design
            optimizer_request = {
                "action": "create_optimizer",
                "parameter_bounds": parameter_bounds,
                "objective_config": {
                    "type": "experimental_design",
                    "hypothesis": target_hypothesis
                },
                "max_iterations": 20,
                "acquisition_function": "expected_improvement"
            }

            optimizer_result = await session.bayesian_optimizer.process_request(optimizer_request)

            if optimizer_result.get("success"):
                optimizer_id = optimizer_result["optimizer_id"]

                # Run optimization to generate observations
                design_result = await session.bayesian_optimizer.process_request({
                    "action": "run_optimization",
                    "optimizer_id": optimizer_id
                })

                if design_result.get("success"):
                    # Fetch detailed iteration results
                    results_data = await session.bayesian_optimizer.process_request({
                        "action": "get_optimization_results",
                        "optimizer_id": optimizer_id
                    })

                    iteration_results = results_data.get("results", []) if results_data.get("success") else []

                    # Create experiment designs from optimization iterations
                    experiments = []
                    for i, it in enumerate(iteration_results):
                        experiment = {
                            "id": f"exp_{i+1}",
                            "hypothesis_id": hypothesis_id,
                            "parameters": it.get("parameters", {}),
                            "expected_outcome": it.get("objective_value"),
                            "design_method": "bayesian_optimization",
                            "created_at": datetime.now().isoformat()
                        }
                        experiments.append(experiment)

                    session.experiments.extend(experiments)

                    return {
                        "success": True,
                        "message": f"Designed {len(experiments)} experiments for hypothesis {hypothesis_id}",
                        "session_id": session_id,
                        "hypothesis_id": hypothesis_id,
                        "experiments": experiments,
                        "optimizer_id": optimizer_id
                    }

            return optimizer_result

        except BiologyError as e:
            return self.handle_error(e, "design_experiments")

    async def run_autonomous_cycle(self, request_data: RunAutonomousCycleResult) -> RunAutonomousCycleResult:
        """Run a complete autonomous research cycle"""
        try:
            session_id = request_data.get("session_id")
            max_iterations = request_data.get("max_iterations", 3)

            if not session_id or session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Research session {session_id} not found"
                }

            session = self.active_sessions[session_id]

            cycle_results = []
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"🔄 Starting autonomous cycle iteration {iteration} for session {session_id}")

                # Phase 1: Generate/refine hypotheses
                if session.current_phase == ResearchPhase.HYPOTHESIS_GENERATION:
                    hypothesis_result = await self.generate_hypotheses({
                        "session_id": session_id,
                        "context": {"iteration": iteration}
                    })

                    if hypothesis_result.get("success"):
                        await self.advance_research_phase({"session_id": session_id})

                # Phase 2: Design experiments
                elif session.current_phase == ResearchPhase.EXPERIMENTAL_DESIGN:
                    if session.hypotheses:
                        # Design experiments for the first hypothesis
                        hypothesis_id = session.hypotheses[0].get("id")
                        design_result = await self.design_experiments({
                            "session_id": session_id,
                            "hypothesis_id": hypothesis_id,
                            "parameter_bounds": request_data.get("parameter_bounds", {})
                        })

                        if design_result.get("success"):
                            await self.advance_research_phase({"session_id": session_id})

                # Phase 3: Simulate data collection and analysis
                elif session.current_phase == ResearchPhase.DATA_COLLECTION:
                    # Simulate data collection
                    simulated_results = await self._simulate_data_collection(session)
                    session.results.extend(simulated_results)
                    await self.advance_research_phase({"session_id": session_id})

                # Phase 4: Analysis
                elif session.current_phase == ResearchPhase.ANALYSIS:
                    analysis_result = await self.analyze_results({
                        "session_id": session_id
                    })

                    if analysis_result.get("success"):
                        await self.advance_research_phase({"session_id": session_id})

                # Phase 5: Interpretation and iteration
                elif session.current_phase == ResearchPhase.INTERPRETATION:
                    insights_result = await self.generate_insights({
                        "session_id": session_id
                    })

                    if insights_result.get("success"):
                        await self.advance_research_phase({"session_id": session_id})

                # Phase 6: Iteration
                elif session.current_phase == ResearchPhase.ITERATION:
                    # Refine hypotheses based on insights
                    refinement_result = await self._refine_hypotheses_from_insights(session)

                    # Reset to hypothesis generation for next iteration
                    session.current_phase = ResearchPhase.HYPOTHESIS_GENERATION

                    cycle_results.append({
                        "iteration": iteration,
                        "completed_phases": ["hypothesis_generation", "experimental_design",
                                           "data_collection", "analysis", "interpretation", "iteration"],
                        "refinement_result": refinement_result
                    })

                    logger.info(f"✅ Completed autonomous cycle iteration {iteration}")

                # Check for convergence or stopping criteria
                if self._check_convergence_criteria(session):
                    logger.info(f"🎯 Convergence achieved after {iteration} iterations")
                    break

            return {
                "success": True,
                "message": f"Completed {iteration} autonomous research cycles",
                "session_id": session_id,
                "total_iterations": iteration,
                "cycle_results": cycle_results,
                "final_status": self.get_research_status({"session_id": session_id})
            }

        except BiologyError as e:
            return self.handle_error(e, "run_autonomous_cycle")

    async def _simulate_data_collection(self, session: ResearchSession) -> List[Dict[str, Any]]:
        """Simulate data collection for experiments"""
        simulated_results = []

        for experiment in session.experiments:
            # Simulate experimental outcome
            parameters = experiment.get("parameters", {})
            hypothesis_id = experiment.get("hypothesis_id")

            # Simple simulation: outcome based on parameter values
            if parameters:
                # Simulate some relationship between parameters and outcome
                outcome_value = sum(param_val * (0.5 + 0.1 * i) for i, param_val in enumerate(parameters.values()))
                outcome_value += np.random.normal(0, 0.1)  # Add noise
            else:
                outcome_value = np.random.normal(0.5, 0.2)

            result = {
                "experiment_id": experiment["id"],
                "hypothesis_id": hypothesis_id,
                "parameters": parameters,
                "outcome": outcome_value,
                "confidence": np.random.uniform(0.7, 0.95),
                "collected_at": datetime.now().isoformat(),
                "data_type": "simulated"
            }

            simulated_results.append(result)

        return simulated_results

    async def analyze_results(self, request_data: AnalyzeResultsResult) -> AnalyzeResultsResult:
        """Analyze experimental results"""
        try:
            session_id = request_data.get("session_id")

            if not session_id or session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Research session {session_id} not found"
                }

            session = self.active_sessions[session_id]

            if not session.results:
                return {
                    "success": False,
                    "error": "No experimental results available for analysis"
                }

            # Perform statistical analysis
            analysis_results = await self._perform_statistical_analysis(session.results)

            # Generate analysis report
            analysis_report = {
                "session_id": session_id,
                "total_experiments": len(session.results),
                "analysis_timestamp": datetime.now().isoformat(),
                "statistical_summary": analysis_results,
                "key_findings": self._extract_key_findings(analysis_results),
                "recommendations": self._generate_analysis_recommendations(analysis_results)
            }

            return {
                "success": True,
                "message": "Analysis completed successfully",
                "analysis_report": analysis_report
            }

        except BiologyError as e:
            return self.handle_error(e, "analyze_results")

    async def _perform_statistical_analysis(self, results: List[PerformStatisticalAnalysisResult]) -> PerformStatisticalAnalysisResult:
        """Perform statistical analysis on results"""
        if not results:
            return {}

        outcomes = [r.get("outcome", 0) for r in results]

        analysis = {
            "sample_size": len(outcomes),
            "mean_outcome": float(np.mean(outcomes)),
            "std_outcome": float(np.std(outcomes)),
            "min_outcome": float(np.min(outcomes)),
            "max_outcome": float(np.max(outcomes)),
            "median_outcome": float(np.median(outcomes)),
            "outcome_range": float(np.max(outcomes) - np.min(outcomes))
        }

        # Calculate confidence intervals
        if len(outcomes) > 1:
            from scipy import stats
            confidence_level = 0.95
            mean = np.mean(outcomes)
            sem = stats.sem(outcomes)
            ci_lower, ci_upper = stats.t.interval(confidence_level, len(outcomes)-1, mean, sem)

            analysis["confidence_interval"] = {
                "level": confidence_level,
                "lower": float(ci_lower),
                "upper": float(ci_upper)
            }

        return analysis

    def _extract_key_findings(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis"""
        findings = []

        if analysis_results.get("sample_size", 0) > 0:
            mean_val = analysis_results.get("mean_outcome", 0.0)
            std_val = analysis_results.get("std_outcome", 0.0)

            findings.append(f"Promedio de resultados: {mean_val:.3f}")

            if std_val > 0:
                findings.append(f"Variabilidad (desv. estándar): {std_val:.3f}")
                if mean_val != 0:
                    cv = std_val / abs(mean_val)
                    findings.append(f"Coeficiente de variación: {cv:.1%}")

        return findings

    def _generate_analysis_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        sample_size = analysis_results.get("sample_size", 0)
        std_val = analysis_results.get("std_outcome", 0)

        if sample_size < 10:
            recommendations.append("Consider collecting more experimental data for robust statistical analysis")

        if std_val > 0.5:
            recommendations.append("High variability detected - consider parameter optimization or experimental controls")

        return recommendations

    async def generate_insights(self, request_data: GenerateInsightsResult) -> GenerateInsightsResult:
        """Generate insights from research results"""
        try:
            session_id = request_data.get("session_id")

            if not session_id or session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Research session {session_id} not found"
                }

            session = self.active_sessions[session_id]

            # Use hypothesis agent to generate insights
            insights_request = {
                "action": "generate_insights",
                "research_topic": session.research_topic,
                "hypotheses": session.hypotheses,
                "experimental_results": session.results,
                "current_phase": session.current_phase.value
            }

            insights_result = await session.hypothesis_agent.process_request(insights_request)

            if insights_result.get("success"):
                new_insights = insights_result.get("insights", [])
                session.insights.extend(new_insights)

                logger.info(f"✅ Generated {len(new_insights)} insights for session {session_id}")

            return insights_result

        except BiologyError as e:
            return self.handle_error(e, "generate_insights")

    async def optimize_parameters(self, request_data: OptimizeParametersResult) -> OptimizeParametersResult:
        """Optimize parameters using Bayesian optimization"""
        try:
            session_id = request_data.get("session_id")
            parameter_bounds = request_data.get("parameter_bounds", {})
            objective_function = request_data.get("objective_function")

            if not session_id or session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Research session {session_id} not found"
                }

            session = self.active_sessions[session_id]

            # Delegate to Bayesian optimization service
            optimization_request = {
                "action": "optimize_design",
                "parameter_bounds": parameter_bounds,
                "objective_config": {
                    "type": "parameter_optimization",
                    "objective_function": objective_function
                },
                "max_iterations": request_data.get("max_iterations", 25)
            }

            return await session.bayesian_optimizer.process_request(optimization_request)

        except BiologyError as e:
            return self.handle_error(e, "optimize_parameters")

    async def create_surrogate_model(self, request_data: CreateSurrogateModelResult) -> CreateSurrogateModelResult:
        """Create surrogate model for expensive simulations"""
        try:
            session_id = request_data.get("session_id")
            simulation_config = request_data.get("simulation_config", {})

            if not session_id or session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Research session {session_id} not found"
                }

            session = self.active_sessions[session_id]

            # Delegate to surrogate modeling service
            return await session.surrogate_modeler.create_surrogate_for_simulation(simulation_config)

        except BiologyError as e:
            return self.handle_error(e, "create_surrogate_model")

    async def _refine_hypotheses_from_insights(self, session: ResearchSession) -> RefineHypothesesFromInsightsResult:
        """Refine hypotheses based on insights from previous iterations"""
        try:
            refinement_request = {
                "action": "refine_hypotheses",
                "research_topic": session.research_topic,
                "existing_hypotheses": session.hypotheses,
                "insights": session.insights,
                "experimental_results": session.results
            }

            return await session.hypothesis_agent.process_request(refinement_request)

        except BiologyError as e:
            logger.warning(f"Error refining hypotheses: {e}")
            return {"success": False, "error": str(e)}

    def _check_convergence_criteria(self, session: ResearchSession) -> bool:
        """Check if research has converged to a satisfactory solution"""
        # Simple convergence criteria
        min_hypotheses = 3
        min_experiments = 5
        min_results = 5
        min_insights = 2

        return (len(session.hypotheses) >= min_hypotheses and
                len(session.experiments) >= min_experiments and
                len(session.results) >= min_results and
                len(session.insights) >= min_insights)

    async def get_research_summary(self, session_id: str) -> GetResearchSummaryResult:
        """Get comprehensive summary of research session"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Research session {session_id} not found"
                }

            session = self.active_sessions[session_id]

            return {
                "success": True,
                "session_id": session_id,
                "research_topic": session.research_topic,
                "current_phase": session.current_phase.value,
                "progress_summary": {
                    "hypotheses_generated": len(session.hypotheses),
                    "experiments_designed": len(session.experiments),
                    "results_collected": len(session.results),
                    "insights_discovered": len(session.insights)
                },
                "timeline": {
                    "created_at": session.created_at.isoformat(),
                    "last_updated": session.last_updated.isoformat(),
                    "duration_hours": (datetime.now() - session.created_at).total_seconds() / 3600
                },
                "key_hypotheses": session.hypotheses[:3],  # Top 3 hypotheses
                "recent_insights": session.insights[-3:] if session.insights else []  # Last 3 insights
            }

        except BiologyError as e:
            return self.handle_error(e, "get_research_summary")
