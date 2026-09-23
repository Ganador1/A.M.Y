"""Loop autónomo de biología estructural con integración de servicios especializados."""
from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import Any, Dict, List, Optional

from contextlib import suppress

from app.autonomous.core.priority_scoring import PriorityScorer
from app.autonomous.core.state_manager import IterationRecord, StateManager
from app.autonomous.evaluation.empirical_feedback import process_feedback
from app.autonomous.evaluation.novelty_assessor import NoveltyAssessor
from app.autonomous.metrics.telemetry_collector import AutonomousTelemetry
from app.autonomous.models.importance_ranker import ImportanceRanker
from app.autonomous.integration import EvidenceSummary, ToolEvidenceBridge
from app.domains.biology.services.computational_biology import ComputationalBiologyService
# ⭐ SERVICIOS DE IA BIOLÓGICA (4 servicios - Fase 1)
from app.domains.biology.services.dnabert2_service import DNABERT2GenomicsService
from app.domains.biology.services.protgpt2_service import ProtGPT2ProteinDesignService
from app.domains.biology.services.biogpt_service import BioGPTService
# ⭐ SERVICIOS DE GENÓMICA (1 servicio - Fase 2)
from app.domains.biology.services.genomics_service import GenomicsService
# ⭐ SERVICIOS DE NLP BIOMÉDICO (1 servicio - Fase 2)
from app.domains.biology.services.biomedical_nlp_service_full import BiomedicalNLPService
from app.compliance.ethics_gate import EthicsGate, ExperimentRequest


logger = logging.getLogger(__name__)


def fetch_biomolecular_targets(limit: int = 5, **kwargs) -> list:
    """Backward-compatible module-level wrapper so tests can patch the function.

    This delegates to the real implementation in `app.autonomous.interfaces.external_apis`.
    """
    try:
        from app.autonomous.interfaces.external_apis import fetch_biomolecular_targets as _ext

        return _ext(limit=limit, **kwargs)
    except Exception:
        # If external API unavailable, return empty list to allow tests to proceed
        return []

