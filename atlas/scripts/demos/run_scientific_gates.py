#!/usr/bin/env python3
"""Scientific gates (initial placeholder).

Current checks:
 - Dataset plausibility CSV exists and has at least MIN_ROWS lines (including header)
 - Metrics file exists (if defined) and contains required keys

Exit codes:
 0 OK
 1 Failed gate
 2 Usage / unexpected error
"""
from __future__ import annotations
import pathlib
import json
import sys
import csv

MIN_ROWS = 50
DATASET_PATH = pathlib.Path("data/plausibility_training.csv")
METRICS_PATH = pathlib.Path("reports/model_metrics.json")  # optional placeholder
REQUIRED_METRICS = {"accuracy", "f1"}

def fail(msg: str) -> int:
    print(f"[GATE][FAIL] {msg}", file=sys.stderr)
    return 1

def main() -> int:
    # 1. Dataset presence & size
    if not DATASET_PATH.is_file():
        return fail(f"No existe dataset requerido: {DATASET_PATH}")
    try:
        with DATASET_PATH.open("r", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            count = sum(1 for _ in reader) - 1  # minus header
    except Exception as e:  # noqa: BLE001
        return fail(f"Error leyendo dataset: {e}")
    if count < MIN_ROWS:
        return fail(f"Dataset insuficiente filas={count} < {MIN_ROWS}")
    print(f"[GATE] Dataset OK filas={count}")

    # 2. Metrics file (optional - warn if missing, fail if present but incomplete)
    if METRICS_PATH.is_file():
        try:
            metrics = json.loads(METRICS_PATH.read_text(encoding='utf-8'))
        except Exception as e:  # noqa: BLE001
            return fail(f"Error leyendo métricas: {e}")
        missing = REQUIRED_METRICS - set(metrics.keys())
        if missing:
            return fail(f"Métricas faltantes: {sorted(missing)}")
        print("[GATE] Métricas OK")
    else:
        print(f"[GATE][WARN] Archivo de métricas no encontrado: {METRICS_PATH}")

    print("[GATE] Scientific gates PASSED")
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
