"""Orquestador del dominio Astronomy.

Centraliza las llamadas a los servicios avanzados del dominio y aporta
funcionalidades de fusión de resultados para entregar respuestas ricas a la
capa de routing y a otros componentes del ecosistema AXIOM.
"""

from __future__ import annotations

import asyncio
import statistics
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import numpy as np

from app.domains.astronomy.astronomy_computational_service import (
    AstronomyComputationalService,
)
from app.domains.astronomy.astronomy_light_curves import AstronomyLightCurveService
from app.domains.astronomy.domain_config import DOMAIN_INFO, DOMAIN_SETTINGS
from app.domains.astronomy.utils.coordinates import AstronomicalCoordinates, DistanceUtils
from app.domains.astronomy.utils.data_analysis import (
    LightCurveAnalysis,
    PhotometryUtils,
    StatisticalAnalysis,
)


@dataclass(frozen=True)
class TelescopeContext:
    """Contexto derivado para peticiones de telescopios."""

    telescope_name: str
    data_type: str
    coordinates: Dict[str, Any]
    observation_parameters: Dict[str, Any]
    user_id: Optional[str] = None


class AstronomyDomainOrchestrator:
    """Coordina servicios internos del dominio Astronomy."""

    def __init__(
        self,
        *,
        computation_service: Optional[AstronomyComputationalService] = None,
        light_curve_service: Optional[AstronomyLightCurveService] = None,
    ) -> None:
        self._computation_service = computation_service or AstronomyComputationalService()
        self._light_curve_service = light_curve_service or AstronomyLightCurveService()

    # ---------------------------------------------------------------------
    # Telescopio & observaciones
    # ---------------------------------------------------------------------
    async def analyze_telescope_data(self, ctx: TelescopeContext) -> Dict[str, Any]:
        """Analiza una solicitud de observación telescópica."""

        coordinates = ctx.coordinates or {}
        cartesian = self._coordinates_to_cartesian(coordinates)
        quality_metrics = self._extract_quality_metrics(ctx.observation_parameters)

        time_series = self._extract_time_series(ctx.observation_parameters)
        light_curve_result: Optional[Dict[str, Any]] = None

        if time_series:
            light_curve_result = await self._run_light_curve_analysis(time_series)
            quality_metrics.setdefault("light_curve", {})["variability"] = (
                light_curve_result.get("variability_metrics")
            )

        return {
            "domain": DOMAIN_INFO.name,
            "version": DOMAIN_INFO.version,
            "telescope": {
                "name": ctx.telescope_name,
                "data_type": ctx.data_type,
                "supported": ctx.data_type in DOMAIN_SETTINGS["supported_telescopes"],
            },
            "coordinates": {
                "input": coordinates,
                "cartesian": cartesian,
            },
            "quality_metrics": quality_metrics,
            "light_curve_analysis": light_curve_result,
            "user_id": ctx.user_id,
        }

    # ---------------------------------------------------------------------
    # Simulaciones
    # ---------------------------------------------------------------------
    async def run_simulation(
        self,
        simulation_type: str,
        parameters: Dict[str, Any],
        time_steps: int,
        spatial_resolution: float,
        *,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Genera resultados sintéticos y métricas para simulaciones astronómicas."""

        rng = np.random.default_rng(seed=parameters.get("seed", 42))
        timeline = np.linspace(0, time_steps, num=min(time_steps, 512))
        energy_profile = rng.normal(loc=1.0, scale=0.05, size=timeline.size)
        stability_index = float(np.clip(1 - np.std(energy_profile), 0.0, 1.0))

        performance = {
            "time_steps": time_steps,
            "spatial_resolution": spatial_resolution,
            "estimated_runtime_seconds": float(time_steps * spatial_resolution * 0.05),
            "stability_index": stability_index,
        }

        return {
            "simulation_type": simulation_type,
            "parameters": parameters,
            "timeline": timeline.tolist(),
            "energy_profile": energy_profile.tolist(),
            "performance": performance,
            "user_id": user_id,
        }

    # ---------------------------------------------------------------------
    # Exoplanetas
    # ---------------------------------------------------------------------
    async def detect_exoplanets(
        self,
        star_name: str,
        method: str,
        time_series_data: List[Dict[str, Any]],
        detection_parameters: Dict[str, Any],
        *,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Combina detección avanzada y análisis BLS para candidatos exoplanetarios."""

        if not time_series_data:
            return {
                "star": star_name,
                "method": method,
                "success": False,
                "error": "time_series_data vacío",
            }

        stellar_params = detection_parameters.get("stellar_parameters", {})
        light_curve_payload = self._build_light_curve_payload(time_series_data, star_name)

        tasks = [
            self._computation_service.process_request(
                self._build_exoplanet_request(method, time_series_data, stellar_params)
            ),
            self._light_curve_service.process_request(light_curve_payload),
        ]

        comp_result, lc_result = await asyncio.gather(*tasks)

        candidates = comp_result.get("transit_candidates") or []
        lc_metrics = lc_result.get("results", {})

        return {
            "star": star_name,
            "method": method,
            "success": comp_result.get("success", False),
            "transit_candidates": candidates,
            "computational_summary": {
                "algorithms_used": comp_result.get("algorithms_used", {}),
                "statistics": comp_result.get("detection_statistics", {}),
                "false_positive_analysis": comp_result.get("false_positive_analysis", {}),
            },
            "light_curve_analysis": lc_metrics,
            "aggregated_confidence": self._aggregate_confidence(candidates),
            "user_id": user_id,
        }

    # ---------------------------------------------------------------------
    # Galaxias, cosmología y formación estelar
    # ---------------------------------------------------------------------
    async def analyze_galaxy(
        self,
        galaxy_name: str,
        analysis_type: str,
        data_sources: Iterable[str],
        parameters: Dict[str, Any],
        *,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Entrega un resumen rico de análisis galáctico."""

        photometry = parameters.get("photometry", {})
        color_index = None
        if "g" in photometry and "r" in photometry:
            color_index = PhotometryUtils.calculate_color(photometry["g"], photometry["r"])

        morphology = {
            "classification": parameters.get("morphology", "unknown"),
            "axis_ratio": parameters.get("axis_ratio", 0.8),
            "color_index_g_r": color_index,
        }

        kinematics = {
            "rotation_curve_kms": parameters.get("rotation_curve_kms", []),
            "velocity_dispersion": parameters.get("sigma_v", 120),
        }

        return {
            "galaxy": galaxy_name,
            "analysis_type": analysis_type,
            "data_sources": list(data_sources),
            "morphological_parameters": morphology,
            "kinematic_analysis": kinematics,
            "derived_quantities": {
                "stellar_mass_log": parameters.get("stellar_mass_log", 10.5),
                "star_formation_rate": parameters.get("sfr", 1.2),
            },
            "user_id": user_id,
        }

    async def analyze_cosmology(
        self,
        dataset: str,
        analysis_type: str,
        parameters: Dict[str, Any],
        *,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Genera estadísticas cosmológicas derivadas simples."""

        if posterior_samples := parameters.get("posterior_samples"):
            omega_m = float(statistics.mean(sample[0] for sample in posterior_samples))
            omega_lambda = float(statistics.mean(sample[1] for sample in posterior_samples))
        else:
            omega_m = parameters.get("omega_m", 0.31)
            omega_lambda = parameters.get("omega_lambda", 0.69)

        return {
            "dataset": dataset,
            "analysis_type": analysis_type,
            "cosmological_parameters": {
                "omega_m": omega_m,
                "omega_lambda": omega_lambda,
                "h0": parameters.get("h0", 67.4),
            },
            "statistical_analysis": {
                "evidence_ratio": parameters.get("evidence_ratio", 1.05),
                "effective_samples": parameters.get("n_eff", 2048),
            },
            "model_comparison": parameters.get("model_comparison"),
            "confidence_intervals": parameters.get(
                "confidence_intervals",
                {"omega_m": [omega_m - 0.02, omega_m + 0.02]},
            ),
            "user_id": user_id,
        }

    async def analyze_star_formation(
        self,
        region_coordinates: Dict[str, Any],
        data_sources: Iterable[str],
        analysis_parameters: Dict[str, Any],
        *,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calcula métricas simples de formación estelar."""

        clouds = analysis_parameters.get("molecular_clouds", [])
        sfr = float(sum(cloud.get("sfr", 0.0) for cloud in clouds))
        densities = [cloud.get("density", 0.0) for cloud in clouds]
        avg_density = float(statistics.mean(densities)) if densities else 0.0

        distance_pc = DistanceUtils.parallax_to_distance(region_coordinates.get("parallax", 0.001))

        return {
            "region": region_coordinates,
            "data_sources": list(data_sources),
            "star_formation_rate": sfr,
            "molecular_clouds": clouds,
            "stellar_populations": analysis_parameters.get("stellar_populations", {}),
            "environmental_analysis": {
                "mean_cloud_density": avg_density,
                "distance_pc": distance_pc,
            },
            "user_id": user_id,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    async def _run_light_curve_analysis(
        self, time_series: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        times = [point["time"] for point in time_series]
        flux = [point["flux"] for point in time_series]

        payload = {
            "operation": "bls_analysis",
            "time": times,
            "flux": flux,
            "target_name": "synthetic",
        }

        result = await self._light_curve_service.process_request(payload)
        results_payload = result.get("results", {})

        variability_metrics = LightCurveAnalysis.calculate_variability(flux)

        return {
            "service": result.get("service"),
            "analysis": results_payload,
            "variability_metrics": variability_metrics,
        }

    def _extract_time_series(
        self, observation_parameters: Dict[str, Any]
    ) -> List[Dict[str, float]]:
        time_series = observation_parameters.get("time_series") or []
        return [
            {"time": float(point["time"]), "flux": float(point["flux"])}
            for point in time_series
            if "time" in point and "flux" in point
        ]

    def _coordinates_to_cartesian(self, coordinates: Dict[str, Any]) -> Dict[str, float]:
        if not coordinates:
            return {}

        ra = float(coordinates.get("ra", 0.0))
        dec = float(coordinates.get("dec", 0.0))
        distance = float(coordinates.get("distance", 1.0))
        x, y, z = AstronomicalCoordinates.ra_dec_to_cartesian(ra, dec, distance)
        return {"x": x, "y": y, "z": z}

    def _extract_quality_metrics(
        self, observation_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        exposure_times = observation_parameters.get("exposure_times", [])
        filters = observation_parameters.get("filters", [])
        seeing = observation_parameters.get("seeing_arcsec")

        stats = {}
        if exposure_times:
            stats["exposure"] = StatisticalAnalysis.calculate_uncertainty(exposure_times)
        if seeing is not None:
            stats["seeing_arcsec"] = seeing
        if filters:
            stats["filters"] = filters
        stats["data_points"] = observation_parameters.get("n_points", len(exposure_times))

        return stats

    def _aggregate_confidence(self, candidates: Iterable[Dict[str, Any]]) -> float:
        confidences = [cand.get("confidence", 0.0) for cand in candidates]
        return float(sum(confidences) / len(confidences)) if confidences else 0.0

    def _build_light_curve_payload(
        self, time_series_data: List[Dict[str, Any]], target_name: str
    ) -> Dict[str, Any]:
        return {
            "operation": "bls_analysis",
            "time": [float(p["time"]) for p in time_series_data],
            "flux": [float(p["flux"]) for p in time_series_data],
            "target_name": target_name,
        }

    def _build_exoplanet_request(
        self,
        method: str,
        time_series_data: List[Dict[str, Any]],
        stellar_parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        operation = "exoplanet_detection"
        if len(time_series_data) < self._computation_service.advanced_config["min_data_points"]:
            operation = "exoplanet_transit"

        return {
            "operation": operation,
            "method": method,
            "light_curve": time_series_data,
            "stellar_parameters": stellar_parameters,
            "use_ml": operation == "exoplanet_detection",
        }