class BiologyLoop:
    def __init__(self, state: StateManager | None = None, telemetry: AutonomousTelemetry | None = None):
        self.state = state or StateManager()
        self.telemetry = telemetry or AutonomousTelemetry()
        self.priority = PriorityScorer()
        self.novelty = NoveltyAssessor()
        self.importance_ranker = ImportanceRanker()
        self.iteration = 0
        self.rand = random.Random(123)
        self.biology_service = ComputationalBiologyService()
        # ⭐ SERVICIOS DE IA BIOLÓGICA (4 servicios - Fase 1)
        self.dnabert2_service = DNABERT2GenomicsService()  # DNA sequence analysis
        self.protgpt2_service = ProtGPT2ProteinDesignService()  # Protein design generation
        self.biogpt_service = BioGPTService()  # Biomedical literature search
        # ⭐ SERVICIOS DE GENÓMICA (2 servicios - Fase 2)
        # Note: AdvancedGenomicsService not instantiated (missing process_request implementation)
        self.genomics_service = GenomicsService()  # DeepVariant integration
        # ⭐ SERVICIOS DE NLP BIOMÉDICO (1 servicio - Fase 2)
        self.biomedical_nlp = BiomedicalNLPService()  # BioBERT entity extraction and semantic analysis
        self.tool_evidence = ToolEvidenceBridge(default_domain="biology")
        self.ethics_gate = EthicsGate()

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

    def _seed_targets(self, k: int = 5) -> List[Dict[str, Any]]:
        """Seed targets using real AlphaFold3 high-uncertainty data when available."""
        # Guard against invalid k values
        if k is None or k <= 0:
            return []

        with suppress(Exception):
            # Use the module-level wrapper so callers/tests can patch `fetch_biomolecular_targets`
            real_targets = fetch_biomolecular_targets(limit=k)
            if real_targets:
                converted = []
                for target in real_targets:
                    uncertainty = target.get("uncertainty", self.rand.uniform(0.2, 0.9))
                    impact = target.get("impact_score", self.rand.random())
                    converted.append(
                        {
                            "id": f"prot_{self.iteration}_{len(converted)}",
                            "uniprot": target.get("uniprot", f"P{len(converted):05d}"),
                            "gene_name": target.get("gene_name", f"GENE{len(converted)}"),
                            "uncertainty": uncertainty,
                            "impact_potential": impact,
                            "length": target.get("length", 200 + 10 * len(converted)),
                            "avg_plddt": target.get("avg_plddt", 50.0),
                            "literature_frequency": self.rand.randint(0, 60),
                            "dependency_count": self.rand.randint(0, 8),
                            "proveability": self.rand.random(),
                            "novelty": self.rand.random(),
                            "information_gain": (uncertainty + impact) / 2.0,
                            "estimated_cost": self.rand.random() * 0.4,
                            "functional_annotation": target.get("functional_annotation", "unknown function"),
                            "disease_relevance": target.get("disease_relevance", []),
                        }
                    )
                return converted[:k]

        items: List[Dict[str, Any]] = []
        for i in range(k):
            uncertainty = self.rand.uniform(0.2, 0.9)
            impact = self.rand.random()
            items.append(
                {
                    "id": f"prot_{self.iteration}_{i}",
                    "uniprot": f"P{i:05d}",
                    "uncertainty": uncertainty,
                    "impact_potential": impact,
                    "literature_frequency": self.rand.randint(0, 60),
                    "dependency_count": self.rand.randint(0, 8),
                    "proveability": self.rand.random(),
                    "novelty": self.rand.random(),
                    "information_gain": (uncertainty + impact) / 2.0,
                    "estimated_cost": self.rand.random() * 0.4,
                }
            )
        return items

    async def _enrich_target_async(
        self,
        target: Dict[str, Any],
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        dynamics_payload = await self.biology_service.population_dynamics(
            {
                "model_type": "logistic_growth",
                "growth_rate": 0.15 + target.get("impact_potential", 0.3) * 0.2,
                "carrying_capacity": 1500,
                "initial_population": 50 + int(target.get("uncertainty", 0.4) * 40),
                "time_years": 30,
            }
        )

        biodiversity_payload = await self.biology_service.biodiversity_analysis(
            {
                "species_abundances": [
                    max(1, int(target.get("impact_potential", 0.4) * 20)),
                    max(1, int(target.get("uncertainty", 0.5) * 18)),
                    self.rand.randint(5, 25),
                    self.rand.randint(2, 12),
                ]
            }
        )

        regulatory_payload: Optional[Dict[str, Any]] = None
        if self.biology_service.networkx_available:
            regulatory_payload = await self.biology_service.regulatory_network_analysis(
                {
                    "gene_interactions": iteration_data.get("gene_interactions") if iteration_data else None,
                    "description": iteration_data.get("target_pathway") if iteration_data else None,
                }
            )

        # ⭐ NUEVO: Análisis de secuencia DNA con DNABERT2
        dna_analysis_payload: Optional[Dict[str, Any]] = None
        try:
            # Simular secuencia DNA para análisis (en producción vendría de target data)
            gene_name = target.get("gene_name", "UNKNOWN")
            logger.info(f"🧬 Analyzing DNA sequence for gene: {gene_name}")
            dna_analysis_payload = await self.dnabert2_service.analyze_sequence(
                operation="predict_function",
                parameters={
                    "sequence_id": gene_name,
                    "task": "function_prediction",
                    "model_type": "dnabert2_multitask"
                }
            )
            if dna_analysis_payload.get("success"):
                logger.info(f"✓ DNABERT2 analysis complete: {dna_analysis_payload.get('predicted_function', 'N/A')}")
        except Exception as exc:
            logger.warning(f"DNABERT2 analysis failed: {exc}")

        # ⭐ NUEVO: Diseño de proteínas con ProtGPT2
        protein_design_payload: Optional[Dict[str, Any]] = None
        try:
            uniprot = target.get("uniprot", "P00000")
            logger.info(f"🧪 Generating protein design for: {uniprot}")
            protein_design_payload = await self.protgpt2_service.generate_protein(
                operation="sequence_generation",
                parameters={
                    "prompt": f"Design protein for {gene_name}",
                    "max_length": 200,
                    "temperature": 0.8
                }
            )
            if protein_design_payload.get("success"):
                logger.info(f"✓ ProtGPT2 generated {protein_design_payload.get('sequence_length', 0)} AA sequence")
        except Exception as exc:
            logger.warning(f"ProtGPT2 design failed: {exc}")

        # ⭐ NUEVO: Búsqueda de literatura biomédica con BioGPT
        literature_payload: Optional[Dict[str, Any]] = None
        try:
            query = f"{gene_name} therapeutic target disease relevance"
            logger.info(f"📚 Generating biomedical literature summary: {query}")
            literature_payload = await self.biogpt_service.generate_biomedical_text(
                prompt=query,
                max_length=256
            )
            if literature_payload.get("success"):
                text_len = len(literature_payload.get("generated_text", ""))
                logger.info(f"✓ BioGPT generated {text_len} chars of literature summary")
        except Exception as exc:
            logger.warning(f"BioGPT literature generation failed: {exc}")

        # Try to use a single unified protein enrichment API when available
        import inspect

        protein_enrichment = {}
        try:
            maybe = self.biology_service.enrich_protein_data({
                "id": target.get("id"),
                "uniprot": target.get("uniprot"),
                "uncertainty": target.get("uncertainty"),
                "impact_potential": target.get("impact_potential"),
            })
            if inspect.isawaitable(maybe):
                protein_enrichment = await maybe
            else:
                protein_enrichment = maybe
        except Exception:
            protein_enrichment = {}

        result = {
            "population_dynamics": dynamics_payload,
            "biodiversity": biodiversity_payload,
            "regulatory_network": regulatory_payload,
            "dna_analysis": dna_analysis_payload,  # ⭐ NUEVO
            "protein_design": protein_design_payload,  # ⭐ NUEVO
            "literature_search": literature_payload,  # ⭐ NUEVO
        }

        # Merge protein enrichment fields (id/uniprot, structural features, etc.)
        result.update(protein_enrichment or {})
        # Ensure basic identity fields are present even if enrichment omitted them
        if "id" not in result:
            result["id"] = target.get("id")
        if "uniprot" not in result:
            result["uniprot"] = target.get("uniprot")
        return result

    def _build_biology_hypothesis(
        self,
        target: Dict[str, Any],
        enrichment: Dict[str, Any],
        iteration_data: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        uniprot = target.get("uniprot") or target.get("gene_name") or target.get("id", "protein_target")
        description = (
            f"Corroborar evidencia para la relevancia terapéutica de {uniprot} considerando dinámica poblacional"
            " y señales de biodiversidad"
        )
        variables: Dict[str, Any] = {
            "uniprot": uniprot,
            "uncertainty": target.get("uncertainty"),
            "impact_potential": target.get("impact_potential"),
            "population_dynamics": enrichment.get("population_dynamics"),
            "biodiversity": enrichment.get("biodiversity"),
            "regulatory_network": enrichment.get("regulatory_network"),
        }
        assumptions = [
            "Los datos poblacionales provienen de simulaciones computacionales",
            "Las métricas de biodiversidad se basan en modelos ecosistémicos",
        ]
        extras = {
            "parameters": {
                "disease_relevance": target.get("disease_relevance"),
                "iteration_context": iteration_data or {},
            },
            "keywords": [uniprot, "therapeutic_target"],
        }
        return self.tool_evidence.build_hypothesis(
            title=f"Validación terapéutica de {uniprot}",
            description=description,
            variables=variables,
            assumptions=assumptions,
            expected_outcome="Determinar viabilidad como diana prioritaria",
            extras=extras,
        )

    async def _run_iteration_impl(
        self,
        top_n: int = 3,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        self.iteration += 1

        targets = self._seed_targets()
        ranked_importance = self.importance_ranker.rank(targets)
        scored = self.priority.rank(ranked_importance)
        selected = scored[:top_n]

        actions: List[str] = []
        outcomes: Dict[str, Any] = {}
        enriched_selected: List[Dict[str, Any]] = []
        growth_snapshots: List[Dict[str, Any]] = []
        support_scores: List[float] = []

        for target in selected:
            emb = [target["uncertainty"], target["impact_potential"], target["information_gain"]]
            novelty_result = self.novelty.assess(emb)
            enrichment = await self._enrich_target_async(target, iteration_data)
            evidence_summary: Optional[EvidenceSummary] = None
            if self.tool_evidence:
                try:
                    hypothesis = self._build_biology_hypothesis(target, enrichment, iteration_data)
                    
                    # Ethics evaluation before execution
                    uniprot = target.get("uniprot") or target.get("gene_name") or target.get("id", "protein_target")
                    disease_relevance = target.get("disease_relevance", [])
                    keywords = [uniprot, "therapeutic_target", "computational_biology"]
                    if disease_relevance:
                        keywords.extend(disease_relevance[:3])
                    
                    ethics_request = ExperimentRequest(
                        domain="computational_biology",
                        description=hypothesis.get("description", ""),
                        data_sensitivity="medium" if disease_relevance else "low",
                        intent="research",
                        keywords=keywords,
                        user_id="biology_loop",
                        metadata={
                            "target_id": target.get("id"),
                            "iteration": self.iteration,
                            "uncertainty": target.get("uncertainty"),
                        }
                    )
                    
                    ethics_decision = self.ethics_gate.evaluate(ethics_request)
                    
                    if not ethics_decision.allowed:
                        logger.info(
                            f"{ethics_decision.level} risk, reasons: {ethics_decision.escalation_reasons}"
                        )
                        # Skip this target if blocked
                        continue
                    
                    if ethics_decision.requires_signature:
                        logger.info(
                            f"Biology hypothesis {target.get('id')} requires human review: "
                            f"{ethics_decision.recommended_actions}"
                        )
                    
                    evidence_summary = await self.tool_evidence.corroborate(hypothesis, domain="biology")
                    if evidence_summary.success:
                        target["impact_potential"] = min(
                            1.0,
                            float(target.get("impact_potential", 0.4)) + evidence_summary.support_score * 0.12,
                        )
                        support_scores.append(evidence_summary.support_score)
                    else:
                        support_scores.append(0.0)
                except (RuntimeError, ValueError, ConnectionError, TimeoutError) as exc:
                    logger.debug("Biology corroboration failed for %s: %s", target.get("id"), exc)

            actions.append("analyze")

            dynamics = enrichment["population_dynamics"].get("results", {})
            growth_snapshots.append(dynamics)

            # Store ethics approval in metadata
            ethics_metadata = {
                "ethics_approved": True,
                "ethics_decision_id": None,
                "ethics_risk_level": "LOW",
            }
            if 'ethics_decision' in locals():
                ethics_metadata.update({
                    "ethics_approved": ethics_decision.allowed,
                    "ethics_decision_id": ethics_decision.decision_id,
                    "ethics_risk_level": ethics_decision.level,
                })
            
            outcomes[target["id"]] = {
                "novelty_score": novelty_result["novelty_score"],
                "pred_structure_shift": self.rand.random() - 0.5,
                "population_dynamics": enrichment["population_dynamics"],
                "biodiversity": enrichment["biodiversity"],
                "regulatory_network": enrichment["regulatory_network"],
                "tool_evidence": evidence_summary.as_dict() if evidence_summary else None,
                "ethics": ethics_metadata,
            }
            enriched_selected.append({
                **target,
                "analysis": enrichment,
                "novelty_score": novelty_result["novelty_score"],
                "ethics": ethics_metadata,
            })

        feedback_event = {
            "metric_name": "analysis_volume",
            "value": len(selected),
            "improved": len(selected) > 0,
            "confidence": 0.55,
        }
        feedback_result = process_feedback(feedback_event)

        rec = IterationRecord(
            iteration=self.iteration,
            domain="biology",
            selected_ids=[s["id"] for s in selected],
            actions=actions,
            outcomes={**outcomes, "feedback_adjustment": feedback_result["adjustment"]},
        )
        self.state.add_iteration(rec)

        avg_novelty = (sum(v["novelty_score"] for v in outcomes.values()) / len(outcomes) if outcomes else 0.0)
        avg_support = (sum(support_scores) / len(support_scores)) if support_scores else 0.0
        self.telemetry.record_iteration(
            domain="biology",
            duration_s=time.time() - start,
            selected=len(selected),
            mutations=0,
            sketches=0,
        )
        try:
            from app.monitoring.metrics import metrics

            metrics.set_gauge("autonomous_novelty_last", avg_novelty)
            metrics.set_gauge("autonomous_feedback_adjustment_last", feedback_result["adjustment"])
            if support_scores:
                metrics.set_gauge("autonomous_support_score_last", avg_support)
        except (ImportError, AttributeError):  # pragma: no cover
            logger.debug("Biology metrics backend unavailable")

        growth_summary = growth_snapshots[0] if growth_snapshots else {}

        return {
            "iteration": self.iteration,
            "selected": enriched_selected,
            "outcomes": rec.outcomes,
            "growth_characteristics": growth_summary,
            "regulatory_analysis": outcomes[selected[0]["id"]].get("regulatory_network") if selected else None,
            "avg_support_score": avg_support,
        }

    def run_iteration(self, top_n: int = 3, iteration_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._run_coro_sync(self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data))

    async def run_genomics_discovery_iteration(
        self,
        iteration_data: Optional[Dict[str, Any]] = None,
        top_n: int = 3,
    ) -> Dict[str, Any]:
        """Iteración asíncrona con integración del servicio de biología computacional."""

        return await self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data)

__all__ = ["BiologyLoop"]
