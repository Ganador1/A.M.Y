#!/usr/bin/env python3
"""Offline audit of the recorded AMY decision -> scientific tool -> learning chain.

This checks local records, never provider identity or scientific novelty. It does
not replay AMY's JSON repair: executable decisions must bind to complete raw JSON.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.execution_evidence import canonical, verify_run
# The frozen H2-only auditor remains unchanged. Shared parsing is preserved here
# while each new domain uses its own producer-independent mathematical checker.
from core.scientific_certificate_checks import check_scientific_certificate

DOMAIN_FILES = {
    "h2_rhf_certificate": "h2_rhf_verifier.py",
    "ssh_gap_certificate": "ssh_spectral_certificate.py",
    "population_selection_certificate": "population_selection_verifier.py",
}


def domain_module(tool_name):
    spec = importlib.util.spec_from_file_location(
        "amy_offline_" + tool_name, ROOT / "atlas/app" / DOMAIN_FILES[tool_name])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def reject(value):
        raise ValueError(f"nonfinite JSON value: {value}")

    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=reject)
    canonical(value)  # Also rejects exponent overflow to infinity.
    return value


def same(left, right):
    """Type-sensitive JSON equality (True must not equal 1)."""
    return canonical(left) == canonical(right)


def canonical_distance_input(raw):
    """Independent exact binding to the producer's rational input convention."""
    request = strict_json(raw)
    if not isinstance(request, dict) or len(request) != 1:
        raise ValueError("tool input must specify one distance")
    unit, value = next(iter(request.items()))
    if unit not in {"distance_angstrom", "distance_bohr"} or isinstance(value, bool):
        raise ValueError("unsupported distance unit or value")
    if not isinstance(value, (str, int, float)):
        raise ValueError("distance must be a string or number")
    text = str(value).strip()
    if len(text) > 64:
        raise ValueError("distance input too long")
    return {unit: str(Fraction(text))}


def raw_action_json(content):
    """Accept complete JSON or one complete Markdown fence; never repair it."""
    fenced = re.fullmatch(r"\s*```(?:json)?\s*\n(.*?)\n```\s*", content, re.DOTALL)
    return strict_json(fenced.group(1) if fenced else content), "complete_fence" if fenced else "json"


def input_rational(value, *, bits, token_limit, decimal_float=False):
    if type(value) not in (str, int) and not (decimal_float and type(value) is float):
        raise ValueError("input rational must have an explicit numeric/string type, never bool")
    text = str(value).strip()
    if len(text) > token_limit:
        raise ValueError("input rational token too long")
    if not re.fullmatch(r"[+-]?(?:\d+/\d+|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)", text):
        raise ValueError("invalid rational syntax")
    exponent = re.search(r"[eE]([+-]?\d+)$", text)
    if exponent and abs(int(exponent[1])) > 128:
        raise ValueError("decimal exponent exceeds input scope")
    value = Fraction(text)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > bits:
        raise ValueError("rational input precision exceeds scope")
    return value


def decode_hex(pair):
    if (not isinstance(pair, list) or len(pair) != 2
            or any(type(token) is not str or len(token) > 16386
                   or re.fullmatch(r"0x(?:0|[1-9a-f][0-9a-f]*)", token) is None for token in pair)):
        raise ValueError("invalid bounded hex rational")
    value = Fraction(int(pair[0], 16), int(pair[1], 16))
    if pair != [hex(value.numerator), hex(value.denominator)]:
        raise ValueError("noncanonical hex rational")
    return value


