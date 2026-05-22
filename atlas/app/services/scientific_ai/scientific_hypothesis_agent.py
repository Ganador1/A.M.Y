"""
Scientific Hypothesis Agent for AXIOM
Autonomous agent that generates and refines scientific hypotheses
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import uuid
from dataclasses import dataclass, field
from enum import Enum
import aiofiles
import asyncio

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.services.literature_service import LiteratureService
from app.core.config import settings
from app.services.hypothesis_persistence import HypothesisPersistenceService
from app.services.local_llm_service import LocalLLMService
from app.services.prompting.prompt_registry_service import prompt_registry_service
from app.services.policy_engine_service import policy_engine_service  # integración PolicyEngine
from app.config.config_loader import load_config_section
from app.exceptions.domain.biology import BiologyError
from app.types.scientific_hypothesis_agent_types import (
    ProcessRequestResult,
    PolicyDecideResult,
    VerifyHypothesisWithLiteratureResult,
    VerifyHypothesisWithKnowledgeResult,
    GenerateHypothesisResult,
    GenerateHypothesisLogicResult,
    GenerateInsightsResult,
    RefineHypothesesResult,
    StartResearchCycleResult,
    CreateWorkflowForHypothesisResult,
    RefineHypothesisResult,
    AnalyzeEvidenceResult,
    CorroborateWithToolsResult,
    GetHypothesisResult,
    ListHypothesesResult,
)


class HypothesisStatus(Enum):
    """Hypothesis lifecycle status"""
    GENERATED = "generated"
    TESTING = "testing"
    VALIDATED = "validated"
    REJECTED = "rejected"
    REFINED = "refined"


class ResearchPhase(Enum):
    """Research cycle phases"""
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    LITERATURE_REVIEW = "literature_review"
    EXPERIMENT_DESIGN = "experiment_design"
    EXECUTION = "execution"
    ANALYSIS = "analysis"
    REFINEMENT = "refinement"


@dataclass
class ScientificHypothesis:
    """Scientific hypothesis representation"""
    hypothesis_id: str
    title: str
    description: str
    domain: str
    variables: List[str]
    assumptions: List[str]
    expected_outcome: str
    confidence_score: float = 0.0
    status: HypothesisStatus = HypothesisStatus.GENERATED
    created_at: datetime = field(default_factory=datetime.now)
    tested_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    related_papers: List[str] = field(default_factory=list)
    refinement_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ResearchCycle:
    """Complete research cycle"""
    cycle_id: str
    hypothesis: ScientificHypothesis
    current_phase: ResearchPhase
    workflow_id: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    iterations: int = 0


class ScientificHypothesisAgent(BaseService):
    """Autonomous agent for scientific hypothesis generation, validation and refinement.

    Enhancements (Sept 2025):
    - agent_name: identificador personalizado (p.ej. "pablito").
    - Avance automático de fases del ciclo de investigación (literature -> design -> execution -> analysis -> refinement) en una sola invocación.
    - Integración automática de corroboración multi‑herramienta (ToolEvidenceOrchestrator) durante la fase EXECUTION.
    - Ajuste de confidence_score incorporando soporte de herramientas dentro del flujo estándar (antes requería llamada manual externa a corroborate_with_tools).
    - Registro consolidado de resultados en cycle.results['tool_corroboration'].
    """

    def __init__(self, agent_name: str | None = None):
        super().__init__("ScientificHypothesisAgent")
        self.agent_name = agent_name or "axiom_hypothesis_agent"
        # Core state
        self.active_hypotheses: Dict[str, ScientificHypothesis] = {}
        self.research_cycles: Dict[str, ResearchCycle] = {}
        self.domain_knowledge: Dict[str, Dict[str, Any]] = {}

        # Services
        self.literature: LiteratureService = LiteratureService()
        self.persistence: Optional[HypothesisPersistenceService] = None
        self.local_llm: Optional[LocalLLMService] = None
        self.hf_provider: Optional[Any] = None  # HuggingFace provider for cloud models
        self.prompt_registry = prompt_registry_service  # already singleton
        # Carga de configuraciones de prompts (si existe archivo)
        try:
            self._prompt_conf = load_config_section('prompts/hypothesis_agent') or {}
        except BiologyError:
            self._prompt_conf = {}
        try:
            self._agents_conf = load_config_section('agents') or {}
        except Exception:
            self._agents_conf = {}
        bio_role_cfg = (self._agents_conf.get("roles", {}) or {}).get("bio_hypothesis", {})
        if not isinstance(bio_role_cfg, dict):
            bio_role_cfg = {}
        self.role_config = bio_role_cfg
        self.preferred_provider = str(self.role_config.get("provider") or "").lower()
        self.preferred_model = self.role_config.get("model")
        self.provider_params = dict(self.role_config.get("params") or {})

        # Optional persistence
        try:
            if settings.enable_database and settings.database_url:
                self.persistence = HypothesisPersistenceService()
        except BiologyError:
            self.persistence = None

        # Optional local LLM
        try:
            if settings.enable_local_llm:
                self.local_llm = LocalLLMService()
        except BiologyError:
            self.local_llm = None

        self.ollama_provider = None
        try:
            from app.services.llm_providers.ollama_provider import ollama_provider
            if ollama_provider.is_available():
                self.ollama_provider = ollama_provider
                logger.info(
                    f"✅ Ollama provider initialized for '{self.agent_name}'"
                    f" model={self.preferred_model or 'default'}"
                )
        except Exception as e:
            logger.warning(f"⚠️ Ollama provider not available: {e}")

        # Optional Groq provider (ultra-fast inference, priority 1)
        self.groq_provider = None
        try:
            from app.services.llm_providers.groq_provider import groq_provider
            if groq_provider.is_available():
                self.groq_provider = groq_provider
                logger.info(f"✅ Groq provider initialized for '{self.agent_name}' (ultra-fast inference)")
        except Exception as e:
            logger.warning(f"⚠️ Groq provider not available: {e}")

        # Optional HuggingFace provider (cloud models with improved prompts)
        try:
            from app.services.llm_providers.huggingface_provider import huggingface_provider
            from app.services.huggingface_agent_wrapper import HuggingFaceAgentWrapper

            # Check if API key is available
            if huggingface_provider.api_key:
                self.hf_provider = huggingface_provider
                self.hf_wrapper = HuggingFaceAgentWrapper(
                    agent_role="bio_hypothesis",
                    use_improved_prompts=True
                )
                logger.info(f"✅ HuggingFace cloud provider initialized for '{self.agent_name}' with improved prompts v2.0")
            else:
                logger.warning("⚠️ HuggingFace API key not found, using local LLM fallback")
        except Exception as e:
            logger.warning(f"⚠️ HuggingFace provider not available: {e}, using local LLM")
            self.hf_wrapper = None

        # Domain knowledge bootstrap
        self._initialize_domain_knowledge()

        # Log instanciación
        logger.info(
            f"✅ ScientificHypothesisAgent initialized as '{self.agent_name}' "
            f"(provider={self.preferred_provider or 'auto'}, model={self.preferred_model or 'auto'})"
        )

    def _initialize_domain_knowledge(self):
        """Initialize domain-specific knowledge for hypothesis generation"""
        self.domain_knowledge = {
            "materials_science": {
                "key_variables": ["composition", "structure", "temperature", "pressure"],
                "common_patterns": ["property optimization", "phase transitions", "defect engineering"],
                "literature_sources": ["Nature Materials", "Advanced Materials", "Materials Science & Engineering"]
            },
            "drug_discovery": {
                "key_variables": ["molecular_structure", "binding_affinity", "toxicity", "solubility"],
                "common_patterns": ["structure-activity relationships", "binding optimization", "ADMET properties"],
                "literature_sources": ["Nature Chemical Biology", "Journal of Medicinal Chemistry", "Drug Discovery Today"]
            },
            "energy_storage": {
                "key_variables": ["capacity", "voltage", "cycle_life", "energy_density"],
                "common_patterns": ["electrode optimization", "electrolyte design", "interface engineering"],
                "literature_sources": ["Nature Energy", "Advanced Energy Materials", "Energy Storage Materials"]
            },
            "quantum_computing": {
                "key_variables": ["qubit_coherence", "gate_fidelity", "error_rate", "scalability"],
                "common_patterns": ["noise reduction", "error correction", "quantum algorithms"],
                "literature_sources": ["Nature Physics", "Physical Review Letters", "Quantum Science and Technology"]
            },
            "quantum_physics": {
                "key_variables": ["hamiltonian", "entanglement_entropy", "topological_order", "coherence_time"],
                "common_patterns": ["error correction", "phase transitions", "spectral gaps", "quantum control"],
                "literature_sources": ["Physical Review X", "Nature Physics", "Quantum Information & Computation"]
            },
            "biophysics": {
                "key_variables": ["protein_structure", "membrane_potential", "molecular_dynamics", "thermodynamics"],
                "common_patterns": ["conformational changes", "protein folding", "membrane interactions", "enzymatic activity"],
                "literature_sources": ["Biophysical Journal", "Nature Structural Biology", "Physical Biology"]
            },
            "genomics": {
                "key_variables": ["sequence_variation", "gene_expression", "epigenetic_marks", "population_structure"],
                "common_patterns": ["GWAS studies", "expression QTL", "evolutionary selection", "functional annotation"],
                "literature_sources": ["Nature Genetics", "Genome Research", "PLOS Genetics"]
            },
            "biology": {
                "key_variables": ["cell_signaling", "gene_expression", "metabolic_pathways", "phenotypic_response"],
                "common_patterns": ["pathway modulation", "gene regulation", "adaptive response", "microenvironment effects"],
                "literature_sources": ["Cell", "Nature Biology", "PLOS Biology"]
            },
            "biomedical_engineering": {
                "key_variables": ["biocompatibility", "mechanical_properties", "degradation_rate", "cellular_response"],
                "common_patterns": ["tissue scaffolds", "drug delivery systems", "medical devices", "regenerative medicine"],
                "literature_sources": ["Nature Biomedical Engineering", "Biomaterials", "Tissue Engineering"]
            },
            "neuroscience": {
                "key_variables": ["neural_activity", "connectivity", "plasticity", "neurotransmitters"],
                "common_patterns": ["synaptic transmission", "neural networks", "learning mechanisms", "disease pathology"],
                "literature_sources": ["Nature Neuroscience", "Neuron", "Journal of Neuroscience"]
            },
            "mathematics": {
                "key_variables": ["spectral_radius", "prime_gaps", "manifold_structure", "symmetry_group"],
                "common_patterns": ["probabilistic method", "spectral analysis", "variational bounds", "algebraic decomposition"],
                "literature_sources": ["Annals of Mathematics", "Communications in Mathematical Physics", "Journal of Number Theory"]
            }
        }

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process hypothesis agent requests"""
        try:
            action = request_data.get("action", "")

            if action == "generate_hypothesis":
                return await self.generate_hypothesis(request_data)
            elif action == "start_research_cycle":
                return await self.start_research_cycle(request_data)
            elif action == "refine_hypothesis":
                return await self.refine_hypothesis(request_data)
            elif action == "analyze_evidence":
                return await self.analyze_evidence(request_data)
            elif action == "generate_insights":
                return await self.generate_insights(request_data)
            elif action == "refine_hypotheses":
                return await self.refine_hypotheses(request_data)
            elif action == "verify_hypothesis_with_literature":
                return await self.verify_hypothesis_with_literature(request_data)
            elif action == "verify_hypothesis_with_knowledge":
                return await self.verify_hypothesis_with_knowledge(request_data)
            elif action == "corroborate_with_tools":
                return await self.corroborate_with_tools(request_data)
            elif action == "policy_decide":  # nueva acción
                return self.policy_decide(request_data)
            elif action == "get_hypothesis":
                return self.get_hypothesis(request_data)
            elif action == "list_hypotheses":
                return self.list_hypotheses(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "generate_hypothesis", "start_research_cycle", "refine_hypothesis",
                        "analyze_evidence", "get_hypothesis", "list_hypotheses", "corroborate_with_tools", "policy_decide"
                    ]
                }

        except BiologyError as e:
            return self.handle_error(e, "process_request")

    # --- Integración Policy Engine ---
    def policy_decide(self, request_data: PolicyDecideResult) -> PolicyDecideResult:
        """Wrapper sobre PolicyEngineService.decide().
        Espera un dict 'scores' con métricas (novelty, evidence_strength, reproducibility_risk, etc.).
        Opcional: hypothesis_id para rastrear y loggear la decisión.
        """
        try:
            scores = request_data.get("scores") or {}
            hypothesis_id = request_data.get("hypothesis_id")
            if hypothesis_id and hypothesis_id not in self.active_hypotheses:
                return {"success": False, "error": f"Hypothesis {hypothesis_id} not found"}
            # Llamar motor
            result = policy_engine_service.decide(scores, hypothesis_id=hypothesis_id)
            return result | {"success": True}
        except BiologyError as e:
            return self.handle_error(e, "policy_decide")

    async def verify_hypothesis_with_literature(self, request_data: VerifyHypothesisWithLiteratureResult) -> VerifyHypothesisWithLiteratureResult:
        try:
            hypothesis_id = request_data.get("hypothesis_id")
            if not hypothesis_id or hypothesis_id not in self.active_hypotheses:
                return {"success": False, "error": f"Hypothesis {hypothesis_id} not found"}
            h = self.active_hypotheses[hypothesis_id]
            lr = await self.literature.process_request({
                "action": "verify_hypothesis",
                "hypothesis": {
                    "title": h.title,
                    "variables": h.variables,
                },
                "k": request_data.get("k", 10)
            })
            if lr.get("success"):
                score = float(lr.get("support_score", 0.0))
                # opcional: ajustar confianza ligeramente
                h.confidence_score = min(1.0, h.confidence_score + 0.1 * score)
                return {"success": True, "support_score": score, "papers": lr.get("papers", [])}
            return lr
        except BiologyError as e:
            return self.handle_error(e, "verify_hypothesis_with_literature")

    async def verify_hypothesis_with_knowledge(self, request_data: VerifyHypothesisWithKnowledgeResult) -> VerifyHypothesisWithKnowledgeResult:
        """Verificación ampliada usando múltiples fuentes (papers, arXiv, patentes, materiales, ChEMBL)."""
        try:
            hypothesis_id = request_data.get("hypothesis_id")
            if not hypothesis_id or hypothesis_id not in self.active_hypotheses:
                return {"success": False, "error": f"Hypothesis {hypothesis_id} not found"}
            h = self.active_hypotheses[hypothesis_id]
            lr = await self.literature.process_request({
                "action": "verify_hypothesis_plus",
                "hypothesis": {
                    "title": h.title,
                    "variables": h.variables,
                },
                "k": request_data.get("k", 12)
            })
            if lr.get("success"):
                score = float(lr.get("support_score", 0.0))
                # ajustar confianza de forma más marcada en la verificación multi-fuente
                h.confidence_score = min(1.0, max(0.0, h.confidence_score + 0.2 * (score - 0.5)))
                return {
                    "success": True,
                    "support_score": score,
                    "reasons": lr.get("reasons", []),
                    "sources": lr.get("sources", {}),
                }
            return lr
        except BiologyError as e:
            return self.handle_error(e, "verify_hypothesis_with_knowledge")

    async def generate_hypothesis(self, request_data: GenerateHypothesisResult) -> GenerateHypothesisResult:
        """Generate a new scientific hypothesis using prompt registry + local LLM fallback."""
        try:
            domain = request_data.get("domain", "")
            research_question = request_data.get("research_question", "")
            context_data = request_data.get("context_data", {})

            if not domain or not research_question:
                return {"success": False, "error": "domain and research_question are required"}

            if domain not in self.domain_knowledge:
                return {"success": False, "error": f"Domain '{domain}' not supported. Available: {list(self.domain_knowledge.keys())}"}

            use_prompt_registry = request_data.get("use_prompt_registry", True)
            requested_version = request_data.get("prompt_version")  # optional explicit version

            # Attempt prompt registry render (register default template if missing) only if flag enabled
            prompt: Optional[str] = None
            default_template = (
                "You are a scientific hypothesis generator. Given a domain, research question and optional context, "
                "produce ONE concise, testable hypothesis.\n"
                "Domain: {{ domain }}\n"
                "Research Question: {{ research_question }}\n"
                "Context: {{ context_data }}\n"
                "Return JSON with keys: title, description, variables (list), assumptions (list), expected_outcome, confidence_score (0-1)."
            )
            if use_prompt_registry:
                try:
                    get_res = self.prompt_registry.get(name="hypothesis_generation") if self.prompt_registry else {"success": False}
                    if not get_res.get("success"):
                        try:
                            self.prompt_registry.register(
                                name="hypothesis_generation",
                                version="v1",
                                template=default_template,
                                variables=["domain", "research_question", "context_data"],
                                metadata={"description": "Default hypothesis generation template"}
                            )
                            get_res = self.prompt_registry.get(name="hypothesis_generation")
                        except BiologyError:
                            get_res = {"success": False}
                    version_to_use: Optional[str] = None
                    raw_prompts = get_res.get("prompts") if isinstance(get_res, dict) else None
                    if get_res.get("success") and isinstance(raw_prompts, list) and raw_prompts:
                        if requested_version:
                            # try find requested
                            match = next((p for p in raw_prompts if p.get("version") == requested_version), None)
                            if match:
                                version_to_use = str(match.get("version"))
                        if not version_to_use:
                            first_prompt = raw_prompts[0]
                            if isinstance(first_prompt, dict):
                                version_to_use = str(first_prompt.get("version"))
                    if version_to_use:
                        render_res = self.prompt_registry.render(
                            name="hypothesis_generation",
                            version=version_to_use,
                            context={
                                "domain": domain,
                                "research_question": research_question,
                                "context_data": context_data
                            }
                        )
                        if render_res.get("success"):
                            prompt = render_res.get("rendered")
                except BiologyError:
                    prompt = None

            # Prompt externo si disponible
            tmpl = None
            try:
                tmpl = self._prompt_conf.get("templates", {}).get("generate", {})
            except BiologyError:
                tmpl = None
            if tmpl and isinstance(tmpl, dict):
                system_p = tmpl.get("system", "")
                user_p = tmpl.get("user", "")
                prompt = system_p + "\n" + user_p.replace("{{research_question}}", research_question).replace("{{domain}}", domain)
            # si no hay tmpl externo, mantener prompt previo (puede venir del registry)
            hypothesis_data: Dict[str, Any]

            structured_prompt = f"""You are a scientific hypothesis generator. Generate ONE precise, novel, and testable hypothesis.

Domain: {domain}
Research Question: {research_question}
Context: {context_data if context_data else 'No additional context'}

Requirements:
1. Be SPECIFIC - name exact molecules, proteins, genes, materials, or mechanisms
2. Include QUANTITATIVE predictions (e.g., "increases by 30-50%", "reduces latency to <100ms")
3. Propose TESTABLE experimental validation methods
4. Explain the underlying MECHANISM

Respond in JSON format:
{{
    "hypothesis": "Your clear hypothesis statement",
    "mechanism": "The underlying scientific mechanism",
    "quantitative_predictions": ["Prediction 1 with numbers", "Prediction 2 with numbers"],
    "experimental_validation": ["Experiment 1", "Experiment 2"],
    "confidence_score": 0.85
}}"""

            # Priority 0: explicit Ollama route from agents.yaml
            if self.preferred_provider == "ollama" and self.ollama_provider is not None and self.ollama_provider.is_available():
                try:
                    logger.info("☁️ Using configured Ollama provider for hypothesis generation...")
                    ollama_kwargs = dict(self.provider_params)
                    max_tokens = int(ollama_kwargs.pop("max_new_tokens", 1024))
                    temperature = float(ollama_kwargs.pop("temperature", 0.7))
                    result = await self.ollama_provider.generate_async(
                        prompt=structured_prompt,
                        model=self.preferred_model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        think=False,
                        **ollama_kwargs,
                    )

                    if result.get("success"):
                        response_text = result.get("text", "")
                        try:
                            json_start = response_text.find('{')
                            json_end = response_text.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                response_data = json.loads(response_text[json_start:json_end])
                                hypothesis_data = {
                                    "title": str(response_data.get("hypothesis", ""))[:200],
                                    "description": str(response_data.get("hypothesis", "")),
                                    "variables": response_data.get("quantitative_predictions", [])[:5],
                                    "assumptions": [response_data.get("mechanism", "")],
                                    "expected_outcome": str(response_data.get("experimental_validation", [""])[0]),
                                    "confidence_score": float(response_data.get("confidence_score", 0.8))
                                }
                                logger.info(f"✅ Ollama generated hypothesis: {hypothesis_data['title'][:80]}...")
                            else:
                                raise json.JSONDecodeError("No JSON found", response_text, 0)
                        except json.JSONDecodeError:
                            hypothesis_data = {
                                "title": f"{domain}: {research_question[:100]}",
                                "description": response_text[:500],
                                "variables": [research_question],
                                "assumptions": ["Generated from Ollama cloud model"],
                                "expected_outcome": "See description for detailed predictions",
                                "confidence_score": 0.8
                            }
                            logger.info(f"✅ Ollama generated text hypothesis: {hypothesis_data['title'][:80]}...")
                    else:
                        logger.warning(f"⚠️ Ollama generation failed: {result.get('error')}, using fallback logic...")
                        hypothesis_data = None
                except Exception as e:
                    logger.error(f"❌ Ollama generation error: {e}, using fallback logic...")
                    hypothesis_data = None
            else:
                hypothesis_data = None

            # Priority 1: Try Groq only when explicitly selected or auto mode
            if (
                hypothesis_data is None
                and self.preferred_provider in {"", "groq"}
                and hasattr(self, 'groq_provider')
                and self.groq_provider is not None
                and self.groq_provider.is_available()
            ):
                try:
                    logger.info("🚀 Using Groq provider (ultra-fast inference)...")

                    result = await self.groq_provider.generate_async(
                        prompt=structured_prompt,
                        model="llama-3.3-70b-versatile",
                        temperature=0.7,
                        max_tokens=1024
                    )
                    
                    if result.get("success"):
                        response_text = result.get("text", "")
                        try:
                            # Parse JSON from response
                            json_start = response_text.find('{')
                            json_end = response_text.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                response_data = json.loads(response_text[json_start:json_end])
                                hypothesis_data = {
                                    "title": str(response_data.get("hypothesis", ""))[:200],
                                    "description": str(response_data.get("hypothesis", "")),
                                    "variables": response_data.get("quantitative_predictions", [])[:5],
                                    "assumptions": [response_data.get("mechanism", "")],
                                    "expected_outcome": str(response_data.get("experimental_validation", [""])[0]),
                                    "confidence_score": float(response_data.get("confidence_score", 0.85))
                                }
                                logger.info(f"✅ Groq generated hypothesis: {hypothesis_data['title'][:80]}...")
                            else:
                                raise json.JSONDecodeError("No JSON found", response_text, 0)
                        except json.JSONDecodeError:
                            # Use text as description
                            hypothesis_data = {
                                "title": f"{domain}: {research_question[:100]}",
                                "description": response_text[:500],
                                "variables": [research_question],
                                "assumptions": ["Generated from Groq LLM"],
                                "expected_outcome": "See description for detailed predictions",
                                "confidence_score": 0.85
                            }
                            logger.info(f"✅ Groq generated text hypothesis: {hypothesis_data['title'][:80]}...")
                    else:
                        logger.warning(f"⚠️ Groq generation failed: {result.get('error')}, trying HuggingFace...")
                        hypothesis_data = None
                except Exception as e:
                    logger.error(f"❌ Groq generation error: {e}, trying HuggingFace...")
                    hypothesis_data = None

            # Priority 2: Try HuggingFace cloud models when explicitly selected or auto mode
            if (
                hypothesis_data is None
                and self.preferred_provider in {"", "huggingface"}
                and hasattr(self, 'hf_wrapper')
                and self.hf_wrapper is not None
            ):
                try:
                    logger.info("🚀 Using HuggingFace cloud model with improved prompts v2.0...")

                    # Use improved prompt template with literatura context
                    from app.services.improved_agent_prompts import get_improved_prompt
                    
                    # Extract context fields using safe gets
                    literatura_context = context_data.get('literature_context') if isinstance(context_data, dict) else None
                    peer_review_feedback = context_data.get('peer_review_feedback') if isinstance(context_data, dict) else None
                    failed_hypotheses = context_data.get('failed_hypotheses') if isinstance(context_data, dict) else None
                    
                    # Build enriched prompt context
                    context_str = ""
                    
                    # 1. Literature Gaps
                    if literatura_context and 'identified_gaps' in literatura_context:
                        gaps = literatura_context['identified_gaps']
                        if gaps:
                            context_str += "\n\nOPEN SCIENTIFIC GAPS:\n" + "\n".join([f"- {gap}" for gap in gaps[:5]])
                            
                    # 2. Peer Review Feedback (Iterative Improvement)
                    if peer_review_feedback:
                        context_str += "\n\nFEEDBACK FROM PREVIOUS PEER REVIEW:\n"
                        if 'issues' in peer_review_feedback:
                            context_str += "Issues to Fix:\n" + "\n".join([f"- {i.get('description', '')}" for i in peer_review_feedback['issues'][:3]])
                        if 'recommendations' in peer_review_feedback:
                            context_str += "\nRecommendations:\n" + "\n".join([f"- {r}" for r in peer_review_feedback['recommendations'][:3]])
                            
                    # 3. Failed Hypotheses (Avoid Repetition)
                    if failed_hypotheses:
                        context_str += "\n\nPREVIOUSLY FAILED HYPOTHESES (DO NOT REPEAT):\n"
                        for h in failed_hypotheses[:3]:
                            context_str += f"- {h.get('title')}: {h.get('rejection_reason', 'Rejected')}\n"
                    
                    # Build user prompt for bio_hypothesis
                    user_prompt_content = f"""Generate a hypothesis about the relationship between {research_question}.
Domain: {domain}

CONTEXT DATA:{context_str}

REQUIREMENTS:
1. Focus on specific entities, quantifiable predictions, and testable experiments.
2. Address the identified gaps and peer review feedback.
3. Propose a novel mechanism not present in failed hypotheses.
"""

                    # Get improved prompt with literatura context
                    full_prompt = get_improved_prompt(
                        agent_role="bio_hypothesis",
                        user_prompt=user_prompt_content,
                        domain=domain,
                        literature_context=literatura_context
                    )

                    response_text = await self.hf_wrapper.generate_async(full_prompt)

                    # Parse JSON response from improved prompts
                    try:
                        # Try parsing as JSON (improved prompts return structured JSON)
                        response_data = json.loads(response_text) if response_text.strip().startswith('{') else None

                        if response_data and isinstance(response_data, dict):
                            # Extract from improved prompt format
                            hypothesis_data = {
                                "title": str(response_data.get("hypothesis", "")[:200]),  # First 200 chars as title
                                "description": str(response_data.get("hypothesis", "")),
                                "variables": response_data.get("quantitative_predictions", [])[:5] if response_data.get("quantitative_predictions") else [],
                                "assumptions": list(response_data.get("mechanism", {}).values())[:3] if response_data.get("mechanism") else [],
                                "expected_outcome": str(response_data.get("quantitative_predictions", [{}])[0].get("outcome", "")) if response_data.get("quantitative_predictions") else "",
                                "confidence_score": 0.9  # High confidence for improved prompts
                            }
                            logger.info(f"✅ HuggingFace generated high-quality hypothesis: {hypothesis_data['title'][:80]}...")
                        else:
                            # Fallback to legacy format
                            hypothesis_data = await self._generate_hypothesis_logic(domain, research_question, context_data)
                    except json.JSONDecodeError:
                        # If not JSON, use text as description
                        logger.warning("⚠️ HF response not JSON, using as text description")
                        hypothesis_data = {
                            "title": f"{domain}: {research_question[:100]}",
                            "description": response_text[:500],
                            "variables": [research_question],
                            "assumptions": ["Generated from HuggingFace cloud model"],
                            "expected_outcome": "See description for detailed predictions",
                            "confidence_score": 0.85
                        }
                except Exception as e:
                    logger.error(f"❌ HuggingFace generation failed: {e}, falling back to local LLM")
                    hypothesis_data = None

            # Priority 2: Local LLM fallback
            if hypothesis_data is None and self.local_llm and self.local_llm.is_ready():
                if not prompt:
                    # Minimal embedded fallback prompt
                    prompt = (
                        "You are a scientific hypothesis generator. Given a research question and domain, propose ONE precise, testable hypothesis.\n"
                        f"Domain: {domain}\nResearch question: {research_question}\nContext: {context_data}\n"
                        "Return JSON with keys: title, description, variables (list), assumptions (list), expected_outcome, confidence_score (0-1)."
                    )
                gen = self.local_llm.generate_json(prompt, schema_hint="hypothesis")
                if gen.get("success") and isinstance(gen.get("json"), dict):
                    data = gen.get("json") or {}
                    if data.get("title") and data.get("variables"):
                        hypothesis_data = {
                            "title": str(data.get("title")),
                            "description": str(data.get("description", "")),
                            "variables": list(data.get("variables", [])),
                            "assumptions": list(data.get("assumptions", [])),
                            "expected_outcome": str(data.get("expected_outcome", "")),
                            "confidence_score": float(data.get("confidence_score", 0.6)),
                        }
                    else:
                        hypothesis_data = await self._generate_hypothesis_logic(domain, research_question, context_data)
                else:
                    hypothesis_data = None

            # Priority 3: Logic-based fallback
            if hypothesis_data is None:
                hypothesis_data = await self._generate_hypothesis_logic(domain, research_question, context_data)

            # Create hypothesis object
            hypothesis = ScientificHypothesis(
                hypothesis_id=str(uuid.uuid4()),
                title=hypothesis_data["title"],
                description=hypothesis_data["description"],
                domain=domain,
                variables=hypothesis_data["variables"],
                assumptions=hypothesis_data["assumptions"],
                expected_outcome=hypothesis_data["expected_outcome"],
                confidence_score=hypothesis_data["confidence_score"]
            )

            self.active_hypotheses[hypothesis.hypothesis_id] = hypothesis

            # Persist if possible
            if self.persistence:
                try:
                    await self.persistence.process_request({
                        "action": "create",
                        "hypothesis_uuid": hypothesis.hypothesis_id,
                        "title": hypothesis.title,
                        "description": hypothesis.description,
                        "domain": hypothesis.domain,
                        "variables": hypothesis.variables,
                        "assumptions": hypothesis.assumptions,
                        "expected_outcome": hypothesis.expected_outcome,
                        "confidence_score": hypothesis.confidence_score,
                        "status": hypothesis.status.value,
                    })
                except Exception:
                    pass

            logger.info(f"✅ Generated hypothesis: {hypothesis.title} in domain {domain}")

            return {
                "success": True,
                "message": f"Hypothesis '{hypothesis.title}' generated successfully",
                "hypothesis_id": hypothesis.hypothesis_id,
                "hypothesis": {
                    "title": hypothesis.title,
                    "description": hypothesis.description,
                    "domain": hypothesis.domain,
                    "variables": hypothesis.variables,
                    "expected_outcome": hypothesis.expected_outcome,
                    "confidence_score": hypothesis.confidence_score
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "generate_hypothesis")

    async def _generate_hypothesis_logic(self, domain: str, research_question: str, context_data: GenerateHypothesisLogicResult) -> GenerateHypothesisLogicResult:
        """Core logic for hypothesis generation using AI reasoning"""
        domain_info = self.domain_knowledge[domain]

        # Simulate AI reasoning for hypothesis generation
        # In a real implementation, this would use LangChain agents

        if domain == "materials_science":
            if "thermal" in research_question.lower():
                return {
                    "title": "Nanoparticle doping enhances thermal conductivity",
                    "description": f"By doping {context_data.get('material', 'the material')} with nanoparticles, thermal conductivity can be increased by 30-50%",
                    "variables": ["dopant_concentration", "particle_size", "temperature"],
                    "assumptions": ["Uniform dispersion", "Interface thermal resistance minimized"],
                    "expected_outcome": "Improved heat dissipation for electronic applications",
                    "confidence_score": 0.75
                }
            elif "mechanical" in research_question.lower():
                return {
                    "title": "Composite reinforcement optimizes strength-to-weight ratio",
                    "description": f"Strategic reinforcement patterns in {context_data.get('material', 'composite materials')} can achieve 40% strength improvement with only 10% weight increase",
                    "variables": ["reinforcement_pattern", "fiber_orientation", "matrix_material"],
                    "assumptions": ["Perfect interfacial bonding", "No defect formation"],
                    "expected_outcome": "Lightweight high-strength materials for aerospace",
                    "confidence_score": 0.80
                }

        elif domain == "drug_discovery":
            if "binding" in research_question.lower():
                return {
                    "title": "Molecular conformation affects binding affinity",
                    "description": f"Optimizing the 3D conformation of {context_data.get('ligand', 'the ligand')} can improve binding affinity to target protein by 2-3 orders of magnitude",
                    "variables": ["conformation_angle", "hydrogen_bonding", "hydrophobic_interactions"],
                    "assumptions": ["Protein structure remains stable", "No allosteric effects"],
                    "expected_outcome": "More potent drug candidates with fewer side effects",
                    "confidence_score": 0.70
                }

        elif domain == "energy_storage":
            if "battery" in research_question.lower():
                return {
                    "title": "Electrolyte additive extends cycle life",
                    "description": f"Adding {context_data.get('additive', 'a specific additive')} to the electrolyte can extend battery cycle life by 200-300%",
                    "variables": ["additive_concentration", "electrolyte_composition", "temperature"],
                    "assumptions": ["Additive remains stable", "No side reactions with electrodes"],
                    "expected_outcome": "Longer-lasting batteries for electric vehicles",
                    "confidence_score": 0.65
                }

        # Default hypothesis generation
        return {
            "title": f"Optimization hypothesis for {domain}",
            "description": f"Systematic optimization of {domain_info['key_variables'][0]} can lead to significant improvements in {research_question}",
            "variables": domain_info["key_variables"][:3],
            "assumptions": ["Linear relationships", "No confounding factors"],
            "expected_outcome": "Measurable improvement in target metrics",
            "confidence_score": 0.60
        }

    async def generate_insights(self, request_data: GenerateInsightsResult) -> GenerateInsightsResult:
        """Generate insights from hypotheses and results (lightweight heuristic)"""
        try:
            research_topic = request_data.get("research_topic", "")
            hypotheses = request_data.get("hypotheses", [])
            results = request_data.get("experimental_results", [])

            insights: List[str] = []

            if hypotheses:
                top = max(hypotheses, key=lambda h: h.get("confidence_score", 0.0))
                insights.append(f"Priorizar hipótesis: {top.get('title')} (confianza {top.get('confidence_score', 0):.2f})")

            if results:
                outcomes = [r.get("outcome", 0.0) for r in results if isinstance(r, dict)]
                if outcomes:
                    import numpy as _np
                    m, s = float(_np.mean(outcomes)), float(_np.std(outcomes))
                    insights.append(f"Resultados: media={m:.3f}, desviación={s:.3f}")

            if research_topic:
                insights.append(f"Siguiente paso sugerido para '{research_topic}': ampliar rango de parámetros clave")

            return {"success": True, "insights": insights}
        except BiologyError as e:
            return self.handle_error(e, "generate_insights")

    async def refine_hypotheses(self, request_data: RefineHypothesesResult) -> RefineHypothesesResult:
        """Refine list of hypotheses based on insights and results"""
        try:
            existing = request_data.get("existing_hypotheses", [])
            insights = request_data.get("insights", [])

            refined = []
            for h in existing:
                if not isinstance(h, dict):
                    continue
                new_h = dict(h)
                # Simple adjustment: boost confidence slightly if any insight mentions prioritization
                if any("Priorizar hipótesis" in i for i in insights):
                    new_h["confidence_score"] = min(1.0, new_h.get("confidence_score", 0.5) + 0.05)
                new_h["title"] = f"Refinada: {new_h.get('title', 'Hipótesis')}"
                refined.append(new_h)

            return {"success": True, "refined_hypotheses": refined}
        except BiologyError as e:
            return self.handle_error(e, "refine_hypotheses")

    async def start_research_cycle(self, request_data: StartResearchCycleResult) -> StartResearchCycleResult:
        """Start a complete research cycle for a hypothesis"""
        try:
            hypothesis_id = request_data.get("hypothesis_id")

            if not hypothesis_id or hypothesis_id not in self.active_hypotheses:
                return {
                    "success": False,
                    "error": f"Hypothesis {hypothesis_id} not found"
                }

            hypothesis = self.active_hypotheses[hypothesis_id]

            # Create research cycle
            cycle = ResearchCycle(
                cycle_id=str(uuid.uuid4()),
                hypothesis=hypothesis,
                current_phase=ResearchPhase.HYPOTHESIS_GENERATION
            )

            self.research_cycles[cycle.cycle_id] = cycle

            # Start the research cycle
            await self._advance_research_cycle(cycle)

            logger.info(f"🚀 Started research cycle for hypothesis: {hypothesis.title}")

            return {
                "success": True,
                "message": f"Research cycle started for hypothesis '{hypothesis.title}'",
                "cycle_id": cycle.cycle_id,
                "current_phase": cycle.current_phase.value
            }

        except BiologyError as e:
            return self.handle_error(e, "start_research_cycle")

    async def _advance_research_cycle(self, cycle: ResearchCycle):
        """Advance the research cycle through phases automatically until analysis (1 iteration by default).

        Nota: Antes el avance se detenía tras cada fase y requería múltiples llamadas.
        Ahora se recorre el pipeline completo (GEN -> LIT -> DESIGN -> EXEC -> ANALYSIS) y se ejecuta
        corroboración de herramientas dentro de EXECUTION. Refinement adicional sigue disponible pero
        por defecto hacemos solo una pasada para evitar loops largos en modo demo.
        """
        try:
            # Bucle de avance controlado
            safety_counter = 0
            while not cycle.completed_at and safety_counter < 10:
                safety_counter += 1
                phase = cycle.current_phase
                if phase == ResearchPhase.HYPOTHESIS_GENERATION:
                    cycle.current_phase = ResearchPhase.LITERATURE_REVIEW
                    await self._perform_literature_review(cycle)
                elif phase == ResearchPhase.LITERATURE_REVIEW:
                    cycle.current_phase = ResearchPhase.EXPERIMENT_DESIGN
                    await self._design_experiments(cycle)
                elif phase == ResearchPhase.EXPERIMENT_DESIGN:
                    cycle.current_phase = ResearchPhase.EXECUTION
                    await self._execute_experiments(cycle)
                elif phase == ResearchPhase.EXECUTION:
                    cycle.current_phase = ResearchPhase.ANALYSIS
                    await self._analyze_results(cycle)
                elif phase == ResearchPhase.ANALYSIS:
                    # Para demostración: finalizar tras primer ciclo de análisis
                    cycle.completed_at = datetime.now()
                elif phase == ResearchPhase.REFINEMENT:
                    # (No usamos refinamiento automático por defecto en esta versión acelerada)
                    cycle.completed_at = datetime.now()
                else:
                    cycle.completed_at = datetime.now()
        except BiologyError as e:
            logger.error(f"❌ Error advancing research cycle {cycle.cycle_id}: {e}")
            cycle.completed_at = datetime.now()

    async def _perform_literature_review(self, cycle: ResearchCycle):
        """Perform literature review for the hypothesis"""
        # Simulate literature search
        # In real implementation, this would search scientific databases
        cycle.results["literature_review"] = {
            "papers_found": 15,
            "relevant_papers": 8,
            "key_findings": [
                "Similar approaches show 20-30% improvement",
                "Critical parameters identified",
                "Potential limitations noted"
            ],
            "confidence_boost": 0.15
        }

        # Update hypothesis confidence
        cycle.hypothesis.confidence_score += 0.15
        cycle.hypothesis.related_papers = ["paper_1", "paper_2", "paper_3"]

    async def _design_experiments(self, cycle: ResearchCycle):
        """Design experiments to test the hypothesis"""
        # Create workflow for hypothesis testing
        from app.services.workflow_orchestration import WorkflowOrchestratorService

        workflow_service = WorkflowOrchestratorService()

        # Design workflow based on hypothesis domain
        workflow_config = self._create_workflow_for_hypothesis(cycle.hypothesis)

        workflow_result = await workflow_service.process_request({
            "action": "create_workflow",
            "name": f"Test: {cycle.hypothesis.title}",
            "steps": workflow_config["steps"],
            "metadata": {
                "hypothesis_id": cycle.hypothesis.hypothesis_id,
                "research_cycle_id": cycle.cycle_id
            }
        })

        if workflow_result.get("success"):
            cycle.workflow_id = workflow_result["workflow_id"]
            cycle.results["experiment_design"] = {
                "workflow_created": True,
                "workflow_id": cycle.workflow_id,
                "steps_count": len(workflow_config["steps"])
            }
        else:
            cycle.results["experiment_design"] = {
                "workflow_created": False,
                "error": workflow_result.get("error")
            }

    def _create_workflow_for_hypothesis(self, hypothesis: ScientificHypothesis) -> CreateWorkflowForHypothesisResult:
        """Create workflow configuration for testing a hypothesis using available ops.

        Domain-specific templates extend the basic reasoning step with extra analytical or simulation
        operations to make experiment design richer.
        """
        base_problem = f"{hypothesis.title}: {hypothesis.description}"
        steps: List[Dict[str, Any]] = [
            {
                "service_type": "scientific_ai",
                "operation": "scientific_reasoning",
                "parameters": {"problem": base_problem},
                "description": "Core reasoning over hypothesis"
            }
        ]
        domain_extra: Dict[str, List[Dict[str, Any]]] = {
            "materials_science": [
                {"service_type": "materials", "operation": "predict_properties", "parameters": {"formula": "LiFePO4"}, "description": "Baseline property prediction"},
                {"service_type": "numpy", "operation": "matrix_operations", "parameters": {"operation": "eigenvalues", "size": 4}, "description": "Lattice eigen analysis"},
            ],
            "genomics": [
                {"service_type": "genomics", "operation": "analyze_sequence", "parameters": {"sequence": "ATCGATCG", "task": "classification"}, "description": "Sequence motif screening"},
                {"service_type": "scikit", "operation": "clustering_analysis", "parameters": {"algorithm": "pca", "data_type": "genomic_data"}, "description": "Dimensionality reduction"},
            ],
            "medical_imaging": [
                {"service_type": "medical_imaging", "operation": "list_methods", "parameters": {}, "description": "Enumerate segmentation methods"},
                {"service_type": "torch", "operation": "medical_ai_analysis", "parameters": {"modality": "MRI", "task": "segmentation"}, "description": "AI segmentation trial"},
            ],
            "biophysics": [
                {"service_type": "scipy", "operation": "optimization", "parameters": {"method": "minimize", "objective": "energy_minimization"}, "description": "Energy landscape optimization"},
            ],
            "drug_discovery": [
                {"service_type": "transformers", "operation": "text_generation", "parameters": {"prompt": "binding affinity factors", "max_length": 80}, "description": "Generate binding rationale"},
            ],
        }
        steps.extend(domain_extra.get(hypothesis.domain, []))
        return {"steps": steps}

    async def _execute_experiments(self, cycle: ResearchCycle):
        """Execute the designed experiments"""
        if cycle.workflow_id:
            from app.services.workflow_orchestration import WorkflowOrchestratorService

            workflow_service = WorkflowOrchestratorService()

            # Execute workflow
            execute_result = await workflow_service.process_request({
                "action": "execute_workflow",
                "workflow_id": cycle.workflow_id
            })

            cycle.results["execution"] = {
                "executed": execute_result.get("success", False),
                "workflow_id": cycle.workflow_id,
                "execution_details": execute_result
            }
            # --- NUEVO: corroboración automática con herramientas científicas ---
            try:
                tool_result = await self.corroborate_with_tools({"hypothesis_id": cycle.hypothesis.hypothesis_id})
                cycle.results["tool_corroboration"] = tool_result
            except BiologyError as e:  # pragma: no cover (defensivo)
                cycle.results["tool_corroboration"] = {"success": False, "error": str(e)}
        else:
            cycle.results["execution"] = {
                "executed": False,
                "error": "No workflow available for execution"
            }

    async def _analyze_results(self, cycle: ResearchCycle):
        """Analyze experiment results"""
        # Simulate result analysis
        # In real implementation, this would analyze actual workflow results
        tool_support = cycle.results.get("tool_corroboration", {}).get("aggregate", {}) if cycle.results.get("tool_corroboration") else {}
        support_score = tool_support.get("support_score", 0.0)
        weighted_cov = tool_support.get("weighted_coverage", 0.0)
        mean_signal = tool_support.get("mean_signal", 0.0)
        analysis_results = {
            "hypothesis_supported": support_score >= 0.25 or mean_signal >= 0.3,
            "confidence_level": round(min(1.0, cycle.hypothesis.confidence_score), 3),
            "support_score": support_score,
            "weighted_coverage": weighted_cov,
            "mean_signal": mean_signal,
            "key_findings": [
                "Tool corroboration executed",
                f"Support score={support_score}",
                f"Weighted coverage={weighted_cov}",
                f"Mean signal={mean_signal}"
            ],
            "recommendations": [
                "Agregar refinamiento dirigido si support_score < 0.5",
                "Extender rutas de evidencia para dominios críticos",
                "Recalibrar pesos si la diversidad es baja"
            ]
        }

        cycle.results["analysis"] = analysis_results

        # Update hypothesis status
        if analysis_results["hypothesis_supported"]:
            cycle.hypothesis.status = HypothesisStatus.VALIDATED
            cycle.hypothesis.validated_at = datetime.now()
        else:
            cycle.hypothesis.status = HypothesisStatus.REJECTED

        cycle.hypothesis.evidence.append({
            "analysis_type": "experimental_validation",
            "results": analysis_results,
            "timestamp": datetime.now().isoformat()
        })

    async def _refine_hypothesis(self, cycle: ResearchCycle):
        """Refine hypothesis based on results"""
        # Generate refined hypothesis
        refinement = {
            "iteration": cycle.iterations + 1,
            "changes": [
                "Adjusted variable ranges",
                "Added control conditions",
                "Modified assumptions"
            ],
            "improved_confidence": 0.10,
            "timestamp": datetime.now().isoformat()
        }

        cycle.hypothesis.refinement_history.append(refinement)
        cycle.hypothesis.confidence_score += refinement["improved_confidence"]
        cycle.hypothesis.status = HypothesisStatus.REFINED

        cycle.results["refinement"] = refinement

    async def refine_hypothesis(self, request_data: RefineHypothesisResult) -> RefineHypothesisResult:
        """Manually refine a hypothesis"""
        try:
            hypothesis_id = request_data.get("hypothesis_id")
            refinement_data = request_data.get("refinement_data", {})

            if not hypothesis_id or hypothesis_id not in self.active_hypotheses:
                return {
                    "success": False,
                    "error": f"Hypothesis {hypothesis_id} not found"
                }

            hypothesis = self.active_hypotheses[hypothesis_id]

            # Apply refinements
            if "new_variables" in refinement_data:
                hypothesis.variables.extend(refinement_data["new_variables"])

            if "new_assumptions" in refinement_data:
                hypothesis.assumptions.extend(refinement_data["new_assumptions"])

            if "confidence_adjustment" in refinement_data:
                hypothesis.confidence_score += refinement_data["confidence_adjustment"]

            hypothesis.status = HypothesisStatus.REFINED
            hypothesis.refinement_history.append({
                "manual_refinement": True,
                "changes": refinement_data,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "success": True,
                "message": f"Hypothesis '{hypothesis.title}' refined successfully",
                "hypothesis_id": hypothesis_id,
                "new_confidence": hypothesis.confidence_score
            }

        except BiologyError as e:
            return self.handle_error(e, "refine_hypothesis")

    async def analyze_evidence(self, request_data: AnalyzeEvidenceResult) -> AnalyzeEvidenceResult:
        """Analyze evidence for a hypothesis"""
        try:
            hypothesis_id = request_data.get("hypothesis_id")

            if not hypothesis_id or hypothesis_id not in self.active_hypotheses:
                return {
                    "success": False,
                    "error": f"Hypothesis {hypothesis_id} not found"
                }

            hypothesis = self.active_hypotheses[hypothesis_id]

            # Analyze evidence strength
            evidence_analysis = {
                "total_evidence": len(hypothesis.evidence),
                "supporting_evidence": sum(1 for e in hypothesis.evidence if e.get("results", {}).get("hypothesis_supported", False)),
                "contradicting_evidence": sum(1 for e in hypothesis.evidence if not e.get("results", {}).get("hypothesis_supported", True)),
                "average_confidence": sum(e.get("results", {}).get("confidence_level", 0) for e in hypothesis.evidence) / max(len(hypothesis.evidence), 1),
                "literature_support": len(hypothesis.related_papers),
                "refinement_iterations": len(hypothesis.refinement_history)
            }

            # Base evidence strength
            evidence_strength = (
                evidence_analysis["supporting_evidence"] * 0.3 +
                evidence_analysis["average_confidence"] * 0.4 +
                min(evidence_analysis["literature_support"] * 0.1, 0.2) +
                min(evidence_analysis["refinement_iterations"] * 0.1, 0.1)
            )

            # Attempt AI Researcher integration for supplemental qualitative insight
            ai_idea_excerpt = None
            try:
                from app.services.ai_researcher_adapter import AIResearcherAdapterService  # local import
                adapter = AIResearcherAdapterService()
                insight_resp = await adapter.process_request({
                    "action": "generate_ideas",
                    "hypothesis": {"title": hypothesis.title, "description": hypothesis.description}
                })
                if insight_resp.get("success"):
                    ai_idea_excerpt = (insight_resp.get("idea_insight") or "")[:300]
                    # Small qualitative bonus if adapter succeeded
                    evidence_strength += 0.03
            except BiologyError as e:  # noqa
                logger.debug("AI Researcher adapter unavailable: %s", e)

            evidence_strength = min(1.0, evidence_strength)

            # Calibration log (delta confidence vs evidence strength)
            try:
                calib_dir = Path("logs/calibration")
                calib_dir.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(calib_dir / "confidence_correlation.log", "a", encoding="utf-8") as fh:
                    await fh.write(json.dumps({
                        "hypothesis_id": hypothesis_id,
                        "timestamp": datetime.now().isoformat(),
                        "confidence_score": hypothesis.confidence_score,
                        "evidence_strength": evidence_strength,
                        "supporting_evidence": evidence_analysis["supporting_evidence"],
                        "literature_support": evidence_analysis["literature_support"],
                    }) + "\n")
            except BiologyError:
                pass

            return {
                "success": True,
                "hypothesis_id": hypothesis_id,
                "evidence_analysis": evidence_analysis,
                "evidence_strength": evidence_strength,
                "recommendation": "strong" if evidence_strength > 0.7 else "moderate" if evidence_strength > 0.5 else "weak",
                "ai_researcher_idea_excerpt": ai_idea_excerpt,
            }

        except BiologyError as e:
            return self.handle_error(e, "analyze_evidence")

    async def corroborate_with_tools(self, request_data: CorroborateWithToolsResult) -> CorroborateWithToolsResult:
        """Invoca orquestador de herramientas para recolectar evidencia externa."""
        try:
            hypothesis_id = request_data.get("hypothesis_id")
            if not hypothesis_id or hypothesis_id not in self.active_hypotheses:
                return {"success": False, "error": f"Hypothesis {hypothesis_id} not found"}
            hyp = self.active_hypotheses[hypothesis_id]

            from app.services.tool_evidence_orchestrator import ToolEvidenceOrchestratorService
            orchestrator = ToolEvidenceOrchestratorService()
            coro_result = await orchestrator.process_request({
                "action": "corroborate",
                "hypothesis": {
                    "title": hyp.title,
                    "description": hyp.description,
                    "domain": hyp.domain,
                    "variables": hyp.variables,
                    "assumptions": hyp.assumptions,
                    "expected_outcome": hyp.expected_outcome,
                },
                "domain": hyp.domain,
            })
            if coro_result.get("success"):
                agg = coro_result.get("aggregate", {})
                support = agg.get("support_score", 0.0)
                weighted_cov = agg.get("weighted_coverage", agg.get("coverage", 0.0))
                diversity = agg.get("diversity", 0.0)
                # Fórmula: incremento = 0.15*support + 0.1*weighted_cov + 0.05*diversity
                delta = 0.15 * support + 0.10 * weighted_cov + 0.05 * diversity
                hyp.confidence_score = min(1.0, hyp.confidence_score + delta)
                hyp.evidence.append({
                    "analysis_type": "tool_corroboration",
                    "results": coro_result,
                    "timestamp": datetime.now().isoformat()
                })
            return coro_result | {"hypothesis_id": hypothesis_id, "new_confidence": hyp.confidence_score}
        except BiologyError as e:
            return self.handle_error(e, "corroborate_with_tools")

    def get_hypothesis(self, request_data: GetHypothesisResult) -> GetHypothesisResult:
        """Get hypothesis details"""
        try:
            hypothesis_id = request_data.get("hypothesis_id")

            if not hypothesis_id or hypothesis_id not in self.active_hypotheses:
                return {
                    "success": False,
                    "error": f"Hypothesis {hypothesis_id} not found"
                }

            hypothesis = self.active_hypotheses[hypothesis_id]

            return {
                "success": True,
                "hypothesis": {
                    "hypothesis_id": hypothesis.hypothesis_id,
                    "title": hypothesis.title,
                    "description": hypothesis.description,
                    "domain": hypothesis.domain,
                    "variables": hypothesis.variables,
                    "assumptions": hypothesis.assumptions,
                    "expected_outcome": hypothesis.expected_outcome,
                    "confidence_score": hypothesis.confidence_score,
                    "status": hypothesis.status.value,
                    "created_at": hypothesis.created_at.isoformat(),
                    "evidence_count": len(hypothesis.evidence),
                    "related_papers_count": len(hypothesis.related_papers),
                    "refinement_count": len(hypothesis.refinement_history)
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "get_hypothesis")

    def list_hypotheses(self, request_data: ListHypothesesResult) -> ListHypothesesResult:
        """List hypotheses with optional filtering"""
        try:
            domain = request_data.get("domain")
            status = request_data.get("status")
            min_confidence = request_data.get("min_confidence", 0.0)

            hypotheses = []
            for h_id, hypothesis in self.active_hypotheses.items():
                # Apply filters
                if domain and hypothesis.domain != domain:
                    continue
                if status and hypothesis.status.value != status:
                    continue
                if hypothesis.confidence_score < min_confidence:
                    continue

                hypotheses.append({
                    "hypothesis_id": h_id,
                    "title": hypothesis.title,
                    "domain": hypothesis.domain,
                    "status": hypothesis.status.value,
                    "confidence_score": hypothesis.confidence_score,
                    "created_at": hypothesis.created_at.isoformat(),
                    "evidence_count": len(hypothesis.evidence)
                })

            return {
                "success": True,
                "hypotheses": hypotheses,
                "total_count": len(hypotheses),
                "filters_applied": {
                    "domain": domain,
                    "status": status,
                    "min_confidence": min_confidence
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "list_hypotheses")
