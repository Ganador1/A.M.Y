import csv
from pathlib import Path

import pytest

from app.autonomous.integration import ToolEvidenceBridge
from app.autonomous.pipelines.climate_loop import ClimateLoop
from app.monitoring.metrics import metrics
from app.services.advanced_earth_sciences_service import AdvancedEarthSciencesService


@pytest.fixture(autouse=True)
def reset_metrics():
    metrics.reset()
    yield
    metrics.reset()


@pytest.fixture()
def climate_dataset_path() -> Path:
    return Path(__file__).resolve().parents[2] / "real_data_tests" / "climate_nasa_gistemp.csv"


@pytest.fixture()
def real_climate_loop(climate_dataset_path: Path) -> ClimateLoop:
    service = AdvancedEarthSciencesService(
        config={
            "simulation": False,
            "gistemp_csv_path": str(climate_dataset_path),
        }
    )
    loop = ClimateLoop(earth_service=service)
    loop.tool_evidence = ToolEvidenceBridge(default_domain="climate")
    return loop


@pytest.mark.asyncio
async def test_climate_loop_uses_real_dataset(real_climate_loop: ClimateLoop):
    result = await real_climate_loop._run_iteration_impl(top_n=2, iteration_data={"scenario": "observed"})

    assert result["success"] is True
    assert result["avg_support_score"] > 0.0
    assert metrics.gauges["autonomous_support_score_last"] == pytest.approx(result["avg_support_score"])
    assert all(candidate["source"] == "earth_service" for candidate in result["selected"])

    analysis = real_climate_loop._last_climate_analysis
    assert analysis is not None
    assert analysis["simulation_mode"] is False
    assert "temperature_trends" in analysis["results"]
    assert all(isinstance(candidate["novelty"]["novelty_score"], float) for candidate in result["selected"])

    # Compare retained analysis with the actual CSV, rather than synthetic
    # candidates or an expected array invented by the test.
    with real_climate_loop.earth_service.gistemp_csv_path.open() as handle:
        next(handle)
        annual = {
            int(row["Year"]): float(row["J-D"])
            for row in csv.DictReader(handle)
            if row["J-D"] != "***"
        }
    trends = analysis["results"]["temperature_trends"]
    assert trends["global_temp_anomaly"] == [annual[year] for year in trends["years"]]


@pytest.mark.asyncio
async def test_climate_tool_evidence_bridge_returns_support(real_climate_loop: ClimateLoop):
    hypothesis = real_climate_loop.tool_evidence.build_hypothesis(
        title="Validación climática global",
        description="Evaluar tendencia reciente de anomalías de temperatura con datos GISTEMP",
        expected_outcome="Confirmar tendencia positiva sostenida",
        extras={"domain": "climate"},
    )

    summary = await real_climate_loop.tool_evidence.corroborate(hypothesis, domain="climate")

    assert summary.success is True
    assert summary.support_score > 0.0
    assert summary.mean_signal >= 0.0
    evidence_items = summary.raw_result.get("evidence_items", [])
    assert evidence_items, "Se esperaba al menos una pieza de evidencia real"
    analysis = evidence_items[0].get("raw_result", {}).get("analysis")
    assert analysis is not None
    assert analysis.get("window_years", 0) >= 1


@pytest.mark.asyncio
async def test_climate_candidates_read_actual_evidence_contract(real_climate_loop: ClimateLoop):
    candidates = await real_climate_loop._fetch_real_climate_data_async(k=2)

    observed = [candidate for candidate in candidates if candidate["source"] == "climate_evidence_service"]
    assert observed
    assert observed[0]["data_source"] == "GISTEMP"
    assert observed[0]["evidence_context"]["window_years"] == 30
    assert observed[0]["impact_potential"] > 0.5
    assert all(candidate["source"] != "synthetic" for candidate in candidates)


@pytest.mark.asyncio
async def test_missing_observed_dataset_does_not_become_simulation(tmp_path, monkeypatch):
    service = AdvancedEarthSciencesService(
        config={"simulation": False, "gistemp_csv_path": str(tmp_path / "missing.csv")}
    )
    loop = ClimateLoop(earth_service=service)

    def forbid_synthetic(*args, **kwargs):
        raise AssertionError("Observed mode must not fabricate replacement data")

    monkeypatch.setattr(loop, "_seed_synthetic_regions", forbid_synthetic)
    result = await loop._run_iteration_impl(top_n=2, iteration_data={"scenario": "observed"})

    assert result == {"success": False, "reason": "no_observed_climate_data"}
    assert loop._last_climate_analysis is None
    assert loop.climate_evidence_service._gistemp_path == service.gistemp_csv_path
