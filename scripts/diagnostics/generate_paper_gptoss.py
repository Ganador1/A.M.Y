#!/usr/bin/env python3
"""Generate one full A.M.Y paper with gpt-oss:120b from REAL evidence.

This drives the same PaperGenerator A.M.Y uses, but in a single deterministic
pass (instead of relying on the multi-cycle heartbeat to eventually choose
write_paper). It:

  1. computes real prime-gap statistics via the Atlas tool worker,
  2. runs a real sandbox experiment (Docker) testing the exponential law,
  3. fetches real literature with the concurrent client,
  4. asks gpt-oss:120b (via ReasoningEngine) to write the paper,
  5. renders it to papers/ and prints the path.

Usage:
    .venv/bin/python scripts/diagnostics/generate_paper_gptoss.py --config config_gptoss.yaml
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

import yaml  # noqa: E402

from cognition.reasoning import ReasoningEngine  # noqa: E402
from communication.paper_generator import PaperGenerator  # noqa: E402
from core.literature_search import search_literature_async  # noqa: E402
from sandbox.executor import SandboxExecutor  # noqa: E402


PRIME_GAP_EXPERIMENT = '''
import numpy as np
from scipy import stats
from sympy import primerange

# Real computation: prime gaps up to 2,000,000, normalized by ln(p)
primes = np.array(list(primerange(2, 2_000_000)))
gaps = np.diff(primes)
norm = gaps / np.log(primes[:-1].astype(float))

# Fit exponential and test goodness of fit
lam = 1.0 / norm.mean()
ks_stat, ks_p = stats.kstest(norm, 'expon', args=(0, norm.mean()))

print(f"N_primes={len(primes)}")
print(f"N_gaps={len(gaps)}")
print(f"raw_mean_gap={gaps.mean():.4f}")
print(f"normalized_mean={norm.mean():.4f}")
print(f"normalized_std={norm.std():.4f}")
print(f"exp_rate_lambda={lam:.4f}")
print(f"KS_statistic={ks_stat:.4f}")
print(f"KS_pvalue={ks_p:.3e}")
print(f"skewness={stats.skew(norm):.4f}")
print(f"kurtosis={stats.kurtosis(norm):.4f}")
print("VERDICT:", "EXPONENTIAL" if ks_p > 0.05 else "DEVIATES_FROM_EXPONENTIAL")
'''


async def main_async(config_path: str) -> int:
    cfg = yaml.safe_load(open(config_path))
    model = cfg["llm"]["reasoner"]["model"]
    topic = "Statistical Distribution of Normalized Prime Gaps: Testing the Exponential Law"
    print(f"=== Generating paper with {model} ===")
    print(f"topic: {topic}\n")

    # ── 1+2. Real sandbox experiment (Docker): gap stats + exponential KS ──
    # We compute everything in one real sandboxed run rather than going through
    # the slow Atlas worker subprocess. Same numbers, fully reproducible.
    print("[1+2/4] Sandbox experiment (Docker): gap stats + exponential KS test ...",
          flush=True)
    sb = SandboxExecutor(cfg.get("sandbox", {"use_docker": True, "max_execution_time": 180}))
    t0 = time.time()
    exp = await sb.execute(PRIME_GAP_EXPERIMENT, language="python")
    print(f"        done in {time.time()-t0:.1f}s  success={exp.get('success')}")
    exp_out = exp.get("stdout", "") or exp.get("stderr", "")
    print("       ", exp_out[:240].replace("\n", " | "))
    gap_tool = exp_out  # the experiment output IS the computational evidence

    # ── 3. Real literature ────────────────────────────────────────────────
    print("[3/4] Literature search ...", flush=True)
    lit = await search_literature_async(
        "prime gaps distribution Cramér model exponential", max_results=6)
    papers = lit.get("papers", [])
    print(f"      {len(papers)} papers, sources={lit.get('sources_succeeded')}")

    # ── 4. Write the paper with the LLM ───────────────────────────────────
    print(f"[4/4] Writing paper with {model} ...", flush=True)
    engine = ReasoningEngine(cfg["llm"])
    gen = PaperGenerator(reasoning_engine=engine)

    tool_sections = [
        {"heading": "Prime gap statistics & exponential-law KS test "
                    "(sandbox, primes up to 2,000,000)",
         "content": exp_out},
    ]
    knowledge_facts = [
        {"subject": "Normalized prime gaps", "predicate": "tested against",
         "object": "exponential distribution via KS test", "confidence": 0.9},
    ]
    recent_thoughts = [
        "Computed prime gaps up to 2,000,000 and normalized each by ln(p).",
        "Ran a Kolmogorov–Smirnov test comparing normalized gaps to an exponential.",
        "Gathered peer-reviewed literature on the Cramér model and prime-gap statistics.",
    ]

    t0 = time.time()
    result = await gen.generate_from_llm(
        topic=topic,
        knowledge_facts=knowledge_facts,
        recent_thoughts=recent_thoughts,
        breakthrough_content=(
            "Empirical KS test on normalized prime gaps up to 2e6 quantifies "
            "agreement with / deviation from the exponential law predicted by "
            "the Cramér random model."
        ),
        tool_sections=tool_sections,
        literature_papers=papers,
    )
    print(f"      paper generated in {time.time()-t0:.1f}s")

    if result.get("error"):
        print("ERROR:", result["error"])
        return 1
    md = result.get("markdown_path") or result.get("md_path") or result.get("paths", {}).get("md")
    print("\n=== RESULT ===")
    for k, v in result.items():
        if "path" in k.lower():
            print(f"  {k}: {v}")
    if md and Path(md).exists():
        text = Path(md).read_text(encoding="utf-8")
        print(f"\n  paper length: {len(text)} chars")
        print("  --- first 1200 chars ---")
        print(text[:1200])
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=str, default="config_gptoss.yaml")
    args = ap.parse_args()
    return asyncio.run(main_async(args.config))


if __name__ == "__main__":
    raise SystemExit(main())
