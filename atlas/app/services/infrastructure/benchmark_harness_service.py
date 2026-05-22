"""Benchmark Harness Service (Stub)
Registro y ejecución básica de benchmarks internos para comparar estrategias/modelos.
"""
from __future__ import annotations
from typing import Callable, Dict, Any, List
import time
import statistics
from app.exceptions.domain.mathematics import MathematicsError

class BenchmarkHarnessService:
    """
    Service for registering and running performance benchmarks.
    
    Provides a framework for benchmarking different algorithms, models, and
    computational strategies. Supports registration of benchmark functions,
    execution with timing measurements, and historical tracking of results.
    
    Attributes:
        _benchmarks: Dictionary mapping benchmark names to callable functions
        _history: List of completed benchmark execution summaries
        version: Version identifier for the benchmark harness
    """
    
    def __init__(self):
        self._benchmarks: Dict[str, Callable[[], Any]] = {}
        self._history: List[Dict[str, Any]] = []
        self.version = "v0"

    def register(self, name: str, fn: Callable[[], Any]) -> None:
        self._benchmarks[name] = fn

    def list_benchmarks(self) -> List[str]:
        return sorted(self._benchmarks.keys())

    def run(self, name: str, repeats: int = 1) -> Dict[str, Any]:
        if name not in self._benchmarks:
            raise ValueError(f"Benchmark no registrado: {name}")
        fn = self._benchmarks[name]
        durations: List[float] = []
        results: List[Any] = []
        for _ in range(repeats):
            start = time.perf_counter()
            try:
                res = fn()
                ok = True
            except MathematicsError as e:  # noqa: BLE001 - stub
                res = e
                ok = False
            end = time.perf_counter()
            durations.append(end - start)
            results.append(res)
            if not ok:
                break  # detener si falla
        summary = {
            "name": name,
            "repeats": len(durations),
            "mean_s": statistics.mean(durations) if durations else None,
            "stdev_s": statistics.pstdev(durations) if len(durations) > 1 else 0.0,
            "min_s": min(durations) if durations else None,
            "max_s": max(durations) if durations else None,
            "last_result": results[-1] if results else None,
            "error": isinstance(results[-1], Exception) if results else False,
        }
        self._history.append(summary)
        return summary

    def history(self) -> List[Dict[str, Any]]:
        return list(self._history)

benchmark_harness_service = BenchmarkHarnessService()
