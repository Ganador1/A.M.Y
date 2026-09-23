from fastapi.testclient import TestClient
from main import app
from app.observability import metrics as obs_metrics

client = TestClient(app)


def test_metrics_endpoint_prometheus_format(reset_metrics):
    # Inicializar métricas mínimas para asegurar que aparezca atlas_phase_success_ratio
    obs_metrics.inc("atlas_phase_success_total", labels={"phase": "analysis"})
    obs_metrics.update_phase_success_ratio("analysis")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    ctype = resp.headers.get("content-type", "")
    assert ctype.startswith("text/plain") and "version=0.0.4" in ctype
    body = resp.text
    # Debe contener HELP y TYPE de al menos una métrica nueva
    assert "# HELP atlas_phase_success_ratio" in body
    assert "# TYPE atlas_phase_success_ratio gauge" in body
    # Verificar que no esté vacío
    assert len(body.splitlines()) > 5


def test_metrics_summary_legacy(reset_metrics):
    resp = client.get("/metrics_summary")
    assert resp.status_code == 200
    data = resp.json()
    # Debe incluir claves conocidas del summary legacy si existen
    assert isinstance(data, dict)


def test_metrics_prom_alias_deprecation_header(reset_metrics):
    resp = client.get("/metrics_prom")
    assert resp.status_code == 200
    assert resp.headers.get("Deprecation") == "true"
    assert "/metrics" in resp.headers.get("Link", "")
