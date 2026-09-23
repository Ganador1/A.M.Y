import re
from app.observability.metrics import reset_metrics, observe, scrape


def test_convergence_time_labeled():
    """Genera observaciones directas de convergencia (simuladas) y verifica histogram etiquetado."""
    reset_metrics()
    # Simular 1 muestra global y 1 etiquetada
    observe("atlas_convergence_time_seconds", 0.123)
    observe("atlas_convergence_time_seconds", 0.123, labels={"phase": "refinement", "domain": "materials_science"})
    text = scrape()
    assert re.search(r"atlas_convergence_time_seconds_count \d+", text)
    # Orden alfabético de labels (domain,phase)
    assert re.search(r"atlas_convergence_time_seconds_count\{domain=\"materials_science\",phase=\"refinement\"} 1", text)
    assert "atlas_convergence_time_seconds_sum{domain=\"materials_science\",phase=\"refinement\"}" in text
