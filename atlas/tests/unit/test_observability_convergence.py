from fastapi.testclient import TestClient
from main import app
from app.observability import metrics as obs_metrics
import re

client = TestClient(app)


def _scrape():
    return client.get("/metrics").text


def test_convergence_time_metric_records(reset_metrics):
    # Simular tiempos medidos de convergencia (tres ejecuciones)
    for t in [0.05, 0.11, 0.4]:
        obs_metrics.observe("atlas_convergence_time_seconds", t)
    body = _scrape()
    assert "# TYPE atlas_convergence_time_seconds histogram" in body
    # count=3 y sum ~0.56
    assert "atlas_convergence_time_seconds_count 3" in body
    assert re.search(r"atlas_convergence_time_seconds_sum .*0.56", body) or "0.560000" in body
    # Bucket +Inf debe ser 3
    assert "atlas_convergence_time_seconds_bucket{le=\"+Inf\"} 3" in body