def independent_domain_check(tool_name, raw_output, raw_input):
    """Recompute the pure domain oracle and bind typed input separately.

    The extra runtime wrapper is checked too, but it is not the only oracle or
    the implementation of the independent request-binding comparisons here.
    """
    if tool_name not in DOMAIN_FILES:
        raise ValueError("tool outside declared audit scope")
    cap = 256*1024 if tool_name == "population_selection_certificate" else 48*1024
    if not isinstance(raw_output, str) or len(raw_output.encode()) > cap:
        raise ValueError("certificate output outside byte/type limit")
    cert = strict_json(raw_output)
    if not isinstance(cert, dict):
        raise ValueError("certificate must be a JSON object")
    module = domain_module(tool_name)
    if tool_name == "h2_rhf_certificate":
        verification = module.verify_h2_rhf_certificate(cert)
        expected = canonical_distance_input(raw_input)
        bound = same(cert.get("input"), expected)
        summary = {"distance_angstrom": cert.get("geometry", {}).get("distance_angstrom"),
                   "total_energy_hartree": cert.get("state", {}).get("total_energy")}
        kind = "h2_rhf_numerical_consistency"
    elif tool_name == "population_selection_certificate":
        verification = module.verify_population_selection_certificate(cert)
        request = strict_json(raw_input)
        keys = {"p0", "wAA", "wAa", "waa", "generations"}
        if not isinstance(request, dict) or set(request) != keys:
            raise ValueError("population request fields differ from contract")
        n = request["generations"]
        if type(n) is not int or not 0 <= n <= 64:
            raise ValueError("population generations must be an integer in [0,64]")
        expected = {"generations": n}
        for key in keys-{"generations"}:
            value = input_rational(request[key], bits=64, token_limit=80)
            if value < 0 or key == "p0" and value > 1:
                raise ValueError("population input outside scope")
            expected[key] = str(value)
        bound = same(cert.get("input"), expected)
        summary = cert.get("summary")
        kind = "population_selection_exact_trajectory"
    else:
        # SSH accepts exact lexical decimal values in JSON, so keep decimal
        # tokens as strings instead of round-tripping them through float64.
        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise ValueError("duplicate SSH request key")
                result[key] = value
            return result
        request = json.loads(raw_input, parse_float=str, object_pairs_hook=pairs)
        if not isinstance(request, dict) or set(request)-{"hoppings", "iterations", "threshold", "strategy"}:
            raise ValueError("unsupported SSH request fields")
        hops = request.get("hoppings")
        if not isinstance(hops, list) or not 3 <= len(hops) <= 511 or len(hops)%2 != 1:
            raise ValueError("SSH request requires 3..511 odd positive hoppings")
        expected_hops = [input_rational(value, bits=128, token_limit=128) for value in hops]
        if any(value <= 0 for value in expected_hops):
            raise ValueError("SSH hoppings must be positive")
        iterations, strategy = request.get("iterations", 4), request.get("strategy", "float")
        if type(iterations) is not int or not 0 <= iterations <= 100 or strategy not in ("float", "auto"):
            raise ValueError("SSH iteration/strategy outside contract")
        threshold = input_rational(request["threshold"], bits=128, token_limit=128) if "threshold" in request else None
        if threshold is not None and threshold < 0:
            raise ValueError("negative SSH threshold")
        encoded = cert["certificate"]
        exact = {name: encoded[name] for name in ("method", "scope")}
        exact.update({name: decode_hex(encoded[name]) for name in ("gap_squared_lower", "gap_squared_upper")})
        exact.update({name: [decode_hex(value) for value in encoded[name]] for name in ("hoppings", "witness")})
        verification = module.verify_gap_certificate(exact)
        retained_threshold = decode_hex(cert["threshold"]["value"]) if "threshold" in cert else None
        retained_strategy = cert.get("strategy_requested", "float")
        bound = (exact["hoppings"] == expected_hops and threshold == retained_threshold
                 and type(cert.get("iterations")) is int and cert["iterations"] == iterations
                 and retained_strategy == strategy)
        expected = {"hoppings": [str(value) for value in expected_hops], "iterations": iterations,
                    "strategy": strategy, "threshold": str(threshold) if threshold is not None else None}
        summary = {"site_count": cert.get("site_count"), "gap_squared_lower": encoded["gap_squared_lower"],
                   "gap_squared_upper": encoded["gap_squared_upper"], "encoding": encoded["encoding"]}
        kind = "ssh_exact_squared_gap_bounds"
    valid = verification is True if tool_name == "ssh_gap_certificate" else verification.get("valid") is True
    envelope = check_scientific_certificate(tool_name, raw_output, expected_input=raw_input)
    return {"certificate": cert, "certificate_kind": kind, "model_instance_valid": valid,
            "input_bound": bound, "exact_input_normalized": expected, "pure_verification": verification,
            "envelope_valid": isinstance(envelope, dict) and envelope.get("valid") is True,
            "envelope_check": envelope, "summary": summary}


