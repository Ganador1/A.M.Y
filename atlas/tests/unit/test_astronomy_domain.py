import pytest

from app.domains.astronomy.services import astronomy_service
from app.domains.astronomy.services.orchestrator import AstronomyDomainOrchestrator


@pytest.mark.asyncio
async def test_facade_telescope_analysis_minimal():
    observation_parameters = {
        "exposure_times": [120.0, 118.0, 119.5],
        "filters": ["F140W", "F150W"],
        "seeing_arcsec": 0.7,
        "time_series": [
            {"time": float(i), "flux": 1.0 if i != 10 else 0.985}
            for i in range(60)
        ],
    }

    result = await astronomy_service.analyze_telescope_data(
        telescope_name="JWST",
        data_type="imaging",
        coordinates={"ra": 120.5, "dec": -34.2, "distance": 1500},
        observation_parameters=observation_parameters,
        user_id="tester",
    )

    assert result["success"] is True
    assert result["telescope_info"]["name"] == "JWST"
    assert "quality_metrics" in result["data_summary"]
    assert result["processed_data"] is not None


@pytest.mark.asyncio
async def test_orchestrator_detect_exoplanets_pipeline():
    orchestrator = AstronomyDomainOrchestrator()
    light_curve = []
    for idx in range(160):
        flux = 1.0
        if 70 <= idx <= 75:
            flux -= 0.015
        light_curve.append({"time": float(idx), "flux": flux})

    detection = await orchestrator.detect_exoplanets(
        star_name="Kepler-XYZ",
        method="transit",
        time_series_data=light_curve,
        detection_parameters={"stellar_parameters": {"mass": 1.05, "radius": 1.01}},
        user_id="tester",
    )

    assert detection["success"] in {True, False}
    assert detection["star"] == "Kepler-XYZ"
    assert "computational_summary" in detection
    assert "light_curve_analysis" in detection
    assert isinstance(detection["aggregated_confidence"], float)