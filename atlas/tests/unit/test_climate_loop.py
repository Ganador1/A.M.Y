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
