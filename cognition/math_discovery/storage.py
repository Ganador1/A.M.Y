"""Crash-conscious append-only storage for mathematical campaigns."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # POSIX advisory locks; AMY currently targets macOS/Linux.
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback remains thread-safe only.
    fcntl = None


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_SAFE_NAME = re.compile(r"[^A-Za-z0-9_.-]+")
_LOCKS: dict[str, threading.RLock] = {}
_LOCKS_GUARD = threading.Lock()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_id(value: str, label: str) -> str:
    if not isinstance(value, str) or _SAFE_ID.fullmatch(value) is None:
        raise ValueError(f"invalid {label}: {value!r}")
    return value


def _path_lock(path: Path) -> threading.RLock:
    key = str(path.resolve())
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(key, threading.RLock())


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise


class HashChainLog:
    """JSONL event stream whose records link to the preceding event hash."""

    def __init__(self, path: Path, chain_name: str, *, create: bool = False):
        self.path = path
        self.chain_name = _validate_id(chain_name, "chain name")
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch(exist_ok=True)
        if self.path.is_symlink() or not self.path.is_file():
            raise FileNotFoundError(f"missing campaign log or invalid log path: {self.path}")
        self._lock = _path_lock(path)

    def append(
        self,
        event_type: str,
        payload: dict[str, Any],
        *,
        actor: str,
    ) -> dict[str, Any]:
        _validate_id(event_type, "event type")
        _validate_id(actor, "actor")
        # Validate serializability before opening the append transaction.
        canonical_json_bytes(payload)
        with self._lock, self.path.open("a+b") as handle:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                handle.seek(0)
                raw_lines = handle.read().splitlines()
                records = [json.loads(line) for line in raw_lines if line.strip()]
                previous_hash = records[-1]["event_hash"] if records else ""
                event = {
                    "schema_version": "1.0",
                    "chain": self.chain_name,
                    "sequence": len(records) + 1,
                    "timestamp": _utc_now(),
                    "event_type": event_type,
                    "actor": actor,
                    "payload": payload,
                    "previous_event_hash": previous_hash,
                }
                event["event_hash"] = sha256_bytes(canonical_json_bytes(event))
                handle.seek(0, os.SEEK_END)
                handle.write(canonical_json_bytes(event) + b"\n")
                handle.flush()
                os.fsync(handle.fileno())
                return event
            finally:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def records(self) -> list[dict[str, Any]]:
        with self._lock:
            lines = self.path.read_bytes().splitlines()
        return [json.loads(line) for line in lines if line.strip()]

    def verify(self) -> dict[str, Any]:
        errors: list[str] = []
        try:
            records = self.records()
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            return {
                "integrity_verified": False,
                "event_count": 0,
                "errors": [f"unreadable chain: {type(exc).__name__}: {exc}"],
                "truth_verified": False,
            }
        previous_hash = ""
        for index, record in enumerate(records, 1):
            observed_hash = record.get("event_hash")
            unhashed = dict(record)
            unhashed.pop("event_hash", None)
            expected_hash = sha256_bytes(canonical_json_bytes(unhashed))
            if record.get("sequence") != index:
                errors.append(f"record {index}: invalid sequence")
            if record.get("chain") != self.chain_name:
                errors.append(f"record {index}: wrong chain")
            if record.get("previous_event_hash") != previous_hash:
                errors.append(f"record {index}: broken previous hash")
            if observed_hash != expected_hash:
                errors.append(f"record {index}: invalid event hash")
            previous_hash = str(observed_hash or "")
        return {
            "integrity_verified": not errors,
            "event_count": len(records),
            "head_hash": previous_hash,
            "errors": errors,
            # Cryptographic integrity is deliberately not mathematical truth.
            "truth_verified": False,
        }


class ArtifactStore:
    def __init__(self, campaign_dir: Path):
        self.campaign_dir = campaign_dir.resolve()
        self.root = self.campaign_dir / "artifacts"
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, name: str, content: bytes, media_type: str) -> dict[str, Any]:
        if not isinstance(content, bytes):
            raise TypeError("artifact content must be bytes")
        safe_name = _SAFE_NAME.sub("_", Path(name).name).strip("._") or "artifact.bin"
        digest = sha256_bytes(content)
        relative = Path("artifacts") / digest / safe_name
        destination = self.campaign_dir / relative
        if destination.exists():
            if destination.read_bytes() != content:
                raise RuntimeError("artifact hash collision or corrupted existing artifact")
        else:
            atomic_write(destination, content)
        return {
            "name": safe_name,
            "path": relative.as_posix(),
            "sha256": digest,
            "size_bytes": len(content),
            "media_type": media_type,
        }

    def verify(self, record: dict[str, Any]) -> tuple[bool, str | None]:
        try:
            candidate = (self.campaign_dir / str(record["path"])).resolve()
            candidate.relative_to(self.campaign_dir)
            content = candidate.read_bytes()
        except (KeyError, OSError, ValueError) as exc:
            return False, f"artifact unavailable: {type(exc).__name__}: {exc}"
        if len(content) != record.get("size_bytes"):
            return False, "artifact size mismatch"
        if sha256_bytes(content) != record.get("sha256"):
            return False, "artifact hash mismatch"
        return True, None

    def read_by_hash(self, digest: str) -> bytes:
        if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError("artifact digest must be a lowercase SHA-256")
        directory = self.root / digest
        if not directory.is_dir():
            raise FileNotFoundError(f"artifact not found: {digest}")
        files = sorted(path for path in directory.iterdir() if path.is_file())
        if not files:
            raise FileNotFoundError(f"artifact bytes missing: {digest}")
        content = files[0].read_bytes()
        if sha256_bytes(content) != digest:
            raise OSError(f"artifact hash mismatch: {digest}")
        return content


class CampaignStore:
    """Filesystem layout and logs for one immutable-identity campaign."""

    def __init__(self, root: Path | str, campaign_id: str):
        self.root = Path(root).resolve()
        self.campaign_id = _validate_id(campaign_id, "campaign_id")
        self.path = self.root / self.campaign_id
        if not self.path.is_dir():
            raise FileNotFoundError(f"campaign does not exist: {self.campaign_id}")
        self.ledger_log = HashChainLog(self.path / "ledger.jsonl", "claim_ledger")
        self.event_log = HashChainLog(self.path / "events.jsonl", "campaign_events")
        self.artifacts = ArtifactStore(self.path)

    @classmethod
    def create(
        cls,
        root: Path | str,
        campaign_id: str,
        *,
        problem: str,
        protocol: dict[str, Any],
    ) -> "CampaignStore":
        campaign_id = _validate_id(campaign_id, "campaign_id")
        if not problem.strip():
            raise ValueError("problem cannot be empty")
        canonical_json_bytes(protocol)
        root_path = Path(root).resolve()
        root_path.mkdir(parents=True, exist_ok=True)
        campaign_dir = root_path / campaign_id
        if campaign_dir.exists():
            raise FileExistsError(f"campaign already exists: {campaign_id}")
        temporary_dir = Path(
            tempfile.mkdtemp(dir=root_path, prefix=f".{campaign_id}.creating-")
        )
        try:
            for name in (
                "jobs",
                "attempts",
                "claims",
                "reviews",
                "literature",
                "computations",
                "formal",
                "artifacts",
                "release",
            ):
                (temporary_dir / name).mkdir()
            problem_bytes = problem.encode("utf-8")
            protocol_bytes = (
                json.dumps(protocol, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
                + b"\n"
            )
            manifest = {
                "schema_version": "1.0",
                "campaign_id": campaign_id,
                "created_at": _utc_now(),
                "problem_sha256": sha256_bytes(problem_bytes),
                "protocol_sha256": sha256_bytes(protocol_bytes),
                "truth_verified": False,
                "manifest_hash_scope": "manifest fields except manifest_sha256",
            }
            manifest["manifest_sha256"] = sha256_bytes(canonical_json_bytes(manifest))
            atomic_write(
                temporary_dir / "manifest.json",
                json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n",
            )
            atomic_write(temporary_dir / "problem.md", problem_bytes)
            atomic_write(temporary_dir / "protocol.json", protocol_bytes)
            # Only creation initializes empty logs; opening must never hide deletion.
            atomic_write(temporary_dir / "events.jsonl", b"")
            atomic_write(temporary_dir / "ledger.jsonl", b"")
            os.replace(temporary_dir, campaign_dir)
        except BaseException:
            shutil.rmtree(temporary_dir, ignore_errors=True)
            raise
        return cls(root, campaign_id)

    def verify_manifest(self) -> dict[str, Any]:
        errors: list[str] = []
        try:
            manifest = json.loads((self.path / "manifest.json").read_text(encoding="utf-8"))
            problem_bytes = (self.path / "problem.md").read_bytes()
            protocol_bytes = (self.path / "protocol.json").read_bytes()
            observed_manifest_hash = manifest.pop("manifest_sha256", None)
            expected_manifest_hash = sha256_bytes(canonical_json_bytes(manifest))
            if observed_manifest_hash != expected_manifest_hash:
                errors.append("manifest hash mismatch")
            if manifest.get("campaign_id") != self.campaign_id:
                errors.append("manifest campaign_id mismatch")
            if manifest.get("problem_sha256") != sha256_bytes(problem_bytes):
                errors.append("problem hash mismatch")
            if manifest.get("protocol_sha256") != sha256_bytes(protocol_bytes):
                errors.append("protocol hash mismatch")
            if manifest.get("truth_verified") is not False:
                errors.append("campaign manifest must not assert mathematical truth")
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
            errors.append(f"unreadable manifest: {type(exc).__name__}: {exc}")
        return {
            "integrity_verified": not errors,
            "errors": errors,
            "truth_verified": False,
        }
