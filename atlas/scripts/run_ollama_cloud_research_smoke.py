#!/usr/bin/env python3
"""Run a lightweight end-to-end Atlas research smoke on Ollama Cloud."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.orchestration.management.multi_agent_coordinator import MultiAgentCoordinator


DEFAULT_GOAL = (
    "Investigate whether a symmetry-preserving variational ansatz reduces energy "
    "estimation error for a 2-qubit Heisenberg Hamiltonian under depolarizing noise."
)


def _to_abs(path_value: str | None) -> str | None:
    if not path_value:
        return None
    return os.path.abspath(path_value)


def _count_tiers(tool_calls: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in tool_calls:
        tier = str(item.get("evidence_tier") or "unknown")
        counts[tier] = counts.get(tier, 0) + 1
    return counts


async def _run(goal: str, domain: str, compile_latex: bool) -> dict[str, Any]:
    coordinator = MultiAgentCoordinator(use_huggingface=False)
    result = await coordinator.run_pipeline_integrated_async(
        research_goal=goal,
        domain=domain,
        compile_latex=compile_latex,
    )
    artifact = result.get("artifact") or {}
    evidence_summary = ((artifact.get("evidence") or {}).get("summary") or {})
    paper_paths = artifact.get("paper_paths") or {}
    tool_calls = ((artifact.get("evidence") or {}).get("tool_calls") or [])
    real_tool_calls = [
        tc for tc in tool_calls
        if tc.get("counts_as_real_evidence") and tc.get("success")
    ]
    publication_claim_audit = artifact.get("publication_claim_audit") or {}

    return {
        "success": result.get("success", False),
        "error": result.get("error"),
        "research_goal": goal,
        "domain": domain,
        "session_id": artifact.get("session_id"),
        "hypothesis_id": artifact.get("scientific_agent_hypothesis_id"),
        "support_score": evidence_summary.get("support_score"),
        "nominal_support_score": evidence_summary.get("nominal_support_score"),
        "coverage": evidence_summary.get("coverage"),
        "weighted_coverage": evidence_summary.get("weighted_coverage"),
        "real_coverage": evidence_summary.get("real_coverage"),
        "real_weighted_coverage": evidence_summary.get("real_weighted_coverage"),
        "diversity": evidence_summary.get("diversity"),
        "tool_realism_score": evidence_summary.get("tool_realism_score"),
        "tool_call_count": len(tool_calls),
        "real_tool_count": len(real_tool_calls),
        "unsupported_quant_claim_count": publication_claim_audit.get("suspect_sentence_count"),
        "tier_counts": evidence_summary.get("tier_counts") or _count_tiers(tool_calls),
        "tool_realism_breakdown": [
            {
                "source": tc.get("source"),
                "operation": tc.get("operation"),
                "success": tc.get("success"),
                "evidence_tier": tc.get("evidence_tier"),
                "counts_as_real_evidence": tc.get("counts_as_real_evidence"),
                "classification_reason": tc.get("classification_reason"),
            }
            for tc in tool_calls
        ],
        "paper_paths": {
            "markdown": _to_abs(paper_paths.get("markdown")),
            "latex": _to_abs(paper_paths.get("latex")),
        },
        "publication_preview": (artifact.get("publication") or "")[:1200],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goal", default=DEFAULT_GOAL, help="Research goal for the smoke run.")
    parser.add_argument("--domain", default="quantum_computing", help="Atlas domain to use.")
    parser.add_argument(
        "--compile-latex",
        action="store_true",
        help="Attempt to compile the LaTeX paper output.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the JSON summary.",
    )
    args = parser.parse_args()

    summary = asyncio.run(_run(args.goal, args.domain, args.compile_latex))
    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    print(payload)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")

    return 0 if summary.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
