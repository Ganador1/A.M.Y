"""Engineering autonomous research loop for experimental design and lab automation."""
from __future__ import annotations

import asyncio
import random
import time
from typing import Any, Dict, List, Optional

from app.autonomous.core.priority_scoring import PriorityScorer
from app.autonomous.core.state_manager import IterationRecord, StateManager
from app.autonomous.evaluation.empirical_feedback import process_feedback
from app.autonomous.evaluation.novelty_assessor import NoveltyAssessor
from app.autonomous.metrics.telemetry_collector import AutonomousTelemetry
from app.autonomous.models.importance_ranker import ImportanceRanker
from app.autonomous.integration import EvidenceSummary, ToolEvidenceBridge
from app.core.bootstrap_logging import logger

# ⭐ ENGINEERING SERVICES - Servicios principales (4)
from app.domains.engineering.services.advanced_lab_automation_service import AdvancedLabAutomationService
from app.domains.engineering.services.experimental_validator import ExperimentalValidatorService
from app.domains.engineering.services.hardware_abstraction_service import HardwareAbstractionService
from app.domains.engineering.services.experimental_toolkit_hub import ExperimentalToolkitHub
# ⭐ ENGINEERING SERVICES ADICIONALES (3 servicios)
from app.domains.engineering.services.lab_automation_service import LabAutomationService
from app.domains.engineering.services.lab_equipment_bridge import LabEquipmentBridge
from app.domains.engineering.services.synthesis_equipment import SynthesisEquipmentService


