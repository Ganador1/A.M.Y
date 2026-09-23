"""Predeclare a matrix, then run fresh AMY minds on public scientific tasks.

The live model selects every action, input and final assessment. This controller
supplies contracts and resource limits, never thoughts or expected answers.
Each selected row runs in a separate process to isolate mutable runtime state.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from core.execution_evidence import canonical, verify_run

MATRIX = ROOT / "benchmarks/native_science/v1.json"


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def make_plan(matrix):
    models = matrix["model_profiles"]
    if any("kimi" in p["model"].lower() for p in models):
        raise ValueError("Kimi models are excluded by the operator")
    rows = []
    for replicate in range(1, matrix["limits"]["replicates"] + 1):
        for case_index, case in enumerate(matrix["cases"]):
            shift = (case_index + replicate - 1) % len(models)
            rotated = models[shift:] + models[:shift]
            profiles = matrix["observation_profiles"]
            if replicate % 2 == 0:
                profiles = list(reversed(profiles))
            for profile in profiles:
                for model in rotated:
                    rows.append({"id": f"{case['id']}-{model['id']}-{profile}-r{replicate}",
                                 "case_id": case["id"], "model_profile": model["id"],
                                 "prompt_profile": profile, "replicate": replicate})
    return {"schema": "amy.native_science.plan.v1", "campaign_id": matrix["campaign_id"],
            "matrix_sha256": digest(matrix), "matrix": matrix, "rows": rows,
            "execution": "sequential, fresh process and isolated memory for each row",
            "source_policy": "retain source bytes at run start; fail integrity if changed during run",
            "comparison_scope": "same task, resource budget and prompt profile; reasoning modes differ as declared",
            "automatic_candidate_reports": False, "native_final_assessment_required": True,
            "attribution": {"Codex": ["tools", "validators", "protocol", "runtime fixes", "evaluation"],
                            "AMY": ["native cognitive loop", "live model decisions", "tool execution", "memory updates"],
                            "provider_identity_authenticated": False},
            "historical_results_supplied": False, "expected_answers_supplied": False}


def freeze_plan(campaign_dir: Path):
    campaign_dir.mkdir(parents=True, exist_ok=True)
    plan = make_plan(json.loads(MATRIX.read_text()))
    path = campaign_dir / "plan.json"
    data = canonical(plan) + b"\n"
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Existing plan differs; use a new campaign directory, never rewrite a protocol")
    else:
        with path.open("xb") as handle:
            handle.write(data)
    return path, plan


def prepare_run(campaign_dir: Path, plan: dict, row: dict):
    from amy import load_config, _evidence_config
    matrix = plan["matrix"]
    case = next(c for c in matrix["cases"] if c["id"] == row["case_id"])
    model = next(m for m in matrix["model_profiles"] if m["id"] == row["model_profile"])
    limits = matrix["limits"]
    if "kimi" in model["model"].lower():
        raise ValueError("Kimi models are excluded")
    run_dir = campaign_dir / "missions" / row["id"]
    run_dir.mkdir(parents=True, exist_ok=False)
    mission = case["mission"] + "\n\n" + matrix["shared_instructions"]
    protocol = {"schema": "amy.native_science.operator_protocol.v1", "plan_sha256": digest(plan),
                "row": row, "mission": mission, "model_profile": model, "limits": limits,
                "prompt_profile": row["prompt_profile"], "entrypoint": "amy.AMY.start",
                "attribution": plan["attribution"], "scoring_tolerances": matrix["scoring_tolerances"],
                "provider_payload": "Public synthetic task, AMY tool contracts, and this isolated run's observations",
                "automatic_candidate_reports": False, "historical_results_supplied": False,
                "expected_answers_supplied": False, "novelty_claim": False}
    protocol_path = run_dir / "operator_protocol.json"
    protocol_path.write_bytes(canonical(protocol) + b"\n")
    config = load_config(str(ROOT / "config.yaml"))
    config["mission"] = {"goal": mission, "description": "Native " + case["domain"] + " benchmark", "urgency": "medium"}
    config["heartbeat"].update(max_cycles=limits["max_cycles"], base_interval_seconds=0,
                               focused_interval_seconds=0, idle_interval_seconds=0,
                               max_cycles_before_reflection=100, continuous_mission=False,
                               allowed_actions=["run_scientific_tool", "think_more"],
                               allowed_scientific_tools=[case["tool"]], require_tool_certificate=True)
    config["llm"].update(total_timeout=limits["total_timeout"], read_timeout=limits["total_timeout"],
                          tool_observation_mode=row["prompt_profile"])
    for role in ("reasoner", "fast"):
        config["llm"][role].update(model=model["model"], max_tokens=limits["max_tokens"],
                                   temperature=limits["temperature"], think=model["think"], num_ctx=limits["num_ctx"])
    config["atlas"]["model"] = model["model"]
    config["memory"].update(namespace_by_mission=True, mission_namespace=row["id"],
                             mission_memory_root=str(run_dir / "memory"))
    config["skills"].update(library_path=str(run_dir / "skills"), use_embedding_recall=False)
    config["communication"].update(method="file", report_path=str(run_dir / "candidate_reports"), max_reports_per_day=0)
    science_sources = ["atlas/app/ssh_certificate_tool.py", "atlas/app/ssh_spectral_certificate.py",
                       "atlas/app/ssh_column_witness.py", "atlas/app/population_selection_certificate.py",
                       "atlas/app/population_selection_verifier.py"]
    # Evaluators are retained when present. Later code cannot silently replace
    # them; the portable packager checks snapshot compatibility before export.
    evaluator_sources = sorted((ROOT / "scripts/verify").glob("*native*science*.py"))
    evaluator_sources += [ROOT / "scripts/verify/summarize_native_benchmark.py",
                          ROOT / "scripts/verify/score_scientific_assessments.py"]
    config["evidence"] = {"enabled": True, "root": str(run_dir / "runs"),
                          "additional_sources": [str(Path(__file__).resolve()), str(MATRIX),
                              str(campaign_dir / "plan.json"), str(protocol_path),
                              *[str(ROOT / path) for path in science_sources],
                              *[str(path) for path in evaluator_sources if path.is_file()]],
                          "benchmark": {"campaign_id": matrix["campaign_id"], "domain": case["domain"],
                              "case_id": case["id"], "replicate": row["replicate"], "arm": model["id"],
                              "model_profile": model, "profile_sha256": digest(model),
                              "mission_sha256": hashlib.sha256(mission.encode()).hexdigest(),
                              "protocol_sha256": digest(protocol), "prompt_profile": row["prompt_profile"]}}
    (run_dir / "effective_config.json").write_bytes(canonical(_evidence_config(config)) + b"\n")
    return run_dir, config


async def execute_row(campaign_dir: Path, plan, row):
    run_dir, config = prepare_run(campaign_dir, plan, row)
    return await execute_config(run_dir, config, row)


async def execute_config(run_dir: Path, config: dict, row: dict):
    """Run a fully declared configuration through the real AMY lifecycle."""
    from amy import AMY
    mind = None
    failure = None
    try:
        mind = AMY(config)
        await mind.start()
    except Exception as exc:
        failure = {"type": type(exc).__name__, "error": str(exc)}
    path = getattr(mind, "evidence_path", None)
    result = {"row": row, "evidence_path": path, "runtime_failure": failure}
    if path:
        verification = verify_run(path)
        result["integrity"] = verification
        if verification["integrity_verified"]:
            root = verification["root_sha256"]
            from scripts.verify.verify_native_science_run import verify_native_science_run
            from scripts.verify.summarize_native_benchmark import summarize_run
            audit = verify_native_science_run(path, expected_root=root)
            result["science_audit"] = audit
            result["metrics"] = summarize_run(path, expected_root=root, domain_audit=audit)
            try:
                from scripts.verify.score_scientific_assessments import score_run
            except ImportError:
                result["quality"] = {"status": "pending_evaluator", "task_solved": None}
            else:
                result["quality"] = score_run(path, expected_root=root)
    (run_dir / "result.json").write_bytes(canonical(result) + b"\n")
    print(json.dumps({"row": row["id"], "evidence_path": path, "runtime_failure": failure,
                      "root_sha256": result.get("integrity", {}).get("root_sha256"),
                      "trace_valid": result.get("science_audit", {}).get("trace_valid"),
                      "domain_valid": result.get("science_audit", {}).get("domain_valid"),
                      "quality": result.get("quality")}), flush=True)
    return int(failure is not None or not result.get("integrity", {}).get("integrity_verified"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-dir", required=True)
    parser.add_argument("--execute", action="store_true", help="Without this flag only freeze/show the full plan")
    parser.add_argument("--case", action="append", dest="cases")
    parser.add_argument("--model", action="append", dest="models", help="Profile ID declared in matrix")
    parser.add_argument("--profile", action="append", dest="profiles", choices=["full", "certified_summary"])
    parser.add_argument("--replicate", type=int, action="append", dest="replicates")
    parser.add_argument("--row", help=argparse.SUPPRESS)
    args = parser.parse_args()
    campaign_dir = Path(args.campaign_dir).resolve()
    path, plan = freeze_plan(campaign_dir)
    if args.row:
        row = next((r for r in plan["rows"] if r["id"] == args.row), None)
        if row is None or not args.execute:
            parser.error("A declared row and --execute are required for a child run")
        return asyncio.run(execute_row(campaign_dir, plan, row))
    selected = [r for r in plan["rows"] if all(v is None or r[k] in v for k, v in
                [("case_id", args.cases), ("model_profile", args.models),
                 ("prompt_profile", args.profiles), ("replicate", args.replicates)])]
    if not selected:
        parser.error("No matrix rows match the filters")
    print(json.dumps({"plan": str(path), "plan_sha256": digest(plan), "declared_rows": len(plan["rows"]),
                      "selected_rows": [r["id"] for r in selected], "execute": args.execute}), flush=True)
    if not args.execute:
        return 0
    status = 0
    logs = campaign_dir / "controller_logs"
    logs.mkdir(exist_ok=True)
    for row in selected:
        run_dir = campaign_dir / "missions" / row["id"]
        if run_dir.exists():
            raise ValueError(f"Refusing to overwrite or silently skip an existing mission: {run_dir}")
        with (logs / (row["id"] + ".log")).open("x") as handle:
            print(json.dumps({"started": row["id"]}), flush=True)
            started = time.time()
            with (campaign_dir / "controller_events.jsonl").open("a") as ledger:
                ledger.write(json.dumps({"event": "started", "row": row["id"], "utc_epoch": started}) + "\n")
            completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--campaign-dir",
                                        str(campaign_dir), "--execute", "--row", row["id"]],
                                       cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=False)
        with (campaign_dir / "controller_events.jsonl").open("a") as ledger:
            ledger.write(json.dumps({"event": "finished", "row": row["id"], "utc_epoch": time.time(),
                                     "exit_code": completed.returncode,
                                     "result_retained": (run_dir / "result.json").is_file()}) + "\n")
        print(json.dumps({"finished": row["id"], "exit_code": completed.returncode}), flush=True)
        status = max(status, int(completed.returncode != 0))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
