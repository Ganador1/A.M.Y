#!/usr/bin/env python3
"""Verify that anti-abuse guardrails remain wired into critical paths."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_CONTROLS = [
    (
        "shared safety kernel",
        ROOT / "core" / "safety_kernel.py",
        ("SAFETY_RULES", "evaluate_safety", "fail_closed_decision"),
    ),
    (
        "A.M.Y Atlas bridge gate",
        ROOT / "core" / "atlas_tools.py",
        ("_evaluate_safety_or_fail_closed", "search_literature", "run_scientific_tool"),
    ),
    (
        "A.M.Y full Atlas research gate",
        ROOT / "core" / "atlas_bridge.py",
        ("_evaluate_research_safety_or_fail_closed", "atlas_bridge.misuse_blocked", "atlas_bridge.safety_blocked"),
    ),
    (
        "Atlas app/security misuse guard",
        ROOT / "atlas" / "app" / "security" / "misuse_guard.py",
        ("MISUSE_RULES", "MisuseGuard", "require_safe_operation", "format_blocked_message"),
    ),
    (
        "Atlas app/security risk policy integration",
        ROOT / "atlas" / "app" / "security" / "risk_policy.py",
        ("misuse_guard.evaluate", "assess_risk_sync", "PolicyAction.BLOCK"),
    ),
    (
        "A.M.Y persistent Atlas worker gate",
        ROOT / "core" / "atlas_worker.py",
        ("evaluate_safety", "Blocked by safety policy"),
    ),
    (
        "A.M.Y heartbeat side-effect gate",
        ROOT / "core" / "heartbeat.py",
        ("_safety_block_for_thought", "heartbeat.safety_blocked"),
    ),
    (
        "direct Atlas registry gate",
        ROOT / "atlas" / "app" / "run_agent_with_tools_legacy.py",
        ("_atlas_misuse_decision", "_core_safety_decision", "atlas_registry.execute_tool"),
    ),
    (
        "Atlas numeric tool literal parser",
        ROOT / "atlas" / "app" / "run_agent_with_tools_legacy.py",
        ("_parse_numeric_array_literal", "ast.literal_eval"),
    ),
    (
        "guardrail regression tests",
        ROOT / "tests" / "test_security_guardrails.py",
        (
            "test_direct_atlas_registry_blocks_dangerous_input",
            "test_sandbox_blocks_local_secret_file_reads",
            "Blocked by safety policy",
        ),
    ),
    (
        "sandbox execution gate",
        ROOT / "sandbox" / "executor.py",
        ("_safety_block", "_sandbox_env", "allow_network", "allow_sensitive_env"),
    ),
    (
        "Atlas misuse regression tests",
        ROOT / "tests" / "test_atlas_misuse_guard.py",
        ("test_autonomous_research_agent_blocks_misuse_before_tool_discovery", "test_risk_policy_blocks_misuse_context"),
    ),
    (
        "secret hygiene verifier",
        ROOT / "scripts" / "diagnostics" / "verify_secret_hygiene.py",
        ("scan_secret_hygiene", "SECRET HYGIENE CHECK", "ignored_by_policy"),
    ),
    (
        "root secret ignore policy",
        ROOT / ".gitignore",
        (".env", ".secrets.*", "**/secrets_*.json"),
    ),
    (
        "Atlas secret ignore policy",
        ROOT / "atlas" / ".gitignore",
        (".secrets.*", "**/secrets_*.json", "keys/"),
    ),
]


def main() -> int:
    failures: list[str] = []
    for name, path, markers in REQUIRED_CONTROLS:
        if not path.exists():
            failures.append(f"{name}: missing {path}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        missing = [marker for marker in markers if marker not in text]
        if missing:
            failures.append(f"{name}: missing markers {missing} in {path}")

    if failures:
        print("SECURITY CONTROL CHECK FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("SECURITY CONTROL CHECK PASSED")
    for name, path, _ in REQUIRED_CONTROLS:
        print(f"- {name}: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
