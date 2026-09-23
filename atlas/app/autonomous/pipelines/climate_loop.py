"""Loop autónomo de clima / geociencias integrado con servicios avanzados."""
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
from app.services.advanced_earth_sciences_service import AdvancedEarthSciencesService
from app.services.scientific_data_lake_service import ScientificDataLakeService
from app.services.advanced_scientific_database_service import AdvancedScientificDatabaseService
from app.domains.climate.services.climate_evidence_service import ClimateEvidenceService


class ClimateLoop:
    def __init__(
        self,
        state: StateManager | None = None,
        telemetry: AutonomousTelemetry | None = None,
        earth_service: AdvancedEarthSciencesService | None = None,
    ):
        self.state = state or StateManager()
        self.telemetry = telemetry or AutonomousTelemetry()
        self.priority = PriorityScorer()
        self.novelty = NoveltyAssessor()
        self.importance_ranker = ImportanceRanker(w_freq=0.2, w_dependency=0.2, w_impact=0.6)
        self.iteration = 0
        self.rng = random.Random(999)
        
        # Advanced services for climate analysis
        self.earth_service = earth_service or AdvancedEarthSciencesService()
        self.data_lake_service = ScientificDataLakeService()
        self.database_service = AdvancedScientificDatabaseService()
        self.climate_evidence_service = ClimateEvidenceService()
        
        self._last_climate_analysis: Optional[Dict[str, Any]] = None
        self.tool_evidence = ToolEvidenceBridge(default_domain="climate")

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

    async def _fetch_real_climate_data_async(self, k: int = 7) -> List[Dict[str, Any]]:
        """Fetch real climate regions from Scientific Data Lake and Climate Evidence Service.
        
        Uses:
        - ClimateEvidenceService for temperature anomaly analysis from GISTEMP
        - ScientificDataLakeService for large-scale climate datasets
        - AdvancedScientificDatabaseService for historical hypothesis correlation
        """
        regions: List[Dict[str, Any]] = []
        
        try:
            # 1. Get climate evidence from GISTEMP data
            climate_evidence_payload = {"action": "climate_evidence"}
            evidence_result = await self.climate_evidence_service.process_request(climate_evidence_payload)
            
            if evidence_result.get("success"):
                evidence_data = evidence_result.get("data", {})
                support_score = evidence_data.get("support_score", 0.0)
                coverage = evidence_data.get("coverage", 0.0)
                mean_signal = evidence_data.get("mean_signal", 0.0)
                
                # Log climate evidence insights
                logger.info(
                    f"Climate evidence: support={support_score:.3f}, "
                    f"coverage={coverage:.3f}, signal={mean_signal:.3f}"
                )
                
                # Use evidence metrics to create high-priority regions
                if support_score > 0.5:
                    regions.append({
                        "id": f"gistemp_region_{self.iteration}_0",
                        "anomaly_index": min(1.0, float(mean_signal) / 1.5),  # Normalize signal
                        "impact_potential": float(support_score),
                        "literature_frequency": int(coverage * 100),
                        "dependency_count": 5 if support_score > 0.7 else 3,
                        "proveability": float(coverage),
                        "novelty": 0.75,  # GISTEMP data has established patterns
                        "information_gain": (support_score + coverage) / 2.0,
                        "estimated_cost": 0.1,
                        "source": "climate_evidence_service",
                        "data_source": "GISTEMP",
                        "region_bounds": {
                            "lat_min": -90.0,
                            "lat_max": 90.0,
                            "lon_min": -180.0,
                            "lon_max": 180.0,
                        },
                        "evidence_context": evidence_data.get("context", {}),
                    })
        except Exception as exc:
            logger.warning(f"ClimateEvidenceService fetch failed: {exc}")
        
        try:
            # 2. Search for related hypotheses in database
            search_payload = {
                "action": "search",
                "target": "hypothesis",
                "query": "climate temperature anomaly",
                "limit": 5,
            }
            search_result = await self.database_service.process_request(search_payload)
            
            if search_result.get("success"):
                hypotheses = search_result.get("hypotheses", [])
                for idx, hyp in enumerate(hypotheses[:3]):  # Top 3 hypotheses
                    # Extract hypothesis metrics
                    hyp_status = hyp.get("status", "pending")
                    hyp_confidence = hyp.get("confidence_score", 0.5)
                    hyp_title = hyp.get("title", f"hypothesis_{idx}")
                    
                    regions.append({
                        "id": f"hypothesis_region_{self.iteration}_{idx}",
                        "anomaly_index": float(hyp_confidence),
                        "impact_potential": 0.8 if hyp_status == "validated" else 0.5,
                        "literature_frequency": self.rng.randint(10, 50),
                        "dependency_count": 4,
                        "proveability": float(hyp_confidence),
                        "novelty": 0.85 if hyp_status == "pending" else 0.60,
                        "information_gain": (hyp_confidence + 0.5) / 2.0,
                        "estimated_cost": 0.15,
                        "source": "database_search",
                        "hypothesis_title": hyp_title,
                        "hypothesis_status": hyp_status,
                        "region_bounds": {
                            "lat_min": self.rng.uniform(-60, 30),
                            "lat_max": self.rng.uniform(30, 70),
                            "lon_min": self.rng.uniform(-150, 0),
                            "lon_max": self.rng.uniform(0, 150),
                        },
                    })
        except Exception as exc:
            logger.warning(f"Database hypothesis search failed: {exc}")
        
        try:
            # 3. Sample data from Scientific Data Lake for climate datasets
            data_lake_payload = {"action": "list_entries", "limit": 10}
            lake_result = await self.data_lake_service.process_request(data_lake_payload)
            
            if lake_result.get("success"):
                entries = lake_result.get("entries", [])
                climate_entries = [
                    e for e in entries 
                    if "climate" in e.get("name", "").lower() or "temperature" in e.get("name", "").lower()
                ]
                
                for idx, entry in enumerate(climate_entries[:2]):  # Top 2 datasets
                    entry_size = entry.get("size_bytes", 0)
                    entry_name = entry.get("name", f"dataset_{idx}")
                    
                    # Size-based impact (larger datasets = more comprehensive)
                    size_impact = min(1.0, entry_size / (100 * 1024 * 1024))  # Normalize by 100MB
                    
                    regions.append({
                        "id": f"datalake_region_{self.iteration}_{idx}",
                        "anomaly_index": 0.65,
                        "impact_potential": float(size_impact),
                        "literature_frequency": self.rng.randint(5, 40),
                        "dependency_count": 3,
                        "proveability": 0.7,
                        "novelty": 0.80,
                        "information_gain": (0.65 + size_impact) / 2.0,
                        "estimated_cost": 0.12,
                        "source": "data_lake_service",
                        "dataset_name": entry_name,
                        "dataset_size": entry_size,
                        "region_bounds": {
                            "lat_min": -75.0,
                            "lat_max": 75.0,
                            "lon_min": -170.0,
                            "lon_max": 170.0,
                        },
                    })
        except Exception as exc:
            logger.warning(f"Data Lake sampling failed: {exc}")
        
        # If we got real data, return it
        if regions:
            logger.info(f"Fetched {len(regions)} real climate regions from advanced services")
            return regions[:k]
        
        # Fallback: minimal synthetic regions only if all services fail
        logger.warning("All advanced climate services failed, using minimal synthetic fallback")
        return self._seed_synthetic_regions(k)

    def _seed_synthetic_regions(self, k: int = 7) -> List[Dict[str, Any]]:
        regions: List[Dict[str, Any]] = []
        for i in range(k):
            anomaly = self.rng.random()
            impact = self.rng.uniform(0.2, 1.0)
            lat_center = self.rng.uniform(-60, 60)
            lon_center = self.rng.uniform(-150, 150)
            bounds = {
                "lat_min": max(-90.0, lat_center - self.rng.uniform(2, 6)),
                "lat_max": min(90.0, lat_center + self.rng.uniform(2, 6)),
                "lon_min": max(-180.0, lon_center - self.rng.uniform(4, 12)),
                "lon_max": min(180.0, lon_center + self.rng.uniform(4, 12)),
            }
            regions.append(
                {
                    "id": f"region_{self.iteration}_{i}",
                    "anomaly_index": anomaly,
                    "impact_potential": impact,
                    "literature_frequency": self.rng.randint(0, 40),
                    "dependency_count": self.rng.randint(0, 5),
                    "proveability": self.rng.random(),
                    "novelty": self.rng.random(),
                    "information_gain": (anomaly + impact) / 2.0,
                    "estimated_cost": self.rng.random() * 0.2,
                    "source": "synthetic",
                    "region_bounds": bounds,
                }
            )
        return regions

    def _fetch_external_regions(self, k: int) -> List[Dict[str, Any]]:
        try:
            from app.autonomous.interfaces.external_apis import fetch_climate_anomaly_regions

            real_regions = fetch_climate_anomaly_regions(limit=k)
        except (ImportError, RuntimeError, ValueError) as exc:  # pragma: no cover - defensivo
            logger.debug("Climate anomaly external fetch failed: %s", exc)
            return []
        return [
            {
                "id": region.get("region_id", f"region_{self.iteration}_{idx}"),
                "anomaly_index": float(region.get("severity", self.rng.random())),
                "impact_potential": float(region.get("impact_score", self.rng.uniform(0.2, 1.0))),
                "literature_frequency": self.rng.randint(0, 40),
                "dependency_count": self.rng.randint(0, 5),
                "proveability": float(min(1.0, region.get("trend_significance", 0.01) * 100)),
                "novelty": self.rng.random(),
                "information_gain": float((region.get("severity", 0.5) + region.get("impact_score", 0.5)) / 2.0),
                "estimated_cost": self.rng.random() * 0.2,
                "data_source": region.get("data_source", "unknown"),
                "temporal_range": region.get("temporal_range", "2024"),
                "variables": region.get("variables", ["temperature"]),
                "region_bounds": region.get("region_bounds"),
                "source": "external_api",
            }
            for idx, region in enumerate(real_regions[:k])
        ]

    def _build_candidate_from_event(
        self,
        idx: int,
        scenario: Optional[str],
        event_type: str,
        event: Dict[str, Any],
        tipping_points: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        intensity = (event.get("intensity") or "moderate").lower()
        intensity_factor = {"moderate": 0.55, "severe": 0.75, "extreme": 0.9}.get(intensity, 0.6)
        duration = float(event.get("duration_days", 30))
        area = float(event.get("affected_area_km2", 5e4))
        anomaly = min(1.0, 0.3 + intensity_factor + duration / 365.0)
        impact = min(1.0, 0.4 + area / 500000.0 + intensity_factor / 2.0)
        novelty = max(0.1, min(1.0, 0.35 + self.rng.random() * 0.6))
        information_gain = min(1.0, 0.5 + intensity_factor / 2.0)

        lat_center = self.rng.uniform(-65, 65)
        lon_center = self.rng.uniform(-170, 170)
        bounds = {
            "lat_min": max(-90.0, lat_center - self.rng.uniform(1, 6)),
            "lat_max": min(90.0, lat_center + self.rng.uniform(1, 6)),
            "lon_min": max(-180.0, lon_center - self.rng.uniform(3, 10)),
            "lon_max": min(180.0, lon_center + self.rng.uniform(3, 10)),
        }

        tipping_point_risk = None
        if tipping_points:
            try:
                tipping_point_risk = max(
                    tipping_points.items(),
                    key=lambda item: item[1].get("exceedance_probability", 0.0),
                )
            except ValueError:
                tipping_point_risk = None

        candidate = {
            "id": event.get("event_id", f"evt_{self.iteration}_{idx}"),
            "anomaly_index": float(anomaly),
            "impact_potential": float(impact),
            "literature_frequency": self.rng.randint(5, 60),
            "dependency_count": self.rng.randint(0, 6),
            "proveability": float(min(1.0, 0.4 + intensity_factor)),
            "novelty": float(novelty),
            "information_gain": float(information_gain),
            "estimated_cost": float(self.rng.random() * 0.15 + 0.05),
            "event_type": event_type,
            "intensity": intensity,
            "duration_days": duration,
            "affected_area_km2": area,
            "scenario": scenario,
            "source": "earth_service",
            "region_bounds": bounds,
            "year": event.get("year"),
        }
        if tipping_point_risk:
            candidate["tipping_point_risk"] = {tipping_point_risk[0]: tipping_point_risk[1]}
        return candidate

    async def _fetch_climate_regions_async(self, limit: int, scenario: Optional[str]) -> List[Dict[str, Any]]:
        try:
            analysis = await self.earth_service.analyze_climate_model_cmip6(
                model_name="CESM2",
                scenario=scenario or "SSP245",
            )
        except (RuntimeError, ValueError, TimeoutError) as exc:  # pragma: no cover - defensivo
            logger.warning("Climate model analysis failed: %s", exc)
            return []

        results = analysis.get("results") or {}
        events_bundle = results.get("extreme_events") or {}
        tipping_points = results.get("tipping_points")

        events: List[tuple[str, Dict[str, Any]]] = [
            (event_type, item)
            for event_type, items in events_bundle.items()
            if isinstance(items, list)
            for item in items
        ]

        if not events:
            return []

        self._last_climate_analysis = analysis
        self.rng.shuffle(events)
        scenario_used = analysis.get("scenario") or scenario

        return [
            self._build_candidate_from_event(idx, scenario_used, event_type, event, tipping_points)
            for idx, (event_type, event) in enumerate(events[:limit])
        ]

    async def _enrich_candidate_async(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        region_bounds = candidate.get("region_bounds")
        if not region_bounds:
            return {}
        try:
            ocean = await self.earth_service.ocean_modeling_advanced(region_bounds, time_span_days=14)
        except (RuntimeError, ValueError, TimeoutError) as exc:  # pragma: no cover - defensivo
            logger.debug("Ocean modeling failed for %s: %s", candidate.get("id"), exc)
            return {"error": str(exc)}

        results = ocean.get("results") or {}
        return {
            "time_series": results.get("time_series_data"),
            "eddies": results.get("eddies"),
            "marine_heatwaves": results.get("marine_heatwaves"),
            "acidification": results.get("ocean_acidification"),
        }

    def _build_climate_hypothesis(
        self,
        region: Dict[str, Any],
        enrichment: Dict[str, Any],
        scenario: Optional[str],
    ) -> Dict[str, Any]:
        region_id = region.get("id", "region")
        description = (
            f"Validar evidencia climática multidominio para la región {region_id} bajo el escenario {scenario or 'desconocido'}."
        )
        variables: Dict[str, Any] = {
            "region_id": region_id,
            "scenario": scenario,
            "anomaly_index": region.get("anomaly_index"),
            "impact_potential": region.get("impact_potential"),
            "event_type": region.get("event_type"),
            "ocean_context": enrichment,
        }
        assumptions = [
            "Las simulaciones provienen de AdvancedEarthSciencesService",
            "Los análisis oceánicos representan condiciones proyectadas a corto plazo",
        ]
        extras = {
            "parameters": {
                "region_bounds": region.get("region_bounds"),
                "temporal_range": region.get("temporal_range"),
            },
            "keywords": [region.get("event_type", "anomaly"), scenario or "baseline"],
        }
        return self.tool_evidence.build_hypothesis(
            title=f"Corroboración clima regional {region_id}",
            description=description,
            variables=variables,
            assumptions=assumptions,
            expected_outcome="Determinar si la región merece intervención prioritaria",
            extras=extras,
        )

    async def _run_iteration_impl(
        self,
        top_n: int = 4,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        self.iteration += 1

        scenario = None
        if iteration_data:
            scenario = iteration_data.get("scenario") or iteration_data.get("climate_scenario")

        seed_count = max(top_n * 2, 6)
        
        # PRIORITY 1: Try advanced climate services (real data)
        regions = await self._fetch_real_climate_data_async(seed_count)
        
        # PRIORITY 2: Try CMIP6 climate model analysis
        if not regions or len(regions) < 3:
            logger.info("Supplementing with CMIP6 climate model data")
            cmip6_regions = await self._fetch_climate_regions_async(seed_count, scenario)
            regions.extend(cmip6_regions)
        
        # PRIORITY 3: Try external APIs
        if not regions or len(regions) < 2:
            logger.info("Supplementing with external API data")
            external_regions = self._fetch_external_regions(seed_count)
            regions.extend(external_regions)
        
        # FALLBACK: Only use synthetic if all real sources fail
        if not regions:
            logger.warning("All real data sources failed, using synthetic fallback")
            regions = self._seed_synthetic_regions(seed_count)

        ranked_importance = self.importance_ranker.rank(regions)
        scored = self.priority.rank(ranked_importance)
        selected = scored[:top_n]
        scenario_context = scenario or (
            self._last_climate_analysis.get("scenario") if self._last_climate_analysis else None
        )

        if not selected:
            logger.warning("No climate candidates available for iteration %d", self.iteration)
            return {"success": False, "reason": "no_candidates"}

        actions: List[str] = []
        outcomes: Dict[str, Any] = {}
        enriched_selected: List[Dict[str, Any]] = []
        novelty_scores: List[float] = []
        support_scores: List[float] = []

        for idx, region in enumerate(selected):
            novelty_res = self.novelty.assess(
                [region["anomaly_index"], region["impact_potential"], region["information_gain"]]
            )
            novelty_scores.append(novelty_res["novelty_score"])
            enrichment = await self._enrich_candidate_async(region) if idx < 2 else {}
            evidence_summary: Optional[EvidenceSummary] = None
            if self.tool_evidence:
                try:
                    hypothesis = self._build_climate_hypothesis(region, enrichment, scenario_context)
                    evidence_summary = await self.tool_evidence.corroborate(hypothesis, domain="climate")
                    if evidence_summary.success:
                        region["impact_potential"] = min(
                            1.0,
                            float(region.get("impact_potential", 0.4)) + evidence_summary.support_score * 0.12,
                        )
                        support_scores.append(evidence_summary.support_score)
                    else:
                        support_scores.append(0.0)
                except (RuntimeError, ValueError, ConnectionError, TimeoutError) as exc:
                    logger.debug("Climate corroboration failed for %s: %s", region.get("id"), exc)
                    support_scores.append(0.0)
            actions.append("climate_modeling")
            outcome_payload: Dict[str, Any] = {
                "novelty_score": novelty_res["novelty_score"],
                "event_type": region.get("event_type") or "anomaly_window",
                "intensity": region.get("intensity"),
                "ocean_context": enrichment or None,
            }
            if self._last_climate_analysis and idx == 0:
                analysis_results = self._last_climate_analysis.get("results", {})
                outcome_payload["analysis_summary"] = {
                    "temperature_trends": analysis_results.get("temperature_trends"),
                    "tipping_points": analysis_results.get("tipping_points"),
                }
            if evidence_summary:
                outcome_payload["tool_evidence"] = evidence_summary.as_dict()
            outcomes[region["id"]] = outcome_payload
            enriched_selected.append({**region, "enrichment": enrichment, "novelty": novelty_res})

        feedback_event = {
            "metric_name": "correlation_volume",
            "value": len(selected),
            "improved": len(selected) > 0,
            "confidence": 0.52,
        }
        feedback_result = process_feedback(feedback_event)

        record = IterationRecord(
            iteration=self.iteration,
            domain="climate",
            selected_ids=[s["id"] for s in selected],
            actions=actions,
            outcomes={**outcomes, "feedback_adjustment": feedback_result["adjustment"]},
        )
        self.state.add_iteration(record)

        duration = time.time() - start
        avg_novelty = sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0.0
        avg_support = sum(support_scores) / len(support_scores) if support_scores else 0.0
        summary = {
            "iteration": self.iteration,
            "duration_s": duration,
            "selected": len(selected),
            "actions": actions,
            "avg_novelty": avg_novelty,
            "scenario": scenario_context,
            "avg_support_score": avg_support,
        }

        try:
            self.telemetry.record_iteration(
                domain="climate",
                duration_s=duration,
                selected=len(selected),
                mutations=0,
                sketches=0,
            )
        except (ValueError, RuntimeError) as exc:  # pragma: no cover - defensivo
            logger.warning("Telemetry recording failed (climate): %s", exc)

        try:
            from app.monitoring.metrics import metrics  # Import local para evitar dependencias circulares

            metrics.set_gauge("autonomous_novelty_last", float(avg_novelty))
            metrics.set_gauge("autonomous_feedback_adjustment_last", feedback_result["adjustment"])
            if support_scores:
                metrics.set_gauge("autonomous_support_score_last", avg_support)
        except (ImportError, AttributeError):  # pragma: no cover - entorno parcial
            logger.debug("Could not set climate gauges")

        logger.info("Climate loop iteration %d: %s", self.iteration, summary)
        return {
            "success": True,
            "summary": summary,
            "selected": enriched_selected,
            "outcomes": outcomes,
            "feedback": feedback_result,
            "avg_support_score": avg_support,
        }

    def run_iteration(
        self,
        top_n: int = 4,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self._run_coro_sync(self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data))

    async def run_climate_discovery_iteration(
        self,
        top_n: int = 4,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data)


__all__ = ["ClimateLoop"]
