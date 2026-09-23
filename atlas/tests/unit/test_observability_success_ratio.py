import re
from app.observability import metrics


def test_success_ratio_updates():
    metrics.reset_metrics()

    # Simular dos fases con 2 éxitos y 1 fallo
    # Éxito 1
    metrics.set_time_provider(lambda: 0.0)
    t = metrics.phase_timer()
    t.start()
    metrics.set_time_provider(lambda: 1.0)
    t.stop("analysis")

    # Éxito 2
    metrics.set_time_provider(lambda: 2.0)
    t2 = metrics.phase_timer()
    t2.start()
    metrics.set_time_provider(lambda: 3.0)
    t2.stop("analysis")

    # Fallo manual: incrementar fallo para misma fase
    metrics.inc("atlas_phase_failures_total", labels={"phase": "analysis"})

    # Forzar actualización ratio explícita (en stop ya se llama, pero por claridad)
    metrics.update_phase_success_ratio("analysis")

    out = metrics.scrape()
    # Buscar gauge ratio con label (2 éxitos / 3 total = 0.666...)
    assert re.search(r"atlas_phase_success_ratio{phase=\"analysis\"} 0\.66666", out)
    # Ratio global (global = 2/(2) porque no registramos fallos globales sin labels => 1.0 presente)
    # Verificamos explícitamente valor global 1.0
    assert re.search(r"^atlas_phase_success_ratio 1\.0", out, re.MULTILINE)
