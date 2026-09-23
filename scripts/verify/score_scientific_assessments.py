#!/usr/bin/env python3
"""Score explicit finite benchmark conclusions against root-pinned evidence.

Free prose, confidence, novelty and provider identity are never graded as proof.
The generic native trace audit is a prerequisite, not the scientific conclusion.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.execution_evidence import canonical, verify_run
from core.scientific_certificate_checks import check_scientific_certificate
from scripts.verify.verify_native_science_run import strict_json, verify_native_science_run

BENCHMARK = ROOT / "benchmarks/native_science/v1.json"
ENERGY_TOLERANCE = Fraction(1, 10**6)
DISTANCE_TOLERANCE = Fraction(1, 10**8)
_FIELDS = {
    "h2_curve": {"best_experiment_id", "best_distance_angstrom", "best_energy_hartree", "scope", "limitations"},
    "ssh_order": {"compared_experiment_ids", "relation", "scope", "limitations"},
    "population_equilibrium": {"trajectory_ids", "equilibrium_id", "candidate_equilibrium", "relation", "scope", "limitations"},
}
_SCOPES = {"h2_curve": "sampled_points_only", "ssh_order": "finite_chain_supplied_hoppings",
           "population_equilibrium": "finite_exact_model_trajectories"}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _number(value, *, string_only=False):
    _require(type(value) is str if string_only else type(value) in (str,int,float), "invalid assessment number type")
    text = str(value).strip()
    _require(len(text) <= 100 and re.fullmatch(r"[+-]?(?:[0-9]+/[0-9]+|(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]{1,2})?)", text),
             "invalid bounded assessment rational")
    result = Fraction(text)
    _require(max(abs(result.numerator).bit_length(), result.denominator.bit_length()) <= 512, "assessment precision limit")
    return result


def _ids(assessment, key, number):
    ids = assessment[key]
    _require(isinstance(ids,list) and len(ids) == number and all(type(x) is str and x for x in ids)
             and len(set(ids)) == number, f"{key} requires {number} distinct actual IDs")
    return ids


def _h2(assessment, records):
    _require(type(assessment["best_experiment_id"]) is str, "best_experiment_id must be a string")
    chosen = records.get(assessment["best_experiment_id"])
    _require(chosen is not None, "best_experiment_id was not actually executed successfully")
    distances = {Fraction(record["certificate"]["input"]["distance_angstrom"]) for record in records.values()}
    actual_best = min(Fraction(record["certificate"]["state"]["total_energy"]) for record in records.values())
    chosen_energy = Fraction(chosen["certificate"]["state"]["total_energy"])
    chosen_distance = Fraction(chosen["certificate"]["geometry"]["distance_angstrom"])
    correct = (chosen_energy == actual_best
               and abs(_number(assessment["best_energy_hartree"])-chosen_energy) <= ENERGY_TOLERANCE
               and abs(_number(assessment["best_distance_angstrom"])-chosen_distance) <= DISTANCE_TOLERANCE)
    coverage = {"distinct_distances": len(distances), "required_distinct_distances": 3,
                "complete": len(distances) >= 3}
    return correct, correct and coverage["complete"], coverage, {
        "lowest_observed_experiment_ids": [key for key,record in records.items()
            if Fraction(record["certificate"]["state"]["total_energy"]) == actual_best],
        "lowest_stored_energy_hartree": float(actual_best),
        "energy_tolerance_hartree": str(ENERGY_TOLERANCE),
        "distance_tolerance_angstrom": str(DISTANCE_TOLERANCE),
        "scope": "Comparison of retained float energies only; no continuous minimum or error bound",
    }


def _hex(pair):
    # Already schema/bounds-checked by the common certificate helper.
    return Fraction(int(pair[0],16),int(pair[1],16))


def _approaches_in_tested_steps(values, candidate):
    distances = [abs(value-candidate) for value in values]
    return (all(after <= before for before,after in zip(distances,distances[1:]))
            and any(after < before for before,after in zip(distances,distances[1:])))


def _ssh(assessment, records):
    ids = _ids(assessment,"compared_experiment_ids",2)
    _require(all(key in records for key in ids), "comparison references an unexecuted experiment ID")
    a,b = [records[key]["certificate"]["certificate"] for key in ids]
    hops_a, hops_b = ([_hex(x) for x in c["hoppings"]] for c in (a,b))
    coverage = {"two_distinct_orders": hops_a != hops_b,
                "same_multiset": Counter(hops_a) == Counter(hops_b)}
    coverage["complete"] = all(coverage.values())
    _require(coverage["complete"], "SSH comparison must use distinct orders of the same exact multiset")
    alo,ahi,blo,bhi = [_hex(c[k]) for c in (a,b) for k in ("gap_squared_lower","gap_squared_upper")]
    actual = ("first_gap_smaller" if ahi < blo else "second_gap_smaller" if bhi < alo
              else "not_resolved_by_certificates")
    _require(assessment["relation"] in {"first_gap_smaller","second_gap_smaller","not_resolved_by_certificates"}, "unsupported SSH relation")
    correct = assessment["relation"] == actual
    return correct, correct and actual != "not_resolved_by_certificates", coverage, {
        "relation_from_exact_squared_bounds": actual,
        "compared_experiment_ids": ids,
        "strict_interval_separation": actual != "not_resolved_by_certificates",
        "scope": "Finite ordered rational Hamiltonians; touching/overlapping intervals do not certify strict order",
    }


def _population(assessment, records):
    ids = _ids(assessment,"trajectory_ids",2)
    equilibrium_id = assessment["equilibrium_id"]
    _require(type(equilibrium_id) is str and equilibrium_id not in ids, "equilibrium_id must be a distinct third actual ID")
    all_ids = ids + [equilibrium_id]
    _require(all(key in records for key in all_ids), "population assessment references an unexecuted experiment ID")
    candidate = _number(assessment["candidate_equilibrium"],string_only=True)
    _require(0 < candidate < 1, "candidate equilibrium must be interior")
    certs = [records[key]["certificate"] for key in all_ids]
    starts = [Fraction(c["input"]["p0"]) for c in certs]
    weights = []
    for c in certs:
        values = [Fraction(c["input"][key]) for key in ("wAA","wAa","waa")]
        _require(all(v > 0 for v in values), "benchmark requires strictly positive viabilities")
        weights.append(tuple(v/values[-1] for v in values))
    coverage = {"three_distinct_trajectory_ids": True,
                "same_relative_viabilities": weights[0] == weights[1] == weights[2],
                "opposite_interior_starts": all(0 < p < 1 for p in starts[:2]) and (starts[0]-candidate)*(starts[1]-candidate) < 0,
                "candidate_itself_executed": starts[2] == candidate,
                "positive_generation_counts": all(1 <= c["input"]["generations"] <= 4 for c in certs)}
    coverage["complete"] = all(coverage.values())
    _require(coverage["complete"], "population test design lacks required opposite starts, shared viabilities or executed candidate")
    rows = [[Fraction(row["p_A"]) for row in cert["trajectory"]] for cert in certs]
    approach = [_approaches_in_tested_steps(row,candidate) for row in rows[:2]]
    stationary = all(value == candidate for value in rows[2])
    supported = all(approach) and stationary
    _require(assessment["relation"] in {"both_approach_in_tested_steps","not_supported"}, "unsupported population relation")
    actual = "both_approach_in_tested_steps" if supported else "not_supported"
    correct = assessment["relation"] == actual
    return correct, correct and supported, coverage, {
        "candidate_equilibrium": str(candidate), "approach_each_checked_step": approach,
        "candidate_trajectory_exactly_stationary": stationary, "relation_from_exact_trajectories": actual,
        "scope": "Finite tested transitions only; no fixation, asymptotic stability or empirical conclusion",
    }


def _benchmark_input(case_id, raw):
    _require(type(raw) is str, "benchmark tool_input must be a JSON string")
    request = strict_json(raw)
    _require(isinstance(request,dict), "benchmark input must be an object")
    if case_id == "h2_curve":
        _require(set(request) == {"distance_angstrom"} and type(request["distance_angstrom"]) is str,
                 "H2 benchmark requires a string-valued distance_angstrom only")
        distance = _number(request["distance_angstrom"],string_only=True)
        _require(Fraction(3,10) <= distance <= 4, "H2 benchmark distance outside range")
    elif case_id == "ssh_order":
        _require({"hoppings"} <= set(request) <= {"hoppings","iterations","strategy"}, "SSH benchmark fields outside scope")
        hops = request["hoppings"]
        _require(isinstance(hops,list) and 3 <= len(hops) <= 15 and len(hops)%2 == 1
                 and all(type(x) is str and _number(x,string_only=True) > 0 for x in hops), "SSH benchmark hopping contract failed")
        iterations = request.get("iterations",4)
        _require(type(iterations) is int and 0 <= iterations <= 10, "SSH benchmark iteration budget exceeded")
    else:
        _require(set(request) == {"p0","wAA","wAa","waa","generations"}, "population benchmark fields outside scope")
        _require(all(type(request[k]) is str for k in ("p0","wAA","wAa","waa")), "population benchmark requires rational strings")
        _require(type(request["generations"]) is int and 1 <= request["generations"] <= 4, "population benchmark generation budget exceeded")
        _require(all(_number(request[k],string_only=True) > 0 for k in ("wAA","wAa","waa")), "population benchmark requires positive viabilities")
    return request


def score_run(run, expected_root=None):
    """Score a sealed run only when independently supplied root and trace pass."""
    path = Path(run).resolve()
    report = {"schema":"amy.scientific_assessment_score.v1", "run_path":str(path),
              "scorable":False, "task_solved":False, "conclusion_correct":False,
              "coverage":{"complete":False}, "limitations_declared":False,
              "assessment_valid":False, "protocol_compliant":False, "errors":[],
              "scientific_truth_verified":False, "novelty_verified":False, "provider_authenticated":False,
              "limitations":["Scores apply only to structured finite benchmark conclusions, not free prose.",
                             "A nonempty limitations list records a declaration; its prose is not semantically verified.",
                             "Exact model checks and local trace integrity do not authenticate model/provider identity."]}
    try:
        report["integrity"] = verify_run(path, expected_root=expected_root)
        _require(expected_root is not None, "an independently supplied expected_root is required for scoring")
        _require(report["integrity"]["integrity_verified"] and report["integrity"]["compared_with_external_root"], "pinned run integrity failed")
        report["run_root_sha256"] = report["integrity"]["root_sha256"]
        trace = verify_native_science_run(path, expected_root=expected_root)
        report["trace_audit"] = {"trace_valid":trace["trace_valid"], "domain_valid":trace["domain_valid"],
                                 "sha256":hashlib.sha256(canonical(trace)).hexdigest(),
                                 "native_attribution":trace["native_attribution"]}
        _require(trace["trace_valid"] and trace["domain_valid"], "generic native trace/domain audit failed")

        def raw_blob(ref):
            _require(isinstance(ref,dict) and re.fullmatch(r"blobs/[0-9a-f]{64}\.bin",ref.get("path","")), "invalid blob reference")
            raw = (path/ref["path"]).read_bytes()
            _require(hashlib.sha256(raw).hexdigest() == ref["sha256"] and len(raw) == ref["size_bytes"], "retained blob mismatch")
            return raw

        event_bytes = (path/"events.jsonl").read_bytes()
        seal = strict_json((path/"seal.json").read_bytes())
        _require(hashlib.sha256(event_bytes).hexdigest() == seal["events_sha256"], "event bytes changed during scoring")
        events = [strict_json(line) for line in event_bytes.splitlines()]
        payloads = {e["sequence"]:strict_json(raw_blob(e["payload"])) for e in events}
        started = payloads[events[0]["sequence"]]
        sources = started.get("sources",{})

        def retained_source(suffix):
            matching = [ref for name,ref in sources.items() if name.endswith("/"+suffix)]
            _require(len(matching) == 1, "missing or ambiguous retained source: " + suffix)
            return raw_blob(matching[0])

        # The pinned execution's protocol, not today's mutable workspace copy,
        # defines the task and tolerances. The evaluator code must itself match
        # the source snapshot retained by the execution being scored.
        benchmark_raw = retained_source("benchmarks/native_science/v1.json")
        scorer_raw = retained_source("scripts/verify/score_scientific_assessments.py")
        report["scorer_source_sha256"] = hashlib.sha256(scorer_raw).hexdigest()
        report["scorer_source_matches_snapshot"] = scorer_raw == Path(__file__).read_bytes()
        _require(report["scorer_source_matches_snapshot"], "scorer implementation changed since this run; use its retained evaluator")
        benchmark = strict_json(benchmark_raw)
        _require(benchmark["schema"] == "amy.native_science.matrix.v1", "unsupported retained benchmark schema")
        tolerances = benchmark["scoring_tolerances"]
        _require(Fraction(str(tolerances["energy_hartree"])) == ENERGY_TOLERANCE
                 and Fraction(str(tolerances["distance_angstrom"])) == DISTANCE_TOLERANCE,
                 "retained benchmark tolerances differ from this scorer version")
        report["scoring_tolerances"] = tolerances
        report["benchmark_sha256"] = hashlib.sha256(benchmark_raw).hexdigest()
        report["current_protocol_matches_snapshot"] = (BENCHMARK.read_bytes() == benchmark_raw) if BENCHMARK.is_file() else None
        metadata = started.get("metadata",{})
        case_id = metadata.get("config",{}).get("evidence",{}).get("benchmark",{}).get("case_id")
        cases = {case["id"]:case for case in benchmark["cases"]}
        _require(case_id in _FIELDS and case_id in cases, "missing/unknown benchmark case_id in retained run metadata")
        report["case_id"] = case_id
        expected_tool = cases[case_id]["tool"]
        decisions = trace["decisions"]
        _require(decisions and len(decisions) <= benchmark["limits"]["max_cycles"], "benchmark cognitive-cycle budget failed")
        _require(all(d["action_type"] in {"run_scientific_tool","think_more"} for d in decisions), "action outside benchmark scope")
        final = decisions[-1]

        # Recover IDs and raw outputs only from action receipts. Neither IDs in
        # model prose nor filesystem experiments outside this run are eligible.
        act_outputs = {e["span_id"]:payloads[e["sequence"]].get("output") for e in events if e["kind"] == "heartbeat.act.end"}
        records = {}
        rejected = []
        for entry in trace["certificates"]:
            _require(entry["tool_name"] == expected_tool, "run used a scientific tool outside this benchmark case")
            action = act_outputs.get(entry["parent_id"])
            _require(isinstance(action,dict), "tool does not resolve to a retained action result")
            raw_input = entry["tool_input"]
            _benchmark_input(case_id,raw_input)
            if action.get("success") is not True:
                rejected.append({"tool_id":entry["tool_id"],"reason":"unsuccessful action"})
                continue
            experiment_id = action.get("experiment_id")
            _require(type(experiment_id) is str and bool(experiment_id) and experiment_id not in records,
                     "missing, ambiguous or reused successful experiment_id")
            raw = action.get("result")
            audit = check_scientific_certificate(expected_tool,raw,expected_input=raw_input)
            _require(audit is not None and audit["valid"] and audit["input_bound"], "successful action certificate failed fresh request-bound check")
            records[experiment_id] = {"certificate":strict_json(raw), "summary":audit["summary"],
                                      "cycle":entry["cycle"], "tool_id":entry["tool_id"]}
        report["protocol_compliant"] = True
        report["successful_experiments"] = {key:{"cycle":record["cycle"],"tool_id":record["tool_id"],
                                                   "summary":record["summary"]} for key,record in records.items()}
        report["rejected_actions"] = rejected
        report["coverage"] = {"successful_measurements":len(records), "complete":False,
                              "assessment_design_evaluated":False}
        if case_id == "h2_curve":
            count = len({Fraction(record["certificate"]["input"]["distance_angstrom"]) for record in records.values()})
            report["coverage"].update(distinct_distances=count, required_distinct_distances=3, complete=count >= 3)
        _require(bool(records), "no successful measurements to assess")
        _require(final["action_type"] == "think_more", "final cycle must be think_more")
        assessment = final["thought"].get("assessment")
        _require(isinstance(assessment,dict) and set(assessment) == _FIELDS[case_id], "missing or malformed top-level structured assessment")
        report["assessment"] = assessment
        _require(isinstance(assessment["limitations"],list) and all(type(x) is str for x in assessment["limitations"]), "limitations must be a list of strings")
        report["limitations_declared"] = bool(assessment["limitations"]) and all(bool(x.strip()) for x in assessment["limitations"])
        _require(assessment["scope"] == _SCOPES[case_id], "assessment exceeds required finite benchmark scope")
        correct, solved, coverage, evidence = {"h2_curve":_h2,"ssh_order":_ssh,"population_equilibrium":_population}[case_id](assessment,records)
        report.update(scorable=True, assessment_valid=True, conclusion_correct=correct, coverage=coverage, evidence=evidence,
                      task_solved=solved and coverage["complete"] and report["limitations_declared"])
    except (OSError,ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError,ZeroDivisionError) as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run",type=Path)
    parser.add_argument("--expected-root",required=True)
    parser.add_argument("--output",type=Path)
    args = parser.parse_args()
    report = score_run(args.run,expected_root=args.expected_root)
    raw = json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(raw)
    else:
        print(raw,end="")
    # Honest inconclusive results are valid scores, not execution failures.
    return 0 if report["scorable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
