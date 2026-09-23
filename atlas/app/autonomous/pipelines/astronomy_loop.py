"""Astronomy autonomous research loop for exoplanet discovery and stellar analysis."""
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

# ⭐ ASTRONOMY SERVICES - Servicios principales (5)
from app.domains.astronomy.services.exoplanet_transit_analysis_service import ExoplanetTransitAnalysisService
from app.domains.astronomy.services.stellar_variability_service import StellarVariabilityService
from app.domains.astronomy.services.astronomical_ml_service import AstronomicalMLService
from app.domains.astronomy.services.lightkurve_advanced_service import LightkurveAdvancedService
from app.domains.astronomy.services.integrated_astronomy_pipeline import IntegratedAstronomyPipeline
# ⭐ ASTRONOMY SERVICES ADICIONALES (6 servicios)
from app.domains.astronomy.services.astropy_precision_service import AstropyPrecisionService
from app.domains.astronomy.services.binary_system_analysis_service import BinarySystemAnalysisService
from app.domains.astronomy.services.astrometric_analysis_service import AstrometricAnalysisService
from app.domains.astronomy.services.multiwavelength_analysis_service import MultiWavelengthAnalysisService
from app.domains.astronomy.services.optimal_aperture_photometry_service import OptimalAperturePhotometryService
from app.domains.astronomy.services.advanced_statistics_service import AdvancedStatisticsService


