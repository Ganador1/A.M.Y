"""Domain-independent execution receipts for an instrumented AMY process.

Records observable inputs, outputs and failures, not private provider internals
or scientific truth. A seal detects deletion/truncation relative to that seal;
an independently retained root is needed against wholesale local replacement.
No credentials, HTTP authorization headers or environment variables are read.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import tempfile
import threading
import uuid

_CURRENT: ContextVar[EvidenceRun | None] = ContextVar("amy_evidence_run", default=None)
_PARENT: ContextVar[str | None] = ContextVar("amy_evidence_parent", default=None)
_LABEL = re.compile(r"^[A-Za-z0-9_.-]{1,160}$")
_INHERIT_PARENT = object()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_digest(path: Path) -> tuple[str, int]:
    """Hash retained data in bounded chunks, including multi-gigabyte runs."""
    sha, size = hashlib.sha256(), 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
            size += len(chunk)
    return sha.hexdigest(), size


def _write(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".writing-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def current_evidence() -> EvidenceRun | None:
    return _CURRENT.get()


class EvidenceRun:
    """A fresh, single-process run with thread-safe, immutable blob storage."""

    def __init__(self, directory: str | Path, *, metadata: dict, source_paths=()):
        self.path = Path(directory).resolve()
        self.path.mkdir(parents=True, exist_ok=False)
        (self.path / "blobs").mkdir()
        self.events_path = self.path / "events.jsonl"
        self.events_path.touch()
        self.run_id = self.path.name
        self._lock = threading.RLock()
        self._sequence = 0
        self._previous = ""
        self._blobs = {}
        self._sources = {}
        self._open_spans = set()
        self._closed = False
        self._incomplete_reasons = []
        self.metadata = metadata
        for source in source_paths:
            source = Path(source).resolve()
            ref = self.blob(source.name, source.read_bytes(), "text/plain")
            self._sources[str(source)] = ref
        self.event("run.started", {
            "metadata": metadata,
            "environment": {"python": platform.python_version(), "system": platform.system(),
                            "machine": platform.machine()},
            "sources": self._sources,
            "assurance": {"provider_authenticated": False, "scientific_truth_verified": False,
                          "scope": "Observable instrumented AMY boundaries; source/version receipts and retained bytes"},
        }, actor="amy.runtime")

    def blob(self, label: str, data: bytes, media_type="application/octet-stream") -> dict:
        if not isinstance(data, bytes):
            raise TypeError("evidence blobs must contain exact bytes")
        with self._lock:
            if self._closed:
                raise RuntimeError("evidence run is already sealed")
            sha = digest(data)
            relative = f"blobs/{sha}.bin"
            path = self.path / relative
            if path.exists():
                if path.read_bytes() != data:
                    raise RuntimeError("evidence blob changed or digest collision")
            else:
                _write(path, data)
            ref = {"path": relative, "sha256": sha, "size_bytes": len(data),
                   "media_type": media_type, "label": label}
            self._blobs[relative] = {"sha256": sha, "size_bytes": len(data)}
            return ref

    def import_inherited_references(self, value, *, origin_root: str | Path):
        """Bind inherited receipts to exact bytes and a retained origin seal.

        A matching, self-consistent origin manifest is required. This certifies
        the imported bytes, not completeness or scientific truth of that run.
        Historical runs are never modified or retroactively repaired.
        """
        wanted = {}

        def collect(item, depth=0):
            if depth > 256:
                raise ValueError("inherited payload nesting exceeds supported depth")
            if isinstance(item, dict):
                if {"path", "sha256", "size_bytes"} <= item.keys():
                    relative, sha, size = item["path"], item["sha256"], item["size_bytes"]
                    if (not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{64}", sha) is None
                            or relative != f"blobs/{sha}.bin" or type(size) is not int or size < 0):
                        raise ValueError("invalid inherited blob reference")
                    entry = {"sha256": sha, "size_bytes": size}
                    if relative in wanted and wanted[relative] != entry:
                        raise ValueError("conflicting inherited blob reference")
                    if relative in self._blobs and self._blobs[relative] != entry:
                        raise ValueError("conflicting local blob reference")
                    wanted[relative] = entry
                for child in item.values():
                    collect(child, depth + 1)
            elif isinstance(item, list):
                for child in item:
                    collect(child, depth + 1)

        collect(value)
        pending = {key: ref for key, ref in wanted.items() if key not in self._blobs}
        origins = []
        for seal_path in sorted(Path(origin_root).glob("*/seal.json")):
            if not pending:
                break
            origin = seal_path.parent
            if origin.resolve() == self.path or origin.is_symlink() or seal_path.is_symlink():
                continue
            try:
                raw_seal = seal_path.read_bytes()
                seal = json.loads(raw_seal)
                root = seal.pop("root_sha256")
                if digest(canonical(seal)) != root or not isinstance(seal.get("blobs"), dict):
                    continue
                matches = {key: ref for key, ref in pending.items() if seal["blobs"].get(key) == ref}
                if not matches:
                    continue
                if (origin / "blobs").is_symlink():
                    continue
                for relative, ref in matches.items():
                    source = origin / relative
                    if source.is_symlink() or _file_digest(source) != (ref["sha256"], ref["size_bytes"]):
                        raise ValueError(f"inherited blob differs from origin manifest: {relative}")
                    target = self.path / relative
                    with source.open("rb") as incoming, target.open("xb") as outgoing:
                        shutil.copyfileobj(incoming, outgoing, length=1024 * 1024)
                        outgoing.flush()
                        os.fsync(outgoing.fileno())
                    if _file_digest(target) != (ref["sha256"], ref["size_bytes"]):
                        raise ValueError("inherited blob changed while copying")
                    self._blobs[relative] = ref
                    del pending[relative]
                origins.append({"origin_run_id": seal.get("run_id"), "origin_root_sha256": root,
                                "origin_seal": self.blob("inherited-origin-seal.json", raw_seal, "application/json"),
                                "imported_paths": sorted(matches)})
            except (OSError, KeyError, TypeError, json.JSONDecodeError):
                continue
        if pending:
            raise ValueError(f"unbound inherited blob references: {len(pending)}")
        if origins:
            self.event("memory.inherited_blobs", {"origins": origins,
                       "scope": "Exact imported bytes bound to retained origin manifests; origin execution completeness not asserted"})
        return sum(len(origin["imported_paths"]) for origin in origins)

    def event(self, kind: str, payload, *, actor="amy.runtime", span_id=None, parent_id=_INHERIT_PARENT) -> str:
        if not _LABEL.fullmatch(kind) or not _LABEL.fullmatch(actor):
            raise ValueError("invalid event or actor label")
        body = canonical(payload)
        with self._lock:
            if self._closed:
                raise RuntimeError("evidence run is already sealed")
            ref = self.blob(f"{kind}.json", body, "application/json")
            record = {"schema_version": 1, "run_id": self.run_id,
                      "sequence": self._sequence+1, "previous_hash": self._previous,
                      "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                      "kind": kind, "actor": actor, "span_id": span_id,
                      "parent_id": _PARENT.get() if parent_id is _INHERIT_PARENT else parent_id,
                      "payload": ref}
            record["event_hash"] = digest(canonical(record))
            with self.events_path.open("ab") as handle:
                handle.write(canonical(record)+b"\n")
                handle.flush()
                os.fsync(handle.fileno())
            self._sequence += 1
            self._previous = record["event_hash"]
            return self._previous

    def mark_incomplete(self, reason: str):
        self._incomplete_reasons.append(reason)
        self.event("coverage.incomplete", {"reason": reason})

    @contextmanager
    def activate(self):
        if current_evidence() is not None:
            raise RuntimeError("nested evidence runs are not allowed")
        token = _CURRENT.set(self)
        parent = _PARENT.set(None)
        try:
            yield self
        finally:
            _PARENT.reset(parent)
            _CURRENT.reset(token)

    def seal(self, *, status="completed") -> dict:
        with self._lock:
            if self._closed:
                return json.loads((self.path / "seal.json").read_text())
            changed_sources = [name for name, ref in self._sources.items()
                               if not Path(name).is_file() or digest(Path(name).read_bytes()) != ref["sha256"]]
            incomplete = list(self._incomplete_reasons)
            if self._open_spans:
                incomplete.append("unclosed spans")
            if changed_sources:
                incomplete.append("source files changed during execution")
            self.event("run.finished", {"status": status, "unclosed_spans": sorted(self._open_spans),
                                        "incomplete_reasons": incomplete, "changed_sources": changed_sources})
            seal = {"schema_version": 1, "run_id": self.run_id, "status": status,
                    "event_count": self._sequence, "last_event_hash": self._previous,
                    "events_sha256": _file_digest(self.events_path)[0],
                    "blobs": dict(sorted(self._blobs.items())),
                    "coverage_complete_for_instrumented_boundaries": not incomplete,
                    "incomplete_reasons": incomplete,
                    "provider_authenticated": False, "scientific_truth_verified": False,
                    "external_anchor": None}
            seal["root_sha256"] = digest(canonical(seal))
            _write(self.path / "seal.json", canonical(seal)+b"\n")
            self._closed = True
            return seal


class _Span:
    def __init__(self):
        self.output = None
        self.span_id = None
        self.begin_event_hash = None
        self.end_event_hash = None

    def result(self, value):
        self.output = value
        return value


@contextmanager
def evidence_span(kind: str, inputs, *, actor="amy.runtime"):
    run = current_evidence()
    span = _Span()
    if run is None:
        yield span
        return
    span.span_id = uuid.uuid4().hex
    parent_id = _PARENT.get()
    span.begin_event_hash = run.event(kind+".begin", {"input": inputs}, actor=actor,
                                     span_id=span.span_id, parent_id=parent_id)
    with run._lock:
        run._open_spans.add(span.span_id)
    token = _PARENT.set(span.span_id)
    try:
        yield span
    except BaseException as exc:
        span.end_event_hash = run.event(kind+".end", {"status": "error", "error_type": type(exc).__name__,
                                                    "error": str(exc), "output": span.output}, actor=actor,
                                       span_id=span.span_id, parent_id=parent_id)
        raise
    else:
        span.end_event_hash = run.event(kind+".end", {"status": "returned", "output": span.output},
                                       actor=actor, span_id=span.span_id, parent_id=parent_id)
    finally:
        with run._lock:
            run._open_spans.discard(span.span_id)
        _PARENT.reset(token)


def record_event(kind: str, payload, *, actor="amy.runtime"):
    run = current_evidence()
    return run.event(kind, payload, actor=actor) if run is not None else None


def record_bytes(label: str, data: bytes, media_type="application/octet-stream"):
    run = current_evidence()
    return run.blob(label, data, media_type) if run is not None else None


def verify_run(directory: str | Path, *, expected_root: str | None = None) -> dict:
    """Recompute links, retained references, span closure and seal consistency.

    The local seal is not an authenticated identity. An independently retained
    ``expected_root`` detects wholesale replacement of an otherwise valid run.
    Source files are checked from their retained bytes, not today's filesystem.
    """
    errors = []
    event_count = 0
    actual_root = None

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    def hash_string(value):
        return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None

    def string_list(value):
        return isinstance(value, list) and all(isinstance(item, str) and item for item in value)

    def strict_json(data):
        def pairs(items):
            result = {}
            for key, value in items:
                require(key not in result, "duplicate JSON key")
                result[key] = value
            return result

        def constant(value):
            raise ValueError(f"non-finite JSON value: {value}")

        return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)

    try:
        path = Path(directory).resolve()
        if expected_root is not None:
            require(hash_string(expected_root), "invalid independently retained root")
        seal = strict_json((path / "seal.json").read_bytes())
        require(isinstance(seal, dict), "seal must be an object")
        actual_root = seal.pop("root_sha256")
        require(hash_string(actual_root), "invalid seal root")
        if digest(canonical(seal)) != actual_root:
            errors.append("seal digest mismatch")
        if expected_root is not None and actual_root != expected_root:
            errors.append("independently retained root mismatch")
        require(type(seal["schema_version"]) is int and seal["schema_version"] == 1,
                "unsupported seal schema")
        require(isinstance(seal["run_id"], str) and bool(seal["run_id"]), "invalid run id")
        require(isinstance(seal["status"], str) and bool(seal["status"]), "invalid run status")
        require(type(seal["event_count"]) is int and seal["event_count"] >= 2, "invalid event count")
        require(hash_string(seal["events_sha256"]) and hash_string(seal["last_event_hash"]),
                "invalid event stream digest or tip")
        require(type(seal["coverage_complete_for_instrumented_boundaries"]) is bool,
                "coverage flag must be boolean")
        require(string_list(seal["incomplete_reasons"]), "invalid incomplete reasons")
        require(seal.get("provider_authenticated") is False
                and seal.get("scientific_truth_verified") is False,
                "unsupported authentication or scientific-truth assertion")
        if _file_digest(path / "events.jsonl")[0] != seal["events_sha256"]:
            errors.append("event stream digest mismatch")
        blobs = seal["blobs"]
        require(isinstance(blobs, dict), "blob manifest must be an object")
        require(not (path / "blobs").is_symlink(), "symlink blob directory is not allowed")
        for relative, ref in blobs.items():
            require(isinstance(relative, str)
                    and re.fullmatch(r"blobs/[0-9a-f]{64}\.bin", relative) is not None,
                    "unsafe blob path")
            require(isinstance(ref, dict) and set(ref) == {"sha256", "size_bytes"},
                    "invalid blob manifest entry")
            require(hash_string(ref["sha256"]) and relative == f"blobs/{ref['sha256']}.bin",
                    "blob path does not match content digest")
            require(type(ref["size_bytes"]) is int and ref["size_bytes"] >= 0,
                    "invalid blob size")
            blob_path = path / relative
            require(not blob_path.is_symlink(), "symlink blob is not allowed")
            actual_sha, actual_size = _file_digest(blob_path)
            if actual_sha != ref["sha256"] or actual_size != ref["size_bytes"]:
                errors.append(f"blob changed: {relative}")

        def bound_reference(ref):
            require(isinstance(ref, dict), "blob reference must be an object")
            relative = ref["path"]
            require(isinstance(relative, str) and hash_string(ref["sha256"])
                    and type(ref["size_bytes"]) is int and ref["size_bytes"] >= 0,
                    "invalid blob reference")
            require(blobs.get(relative) == {"sha256": ref["sha256"], "size_bytes": ref["size_bytes"]},
                    "unbound retained blob reference")
            return path / relative

        def nested_references(value, depth=0):
            require(depth <= 256, "payload nesting exceeds supported depth")
            if isinstance(value, dict):
                # Scientific file paths and ordinary strings are not receipts.
                if {"path", "sha256", "size_bytes"} <= value.keys():
                    bound_reference(value)
                for item in value.values():
                    nested_references(item, depth + 1)
            elif isinstance(value, list):
                for item in value:
                    nested_references(item, depth + 1)

        def event_rows():
            with (path / "events.jsonl").open("rb") as handle:
                for line in handle:
                    yield strict_json(line)

        events = event_rows()
        previous = ""
        open_spans, seen_spans = {}, set()
        started_payload = finished_payload = None
        checkpoint_state = None
        starts = finishes = 0
        coverage_failures = []
        for seq, event in enumerate(events, 1):
            event_count = seq
            require(isinstance(event, dict), "event must be an object")
            claimed = event.pop("event_hash")
            require(hash_string(claimed), "invalid event digest")
            if digest(canonical(event)) != claimed:
                errors.append(f"event digest mismatch: {seq}")
            require(type(event["schema_version"]) is int and event["schema_version"] == 1,
                    "unsupported event schema")
            require(type(event["sequence"]) is int, "event sequence must be integer")
            if event["sequence"] != seq or event["previous_hash"] != previous or event["run_id"] != seal["run_id"]:
                errors.append(f"event identity/order mismatch: {seq}")
            require(isinstance(event["timestamp_utc"], str), "invalid event timestamp")
            timestamp = datetime.fromisoformat(event["timestamp_utc"])
            require(timestamp.utcoffset() is not None and timestamp.utcoffset().total_seconds() == 0,
                    "event timestamp must specify UTC")
            previous = claimed
            data = strict_json(bound_reference(event["payload"]).read_bytes())
            nested_references(data)
            if event["kind"] == "memory.checkpoint":
                from core.memory_checkpoint import reconstruct
                checkpoint_state = reconstruct(checkpoint_state, data)
                nested_references(checkpoint_state)
            sid, parent, kind, actor = event["span_id"], event["parent_id"], event["kind"], event["actor"]
            require(isinstance(kind, str) and _LABEL.fullmatch(kind) is not None,
                    "invalid event kind")
            require(isinstance(actor, str) and _LABEL.fullmatch(actor) is not None,
                    "invalid event actor")
            require(sid is None or (isinstance(sid, str) and bool(sid)), "invalid span id")
            require(parent is None or (isinstance(parent, str) and bool(parent)), "invalid parent id")
            if parent is not None and parent not in open_spans:
                errors.append(f"event parent absent: {seq}")
            if kind.endswith(".begin"):
                require(isinstance(data, dict) and "input" in data, "invalid span input payload")
                if not sid or sid in seen_spans:
                    errors.append(f"invalid span start: {seq}")
                open_spans[sid] = (kind[:-6], parent, actor)
                seen_spans.add(sid)
            elif kind.endswith(".end"):
                require(isinstance(data, dict) and data.get("status") in ("returned", "error")
                        and "output" in data, "invalid span output payload")
                if data["status"] == "error":
                    require(isinstance(data.get("error"), str)
                            and isinstance(data.get("error_type"), str) and bool(data["error_type"]),
                            "invalid error receipt")
                if any(value[1] == sid for value in open_spans.values()):
                    errors.append(f"span ended before its child: {seq}")
                if open_spans.pop(sid, None) != (kind[:-4], parent, actor):
                    errors.append(f"invalid span end: {seq}")
            if kind == "run.started":
                starts += 1
                started_payload = data
                require(seq == 1 and parent is None and sid is None, "invalid start boundary")
            elif kind == "run.finished":
                finishes += 1
                finished_payload = data
                require(seq == seal["event_count"] and parent is None and sid is None, "invalid finish boundary")
            elif kind == "coverage.incomplete":
                require(isinstance(data, dict) and isinstance(data.get("reason"), str)
                        and bool(data["reason"]), "invalid coverage failure")
                coverage_failures.append(data["reason"])
        require(starts == 1 and finishes == 1, "run boundary missing or duplicated")
        require(isinstance(started_payload, dict) and isinstance(started_payload["sources"], dict),
                "invalid retained source manifest")
        for name, ref in started_payload["sources"].items():
            require(isinstance(name, str) and bool(name), "invalid source name")
            bound_reference(ref)
        require(isinstance(started_payload["metadata"], dict), "invalid run metadata")
        assurance = started_payload["assurance"]
        require(isinstance(assurance, dict) and assurance.get("provider_authenticated") is False
                and assurance.get("scientific_truth_verified") is False, "unsupported start assurance")
        require(isinstance(finished_payload, dict), "invalid finish payload")
        for field in ("unclosed_spans", "incomplete_reasons", "changed_sources"):
            require(string_list(finished_payload[field]), f"invalid finished {field}")
        if (finished_payload["status"] != seal["status"]
                or finished_payload["incomplete_reasons"] != seal["incomplete_reasons"]):
            errors.append("finish payload disagrees with seal")
        if event_count != seal["event_count"] or previous != seal["last_event_hash"]:
            errors.append("sealed count/tip mismatch")
        if (open_spans or coverage_failures or seal["incomplete_reasons"]
                or any(finished_payload[field] for field in ("unclosed_spans", "incomplete_reasons", "changed_sources"))
                or not seal["coverage_complete_for_instrumented_boundaries"]):
            errors.append("instrumented execution incomplete")
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError, OverflowError) as exc:
        errors.append(f"malformed or missing evidence: {type(exc).__name__}: {exc}")
    return {"integrity_verified": not errors, "errors": errors, "event_count": event_count,
            "root_sha256": actual_root, "compared_with_external_root": expected_root is not None,
            "provider_authenticated": False, "scientific_truth_verified": False,
            "scope": "Recorded boundaries and retained bytes; no guarantee about uninstrumented code or physical truth"}