def audit_tool_chain(tool, act, action_result, context, report, check, children, output):
    tool_id, supplied = tool["begin"]["span_id"], tool["input"]
    tool_name, raw = supplied.get("tool_name"), output(tool)
    entry = {"cycle": context["cycle"], "tool_id": tool_id, "tool_name": tool_name,
             "parent_id": tool["begin"]["parent_id"], "tool_input": supplied.get("tool_input"),
             "model_instance_valid": None, "input_bound": False, "envelope_valid": False}
    report["certificates"].append(entry)
    check("tool_result_matches_action_result", same(raw, action_result.get("result")), tool_id=tool_id)
    # Operational tool failures are retained, not mistaken for certificates.
    structured_error = None
    try:
        structured_error = strict_json(raw) if isinstance(raw, str) and not raw.startswith("Error:") else None
    except (ValueError, TypeError, RecursionError):
        pass
    if (isinstance(raw, str) and raw.startswith("Error:")
            or isinstance(structured_error, dict) and structured_error.get("status") == "error"):
        entry["operational_error"] = raw
        check("tool_error_not_accepted", action_result.get("success") is False, tool_id=tool_id)
        return
    try:
        result = independent_domain_check(tool_name, raw, supplied.get("tool_input"))
        certificate = result.pop("certificate")
        entry.update(result)
        check("certificate_bound_to_exact_tool_input", entry["input_bound"], tool_id=tool_id)
        audits = [verification for verification in children(act, "atlas.certificate_verification")
                  if verification["input"].get("tool_name") == tool_name
                  and same(verification["input"].get("certificate"), certificate)]
        check("one_bound_runtime_verification", len(audits) == 1, tool_id=tool_id)
        if len(audits) == 1:
            verification = audits[0]
            entry["verification_id"] = verification["begin"]["span_id"]
            check("verification_follows_tool", tool["end"]["sequence"] < verification["begin"]["sequence"], tool_id=tool_id)
            check("runtime_audit_matches_recomputation", same(output(verification), result["pure_verification"]), tool_id=tool_id)
        if action_result.get("success") is True:
            check("accepted_domain_result_verified", result["model_instance_valid"] and result["input_bound"]
                  and result["envelope_valid"], tool_id=tool_id)
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError, ZeroDivisionError, OverflowError, ImportError) as exc:
        entry.update(model_instance_valid=False, error=str(exc))
        check("domain_certificate_parseable", False, tool_id=tool_id, error=str(exc))


