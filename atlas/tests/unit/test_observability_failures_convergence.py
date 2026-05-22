import re
from app.observability import metrics

def test_failures_and_convergence_histogram():
    metrics.reset_metrics()
    # Simular fallos en distintas fases
    for phase in ["analysis", "validation", "refinement"]:
        metrics.inc("atlas_phase_failures_total")
        metrics.inc(f"atlas_phase_failures_{phase}")
    # Simular tiempo de convergencia (tres observaciones artificiales)
    for d in [0.02, 0.05, 0.15]:
        # Fake observe directamente (no necesitamos ciclo real)
        metrics.observe("atlas_convergence_time_seconds", d)  # type: ignore
    body = metrics.scrape()
    # Verificar counters fallos totales y específicos
    assert "atlas_phase_failures_total 3" in body or "atlas_phase_failures_total 3.0" in body
    assert re.search(r"atlas_phase_failures_analysis ", body)
    assert re.search(r"atlas_phase_failures_validation ", body)
    assert re.search(r"atlas_phase_failures_refinement ", body)
    # Verificar histograma convergencia
    lines = [line for line in body.splitlines() if line.startswith("atlas_convergence_time_seconds_bucket")]
    assert lines, "Histograma convergencia ausente"
    assert any('le="+Inf"' in line and line.strip().endswith('3') for line in lines)
    assert re.search(r"atlas_convergence_time_seconds_count 3", body)
    assert re.search(r"atlas_convergence_time_seconds_sum ", body)
