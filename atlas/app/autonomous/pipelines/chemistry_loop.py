"""Loop autónomo de química computacional con integración de servicios Meta 4."""
from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from app.autonomous.core.priority_scoring import PriorityScorer
from app.autonomous.core.state_manager import IterationRecord, StateManager
from app.autonomous.evaluation.empirical_feedback import process_feedback
from app.autonomous.evaluation.novelty_assessor import NoveltyAssessor
from app.autonomous.generators.experimental_design_generator import generate_experimental_design
from app.autonomous.metrics.telemetry_collector import AutonomousTelemetry
from app.autonomous.models.importance_ranker import ImportanceRanker
from app.autonomous.integration import EvidenceSummary, ToolEvidenceBridge
from app.domains.service_locator import get_service
from app.domains.chemistry.services.materials_discovery_service import MaterialCandidate
from app.compliance.ethics_gate import EthicsGate, ExperimentRequest

logger = logging.getLogger(__name__)


class ChemistryLoop:
    def __init__(self, state: StateManager | None = None, telemetry: AutonomousTelemetry | None = None):
        self.state = state or StateManager()
        self.telemetry = telemetry or AutonomousTelemetry()
        self.priority = PriorityScorer()
        self.novelty = NoveltyAssessor()
        self.importance_ranker = ImportanceRanker()
        self.iteration = 0
        self.random = random.Random(42)
        
        # Use ServiceLocator for dependency injection
        self.chemistry_service = get_service("ComputationalChemistryService")
        self.materials_service = get_service("MaterialsDiscoveryService")
        self.gnome_service = get_service("GNOMEMaterialsService")
        self.chemml_service = get_service("ChemMLService")
        
        # Phase 2 services (lazy loaded via locator)
        self.nmr_service = get_service("AdvancedNMRService")
        self.spectrometers = get_service("AdvancedSpectrometers")
        # DSC service not yet in default registry, fallback or add it
        # self.dsc_service = get_service("DifferentialScanningCalorimetryService") 
        # For now, we'll keep direct import for DSC if not registered, or register it.
        # Let's assume we register it or keep it as is if not critical.
        # Actually, let's register it in ServiceLocator dynamically if needed or just use it.
        # But to be clean, let's use the locator for what we can.
        
        self.tool_evidence = ToolEvidenceBridge(default_domain="chemistry")
        self.ethics_gate = EthicsGate()

    # ------------------------------ Helpers ------------------------------
    @staticmethod
    def _normalize_hypothesis(hypothesis: Any) -> Dict[str, Any]:
        if isinstance(hypothesis, dict):
            return hypothesis
        if hasattr(hypothesis, "to_dict"):
            try:
                return hypothesis.to_dict()  # type: ignore[attr-defined]
            except Exception:
                pass
        if hasattr(hypothesis, "as_dict"):
            try:
                return hypothesis.as_dict()  # type: ignore[attr-defined]
            except Exception:
                pass
        return {"description": str(hypothesis)}

    @staticmethod
    def _design_runs(design: Any) -> List[Any]:
        return design.get("runs", []) if isinstance(design, dict) else []

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

    def _seed_synthetic_candidates(self, k: int) -> List[Dict[str, Any]]:
        return [
            {
                "id": f"chem_{self.iteration}_{i}",
                "smiles": f"C{i}H{i*2+2}",
                "composition": f"C{i}H{i*2+2}",
                "source": "synthetic",
                "literature_frequency": self.random.randint(0, 120),
                "dependency_count": self.random.randint(0, 10),
                "impact_potential": self.random.random(),
                "proveability": self.random.random(),
                "novelty": self.random.random(),
                "information_gain": self.random.random(),
                "estimated_cost": self.random.random() * 0.3,
                "suitability_score": self.random.random(),
            }
            for i in range(k)
        ]

    async def _fetch_domain_candidates_async(
        self,
        k: Optional[int] = None,
        application: Optional[str] = None,
        *,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        candidate_limit = limit if limit is not None else k
        if candidate_limit is None:
            candidate_limit = 5

        # ⭐ NUEVO: Buscar primero en GNOME (381K+ materiales reales)
        gnome_candidates = []
        try:
            target_app = application or "battery_cathode"
            logger.info(f"🔍 Searching GNOME database for {target_app} materials (381K+ available)...")
            gnome_results = await self.gnome_service.search_materials(  # type: ignore[attr-defined]
                application=target_app,
                max_results=candidate_limit * 3,  # Traer más para filtrar mejor
                filters={
                    "formation_energy_max": -0.5,
                    "band_gap_min": 0.1,
                    "stability_min": 0.7
                }
            )
            
            # Enriquecer con predicciones ML
            for material in gnome_results[:candidate_limit * 2]:
                formula = material.get("formula", "")
                if formula:
                    try:
                        # ⭐ NUEVO: Predicciones ML con ChemML
                        ml_props = await self.chemml_service.predict_properties(  # type: ignore[attr-defined]
                            composition=formula,
                            properties=["band_gap", "formation_energy", "elastic_modulus"]
                        )
                        material["ml_predictions"] = ml_props
                        material["ml_confidence"] = ml_props.get("confidence", 0.5)
                        gnome_candidates.append(material)
                        logger.debug(f"✓ GNOME material {formula}: ML confidence={ml_props.get('confidence', 0):.2f}")
                    except Exception as ml_exc:
                        logger.debug(f"ChemML prediction failed for {formula}: {ml_exc}")
                        gnome_candidates.append(material)
            
            if gnome_candidates:
                logger.info(f"✅ Found {len(gnome_candidates)} GNOME materials with ML enrichment")
        except Exception as gnome_exc:
            logger.debug(f"GNOME search failed (falling back to materials service): {gnome_exc}")
        
        # Fallback: MaterialsDiscoveryService tradicional
        materials_service_candidates = []
        try:
            if hasattr(self.materials_service, "discover_materials"):
                materials = await self.materials_service.discover_materials(  # type: ignore[attr-defined]
                    application=application or "battery_cathode",
                    max_candidates=candidate_limit,
                )
            else:
                materials = await self.materials_service.discover_materials_for_application(
                    application or "battery_cathode",
                    max_candidates=candidate_limit,
                )
            materials_service_candidates = materials
        except (RuntimeError, ValueError, OSError) as exc:
            logger.debug("Material discovery fallback due to error: %s", exc)
            # If the materials discovery service raises, return empty list by
            # contract for the simpler test scenarios that simulate service errors.
            return []

        # Combinar GNOME + MaterialsService
        all_candidates = gnome_candidates + materials_service_candidates
        
        processed: List[Dict[str, Any]] = []
        for idx, candidate in enumerate(all_candidates[:candidate_limit * 2]):
            # Detectar si es de GNOME (dict) o MaterialsService (MaterialCandidate object)
            if isinstance(candidate, dict):
                # GNOME candidate
                formula = candidate.get("formula")
                suitability = candidate.get("suitability_score", 0.7)  # GNOME tiene scores más altos
                band_gap = candidate.get("band_gap")
                stability = candidate.get("stability_score")
                electrical = candidate.get("electrical_conductivity")
                source = "gnome"
                ml_predictions = candidate.get("ml_predictions", {})
            else:
                # MaterialsService candidate
                composition = getattr(candidate, "composition", None)
                formula = getattr(composition, "formula", None) if composition else None
                suitability = getattr(candidate, "suitability_score", 0.5) or 0.5
                properties = getattr(candidate, "properties", None)
                band_gap = getattr(properties, "band_gap", None) if properties else None
                stability = getattr(properties, "stability_score", None) if properties else None
                electrical = getattr(properties, "electrical_conductivity", None) if properties else None
                source = "materials_service"
                ml_predictions = {}

            impact = 0.6
            if electrical is not None:
                impact = max(0.1, min(1.0, float(electrical) / 10.0))
            elif band_gap is not None:
                impact = max(0.1, min(1.0, 1.8 - abs(1.4 - float(band_gap))))

            proveability = 0.5 + min(0.4, suitability / 2.5)
            novelty = max(0.05, min(0.95, 1.0 - suitability + self.random.random() * 0.1))
            info_gain = max(0.1, min(1.0, suitability + novelty / 2.0))
            estimated_cost = max(0.05, 0.3 - (stability or 0.4) * 0.1)
            
            # ⭐ Boost scores para materiales de GNOME con ML predictions
            if source == "gnome" and ml_predictions:
                ml_confidence = ml_predictions.get("confidence", 0.5)
                impact = min(1.0, impact * (1 + ml_confidence * 0.2))
                proveability = min(1.0, proveability * (1 + ml_confidence * 0.15))
                logger.debug(f"🚀 GNOME material boosted by ML confidence={ml_confidence:.2f}")

            processed.append(
                {
                    "id": f"chem_{self.iteration}_{idx}",
                    "smiles": formula or f"M{idx}",
                    "composition": formula or f"M{idx}",
                    "source": source,  # ⭐ NUEVO: identificar fuente
                    "literature_frequency": int(40 + suitability * 60),
                    "dependency_count": max(0, 6 - int(suitability * 5)),
                    "impact_potential": float(impact),
                    "proveability": float(max(0.1, min(1.0, proveability))),
                    "novelty": float(max(0.05, min(1.0, novelty))),
                    "information_gain": float(info_gain),
                    "estimated_cost": float(max(0.02, min(0.5, estimated_cost))),
                    "suitability_score": float(suitability),
                    "ml_predictions": ml_predictions,  # ⭐ NUEVO: predicciones ML
                    "materials_metadata": {
                        "target_application": application or "battery_cathode",
                        "discovery_method": "gnome_ml" if source == "gnome" else "compositional_substitution",
                        "data_source": source,  # ⭐ NUEVO
                    },
                }
            )

        return processed[:k]

    def _seed_candidates(self, k: int = 6, application: Optional[str] = None) -> List[Dict[str, Any]]:
        domain_candidates = self._run_coro_sync(self._fetch_domain_candidates_async(k, application))
        if domain_candidates:
            return domain_candidates
        return self._seed_synthetic_candidates(k)

    async def _analyze_candidate_async(
        self,
        candidate: Dict[str, Any],
        include_quantum: bool = False,
    ) -> Dict[str, Any]:
        molecular_analysis = self.chemistry_service.analyze_molecule(candidate.get("smiles", ""))

        try:
            material_props = await self.materials_service.predict_material_properties(candidate.get("composition", ""))
            if hasattr(material_props, "__dict__"):
                materials_properties = asdict(material_props)
            else:
                materials_properties = material_props
        except (RuntimeError, ValueError, TypeError) as exc:  # pragma: no cover - fallback
            materials_properties = {"error": str(exc)}

        quantum_summary: Optional[Dict[str, Any]] = None
        if include_quantum:
            molecule_data = {
                "atom": candidate.get("quantum_atom_spec", "H 0 0 0; H 0 0 0.74"),
                "basis": "sto-3g",
            }
            quantum_summary = self.chemistry_service.quantum_chemistry_calculation(molecule_data)

        return {
            "molecular_analysis": molecular_analysis,
            "materials_properties": materials_properties,
            "quantum_summary": quantum_summary,
        }

    def _build_chemistry_hypothesis(
        self,
        candidate: Dict[str, Any],
        enrichment: Dict[str, Any],
        application: Optional[str],
    ) -> Dict[str, Any]:
        smiles = candidate.get("smiles") or candidate.get("composition") or candidate.get("id", "molecule")
        materials_md = candidate.get("materials_metadata")
        if not isinstance(materials_md, dict):
            materials_md = {}
        target_application = application or materials_md.get("target_application")
        target_application = target_application or "drug_discovery"
        description = (
            f"Evaluar la viabilidad de {smiles} para {target_application} considerando propiedades computacionales y"
            " predicciones materiales"
        )
        variables: Dict[str, Any] = {
            "smiles": smiles,
            "composition": candidate.get("composition"),
            "impact_potential": candidate.get("impact_potential"),
            "materials_properties": enrichment.get("materials_properties"),
            "molecular_analysis": enrichment.get("molecular_analysis"),
        }
        assumptions = [
            "Los análisis moleculares provienen de ComputationalChemistryService",
            "Las propiedades materiales son aproximaciones basadas en modelos predictivos",
        ]
        extras = {
            "parameters": {
                "suitability_score": candidate.get("suitability_score"),
                "novelty": candidate.get("novelty"),
            },
            "keywords": [target_application, smiles],
        }
        hypothesis = self.tool_evidence.build_hypothesis(
            title=f"Validación molecular de {smiles}",
            description=description,
            domain="drug_discovery",
            variables=variables,
            assumptions=assumptions,
            expected_outcome=f"Confirmar viabilidad de {target_application}",
            extras=extras,
        )
        return self._normalize_hypothesis(hypothesis)

    async def _run_iteration_impl(
        self,
        top_n: int = 4,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        self.iteration += 1

        application = None
        if isinstance(iteration_data, dict):
            application = iteration_data.get("target_application") or iteration_data.get("material_class")

        seed_count = max(top_n * 2, 6)
        raw_items = await self._fetch_domain_candidates_async(seed_count, application)
        raw_items = raw_items or self._seed_synthetic_candidates(seed_count)

        ranked_importance = self.importance_ranker.rank(raw_items)
        scored = self.priority.rank(ranked_importance)
        selected = scored[:top_n]

        design_config = iteration_data.get("design_config") if isinstance(iteration_data, dict) else None
        design = generate_experimental_design(
            design_config
            or {
                "factors": {"temp": [270, 300, 330], "ph": [6, 7, 8]},
                "max_runs": 5,
                "stop_metric": "energy",
            }
        )

        actions: List[str] = []
        outcomes: Dict[str, Any] = {}
        enriched_selected: List[Dict[str, Any]] = []
        support_scores: List[float] = []

        for idx, candidate in enumerate(selected):
            enrichment = await self._analyze_candidate_async(candidate, include_quantum=idx == 0)
            novelty_res = self.novelty.assess(
                [candidate["novelty"], candidate["information_gain"], candidate["impact_potential"]]
            )
            evidence_summary: Optional[EvidenceSummary] = None
            ethics_metadata = {"ethics_approved": True, "ethics_decision_id": None, "ethics_risk_level": "LOW"}
            
            if self.tool_evidence:
                try:
                    hypothesis = self._build_chemistry_hypothesis(candidate, enrichment, application)
                    
                    # Ethics evaluation before execution
                    formula = candidate.get("formula", candidate.get("id", "unknown"))
                    keywords = [formula, "computational_chemistry", "materials_discovery"]
                    if application:
                        keywords.append(application)
                    
                    # Asegurar que la descripción es texto
                    hyp_desc = hypothesis.get("description", "") if isinstance(hypothesis, dict) else str(hypothesis)
                    ethics_request = ExperimentRequest(
                        domain="computational_chemistry",
                        description=hyp_desc,
                        data_sensitivity="low",
                        declared_intent="research",
                        keywords=keywords,
                        user_id="chemistry_loop",
                        metadata={
                            "candidate_id": candidate.get("id"),
                            "iteration": self.iteration,
                            "application": application,
                        }
                    )
                    
                    ethics_decision = self.ethics_gate.evaluate(ethics_request)
                    ethics_metadata.update({
                        "ethics_approved": ethics_decision.allowed,
                        "ethics_decision_id": ethics_decision.decision_id,
                        # EthicsDecision usa `level`; mantenemos compatibilidad si existiera `risk_level`
                        "ethics_risk_level": getattr(ethics_decision, "level", getattr(ethics_decision, "risk_level", "UNKNOWN")),
                    })
                    
                    if not ethics_decision.allowed:
                        logger.warning(
                            f"Chemistry hypothesis {candidate.get('id')} blocked by ethics gate: "
                            f"{getattr(ethics_decision, 'level', 'UNKNOWN')} risk, reasons: {ethics_decision.escalation_reasons}"
                        )
                        # Skip this candidate if blocked
                        continue
                    
                    if ethics_decision.requires_signature:
                        logger.info(
                            f"Chemistry hypothesis {candidate.get('id')} requires human review: "
                            f"{ethics_decision.recommended_actions}"
                        )
                    
                    evidence_summary = await self.tool_evidence.corroborate(hypothesis, domain="drug_discovery")
                    if evidence_summary.success:
                        candidate["impact_potential"] = min(
                            1.0,
                            float(candidate.get("impact_potential", 0.5)) + evidence_summary.support_score * 0.15,
                        )
                        support_scores.append(evidence_summary.support_score)
                    else:
                        support_scores.append(0.0)
                except (RuntimeError, ValueError, ConnectionError, TimeoutError) as exc:
                    logger.debug("Chemistry candidate corroboration failed: %s", exc)

            actions.append("simulate")
            outcome_payload = {
                "novelty_score": novelty_res["novelty_score"],
                "simulated_energy": self.random.random() - 0.5,
                "molecular_analysis": enrichment["molecular_analysis"],
                "materials_properties": enrichment["materials_properties"],
                "ethics": ethics_metadata,
            }
            if enrichment["quantum_summary"]:
                outcome_payload["quantum_summary"] = enrichment["quantum_summary"]
            if evidence_summary:
                outcome_payload["tool_evidence"] = evidence_summary.as_dict()
            outcomes[candidate["id"]] = outcome_payload
            enriched_selected.append({**candidate, "analysis": enrichment, "ethics": ethics_metadata})

        feedback_event = {
            "metric_name": "selection_volume",
            "value": len(selected),
            "improved": len(selected) > 0,
            "confidence": 0.55,
        }
        feedback_result = process_feedback(feedback_event)

        rec = IterationRecord(
            iteration=self.iteration,
            domain="chemistry",
            selected_ids=[s["id"] for s in selected],
            actions=actions,
            outcomes={**outcomes, "feedback_adjustment": feedback_result["adjustment"]},
        )
        self.state.add_iteration(rec)
        avg_novelty = (sum(v["novelty_score"] for v in outcomes.values()) / len(outcomes) if outcomes else 0.0)
        self.telemetry.record_iteration(
            domain="chemistry",
            duration_s=time.time() - start,
            selected=len(selected),
            mutations=0,
            sketches=0,
        )
        from app.monitoring.metrics import metrics  # import local para evitar dependencias circulares

        metrics.set_gauge("autonomous_novelty_last", avg_novelty)
        metrics.set_gauge("autonomous_feedback_adjustment_last", feedback_result["adjustment"])
        if support_scores:
            metrics.set_gauge("autonomous_support_score_last", sum(support_scores) / len(support_scores))

        return {
            "iteration": self.iteration,
            "selected": enriched_selected,
            "design_runs": self._design_runs(design),
            "outcomes": rec.outcomes,
            "application": application or "battery_cathode",
            "avg_support_score": (sum(support_scores) / len(support_scores)) if support_scores else 0.0,
        }

    def run_iteration(self, top_n: int = 4, iteration_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._run_coro_sync(self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data))

    async def run_chemistry_discovery_iteration(
        self,
        iteration_data: Optional[Dict[str, Any]] = None,
        top_n: int = 4,
    ) -> Dict[str, Any]:
        """Iteración asíncrona preparada para la demo end-to-end Meta 4."""

        return await self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data)

__all__ = ["ChemistryLoop"]
