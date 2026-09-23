from app.observability import metrics


def test_cardinality_limit_counters(reset_metrics):
    # Generar más series de las permitidas
    limit = 55
    for i in range(limit):
        metrics.inc("atlas_test_counter", labels={"id": f"x{i}"})
    data = metrics.scrape()
    # Debe existir overflow
    assert "atlas_test_counter{overflow=\"true\"}" in data
    # Contar series reales sin overflow no debe exceder 50
    lines = [line for line in data.splitlines() if line.startswith("atlas_test_counter{") and 'overflow="true"' not in line]
    assert len(lines) <= 50


def test_cardinality_limit_histograms(reset_metrics):
    for i in range(60):
        metrics.observe("atlas_test_hist", 0.1, labels={"id": f"h{i}"})
    data = metrics.scrape()
    # Debe existir bucket overflow
    assert "atlas_test_hist_bucket{overflow=\"true\",le=" in data


def test_cardinality_limit_gauges(reset_metrics):
    for i in range(70):
        metrics.gauge_set("atlas_test_gauge", i, labels={"id": f"g{i}"})
    data = metrics.scrape()
    assert "atlas_test_gauge{overflow=\"true\"}" in data
    # No más de 50 gauges distintas sin overflow
    lines = [line for line in data.splitlines() if line.startswith("atlas_test_gauge{") and 'overflow="true"' not in line]
    assert len(lines) <= 50
