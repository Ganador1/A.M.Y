from fastapi.testclient import TestClient
from main import app
from app.observability import metrics as obs_metrics
import re

client = TestClient(app)


def _scrape():
    return client.get("/metrics").text


def test_cycle_total_duration_histogram_records_values(reset_metrics):
    # Simulamos tres ciclos completos con duraciones distintas
    for d in [0.12, 0.6, 1.3]:
        obs_metrics.observe("atlas_cycle_total_duration_seconds", d)
    body = _scrape()
    assert "# TYPE atlas_cycle_total_duration_seconds histogram" in body
    # Debe tener count=3 y sum aproximadamente 0.12+0.6+1.3=2.02
    # Línea exacta count
    assert "atlas_cycle_total_duration_seconds_count 3" in body
    assert re.search(r"atlas_cycle_total_duration_seconds_sum .*2.02", body) or "2.020000" in body


def test_refinement_iterations_per_cycle_histogram(reset_metrics):
    # Simulamos distribución: 1,2,5 iteraciones
    for v in [1, 2, 5]:
        obs_metrics.observe("atlas_refinement_iterations_per_cycle", float(v))
    body = _scrape()
    assert "# TYPE atlas_refinement_iterations_per_cycle histogram" in body
    assert "atlas_refinement_iterations_per_cycle_count 3" in body
    # Bucket +Inf debe ser 3
    # Línea bucket +Inf exacta
    assert "atlas_refinement_iterations_per_cycle_bucket{le=\"+Inf\"} 3" in body
