#!/usr/bin/env python
"""Ejecuta validaciones de datos usando Great Expectations (modo ligero).

Busca un dataset CSV de ejemplo en data/ o datasets/ (primer *.csv encontrado) y ejecuta
la suite plausibility_training_basic si existe. Genera:
- data_quality/data_validation_report.json: resultado consolidado
- data_quality/data_validation.fail.json: presente sólo si alguna expectativa falla

Exit codes:
- 0 si todas las expectativas pasan
- 1 si falla alguna o hay errores
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any, Dict

try:
    import great_expectations as ge
except ImportError as exc:  # pragma: no cover
    print("Great Expectations no instalado", file=sys.stderr)
    raise SystemExit(1) from exc

BASE_DIR = Path(__file__).resolve().parent.parent
DQ_DIR = BASE_DIR / "data_quality"
EXPECTATIONS_DIR = DQ_DIR / "expectations"
REPORT_PATH = DQ_DIR / "data_validation_report.json"
FAIL_PATH = DQ_DIR / "data_validation.fail.json"


def find_dataset() -> Path | None:
    candidates = []
    for folder in [BASE_DIR / "data", BASE_DIR / "datasets"]:
        if folder.exists():
            candidates.extend(folder.glob("*.csv"))
    return candidates[0] if candidates else None


def load_suite(name: str) -> Dict[str, Any] | None:
    suite_file = EXPECTATIONS_DIR / f"{name}.json"
    if not suite_file.exists():
        return None
    return json.loads(suite_file.read_text(encoding="utf-8"))


def run_suite(df, suite: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore[no-untyped-def]
    ge_df = ge.from_pandas(df)
    results = []
    all_passed = True
    for exp in suite.get("expectations", []):
        exp_type = exp.get("expectation_type")
        kwargs = exp.get("kwargs", {})
        method = getattr(ge_df, exp_type, None)
        if method is None:
            results.append({"expectation_type": exp_type, "success": False, "error": "unsupported"})
            all_passed = False
            continue
        try:
            r = method(**kwargs)
            success = bool(r.get("success"))
            if not success:
                all_passed = False
            results.append({
                "expectation_type": exp_type,
                "kwargs": kwargs,
                "success": success,
            })
        except Exception as e:  # pragma: no cover
            all_passed = False
            results.append({"expectation_type": exp_type, "kwargs": kwargs, "success": False, "error": str(e)})
    return {"results": results, "success": all_passed}


def main() -> int:
    DQ_DIR.mkdir(parents=True, exist_ok=True)
    suite = load_suite("plausibility_training_basic")
    if suite is None:
        print("Suite no encontrada, saltando validaciones (success=skipped)")
        REPORT_PATH.write_text(json.dumps({"skipped": True}, indent=2, ensure_ascii=False), encoding="utf-8")
        return 0
    dataset_path = find_dataset()
    if dataset_path is None:
        print("Dataset CSV no encontrado", file=sys.stderr)
        FAIL_PATH.write_text(json.dumps({"error": "dataset_missing"}, indent=2, ensure_ascii=False), encoding="utf-8")
        return 1
    import pandas as pd  # local import for speed when skipped
    df = pd.read_csv(dataset_path)
    suite_result = run_suite(df, suite)
    report = {
        "suite": suite.get("expectation_suite_name"),
        "dataset": str(dataset_path),
        "success": suite_result["success"],
        "details": suite_result["results"],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if not suite_result["success"]:
        FAIL_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return 1
    if FAIL_PATH.exists():
        FAIL_PATH.unlink()
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
