"""Adversarial, hermetic tests for local execution receipts (no cloud calls).

Re-sealing helpers model structurally malformed but internally hashed input.
They do not assert that a local hash authenticates the producer: wholesale
replacement is only detectable when the caller retains an external root.
"""
import copy
import hashlib
import json
import shutil

import pytest

from core.execution_evidence import (
    EvidenceRun, current_evidence, evidence_span, record_bytes, record_event,
    verify_run,
)


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_seal(run):
    return json.loads((run.path / "seal.json").read_bytes())


def reseal(run, seal):
    """Recompute only the local root, never the separately retained root."""
    seal.pop("root_sha256", None)
    seal["root_sha256"] = sha(encoded(seal))
    (run.path / "seal.json").write_bytes(encoded(seal) + b"\n")
    return seal


def events(run):
    return [json.loads(line) for line in run.events_path.read_bytes().splitlines()]


def payload(run, event):
    return json.loads((run.path / event["payload"]["path"]).read_bytes())


def rechain(run, rows, seal=None):
    """Create valid links around a semantic mutation, preserving event order."""
    seal = read_seal(run) if seal is None else seal
    previous = ""
    for index, event in enumerate(rows, 1):
        event.pop("event_hash", None)
        event["sequence"] = index
        event["previous_hash"] = previous
        event["event_hash"] = sha(encoded(event))
        previous = event["event_hash"]
    raw = b"".join(encoded(row) + b"\n" for row in rows)
    run.events_path.write_bytes(raw)
    seal.update(events_sha256=sha(raw), event_count=len(rows), last_event_hash=previous)
    return reseal(run, seal)


def replace_payload(run, event, value, seal):
    data = encoded(value)
    digest = sha(data)
    relative = f"blobs/{digest}.bin"
    (run.path / relative).write_bytes(data)
    ref = {"sha256": digest, "size_bytes": len(data)}
    seal["blobs"][relative] = ref
    event["payload"] = {**event["payload"], **ref, "path": relative}


@pytest.fixture
def completed(tmp_path):
    source = tmp_path / "instrumented.py"
    source.write_bytes(b"# retained source\nanswer = 3\n")
    run = EvidenceRun(tmp_path / "run", metadata={"origin": "test"}, source_paths=[source])
    with run.activate():
        with evidence_span("decision", {"question": "compute"}, actor="amy.test") as outer:
            binary = record_bytes("raw-response", b"exact\x00bytes\xff")
            with evidence_span("tool", {"value": 3}, actor="amy.tool") as inner:
                inner.result({"value": 6, "raw": binary})
            record_event("decision.observation", {"answer": 6})
            outer.result({"answer": 6})
    seal = run.seal()
    return run, seal, source


def assert_rejected(run, **kwargs):
    report = verify_run(run.path, **kwargs)
    assert report["integrity_verified"] is False, report
    assert report["errors"], report
    return report


def test_complete_nested_receipt_verifies_against_external_root(completed):
    run, seal, _ = completed
    report = verify_run(run.path, expected_root=seal["root_sha256"])
    assert report["integrity_verified"], report
    assert report["compared_with_external_root"] is True
    assert report["provider_authenticated"] is False
    assert report["scientific_truth_verified"] is False
    rows = events(run)
    outer, inner = rows[1], rows[2]
    assert inner["parent_id"] == outer["span_id"]
    assert rows[3]["parent_id"] == outer["span_id"]
    assert rows[4]["parent_id"] == outer["span_id"]
    assert rows[-2]["parent_id"] is None


def test_offline_replay_uses_retained_bytes_not_mutable_source(completed, tmp_path):
    run, seal, source = completed
    source.write_bytes(b"# changed after sealing\n")
    archive = tmp_path / "copied-evidence"
    shutil.copytree(run.path, archive)
    report = verify_run(archive, expected_root=seal["root_sha256"])
    assert report["integrity_verified"], report
    source.unlink()
    assert verify_run(archive, expected_root=seal["root_sha256"])["integrity_verified"]


def test_seal_is_idempotent_and_no_new_events_or_blobs_are_allowed(completed):
    run, seal, _ = completed
    assert run.seal(status="different") == seal
    with pytest.raises(RuntimeError):
        run.event("late.event", {})
    with pytest.raises(RuntimeError):
        run.blob("late", b"late")


