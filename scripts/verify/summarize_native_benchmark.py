#!/usr/bin/env python3
"""Summarize sealed native runs without inferring scientific truth or prices.

Failures, retries and incomplete responses remain in every denominator. Provider
nanoseconds and observed timestamp differences are separate measurements. Domain
audits can be attached explicitly; this module is not a scientific verifier.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from core.execution_evidence import canonical, verify_run

TOKEN_FIELDS = ("prompt_eval_count", "prompt_eval_cached_count", "eval_count")
DURATION_FIELDS = ("total_duration", "load_duration", "prompt_eval_duration", "eval_duration")


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=pairs)
    canonical(value)
    return value


def json_action(content):
    fence = re.fullmatch(r"\s*```(?:json)?\s*\n(.*?)\n```\s*", content, re.DOTALL)
    value = strict_json(fence.group(1) if fence else content)
    if not isinstance(value, dict):
        raise ValueError("action is not an object")
    return value


def number(value):
    return value if type(value) in (int, float) and math.isfinite(value) else None


def elapsed(begin, end):
    try:
        seconds = (datetime.fromisoformat(end["timestamp_utc"])
                   - datetime.fromisoformat(begin["timestamp_utc"])).total_seconds()
        return seconds if seconds >= 0 else None
    except (KeyError, ValueError, TypeError):
        return None


def distribution(values):
    known = [value for value in values if number(value) is not None]
    return {"known_n": len(known), "missing_n": len(values)-len(known),
            "sum": sum(known) if known else None,
            "mean": statistics.mean(known) if known else None,
            "median": statistics.median(known) if known else None,
            "max": max(known) if known else None}


def summarize_run(directory, *, expected_root=None, domain_audit=None):
    path = Path(directory).resolve()
    integrity = verify_run(path, expected_root=expected_root)
    report = {"run_path": str(path), "integrity": integrity, "attempts": [], "decisions": [],
              "tool_calls": [], "metrics": None, "domain_audit": None,
              "scientific_truth_verified": False, "autonomy_verified": False}
    if not integrity["integrity_verified"]:
        return report

    def blob(ref):
        if not isinstance(ref, dict) or not re.fullmatch(r"blobs/[0-9a-f]{64}\.bin", ref.get("path", "")):
            raise ValueError("invalid blob reference")
        raw = (path/ref["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != ref["sha256"] or len(raw) != ref["size_bytes"]:
            raise ValueError("blob reference mismatch")
        return raw

    events = [strict_json(line) for line in (path/"events.jsonl").read_bytes().splitlines()]
    payload = {event["sequence"]: strict_json(blob(event["payload"])) for event in events}
    metadata = payload[events[0]["sequence"]].get("metadata", {})
    report["metadata"] = metadata
    report["run_status"] = payload[events[-1]["sequence"]].get("status")
    spans = {}
    for event in events:
        if event["kind"].endswith(".begin"):
            spans[event["span_id"]] = {"kind": event["kind"][:-6], "begin": event,
                                       "input": payload[event["sequence"]]["input"]}
        elif event["kind"].endswith(".end"):
            spans[event["span_id"]].update(end=event, result=payload[event["sequence"]])

    def parent_of_kind(span, kind):
        sid = span["begin"]["parent_id"]
        while sid in spans:
            if spans[sid]["kind"] == kind:
                return spans[sid]
            sid = spans[sid]["begin"]["parent_id"]
        return None

    def out(span):
        return span["result"].get("output") if span else None

    for span in spans.values():
        if span["kind"] != "llm.transport":
            continue
        decision = parent_of_kind(span, "reasoning.decision")
        cycle = parent_of_kind(span, "heartbeat.cycle")
        received = out(span) if isinstance(out(span), dict) else {}
        receipt = received.get("receipt", {})
        request = span["input"].get("payload", {})
        item = {"span_id": span["begin"]["span_id"], "sequence": span["begin"]["sequence"],
                "decision_id": decision["begin"]["span_id"] if decision else None,
                "cycle": cycle["input"].get("cycle") if cycle else None,
                "model": request.get("model"), "requested_think": request.get("think"),
                "requested_options": request.get("options", {}),
                "observed_seconds": elapsed(span["begin"], span["end"]),
                "transport_status": span["result"].get("status"),
                "http_status": receipt.get("status_code"),
                "error_type": span["result"].get("error_type"), "error": span["result"].get("error"),
                "completion": "unknown", "raw_receipt_bound": False, "request_receipt_bound": False,
                "valid_action_json": False, "action": None,
                "provider_tokens": {key: None for key in TOKEN_FIELDS},
                "provider_durations_ns": {key: None for key in DURATION_FIELDS}}
        report["attempts"].append(item)
        try:
            if receipt.get("request_body"):
                item["request_receipt_bound"] = canonical(strict_json(blob(receipt["request_body"]))) == canonical(request)
            if receipt.get("response_body") and receipt.get("status_code") == 200:
                envelope = strict_json(blob(receipt["response_body"]))
                item["raw_receipt_bound"] = canonical(envelope) == canonical(received.get("response"))
                item["done"], item["done_reason"] = envelope.get("done"), envelope.get("done_reason")
                item["completion"] = ("incomplete" if envelope.get("done") is False or envelope.get("done_reason") == "length"
                                      else "complete" if envelope.get("done") is True else "unknown")
                for field in TOKEN_FIELDS+DURATION_FIELDS:
                    value = envelope.get(field)
                    value = value if type(value) is int and value >= 0 else None
                    item["provider_tokens" if field in TOKEN_FIELDS else "provider_durations_ns"][field] = value
                message = envelope.get("message", {})
                content, thinking = message.get("content", ""), message.get("thinking", "")
                item.update(content_characters=len(content), thinking_characters=len(thinking))
                try:
                    item["action"] = json_action(content if content.strip() else thinking)
                    item["valid_action_json"] = True
                except (ValueError, TypeError, RecursionError):
                    pass
        except (ValueError, KeyError, TypeError, AttributeError, RecursionError) as exc:
            item["receipt_error"] = str(exc)
        failure = item["transport_status"] != "returned"
        item["completion_unobserved"] = failure or item["completion"] != "complete"
        item["censor_reason"] = ("transport_failure" if failure else "generation_length_or_done_false"
                                  if item["completion"] == "incomplete" else "completion_metadata_missing"
                                  if item["completion"] == "unknown" else None)
        tokens, duration = item["provider_tokens"]["eval_count"], item["provider_durations_ns"]["eval_duration"]
        item["provider_generated_tokens_per_second"] = tokens/(duration/1e9) if tokens is not None and duration else None

    attempts_by_decision = defaultdict(list)
    for item in report["attempts"]:
        if item["decision_id"]:
            attempts_by_decision[item["decision_id"]].append(item)
    for span in spans.values():
        if span["kind"] != "reasoning.decision":
            continue
        sid = span["begin"]["span_id"]
        cycle = parent_of_kind(span, "heartbeat.cycle")
        thought = out(span) if isinstance(out(span), dict) else {}
        attempts = attempts_by_decision[sid]
        successful = [item for item in attempts if item["transport_status"] == "returned"]
        final = successful[-1] if successful else None
        bound = False
        if final and final["raw_receipt_bound"] and final["request_receipt_bound"] and final["completion"] == "complete" and final["valid_action_json"]:
            parsed = copy.deepcopy(final["action"])
            focus = span["input"].get("focus", {})
            parsed.update(source=focus.get("source", "unknown"), focus_content=focus.get("content", "")[:200],
                          cycle=span["input"].get("context", {}).get("cycle", 0))
            parsed.setdefault("action_type", "think_more")
            if isinstance(parsed.get("action_details"), dict):
                parsed.update(parsed["action_details"])
            bound = canonical(parsed) == canonical(thought)
        acts = [candidate for candidate in spans.values() if candidate["kind"] == "heartbeat.act"
                and cycle is not None and candidate["begin"]["parent_id"] == cycle["begin"]["span_id"]]
        action = acts[0] if len(acts) == 1 else None
        action_result = out(action) if isinstance(out(action), dict) else {}
        if action:
            bound = bound and canonical(action["input"].get("thought")) == canonical(thought)
        else:
            bound = False
        hypothesis = thought.get("hypothesis", "")
        hypothesis = hypothesis if isinstance(hypothesis, str) else ""
        cues = {"hypothesis_present": bool(hypothesis.strip()),
                "numeric_literal": bool(re.search(r"\d", hypothesis)),
                "comparison_or_direction": bool(re.search(r"[<>≤≥=]|\b(higher|lower|increase|decrease|greater|less|minimum|maximum|above|below)\b", hypothesis, re.I)),
                "tool_action": thought.get("action_type") == "run_scientific_tool"}
        report["decisions"].append({"span_id": sid, "cycle": cycle["input"].get("cycle") if cycle else None,
            "model": final["model"] if final else attempts[-1]["model"] if attempts else None,
            "attempts": len(attempts), "retry_attempts": max(0, len(attempts)-1),
            "observed_seconds": elapsed(span["begin"], span["end"]),
            "accepted_complete_action_bound": bound, "action_type": thought.get("action_type"),
            "action_reported_success": action_result.get("success") if type(action_result.get("success")) is bool else None,
            "action_error": action_result.get("error"), "hypothesis": hypothesis,
            "hypothesis_cues_unvalidated": cues, "progress_self_reported": number(thought.get("progress_toward_goal")),
            "observation": thought.get("observation"), "thought": thought.get("thought"), "content": thought.get("content"),
            "tool_name": thought.get("tool_name"), "tool_input": thought.get("tool_input")})

    for span in spans.values():
        if span["kind"] != "atlas.scientific_tool":
            continue
        act = parent_of_kind(span, "heartbeat.act")
        cycle = parent_of_kind(span, "heartbeat.cycle")
        result = out(act) if isinstance(out(act), dict) else {}
        report["tool_calls"].append({"span_id": span["begin"]["span_id"],
            "cycle": cycle["input"].get("cycle") if cycle else None,
            "tool_name": span["input"].get("tool_name"), "tool_input": span["input"].get("tool_input"),
            "status": span["result"].get("status"), "observed_seconds": elapsed(span["begin"], span["end"]),
            "action_reported_success": result.get("success") if type(result.get("success")) is bool else None,
            "output_bound_to_action": canonical(out(span)) == canonical(result.get("result")),
            "error": result.get("error") or span["result"].get("error")})

    cycles = [span for span in spans.values() if span["kind"] == "heartbeat.cycle"]
    decisions, attempts, tools = report["decisions"], report["attempts"], report["tool_calls"]
    config = metadata.get("config", {})
    benchmark = config.get("evidence", {}).get("benchmark", {})
    report["benchmark"] = benchmark
    options = [{"think": item["requested_think"], "options": item["requested_options"]} for item in attempts]
    profiles = {canonical(value).decode(): value for value in options}
    mission = config.get("mission", metadata.get("mission"))
    if mission is None and cycles:
        mission = cycles[0]["input"].get("goal")
    cohort = {"case_id": benchmark.get("case_id"),
              "mission_sha256": benchmark.get("mission_sha256") or hashlib.sha256(canonical(mission)).hexdigest(),
              "max_cycles": config.get("heartbeat", {}).get("max_cycles"),
              "prompt_profile": benchmark.get("prompt_profile"),
              "budgets": sorted({canonical(item["requested_options"]).decode() for item in attempts})}
    report["cohort_definition"] = cohort
    report["cohort_sha256"] = hashlib.sha256(canonical(cohort)).hexdigest()
    report["requested_profiles"] = list(profiles.values())
    report["models"] = sorted({item["model"] for item in attempts if isinstance(item["model"], str)})
    report["observed_run_seconds"] = elapsed(events[0], events[-1])
    report["metrics"] = {
        "cycles": len(cycles), "decisions": len(decisions), "attempts": len(attempts),
        "retry_attempts": sum(item["retry_attempts"] for item in decisions),
        "auxiliary_attempts": sum(item["decision_id"] is None for item in attempts),
        "transport_errors": sum(item["transport_status"] != "returned" for item in attempts),
        "completion_counts": dict(Counter(item["completion"] for item in attempts)),
        "completion_unobserved": sum(item["completion_unobserved"] for item in attempts),
        "accepted_complete_decisions": sum(item["accepted_complete_action_bound"] for item in decisions),
        "accepted_complete_decision_rate": sum(item["accepted_complete_action_bound"] for item in decisions)/len(decisions) if decisions else None,
        "action_types": dict(Counter(item["action_type"] or "unknown" for item in decisions)),
        "tool_calls": len(tools),
        "tool_successes_reported_and_bound": sum(item["action_reported_success"] is True and item["output_bound_to_action"] for item in tools),
        "unique_tool_inputs": len({canonical([item["tool_name"], item["tool_input"]]) for item in tools}),
        "hypotheses_with_measurement_cues_unvalidated": sum(c["hypothesis_present"] and c["tool_action"]
            and (c["numeric_literal"] or c["comparison_or_direction"]) for c in (item["hypothesis_cues_unvalidated"] for item in decisions)),
        "attempt_elapsed_seconds_all_outcomes": distribution([item["observed_seconds"] for item in attempts]),
        "decision_elapsed_seconds_including_retries": distribution([item["observed_seconds"] for item in decisions]),
        "provider_tokens": {field: distribution([item["provider_tokens"][field] for item in attempts]) for field in TOKEN_FIELDS},
        "provider_durations_ns": {field: distribution([item["provider_durations_ns"][field] for item in attempts]) for field in DURATION_FIELDS},
        "runtime_audits_reporting_valid": sum(out(span).get("valid") is True for span in spans.values()
            if span["kind"] == "atlas.certificate_verification" and isinstance(out(span), dict)),
    }
    report["last_cycle"] = decisions[-1] if decisions else None
    report["local_entrypoint_declared"] = metadata.get("entrypoint")
    report["fixture_declared"] = metadata.get("fixture") is True or metadata.get("origin") == "hermetic_test"
    if domain_audit is not None:
        audit_root = domain_audit.get("run_root_sha256", domain_audit.get("integrity", {}).get("root_sha256"))
        report["domain_audit"] = {"root_matches": audit_root == integrity["root_sha256"],
                                  "artifact_sha256": hashlib.sha256(canonical(domain_audit)).hexdigest(),
                                  "result": domain_audit,
                                  "recomputed_by_this_summarizer": False}
    return report


def aggregate_reports(reports):
    """Pool counts within matched tasks/profiles; never average success rates."""
    groups = defaultdict(list)
    invalid = []
    for report in reports:
        if report.get("metrics") is None:
            invalid.append(report["run_path"])
            continue
        key = (report["cohort_sha256"], canonical(report["models"]).decode(), canonical(report["requested_profiles"]).decode())
        groups[key].append(report)
    aggregates = []
    for (cohort, models, profiles), runs in groups.items():
        decisions = sum(run["metrics"]["decisions"] for run in runs)
        accepted = sum(run["metrics"]["accepted_complete_decisions"] for run in runs)
        observed = distribution([run["observed_run_seconds"] for run in runs])
        known_tokens = [run["metrics"]["provider_tokens"]["eval_count"]["sum"] for run in runs
                        if run["metrics"]["provider_tokens"]["eval_count"]["known_n"] > 0]
        item = {"cohort_sha256": cohort, "models": json.loads(models), "profiles": json.loads(profiles),
                "run_paths": [run["run_path"] for run in runs], "replicates": len(runs),
                "decisions": decisions, "accepted_complete_decisions": accepted,
                "accepted_complete_decision_rate": accepted/decisions if decisions else None,
                "attempts": sum(run["metrics"]["attempts"] for run in runs),
                "transport_errors": sum(run["metrics"]["transport_errors"] for run in runs),
                "completion_unobserved": sum(run["metrics"]["completion_unobserved"] for run in runs),
                "retry_attempts": sum(run["metrics"]["retry_attempts"] for run in runs),
                "tool_successes_reported_and_bound": sum(run["metrics"]["tool_successes_reported_and_bound"] for run in runs),
                "observed_run_seconds": observed,
                "seconds_per_accepted_decision_including_failures": observed["sum"]/accepted
                    if accepted and observed["missing_n"] == 0 else None,
                "known_eval_tokens": sum(known_tokens) if known_tokens else None,
                "attempts_missing_eval_tokens": sum(run["metrics"]["provider_tokens"]["eval_count"]["missing_n"] for run in runs)}
        item["eval_tokens_total_complete"] = item["attempts_missing_eval_tokens"] == 0
        aggregates.append(item)
    for item in aggregates:
        cost = item["seconds_per_accepted_decision_including_failures"]
        rate = item["accepted_complete_decision_rate"]
        item["pareto_eligible"] = cost is not None and rate is not None
        item["pareto_runtime_nondominated"] = None
        if not item["pareto_eligible"]:
            continue
        dominated = any(other is not item and other["cohort_sha256"] == item["cohort_sha256"]
            and other["seconds_per_accepted_decision_including_failures"] is not None
            and other["accepted_complete_decision_rate"] >= rate
            and other["seconds_per_accepted_decision_including_failures"] <= cost
            and (other["accepted_complete_decision_rate"] > rate or other["seconds_per_accepted_decision_including_failures"] < cost)
            for other in aggregates)
        item["pareto_runtime_nondominated"] = not dominated
    return {"groups": aggregates, "invalid_runs_retained_without_scoring": invalid,
            "pareto_scope": "Operational comparison within task/budget cohort, not science or autonomous ability. "
                            "Maximize raw-bound complete decision rate; minimize total observed run time per accepted decision. "
                            "Failures/retries remain in time and rate denominators. Groups with no accepted decisions remain reported but have no cost-per-acceptance estimate."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--expected-root", action="append", default=[], metavar="RUN=ROOT")
    parser.add_argument("--domain-audit", action="append", default=[], metavar="RUN=JSON")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    def mapping(values):
        result = {}
        for value in values:
            key, separator, item = value.partition("=")
            if not separator:
                parser.error("mapping arguments require RUN=VALUE")
            result[str(Path(key).resolve())] = item
        return result
    roots, audits = mapping(args.expected_root), mapping(args.domain_audit)
    reports = []
    for path in args.runs:
        key = str(path.resolve())
        try:
            audit = strict_json(Path(audits[key]).read_bytes()) if key in audits else None
            reports.append(summarize_run(path, expected_root=roots.get(key), domain_audit=audit))
        except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as exc:
            reports.append({"run_path": key, "metrics": None, "error": f"{type(exc).__name__}: {exc}"})
    result = {"schema": "amy.native_benchmark_summary.v1", "runs": reports,
              "aggregation": aggregate_reports(reports), "provider_price_estimate": None,
              "notes": ["Missing token/duration counters are unknown, not zero; known sums are lower bounds when coverage is incomplete.",
                        "Observed durations use recorded UTC timestamps and include local overhead; provider durations are nanoseconds.",
                        "Hypothesis cues and progress fields are unvalidated model metadata, not scientific achievement.",
                        "Different requested thinking profiles and model tokenizers prevent claims of identical compute budgets.",
                        "No provider price, quota, autonomy or scientific truth is inferred."]}
    raw = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(raw)
    else:
        print(raw, end="")
    return 0 if all(report.get("metrics") is not None for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