class EngineeringLoop:
    """Autonomous research loop for engineering domain focusing on experimental design and automation"""

    def __init__(
        self,
        state: StateManager | None = None,
        telemetry: AutonomousTelemetry | None = None,
    ):
        self.state = state or StateManager()
        self.telemetry = telemetry or AutonomousTelemetry()
        self.priority = PriorityScorer()
        self.novelty = NoveltyAssessor()
        self.importance_ranker = ImportanceRanker(w_freq=0.2, w_dependency=0.2, w_impact=0.6)
        self.iteration = 0
        self.rng = random.Random(999)

        # ⭐ ENGINEERING SERVICES - Servicios principales (4)
        self.automation_service = AdvancedLabAutomationService()  # Automatización de laboratorio
        self.validator_service = ExperimentalValidatorService()  # Validación experimental
        self.hardware_service = HardwareAbstractionService()  # Abstracción de hardware
        self.toolkit_service = ExperimentalToolkitHub()  # Hub de herramientas experimentales
        # ⭐ ENGINEERING SERVICES ADICIONALES (3 servicios)
        self.lab_automation = LabAutomationService()  # Lab automation protocols
        self.equipment_bridge = LabEquipmentBridge()  # Equipment connectivity bridge
        self.synthesis_equipment = SynthesisEquipmentService()  # Chemical synthesis equipment

        self.tool_evidence = ToolEvidenceBridge(default_domain="engineering")
        # Backwards compatibility
        self.evidence = self.tool_evidence
        self._last_designs: Optional[List[Dict[str, Any]]] = None

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

    def _seed_synthetic_designs(self, k: int = 6) -> List[Dict[str, Any]]:
        """Generate synthetic experimental designs as fallback."""
        designs: List[Dict[str, Any]] = []

        experiment_types = [
            "synthesis_optimization",
            "material_characterization",
            "process_validation",
            "quality_control",
        ]

        equipment_types = [
            "reactor",
            "spectrometer",
            "chromatograph",
            "microscope",
        ]

        for i in range(k):
            experiment_type = experiment_types[i % len(experiment_types)]
            equipment = equipment_types[i % len(equipment_types)]

            # Simulate experimental metrics
            throughput = self.rng.uniform(10, 100)  # Samples per hour
            precision = self.rng.uniform(0.90, 0.99)  # Measurement precision
            cost_per_run = self.rng.uniform(50, 500)  # USD

            designs.append({
                "id": f"eng_synthetic_{self.iteration}_{i}",
                "experiment_type": experiment_type,
                "equipment": equipment,
                "throughput": throughput,
                "precision": precision,
                "cost_per_run": cost_per_run,
                "automation_level": self.rng.uniform(0.3, 1.0),
                "anomaly_index": float((1.0 - precision) * 10),
                "impact_potential": min(1.0, throughput / 100.0),
                "literature_frequency": self.rng.randint(5, 40),
                "dependency_count": self.rng.randint(2, 7),
                "proveability": precision,
                "novelty": self.rng.random(),
                "information_gain": (throughput / 100.0 + precision) / 2.0,
                "estimated_cost": min(1.0, cost_per_run / 500.0),
                "source": "synthetic",
            })

        return designs

    async def _fetch_experimental_designs_async(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Fetch experimental designs from automation and toolkit services.

        Sources (priority order):
        1. Lab automation service (automated protocols)
        2. Toolkit hub (available experimental methods)
        3. Synthetic fallback
        """
        candidates: List[Dict[str, Any]] = []

        # SOURCE 1: Automated experimental protocols
        try:
            logger.info("🔧 Querying lab automation for experimental protocols...")

            automation_results = await self.automation_service.get_protocols({
                "min_automation_level": 0.5,
                "max_protocols": limit * 2,
                "domains": ["synthesis", "characterization", "quality_control"],
            })

            if automation_results.get("success"):
                protocols = automation_results.get("protocols", [])
                logger.info(f"Found {len(protocols)} automated protocols")

                for idx, protocol in enumerate(protocols[:limit]):
                    throughput = protocol.get("throughput", self.rng.uniform(20, 80))
                    precision = protocol.get("precision", self.rng.uniform(0.92, 0.98))
                    automation_level = protocol.get("automation_level", self.rng.uniform(0.6, 0.95))

                    candidates.append({
                        "id": f"protocol_{self.iteration}_{idx}",
                        "experiment_type": protocol.get("type", "synthesis_optimization"),
                        "equipment": protocol.get("equipment", "reactor"),
                        "throughput": throughput,
                        "precision": precision,
                        "automation_level": automation_level,
                        "cost_per_run": protocol.get("cost_per_run", self.rng.uniform(100, 400)),
                        "anomaly_index": float((1.0 - precision) * 10),
                        "impact_potential": min(1.0, (throughput / 100.0 + automation_level) / 2.0),
                        "literature_frequency": self.rng.randint(10, 35),
                        "dependency_count": self.rng.randint(3, 8),
                        "proveability": precision,
                        "novelty": 0.70 + automation_level * 0.25,
                        "information_gain": (throughput / 100.0 + precision) / 2.0,
                        "estimated_cost": min(1.0, protocol.get("cost_per_run", 300) / 500.0),
                        "source": "lab_automation",
                        "protocol_name": protocol.get("name", f"Protocol_{idx}"),
                    })
        except Exception as exc:
            logger.warning(f"Lab automation query failed: {exc}")

        # SOURCE 2: Experimental toolkit methods
        try:
            logger.info("🛠️ Querying experimental toolkit for available methods...")

            toolkit_results = await self.toolkit_service.get_methods({
                "categories": ["synthesis", "analysis", "validation"],
                "max_methods": limit,
            })

            if toolkit_results.get("success"):
                methods = toolkit_results.get("methods", [])
                logger.info(f"Found {len(methods)} experimental methods")

                for idx, method in enumerate(methods):
                    reliability = method.get("reliability", self.rng.uniform(0.85, 0.97))
                    versatility = method.get("versatility", self.rng.uniform(0.6, 0.9))

                    candidates.append({
                        "id": f"method_{self.iteration}_{idx}",
                        "experiment_type": method.get("category", "material_characterization"),
                        "equipment": method.get("equipment_required", "spectrometer"),
                        "reliability": reliability,
                        "versatility": versatility,
                        "throughput": method.get("throughput", self.rng.uniform(15, 60)),
                        "precision": reliability,
                        "anomaly_index": float((1.0 - reliability) * 8),
                        "impact_potential": versatility,
                        "literature_frequency": self.rng.randint(8, 30),
                        "dependency_count": self.rng.randint(2, 6),
                        "proveability": reliability,
                        "novelty": 0.60 + self.rng.random() * 0.25,
                        "information_gain": (reliability + versatility) / 2.0,
                        "estimated_cost": self.rng.random() * 0.4 + 0.2,
                        "source": "toolkit_hub",
                        "method_name": method.get("name", f"Method_{idx}"),
                    })
        except Exception as exc:
            logger.warning(f"Toolkit hub query failed: {exc}")

        # Fallback: Synthetic designs if all services failed
        if not candidates:
            logger.warning("⚠️ All engineering sources failed - using synthetic fallback")
            candidates = self._seed_synthetic_designs(limit)

        return candidates[:limit]

    async def _enrich_design_async(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich experimental design with validation and hardware compatibility checks."""
        enrichment: Dict[str, Any] = {}

        # ENRICHMENT 1: Experimental validation
        try:
            validation_payload = {
                "action": "validate_design",
                "experiment_type": design.get("experiment_type"),
                "equipment": design.get("equipment"),
                "throughput": design.get("throughput"),
                "precision": design.get("precision"),
            }
            validation_result = await self.validator_service.validate_experiment(validation_payload)

            if validation_result.get("success"):
                enrichment["validation"] = validation_result.get("validation", {})
                enrichment["feasibility_score"] = validation_result.get("feasibility_score", 0.75)
        except Exception as exc:
            logger.debug(f"Validation enrichment failed for {design.get('id')}: {exc}")
            enrichment["validation"] = {"error": str(exc)}

        # ENRICHMENT 2: Hardware compatibility check
        try:
            hardware_payload = {
                "action": "check_compatibility",
                "equipment": design.get("equipment"),
                "experiment_type": design.get("experiment_type"),
            }
            hardware_result = await self.hardware_service.check_compatibility(hardware_payload)

            if hardware_result.get("success"):
                enrichment["hardware_compatibility"] = hardware_result.get("compatibility", {})
                enrichment["available_equipment"] = hardware_result.get("available_equipment", [])
        except Exception as exc:
            logger.debug(f"Hardware check failed: {exc}")
            enrichment["hardware_compatibility"] = {"error": str(exc)}

        return enrichment

    def _build_engineering_hypothesis(
        self,
        design: Dict[str, Any],
        enrichment: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build hypothesis for experimental design validation."""
        design_id = design.get("id", "unknown")
        experiment_type = design.get("experiment_type", "Unknown")
        equipment = design.get("equipment", "Unknown")

        description = (
            f"Validate experimental design {design_id} ({experiment_type}) using "
            f"{equipment} with throughput {design.get('throughput', 0):.1f} samples/hour "
            f"and precision {design.get('precision', 0):.3f}"
        )

        variables: Dict[str, Any] = {
            "design_id": design_id,
            "experiment_type": experiment_type,
            "equipment": equipment,
            "throughput": design.get("throughput"),
            "precision": design.get("precision"),
            "automation_level": design.get("automation_level"),
            "source": design.get("source"),
            "enrichment": enrichment,
        }

        assumptions = [
            "Equipment is properly calibrated and maintained",
            "Standard operating procedures are followed",
            "Environmental conditions are controlled",
            "Safety protocols are in place",
        ]

        extras = {
            "parameters": {
                "cost_per_run": design.get("cost_per_run"),
                "protocol_name": design.get("protocol_name") or design.get("method_name"),
            },
            "keywords": ["engineering", experiment_type, equipment, "automation", "validation"],
        }

        return self.tool_evidence.build_hypothesis(
            title=f"Engineering Design: {design_id} ({experiment_type})",
            description=description,
            variables=variables,
            assumptions=assumptions,
            expected_outcome="Validate experimental feasibility and optimize parameters",
            extras=extras,
        )

    async def _run_iteration_impl(
        self,
        top_n: int = 3,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        self.iteration += 1

        seed_count = max(top_n * 2, 6)

        # Fetch experimental designs from services
        candidates = await self._fetch_experimental_designs_async(seed_count)

        # Rank by importance and priority
        ranked_importance = self.importance_ranker.rank(candidates)
        scored = self.priority.rank(ranked_importance)
        selected = scored[:top_n]

        if not selected:
            logger.warning("No experimental designs available for iteration %d", self.iteration)
            return {"success": False, "reason": "no_designs", "processed_count": 0}

        actions: List[str] = []
        outcomes: Dict[str, Any] = {}
        enriched_selected: List[Dict[str, Any]] = []
        novelty_scores: List[float] = []
        support_scores: List[float] = []

        for idx, design in enumerate(selected):
            # Novelty assessment
            novelty_res = self.novelty.assess([
                design.get("anomaly_index", 0.5),
                design.get("impact_potential", 0.5),
                design.get("information_gain", 0.5),
            ])
            novelty_scores.append(novelty_res["novelty_score"])

            # Enrich top 2 designs
            enrichment = await self._enrich_design_async(design) if idx < 2 else {}

            # Tool evidence corroboration
            evidence_summary: Optional[EvidenceSummary] = None
            summary_data: Optional[Dict[str, Any]] = None
            if self.tool_evidence:
                try:
                    hypothesis = self._build_engineering_hypothesis(design, enrichment)
                    evidence_summary = await self.tool_evidence.corroborate(hypothesis, domain="engineering")
                    success_flag = False
                    support_score = 0.0

                    if isinstance(evidence_summary, dict):
                        summary_data = evidence_summary
                        support_score = float(summary_data.get("support_score", summary_data.get("confidence", 0.0)))
                        success_flag = summary_data.get("success", True)
                    else:
                        summary_data = evidence_summary.as_dict()
                        support_score = float(getattr(evidence_summary, "support_score", 0.0))
                        success_flag = getattr(evidence_summary, "success", True)

                    if success_flag:
                        design["impact_potential"] = min(
                            1.0,
                            float(design.get("impact_potential", 0.5)) + support_score * 0.15,
                        )
                    support_scores.append(support_score)
                except Exception as exc:
                    logger.debug(f"Design hypothesis corroboration failed for {design.get('id')}: {exc}")
                    support_scores.append(0.0)

            actions.append("design_validation")

            outcome_payload: Dict[str, Any] = {
                "novelty_score": novelty_res["novelty_score"],
                "experiment_type": design.get("experiment_type"),
                "equipment": design.get("equipment"),
                "precision": design.get("precision"),
                "source": design.get("source"),
                "enrichment": enrichment or None,
            }

            if summary_data is not None:
                outcome_payload["tool_evidence"] = summary_data

            outcomes[design["id"]] = outcome_payload
            enriched_selected.append({**design, "enrichment": enrichment, "novelty": novelty_res})

        # Feedback processing
        feedback_event = {
            "metric_name": "experimental_feasibility",
            "value": len(selected),
            "improved": len(selected) > 0,
            "confidence": 0.72,
        }
        feedback_result = process_feedback(feedback_event)

        # Record iteration
        record = IterationRecord(
            iteration=self.iteration,
            domain="engineering",
            selected_ids=[s["id"] for s in selected],
            actions=actions,
            outcomes={**outcomes, "feedback_adjustment": feedback_result["adjustment"]},
        )
        self.state.add_iteration(record)

        # Calculate metrics
        duration = time.time() - start
        avg_novelty = sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0.0
        avg_support = sum(support_scores) / len(support_scores) if support_scores else 0.0
        avg_precision = sum(
            d.get("precision", 0.0) for d in selected if "precision" in d
        ) / len([d for d in selected if "precision" in d]) if any("precision" in d for d in selected) else 0.0

        summary = {
            "iteration": self.iteration,
            "duration_s": duration,
            "selected": len(selected),
            "actions": actions,
            "avg_novelty": avg_novelty,
            "avg_support_score": avg_support,
            "avg_precision": avg_precision,
        }

        # Telemetry
        try:
            self.telemetry.record_iteration(
                domain="engineering",
                duration_s=duration,
                selected=len(selected),
                mutations=0,
                sketches=0,
            )
        except Exception as exc:
            logger.warning("Telemetry recording failed (engineering): %s", exc)

        # Metrics
        try:
            from app.monitoring.metrics import metrics

            metrics.set_gauge("autonomous_novelty_last", float(avg_novelty))
            metrics.set_gauge("autonomous_feedback_adjustment_last", feedback_result["adjustment"])
            if support_scores:
                metrics.set_gauge("autonomous_support_score_last", avg_support)
            if avg_precision > 0:
                metrics.set_gauge("engineering_avg_precision", avg_precision)
        except (ImportError, AttributeError):
            logger.debug("Could not set engineering gauges")

        logger.info("Engineering loop iteration %d: %s", self.iteration, summary)

        return {
            "success": True,
            "summary": summary,
            "selected": enriched_selected,
            "outcomes": outcomes,
            "feedback": feedback_result,
            "avg_support_score": avg_support,
            "avg_precision": avg_precision,
            "processed_count": len(selected),
        }

    def run_iteration(
        self,
        top_n: int = 3,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Synchronous wrapper for iteration execution"""
        return self._run_coro_sync(self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data))

    async def run_engineering_iteration(
        self,
        top_n: int = 3,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Async engineering design iteration"""
        return await self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data)


__all__ = ["EngineeringLoop"]
