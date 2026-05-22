import re
from app.observability.metrics import reset_metrics, set_time_provider, reset_time_provider, phase_timer, scrape


def test_phase_timer_deterministic():
    """Verifica que PhaseTimer use proveedor de tiempo inyectado sin sleeps."""
    reset_metrics()
    fake_t = [1000.0]
    def fake_time():
        return fake_t[0]
    set_time_provider(fake_time)
    try:
        t = phase_timer(domain="materials_science")
        t.start()
        fake_t[0] += 0.25  # avanzar tiempo simulado
        t.stop("analysis")
        text = scrape()
        assert re.search(r"atlas_phase_duration_seconds_count\{domain=\"materials_science\",phase=\"analysis\"} 1", text)
        assert re.search(r"atlas_phase_duration_seconds_sum\{domain=\"materials_science\",phase=\"analysis\"} 0\.25", text)
    finally:
        reset_time_provider()