class AstronomyLoop:
    """Autonomous research loop for astronomy domain focusing on exoplanet discovery and stellar analysis"""

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
        self.rng = random.Random(888)

        # ⭐ ASTRONOMY SERVICES - Servicios principales (5)
        self.exoplanet_service = ExoplanetTransitAnalysisService()  # Detección de exoplanetas
        self.stellar_service = StellarVariabilityService()  # Análisis de variabilidad estelar
        self.ml_service = AstronomicalMLService()  # Machine Learning astronómico
        self.lightkurve_service = LightkurveAdvancedService()  # Análisis de curvas de luz
        self.pipeline_service = IntegratedAstronomyPipeline()  # Pipeline integrado
        # ⭐ ASTRONOMY SERVICES ADICIONALES (6 servicios)
        self.astropy_service = AstropyPrecisionService()  # High-precision astrometry
        self.binary_system_service = BinarySystemAnalysisService()  # Binary star analysis
        self.astrometric_service = AstrometricAnalysisService()  # Astrometric measurements
        self.multiwavelength_service = MultiWavelengthAnalysisService()  # Multi-wavelength analysis
        self.photometry_service = OptimalAperturePhotometryService()  # Optimal aperture photometry
        self.statistics_service = AdvancedStatisticsService()  # Advanced statistical analysis

        self.tool_evidence = ToolEvidenceBridge(default_domain="astronomy")
        # Backwards compatibility
        self.evidence = self.tool_evidence
        self._last_targets: Optional[List[Dict[str, Any]]] = None

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

    def _seed_synthetic_targets(self, k: int = 7) -> List[Dict[str, Any]]:
        """Generate synthetic astronomical targets as fallback."""
        targets: List[Dict[str, Any]] = []

        target_types = ["exoplanet_candidate", "variable_star", "transient", "binary_system"]

        for i in range(k):
            target_type = target_types[i % len(target_types)]

            # Simulate astronomical metrics
            transit_depth = self.rng.uniform(0.001, 0.05)  # Transit depth in magnitude
            period = self.rng.uniform(1.0, 365.0)  # Orbital period in days
            snr = self.rng.uniform(5.0, 50.0)  # Signal-to-noise ratio

            targets.append({
                "id": f"astro_synthetic_{self.iteration}_{i}",
                "target_type": target_type,
                "ra": self.rng.uniform(0, 360),  # Right ascension
                "dec": self.rng.uniform(-90, 90),  # Declination
                "magnitude": self.rng.uniform(8.0, 16.0),  # Apparent magnitude
                "transit_depth": transit_depth,
                "orbital_period": period,
                "snr": snr,
                "anomaly_index": float(transit_depth * 10),
                "impact_potential": min(1.0, snr / 50.0),
                "literature_frequency": self.rng.randint(1, 50),
                "dependency_count": self.rng.randint(1, 8),
                "proveability": min(1.0, snr / 30.0),
                "novelty": self.rng.random(),
                "information_gain": (transit_depth * 10 + snr / 50.0) / 2.0,
                "estimated_cost": self.rng.random() * 0.4 + 0.1,
                "source": "synthetic",
            })

        return targets

    async def _fetch_astronomical_targets_async(self, limit: int = 7) -> List[Dict[str, Any]]:
        """Fetch astronomical targets from multiple sources.

        Sources (priority order):
        1. Exoplanet transit analysis (TESS/Kepler candidates)
        2. Stellar variability analysis (variable stars)
        3. ML predictions (anomaly detection)
        4. Synthetic fallback
        """
        candidates: List[Dict[str, Any]] = []

        # SOURCE 1: Exoplanet candidates from transit analysis
        try:
            logger.info("🔭 Searching for exoplanet transit candidates...")

            # Query exoplanet service for transit candidates
            exoplanet_results = await self.exoplanet_service.detect_transits({
                "min_snr": 5.0,
                "max_candidates": limit * 2,
                "mission": "TESS",  # Or "Kepler"
            })

            if exoplanet_results.get("success"):
                exoplanet_candidates = exoplanet_results.get("candidates", [])
                logger.info(f"Found {len(exoplanet_candidates)} exoplanet candidates")

                for idx, candidate in enumerate(exoplanet_candidates[:limit]):
                    transit_depth = candidate.get("transit_depth", self.rng.uniform(0.001, 0.05))
                    period = candidate.get("period", self.rng.uniform(1.0, 365.0))
                    snr = candidate.get("snr", self.rng.uniform(10.0, 50.0))

                    candidates.append({
                        "id": f"exoplanet_{self.iteration}_{idx}",
                        "target_type": "exoplanet_candidate",
                        "ra": candidate.get("ra", self.rng.uniform(0, 360)),
                        "dec": candidate.get("dec", self.rng.uniform(-90, 90)),
                        "magnitude": candidate.get("magnitude", self.rng.uniform(10.0, 15.0)),
                        "transit_depth": transit_depth,
                        "orbital_period": period,
                        "snr": snr,
                        "anomaly_index": float(transit_depth * 10),
                        "impact_potential": min(1.0, snr / 50.0),
                        "literature_frequency": self.rng.randint(5, 30),
                        "dependency_count": self.rng.randint(2, 6),
                        "proveability": min(1.0, snr / 30.0),
                        "novelty": 0.80 + self.rng.random() * 0.15,  # High novelty for new candidates
                        "information_gain": (transit_depth * 10 + snr / 50.0) / 2.0,
                        "estimated_cost": 0.20 + self.rng.random() * 0.15,
                        "source": "exoplanet_transit",
                        "mission": candidate.get("mission", "TESS"),
                    })
        except Exception as exc:
            logger.warning(f"Exoplanet transit analysis failed: {exc}")

        # SOURCE 2: Variable stars from stellar variability analysis
        try:
            logger.info("⭐ Analyzing stellar variability...")

            stellar_results = await self.stellar_service.analyze_variability({
                "min_amplitude": 0.01,
                "max_candidates": limit,
                "variability_types": ["eclipsing_binary", "pulsating", "cataclysmic"],
            })

            if stellar_results.get("success"):
                stellar_candidates = stellar_results.get("candidates", [])
                logger.info(f"Found {len(stellar_candidates)} variable star candidates")

                for idx, candidate in enumerate(stellar_candidates):
                    amplitude = candidate.get("amplitude", self.rng.uniform(0.01, 0.5))
                    period = candidate.get("period", self.rng.uniform(0.1, 100.0))

                    candidates.append({
                        "id": f"variable_star_{self.iteration}_{idx}",
                        "target_type": "variable_star",
                        "ra": candidate.get("ra", self.rng.uniform(0, 360)),
                        "dec": candidate.get("dec", self.rng.uniform(-90, 90)),
                        "magnitude": candidate.get("magnitude", self.rng.uniform(8.0, 14.0)),
                        "amplitude": amplitude,
                        "period": period,
                        "variability_type": candidate.get("variability_type", "unknown"),
                        "anomaly_index": float(amplitude * 2),
                        "impact_potential": min(1.0, amplitude / 0.5),
                        "literature_frequency": self.rng.randint(10, 40),
                        "dependency_count": self.rng.randint(3, 8),
                        "proveability": 0.70 + self.rng.random() * 0.20,
                        "novelty": 0.65 + self.rng.random() * 0.20,
                        "information_gain": amplitude,
                        "estimated_cost": 0.15 + self.rng.random() * 0.10,
                        "source": "stellar_variability",
                    })
        except Exception as exc:
            logger.warning(f"Stellar variability analysis failed: {exc}")

        # Fallback: Synthetic targets if all services failed
        if not candidates:
            logger.warning("⚠️ All astronomy sources failed - using synthetic fallback")
            candidates = self._seed_synthetic_targets(limit)

        return candidates[:limit]

    async def _enrich_target_async(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich astronomical target with ML predictions and light curve analysis."""
        enrichment: Dict[str, Any] = {}

        # ENRICHMENT 1: ML-based anomaly detection and classification
        try:
            ml_payload = {
                "action": "classify_target",
                "ra": target.get("ra"),
                "dec": target.get("dec"),
                "magnitude": target.get("magnitude"),
                "target_type": target.get("target_type"),
            }
            ml_result = await self.ml_service.process_request(ml_payload)

            if ml_result.get("success"):
                enrichment["ml_classification"] = ml_result.get("classification", {})
                enrichment["anomaly_score"] = ml_result.get("anomaly_score", 0.5)
        except Exception as exc:
            logger.debug(f"ML enrichment failed for {target.get('id')}: {exc}")
            enrichment["ml_classification"] = {"error": str(exc)}

        # ENRICHMENT 2: Light curve analysis with Lightkurve
        try:
            lightkurve_payload = {
                "action": "analyze_lightcurve",
                "target_id": target.get("id"),
                "ra": target.get("ra"),
                "dec": target.get("dec"),
            }
            lightkurve_result = await self.lightkurve_service.process_request(lightkurve_payload)

            if lightkurve_result.get("success"):
                enrichment["lightcurve_analysis"] = lightkurve_result.get("analysis", {})
                enrichment["periodogram"] = lightkurve_result.get("periodogram", {})
        except Exception as exc:
            logger.debug(f"Lightkurve analysis failed: {exc}")
            enrichment["lightcurve_analysis"] = {"error": str(exc)}

        return enrichment

    def _build_astronomy_hypothesis(
        self,
        target: Dict[str, Any],
        enrichment: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build hypothesis for astronomical target validation."""
        target_id = target.get("id", "unknown")
        target_type = target.get("target_type", "Unknown")

        description = (
            f"Validate astronomical target {target_id} ({target_type}) with "
            f"coordinates RA={target.get('ra', 0):.2f}°, Dec={target.get('dec', 0):.2f}° "
            f"and magnitude {target.get('magnitude', 0):.2f}"
        )

        variables: Dict[str, Any] = {
            "target_id": target_id,
            "target_type": target_type,
            "coordinates": {
                "ra": target.get("ra"),
                "dec": target.get("dec"),
            },
            "magnitude": target.get("magnitude"),
            "source": target.get("source"),
            "enrichment": enrichment,
        }

        # Add target-specific variables
        if target_type == "exoplanet_candidate":
            variables["transit_depth"] = target.get("transit_depth")
            variables["orbital_period"] = target.get("orbital_period")
        elif target_type == "variable_star":
            variables["amplitude"] = target.get("amplitude")
            variables["period"] = target.get("period")
            variables["variability_type"] = target.get("variability_type")

        assumptions = [
            "Photometric data is calibrated and reliable",
            "Target coordinates are accurate within 1 arcsecond",
            "Background contamination is minimal",
        ]

        extras = {
            "parameters": {
                "snr": target.get("snr"),
                "mission": target.get("mission"),
            },
            "keywords": ["astronomy", target_type, "discovery", "validation"],
        }

        return self.tool_evidence.build_hypothesis(
            title=f"Astronomy Discovery: {target_id} ({target_type})",
            description=description,
            variables=variables,
            assumptions=assumptions,
            expected_outcome="Validate target and determine follow-up priority",
            extras=extras,
        )

    async def _run_iteration_impl(
        self,
        top_n: int = 4,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        self.iteration += 1

        seed_count = max(top_n * 2, 6)

        # Fetch astronomical targets from services
        candidates = await self._fetch_astronomical_targets_async(seed_count)

        # Rank by importance and priority
        ranked_importance = self.importance_ranker.rank(candidates)
        scored = self.priority.rank(ranked_importance)
        selected = scored[:top_n]

        if not selected:
            logger.warning("No astronomical targets available for iteration %d", self.iteration)
            return {"success": False, "reason": "no_targets", "processed_count": 0}

        actions: List[str] = []
        outcomes: Dict[str, Any] = {}
        enriched_selected: List[Dict[str, Any]] = []
        novelty_scores: List[float] = []
        support_scores: List[float] = []

        for idx, target in enumerate(selected):
            # Novelty assessment
            novelty_res = self.novelty.assess([
                target.get("anomaly_index", 0.5),
                target.get("impact_potential", 0.5),
                target.get("information_gain", 0.5),
            ])
            novelty_scores.append(novelty_res["novelty_score"])

            # Enrich top 2 targets
            enrichment = await self._enrich_target_async(target) if idx < 2 else {}

            # Tool evidence corroboration
            evidence_summary: Optional[EvidenceSummary] = None
            summary_data: Optional[Dict[str, Any]] = None
            if self.tool_evidence:
                try:
                    hypothesis = self._build_astronomy_hypothesis(target, enrichment)
                    evidence_summary = await self.tool_evidence.corroborate(hypothesis, domain="astronomy")
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
                        target["impact_potential"] = min(
                            1.0,
                            float(target.get("impact_potential", 0.5)) + support_score * 0.15,
                        )
                    support_scores.append(support_score)
                except Exception as exc:
                    logger.debug(f"Target hypothesis corroboration failed for {target.get('id')}: {exc}")
                    support_scores.append(0.0)

            actions.append("target_validation")

            outcome_payload: Dict[str, Any] = {
                "novelty_score": novelty_res["novelty_score"],
                "target_type": target.get("target_type"),
                "coordinates": {
                    "ra": target.get("ra"),
                    "dec": target.get("dec"),
                },
                "source": target.get("source"),
                "enrichment": enrichment or None,
            }

            if summary_data is not None:
                outcome_payload["tool_evidence"] = summary_data

            outcomes[target["id"]] = outcome_payload
            enriched_selected.append({**target, "enrichment": enrichment, "novelty": novelty_res})

        # Feedback processing
        feedback_event = {
            "metric_name": "discovery_potential",
            "value": len(selected),
            "improved": len(selected) > 0,
            "confidence": 0.70,
        }
        feedback_result = process_feedback(feedback_event)

        # Record iteration
        record = IterationRecord(
            iteration=self.iteration,
            domain="astronomy",
            selected_ids=[s["id"] for s in selected],
            actions=actions,
            outcomes={**outcomes, "feedback_adjustment": feedback_result["adjustment"]},
        )
        self.state.add_iteration(record)

        # Calculate metrics
        duration = time.time() - start
        avg_novelty = sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0.0
        avg_support = sum(support_scores) / len(support_scores) if support_scores else 0.0
        avg_snr = sum(
            t.get("snr", 0.0) for t in selected if "snr" in t
        ) / len([t for t in selected if "snr" in t]) if any("snr" in t for t in selected) else 0.0

        summary = {
            "iteration": self.iteration,
            "duration_s": duration,
            "selected": len(selected),
            "actions": actions,
            "avg_novelty": avg_novelty,
            "avg_support_score": avg_support,
            "avg_snr": avg_snr,
        }

        # Telemetry
        try:
            self.telemetry.record_iteration(
                domain="astronomy",
                duration_s=duration,
                selected=len(selected),
                mutations=0,
                sketches=0,
            )
        except Exception as exc:
            logger.warning("Telemetry recording failed (astronomy): %s", exc)

        # Metrics
        try:
            from app.monitoring.metrics import metrics

            metrics.set_gauge("autonomous_novelty_last", float(avg_novelty))
            metrics.set_gauge("autonomous_feedback_adjustment_last", feedback_result["adjustment"])
            if support_scores:
                metrics.set_gauge("autonomous_support_score_last", avg_support)
            if avg_snr > 0:
                metrics.set_gauge("astronomy_avg_snr", avg_snr)
        except (ImportError, AttributeError):
            logger.debug("Could not set astronomy gauges")

        logger.info("Astronomy loop iteration %d: %s", self.iteration, summary)

        return {
            "success": True,
            "summary": summary,
            "selected": enriched_selected,
            "outcomes": outcomes,
            "feedback": feedback_result,
            "avg_support_score": avg_support,
            "avg_snr": avg_snr,
            "processed_count": len(selected),
        }

    def run_iteration(
        self,
        top_n: int = 4,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Synchronous wrapper for iteration execution"""
        return self._run_coro_sync(self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data))

    async def run_astronomy_iteration(
        self,
        top_n: int = 4,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Async astronomy discovery iteration"""
        return await self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data)


__all__ = ["AstronomyLoop"]