def test_disabled_instrumentation_preserves_outputs_and_exceptions():
    assert current_evidence() is None
    assert record_event("unused", {}) is None
    assert record_bytes("unused", b"bytes") is None
    with evidence_span("unused", {}) as span:
        assert span.result(3) == 3
    assert span.span_id is None
    with pytest.raises(LookupError):
        with evidence_span("unused", {}):
            raise LookupError("original")


def test_nested_runs_rejected_without_losing_outer_context(tmp_path):
    a = EvidenceRun(tmp_path / "a", metadata={})
    b = EvidenceRun(tmp_path / "b", metadata={})
    with a.activate():
        with pytest.raises(RuntimeError):
            with b.activate():
                pass
        assert current_evidence() is a
    assert current_evidence() is None
    assert verify_run(a.path, expected_root=a.seal()["root_sha256"])["integrity_verified"]
    assert verify_run(b.path, expected_root=b.seal()["root_sha256"])["integrity_verified"]


@pytest.mark.parametrize("exception", [RuntimeError("failed"), KeyboardInterrupt("cancelled")])
def test_errored_spans_close_preserve_error_and_restore_parent(tmp_path, exception):
    run = EvidenceRun(tmp_path / "run", metadata={})
    with run.activate():
        with pytest.raises(type(exception)):
            with evidence_span("outer", {}):
                with evidence_span("inner", {}) as span:
                    span.result({"partial": True})
                    raise exception
        record_event("after.error", {})
    assert current_evidence() is None
    seal = run.seal(status="failed")
    assert verify_run(run.path, expected_root=seal["root_sha256"])["integrity_verified"]
    rows = events(run)
    endings = [payload(run, event) for event in rows if event["kind"].endswith(".end")]
    assert all(end["status"] == "error" for end in endings)
    assert all(end["error_type"] == type(exception).__name__ for end in endings)
    assert endings[0]["output"] == {"partial": True}
    assert next(event for event in rows if event["kind"] == "after.error")["parent_id"] is None


@pytest.mark.parametrize("action", ["delete_seal", "delete_events", "delete_blob", "change_blob",
                                    "truncate_events", "duplicate_event", "reorder_events",
                                    "modify_event", "modify_seal"])
def test_tampering_or_missing_retained_bytes_rejected(completed, action):
    run, seal, _ = completed
    blob_path = run.path / next(iter(seal["blobs"]))
    lines = run.events_path.read_bytes().splitlines(keepends=True)
    if action == "delete_seal":
        (run.path / "seal.json").unlink()
    elif action == "delete_events":
        run.events_path.unlink()
    elif action == "delete_blob":
        blob_path.unlink()
    elif action == "change_blob":
        blob_path.write_bytes(blob_path.read_bytes() + b" changed")
    elif action == "truncate_events":
        run.events_path.write_bytes(b"".join(lines[:-1]))
    elif action == "duplicate_event":
        run.events_path.write_bytes(b"".join(lines[:2] + [lines[1]] + lines[2:]))
    elif action == "reorder_events":
        lines[2], lines[3] = lines[3], lines[2]
        run.events_path.write_bytes(b"".join(lines))
    elif action == "modify_event":
        row = json.loads(lines[1])
        row["actor"] = "different.actor"
        lines[1] = encoded(row) + b"\n"
        run.events_path.write_bytes(b"".join(lines))
    else:
        seal["status"] = "different"
        (run.path / "seal.json").write_bytes(encoded(seal))
    assert_rejected(run, expected_root=seal["root_sha256"])


def test_external_root_detects_wholesale_locally_consistent_replacement(completed):
    run, seal, _ = completed
    original = seal["root_sha256"]
    mutated = read_seal(run)
    rows = events(run)
    start = payload(run, rows[0])
    start["metadata"]["origin"] = "different untrusted producer claim"
    replace_payload(run, rows[0], start, mutated)
    rechain(run, rows, mutated)
    # Local hashing by itself provides integrity, not origin authentication.
    assert verify_run(run.path)["integrity_verified"]
    report = assert_rejected(run, expected_root=original)
    assert "independently retained root mismatch" in report["errors"]


