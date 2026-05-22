#!/usr/bin/env python3
"""Check that local secret-like files are covered by ignore policy.

This verifier reports paths only. It deliberately never prints secret values.
Use ``--strict`` before publishing an artifact if you want the presence of any
local secret file to fail the release check.
"""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
import argparse
import sys


ROOT = Path(__file__).parent.resolve()

SENSITIVE_FILE_PATTERNS = (
    ".env",
    ".env.*",
    ".secrets.*",
    "*.key",
    "*.pem",
    "secrets_*.json",
    "*.secret.json",
)

SAFE_EXAMPLE_PATTERNS = (
    ".env.example",
    ".env.template",
    "**/.env.example",
    "**/.env.template",
    "**/config/.env.example",
)

IGNORE_POLICY_PATTERNS = (
    ".env",
    ".env.*",
    "!.env.example",
    "!.env.template",
    ".secrets.*",
    "*.key",
    "*.pem",
    "**/secrets_*.json",
    "**/*.secret.json",
)

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    ".venv_new",
    "__pycache__",
    "external_tools",
    "node_modules",
    "test_env",
    "venv-new",
    "venv_improvements",
}


@dataclass(frozen=True)
class SecretFinding:
    path: Path
    reason: str
    ignored_by_policy: bool


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _matches_any(path: Path, patterns: tuple[str, ...]) -> bool:
    rel = _rel(path)
    name = path.name
    return any(fnmatch(rel, pattern) or fnmatch(name, pattern) for pattern in patterns)


def _covered_by_ignore_policy(path: Path) -> bool:
    if _matches_any(path, SAFE_EXAMPLE_PATTERNS):
        return True
    return _matches_any(path, IGNORE_POLICY_PATTERNS)


def iter_candidate_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.is_symlink():
            continue
        if not path.is_file():
            continue
        if _matches_any(path, SAFE_EXAMPLE_PATTERNS):
            continue
        if _matches_any(path, SENSITIVE_FILE_PATTERNS):
            yield path


def scan_secret_hygiene(root: Path = ROOT) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    for path in iter_candidate_files(root):
        findings.append(
            SecretFinding(
                path=path,
                reason="secret-like filename",
                ignored_by_policy=_covered_by_ignore_policy(path),
            )
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail if any local secret-like file exists, even when ignored",
    )
    args = parser.parse_args()

    findings = scan_secret_hygiene(ROOT)
    unignored = [finding for finding in findings if not finding.ignored_by_policy]

    if not findings:
        print("SECRET HYGIENE CHECK PASSED: no local secret-like files found")
        return 0

    print("SECRET HYGIENE CHECK FOUND LOCAL SECRET-LIKE FILES")
    for finding in findings:
        status = "ignored" if finding.ignored_by_policy else "NOT_IGNORED"
        print(f"- {status}: {_rel(finding.path)} ({finding.reason})")

    if unignored:
        print("SECRET HYGIENE CHECK FAILED: at least one secret-like file is not covered by ignore policy")
        return 1

    if args.strict:
        print("SECRET HYGIENE CHECK FAILED: strict mode disallows local secret-like files")
        return 1

    print("SECRET HYGIENE CHECK PASSED: all local secret-like files are covered by ignore policy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
