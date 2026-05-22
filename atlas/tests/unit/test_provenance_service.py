import pytest

from app.services.provenance import ProvenanceService
from app.services.experiment_tracking import ExperimentTrackingService
from app.services.data_versioning import DataVersioningService


@pytest.mark.asyncio
async def test_build_all_experiments_graph_empty():
    prov = ProvenanceService()
    exp = ExperimentTrackingService()
    data = DataVersioningService()

    result = prov.build_all_experiments_graph(exp_service=exp, data_service=data, render_html=False)

    assert result["success"] is True
    assert "graph" in result
    assert "nodes" in result["graph"]
    assert "edges" in result["graph"]


@pytest.mark.asyncio
async def test_build_single_experiment_graph_flow():
    # Arrange: crear experimento y un artefacto mínimo
    exp = ExperimentTrackingService()
    start = await exp.process_request({
        "action": "start_experiment",
        "name": "prov-test-exp",
        "parameters": {"alpha": 0.1}
    })
    assert start["success"]
    exp_id = start["experiment_id"]

    # No necesitamos artefactos reales para el grafo básico
    prov = ProvenanceService()
    data = DataVersioningService()

    result = prov.build_experiment_graph(exp_service=exp, experiment_id=exp_id, data_service=data, render_html=False)
    assert result["success"] is True
    assert result["counts"]["nodes"] >= 1
