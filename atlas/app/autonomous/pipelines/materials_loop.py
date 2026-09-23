"""Materials exploration loop with integration to MaterialsDiscoveryService."""
from __future__ import annotations

import asyncio
import time
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Optional

from app.autonomous.core.budget_allocator import BudgetAllocator
from app.autonomous.core.priority_scoring import PriorityScorer
from app.autonomous.core.state_manager import IterationRecord, StateManager
from app.autonomous.core.task_scheduler import TaskScheduler
from app.autonomous.evaluation.empirical_feedback import process_feedback
from app.autonomous.evaluation.novelty_assessor import NoveltyAssessor
from app.autonomous.metrics.telemetry_collector import telemetry
from app.autonomous.interfaces.external_apis import fetch_material_candidates
from app.autonomous.integration import EvidenceSummary, ToolEvidenceBridge
from app.core.bootstrap_logging import logger
from app.domains.chemistry.services.materials_discovery_service import (
    MaterialCandidate,
    MaterialsDiscoveryService,
)
from app.domains.chemistry.services.gnome_materials_service import GNOMEMaterialsService  # ⭐ GNOME - 381K+ materiales
from app.domains.chemistry.services.chemml_service import ChemMLService  # ⭐ ML predictions
# ⭐ SERVICIOS DE CARACTERIZACIÓN EXPERIMENTAL (3 servicios)
from app.domains.chemistry.services.advanced_nmr_service import AdvancedNMRService
from app.domains.chemistry.services.advanced_spectrometers import AdvancedSpectrometers
from app.domains.chemistry.services.differential_scanning_calorimetry_service import DifferentialScanningCalorimetryService
from app.exceptions.domain.biology import BiologyError


MaterialsCandidateProvider = Callable[[], List[Dict[str, Any]]]