def verify_native_science_run(directory, *, expected_root=None):
    path = Path(directory).resolve()
    integrity = verify_run(path, expected_root=expected_root)
    report = {
        "schema": "amy.native_science_chain_audit.v1", "run_path": str(path),
        "integrity": integrity, "trace_valid": False, "domain_valid": False,
        "causal_checks": [], "calls": [], "decisions": [], "certificates": [],
        "native_attribution": {"consistent_with_recorded_native_path": False,
                               "provider_identity_authenticated": False,
                               "local_actor_identity_authenticated": False},
        "limitations": [
            "Local recorded causal consistency is not authenticated execution or provider identity.",
            "Each checker certifies its stated finite mathematical or numerical model only, not scientific novelty or empirical truth.",
            "A memory snapshot records state, not truth or proof of model comprehension.",
            "Model action JSON repairs are not reproduced or silently accepted by this verifier.",
        ],
    }
    if not integrity["integrity_verified"]:
        return report

    def check(name, valid, **context):
        report["causal_checks"].append({"check": name, "valid": bool(valid), **context})
        return bool(valid)

    def read_ref(ref):
        if not isinstance(ref, dict) or not re.fullmatch(r"blobs/[0-9a-f]{64}\.bin", ref.get("path", "")):
            raise ValueError("invalid body reference")
        raw = (path / ref["path"]).read_bytes()
        if len(raw) != ref["size_bytes"] or hashlib.sha256(raw).hexdigest() != ref["sha256"]:
            raise ValueError("body reference does not match bytes")
        return raw

    events = [strict_json(line) for line in (path / "events.jsonl").read_bytes().splitlines()]
    payloads = {event["sequence"]: strict_json(read_ref(event["payload"])) for event in events}
    spans = {}
    for event in events:
        if event["kind"].endswith(".begin"):
            spans[event["span_id"]] = {"begin": event, "input": payloads[event["sequence"]]["input"]}
        elif event["kind"].endswith(".end"):
            spans[event["span_id"]].update(end=event, result=payloads[event["sequence"]])

    def kind(span):
        return span["begin"]["kind"][:-6]

    def ancestor(span, expected):
        parent = span["begin"]["parent_id"]
        while parent in spans:
            current = spans[parent]
            if kind(current) == expected:
                return current
            parent = current["begin"]["parent_id"]
        return None

    def children(parent, expected):
        return [span for span in spans.values() if kind(span) == expected
                and span["begin"]["parent_id"] == parent["begin"]["span_id"]]

    def output(span):
        return span["result"].get("output") if span else None

    def singleton(parent, expected):
        found = children(parent, expected)
        check("one_"+expected, len(found) == 1, parent_id=parent["begin"]["span_id"])
        return found[0] if len(found) == 1 else None

    # Include every HTTP attempt, not only the successful model decisions.
    envelopes = {}
    for span in spans.values():
        if kind(span) != "llm.transport":
            continue
        sid = span["begin"]["span_id"]
        decision, cycle = ancestor(span, "reasoning.decision"), ancestor(span, "heartbeat.cycle")
        retained = output(span) or {}
        receipt = retained.get("receipt", {})
        item = {"span_id": sid, "parent_id": span["begin"]["parent_id"],
                "decision_id": decision["begin"]["span_id"] if decision else None,
                "cycle": cycle["input"].get("cycle") if cycle else None,
                "status": span["result"].get("status"), "http_status": receipt.get("status_code"),
                "error_type": span["result"].get("error_type"), "error": span["result"].get("error"),
                "model": span["input"].get("payload", {}).get("model"),
                "response_body_sha256": receipt.get("response_body", {}).get("sha256")}
        report["calls"].append(item)
        try:
            if receipt.get("request_body"):
                request = strict_json(read_ref(receipt["request_body"]))
                check("wire_request_matches_payload", same(request, span["input"].get("payload")), call_id=sid)
            if receipt.get("response_body"):
                raw = read_ref(receipt["response_body"])
                item["response_bytes"] = len(raw)
                if receipt.get("status_code") == 200:
                    envelope = strict_json(raw)
                    envelopes[sid] = envelope
                    check("raw_response_matches_decoded", same(envelope, retained.get("response")), call_id=sid)
                    item.update(done=envelope.get("done"), done_reason=envelope.get("done_reason"))
            if span["result"].get("status") == "returned":
                check("returned_http_has_raw_receipts", bool(receipt.get("request_body")) and sid in envelopes, call_id=sid)
        except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
            check("transport_receipt_readable", False, call_id=sid, error=str(exc))

    cycles = [span for span in spans.values() if kind(span) == "heartbeat.cycle"]
    check("has_cognitive_cycles", bool(cycles))
    for cycle in cycles:
        cycle_no, cycle_id = cycle["input"].get("cycle"), cycle["begin"]["span_id"]
        think = singleton(cycle, "heartbeat.think")
        act = singleton(cycle, "heartbeat.act")
        learn = singleton(cycle, "heartbeat.learn")
        decision = singleton(think, "reasoning.decision") if think else None
        if not all((think, act, learn, decision)):
            continue
        thought = output(decision)
        item = {"cycle": cycle_no, "span_id": decision["begin"]["span_id"],
                "decision_id": decision["begin"]["span_id"], "act_id": act["begin"]["span_id"],
                "parent_id": decision["begin"]["parent_id"], "cycle_id": cycle_id,
                "thought": thought, "action_type": (thought or {}).get("action_type"),
                "tool_calls": [], "memory_snapshots": []}
        report["decisions"].append(item)
        context = {"cycle": cycle_no, "decision_id": item["span_id"]}
        check("reasoning_input_matches_cycle_focus", same(decision["input"].get("focus"), think["input"].get("focus"))
              and same(decision["input"].get("context", {}).get("cycle"), cycle_no), **context)
        check("decision_think_act_identical", same(thought, output(think))
              and same(thought, act["input"].get("thought")), **context)
        check("decision_precedes_action", decision["end"]["sequence"] < act["begin"]["sequence"], **context)
        attempts = children(decision, "llm.transport")
        check("decision_has_model_attempt", bool(attempts), **context)
        returned = [attempt for attempt in attempts if attempt["result"].get("status") == "returned"]
        if returned:
            attempt = returned[-1]
            envelope = envelopes.get(attempt["begin"]["span_id"], {})
            incomplete = envelope.get("done") is False or envelope.get("done_reason") == "length"
            if incomplete:
                check("incomplete_model_action_rejected", thought.get("action_type") == "think_more"
                      and thought.get("error") == "incomplete_model_response" and not children(act, "atlas.scientific_tool"), **context)
            else:
                check("accepted_model_response_complete", envelope.get("done") is True, **context)
                try:
                    message = envelope["message"]
                    raw_content = message.get("content", "")
                    if not raw_content.strip():
                        raw_content = message.get("thinking", "")
                    parsed, item["raw_action_format"] = raw_action_json(raw_content)
                    if not isinstance(parsed, dict):
                        raise ValueError("raw model action must be an object")
                    enriched = copy.deepcopy(parsed)
                    focus = decision["input"].get("focus", {})
                    enriched.update(source=focus.get("source", "unknown"),
                                    focus_content=focus.get("content", "")[:200],
                                    cycle=decision["input"].get("context", {}).get("cycle", 0))
                    enriched.setdefault("action_type", "think_more")
                    if isinstance(parsed.get("action_details"), dict):
                        enriched.update(parsed["action_details"])
                    check("raw_action_matches_executed_decision", same(enriched, thought), **context)
                    parsed_events = [event for event in events if event["kind"] == "reasoning.parsed_response"
                                     and event["parent_id"] == item["span_id"]]
                    check("raw_action_matches_parse_event", len(parsed_events) == 1 and same(
                        payloads[parsed_events[0]["sequence"]].get("thought"), parsed), **context)
                except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
                    check("raw_action_independently_parseable", False, error=str(exc), **context)
        else:
            check("failed_transport_does_not_execute_tool", thought.get("action_type") == "think_more"
                  and not children(act, "atlas.scientific_tool"), **context)

        action_result = output(act)
        check("learning_receives_exact_action", same(learn["input"].get("thought"), thought)
              and same(learn["input"].get("action_result"), action_result), **context)
        check("action_precedes_learning", act["end"]["sequence"] < learn["begin"]["sequence"], **context)
        snapshots = [event for event in events if event["kind"] == "memory.snapshot"
                     and event["parent_id"] == learn["begin"]["span_id"]]
        check("learning_snapshot_present", len(snapshots) == 1, **context)
        for event in snapshots:
            snapshot = payloads[event["sequence"]]
            check("snapshot_matches_cycle", snapshot.get("cycle") == cycle_no
                  and snapshot.get("state") == "after_learning", **context)
            item["memory_snapshots"].append({"sequence": event["sequence"], "parent_id": event["parent_id"],
                                             "payload_sha256": event["payload"]["sha256"]})

        tools = children(act, "atlas.scientific_tool")
        if thought.get("action_type") == "run_scientific_tool" and action_result.get("success") is True:
            check("successful_action_has_one_tool_call", len(tools) == 1, **context)
        if tools:
            check("tool_was_model_selected", thought.get("action_type") == "run_scientific_tool", **context)
        for tool in tools:
            tool_id, supplied = tool["begin"]["span_id"], tool["input"]
            item["tool_calls"].append(tool_id)
            check("tool_call_matches_decision", supplied.get("tool_name") == thought.get("tool_name")
                  and same(supplied.get("tool_input"), thought.get("tool_input"))
                  and supplied.get("domain") == thought.get("domain", "mathematics"), tool_id=tool_id, **context)
            audit_tool_chain(tool, act, action_result, context, report, check, children, output)

    # No orphan scientific tools or decisions outside a cognitive cycle can be omitted.
    decision_ids = {item["span_id"] for item in report["decisions"]}
    check("all_decisions_linked_to_cycles", all(span["begin"]["span_id"] in decision_ids
          for span in spans.values() if kind(span) == "reasoning.decision"))
    tool_ids = {sid for item in report["decisions"] for sid in item["tool_calls"]}
    check("all_tools_linked_to_decisions", all(span["begin"]["span_id"] in tool_ids
          for span in spans.values() if kind(span) == "atlas.scientific_tool"))
    report["trace_valid"] = all(item["valid"] for item in report["causal_checks"])
    domain_results = [item["model_instance_valid"] and item["input_bound"] and item["envelope_valid"]
                      for item in report["certificates"] if item["model_instance_valid"] is not None]
    report["domain_valid"] = bool(domain_results) and all(domain_results)
    metadata = payloads[events[0]["sequence"]].get("metadata", {})
    lifecycle_linked = all(ancestor(cycle, "amy.lifecycle") is not None for cycle in cycles)
    fixture = metadata.get("fixture") is True or metadata.get("origin") == "hermetic_test"
    report["native_attribution"].update(
        declared_entrypoint=metadata.get("entrypoint"), fixture=fixture,
        lifecycle_linked=lifecycle_linked,
        consistent_with_recorded_native_path=report["trace_valid"] and lifecycle_linked and not fixture
        and metadata.get("entrypoint") == "amy.AMY.start",
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--expected-root")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = verify_native_science_run(args.directory, expected_root=args.expected_root)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as exc:
        report = {"trace_valid": False, "domain_valid": False, "error": f"{type(exc).__name__}: {exc}"}
    serialized = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized)
    else:
        print(serialized, end="")
    return 0 if report["trace_valid"] and report["domain_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
