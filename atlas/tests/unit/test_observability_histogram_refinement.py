import re
import time
from app.observability import metrics


def test_histogram_multiple_observations_and_refinement_counters():
    metrics.reset_metrics()
    # Simular diversas duraciones en buckets distintos
    durations = [0.005, 0.02, 0.08, 0.2, 0.7, 1.2]  # cubre varios buckets
    for d in durations:
        t = metrics.phase_timer()
        t.start()
        time.sleep(d)
        t.stop("analysis")  # reutilizamos etiqueta de fase existente
    # Simular refinamiento (incrementos directos)
    for _ in range(3):
        metrics.inc("atlas_refinement_iterations_total")
    metrics.inc("atlas_refinement_cycles_total")

    body = metrics.scrape()

    # Verificar contador de refinamiento
    assert "atlas_refinement_iterations_total 3" in body or "atlas_refinement_iterations_total 3.0" in body
    assert "atlas_refinement_cycles_total 1" in body or "atlas_refinement_cycles_total 1.0" in body

    # Capturar líneas de buckets
    bucket_lines = [line for line in body.splitlines() if line.startswith("atlas_phase_duration_seconds_bucket")]
    assert bucket_lines, "Debe existir histograma"

    # Validar monotonicidad acumulativa
    counts = []
    for line in bucket_lines:
        m = re.search(r"le=\"(.*?)\"} (\d+)$", line)
        if not m:
            continue
        le, val = m.group(1), int(m.group(2))
        counts.append((le, val))
    # Último bucket +Inf debe igualar número de observaciones
    assert counts[-1][0] == "+Inf"
    assert counts[-1][1] == len(durations)
    # Monotonicidad
    prev = -1
    for _, v in counts:
        assert v >= prev
        prev = v

    # Verificar sum y count
    assert re.search(r"atlas_phase_duration_seconds_sum ", body)
    assert re.search(r"atlas_phase_duration_seconds_count 6", body)
