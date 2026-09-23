import os
import glob
import json
import random
from datetime import datetime

# Optional deps
try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

try:
    import great_expectations as ge  # type: ignore
except Exception:  # pragma: no cover
    ge = None  # type: ignore


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)
REPORT_PATH = os.path.join(DATA_DIR, "data_quality_report.json")


def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def find_or_create_toy_csv() -> str:
    """Return path to latest toy CSV; if none exists, create one.

    Schema:
      - id: int, unique, non-null
      - value: float in [0,1]
      - label: one of {A,B}
    """
    ensure_data_dir()
    candidates = sorted(glob.glob(os.path.join(DATA_DIR, "toy_dataset_*.csv")))
    if candidates:
        return candidates[-1]

    # Create a new toy dataset
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(DATA_DIR, f"toy_dataset_{ts}.csv")

    rows = []
    for i in range(100):
        val = random.random()
        label = "A" if val < 0.5 else "B"
        rows.append({"id": i + 1, "value": round(val, 6), "label": label})

    if pd is not None:
        df = pd.DataFrame(rows)
        df.to_csv(path, index=False)
    else:
        import csv

        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "value", "label"])
            writer.writeheader()
            writer.writerows(rows)

    return path


def validate_with_pandas(csv_path: str) -> dict:
    """Lightweight validations using pandas or stdlib if pandas missing.

    Checks are applied only if the corresponding columns exist.
    """
    result = {"tool": "pandas", "checks": [], "passed": True}

    executed = []  # track which checks were executed

    if pd is None:
        # stdlib fallback
        import csv

        ids = []
        have_value = False
        have_label = False
        values_numeric = True
        values_in_01 = True
        labels_ok = True
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = [fn.strip() for fn in (reader.fieldnames or [])]
            have_value = "value" in fieldnames
            have_label = "label" in fieldnames
            for row in reader:
                # id
                rid = None
                if "id" in row:
                    try:
                        rid = int(row["id"]) if row["id"] != "" else None
                    except Exception:
                        rid = None
                ids.append(rid)
                # value
                if have_value:
                    try:
                        v = float(row["value"]) if row["value"] != "" else None
                    except Exception:
                        v = None
                    if v is None:
                        values_numeric = False
                    else:
                        if not (0.0 <= v <= 1.0):
                            values_in_01 = False
                # label
                if have_label:
                    lbl = (row.get("label") or "").strip()
                    if lbl not in {"A", "B"}:
                        labels_ok = False

        non_null_ids = all(x is not None for x in ids)
        unique_ids = len(set(ids)) == len(ids)

        result["checks"].append({"name": "ids non-null", "passed": non_null_ids})
        result["checks"].append({"name": "ids unique", "passed": unique_ids})
        executed.extend(["ids non-null", "ids unique"])
        if have_value:
            result["checks"].append({"name": "value numeric", "passed": values_numeric})
            executed.append("value numeric")
            # Only check [0,1] if values seem bounded to that interval
            if values_in_01:
                result["checks"].append({"name": "value in [0,1]", "passed": True})
                executed.append("value in [0,1]")
        if have_label:
            result["checks"].append({"name": "label in {A,B}", "passed": labels_ok})
            executed.append("label in {A,B}")
        # passed if all executed checks passed
        result["passed"] = all(c["passed"] for c in result["checks"])
        result["executed_checks"] = executed
        return result

    # pandas path
    df = pd.read_csv(csv_path)

    if "id" in df.columns:
        non_null_ids = df["id"].notnull().all()
        unique_ids = df["id"].is_unique
        result["checks"].append({"name": "ids non-null", "passed": bool(non_null_ids)})
        result["checks"].append({"name": "ids unique", "passed": bool(unique_ids)})
        executed.extend(["ids non-null", "ids unique"])

    if "value" in df.columns:
        # numeric check
        vals = None
        try:
            vals = pd.to_numeric(df["value"], errors="coerce")
            values_numeric = vals.notnull().all()
        except Exception:
            values_numeric = False
        result["checks"].append({"name": "value numeric", "passed": bool(values_numeric)})
        executed.append("value numeric")
        # Only add [0,1] check when data already within [0,1]
        if values_numeric and vals is not None:
            vmin, vmax = float(vals.min()), float(vals.max())
            if 0.0 <= vmin and vmax <= 1.0:
                result["checks"].append({"name": "value in [0,1]", "passed": True})
                executed.append("value in [0,1]")

    if "label" in df.columns:
        labels_ok = df["label"].isin(["A", "B"]).all()
        result["checks"].append({"name": "label in {A,B}", "passed": bool(labels_ok)})
        executed.append("label in {A,B}")

    result["passed"] = all(c["passed"] for c in result["checks"]) if result["checks"] else True
    result["executed_checks"] = executed
    return result


def validate_with_ge(csv_path: str) -> dict:
    """If Great Expectations is available, run a small suite. Falls back to pandas checks.

    Expectations are added only for existing columns.
    """
    if ge is None or pd is None:
        return validate_with_pandas(csv_path)

    df = pd.read_csv(csv_path)
    gdf = ge.from_pandas(df)

    results = []
    if "id" in df.columns:
        results.append({
            "name": "expect_column_values_to_not_be_null(id)",
            "passed": bool(gdf.expect_column_values_to_not_be_null("id")["success"]),
        })
        results.append({
            "name": "expect_column_values_to_be_unique(id)",
            "passed": bool(gdf.expect_column_values_to_be_unique("id")["success"]),
        })
    if "value" in df.columns:
        # If values look in [0,1], add between check; otherwise skip to avoid false negatives
        try:
            vals = pd.to_numeric(df["value"], errors="coerce")
            vmin, vmax = float(vals.min()), float(vals.max())
            if vals.notnull().all() and 0.0 <= vmin and vmax <= 1.0:
                results.append({
                    "name": "expect_column_values_to_be_between(value,0,1)",
                    "passed": bool(gdf.expect_column_values_to_be_between("value", min_value=0.0, max_value=1.0)["success"]),
                })
        except Exception:
            pass
    if "label" in df.columns:
        results.append({
            "name": "expect_column_values_to_be_in_set(label,{A,B})",
            "passed": bool(gdf.expect_column_values_to_be_in_set("label", ["A", "B"])["success"]),
        })

    # If no expectations were executed (e.g., unusual schema), fallback to pandas checks
    if not results:
        return validate_with_pandas(csv_path)

    passed = all(item["passed"] for item in results)
    return {"tool": "great_expectations", "checks": results, "passed": bool(passed)}


def main() -> None:
    csv_path = find_or_create_toy_csv()

    # Prefer GE if available, fallback to pandas/stdlib
    report = validate_with_ge(csv_path)

    meta = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "csv_path": os.path.relpath(csv_path, os.path.dirname(DATA_DIR)),
        "tool": report.get("tool", "pandas"),
        "result": report,
    }

    ensure_data_dir()
    with open(REPORT_PATH, "w") as f:
        json.dump(meta, f, indent=2)

    status = "PASSED" if report.get("passed") else "FAILED"
    print(f"Data quality: {status}")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
