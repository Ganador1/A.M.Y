"""
Autonomous Peer Review Service for AXIOM
Sistema de validación por pares autónomo basado en aiXiv, AI Scientist y CycleResearcher

Este servicio implementa:
- Validación automática del método científico
- Peer review por agentes especializados
- Detección de experimentos sin fundamento científico
- Integración con servicios científicos de AXIOM

Inspirado en:
- aiXiv: Ecosistema de publicación científica generada por AI
- AI Scientist-v2: Producción autónoma de papers científicos
- CycleResearcher: Mejora de investigación automatizada vía revisión automatizada
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import re

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.services.orchestration.tool_evidence_orchestrator import ToolEvidenceOrchestratorService
from app.types.autonomous_peer_review_service_types import (
    ProcessRequestResult,
    ValidateExperimentResult,
    ScientificCopilotGuidanceResult,
    IntegrateWithExistingServicesResult,
    ConnectToServiceResult,
    SetupValidationHookResult,
    SetupAutomatedWorkflowResult,
    RealTimeValidationResult,
    AnalyzeTrendsResult,
    GenerateImmediateFeedbackResult,
    PerformPeerReviewResult,
    BatchValidationResult,
    GetValidationStatusResult,
)


class ValidationSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ScientificDomain(Enum):
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    MEDICINE = "medicine"
    COMPUTER_SCIENCE = "computer_science"
    ENGINEERING = "engineering"
    NEUROSCIENCE = "neuroscience"
    MATERIALS_SCIENCE = "materials_science"
    DRUG_DISCOVERY = "drug_discovery"
    ENERGY_STORAGE = "energy_storage"
    QUANTUM_COMPUTING = "quantum_computing"
    BIOPHYSICS = "biophysics"
    GENOMICS = "genomics"
    BIOMEDICAL_ENGINEERING = "biomedical_engineering"
    INTERDISCIPLINARY = "interdisciplinary"


@dataclass
class ValidationIssue:
    """Issue encontrado durante la validación"""
    issue_id: str
    severity: ValidationSeverity
    category: str
    description: str
    location: str
    suggestion: str
    references: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class PeerReviewResult:
    """Resultado completo de una revisión por pares"""
    experiment_id: str
    reviewer_agent: str
    domain: ScientificDomain
    overall_score: float  # 0-10
    scientific_validity: float  # 0-10
    methodological_rigor: float  # 0-10
    novelty_contribution: float  # 0-10
    issues: List[ValidationIssue]
    recommendations: List[str]
    approved: bool
    review_date: datetime
    review_duration: float  # segundos


@dataclass
class ExperimentValidation:
    """Validación completa de un experimento"""
    experiment_id: str
    hypothesis: str
    methodology: str
    results: Dict[str, Any]
    peer_reviews: List[PeerReviewResult]
    validation_status: str
    created_at: datetime
    validated_at: Optional[datetime] = None


class AutonomousPeerReviewService(BaseService):
    """
    Servicio de validación por pares autónomo para AXIOM

    Características principales:
    - Validación automática del método científico
    - Peer review por agentes especializados
    - Detección de falacias científicas
    - Integración con servicios científicos existentes
    """

    def __init__(self):
        super().__init__("AutonomousPeerReviewService")
        self.reviewer_agents = self._initialize_reviewer_agents()
        self.validation_rules = self._load_validation_rules()
        self.tool_orchestrator = ToolEvidenceOrchestratorService()
        logger.info("✅ AutonomousPeerReviewService initialized")

    @staticmethod
    def _issue_to_dict(issue: ValidationIssue) -> Dict[str, Any]:
        """Serializar ValidationIssue incluyendo enums"""
        return {
            "issue_id": issue.issue_id,
            "severity": issue.severity.value if isinstance(issue.severity, ValidationSeverity) else str(issue.severity),
            "category": issue.category,
            "description": issue.description,
            "location": issue.location,
            "suggestion": issue.suggestion,
            "references": list(issue.references) if issue.references else [],
            "confidence": issue.confidence,
        }

    def _peer_review_to_dict(self, review: PeerReviewResult) -> Dict[str, Any]:
        """Serializar PeerReviewResult asegurando estructuras JSON friendly"""
        return {
            "experiment_id": review.experiment_id,
            "reviewer_agent": review.reviewer_agent,
            "domain": review.domain.value if isinstance(review.domain, ScientificDomain) else str(review.domain),
            "overall_score": review.overall_score,
            "scientific_validity": review.scientific_validity,
            "methodological_rigor": review.methodological_rigor,
            "novelty_contribution": review.novelty_contribution,
            "issues": [self._issue_to_dict(issue) for issue in review.issues],
            "recommendations": list(review.recommendations),
            "approved": review.approved,
            "review_date": review.review_date.isoformat() if isinstance(review.review_date, datetime) else review.review_date,
            "review_duration": review.review_duration,
        }

    def _initialize_reviewer_agents(self) -> Dict[str, Dict[str, Any]]:
        """Inicializar agentes revisores especializados por dominio"""
        return {
            # Agentes especializados por dominio principal
            "mathematical_reviewer": {
                "domain": ScientificDomain.MATHEMATICS,
                "expertise": ["proofs", "theorems", "algorithms", "mathematical modeling", "calculus", "algebra", "geometry"],
                "validation_focus": ["logical consistency", "mathematical rigor", "proof completeness", "algorithm correctness"],
                "specializations": ["pure_math", "applied_math", "computational_math"]
            },
            "physics_reviewer": {
                "domain": ScientificDomain.PHYSICS,
                "expertise": ["theoretical physics", "experimental physics", "computational physics", "quantum mechanics", "thermodynamics"],
                "validation_focus": ["physical laws", "experimental design", "measurement accuracy", "theoretical consistency"],
                "specializations": ["quantum_physics", "classical_physics", "condensed_matter", "particle_physics"]
            },
            "chemistry_reviewer": {
                "domain": ScientificDomain.CHEMISTRY,
                "expertise": ["organic chemistry", "inorganic chemistry", "computational chemistry", "physical chemistry", "analytical chemistry"],
                "validation_focus": ["chemical reactions", "molecular structures", "safety protocols", "stoichiometry", "reaction mechanisms"],
                "specializations": ["organic_synthesis", "materials_chemistry", "computational_chemistry", "analytical_chemistry"]
            },
            "biology_reviewer": {
                "domain": ScientificDomain.BIOLOGY,
                "expertise": ["molecular biology", "ecology", "neuroscience", "genomics", "microbiology", "biochemistry"],
                "validation_focus": ["biological mechanisms", "experimental controls", "statistical analysis", "biosafety"],
                "specializations": ["molecular_biology", "ecology", "neuroscience", "genomics", "microbiology"]
            },
            "biomedical_reviewer": {
                "domain": ScientificDomain.MEDICINE,
                "expertise": ["clinical trials", "medical imaging", "drug development", "diagnostics", "pharmacology", "toxicology"],
                "validation_focus": ["clinical relevance", "patient safety", "regulatory compliance", "ethical standards"],
                "specializations": ["clinical_research", "drug_discovery", "medical_imaging", "translational_medicine"]
            },
            "cs_reviewer": {
                "domain": ScientificDomain.COMPUTER_SCIENCE,
                "expertise": ["algorithms", "machine learning", "software engineering", "data science", "AI", "cybersecurity"],
                "validation_focus": ["algorithm correctness", "computational complexity", "reproducibility", "data privacy"],
                "specializations": ["machine_learning", "software_engineering", "data_science", "ai_safety", "cybersecurity"]
            },
            "engineering_reviewer": {
                "domain": ScientificDomain.ENGINEERING,
                "expertise": ["mechanical engineering", "electrical engineering", "materials science", "civil engineering", "biomedical engineering"],
                "validation_focus": ["design principles", "safety standards", "performance metrics", "feasibility analysis"],
                "specializations": ["mechanical_design", "electrical_systems", "materials_engineering", "biomedical_devices"]
            },
            "materials_science_reviewer": {
                "domain": ScientificDomain.ENGINEERING,
                "expertise": ["materials science", "nanotechnology", "polymers", "ceramics", "metallurgy", "composites"],
                "validation_focus": ["material properties", "synthesis methods", "characterization techniques", "structure-property relationships"],
                "specializations": ["nanomaterials", "polymeric_materials", "ceramic_materials", "metallic_materials"]
            },
            "data_science_reviewer": {
                "domain": ScientificDomain.COMPUTER_SCIENCE,
                "expertise": ["statistics", "data analysis", "machine learning", "big data", "data visualization", "predictive modeling"],
                "validation_focus": ["statistical validity", "data quality", "model performance", "reproducibility"],
                "specializations": ["statistical_modeling", "machine_learning", "data_mining", "predictive_analytics"]
            },
            "environmental_science_reviewer": {
                "domain": ScientificDomain.INTERDISCIPLINARY,
                "expertise": ["environmental science", "ecology", "climate science", "sustainability", "environmental chemistry"],
                "validation_focus": ["environmental impact", "sustainability assessment", "ecological validity", "regulatory compliance"],
                "specializations": ["climate_change", "ecosystem_science", "environmental_chemistry", "sustainability_studies"]
            },
            # Agente guía general interdisciplinario
            "scientific_guide_agent": {
                "domain": ScientificDomain.INTERDISCIPLINARY,
                "expertise": ["scientific_method", "research_design", "interdisciplinary_synthesis", "knowledge_integration", "scientific_communication"],
                "validation_focus": ["methodological_soundness", "interdisciplinary_coherence", "scientific_communication", "knowledge_synthesis"],
                "specializations": ["research_methodology", "scientific_writing", "peer_review_process", "interdisciplinary_research"],
                "role": "guide",
                "capabilities": ["beginner_guidance", "methodology_advice", "literature_integration", "hypothesis_development"]
            },
            "interdisciplinary_reviewer": {
                "domain": ScientificDomain.INTERDISCIPLINARY,
                "expertise": ["systems thinking", "complex systems", "multidisciplinary approaches", "integration methods"],
                "validation_focus": ["integration quality", "cross-domain validity", "holistic analysis", "systemic_understanding"],
                "specializations": ["complex_systems", "systems_engineering", "multidisciplinary_research", "holistic_analysis"]
            },
            # Sub-reviewers especializados para neurociencia
            "neuroscience_imaging_reviewer": {
                "domain": ScientificDomain.NEUROSCIENCE,
                "expertise": ["neuroimaging", "brain imaging", "fMRI", "MRI", "PET", "neural signal processing", "neuroanatomy"],
                "validation_focus": ["imaging protocols", "signal processing accuracy", "anatomical precision", "statistical analysis"],
                "specializations": ["functional_imaging", "structural_imaging", "connectomics", "neuromodulation"],
                "parent_reviewer": "biomedical_reviewer",
                "sub_specialty": "neuroimaging"
            },
            "neuroscience_molecular_reviewer": {
                "domain": ScientificDomain.NEUROSCIENCE,
                "expertise": ["molecular neuroscience", "synaptic transmission", "neurotransmitters", "neural development", "neurodegeneration"],
                "validation_focus": ["molecular mechanisms", "cellular pathways", "protein interactions", "genetic factors"],
                "specializations": ["synaptic_plasticity", "neurodegeneration", "neural_development", "neuropharmacology"],
                "parent_reviewer": "biology_reviewer",
                "sub_specialty": "molecular_neuroscience"
            },
            # Sub-reviewers para ciencia de materiales
            "materials_nanotech_reviewer": {
                "domain": ScientificDomain.MATERIALS_SCIENCE,
                "expertise": ["nanotechnology", "nanomaterials", "nanoparticles", "surface chemistry", "nanocharacterization"],
                "validation_focus": ["nanoscale properties", "characterization methods", "safety assessment", "scalability"],
                "specializations": ["nanoparticle_synthesis", "surface_functionalization", "nano_biointerfaces", "nano_toxicology"],
                "parent_reviewer": "chemistry_reviewer",
                "sub_specialty": "nanotechnology"
            },
            "materials_biomaterials_reviewer": {
                "domain": ScientificDomain.MATERIALS_SCIENCE,
                "expertise": ["biomaterials", "biocompatibility", "tissue engineering", "scaffolds", "implants"],
                "validation_focus": ["biocompatibility", "mechanical properties", "degradation behavior", "immune response"],
                "specializations": ["tissue_scaffolds", "bioactive_materials", "drug_delivery", "implant_materials"],
                "parent_reviewer": "biomedical_reviewer",
                "sub_specialty": "biomaterials"
            },
            # Sub-reviewers para biología computacional
            "computational_biology_reviewer": {
                "domain": ScientificDomain.BIOLOGY,
                "expertise": ["computational biology", "bioinformatics", "systems biology", "genomics", "proteomics"],
                "validation_focus": ["algorithm accuracy", "statistical methods", "data quality", "model validation"],
                "specializations": ["sequence_analysis", "structural_biology", "systems_modeling", "omics_integration"],
                "parent_reviewer": "biology_reviewer",
                "sub_specialty": "computational_biology"
            },
            # Sub-reviewers para ensayos clínicos
            "clinical_trials_reviewer": {
                "domain": ScientificDomain.MEDICINE,
                "expertise": ["clinical trials", "medical statistics", "patient safety", "regulatory compliance", "evidence-based medicine"],
                "validation_focus": ["trial design", "statistical power", "safety monitoring", "regulatory compliance"],
                "specializations": ["phase_trials", "biostatistics", "pharmacovigilance", "medical_devices"],
                "parent_reviewer": "biomedical_reviewer",
                "sub_specialty": "clinical_research"
            },
            # Sub-reviewers para descubrimiento de fármacos
            "drug_discovery_reviewer": {
                "domain": ScientificDomain.DRUG_DISCOVERY,
                "expertise": ["drug discovery", "medicinal chemistry", "pharmacology", "toxicology", "ADMET"],
                "validation_focus": ["target validation", "compound optimization", "safety assessment", "efficacy evaluation"],
                "specializations": ["lead_optimization", "target_identification", "drug_metabolism", "toxicity_prediction"],
                "parent_reviewer": "chemistry_reviewer",
                "sub_specialty": "medicinal_chemistry"
            },
            # Sub-reviewers para ingeniería biomédica
            "biomedical_engineering_reviewer": {
                "domain": ScientificDomain.BIOMEDICAL_ENGINEERING,
                "expertise": ["medical devices", "biosensors", "biomedical imaging", "rehabilitation engineering", "neural engineering"],
                "validation_focus": ["device performance", "biocompatibility", "safety standards", "clinical validation"],
                "specializations": ["medical_devices", "biosensing", "neural_interfaces", "rehabilitation_tech"],
                "parent_reviewer": "engineering_reviewer",
                "sub_specialty": "biomedical_devices"
            }
        }

    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Cargar reglas de validación científica"""
        return {
            "scientific_method": {
                "required_steps": [
                    "clear_hypothesis",
                    "experimental_design",
                    "controlled_variables",
                    "data_collection",
                    "statistical_analysis",
                    "conclusion_validation"
                ],
                "critical_checks": [
                    "hypothesis_testability",
                    "methodological_soundness",
                    "result_reproducibility",
                    "conclusion_justification"
                ]
            },
            "ethical_considerations": {
                "required_checks": [
                    "informed_consent",
                    "data_privacy",
                    "safety_protocols",
                    "environmental_impact",
                    "dual_use_potential"
                ]
            },
            "quality_assurance": {
                "metrics": [
                    "methodological_rigor",
                    "data_quality",
                    "statistical_power",
                    "peer_review_quality"
                ]
            }
        }

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Procesar solicitud de validación por pares"""
        try:
            action = request_data.get("action", "")

            if action == "validate_experiment":
                return await self.validate_experiment(request_data)
            elif action == "peer_review":
                return await self.perform_peer_review(request_data)
            elif action == "batch_validation":
                return await self.batch_validation(request_data)
            elif action == "get_validation_status":
                return self.get_validation_status(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": ["validate_experiment", "peer_review", "batch_validation", "get_validation_status"]
                }

        except BiologyError as e:
            return self.handle_error(e, "process_request")

    async def validate_experiment(self, request_data: ValidateExperimentResult) -> ValidateExperimentResult:
        """
        Validar un experimento completo usando el método científico

        Inspirado en CycleResearcher - validación iterativa con feedback
        """
        experiment_data = request_data.get("experiment", {})
        experiment_id = experiment_data.get("id", f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # Extraer componentes del experimento
        hypothesis = experiment_data.get("hypothesis", "")
        methodology = experiment_data.get("methodology", "")
        results = experiment_data.get("results", {})
        domain = ScientificDomain(experiment_data.get("domain", "interdisciplinary"))

        # Validación del método científico
        scientific_validation = await self._validate_scientific_method(
            hypothesis, methodology, results, domain
        )

        # Peer review por agentes especializados
        peer_reviews = await self._perform_multi_agent_review(
            experiment_id, hypothesis, methodology, results, domain
        )

        # Consolidar resultados
        overall_score = self._calculate_overall_score(peer_reviews)
        approved = overall_score >= 7.0  # Umbral de aprobación

        # ExperimentValidation object created but not used - keeping for future use
        # validation_result = ExperimentValidation(
        #     experiment_id=experiment_id,
        #     hypothesis=hypothesis,
        #     methodology=methodology,
        #     results=results,
        #     peer_reviews=peer_reviews,
        #     validation_status="approved" if approved else "rejected",
        #     created_at=datetime.now(),
        #     validated_at=datetime.now()
        # )

        return {
            "success": True,
            "experiment_id": experiment_id,
            "overall_score": overall_score,
            "approved": approved,
            "scientific_validation": scientific_validation,
            "peer_reviews": [self._peer_review_to_dict(review) for review in peer_reviews],
            "recommendations": self._consolidate_recommendations(peer_reviews)
        }

    async def _validate_scientific_method(self, hypothesis: str, methodology: str,
                                        results: Dict[str, Any], domain: ScientificDomain = ScientificDomain.INTERDISCIPLINARY) -> Dict[str, Any]:
        """
        Validar cumplimiento del método científico

        Basado en las reglas de validación de CycleResearcher
        """
        issues = []

        # 1. Validar hipótesis
        if not hypothesis or len(hypothesis.strip()) < 10:
            issues.append(ValidationIssue(
                issue_id="weak_hypothesis",
                severity=ValidationSeverity.HIGH,
                category="hypothesis",
                description="Hypothesis is too vague or insufficiently detailed",
                location="hypothesis",
                suggestion="Formulate a clear, testable hypothesis with specific predictions"
            ))

        # 2. Validar testabilidad (domain-aware)
        if not self._is_hypothesis_testable(hypothesis, domain, results):
            issues.append(ValidationIssue(
                issue_id="untestable_hypothesis",
                severity=ValidationSeverity.CRITICAL,
                category="hypothesis",
                description="Hypothesis is not testable with the expected methods for this domain",
                location="hypothesis",
                suggestion=(
                    "For empirical domains, ensure it can be tested via observation/experimentation. "
                    "For mathematics, include a verifiable statement (bounds, counterexample search, proof obligations) or explicit computational verification plan."
                )
            ))

        # 3. Validar metodología
        methodology_issues = self._validate_methodology(methodology, domain)
        issues.extend(methodology_issues)

        # 4. Validar resultados
        results_issues = self._validate_results(results, domain)
        issues.extend(results_issues)

        # 5. Validar conclusiones
        conclusion_issues = self._validate_conclusions(hypothesis, results)
        issues.extend(conclusion_issues)

        return {
            "valid": len([i for i in issues if i.severity == ValidationSeverity.CRITICAL]) == 0,
            "issues": [self._issue_to_dict(issue) for issue in issues],
            "score": max(0, 10 - len(issues) * 0.5)
        }

    def _is_hypothesis_testable(self, hypothesis: str, domain: ScientificDomain = ScientificDomain.INTERDISCIPLINARY, results: Dict[str, Any] | None = None) -> bool:
        """Verificar si una hipótesis es testable (ajustado por dominio)."""
        hypothesis_lower = (hypothesis or "").lower()

        if domain == ScientificDomain.MATHEMATICS:
            math_indicators = [
                "prove", "proof", "lemma", "theorem", "proposition",
                "verify", "verification", "counterexample", "no counterexample",
                "for all", "exists", "iff", "if and only if",
                "up to", "<=", "\u2264", "bound", "upper bound", "lower bound",
                "algorithm", "complexity", "computational"
            ]
            if any(ind in hypothesis_lower for ind in math_indicators):
                return True

            # También consideramos testable si hay evidencia computacional adjunta
            if isinstance(results, dict) and results.get("tool_results"):
                return True
            return False

        testable_indicators = [
            "predict", "expect", "should", "will", "increase", "decrease",
            "greater than", "less than", "different from", "same as",
            "correlated", "associated", "caused by", "leads to",
            "measured", "observed", "experiment", "trial"
        ]

        return any(indicator in hypothesis_lower for indicator in testable_indicators)

    def _validate_methodology(self, methodology: str, domain: ScientificDomain = ScientificDomain.INTERDISCIPLINARY) -> List[ValidationIssue]:
        """Validar la metodología experimental"""
        issues = []

        if domain == ScientificDomain.MATHEMATICS:
            if not methodology or len(methodology.strip()) < 20:
                issues.append(ValidationIssue(
                    issue_id="insufficient_methodology",
                    severity=ValidationSeverity.HIGH,
                    category="methodology",
                    description="Methodology is too brief for a mathematical/computational validation",
                    location="methodology",
                    suggestion="Describe the verification approach (proof strategy or computational bounds, algorithm, and reproducibility details)"
                ))

            repro_indicators = ["code", "script", "deterministic", "reproduc", "bound", "verified", "up to", "algorithm"]
            if not any(indicator in (methodology or "").lower() for indicator in repro_indicators):
                issues.append(ValidationIssue(
                    issue_id="low_replicability",
                    severity=ValidationSeverity.MEDIUM,
                    category="methodology",
                    description="Limited information about computational reproducibility",
                    location="methodology",
                    suggestion="Include exact bounds, algorithm details, and how to reproduce the verification"
                ))
            return issues

        if not methodology or len(methodology.strip()) < 50:
            issues.append(ValidationIssue(
                issue_id="insufficient_methodology",
                severity=ValidationSeverity.HIGH,
                category="methodology",
                description="Methodology description is too brief or incomplete",
                location="methodology",
                suggestion="Provide detailed experimental procedures, controls, and variables"
            ))

        # Verificar controles experimentales
        if "control" not in methodology.lower():
            issues.append(ValidationIssue(
                issue_id="missing_controls",
                severity=ValidationSeverity.MEDIUM,
                category="methodology",
                description="No mention of experimental controls",
                location="methodology",
                suggestion="Include appropriate control groups or conditions"
            ))

        # Verificar replicabilidad
        replicability_indicators = ["repeat", "replicate", "sample size", "n=", "trials"]
        if not any(indicator in methodology.lower() for indicator in replicability_indicators):
            issues.append(ValidationIssue(
                issue_id="low_replicability",
                severity=ValidationSeverity.MEDIUM,
                category="methodology",
                description="Limited information about replicability",
                location="methodology",
                suggestion="Specify sample sizes, number of trials, and replication procedures"
            ))

        return issues

    def _validate_results(self, results: Dict[str, Any], domain: ScientificDomain = ScientificDomain.INTERDISCIPLINARY) -> List[ValidationIssue]:
        """Validar la calidad de los resultados"""
        issues = []

        if domain == ScientificDomain.MATHEMATICS:
            if not results:
                issues.append(ValidationIssue(
                    issue_id="missing_results",
                    severity=ValidationSeverity.CRITICAL,
                    category="results",
                    description="No results data provided",
                    location="results",
                    suggestion="Include computational verification outputs and summary statistics"
                ))
                return issues

            # En matemáticas, pedimos evidencia computacional (tools) o una verificación explícita.
            tool_results = results.get("tool_results") if isinstance(results, dict) else None

            if not tool_results:
                issues.append(ValidationIssue(
                    issue_id="missing_tool_evidence",
                    severity=ValidationSeverity.MEDIUM,
                    category="results",
                    description="No tool-driven evidence attached",
                    location="results",
                    suggestion="Attach at least one computational verification result (bounds checked, counts, or failure cases)"
                ))
            return issues

        if not results:
            issues.append(ValidationIssue(
                issue_id="missing_results",
                severity=ValidationSeverity.CRITICAL,
                category="results",
                description="No results data provided",
                location="results",
                suggestion="Include quantitative results, measurements, or observations"
            ))
            return issues

        # Verificar análisis estadístico
        if "statistics" not in str(results).lower() and "p-value" not in str(results).lower():
            issues.append(ValidationIssue(
                issue_id="missing_statistics",
                severity=ValidationSeverity.MEDIUM,
                category="results",
                description="No statistical analysis mentioned",
                location="results",
                suggestion="Include appropriate statistical tests and significance levels"
            ))

        # Verificar reproducibilidad
        if "error" not in str(results).lower() and "uncertainty" not in str(results).lower():
            issues.append(ValidationIssue(
                issue_id="missing_uncertainty",
                severity=ValidationSeverity.LOW,
                category="results",
                description="No uncertainty or error analysis provided",
                location="results",
                suggestion="Include error bars, confidence intervals, or uncertainty estimates"
            ))

        return issues

    def _validate_conclusions(self, hypothesis: str, results: Dict[str, Any]) -> List[ValidationIssue]:
        """Validar las conclusiones del experimento"""
        issues = []

        # Aquí iría lógica para validar que las conclusiones están respaldadas por los resultados
        # Por simplicidad, implementamos validaciones básicas

        if not results:
            issues.append(ValidationIssue(
                issue_id="unsupported_conclusions",
                severity=ValidationSeverity.HIGH,
                category="conclusions",
                description="Conclusions cannot be validated without results",
                location="conclusions",
                suggestion="Ensure conclusions are directly supported by experimental results"
            ))

        return issues

    async def _perform_multi_agent_review(self, experiment_id: str, hypothesis: str,
                                       methodology: str, results: Dict[str, Any],
                                       domain: ScientificDomain) -> List[PeerReviewResult]:
        """
        Realizar revisión por múltiples agentes especializados

        Inspirado en aiXiv - múltiples agentes revisores
        """
        reviews = []

        # Seleccionar agentes relevantes para el dominio
        relevant_agents = self._select_relevant_agents(domain)

        for agent_name, agent_config in relevant_agents.items():
            review = await self._simulate_peer_review(
                agent_name, agent_config, experiment_id,
                hypothesis, methodology, results
            )
            reviews.append(review)

        return reviews

    def _select_relevant_agents(self, domain: ScientificDomain) -> Dict[str, Dict[str, Any]]:
        """Seleccionar agentes revisores relevantes para el dominio"""
        if domain == ScientificDomain.INTERDISCIPLINARY:
            # Para trabajos interdisciplinarios, usar múltiples agentes incluyendo el guía
            return {
                "scientific_guide_agent": self.reviewer_agents["scientific_guide_agent"],
                "interdisciplinary_reviewer": self.reviewer_agents["interdisciplinary_reviewer"],
                "cs_reviewer": self.reviewer_agents["cs_reviewer"]
            }

        # Mapear dominio a agentes específicos con especializaciones
        domain_agent_map = {
            ScientificDomain.MATHEMATICS: ["mathematical_reviewer"],
            ScientificDomain.PHYSICS: ["physics_reviewer"],
            ScientificDomain.CHEMISTRY: ["chemistry_reviewer", "materials_science_reviewer"],
            ScientificDomain.BIOLOGY: ["biology_reviewer", "biomedical_reviewer", "computational_biology_reviewer"],
            ScientificDomain.MEDICINE: ["biomedical_reviewer", "biology_reviewer", "clinical_trials_reviewer"],
            ScientificDomain.COMPUTER_SCIENCE: ["cs_reviewer", "data_science_reviewer"],
            ScientificDomain.ENGINEERING: ["engineering_reviewer", "materials_science_reviewer"],
            ScientificDomain.NEUROSCIENCE: ["neuroscience_imaging_reviewer", "neuroscience_molecular_reviewer", "biomedical_reviewer"],
            ScientificDomain.MATERIALS_SCIENCE: ["materials_nanotech_reviewer", "materials_biomaterials_reviewer", "chemistry_reviewer"],
            ScientificDomain.DRUG_DISCOVERY: ["drug_discovery_reviewer", "chemistry_reviewer", "biomedical_reviewer"],
            ScientificDomain.BIOMEDICAL_ENGINEERING: ["biomedical_engineering_reviewer", "engineering_reviewer", "biomedical_reviewer"],
            ScientificDomain.GENOMICS: ["computational_biology_reviewer", "biology_reviewer", "biomedical_reviewer"],
            ScientificDomain.BIOPHYSICS: ["physics_reviewer", "biology_reviewer", "computational_biology_reviewer"]
        }

        # Obtener agentes principales para el dominio
        primary_agents = domain_agent_map.get(domain, ["interdisciplinary_reviewer"])

        # Siempre incluir el agente guía para contexto general
        selected_agents = {agent: self.reviewer_agents[agent] for agent in primary_agents}
        selected_agents["scientific_guide_agent"] = self.reviewer_agents["scientific_guide_agent"]

        return selected_agents

    async def _simulate_peer_review(self, agent_name: str, agent_config: Dict[str, Any],
                                  experiment_id: str, hypothesis: str, methodology: str,
                                  results: Dict[str, Any]) -> PeerReviewResult:
        """
        Simular revisión por pares por un agente especializado, AHORA CON VALIDACIÓN DE HERRAMIENTAS.
        """
        start_time = datetime.now()
        domain_str = agent_config["domain"].value if isinstance(agent_config["domain"], ScientificDomain) else str(agent_config["domain"])

        # 1. Validación Computacional con Herramientas (Nuevo)
        tool_evidence = await self._corroborate_with_tools(hypothesis, methodology, domain_str)
        
        # 2. Análisis Inteligente con LLM (Nuevo: Deep Understanding)
        # Construct simplified paper content for review
        paper_content_sim = f"METHODOLOGY:\n{methodology}\n\nRESULTS:\n{str(results)}"
        
        llm_review = await self._intelligent_llm_review(
            hypothesis=hypothesis,
            paper_content=paper_content_sim,
            domain=domain_str
        )
        
        # Use LLM scores if available, otherwise fallback to heuristics
        if llm_review and llm_review.get("success") and llm_review.get("llm_review"):
            scientific_validity = llm_review.get("rigor_score", 5.0)
            methodological_rigor = llm_review.get("methodology_score", 5.0)
            novelty_contribution = llm_review.get("novelty_score", 5.0)
            overall_score = llm_review.get("overall_score", 5.0)
            
            # Extract recommendations from LLM
            recommendations = llm_review.get("actionable_feedback", [])
            if llm_review.get("key_question"):
                recommendations.insert(0, f"Key Question: {llm_review.get('key_question')}")
                
            # Log strengths
            logger.info(f"✅ Peer Review Strengths: {', '.join(llm_review.get('strengths', [])[:3])}")
        else:
            # Fallback to heuristics
            scientific_validity = self._assess_scientific_validity(hypothesis, methodology, results)
            methodological_rigor = self._assess_methodological_rigor(methodology)
            novelty_contribution = self._assess_novelty_contribution(hypothesis, results)
            overall_score = (scientific_validity + methodological_rigor + novelty_contribution) / 3
            recommendations = []

        # Ajustar scores con evidencia de herramientas (weighted boost)
        if tool_evidence:
            if tool_evidence.get('success'):
                support_score = tool_evidence.get('aggregate', {}).get('support_score', 0.0)
                # Boost validity if tools support it
                scientific_validity = min(10.0, scientific_validity + (support_score * 2.0))
                # Tool success confirms methodology
                methodological_rigor = min(10.0, methodological_rigor + 1.0)
            else:
                # Penalty if tool verification failed explicitly
                scientific_validity = max(0.0, scientific_validity - 2.0)
                methodological_rigor = max(0.0, methodological_rigor - 2.0)

        # 3. Generar issues específicos (Hybrid: LLM weaknesses + Heuristics)
        issues = self._generate_domain_specific_issues(agent_config, hypothesis, methodology, results)
        
        # Add LLM weaknesses as issues
        if llm_review and llm_review.get("weaknesses"):
            for weakness in llm_review.get("weaknesses", []):
                issues.append(ValidationIssue(
                    issue_id=f"llm_review_weakness_{hash(weakness) % 10000}",
                    severity=ValidationSeverity.MEDIUM,
                    category="peer_review_feedback",
                    description=weakness,
                    location="general",
                    suggestion="Address this weakness in the next revision."
                ))
        
        # Agregar issues de herramientas fallidas
        if tool_evidence and not tool_evidence.get('success'):
            issues.append(ValidationIssue(
                issue_id=f"tool_fail_{datetime.now().timestamp()}",
                severity=ValidationSeverity.CRITICAL,
                category="verification_failure",
                description=f"Tool verification failed: {tool_evidence.get('error', 'unknown error')}",
                location="computational_verification",
                suggestion="Review hypothesis constraints and mathematical formulation.",
                confidence=1.0
            ))
            
            # Check for specific failure types (e.g., counterexample)
            for item in tool_evidence.get('evidence_items', []):
                if not item.get('success') and 'counterexample' in str(item.get('raw_result', '')).lower():
                    issues.append(ValidationIssue(
                        issue_id=f"counterexample_{datetime.now().timestamp()}",
                        severity=ValidationSeverity.CRITICAL,
                        category="counterexample_found",
                        description="A counterexample was found during automated verification.",
                        location="hypothesis_statement",
                        suggestion="Refine hypothesis to exclude the counterexample case.",
                        confidence=1.0
                    ))

        # 4. Calcular puntuación general
        overall_score = (scientific_validity + methodological_rigor + novelty_contribution) / 3

        # 5. Generar recomendaciones
        recommendations = self._generate_recommendations(issues, overall_score)

        # 6. Determinar aprobación
        # Critical issues fail immediately
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        approved = overall_score >= 6.0 and len(critical_issues) == 0

        review_duration = (datetime.now() - start_time).total_seconds()

        return PeerReviewResult(
            experiment_id=experiment_id,
            reviewer_agent=agent_name,
            domain=agent_config["domain"],
            overall_score=round(overall_score, 2),
            scientific_validity=round(scientific_validity, 2),
            methodological_rigor=round(methodological_rigor, 2),
            novelty_contribution=round(novelty_contribution, 2),
            issues=issues,
            recommendations=recommendations,
            approved=approved,
            review_date=datetime.now(),
            review_duration=review_duration
        )

    async def _corroborate_with_tools(self, hypothesis: str, description: str, domain: str) -> Optional[Dict[str, Any]]:
        """
        Llama al ToolEvidenceOrchestrator para verificar afirmaciones.
        """
        # Solo para dominios con herramientas fuertes configuradas
        supported_domains = ["mathematics", "number_theory", "physics", "computer_science"]
        
        if domain not in supported_domains and "math" not in domain:
            return None
            
        try:
            payload = {
                "action": "corroborate",
                "hypothesis": {
                    "title": hypothesis,
                    "description": description,
                    "domain": domain,
                    "variables": {},  # Extraction could be improved
                    "assumptions": []
                }
            }
            logger.info(f"🕵️‍♀️ Invoking tool verification for {domain}...")
            result = await self.tool_orchestrator.process_request(payload)
            return result
        except Exception as e:
            logger.warning(f"Tool corroboration failed: {e}")
            return None

    async def _intelligent_llm_review(
        self,
        hypothesis: str,
        paper_content: str,
        domain: str,
        model_name: str = "minimax-m2.1:cloud"
    ) -> Dict[str, Any]:
        """
        Use LLM to perform deep analysis of the paper.
        
        This provides intelligent peer review that:
        - Actually understands mathematical proofs
        - Provides specific, actionable feedback
        - Evaluates scientific rigor beyond keyword matching
        
        Based on AI Scientist peer review patterns.
        """
        try:
            from app.services.llm_providers.ollama_provider import OllamaProvider
            
            provider = OllamaProvider()
            
            # Truncate for context window
            hypothesis_text = hypothesis[:3000] if len(hypothesis) > 3000 else hypothesis
            paper_text = paper_content[:5000] if len(paper_content) > 5000 else paper_content
            
            prompt = f"""You are a rigorous scientific peer reviewer specializing in {domain}.

