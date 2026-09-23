"""
RFC 3161 Timestamping and External Temporal Anchors.

Enables verifiable proof-of-existence in time (independent of GitHub and Zenodo)
via standard Timestamping Authorities (TSA) and in-toto anchors[] format.
"""
from __future__ import annotations

import base64
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any
import urllib.request
import urllib.error

DEFAULT_TSA_URL = "https://freetsa.org/tsr"
DEFAULT_FALLBACK_TSA_URL = "http://timestamp.digicert.com"


class TimestampError(Exception):
    """Raised when timestamp query generation, fetching, or verification fails."""
    pass


def _find_openssl() -> str:
    candidate = shutil.which("openssl")
    if candidate:
        return candidate
    for path in ["/opt/homebrew/bin/openssl", "/usr/local/bin/openssl", "/usr/bin/openssl"]:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    raise TimestampError("openssl binary not found; required for RFC 3161 operations")


def create_timestamp_query(target: Path | bytes | str) -> bytes:
    """Generate an RFC 3161 DER-encoded timestamp query (.tsq) for target data."""
    openssl = _find_openssl()
    if isinstance(target, Path):
        target_bytes = target.read_bytes()
    elif isinstance(target, str):
        target_bytes = target.encode("utf-8")
    elif isinstance(target, bytes):
        target_bytes = target
    else:
        raise TypeError(f"unsupported target type: {type(target).__name__}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        data_path = Path(tmp_dir) / "data.bin"
        tsq_path = Path(tmp_dir) / "request.tsq"
        data_path.write_bytes(target_bytes)

        cmd = [
            openssl,
            "ts",
            "-query",
            "-data",
            str(data_path),
            "-sha256",
            "-cert",
            "-out",
            str(tsq_path),
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise TimestampError(f"openssl ts -query failed: {result.stderr.decode('utf-8', errors='replace')}")
        return tsq_path.read_bytes()


def fetch_timestamp_token(
    tsq_bytes: bytes,
    tsa_url: str = DEFAULT_TSA_URL,
    timeout_seconds: float = 15.0,
) -> bytes:
    """Send timestamp query to TSA server and receive RFC 3161 token (.tsr)."""
    req = urllib.request.Request(
        tsa_url,
        data=tsq_bytes,
        headers={"Content-Type": "application/timestamp-query"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            if resp.status != 200:
                raise TimestampError(f"TSA server {tsa_url} returned HTTP {resp.status}")
            return resp.read()
    except urllib.error.URLError as exc:
        raise TimestampError(f"Failed to connect to TSA server {tsa_url}: {exc}") from exc


def verify_timestamp_token(
    target: Path | bytes | str,
    tsr_bytes: bytes,
    ca_file: Path | str | None = None,
    untrusted_file: Path | str | None = None,
) -> dict[str, Any]:
    """
    Verify an RFC 3161 timestamp response (.tsr) against data and certificates.
    """
    openssl = _find_openssl()
    if isinstance(target, Path):
        target_bytes = target.read_bytes()
    elif isinstance(target, str):
        target_bytes = target.encode("utf-8")
    elif isinstance(target, bytes):
        target_bytes = target
    else:
        raise TypeError(f"unsupported target type: {type(target).__name__}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        data_path = Path(tmp_dir) / "data.bin"
        tsr_path = Path(tmp_dir) / "response.tsr"
        token_path = Path(tmp_dir) / "token.der"
        data_path.write_bytes(target_bytes)
        tsr_path.write_bytes(tsr_bytes)

        # 1. Parse timestamp details and token text
        cmd_reply = [openssl, "ts", "-reply", "-in", str(tsr_path), "-text"]
        res_reply = subprocess.run(cmd_reply, capture_output=True)
        if res_reply.returncode != 0:
            return {
                "verified": False,
                "error": f"corrupt tsr token: {res_reply.stderr.decode('utf-8', errors='replace')}",
                "tsa_time": None,
            }

        reply_text = res_reply.stdout.decode("utf-8", errors="replace")

        # Extract token
        cmd_token = [openssl, "ts", "-reply", "-in", str(tsr_path), "-token_out", "-out", str(token_path)]
        res_token = subprocess.run(cmd_token, capture_output=True)
        if res_token.returncode != 0:
            return {
                "verified": False,
                "error": f"token extraction failed: {res_token.stderr.decode('utf-8', errors='replace')}",
                "tsa_time": None,
            }

        # 2. Verify cryptographically against data
        cmd_verify = [
            openssl,
            "ts",
            "-verify",
            "-data",
            str(data_path),
            "-in",
            str(token_path),
            "-token_in",
        ]
        if ca_file:
            cmd_verify.extend(["-CAfile", str(ca_file)])
        if untrusted_file:
            cmd_verify.extend(["-untrusted", str(untrusted_file)])

        res_verify = subprocess.run(cmd_verify, capture_output=True)
        verify_output = res_verify.stdout.decode("utf-8", errors="replace") + res_verify.stderr.decode("utf-8", errors="replace")
        is_ok = res_verify.returncode == 0

        # Extract time and policy OID if available
        tsa_time = None
        policy_oid = None
        for line in reply_text.splitlines():
            line_str = line.strip()
            if "Time stamp:" in line_str:
                tsa_time = line_str.split("Time stamp:", 1)[1].strip()
            elif "Policy OID:" in line_str:
                policy_oid = line_str.split("Policy OID:", 1)[1].strip()

        return {
            "verified": is_ok,
            "tsa_time": tsa_time,
            "policy_oid": policy_oid,
            "raw_output": verify_output.strip(),
            "error": None if is_ok else verify_output.strip(),
        }


def format_in_toto_anchor(
    tsr_bytes: bytes,
    canonical_root_sha256: str,
    anchor_type: str = "rfc3161",
) -> dict[str, Any]:
    """Format external temporal proof as an in-toto / DSSE anchor record."""
    return {
        "type": anchor_type,
        "canonical_root": canonical_root_sha256.lower().strip(),
        "proof": base64.b64encode(tsr_bytes).decode("ascii"),
    }
