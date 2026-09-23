from app.services.benchmark_harness_service import benchmark_harness_service

def test_benchmark_registration_and_run():
    def sample():
        return 42
    benchmark_harness_service.register("sample", sample)
    summary = benchmark_harness_service.run("sample", repeats=2)
    assert summary["name"] == "sample"
    assert summary["repeats"] == 2
    assert summary["mean_s"] >= 0.0


def test_benchmark_failure_short_circuit():
    calls = {"n": 0}
    def failing():  # noqa: D401
        calls["n"] += 1
        raise RuntimeError("boom")
    benchmark_harness_service.register("fail_once", failing)
    summary = benchmark_harness_service.run("fail_once", repeats=3)
    assert summary["repeats"] == 1  # se detiene tras fallo
    assert summary["error"] is True
