from fastapi.testclient import TestClient
from main import app
from app.observability.metrics import phase_timer, scrape, inc
import re
import time

client = TestClient(app)

def test_metrics_prometheus_endpoint():
    # Inicialmente no hay métricas registradas => scrape vacío.
    resp0 = client.get("/metrics_prom")
    assert resp0.status_code == 200
    assert resp0.text.strip() == ""  # ahora sin HELP hasta primer registro

    # Registrar feedback y fase para activar emisión
    inc("atlas_feedback_total")
    t = phase_timer(domain="genomics")
    t.start()
    time.sleep(0.01)
    t.stop("hypothesis_generation")

    # Segundo scrape vía endpoint
    resp = client.get("/metrics_prom")
    assert resp.status_code == 200
    body = resp.text

    # HELP/TYPE deben existir ahora
    assert "# TYPE atlas_feedback_total counter" in body
    assert "atlas_feedback_total" in body
    assert "# TYPE atlas_phase_duration_seconds histogram" in body

    # Histograma sin labels legacy
    assert re.search(r"atlas_phase_duration_seconds_bucket\{le=\"0.01\"}\s+\d+", body)
    # Histograma etiquetado (phase,domain) -> bucket con labels combinados
    # Basta con verificar que existe bucket etiquetado con +Inf (sin forzar orden ni valor exacto numérico repetido ya que count lo valida)
    assert "+Inf" in body and "domain=\"genomics\"" in body and "phase=\"hypothesis_generation\"" in body

    # Contadores legacy y nuevos de éxito
    assert "atlas_phase_count_hypothesis_generation" in body
    assert re.search(r"atlas_phase_success_hypothesis_generation\s+1", body)
    assert re.search(r"atlas_phase_success_total\s+\d+", body)

    # Versión etiquetada del éxito total
    assert re.search(r"atlas_phase_success_total\{domain=\"genomics\",phase=\"hypothesis_generation\"}\s+1", body)

    # Scrape directo para confirmar consistencia
    direct = scrape()
    assert body == direct