@pytest.mark.parametrize("mutation", ["modified", "deleted"])
def test_source_changed_during_run_is_incomplete(tmp_path, mutation):
    source = tmp_path / "source.py"
    source.write_text("before\n")
    run = EvidenceRun(tmp_path / "run", metadata={}, source_paths=[source])
    if mutation == "deleted":
        source.unlink()
    else:
        source.write_text("after\n")
    seal = run.seal()
    assert seal["coverage_complete_for_instrumented_boundaries"] is False
    assert "source files changed during execution" in seal["incomplete_reasons"]
    assert_rejected(run, expected_root=seal["root_sha256"])
    started = payload(run, events(run)[0])
    assert (run.path / started["sources"][str(source)]["path"]).read_text() == "before\n"


def test_explicitly_omitted_boundary_is_incomplete(tmp_path):
    run = EvidenceRun(tmp_path / "run", metadata={})
    run.mark_incomplete("artifact could not be retained")
    seal = run.seal()
    assert seal["coverage_complete_for_instrumented_boundaries"] is False
    assert_rejected(run, expected_root=seal["root_sha256"])


def test_missing_artifact_before_seal_never_verifies(tmp_path):
    run = EvidenceRun(tmp_path / "run", metadata={})
    ref = run.blob("output", b"must be present")
    run.event("tool.result", {"artifact": ref})
    (run.path / ref["path"]).unlink()
    seal = run.seal()
    assert_rejected(run, expected_root=seal["root_sha256"])


@pytest.mark.parametrize("target", ["source", "nested_receipt"])
def test_omitted_referenced_file_is_rejected_even_if_manifest_resealed(completed, target):
    run, _, _ = completed
    rows = events(run)
    if target == "source":
        ref = next(iter(payload(run, rows[0])["sources"].values()))
    else:
        ref = payload(run, rows[3])["output"]["raw"]
    seal = read_seal(run)
    seal["blobs"].pop(ref["path"])
    (run.path / ref["path"]).unlink()
    reseal(run, seal)
    assert_rejected(run)


@pytest.mark.parametrize("location,value", [
    ("seal", None), ("seal", []), ("seal", 4), ("seal", "text"),
    ("blobs", None), ("blobs", []), ("blobs", "text"),
    ("event", None), ("event", []), ("event", 4), ("event", "text"),
    ("kind", None), ("kind", []), ("kind", 4),
])
def test_malformed_structures_return_rejection_instead_of_exception(completed, location, value):
    run, _, _ = completed
    if location == "seal":
        (run.path / "seal.json").write_bytes(encoded(value))
    elif location == "blobs":
        seal = read_seal(run)
        seal["blobs"] = value
        reseal(run, seal)
    elif location == "event":
        run.events_path.write_bytes(encoded(value) + b"\n")
    else:
        rows = events(run)
        rows[1]["kind"] = value
        rechain(run, rows)
    assert_rejected(run)


@pytest.mark.parametrize("field,value", [("schema_version", 99), ("schema_version", True),
                                          ("event_count", 7.0),
                                          ("coverage_complete_for_instrumented_boundaries", "false"),
                                          ("coverage_complete_for_instrumented_boundaries", 1)])
def test_seal_schema_and_types_are_not_inferred_from_truthiness(completed, field, value):
    run, _, _ = completed
    seal = read_seal(run)
    seal[field] = value
    reseal(run, seal)
    assert_rejected(run)


@pytest.mark.parametrize("mutation", ["replayed_span", "unknown_parent", "wrong_actor",
                                     "end_before_start", "parent_closed_before_child",
                                     "missing_end", "duplicate_start_boundary"])
def test_rehashed_invalid_span_graph_or_boundaries_are_rejected(completed, mutation):
    run, _, _ = completed
    rows = events(run)
    if mutation == "replayed_span":
        rows[-1:-1] = copy.deepcopy(rows[1:-1])
    elif mutation == "unknown_parent":
        rows[2]["parent_id"] = "unknown"
    elif mutation == "wrong_actor":
        rows[3]["actor"] = "impostor"
    elif mutation == "end_before_start":
        rows[2], rows[3] = rows[3], rows[2]
    elif mutation == "parent_closed_before_child":
        # Outer end precedes inner end; hashes alone cannot enforce nesting.
        rows[3], rows[5] = rows[5], rows[3]
        rows.pop(4)  # omit the observation so it cannot independently reveal this
    elif mutation == "missing_end":
        rows.pop(3)
    else:
        rows.insert(1, copy.deepcopy(rows[0]))
    rechain(run, rows)
    assert_rejected(run)


