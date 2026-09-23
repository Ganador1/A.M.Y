"""Twelve fresh native H2 runs isolating visibility of the receipt index.

All arms use current pending-claim storage and certified summaries. Only the
receipt-index prompt flag changes. This is a targeted follow-up, not held-out
scientific discovery. No prior energies, successful distances or decisions are
supplied. Every started, failed and finished row remains in the campaign ledger.
"""
from __future__ import annotations

import argparse
import asyncio
import copy
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from core.execution_evidence import canonical
from scripts.run.run_native_science_benchmark import MATRIX, digest, execute_config, make_plan, prepare_run


def make_validation_plan():
    matrix = json.loads(MATRIX.read_bytes())
    matrix["campaign_id"] = "amy-receipt-memory-20260906-v2"
    matrix["cases"] = [c for c in matrix["cases"] if c["id"] == "h2_curve"]
    matrix["observation_profiles"] = ["certified_summary"]
    plan = make_plan(matrix)
    rows = []
    for row in plan["rows"]:
        arms = ["index_visible", "recent_only"] if row["replicate"] == 1 else ["recent_only", "index_visible"]
        for arm in arms:
            rows.append({**row, "id": row["id"] + "-" + arm, "memory_profile": arm})
    plan.update(rows=rows,
                comparison_scope="Same H2 mission, model, token budget and certified-summary profile; toggle only receipt-index visibility. Two unpaired stochastic replicates; no causal certainty from small n.",
                hypothesis="Showing all five possible execution receipts may prevent losing a previously sampled minimum or its ID.",
                native_runtime_changes_shared=["unverified model claims stored separately", "receipt index retained in memory"],
                prior_results_used_for_design=True, historical_results_supplied=False,
                task_selection="Follow-up selected after observed missing old IDs in the v1 H2 benchmark; not a new held-out task.")
    return plan


def freeze_validation_plan(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    plan = make_validation_plan()
    file = path/"plan.json"
    raw = canonical(plan) + b"\n"
    if file.exists():
        if file.read_bytes() != raw:
            raise ValueError("Existing plan differs; use a fresh directory")
    else:
        file.write_bytes(raw)
    return plan


def prepare_validation(path, plan, row):
    directory, config = prepare_run(path, plan, row)
    config["llm"]["experiment_receipt_context"] = row["memory_profile"] == "index_visible"
    config["evidence"]["additional_sources"].append(str(Path(__file__).resolve()))
    config["evidence"]["benchmark"]["memory_profile"] = row["memory_profile"]
    # Include the flag in the prompt-profile comparison key, not in the mission.
    config["evidence"]["benchmark"]["prompt_profile"] += "/" + row["memory_profile"]
    from amy import _evidence_config
    (directory/"effective_config.json").write_bytes(canonical(_evidence_config(config)) + b"\n")
    return directory, config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--row", help=argparse.SUPPRESS)
    args = parser.parse_args()
    path = args.campaign_dir.resolve()
    plan = freeze_validation_plan(path)
    if args.row:
        if not args.execute:
            parser.error("Child execution requires --execute")
        row = next(r for r in plan["rows"] if r["id"] == args.row)
        directory, config = prepare_validation(path, plan, row)
        return asyncio.run(execute_config(directory, config, row))
    print(json.dumps({"plan_sha256": digest(plan), "rows": len(plan["rows"]), "execute": args.execute}), flush=True)
    if not args.execute:
        return 0
    logs = path/"controller_logs"
    logs.mkdir(exist_ok=True)
    status = 0
    for row in plan["rows"]:
        directory = path/"missions"/row["id"]
        if directory.exists():
            raise ValueError("Refusing to overwrite or silently skip " + str(directory))
        with (path/"controller_events.jsonl").open("a") as handle:
            handle.write(json.dumps({"event": "started", "row": row["id"], "utc_epoch": time.time()}) + "\n")
        print(json.dumps({"started": row["id"]}), flush=True)
        with (logs/(row["id"] + ".log")).open("x") as handle:
            child = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--campaign-dir", str(path),
                                    "--execute", "--row", row["id"]], cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT)
        with (path/"controller_events.jsonl").open("a") as handle:
            handle.write(json.dumps({"event": "finished", "row": row["id"], "utc_epoch": time.time(),
                                     "exit_code": child.returncode, "result_retained": (directory/"result.json").is_file()}) + "\n")
        print(json.dumps({"finished": row["id"], "exit_code": child.returncode}), flush=True)
        status = max(status, int(child.returncode != 0))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