TASK: Perform a detailed peer review of this research submission.

## HYPOTHESIS/CLAIM:
{hypothesis_text}

## PAPER CONTENT:
{paper_text}

## REVIEW CRITERIA (score each 1-10):

1. **Scientific/Mathematical Rigor** (rigor_score):
   - Are proofs complete and logically valid?
   - Are there gaps in reasoning?
   - Is the mathematical notation correct?

2. **Novelty & Contribution** (novelty_score):
   - Does this add new knowledge to the field?
   - Is it a trivial restatement of known results?
   - What is the significance of the contribution?

3. **Methodology** (methodology_score):
   - Is the approach sound and reproducible?
   - Are the methods appropriate for the claims?
   - Could an independent researcher replicate this?

4. **Evidence Quality** (evidence_score):
   - Are claims supported by sufficient evidence?
   - Are there unfounded assertions?
   - Is computational verification adequate?

5. **Presentation & Clarity** (clarity_score):
   - Is the paper well-structured?
   - Are definitions clear?
   - Is notation consistent?

## YOUR RESPONSE (JSON format):
```json
{{
  "rigor_score": <1-10>,
  "novelty_score": <1-10>,
  "methodology_score": <1-10>,
  "evidence_score": <1-10>,
  "clarity_score": <1-10>,
  "overall_assessment": "<accept/minor_revision/major_revision/reject>",
  "strengths": ["<specific strength 1>", "<specific strength 2>"],
  "weaknesses": ["<specific weakness with location>", "<another weakness>"],
  "actionable_feedback": ["<specific suggestion 1>", "<specific suggestion 2>"],
  "key_question": "<most important question for authors to address>"
}}
```

