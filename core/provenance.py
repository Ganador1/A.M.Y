"""
Provenance Manager — Real provenance tracking for A.M.Y tool executions.

Every tool execution now writes a real provenance.json with:
- Full input/output
- Tool name, version, timestamp
- Environment info (Python, OS, hardware)
- SHA-256 hash of the output
- Execution duration

Papers cite these real provenance files, not synthetic IDs.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import platform
import re
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

PROVENANCE_DIR = Path("data/experiments")
JOURNAL_FILENAME = "provenance_journal.jsonl"
_JOURNAL_LOCKS: dict[str, threading.RLock] = {}
_JOURNAL_LOCKS_GUARD = threading.Lock()


def _sha256_hash(text: str) -> str:
    """Compute SHA-256 hash of text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically for local integrity checking.

    This is an internal canonical form, not a signature format and not an
    interoperability claim such as RFC 8785.
    """
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")


def _record_integrity_hash(record: dict) -> str:
    """Hash every retained record field except the hash value itself."""
    payload = dict(record)
    integrity = dict(payload.get("integrity", {}))
    integrity.pop("record_hash", None)
    payload["integrity"] = integrity
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def _fsync_directory(directory: Path) -> None:
    """Best-effort directory fsync after an atomic rename."""
    try:
        descriptor = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        # Some filesystems/platforms do not support fsync on directories.
        pass
    finally:
        os.close(descriptor)


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    """Commit one file atomically within its destination directory."""
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        handle = os.fdopen(descriptor, "wb")
    except BaseException:
        os.close(descriptor)
        temporary_path.unlink(missing_ok=True)
        raise
    try:
        with handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        _fsync_directory(path.parent)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def _get_environment() -> dict:
    """Capture execution environment info."""
    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
    }


def _get_journal_lock(journal_path: Path) -> threading.RLock:
    key = str(journal_path.resolve())
    with _JOURNAL_LOCKS_GUARD:
        return _JOURNAL_LOCKS.setdefault(key, threading.RLock())


class ProvenanceManager:
    """Tracks real provenance for every tool execution."""

    def __init__(self, base_dir: Path | str | None = None):
        self.base_dir = Path(base_dir) if base_dir else PROVENANCE_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.journal_path = self.base_dir / JOURNAL_FILENAME

    def record_execution(
        self,
        tool_name: str,
        tool_input: str,
        tool_output: str,
        success: bool,
        duration_seconds: float,
        domain: str = "unknown",
        experiment_id: str | None = None,
        extra: dict | None = None,
    ) -> dict:
        """
        Record a tool execution with full provenance and continuous hash-chaining.

        Returns the provenance record dict (also saved to disk).
        """
        # Generate experiment ID if not provided.
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        if experiment_id is None:
            experiment_id = f"{domain}_{tool_name}_{timestamp}"

        # Validate before any filesystem lookup.
        from core.security_hardening_v2 import require_valid_experiment_id
        experiment_id = require_valid_experiment_id(experiment_id)
        experiment_id, exp_dir = self._reserve_experiment_directory(experiment_id)

        output_bytes = tool_output.encode("utf-8")
        output_sha256 = hashlib.sha256(output_bytes).hexdigest()
        thread_lock = _get_journal_lock(self.journal_path)

        with thread_lock:
            self.journal_path.touch(exist_ok=True)
            with self.journal_path.open("a+b") as journal_handle:
                if fcntl is not None:
                    fcntl.flock(journal_handle.fileno(), fcntl.LOCK_EX)
                try:
                    journal_handle.seek(0)
                    raw_lines = journal_handle.read().splitlines()
                    journal_entries = [json.loads(line) for line in raw_lines if line.strip()]
                    prev_record_hash = (
                        journal_entries[-1]["record_hash"] if journal_entries else ""
                    )
                    sequence = len(journal_entries) + 1

                    # Build provenance record
                    record = {
                        "experiment_id": experiment_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "tool": {
                            "name": tool_name,
                            "input": tool_input,
                            "output_hash": output_sha256,
                            "output_length": len(tool_output),
                            "output_size_bytes": len(output_bytes),
                            "success": success,
                            "duration_seconds": round(duration_seconds, 3),
                        },
                        "output_preview": tool_output[:2000] if success else f"ERROR: {tool_output[:500]}",
                        "domain": domain,
                        "environment": _get_environment(),
                        "provenance_version": "2.0",
                        "integrity": {
                            "algorithm": "sha256",
                            "scope": (
                                "all provenance record fields except integrity.record_hash, "
                                "plus retained output bytes via tool.output_hash"
                            ),
                            "prev_record_hash": prev_record_hash,
                            "journal_sequence": sequence,
                            "authenticated": False,
                            "rollback_protected": False,
                            "truth_verified": False,
                        },
                    }

                    if extra:
                        record["extra"] = extra

                    record_hash = _record_integrity_hash(record)
                    record["integrity"]["record_hash"] = record_hash

                    prov_path = exp_dir / "provenance.json"
                    output_path = exp_dir / "output.txt"
                    provenance_bytes = json.dumps(
                        record,
                        indent=2,
                        ensure_ascii=False,
                        default=str,
                    ).encode("utf-8")

                    try:
                        _atomic_write_bytes(output_path, output_bytes)
                        _atomic_write_bytes(prov_path, provenance_bytes)
                    except BaseException:
                        prov_path.unlink(missing_ok=True)
                        output_path.unlink(missing_ok=True)
                        try:
                            exp_dir.rmdir()
                        except OSError:
                            pass
                        raise

                    # Append to journal log
                    journal_entry = {
                        "sequence": sequence,
                        "experiment_id": experiment_id,
                        "timestamp": record["timestamp"],
                        "record_hash": record_hash,
                        "prev_record_hash": prev_record_hash,
                        "tool_output_hash": output_sha256,
                    }
                    journal_handle.seek(0, os.SEEK_END)
                    journal_handle.write(_canonical_json_bytes(journal_entry) + b"\n")
                    journal_handle.flush()
                    os.fsync(journal_handle.fileno())

                finally:
                    if fcntl is not None:
                        fcntl.flock(journal_handle.fileno(), fcntl.LOCK_UN)

        return record

    def _reserve_experiment_directory(self, experiment_id: str) -> tuple[str, Path]:
        """Atomically reserve a unique ID across threads and processes."""
        candidate = experiment_id
        counter = 2
        while True:
            candidate_dir = self.base_dir / candidate
            try:
                candidate_dir.mkdir(parents=False, exist_ok=False)
                return candidate, candidate_dir
            except FileExistsError:
                candidate = f"{experiment_id}_{counter}"
                counter += 1

    def verify_experiment_id(self, experiment_id: str) -> dict:
        """
        Verify that an experiment_id has a real provenance file.

        Returns dict with 'exists', 'path', and 'record' (if exists).
        """
        from core.security_hardening_v2 import validate_experiment_id
        if not isinstance(experiment_id, str) or not validate_experiment_id(experiment_id):
            return {
                "exists": False,
                "path": None,
                "record": None,
                "integrity_verified": False,
                "authenticated": False,
                "rollback_protected": False,
                "truth_verified": False,
            }

        exp_dir = self.base_dir / experiment_id
        prov_path = exp_dir / "provenance.json"
        output_path = exp_dir / "output.txt"
        if prov_path.exists():
            try:
                if exp_dir.is_symlink() or prov_path.is_symlink() or output_path.is_symlink():
                    raise OSError("symlinked provenance path")
                record = json.loads(prov_path.read_text(encoding="utf-8"))
                output_raw = output_path.read_bytes()
                output_text = output_raw.decode("utf-8")
                integrity = record.get("integrity", {})
                expected_hash = record.get("tool", {}).get("output_hash")
                observed_hash = hashlib.sha256(output_raw).hexdigest()
                expected_record_hash = integrity.get("record_hash")
                observed_record_hash = _record_integrity_hash(record)
                version = record.get("provenance_version")

                integrity_verified = (
                    record.get("experiment_id") == experiment_id
                    and version in ("1.1", "2.0")
                    and integrity.get("algorithm") == "sha256"
                    and integrity.get("authenticated") is False
                    and integrity.get("rollback_protected") is False
                    and integrity.get("truth_verified") is False
                    and isinstance(expected_hash, str)
                    and hmac.compare_digest(expected_hash, observed_hash)
                    and record.get("tool", {}).get("output_length") == len(output_text)
                    and record.get("tool", {}).get("output_size_bytes") == len(output_raw)
                    and isinstance(expected_record_hash, str)
                    and hmac.compare_digest(expected_record_hash, observed_record_hash)
                )
                return {
                    "exists": True,
                    "path": str(prov_path),
                    "record": record,
                    "integrity_verified": integrity_verified,
                    "authenticated": False,
                    "rollback_protected": False,
                    "truth_verified": False,
                }
            except (
                AttributeError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                OSError,
                TypeError,
                ValueError,
            ):
                return {
                    "exists": True,
                    "path": str(prov_path),
                    "record": None,
                    "integrity_verified": False,
                    "authenticated": False,
                    "rollback_protected": False,
                    "truth_verified": False,
                }
        return {
            "exists": False,
            "path": str(prov_path),
            "record": None,
            "integrity_verified": False,
            "authenticated": False,
            "rollback_protected": False,
            "truth_verified": False,
        }

    def verify_journal(self) -> dict[str, Any]:
        """
        Verify the complete chronological journal hash chain and cross-check records.
        """
        if not self.journal_path.exists():
            return {
                "integrity_verified": False,
                "total_records": 0,
                "head_hash": "",
                "errors": ["missing journal; an absent history is not a verified empty history"],
                "truth_verified": False,
            }

        thread_lock = _get_journal_lock(self.journal_path)
        with thread_lock:
            try:
                lines = self.journal_path.read_bytes().splitlines()
                entries = [json.loads(line) for line in lines if line.strip()]
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                return {
                    "integrity_verified": False,
                    "total_records": 0,
                    "head_hash": "",
                    "errors": [f"unreadable journal: {type(exc).__name__}: {exc}"],
                    "truth_verified": False,
                }

        errors: list[str] = []
        previous_hash = ""
        seen_experiments: set[str] = set()
        for index, entry in enumerate(entries, 1):
            if not isinstance(entry, dict):
                errors.append(f"entry {index}: journal entry must be an object")
                continue
            if type(entry.get("sequence")) is not int or entry.get("sequence") != index:
                errors.append(f"entry {index}: sequence number mismatch")
            if entry.get("prev_record_hash") != previous_hash:
                errors.append(f"entry {index}: broken previous record hash link")
            for field in ("record_hash", "tool_output_hash"):
                value = entry.get(field)
                if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
                    errors.append(f"entry {index}: invalid {field}")
            exp_id = entry.get("experiment_id")
            if not isinstance(exp_id, str) or not exp_id:
                errors.append(f"entry {index}: experiment_id is required")
            else:
                if exp_id in seen_experiments:
                    errors.append(f"entry {index}: duplicate experiment_id {exp_id}")
                seen_experiments.add(exp_id)
                exp_res = self.verify_experiment_id(exp_id)
                if not exp_res["integrity_verified"]:
                    errors.append(f"entry {index} ({exp_id}): experiment verification failed")
                else:
                    record = exp_res["record"]
                    binding = {
                        "record_hash": record["integrity"].get("record_hash"),
                        "prev_record_hash": record["integrity"].get("prev_record_hash"),
                        "sequence": record["integrity"].get("journal_sequence"),
                        "timestamp": record.get("timestamp"),
                        "tool_output_hash": record["tool"].get("output_hash"),
                    }
                    for field, value in binding.items():
                        if value is None or entry.get(field) != value:
                            errors.append(f"entry {index} ({exp_id}): {field} mismatch with record")
                    if type(binding["sequence"]) is not int:
                        errors.append(f"entry {index} ({exp_id}): invalid record journal sequence")

            previous_hash = str(entry.get("record_hash") or "")

        return {
            "integrity_verified": len(errors) == 0,
            "total_records": len(entries),
            "head_hash": previous_hash,
            "errors": errors,
            "truth_verified": False,
        }

    def verify_all(self, experiment_ids: list[str]) -> list[dict]:
        """Verify a list of experiment IDs. Returns list of verification results."""
        return [self.verify_experiment_id(eid) for eid in experiment_ids]

    def get_provenance_path(self, experiment_id: str) -> str:
        """Return the expected provenance path for an experiment ID."""
        from core.security_hardening_v2 import require_valid_experiment_id
        experiment_id = require_valid_experiment_id(experiment_id)
        return str(self.base_dir / experiment_id / "provenance.json")

    def list_experiments(self) -> list[dict]:
        """List all experiments with provenance."""
        experiments = []
        if not self.base_dir.exists():
            return experiments
        for exp_dir in sorted(self.base_dir.iterdir()):
            if exp_dir.is_dir() and not exp_dir.name.startswith("."):
                prov_path = exp_dir / "provenance.json"
                if prov_path.exists():
                    try:
                        record = json.loads(prov_path.read_text(encoding="utf-8"))
                        experiments.append({
                            "experiment_id": exp_dir.name,
                            "tool": record.get("tool", {}).get("name", "unknown"),
                            "domain": record.get("domain", "unknown"),
                            "timestamp": record.get("timestamp", "unknown"),
                            "success": record.get("tool", {}).get("success", False),
                        })
                    except (json.JSONDecodeError, OSError):
                        experiments.append({
                            "experiment_id": exp_dir.name,
                            "tool": "unknown",
                            "domain": "unknown",
                            "timestamp": "unknown",
                            "success": False,
                        })
        return experiments


# Global instance
_provenance = ProvenanceManager()


def get_provenance_manager() -> ProvenanceManager:
    """Get the global provenance manager instance."""
    return _provenance
