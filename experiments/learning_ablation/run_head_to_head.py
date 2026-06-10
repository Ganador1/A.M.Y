#!/usr/bin/env python3
"""
Anchored head-to-head: do LLM-evolved hypotheses actually beat the others?

WHY THIS EXISTS. Three successive Elo-loop experiments were rejected by
adversarial verification because *within-pool tournament ratings* are dominated
by mechanics (entry-rating equilibration, dedup-broken controls, non-zero-sum
per-player-K updates) rather than hypothesis quality. The fix is to remove
pool mechanics from the measurement entirely:

  - Take the FINAL top hypotheses each arm actually produced (from the v2 run
    JSONs' ``final_pool`` — real artifacts, on disk, auditable).
  - Pit them against each other DIRECTLY, arm vs arm, rank vs rank, in blind
    pairwise matches judged by the LLM scientific-debate judge
    (cognition.ranking_agent.llm_judge — the Co-Scientist §3.3.3 judge, which
    as of today actually runs: the think-model bug is fixed).
  - Randomize A/B presentation order per match to cancel position bias.
  - Report per-arm win rates with exact binomial CIs. No Elo, no pools.

If LLM evolution genuinely improves hypotheses, evolution/full/full_weights
entries should beat none/placebo head-to-head. If they don't, the honest
conclusion is that the loop's measurable gains were rating mechanics all along.

Usage:
    .venv/bin/python experiments/learning_ablation/run_head_to_head.py \
        [--judge llm|heuristic|both] [--top-k 3] [--concurrency 4]
"""
from __future__ import annotations

import argparse
import asyncio
import glob
import json
import math
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cognition.ranking_agent import HypothesisRecord, llm_judge, heuristic_judge  # noqa: E402

RUNS_DIR = ROOT / "experiments" / "learning_ablation" / "elo_runs"
ARMS = ["none", "placebo", "evolution", "full", "full_weights"]


def load_arm_entries(arm: str, top_k: int) -> dict[str, list[dict]]:
    """Per topic: pool final_pool entries across the arm's v2 runs, dedupe,
    keep the top_k by within-arm Elo. Only v2 files (uuid-suffixed) qualify."""
    per_topic: dict[str, list[dict]] = defaultdict(list)
    for path in sorted(glob.glob(str(RUNS_DIR / f"elo_loop_{arm}_2*_*.json"))):
        # v2 files have a 6-hex uuid suffix segment; v1 files don't.
        stem = Path(path).stem
        if len(stem.split("_")[-1]) != 6:
            continue
        try:
            data = json.loads(Path(path).read_text())
        except Exception:
            continue
        for run in data.get("runs", []):
            if run.get("arm") != arm:
                continue
            topic = run.get("domain", "unknown")
            for entry in run.get("final_pool", []):
                per_topic[topic].append(entry)
    out: dict[str, list[dict]] = {}
    for topic, entries in per_topic.items():
        seen: dict[str, dict] = {}
        for e in sorted(entries, key=lambda x: -(x.get("elo") or 0)):
            key = (e.get("hypothesis") or "")[:120].lower()
            if key and key not in seen:
                seen[key] = e
        out[topic] = list(seen.values())[:top_k]
    return out


async def judge_match(a_text: str, b_text: str, judge: str, rng: random.Random,
                      sem: asyncio.Semaphore) -> float:
    """Score favoring A in [0,1], with A/B order randomized to cancel position bias."""
    ra = HypothesisRecord(hypothesis=a_text)
    rb = HypothesisRecord(hypothesis=b_text)
    flip = rng.random() < 0.5
    x, y = (rb, ra) if flip else (ra, rb)
    if judge == "heuristic":
        s = heuristic_judge(x, y)
    else:
        async with sem:
            s = await llm_judge(x, y)
    return (1.0 - s) if flip else s


def wilson_ci(wins: float, n: int) -> tuple[float, float]:
    """95% Wilson interval for a win proportion (draws counted as half-wins)."""
    if n == 0:
        return (0.0, 1.0)
    p = wins / n
    z = 1.96
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(center - half, 3), round(center + half, 3))


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", default="llm", choices=["llm", "heuristic", "both"])
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    sem = asyncio.Semaphore(args.concurrency)

    # Load entries: arm -> topic -> [entries]
    arm_entries = {arm: load_arm_entries(arm, args.top_k) for arm in ARMS}
    topics = sorted({t for d in arm_entries.values() for t in d})
    print("Entrants per (arm, topic):")
    for arm in ARMS:
        counts = {t: len(arm_entries[arm].get(t, [])) for t in topics}
        print(f"  {arm:13s} {counts}")

    judges = ["llm", "heuristic"] if args.judge == "both" else [args.judge]
    results = {}
    t0 = time.time()
    for judge in judges:
        # arm-pair match plan: within each topic, rank-i vs rank-i for every arm pair.
        plan = []
        for topic in topics:
            for i, arm_a in enumerate(ARMS):
                for arm_b in ARMS[i + 1:]:
                    ea = arm_entries[arm_a].get(topic, [])
                    eb = arm_entries[arm_b].get(topic, [])
                    for k in range(min(len(ea), len(eb))):
                        plan.append((topic, arm_a, arm_b,
                                     ea[k]["hypothesis"], eb[k]["hypothesis"]))
        print(f"\n[{judge}] {len(plan)} matches…")

        scores = await asyncio.gather(*[
            judge_match(a_text, b_text, judge, rng, sem)
            for (_, _, _, a_text, b_text) in plan
        ])

        # Tally per arm and per pair (draws = half win each).
        arm_w: dict[str, float] = defaultdict(float)
        arm_n: dict[str, int] = defaultdict(int)
        pair_w: dict[tuple, float] = defaultdict(float)
        pair_n: dict[tuple, int] = defaultdict(int)
        for (topic, arm_a, arm_b, _, _), s in zip(plan, scores):
            if s > 0.55:
                wa, wb = 1.0, 0.0
            elif s < 0.45:
                wa, wb = 0.0, 1.0
            else:
                wa = wb = 0.5
            arm_w[arm_a] += wa; arm_n[arm_a] += 1
            arm_w[arm_b] += wb; arm_n[arm_b] += 1
            pair_w[(arm_a, arm_b)] += wa; pair_n[(arm_a, arm_b)] += 1

        table = {}
        for arm in ARMS:
            n = arm_n[arm]
            ci = wilson_ci(arm_w[arm], n)
            table[arm] = {"win_rate": round(arm_w[arm] / n, 3) if n else None,
                          "n": n, "ci95": ci}
        pairs = {f"{a} vs {b}": {"win_rate_a": round(pair_w[(a, b)] / pair_n[(a, b)], 3),
                                 "n": pair_n[(a, b)]}
                 for (a, b) in pair_n}
        results[judge] = {"per_arm": table, "per_pair": pairs}

        print(f"  {'arm':13s} {'win_rate':>9s} {'95% CI':>16s} {'n':>4s}")
        for arm in ARMS:
            t = table[arm]
            print(f"  {arm:13s} {str(t['win_rate']):>9s} {str(t['ci95']):>16s} {t['n']:>4d}")

    out = {"config": vars(args), "results": results,
           "entrants": {arm: {t: [e["hypothesis"][:140] for e in d.get(t, [])]
                              for t in topics}
                        for arm, d in arm_entries.items()},
           "wall_seconds": round(time.time() - t0, 1)}
    import uuid
    out_path = RUNS_DIR / f"head_to_head_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}  ({out['wall_seconds']}s)")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()) or 0)