class MaterialsLoop:
    def __init__(
        self,
        provider: MaterialsCandidateProvider | None = None,
        state: StateManager | None = None,
    ):
        self.provider = provider
        self.state = state or StateManager()
        self.scorer = PriorityScorer()
        self.scheduler = TaskScheduler(diversity_quota=6)
        self.budget = BudgetAllocator(total_budget=9.0)
        self.novelty = NoveltyAssessor()
        self.materials_service = MaterialsDiscoveryService()
        self.gnome_service = GNOMEMaterialsService()  # ⭐ GNOME - 381K+ materiales reales
        self.chemml_service = ChemMLService()  # ⭐ ML para predicciones
        # ⭐ SERVICIOS DE CARACTERIZACIÓN EXPERIMENTAL (3 servicios)
        self.nmr_service = AdvancedNMRService()  # NMR spectroscopy
        self.spectrometers = AdvancedSpectrometers()  # Advanced spectrometry
        self.dsc_service = DifferentialScanningCalorimetryService()  # Differential scanning calorimetry
        self.tool_evidence = ToolEvidenceBridge(default_domain="materials_science")

    @staticmethod
    def _run_coro_sync(coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    async def _default_provider_async(
        self,
        limit: int,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        application = None
        formula_hint = None
        if iteration_data:
            application = iteration_data.get("target_application") or iteration_data.get("material_class")
            experimental = iteration_data.get("experimental_data")
            if isinstance(experimental, dict):
                formula_hint = (
                    experimental.get("formula")
                    or experimental.get("composition")
                    or experimental.get("material")
                )

        # ⭐ NUEVO: Buscar primero en GNOME (381K+ materiales reales)
        gnome_candidates: List[Dict[str, Any]] = []
        try:
            target_app = application or "solar_cell"
            logger.info(f"🔍 Materials Loop searching GNOME for {target_app} (381K+ available)...")
            gnome_results = await self.gnome_service.search_materials(
                application=target_app,
                max_results=limit * 3,
                filters={
                    "formation_energy_max": -0.5,
                    "band_gap_min": 0.1,
                    "stability_min": 0.7
                }
            )
            
            # Enriquecer con ML
            for material in gnome_results[:limit * 2]:
                formula = material.get("formula", "")
                if formula:
                    try:
                        ml_props = await self.chemml_service.predict_properties(
                            composition=formula,
                            properties=["band_gap", "formation_energy", "elastic_modulus", "thermal_conductivity"]
                        )
                        material["ml_predictions"] = ml_props
                        material["ml_confidence"] = ml_props.get("confidence", 0.5)
                        gnome_candidates.append(material)
                        logger.debug(f"✓ GNOME {formula}: ML confidence={ml_props.get('confidence', 0):.2f}")
                    except Exception as ml_exc:
                        logger.debug(f"ChemML failed for {formula}: {ml_exc}")
                        gnome_candidates.append(material)
            
            if gnome_candidates:
                logger.info(f"✅ Found {len(gnome_candidates)} GNOME materials for Materials Loop")
        except Exception as gnome_exc:
            logger.debug(f"GNOME search failed: {gnome_exc}")

        # Fallback: MaterialsDiscoveryService tradicional
        candidates: List[MaterialCandidate] = []
        try:
            candidates = await self.materials_service.discover_materials_for_application(
                application or "solar_cell",
                max_candidates=limit,
            )
        except (RuntimeError, ValueError) as exc:
            logger.debug("Materials service discovery fallback (%s): %s", application, exc)

        # Combinar GNOME + MaterialsService
        processed: List[Dict[str, Any]] = []
        
        # Procesar GNOME candidates primero (tienen prioridad)
        for idx, material in enumerate(gnome_candidates[:limit]):
            formula = material.get("formula", f"GNOME_{idx}")
            suitability = material.get("suitability_score", 0.8)  # GNOME suele tener scores altos
            ml_predictions = material.get("ml_predictions", {})
            
            processed.append(
                {
                    "id": f"mat_gnome_{idx}",
                    "formula": formula,
                    "embedding": [
                        float(material.get("band_gap", 1.2)),
                        float(material.get("stability_score", 0.8)),
                        float(material.get("thermal_conductivity", 5.0)),
                    ],
                    "literature_frequency": int(40 + suitability * 60),  # GNOME materiales bien documentados
                    "dependency_count": max(0, 3 - int(suitability * 2)),
                    "impact_potential": float(min(1.0, 0.6 + suitability * 0.3)),
                    "proveability": float(min(1.0, 0.7 + suitability / 2)),
                    "novelty": float(max(0.1, 1.0 - suitability + 0.15)),
                    "information_gain": float(min(1.0, 0.6 + suitability / 2)),
                    "estimated_cost": float(max(0.05, 0.25 - suitability * 0.1)),
                    "suitability": float(suitability),
                    "materials_properties": ml_predictions,  # ⭐ ML predictions
                    "target_application": material.get("target_application", application or "solar_cell"),
                    "data_source": "gnome_ml",  # ⭐ Identificar fuente
                }
            )
        
        # Agregar MaterialsService candidates si hay espacio
        for idx, candidate in enumerate(candidates[:max(0, limit - len(processed))]):
            composition = getattr(candidate, "composition", None)
            formula = getattr(composition, "formula", None) if composition else None
            suitability = getattr(candidate, "suitability_score", 0.5) or 0.5
            properties = getattr(candidate, "properties", None)
            props_dict = asdict(properties) if properties and hasattr(properties, "__dict__") else {}
            processed.append(
                {
                    "id": f"mat_{idx}",
                    "formula": formula or f"MAT_{idx}",
                    "embedding": [
                        float(props_dict.get("band_gap", 1.2) or 1.2),
                        float(props_dict.get("stability_score", 0.6) or 0.6),
                        float(props_dict.get("thermal_conductivity", 5.0) or 5.0),
                    ],
                    "literature_frequency": int(20 + suitability * 50),
                    "dependency_count": max(0, 5 - int(suitability * 4)),
                    "impact_potential": float(min(1.0, 0.4 + suitability)),
                    "proveability": float(min(1.0, 0.5 + suitability / 2)),
                    "novelty": float(max(0.1, 1.0 - suitability + 0.1)),
                    "information_gain": float(min(1.0, 0.5 + suitability / 2)),
                    "estimated_cost": float(max(0.05, 0.35 - suitability * 0.2)),
                    "suitability": float(suitability),
                    "materials_properties": props_dict,
                    "target_application": getattr(candidate, "target_application", application or "solar_cell"),
                    "data_source": getattr(candidate, "discovery_method", "atlas_internal"),
                }
            )

        remaining_slots = max(0, limit - len(processed))
        query = formula_hint or application or "solar_cell"

        if remaining_slots > 0 and query:
            try:
                external_materials = await fetch_material_candidates(query, limit)
            except BiologyError as exc:  # noqa: BLE001
                logger.debug("External materials fetch failed for %s: %s", query, exc)
                external_materials = []
            for ext_idx, material in enumerate(external_materials):
                if len(processed) >= limit:
                    break
                stability = float(material.get("predicted_stability", 0.6) or 0.6)
                band_gap = float(material.get("band_gap", 1.4) or 1.4)
                formation = float(material.get("formation_energy", -0.3) or -0.3)
                processed.append(
                    {
                        "id": material.get("material_id") or f"mat_ext_{ext_idx}",
                        "formula": material.get("formula") or f"MAT_EXT_{ext_idx}",
                        "embedding": [band_gap, stability, abs(formation)],
                        "literature_frequency": int(material.get("literature_mentions", 18)),
                        "dependency_count": max(0, 4 - int(stability * 3)),
                        "impact_potential": float(min(1.0, 0.35 + stability * 0.6)),
                        "proveability": float(min(1.0, 0.45 + stability * 0.4)),
                        "novelty": float(max(0.15, 1.0 - stability + 0.05)),
                        "information_gain": float(min(1.0, 0.45 + stability / 1.5)),
                        "estimated_cost": float(max(0.05, 0.28 - stability * 0.1)),
                        "suitability": float(stability),
                        "materials_properties": {
                            "formation_energy": formation,
                            "band_gap": band_gap,
                            "elasticity_modulus": material.get("elasticity_modulus"),
                            "hardness": material.get("hardness"),
                            "source": material.get("source", "materials_project"),
                        },
                        "target_application": material.get("target_application") or application or "solar_cell",
                        "data_source": material.get("source", "materials_project"),
                    }
                )

        if len(processed) < limit:
            fallback_formula = formula_hint or application or "Fallback"
            for idx in range(len(processed), limit):
                suitability = 0.45 + 0.05 * (idx % 3)
                processed.append(
                    {
                        "id": f"mat_fallback_{idx}",
                        "formula": f"{fallback_formula}_{idx}",
                        "embedding": [1.1 + 0.1 * (idx % 4), suitability, 4.5 + idx * 0.2],
                        "literature_frequency": 12 + idx,
                        "dependency_count": 3 - (idx % 3),
                        "impact_potential": float(min(1.0, 0.3 + suitability)),
                        "proveability": float(min(1.0, 0.4 + suitability / 1.5)),
                        "novelty": float(max(0.2, 0.8 - suitability / 2)),
                        "information_gain": float(min(1.0, 0.4 + suitability / 1.4)),
                        "estimated_cost": float(max(0.05, 0.32 - suitability * 0.18)),
                        "suitability": float(suitability),
                        "materials_properties": {
                            "band_gap": 1.1 + 0.1 * (idx % 4),
                            "stability_score": suitability,
                            "thermal_conductivity": 4.5 + idx * 0.2,
                            "source": "synthetic_fallback",
                        },
                        "target_application": application or "solar_cell",
                        "data_source": "synthetic_fallback",
                    }
                )

        return processed

    def _build_materials_hypothesis(
        self,
        candidate: Dict[str, Any],
        properties: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        formula = candidate.get("formula") or candidate.get("id", "material_candidate")
        application = candidate.get("target_application") or "materials_science"
        description = (
            f"Evaluar si {formula} mantiene propiedades favorables para {application} bajo condiciones operativas"
        )
        variables: Dict[str, Any] = {
            "formula": formula,
            "target_application": application,
            "embedding": candidate.get("embedding"),
            "materials_properties": properties or candidate.get("materials_properties"),
            "suitability": candidate.get("suitability"),
        }
        assumptions = [
            "Las propiedades iniciales provienen de MaterialsDiscoveryService",
            "Las simulaciones se ejecutan en atmósfera controlada",
        ]
        extras = {
            "parameters": {
                "estimated_cost": candidate.get("estimated_cost"),
                "temperature_window": [280, 360],
            },
            # Enriquecer keywords para mejorar evidencia externa (Materials Project / literatura)
            "keywords": [
                application,
                formula,
                "materials_science",
                "band_gap",
                "formation_energy",
                "stability",
            ],
        }
        return self.tool_evidence.build_hypothesis(
            title=f"Validación de {formula} para {application}",
            description=description,
            variables=variables,
            assumptions=assumptions,
            expected_outcome=f"Optimizar el desempeño de {application}",
            extras=extras,
        )

    async def _evaluate_candidate_async(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        composition = candidate.get("formula", "")
        stability = await self.materials_service.analyze_stability(composition)
        properties = candidate.get("materials_properties")
        if not properties:
            try:
                predicted = await self.materials_service.predict_material_properties(composition)
                properties = asdict(predicted) if hasattr(predicted, "__dict__") else predicted
            except (RuntimeError, ValueError, LookupError) as exc:  # pragma: no cover - fallback
                properties = {"error": str(exc)}

        evidence_summary: Optional[EvidenceSummary] = None
        if self.tool_evidence:
            try:
                hypothesis = self._build_materials_hypothesis(candidate, properties if isinstance(properties, dict) else None)
                evidence_summary = await self.tool_evidence.corroborate(hypothesis)
                if evidence_summary.success:
                    candidate["evidence_support_score"] = evidence_summary.support_score
                    candidate["impact_potential"] = min(
                        1.0,
                        float(candidate.get("impact_potential", 0.3)) + evidence_summary.support_score * 0.1,
                    )
                else:
                    # Fallback: si análisis interno de estabilidad no falló, asignar soporte mínimo
                    if isinstance(properties, dict) and not properties.get("error"):
                        candidate["evidence_support_score"] = max(0.05, float(candidate.get("evidence_support_score", 0.0)))
                    else:
                        candidate.setdefault("evidence_support_score", 0.0)
            except BiologyError as exc:  # noqa: BLE001
                logger.debug("Material candidate corroboration failed: %s", exc)

        return {
            "stability": stability,
            "properties": properties,
            "tool_evidence": evidence_summary.as_dict() if evidence_summary else None,
        }

    async def _run_iteration_impl(
        self,
        iteration: int,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        limit = max(5, iteration_data.get("candidate_count", 8) if iteration_data else 8)

        candidates: List[Dict[str, Any]] = []
        if self.provider:
            candidates = self.provider()

        if not candidates:
            candidates = await self._default_provider_async(limit, iteration_data)

        if not candidates:
            logger.warning("No materials candidates available")
            return {"success": False, "reason": "no_candidates"}

        novelty_scores: List[float] = []
        for cand in candidates:
            emb = cand.get("embedding") or []
            score = self.novelty.assess(emb)["novelty_score"]
            cand["novelty_score"] = score
            novelty_scores.append(score)

        ranked = self.scorer.rank(candidates)
        scheduled = self.scheduler.select(ranked, limit=min(5, len(ranked)))
        allocated = self.budget.allocate(scheduled)

        mutations = [
            {"parent": a.get("id", "?"), "type": "element_substitution", "detail": "X->Y"}
            for a in allocated
        ]

        feedback_event = {
            "metric_name": "mutation_volume",
            "value": len(mutations),
            "improved": len(mutations) > 0,
            "confidence": 0.5,
        }
        feedback_result = process_feedback(feedback_event)

        enriched_allocated: List[Dict[str, Any]] = []
        outcomes: Dict[str, Any] = {}
        support_scores: List[float] = []
        for cand in allocated:
            evaluation = await self._evaluate_candidate_async(cand)
            enriched = {**cand, "evaluation": evaluation}
            enriched_allocated.append(enriched)
            evidence_info = evaluation.get("tool_evidence") or {}
            if evidence_info.get("success"):
                support_scores.append(float(evidence_info.get("support_score", 0.0)))
            elif cand.get("evidence_support_score", 0.0) > 0:
                # Include fallback score in the average if available
                val = cand.get("evidence_support_score", 0.0)
                if val is not None:
                    support_scores.append(float(val))
            
            outcomes[cand.get("id", "?")] = {
                "mutation": "element_substitution",
                "evaluation": evaluation,
            }

        record = IterationRecord(
            iteration=iteration,
            domain="materials",
            selected_ids=[c.get("id", "?") for c in allocated],
            actions=["element_substitution"],
            outcomes={**outcomes, "feedback_adjustment": feedback_result["adjustment"]},
        )
        self.state.add_iteration(record)

        duration = time.time() - start
        avg_novelty = sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0.0
        avg_support = sum(support_scores) / len(support_scores) if support_scores else 0.0
        summary = {
            "iteration": iteration,
            "duration_s": duration,
            "selected": len(allocated),
            "mutations": len(mutations),
            "sketches": 0,
            "avg_novelty": avg_novelty,
            "feedback_adjustment": feedback_result["adjustment"],
            "avg_support_score": avg_support,
        }

        try:
            telemetry.record_iteration(
                domain="materials",
                duration_s=duration,
                selected=len(allocated),
                mutations=len(mutations),
                sketches=0,
            )
        except (ValueError, RuntimeError) as exc:
            logger.warning("Telemetry recording failed (materials): %s", exc)
        try:
            from app.monitoring.metrics import metrics

            metrics.set_gauge("autonomous_novelty_last", float(avg_novelty))
            metrics.set_gauge("autonomous_feedback_adjustment_last", feedback_result["adjustment"])
            metrics.set_gauge("autonomous_support_score_last", float(avg_support))
        except (ImportError, AttributeError):  # pragma: no cover
            logger.debug("Could not set materials novelty gauge")

        logger.info("Materials loop iteration %d: %s", iteration, summary)
        return {
            "success": True,
            "summary": summary,
            "mutations": mutations,
            "selected": enriched_allocated,
            "predictions": outcomes,
        }

    def run_iteration(self, iteration: int, iteration_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._run_coro_sync(self._run_iteration_impl(iteration=iteration, iteration_data=iteration_data))

    async def run_materials_discovery_iteration(
        self,
        iteration_data: Optional[Dict[str, Any]] = None,
        iteration: int = 1,
    ) -> Dict[str, Any]:
        """Iteración asíncrona lista para pipelines Meta 4."""

        return await self._run_iteration_impl(iteration=iteration, iteration_data=iteration_data)

__all__ = ["MaterialsLoop"]