Provide your review:"""

            response_data = await provider.generate_async(prompt, model=model_name)
            
            if isinstance(response_data, dict):
                response_text = response_data.get("text", "")
            else:
                response_text = str(response_data)
            
            # Parse the JSON response
            import json
            import re
            
            # Try to extract JSON from response
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                review_data = json.loads(json_match.group(1))
            else:
                # Try direct JSON parsing
                try:
                    # Find JSON object in response
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        review_data = json.loads(response_text[json_start:json_end])
                    else:
                        raise ValueError("No JSON found")
                except:
                    # Fallback: return basic success
                    logger.warning("Could not parse LLM review response, using defaults")
                    return {
                        "success": True,
                        "llm_review": False,
                        "message": "LLM review parsing failed"
                    }
            
            # Calculate overall score from components
            scores = [
                review_data.get("rigor_score", 5),
                review_data.get("novelty_score", 5),
                review_data.get("methodology_score", 5),
                review_data.get("evidence_score", 5),
                review_data.get("clarity_score", 5)
            ]
            overall_score = sum(scores) / len(scores)
            
            logger.info(f"🧠 LLM Peer Review: Score {overall_score:.1f}/10")
            
            return {
                "success": True,
                "llm_review": True,
                "overall_score": overall_score,
                "rigor_score": review_data.get("rigor_score", 5),
                "novelty_score": review_data.get("novelty_score", 5),
                "methodology_score": review_data.get("methodology_score", 5),
                "evidence_score": review_data.get("evidence_score", 5),
                "clarity_score": review_data.get("clarity_score", 5),
                "assessment": review_data.get("overall_assessment", "minor_revision"),
                "strengths": review_data.get("strengths", []),
                "weaknesses": review_data.get("weaknesses", []),
                "actionable_feedback": review_data.get("actionable_feedback", []),
                "key_question": review_data.get("key_question", "")
            }
            
        except Exception as e:
            logger.warning(f"LLM peer review failed: {e}")
            return {
                "success": False,
                "llm_review": False,
                "error": str(e)
            }

    def _assess_scientific_validity(self, hypothesis: str, methodology: str, results: Dict[str, Any]) -> float:
        """Evaluar validez científica (0-10)"""
        score = 5.0  # Puntaje base

        # Hipótesis clara y testable
        if self._is_hypothesis_testable(hypothesis):
            score += 2.0

        # Metodología sólida
        if len(methodology) > 100 and "control" in methodology.lower():
            score += 1.5

        # Resultados con análisis
        if results and ("statistics" in str(results).lower() or "analysis" in str(results).lower()):
            score += 1.5

        return min(10.0, max(0.0, score))

    def _assess_methodological_rigor(self, methodology: str) -> float:
        """Evaluar rigor metodológico (0-10)"""
        score = 5.0

        # Longitud y detalle
        if len(methodology) > 200:
            score += 1.0

        # Controles mencionados
        if "control" in methodology.lower():
            score += 1.5

        # Replicabilidad
        replicability_terms = ["repeat", "replicate", "sample size", "n=", "trials"]
        if any(term in methodology.lower() for term in replicability_terms):
            score += 1.5

        # Variables controladas
        if "variable" in methodology.lower() or "independent" in methodology.lower():
            score += 1.0

        return min(10.0, max(0.0, score))

    def _assess_novelty_contribution(self, hypothesis: str, results: Dict[str, Any]) -> float:
        """Evaluar contribución novedosa (0-10)"""
        score = 5.0

        # Hipótesis novedosa
        if len(hypothesis) > 50 and any(word in hypothesis.lower() for word in ["novel", "new", "innovative", "unique"]):
            score += 2.0

        # Resultados significativos
        if results and len(str(results)) > 100:
            score += 1.0

        # Implicaciones prácticas
        if "application" in str(results).lower() or "impact" in str(results).lower():
            score += 1.0

        return min(10.0, max(0.0, score))

    def _generate_domain_specific_issues(self, agent_config: Dict[str, Any],
                                       hypothesis: str, methodology: str,
                                       results: Dict[str, Any]) -> List[ValidationIssue]:
        """Generar issues específicos del dominio"""
        issues = []
        domain = agent_config["domain"]
        # expertise = agent_config["expertise"]  # No longer used

        # Issues específicos por dominio
        if domain == ScientificDomain.MATHEMATICS:
            issues.extend(self._check_mathematical_issues(hypothesis, methodology, results))
        elif domain == ScientificDomain.PHYSICS:
            issues.extend(self._check_physics_issues(hypothesis, methodology, results))
        elif domain == ScientificDomain.CHEMISTRY:
            issues.extend(self._check_chemistry_issues(hypothesis, methodology, results))
        elif domain == ScientificDomain.BIOLOGY:
            issues.extend(self._check_biology_issues(hypothesis, methodology, results))
        elif domain == ScientificDomain.COMPUTER_SCIENCE:
            issues.extend(self._check_cs_issues(hypothesis, methodology, results))

        return issues

    def _check_mathematical_issues(self, hypothesis: str, methodology: str, results: Dict[str, Any]) -> List[ValidationIssue]:
        """Verificar issues específicos de matemáticas"""
        issues = []
        
        # Combine hypothesis and methodology for fuller analysis
        full_content = f"{hypothesis} {methodology}".lower()

        # Verificar consistencia lógica - now includes Spanish, LaTeX, and common terms
        math_framework_terms = [
            # English
            "theorem", "proof", "conjecture", "lemma", "corollary", "proposition",
            "definition", "axiom", "formula", "equation", "hypothesis",
            # Spanish
            "teorema", "demostración", "prueba", "conjetura", "lema", "corolario",
            "proposición", "definición", "axioma", "fórmula", "ecuación", "hipótesis",
            # LaTeX common
            "\\text{", "\\forall", "\\exists", "\\implies", "\\iff", "\\in", "\\mathbb",
            # Mathematical symbols that suggest formal content
            "∀", "∃", "⟹", "⟺", "∈", "⊂", "≤", "≥", "χ(", "δ(", "Δ(",
        ]
        if not any(term in full_content for term in math_framework_terms):
            issues.append(ValidationIssue(
                issue_id="missing_mathematical_framework",
                severity=ValidationSeverity.MEDIUM,
                category="mathematical_rigor",
                description="Mathematical framework or proof structure not clearly defined",
                location="hypothesis",
                suggestion="Specify mathematical framework, theorems, or proof techniques"
            ))

        # Verificar notación matemática - check both hypothesis and methodology
        math_notation = [
            # Unicode symbols
            "∑", "∫", "∂", "∇", "∈", "∀", "∃", "≤", "≥", "⊂", "⊆", "→", "⟹",
            # LaTeX commands
            "\\int", "\\sum", "\\forall", "\\exists", "\\leq", "\\geq", "\\subset",
            "\\chi", "\\Delta", "\\delta", "\\phi", "\\psi", "\\omega",
            # Dollar signs for LaTeX math
            "$$", "$\\",
            # Common math expressions
            ":=", "=>", "<=",
        ]
        if not any(symbol in full_content for symbol in math_notation):
            issues.append(ValidationIssue(
                issue_id="missing_mathematical_notation",
                severity=ValidationSeverity.LOW,
                category="presentation",
                description="Limited use of mathematical notation or formalism",
                location="methodology",
                suggestion="Use appropriate mathematical notation for clarity"
            ))

        return issues

    def _check_physics_issues(self, hypothesis: str, methodology: str, results: Dict[str, Any]) -> List[ValidationIssue]:
        """Verificar issues específicos de física"""
        issues = []

        # Verificar leyes físicas
        physics_laws = ["newton", "einstein", "maxwell", "thermodynamics", "quantum"]
        if not any(law in hypothesis.lower() for law in physics_laws):
            issues.append(ValidationIssue(
                issue_id="missing_physical_laws",
                severity=ValidationSeverity.MEDIUM,
                category="physical_principles",
                description="Physical laws or principles not clearly referenced",
                location="hypothesis",
                suggestion="Reference relevant physical laws or principles"
            ))

        # Verificar unidades y mediciones
        if not any(unit in methodology.lower() for unit in ["meter", "second", "kg", "newton", "joule"]):
            issues.append(ValidationIssue(
                issue_id="missing_units",
                severity=ValidationSeverity.LOW,
                category="measurements",
                description="Physical units not specified in methodology",
                location="methodology",
                suggestion="Specify appropriate physical units for measurements"
            ))

        return issues

    def _check_chemistry_issues(self, hypothesis: str, methodology: str, results: Dict[str, Any]) -> List[ValidationIssue]:
        """Verificar issues específicos de química"""
        issues = []

        # Verificar fórmulas químicas
        if not re.search(r'[A-Z][a-z]?\d*', hypothesis):
            issues.append(ValidationIssue(
                issue_id="missing_chemical_formulas",
                severity=ValidationSeverity.LOW,
                category="chemical_notation",
                description="Chemical formulas or compounds not clearly specified",
                location="hypothesis",
                suggestion="Use proper chemical notation for compounds and reactions"
            ))

        # Verificar seguridad
        if not any(term in methodology.lower() for term in ["safety", "hazard", "precaution", "protective"]):
            issues.append(ValidationIssue(
                issue_id="missing_safety_protocols",
                severity=ValidationSeverity.MEDIUM,
                category="safety",
                description="Safety protocols not mentioned in experimental procedure",
                location="methodology",
                suggestion="Include safety precautions and hazard assessments"
            ))

        return issues

    def _check_biology_issues(self, hypothesis: str, methodology: str, results: Dict[str, Any]) -> List[ValidationIssue]:
        """Verificar issues específicos de biología"""
        issues = []

        # Verificar controles biológicos
        if not any(term in methodology.lower() for term in ["control", "wild-type", "reference", "baseline"]):
            issues.append(ValidationIssue(
                issue_id="missing_biological_controls",
                severity=ValidationSeverity.HIGH,
                category="experimental_design",
                description="Appropriate biological controls not specified",
                location="methodology",
                suggestion="Include proper biological controls (wild-type, reference strains, etc.)"
            ))

        # Verificar consideraciones éticas
        if not any(term in methodology.lower() for term in ["ethics", "animal", "human", "consent", "welfare"]):
            issues.append(ValidationIssue(
                issue_id="missing_ethical_considerations",
                severity=ValidationSeverity.MEDIUM,
                category="ethics",
                description="Ethical considerations for biological research not addressed",
                location="methodology",
                suggestion="Address ethical considerations for biological experiments"
            ))

        return issues

    def _check_cs_issues(self, hypothesis: str, methodology: str, results: Dict[str, Any]) -> List[ValidationIssue]:
        """Verificar issues específicos de ciencias de la computación"""
        issues = []

        # Verificar algoritmos
        if not any(term in methodology.lower() for term in ["algorithm", "code", "implementation", "software"]):
            issues.append(ValidationIssue(
                issue_id="missing_algorithm_specification",
                severity=ValidationSeverity.MEDIUM,
                category="computational_method",
                description="Algorithm or computational method not clearly specified",
                location="methodology",
                suggestion="Specify algorithms, data structures, and computational methods"
            ))

        # Verificar reproducibilidad
        if not any(term in methodology.lower() for term in ["reproducible", "code", "repository", "open-source"]):
            issues.append(ValidationIssue(
                issue_id="missing_reproducibility",
                severity=ValidationSeverity.MEDIUM,
                category="reproducibility",
                description="Computational reproducibility not addressed",
                location="methodology",
                suggestion="Provide code, data, and instructions for reproducibility"
            ))

        return issues

    def _generate_recommendations(self, issues: List[ValidationIssue], overall_score: float) -> List[str]:
        """Generar recomendaciones basadas en los issues encontrados"""
        recommendations = []

        # Recomendaciones por severidad
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        high_issues = [i for i in issues if i.severity == ValidationSeverity.HIGH]

        if critical_issues:
            recommendations.append("Address critical issues before proceeding with publication")
            for issue in critical_issues[:3]:  # Top 3 critical issues
                recommendations.append(f"CRITICAL: {issue.suggestion}")

        if high_issues:
            recommendations.append("Consider major revisions to address high-priority issues")
            for issue in high_issues[:2]:  # Top 2 high issues
                recommendations.append(f"HIGH: {issue.suggestion}")

        # Recomendaciones generales por puntuación
        if overall_score < 5.0:
            recommendations.append("Significant methodological improvements needed")
            recommendations.append("Consider consulting domain experts for guidance")
        elif overall_score < 7.0:
            recommendations.append("Minor revisions recommended for publication readiness")
        else:
            recommendations.append("Well-executed research with strong scientific foundation")

        return recommendations

    def _calculate_overall_score(self, peer_reviews: List[PeerReviewResult]) -> float:
        """Calcular puntuación general de múltiples revisiones"""
        if not peer_reviews:
            return 0.0

        # Promedio ponderado de las revisiones
        total_score = sum(review.overall_score for review in peer_reviews)
        return round(total_score / len(peer_reviews), 2)

    def _consolidate_recommendations(self, peer_reviews: List[PeerReviewResult]) -> List[str]:
        """Consolidar recomendaciones de múltiples revisiones"""
        all_recommendations = []
        for review in peer_reviews:
            all_recommendations.extend(review.recommendations)

        # Eliminar duplicados y mantener las más importantes
        unique_recommendations = list(set(all_recommendations))

        # Priorizar por palabras clave
        priority_keywords = ["critical", "significant", "major", "address", "revision"]
        prioritized = []
        others = []

        for rec in unique_recommendations:
            if any(keyword in rec.lower() for keyword in priority_keywords):
                prioritized.append(rec)
            else:
                others.append(rec)

        return prioritized + others

    # ========================================
    # SISTEMA DE COPILOT CIENTÍFICO
    # ========================================

    async def scientific_copilot_guidance(self, request_data: ScientificCopilotGuidanceResult) -> ScientificCopilotGuidanceResult:
        """
        Sistema de Copilot Científico para guiar a nuevos científicos

        Proporciona:
        - Guía paso a paso para principiantes
        - Desarrollo de hipótesis científicas
        - Diseño experimental asistido
        - Validación en tiempo real
        """
        user_level = request_data.get("user_level", "beginner")  # beginner, intermediate, advanced
        research_topic = request_data.get("research_topic", "")
        current_phase = request_data.get("current_phase", "exploration")
        user_query = request_data.get("query", "")

        # Usar el agente guía general para proporcionar asistencia
        guidance = await self._generate_scientific_guidance(
            user_level, research_topic, current_phase, user_query
        )

        return {
            "success": True,
            "user_level": user_level,
            "research_topic": research_topic,
            "current_phase": current_phase,
            "guidance": guidance,
            "next_steps": self._suggest_next_steps(current_phase, user_level),
            "learning_resources": self._recommend_learning_resources(user_level, research_topic)
        }

    async def _generate_scientific_guidance(self, user_level: str, research_topic: str,
                                          current_phase: str, user_query: str) -> Dict[str, Any]:
        """
        Generar guía científica personalizada usando el agente guía general
        """
        # guide_agent = self.reviewer_agents["scientific_guide_agent"]  # No longer used

        guidance = {
            "phase_guidance": "",
            "methodological_advice": [],
            "hypothesis_suggestions": [],
            "experimental_design_tips": [],
            "validation_checkpoints": [],
            "learning_objectives": [],
            "potential_pitfalls": []
        }

        # Adaptar guía según nivel del usuario y fase
        if user_level == "beginner":
            guidance["phase_guidance"] = self._beginner_phase_guidance(current_phase)
            guidance["methodological_advice"] = self._beginner_methodology_advice(research_topic)
            guidance["learning_objectives"] = self._beginner_learning_objectives(current_phase)
        elif user_level == "intermediate":
            guidance["phase_guidance"] = self._intermediate_phase_guidance(current_phase)
            guidance["methodological_advice"] = self._intermediate_methodology_advice(research_topic)
        else:  # advanced
            guidance["phase_guidance"] = self._advanced_phase_guidance(current_phase)
            guidance["methodological_advice"] = self._advanced_methodology_advice(research_topic)

        # Generar sugerencias de hipótesis si es relevante
        if current_phase in ["hypothesis_generation", "exploration"]:
            guidance["hypothesis_suggestions"] = self._generate_hypothesis_suggestions(research_topic, user_level)

        # Consejos de diseño experimental
        if current_phase in ["experimental_design", "methodology"]:
            guidance["experimental_design_tips"] = self._experimental_design_tips(research_topic, user_level)

        # Puntos de validación
        guidance["validation_checkpoints"] = self._validation_checkpoints(current_phase, user_level)

        # Posibles errores comunes
        guidance["potential_pitfalls"] = self._identify_potential_pitfalls(current_phase, research_topic)

        return guidance

    def _beginner_phase_guidance(self, phase: str) -> str:
        """Guía de fase para principiantes"""
        guidance_map = {
            "exploration": "¡Excelente! Estás en la fase de exploración. Esta es la fase más importante donde aprendes sobre tu tema de interés. Lee artículos científicos, libros, y habla con expertos. No te preocupes por ser perfecto aún - el objetivo es construir una base sólida de conocimiento.",
            "hypothesis_generation": "Ahora vamos a formular hipótesis. Una hipótesis es una predicción testable sobre cómo funciona algo. Recuerda: debe ser específica, measurable, y falsable. No tengas miedo de equivocarte - las hipótesis se refinan con el tiempo.",
            "experimental_design": "En esta fase diseñamos el experimento. Piensa en: ¿Qué voy a medir? ¿Cómo lo voy a medir? ¿Qué variables controlaré? ¿Cuántas repeticiones necesito? Esta es la fase más crítica para obtener resultados confiables.",
            "data_collection": "¡Manos a la obra! Recuerda mantener registros detallados de todo lo que haces. Usa cuadernos de laboratorio, toma fotos, anota observaciones. La reproducibilidad depende de tu documentación.",
            "analysis": "Ahora analizamos los datos. ¿Qué patrones ves? ¿Los resultados apoyan tu hipótesis? Usa estadística básica y gráficos claros. Recuerda: los datos no mienten, pero sí pueden ser malinterpretados.",
            "interpretation": "La fase final: ¿Qué significan tus resultados? ¿Contribuyen al conocimiento científico? ¿Qué preguntas nuevas surgen? Esta es donde conectas tu trabajo con el conocimiento existente."
        }
        return guidance_map.get(phase, "Cada fase del método científico es importante. Concéntrate en aprender y documentar todo cuidadosamente.")

    def _beginner_methodology_advice(self, research_topic: str) -> List[str]:
        """Consejos metodológicos para principiantes"""
        return [
            "Empieza con preguntas simples: ¿Qué? ¿Cómo? ¿Por qué?",
            "Lee al menos 5-10 artículos científicos sobre tu tema antes de empezar",
            "Practica el diseño experimental con ejercicios simples antes de tu experimento real",
            "Mantén un diario científico donde registres todas tus ideas y observaciones",
            "No tengas miedo de pedir ayuda a mentores o colegas más experimentados",
            "Recuerda: la ciencia es un proceso iterativo - los errores son oportunidades de aprendizaje",
            "Documenta todo: métodos, resultados, y pensamientos - aunque parezcan obvios",
            "Empieza pequeño: diseña experimentos que puedas completar en tiempo razonable"
        ]

    def _beginner_learning_objectives(self, phase: str) -> List[str]:
        """Objetivos de aprendizaje para principiantes"""
        objectives_map = {
            "exploration": [
                "Comprender los conceptos básicos del tema de investigación",
                "Identificar preguntas científicas relevantes",
                "Aprender a leer y entender artículos científicos",
                "Desarrollar vocabulario técnico del campo"
            ],
            "hypothesis_generation": [
                "Formular hipótesis claras y testables",
                "Entender la diferencia entre hipótesis y predicciones",
                "Aprender a justificar hipótesis con evidencia preliminar",
                "Practicar el pensamiento crítico y lógico"
            ],
            "experimental_design": [
                "Entender los componentes de un buen diseño experimental",
                "Aprender sobre variables independientes y dependientes",
                "Comprender la importancia de controles y réplicas",
                "Desarrollar habilidades de planificación y organización"
            ]
        }
        return objectives_map.get(phase, ["Aprender los fundamentos del método científico", "Desarrollar habilidades de observación y documentación"])

    def _intermediate_phase_guidance(self, phase: str) -> str:
        """Guía de fase para nivel intermedio"""
        guidance_map = {
            "exploration": "Como investigador intermedio, enfócate en identificar gaps en la literatura. Busca preguntas no respondidas o metodologías mejorables. Considera enfoques interdisciplinarios.",
            "hypothesis_generation": "Formula hipótesis más sofisticadas. Considera hipótesis alternativas, efectos moderadores, y mecanismos subyacentes. Usa teoría existente para fundamentar tus predicciones.",
            "experimental_design": "Optimiza tu diseño para máxima eficiencia estadística. Considera power analysis, tamaños de efecto esperados, y estrategias para minimizar sesgos. Incluye medidas de validación.",
            "data_collection": "Implementa protocolos estandarizados. Monitorea calidad de datos en tiempo real. Prepárate para troubleshooting y ajustes adaptativos del protocolo.",
            "analysis": "Aplica análisis estadísticos apropiados. Considera análisis de sensibilidad, validación cruzada, y exploración de subgrupos. Evalúa robustness de los resultados.",
            "interpretation": "Integra resultados con teoría existente. Considera implicaciones prácticas y teóricas. Identifica limitaciones y direcciones futuras de investigación."
        }
        return guidance_map.get(phase, "Aprovecha tu experiencia para refinar y optimizar cada fase del proceso científico.")

    def _intermediate_methodology_advice(self, research_topic: str) -> List[str]:
        """Consejos metodológicos para nivel intermedio"""
        return [
            "Realiza revisión sistemática de literatura antes de diseñar experimentos",
            "Considera diseños experimentales más sofisticados (factorial, longitudinal)",
            "Implementa medidas de calidad y control de sesgos",
            "Desarrolla protocolos detallados con criterios de inclusión/exclusión",
            "Incluye análisis de poder estadístico en la planificación",
            "Considera replicabilidad y generalizabilidad desde el inicio",
            "Documenta decisiones metodológicas y justificaciones",
            "Pre-registra hipótesis y análisis planeados cuando sea posible"
        ]

    def _advanced_phase_guidance(self, phase: str) -> str:
        """Guía de fase para nivel avanzado"""
        guidance_map = {
            "exploration": "Como experto, identifica oportunidades para avances paradigmáticos. Busca integraciones teóricas novedosas y aplicaciones de frontera tecnológica.",
            "hypothesis_generation": "Desarrolla hipótesis que desafíen paradigmas existentes. Considera mecanismos causales complejos y efectos emergentes.",
            "experimental_design": "Diseña experimentos que prueben mecanismos subyacentes. Incluye validación múltiple, réplicas independientes, y análisis de robustness extremos.",
            "data_collection": "Implementa monitoreo continuo de calidad y adaptaciones en tiempo real. Considera meta-análisis integrados y validación cruzada múltiple.",
            "analysis": "Aplica técnicas analíticas de vanguardia. Evalúa validez causal, efectos moderadores, y generalizabilidad. Considera análisis de sensibilidad comprehensivos.",
            "interpretation": "Integra resultados en marcos teóricos más amplios. Evalúa impacto potencial en el campo y aplicaciones transformadoras."
        }
        return guidance_map.get(phase, "Como investigador avanzado, enfócate en contribuciones transformadoras y avances metodológicos.")

    def _advanced_methodology_advice(self, research_topic: str) -> List[str]:
        """Consejos metodológicos para nivel avanzado"""
        return [
            "Desarrolla nuevas metodologías o adapta técnicas de vanguardia",
            "Implementa diseños experimentales innovadores para preguntas complejas",
            "Integra múltiples métodos de validación (triangulación)",
            "Considera escalabilidad y aplicabilidad a problemas del mundo real",
            "Desarrolla marcos teóricos integradores",
            "Evalúa impacto potencial y significancia científica",
            "Prepara estrategias de diseminación y traducción de conocimiento",
            "Considera colaboraciones interdisciplinarias estratégicas"
        ]

    def _generate_hypothesis_suggestions(self, research_topic: str, user_level: str) -> List[str]:
        """Generar sugerencias de hipótesis basadas en el tema"""
        if not research_topic:
            return ["Explora un tema específico para recibir sugerencias de hipótesis personalizadas"]

        suggestions = []

        # Sugerencias genéricas basadas en nivel
        if user_level == "beginner":
            suggestions = [
                f"¿Cómo afecta [variable independiente] a [variable dependiente] en {research_topic}?",
                f"¿Existen diferencias significativas entre [grupo A] y [grupo B] en {research_topic}?",
                f"¿Cuál es la relación entre [factor X] y [resultado Y] en {research_topic}?",
                f"¿Cómo cambia [propiedad] con [condición] en {research_topic}?"
            ]
        elif user_level == "intermediate":
            suggestions = [
                f"¿Cómo interactúan [variable A] y [variable B] para influir en [resultado] en {research_topic}?",
                f"¿Bajo qué condiciones se maximiza [efecto deseado] en {research_topic}?",
                f"¿Cómo se compara [método nuevo] vs [método estándar] en {research_topic}?",
                f"¿Qué factores moderan la relación entre [X] y [Y] en {research_topic}?"
            ]
        else:  # advanced
            suggestions = [
                f"¿Cómo se puede integrar [teoría A] con [teoría B] para explicar [fenómeno] en {research_topic}?",
                f"¿Qué mecanismos causales subyacentes explican [patrón observado] en {research_topic}?",
                f"¿Cómo evolucionan [procesos] a través de [escalas temporales/espaciales] en {research_topic}?",
                f"¿Qué principios fundamentales se pueden derivar de [observaciones] en {research_topic}?"
            ]

        return suggestions

    def _experimental_design_tips(self, research_topic: str, user_level: str) -> List[str]:
        """Consejos para diseño experimental"""
        tips = []

        if user_level == "beginner":
            tips = [
                "Identifica claramente variables independientes y dependientes",
                "Incluye al menos 3 réplicas por condición experimental",
                "Define controles apropiados (positivo, negativo, placebo)",
                "Mide variables de confusión potenciales",
                "Documenta todos los pasos del protocolo experimental",
                "Considera el tamaño de muestra necesario para detectar efectos",
                "Planifica análisis estadísticos antes de recoger datos",
                "Incluye medidas de calidad y reproducibilidad"
            ]
        elif user_level == "intermediate":
            tips = [
                "Implementa diseños factoriales para estudiar interacciones",
                "Considera efectos de orden y aprendizaje en diseños longitudinales",
                "Incluye medidas de validación y calibración",
                "Planifica análisis de poder estadístico",
                "Considera blinding y randomization apropiados",
                "Desarrolla criterios claros de inclusión/exclusión",
                "Incluye medidas de adherencia al protocolo",
                "Planifica estrategias de manejo de datos faltantes"
            ]
        else:  # advanced
            tips = [
                "Desarrolla diseños adaptativos basados en resultados preliminares",
                "Implementa validación cruzada múltiple",
                "Considera diseños que prueben mecanismos causales",
                "Incluye medidas de robustness bajo condiciones extremas",
                "Desarrolla protocolos para meta-análisis integrados",
                "Considera escalabilidad y eficiencia computacional",
                "Implementa monitoreo continuo de calidad de datos",
                "Desarrolla estrategias para minimizar sesgos cognitivos"
            ]

        return tips

    def _validation_checkpoints(self, current_phase: str, user_level: str) -> List[str]:
        """Puntos de validación para cada fase"""
        checkpoints = {
            "exploration": [
                "He revisado al menos 10 artículos científicos relevantes",
                "Puedo explicar los conceptos básicos a un colega",
                "He identificado al menos 3 preguntas científicas no respondidas",
                "Entiendo las metodologías comunes en este campo"
            ],
            "hypothesis_generation": [
                "La hipótesis es clara y específica",
                "La hipótesis es testable con métodos disponibles",
                "He considerado hipótesis alternativas",
                "La hipótesis está fundamentada en evidencia preliminar"
            ],
            "experimental_design": [
                "He definido claramente variables y controles",
                "El diseño permite detectar el efecto esperado",
                "He considerado fuentes potenciales de sesgo",
                "El protocolo es reproducible por otros investigadores"
            ],
            "data_collection": [
                "Los datos se están registrando sistemáticamente",
                "Estoy monitoreando calidad de datos en tiempo real",
                "Los controles están funcionando como esperado",
                "Puedo identificar y corregir problemas rápidamente"
            ],
            "analysis": [
                "Estoy usando métodos estadísticos apropiados",
                "He verificado supuestos de los análisis",
                "Estoy considerando análisis de sensibilidad",
                "Los resultados son robustos a diferentes métodos"
            ],
            "interpretation": [
                "Los resultados apoyan o rechazan la hipótesis",
                "He considerado explicaciones alternativas",
                "Los hallazgos contribuyen al conocimiento existente",
                "He identificado limitaciones y direcciones futuras"
            ]
        }

        return checkpoints.get(current_phase, ["Validar que cada paso sigue el método científico", "Documentar decisiones y justificaciones"])

    def _identify_potential_pitfalls(self, current_phase: str, research_topic: str) -> List[str]:
        """Identificar posibles errores comunes en cada fase"""
        pitfalls = {
            "exploration": [
                "Sesgo de confirmación: solo buscar evidencia que apoye ideas preconcebidas",
                "Profundidad insuficiente: no entender conceptos fundamentales",
                "Sesgo de disponibilidad: basar conclusiones en información fácilmente accesible",
                "Ignorar literatura contradictoria"
            ],
            "hypothesis_generation": [
                "Hipótesis demasiado vagas o no testables",
                "Hipótesis basadas en anécdotas en lugar de evidencia",
                "Ignorar hipótesis alternativas viables",
                "Hipótesis que no contribuyen significativamente al conocimiento"
            ],
            "experimental_design": [
                "Controles inadecuados o faltantes",
                "Tamaño de muestra insuficiente",
                "Medición inexacta de variables",
                "No considerar variables confusoras"
            ],
            "data_collection": [
                "Errores sistemáticos en la medición",
                "Pérdida de datos sin documentación",
                "Cambios no documentados en el protocolo",
                "Sesgos en la observación o registro"
            ],
            "analysis": [
                "Uso de pruebas estadísticas incorrectas",
                "No verificar supuestos de los análisis",
                "p-hacking o manipulación de resultados",
                "Ignorar valores atípicos sin justificación"
            ],
            "interpretation": [
                "Sobreinterpretación de resultados",
                "Ignorar limitaciones del estudio",
                "Conclusiones no apoyadas por los datos",
                "No considerar implicaciones prácticas"
            ]
        }

        return pitfalls.get(current_phase, ["Documentar todas las decisiones", "Buscar feedback de colegas", "Mantener escepticismo científico"])

    def _suggest_next_steps(self, current_phase: str, user_level: str) -> List[str]:
        """Sugerir próximos pasos en el proceso científico"""
        next_steps_map = {
            "exploration": [
                "Revisar literatura específica sobre tu pregunta de investigación",
                "Identificar expertos en el campo para consulta",
                "Desarrollar hipótesis preliminares",
                "Explorar metodologías disponibles"
            ],
            "hypothesis_generation": [
                "Refinar hipótesis basadas en literatura",
                "Desarrollar predicciones específicas",
                "Diseñar experimento preliminar",
                "Buscar colaboración si es necesario"
            ],
            "experimental_design": [
                "Desarrollar protocolo detallado",
                "Obtener materiales y equipos necesarios",
                "Entrenar en procedimientos experimentales",
                "Realizar prueba piloto del experimento"
            ],
            "data_collection": [
                "Implementar sistema de registro de datos",
                "Establecer rutina de monitoreo de calidad",
                "Preparar planes de contingencia",
                "Documentar cualquier desviación del protocolo"
            ],
            "analysis": [
                "Organizar y limpiar datos",
                "Seleccionar métodos analíticos apropiados",
                "Realizar análisis exploratorios",
                "Validar resultados con diferentes métodos"
            ],
            "interpretation": [
                "Comparar resultados con literatura existente",
                "Desarrollar explicaciones teóricas",
                "Identificar implicaciones prácticas",
                "Planificar estudios futuros"
            ]
        }

        return next_steps_map.get(current_phase, ["Continuar con la siguiente fase del método científico", "Documentar progreso y decisiones"])

    def _recommend_learning_resources(self, user_level: str, research_topic: str) -> List[Dict[str, str]]:
        """Recomendar recursos de aprendizaje"""
        resources = []

        if user_level == "beginner":
            resources = [
                {
                    "title": "El Método Científico: Una Guía Práctica",
                    "type": "book",
                    "description": "Introducción clara al proceso científico",
                    "level": "beginner"
                },
                {
                    "title": "Cómo Leer un Artículo Científico",
                    "type": "online_course",
                    "description": "Habilidades básicas para leer literatura científica",
                    "level": "beginner"
                },
                {
                    "title": "Estadística Básica para Investigadores",
                    "type": "tutorial",
                    "description": "Conceptos fundamentales de estadística",
                    "level": "beginner"
                }
            ]
        elif user_level == "intermediate":
            resources = [
                {
                    "title": "Diseño Experimental en Ciencias",
                    "type": "book",
                    "description": "Técnicas avanzadas de diseño experimental",
                    "level": "intermediate"
                },
                {
                    "title": "Análisis Estadístico con R/Python",
                    "type": "online_course",
                    "description": "Herramientas computacionales para análisis de datos",
                    "level": "intermediate"
                },
                {
                    "title": "Escritura Científica Efectiva",
                    "type": "workshop",
                    "description": "Cómo comunicar resultados científicos",
                    "level": "intermediate"
                }
            ]
        else:  # advanced
            resources = [
                {
                    "title": "Metodología de Investigación Avanzada",
                    "type": "book",
                    "description": "Técnicas de vanguardia en investigación",
                    "level": "advanced"
                },
                {
                    "title": "Publicación en Revistas de Alto Impacto",
                    "type": "seminar",
                    "description": "Estrategias para publicación científica",
                    "level": "advanced"
                },
                {
                    "title": "Liderazgo en Investigación Científica",
                    "type": "mentorship",
                    "description": "Desarrollo de carrera en investigación",
                    "level": "advanced"
                }
            ]

        return resources

    # ========================================
    # INTEGRACIÓN CON SERVICIOS EXISTENTES
    # ========================================

    async def integrate_with_existing_services(self) -> IntegrateWithExistingServicesResult:
        """
        Integrar el sistema de peer review con servicios científicos existentes de AXIOM

        Esta función establece conexiones automáticas con:
        - Servicios de computación científica
        - Servicios de machine learning
        - Servicios de análisis de datos
        - Servicios de visualización
        """
        integration_status = {
            "services_connected": [],
            "services_failed": [],
            "validation_hooks": [],
            "automated_workflows": []
        }

        # Lista de servicios científicos disponibles en AXIOM
        axiom_services = [
            "ComputationalChemistry",
            "MolecularDynamics",
            "ScientificAI",
            "DataVersioning",
            "ExperimentTracking",
            "Reproducibility",
            "BiomedicalNLP",
            "GNOMEMaterials",
            "DNABERT2",
            "Protgpt2"
        ]

        for service_name in axiom_services:
            try:
                # Intentar conectar con el servicio
                connection_result = await self._connect_to_service(service_name)
                if connection_result["success"]:
                    integration_status["services_connected"].append(service_name)

                    # Establecer hooks de validación automática
                    validation_hook = await self._setup_validation_hook(service_name)
                    integration_status["validation_hooks"].append(validation_hook)

                    # Configurar flujos de trabajo automatizados
                    workflow = await self._setup_automated_workflow(service_name)
                    integration_status["automated_workflows"].append(workflow)

                else:
                    integration_status["services_failed"].append({
                        "service": service_name,
                        "error": connection_result.get("error", "Unknown error")
                    })

            except BiologyError as e:
                integration_status["services_failed"].append({
                    "service": service_name,
                    "error": str(e)
                })

        return {
            "success": True,
            "integration_summary": {
                "total_services": len(axiom_services),
                "connected": len(integration_status["services_connected"]),
                "failed": len(integration_status["services_failed"]),
                "validation_hooks_established": len(integration_status["validation_hooks"]),
                "automated_workflows_created": len(integration_status["automated_workflows"])
            },
            "details": integration_status
        }

    async def _connect_to_service(self, service_name: str) -> ConnectToServiceResult:
        """
        Conectar con un servicio específico de AXIOM
        """
        try:
            # Importar dinámicamente el servicio
            module_path = f"app.services.{service_name.lower()}"
            service_module = __import__(module_path, fromlist=[service_name])

            # Obtener la clase del servicio
            service_class = getattr(service_module, service_name)

            # Instanciar el servicio
            service_instance = service_class()

            # Verificar que el servicio esté operativo
            if hasattr(service_instance, 'process_request'):
                # El servicio está disponible
                return {
                    "success": True,
                    "service_instance": service_instance,
                    "capabilities": self._get_service_capabilities(service_instance)
                }
            else:
                return {
                    "success": False,
                    "error": f"Service {service_name} does not have process_request method"
                }

        except ImportError:
            return {
                "success": False,
                "error": f"Could not import service {service_name}"
            }
        except BiologyError as e:
            return {
                "success": False,
                "error": f"Error connecting to service {service_name}: {str(e)}"
            }

    def _get_service_capabilities(self, service_instance) -> List[str]:
        """Obtener capacidades de un servicio"""
        capabilities = []

        # Verificar métodos disponibles
        available_methods = dir(service_instance)

        if 'validate_experiment' in available_methods:
            capabilities.append("experiment_validation")
        if 'analyze_data' in available_methods:
            capabilities.append("data_analysis")
        if 'generate_hypothesis' in available_methods:
            capabilities.append("hypothesis_generation")
        if 'simulate' in available_methods:
            capabilities.append("simulation")
        if 'optimize' in available_methods:
            capabilities.append("optimization")
        if 'predict' in available_methods:
            capabilities.append("prediction")

        return capabilities

    async def _setup_validation_hook(self, service_name: str) -> SetupValidationHookResult:
        """
        Establecer hook de validación automática para un servicio
        """
        return {
            "service": service_name,
            "hook_type": "pre_execution_validation",
            "validation_rules": [
                "scientific_method_compliance",
                "ethical_considerations",
                "resource_requirements",
                "reproducibility_checks"
            ],
            "trigger_events": [
                "experiment_start",
                "data_collection_begin",
                "analysis_start",
                "results_generation"
            ]
        }

    async def _setup_automated_workflow(self, service_name: str) -> SetupAutomatedWorkflowResult:
        """
        Configurar flujo de trabajo automatizado con validación integrada
        """
        return {
            "service": service_name,
            "workflow_type": "scientific_pipeline",
            "steps": [
                "hypothesis_validation",
                "methodology_review",
                "execution_with_monitoring",
                "results_validation",
                "peer_review_preparation"
            ],
            "integration_points": [
                "real_time_validation",
                "automated_peer_review",
                "quality_assurance_checks",
                "documentation_generation"
            ]
        }

    # ========================================
    # VALIDACIÓN EN TIEMPO REAL
    # ========================================

    async def real_time_validation(self, request_data: RealTimeValidationResult) -> RealTimeValidationResult:
        """
        Validación en tiempo real durante la ejecución de experimentos

        Proporciona feedback inmediato sobre:
        - Cumplimiento del protocolo experimental
        - Calidad de datos en tiempo real
        - Detección de anomalías
        - Sugerencias de ajuste
        """
        experiment_id = request_data.get("experiment_id", "")
        current_data = request_data.get("current_data", {})
        execution_phase = request_data.get("phase", "data_collection")

        # Análisis en tiempo real
        real_time_analysis = await self._analyze_real_time_data(
            experiment_id, current_data, execution_phase
        )

        # Generar feedback inmediato
        immediate_feedback = self._generate_immediate_feedback(
            real_time_analysis, execution_phase
        )

        # Sugerencias de ajuste si es necesario
        adjustment_suggestions = self._suggest_adjustments(
            real_time_analysis, execution_phase
        )

        return {
            "success": True,
            "experiment_id": experiment_id,
            "phase": execution_phase,
            "real_time_analysis": real_time_analysis,
            "immediate_feedback": immediate_feedback,
            "adjustment_suggestions": adjustment_suggestions,
            "continue_execution": real_time_analysis.get("should_continue", True)
        }

    async def _analyze_real_time_data(self, experiment_id: str, current_data: Dict[str, Any],
                                    execution_phase: str) -> Dict[str, Any]:
        """
        Analizar datos en tiempo real durante la ejecución
        """
        analysis = {
            "data_quality_score": 0.0,
            "protocol_compliance": 0.0,
            "anomaly_detection": [],
            "trend_analysis": {},
            "quality_metrics": {},
            "should_continue": True,
            "critical_issues": []
        }

        # Análisis de calidad de datos
        if "measurements" in current_data:
            analysis["data_quality_score"] = self._assess_data_quality(current_data["measurements"])

        # Verificación de cumplimiento del protocolo
        if "protocol_steps" in current_data:
            analysis["protocol_compliance"] = self._check_protocol_compliance(
                current_data["protocol_steps"], execution_phase
            )

        # Detección de anomalías
        if "time_series" in current_data:
            analysis["anomaly_detection"] = self._detect_anomalies(current_data["time_series"])

        # Análisis de tendencias
        if "historical_data" in current_data:
            analysis["trend_analysis"] = self._analyze_trends(current_data["historical_data"])

        # Métricas de calidad
        analysis["quality_metrics"] = self._calculate_quality_metrics(current_data)

        # Determinar si continuar la ejecución
        analysis["should_continue"] = self._should_continue_execution(analysis)

        # Identificar issues críticos
        analysis["critical_issues"] = self._identify_critical_issues(analysis)

        return analysis

    def _assess_data_quality(self, measurements: List[Dict[str, Any]]) -> float:
        """Evaluar calidad de mediciones en tiempo real"""
        if not measurements:
            return 0.0

        quality_score = 0.0
        total_measurements = len(measurements)

        for measurement in measurements:
            # Verificar completitud
            if all(key in measurement for key in ["value", "timestamp", "units"]):
                quality_score += 0.3

            # Verificar razonabilidad de valores
            if "value" in measurement:
                value = measurement["value"]
                if isinstance(value, (int, float)) and not (value is None or str(value).lower() in ['nan', 'inf', '-inf']):
                    quality_score += 0.4

            # Verificar consistencia temporal
            if "timestamp" in measurement:
                quality_score += 0.3

        return min(1.0, quality_score / total_measurements)

    def _check_protocol_compliance(self, protocol_steps: List[Dict[str, Any]], phase: str) -> float:
        """Verificar cumplimiento del protocolo experimental"""
        if not protocol_steps:
            return 0.0

        compliance_score = 0.0
        expected_steps = self._get_expected_protocol_steps(phase)

        for step in protocol_steps:
            if step.get("completed", False):
                compliance_score += 1.0

            # Verificar timing
            if "planned_time" in step and "actual_time" in step:
                time_diff = abs(step["actual_time"] - step["planned_time"])
                if time_diff < 0.1:  # Dentro del 10% del tiempo planeado
                    compliance_score += 0.5

        return min(1.0, compliance_score / len(expected_steps))

    def _get_expected_protocol_steps(self, phase: str) -> List[str]:
        """Obtener pasos esperados del protocolo para cada fase"""
        phase_steps = {
            "setup": ["equipment_calibration", "control_setup", "baseline_measurement"],
            "data_collection": ["sample_preparation", "measurement_execution", "data_recording"],
            "analysis": ["data_processing", "statistical_analysis", "results_interpretation"],
            "validation": ["cross_validation", "sensitivity_analysis", "robustness_check"]
        }
        return phase_steps.get(phase, [])

    def _detect_anomalies(self, time_series: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detectar anomalías en series temporales"""
        anomalies = []

        if len(time_series) < 3:
            return anomalies

        values = [point.get("value", 0) for point in time_series]

        # Cálculo de media y desviación estándar
        mean_val = sum(values) / len(values)
        std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5

        # Detectar valores atípicos (más de 3 desviaciones estándar)
        threshold = 3 * std_val

        for i, point in enumerate(time_series):
            if abs(point.get("value", 0) - mean_val) > threshold:
                anomalies.append({
                    "index": i,
                    "timestamp": point.get("timestamp"),
                    "value": point.get("value"),
                    "deviation": abs(point.get("value", 0) - mean_val),
                    "severity": "high" if abs(point.get("value", 0) - mean_val) > 5 * std_val else "medium"
                })

        return anomalies

    def _analyze_trends(self, historical_data: List[AnalyzeTrendsResult]) -> AnalyzeTrendsResult:
        """Analizar tendencias en datos históricos"""
        if len(historical_data) < 2:
            return {"trend": "insufficient_data"}

        # Análisis simple de tendencias
        values = [point.get("value", 0) for point in historical_data]
        timestamps = [point.get("timestamp", 0) for point in historical_data]

        # Cálculo de pendiente (regresión lineal simple)
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_xx = sum(x * x for x in timestamps)

        if n * sum_xx - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        else:
            slope = 0

        # Determinar dirección de la tendencia
        if slope > 0.01:
            trend_direction = "increasing"
        elif slope < -0.01:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        return {
            "trend_direction": trend_direction,
            "slope": slope,
            "confidence": min(1.0, abs(slope) * 100),  # Confianza basada en magnitud de la pendiente
            "data_points": n
        }

    def _calculate_quality_metrics(self, current_data: Dict[str, Any]) -> Dict[str, float]:
        """Calcular métricas de calidad de datos"""
        metrics = {
            "completeness": 0.0,
            "consistency": 0.0,
            "accuracy": 0.0,
            "timeliness": 0.0
        }

        # Completitud
        required_fields = ["value", "timestamp", "units"]
        if "measurements" in current_data:
            complete_records = sum(1 for m in current_data["measurements"]
                                 if all(field in m for field in required_fields))
            metrics["completeness"] = complete_records / len(current_data["measurements"]) if current_data["measurements"] else 0

        # Consistencia (verificar unidades consistentes)
        if "measurements" in current_data:
            units = [m.get("units") for m in current_data["measurements"] if "units" in m]
            if units:
                consistent_units = sum(1 for unit in units if unit == units[0])
                metrics["consistency"] = consistent_units / len(units)

        # Precisión (basada en decimales)
        if "measurements" in current_data:
            precision_scores = []
            for m in current_data["measurements"]:
                if "value" in m:
                    value_str = str(m["value"])
                    if "." in value_str:
                        decimals = len(value_str.split(".")[1])
                        precision_scores.append(min(1.0, decimals / 4))  # Máximo 4 decimales esperado
            if precision_scores:
                metrics["accuracy"] = sum(precision_scores) / len(precision_scores)

        # Oportunidad (datos recientes)
        if "measurements" in current_data and current_data["measurements"]:
            latest_timestamp = max(m.get("timestamp", 0) for m in current_data["measurements"])
            current_time = datetime.now().timestamp()
            time_diff_hours = (current_time - latest_timestamp) / 3600
            metrics["timeliness"] = max(0, 1 - time_diff_hours / 24)  # Degradación en 24 horas

        return metrics

    def _should_continue_execution(self, analysis: Dict[str, Any]) -> bool:
        """Determinar si se debe continuar la ejecución del experimento"""
        # Criterios para detener la ejecución
        stop_conditions = []

        # Calidad de datos muy baja
        if analysis.get("data_quality_score", 1.0) < 0.3:
            stop_conditions.append("data_quality_too_low")

        # Muchas anomalías
        if len(analysis.get("anomaly_detection", [])) > 5:
            stop_conditions.append("too_many_anomalies")

        # Cumplimiento del protocolo bajo
        if analysis.get("protocol_compliance", 1.0) < 0.5:
            stop_conditions.append("protocol_compliance_low")

        # Issues críticos
        if analysis.get("critical_issues"):
            stop_conditions.append("critical_issues_detected")

        return len(stop_conditions) == 0

    def _identify_critical_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """Identificar issues críticos que requieren atención inmediata"""
        critical_issues = []

        if analysis.get("data_quality_score", 1.0) < 0.3:
            critical_issues.append("Data quality is critically low - check measurement equipment")

        if len(analysis.get("anomaly_detection", [])) > 10:
            critical_issues.append("Excessive anomalies detected - investigate experimental conditions")

        if analysis.get("protocol_compliance", 1.0) < 0.3:
            critical_issues.append("Protocol compliance is critically low - review experimental procedure")

        quality_metrics = analysis.get("quality_metrics", {})
        if quality_metrics.get("completeness", 1.0) < 0.5:
            critical_issues.append("Data completeness is critically low - ensure all measurements are recorded")

        return critical_issues

    def _generate_immediate_feedback(self, analysis: GenerateImmediateFeedbackResult, phase: str) -> GenerateImmediateFeedbackResult:
        """Generar feedback inmediato basado en el análisis en tiempo real"""
        feedback = {
            "overall_status": "good",
            "performance_indicators": {},
            "recommendations": [],
            "alerts": []
        }

        # Determinar estado general
        data_quality = analysis.get("data_quality_score", 0)
        protocol_compliance = analysis.get("protocol_compliance", 0)

        if data_quality > 0.8 and protocol_compliance > 0.8:
            feedback["overall_status"] = "excellent"
        elif data_quality > 0.6 and protocol_compliance > 0.6:
            feedback["overall_status"] = "good"
        elif data_quality > 0.4 or protocol_compliance > 0.4:
            feedback["overall_status"] = "concerning"
        else:
            feedback["overall_status"] = "critical"

        # Indicadores de rendimiento
        feedback["performance_indicators"] = {
            "data_quality": f"{data_quality:.1%}",
            "protocol_compliance": f"{protocol_compliance:.1%}",
            "anomalies_detected": len(analysis.get("anomaly_detection", [])),
            "trend_direction": analysis.get("trend_analysis", {}).get("trend_direction", "unknown")
        }

        # Recomendaciones basadas en el análisis
        if data_quality < 0.7:
            feedback["recommendations"].append("Review measurement procedures and equipment calibration")

        if protocol_compliance < 0.7:
            feedback["recommendations"].append("Ensure all protocol steps are being followed correctly")

        if analysis.get("anomaly_detection"):
            feedback["recommendations"].append("Investigate detected anomalies and consider protocol adjustments")

        # Alertas críticas
        critical_issues = analysis.get("critical_issues", [])
        feedback["alerts"].extend(critical_issues)

        return feedback

    def _suggest_adjustments(self, analysis: Dict[str, Any], phase: str) -> List[Dict[str, Any]]:
        """Sugerir ajustes al experimento basados en el análisis en tiempo real"""
        suggestions = []

        # Sugerencias basadas en calidad de datos
        data_quality = analysis.get("data_quality_score", 1.0)
        if data_quality < 0.7:
            suggestions.append({
                "type": "measurement_improvement",
                "priority": "high",
                "description": "Improve measurement precision and accuracy",
                "actions": [
                    "Recalibrate measurement equipment",
                    "Review measurement procedures",
                    "Add redundant measurements",
                    "Implement quality control checks"
                ]
            })

        # Sugerencias basadas en anomalías
        anomalies = analysis.get("anomaly_detection", [])
        if len(anomalies) > 3:
            suggestions.append({
                "type": "anomaly_investigation",
                "priority": "medium",
                "description": "Investigate source of detected anomalies",
                "actions": [
                    "Check experimental conditions",
                    "Review environmental factors",
                    "Verify equipment stability",
                    "Consider systematic errors"
                ]
            })

        # Sugerencias basadas en tendencias
        trend_analysis = analysis.get("trend_analysis", {})
        if trend_analysis.get("trend_direction") == "decreasing" and trend_analysis.get("confidence", 0) > 0.7:
            suggestions.append({
                "type": "trend_correction",
                "priority": "medium",
                "description": "Address declining trend in measurements",
                "actions": [
                    "Check for systematic drift",
                    "Review control conditions",
                    "Consider protocol modifications",
                    "Implement corrective actions"
                ]
            })

        # Sugerencias basadas en cumplimiento del protocolo
        protocol_compliance = analysis.get("protocol_compliance", 1.0)
        if protocol_compliance < 0.8:
            suggestions.append({
                "type": "protocol_compliance",
                "priority": "high",
                "description": "Improve adherence to experimental protocol",
                "actions": [
                    "Review protocol documentation",
                    "Provide additional training",
                    "Implement protocol checklists",
                    "Add monitoring procedures"
                ]
            })

        return suggestions

    async def perform_peer_review(self, request_data: PerformPeerReviewResult) -> PerformPeerReviewResult:
        """Realizar una revisión por pares individual"""
        experiment_data = request_data.get("experiment", {})
        agent_name = request_data.get("reviewer_agent", "interdisciplinary_reviewer")

        if agent_name not in self.reviewer_agents:
            return {
                "success": False,
                "error": f"Unknown reviewer agent: {agent_name}",
                "available_agents": list(self.reviewer_agents.keys())
            }

        agent_config = self.reviewer_agents[agent_name]

        review = await self._simulate_peer_review(
            agent_name, agent_config,
            experiment_data.get("id", "unknown"),
            experiment_data.get("hypothesis", ""),
            experiment_data.get("methodology", ""),
            experiment_data.get("results", {})
        )

        return {
            "success": True,
                "review": self._peer_review_to_dict(review)
        }

    async def batch_validation(self, request_data: BatchValidationResult) -> BatchValidationResult:
        """Validar múltiples experimentos en lote"""
        experiments = request_data.get("experiments", [])

        if not experiments:
            return {
                "success": False,
                "error": "No experiments provided for batch validation"
            }

        results = []
        for i, experiment in enumerate(experiments):
            try:
                validation_result = await self.validate_experiment({"experiment": experiment})
                results.append({
                    "experiment_index": i,
                    "experiment_id": experiment.get("id", f"batch_exp_{i}"),
                    "validation_result": validation_result
                })
            except BiologyError as e:
                results.append({
                    "experiment_index": i,
                    "experiment_id": experiment.get("id", f"batch_exp_{i}"),
                    "error": str(e)
                })

        # Resumen del lote
        successful_validations = [r for r in results if "validation_result" in r and r["validation_result"]["success"]]
        approved_experiments = [r for r in successful_validations if r["validation_result"]["approved"]]

        return {
            "success": True,
            "batch_summary": {
                "total_experiments": len(experiments),
                "successful_validations": len(successful_validations),
                "approved_experiments": len(approved_experiments),
                "approval_rate": len(approved_experiments) / len(experiments) if experiments else 0
            },
            "results": results
        }

    def get_validation_status(self, request_data: GetValidationStatusResult) -> GetValidationStatusResult:
        """Obtener estado de validación de un experimento"""
        experiment_id = request_data.get("experiment_id")

        if not experiment_id:
            return {
                "success": False,
                "error": "experiment_id is required"
            }

        # En una implementación real, esto consultaría una base de datos
        # Por ahora, devolver un estado simulado
        return {
            "success": True,
            "experiment_id": experiment_id,
            "status": "completed",  # pending, in_progress, completed, failed
            "last_updated": datetime.now().isoformat(),
            "validation_score": 8.5,
            "approved": True
        }
