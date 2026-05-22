from fastapi.testclient import TestClient
from main import app
from app.observability.metrics import phase_activity

client = TestClient(app)


def _scrape():
    return client.get("/metrics").text


def test_phase_active_gauge_single_and_nested(reset_metrics):
    # Antes de cualquier fase, gauge no debe aparecer (o valor implícito 0)
    body = _scrape()
    assert "atlas_phase_active" not in body or "atlas_phase_active 0" in body

    # Fase única
    with phase_activity("analysis"):
        body = _scrape()
        assert "atlas_phase_active{phase=\"analysis\"} 1" in body
        # Gauge global
        assert "atlas_phase_active 1" in body

    # Tras salir vuelve a 0
    body = _scrape()
    assert "atlas_phase_active{phase=\"analysis\"} 0" in body or "atlas_phase_active{phase=\"analysis\"}" not in body
    assert "atlas_phase_active 0" in body or "atlas_phase_active\n" not in body

    # Dos fases concurrentes
    with phase_activity("analysis"), phase_activity("execution"):
        body = _scrape()
        assert "atlas_phase_active{phase=\"analysis\"} 1" in body
        assert "atlas_phase_active{phase=\"execution\"} 1" in body
        assert "atlas_phase_active 2" in body

    body = _scrape()
    # Debe decrementar global
    assert "atlas_phase_active 0" in body or "atlas_phase_active\n" not in body