def test_resealed_complete_flag_cannot_erase_recorded_coverage_failure(tmp_path):
    run = EvidenceRun(tmp_path / "run", metadata={})
    run.mark_incomplete("missing instrumented boundary")
    seal = run.seal()
    seal["coverage_complete_for_instrumented_boundaries"] = True
    seal["incomplete_reasons"] = []
    reseal(run, seal)
    assert_rejected(run)


def test_finished_payload_cannot_claim_unclosed_spans_in_valid_seal(completed):
    run, _, _ = completed
    rows = events(run)
    seal = read_seal(run)
    final = payload(run, rows[-1])
    final["unclosed_spans"] = ["missing-span"]
    replace_payload(run, rows[-1], final, seal)
    rechain(run, rows, seal)
    assert_rejected(run)


def test_payload_json_must_be_parseable_even_if_blob_hash_matches(completed):
    run, _, _ = completed
    rows = events(run)
    seal = read_seal(run)
    content = b"not valid JSON"
    relative = f"blobs/{sha(content)}.bin"
    (run.path / relative).write_bytes(content)
    ref = {"sha256": sha(content), "size_bytes": len(content)}
    seal["blobs"][relative] = ref
    rows[1]["payload"].update(ref, path=relative)
    rechain(run, rows, seal)
    assert_rejected(run)


@pytest.mark.parametrize("kind", ["unsafe_path", "symlink"])
def test_blob_path_escape_and_symlink_rejected(completed, tmp_path, kind):
    run, _, _ = completed
    seal = read_seal(run)
    relative = next(iter(seal["blobs"]))
    if kind == "unsafe_path":
        seal["blobs"]["../escaped.bin"] = seal["blobs"].pop(relative)
        reseal(run, seal)
    else:
        outside = tmp_path / "outside.bin"
        blob = run.path / relative
        outside.write_bytes(blob.read_bytes())
        blob.unlink()
        blob.symlink_to(outside)
    assert_rejected(run)


@pytest.mark.parametrize("content", [b'{"input":{"value":NaN}}',
                                     b'{"input":1,"input":2}',
                                     b"[" * 2000 + b"0" + b"]" * 2000])
def test_ambiguous_nonfinite_and_excessively_nested_payload_json_rejected(completed, content):
    run, _, _ = completed
    rows = events(run)
    seal = read_seal(run)
    relative = f"blobs/{sha(content)}.bin"
    (run.path / relative).write_bytes(content)
    ref = {"sha256": sha(content), "size_bytes": len(content)}
    seal["blobs"][relative] = ref
    rows[1]["payload"].update(ref, path=relative)
    rechain(run, rows, seal)
    assert_rejected(run)


def test_scientific_paths_and_binary_receipts_do_not_require_external_files(tmp_path):
    run = EvidenceRun(tmp_path / "run", metadata={})
    with run.activate():
        binary = record_bytes("failed-http-body", b"not JSON", "application/json")
        record_event("scientific.output", {
            "model_path": "/a/scientific/file/that/is/not/an/evidence/receipt",
            "mapping": {"path": "model.xyz", "value": [1, 2]},
            "transport_body": binary,
        })
    seal = run.seal()
    # Binary transport bodies retain exact bytes, even when a server labels an
    # error body application/json. Only event payloads must be JSON objects.
    assert verify_run(run.path, expected_root=seal["root_sha256"])["integrity_verified"]


def test_unserializable_span_output_leaves_detectable_missing_end(tmp_path):
    run = EvidenceRun(tmp_path / "run", metadata={})
    with run.activate():
        with pytest.raises(ValueError):
            with evidence_span("tool", {}) as span:
                span.result(float("nan"))
        record_event("after.failure", {})
    assert current_evidence() is None
    seal = run.seal()
    assert_rejected(run, expected_root=seal["root_sha256"])
