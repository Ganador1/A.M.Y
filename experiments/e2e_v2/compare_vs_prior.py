#!/usr/bin/env python3
"""
Blind head-to-head: NEW e2e_v2 papers vs PRIOR-version papers.

Whole-paper quality comparison, the user's core question ("how good are the
papers now vs my previous versions"). Each new paper is matched, within the same
domain where possible, against a prior-version paper, and an LLM judge picks the
better manuscript blind (A/B order randomized to cancel position bias). Reports
win rate with a Wilson CI.

Prior pool = papers/showcase + experiments/all_domains/papers (the curated best
of the legacy system) plus a random draw of pre-hardening papers/*.md.

Run:
    .venv/bin/python experiments/e2e_v2/compare_vs_prior.py [--judge llm|heuristic]
"""
from __future__ import annotations

import argparse
import asyncio
import glob
import json
import math
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cognition.ranking_agent import HypothesisRecord, llm_judge, heuristic_judge  # noqa: E402

ERA_E2E_START = time.mktime((2026, 6, 9, 0, 0, 0, 0, 0, -1))

PAPER_JUDGE_PROMPT = """You are an impartial reviewer comparing two computational-science manuscripts (call them A and B). Judge which is the BETTER paper overall, weighing: scientific rigor, whether numerical claims are grounded in stated computational evidence, honest treatment of limitations and novelty (not overstating), depth of the Discussion, and reproducibility. Penalise vagueness, template-like boilerplate, and unsupported claims.

Output STRICTLY one JSON object: {{"winner": "A" or "B", "reason": "<one sentence>"}}.

=== PAPER A ===
{a}

=== PAPER B ===
{b}
"""


def _excerpt(path: str, max_chars: int = 4000) -> str:
    md = Path(path).read_text(encoding="utf-8", errors="ignore")
    # Strip the bulky raw-output code fences so the judge sees prose/structure.
    md = re.sub(r"```.*?```", "[tool output omitted]", md, flags=re.DOTALL)
    return md[:max_chars]


def _domain_of(path: str) -> str:
    name = Path(path).name.lower()
    for d in ("math", "prime", "chem", "physic", "hydrogen", "bio", "dna",
              "stat", "astro", "quantum"):
        if d in name:
            return d
    return "other"


async def judge_papers(a_path: str, b_path: str, judge: str, rng, sem) -> int:
    """Return 1 if A wins, 0 if B wins, with A/B order randomized."""
    flip = rng.random() < 0.5
    pa, pb = (b_path, a_path) if flip else (a_path, b_path)
    if judge == "heuristic":
        # crude proxy: longer non-boilerplate discussion + more grounded numbers
        from experiments.ab_test.scoring.score_discussion import score_discussion
        sa = score_discussion(Path(pa)).total
        sb = score_discussion(Path(pb)).total
        a_wins_raw = sa >= sb
    else:
        prompt = PAPER_JUDGE_PROMPT.format(a=_excerpt(pa), b=_excerpt(pb))
        from cognition.ranking_agent import _build_ranking_client
        import os
        client = _build_ranking_client()
        model = os.getenv("AMY_ENHANCER_MODEL") or "glm-5.1"
        try:
            async with sem:
                resp = await asyncio.wait_for(
                    client.chat(model=model, messages=[{"role": "user", "content": prompt}],
                                temperature=0.0, max_tokens=600, format_json=True, think=False),
                    timeout=60.0)
            content = (resp.get("message", {}) or {}).get("content", "").strip()
            if content.startswith("```"):
                content = content.strip("`").lstrip("json").strip()
            winner = str(json.loads(content).get("winner", "")).upper()
            a_wins_raw = (winner == "A")
        except Exception:
            a_wins_raw = False
    # de-randomize
    a_wins = (not a_wins_raw) if flip else a_wins_raw
    return 1 if a_wins else 0


def wilson(wins: int, n: int):
    if n == 0:
        return (0.0, 1.0)
    p, z = wins / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", default="llm", choices=["llm", "heuristic"])
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--n-prior", type=int, default=10, help="prior papers to sample")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    sem = asyncio.Semaphore(args.concurrency)

    # New papers: read the authoritative markdown_path from the e2e_v2 audit
    # JSONs (PaperGenerator writes to papers/ flat, not papers/e2e_v2/, so a
    # glob would miss them). Fall back to a glob if no audits exist.
    new_papers = []
    for ap_json in sorted(glob.glob(str(ROOT / "experiments" / "e2e_v2" / "audits" / "*.audit.json"))):
        try:
            a = json.loads(Path(ap_json).read_text())
            mp = a.get("markdown_path")
            if a.get("ok") and mp and Path(ROOT / mp).exists():
                new_papers.append(str(ROOT / mp))
        except Exception:
            pass
    if not new_papers:
        new_papers = sorted(glob.glob(str(ROOT / "papers" / "e2e_v2" / "*.md")))
    if not new_papers:
        print("No e2e_v2 papers found — run gen_e2e_v2.py first."); return 1

    prior = (glob.glob(str(ROOT / "papers" / "showcase" / "*.md"))
             + glob.glob(str(ROOT / "experiments" / "all_domains" / "papers" / "*.md")))
    # add some pre-hardening flat papers
    flat = [p for p in glob.glob(str(ROOT / "papers" / "*.md"))
            if Path(p).stat().st_mtime < ERA_E2E_START]
    rng.shuffle(flat)
    prior = prior + flat[: args.n_prior]
    prior = sorted(set(prior))

    # Match each new paper against several prior papers (prefer same domain).
    matches = []
    for npaper in new_papers:
        nd = _domain_of(npaper)
        same = [p for p in prior if _domain_of(p) == nd] or prior
        for opp in rng.sample(same, min(4, len(same))):
            matches.append((npaper, opp))

    print(f"{len(new_papers)} new vs {len(prior)} prior → {len(matches)} matches [{args.judge}]")
    outcomes = await asyncio.gather(*[
        judge_papers(a, b, args.judge, rng, sem) for (a, b) in matches])
    wins = sum(outcomes)
    n = len(outcomes)
    ci = wilson(wins, n)
    print(f"\nNEW papers win rate vs PRIOR: {wins}/{n} = {round(wins/n, 3)}  95% CI {ci}")

    out = {"judge": args.judge, "n_matches": n, "new_wins": wins,
           "new_win_rate": round(wins / n, 3), "ci95": ci,
           "new_papers": [Path(p).name for p in new_papers],
           "prior_pool_size": len(prior),
           "per_match": [{"new": Path(a).name, "prior": Path(b).name, "new_won": bool(o)}
                         for (a, b), o in zip(matches, outcomes)]}
    import uuid
    p = ROOT / "experiments" / "e2e_v2" / f"compare_vs_prior_{args.judge}_{uuid.uuid4().hex[:6]}.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
