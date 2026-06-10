#!/usr/bin/env python3
"""
Full Co-Scientist loop — does the paper's Figure-4 Elo curve reproduce?

RE-ANALYSIS THAT MOTIVATED THIS HARNESS. The earlier learning ablation
(run_ablation.py) tested meta-review feedback and belief-weight updates as
*Discussion-prose* modifiers and found them statistically indistinguishable.
Re-reading the Co-Scientist paper (arXiv:2502.18864) showed why that experiment
could not reproduce Google's improvement even in principle:

  1. Google's improvement METRIC is the Elo of hypotheses in the tournament
     (§4.2, Figure 4: best-hypothesis Elo rising ~1350→1610 across 10 time
     buckets) — not the quality of one paper's prose.
  2. Google's improvement ENGINE is the Evolution agent + tournament selection
     pressure ("the co-scientist's iterative improvement capability relies
     heavily on this [Evolution] agent", §3.3.5). Meta-review feedback is an
     amplifier, not the engine. We had never implemented Evolution.

This harness implements the full loop faithfully and measures Google's metric:

  per cycle:  Evolution (top-ranked → new entrants, initial Elo 1200)
              → tournament matches (persistent Elo, FIDE-style K decay)
              → meta-review weakness mining (full arms) → feedback to next
                cycle's evolution prompt (§3.3.6 propagation)

ARMS
  none         control: initial pool only, matches keep playing each cycle (so
               any within-pool Elo drift is measured and subtracted).
  evolution    tournament + Evolution agent, NO meta-review feedback.
  full         the paper's recipe: evolution + meta-review feedback propagation.
  full_weights full + belief-confidence (re-estimated from per-cycle outcomes)
               setting evolved children's confidence (judge weighs confidence
               at 20%) — the "weights" mechanism on top of the paper's recipe.

METRICS (Google's, Figure 4): best_elo and top3_avg_elo per cycle, plus the
control-adjusted improvement Δbest(arm) − Δbest(none).

Run:
    .venv/bin/python experiments/learning_ablation/run_elo_loop.py \
        --arms none,evolution,full,full_weights --topic-index 0 --seeds 3 --cycles 8
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cognition.ranking_agent import (  # noqa: E402
    HypothesisRecord, expected_score, _k_factor, heuristic_judge, INITIAL_ELO,
)
from cognition.evolution_agent import evolve_hypothesis, STRATEGIES  # noqa: E402
from cognition.meta_review_agent import MetaReviewAgent  # noqa: E402
from communication.paper_enhancer import generate_hypothesis  # noqa: E402
from experiments.learning_ablation.run_ablation import TOPICS  # noqa: E402

OUT_DIR = ROOT / "experiments" / "learning_ablation" / "elo_runs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ── tournament mechanics (persistent Elo, paper-faithful) ─────────────────────

def _play_match(a: HypothesisRecord, b: HypothesisRecord) -> None:
    """One pairwise match with persistent Elo update.

    Standard Elo: EACH player's update uses their OWN K-factor. The earlier
    pair-averaged K let a veteran (K=10) harvest inflated gains from fresh
    entrants (K=40 → pair avg 25), which the adversarial verifiers identified
    as a mechanical Elo pump in the treated arms. Per-player K removes it.
    """
    s_a = heuristic_judge(a, b)
    e_a = expected_score(a.elo, b.elo)
    a.elo += _k_factor(a.matches) * (s_a - e_a)
    b.elo += _k_factor(b.matches) * ((1.0 - s_a) - (1.0 - e_a))
    a.matches += 1
    b.matches += 1
    if s_a > 0.55:
        a.wins += 1; b.losses += 1
    elif s_a < 0.45:
        a.losses += 1; b.wins += 1
    else:
        a.draws += 1; b.draws += 1


def _record_from_dict(h: dict) -> HypothesisRecord:
    return HypothesisRecord(
        hypothesis=h.get("hypothesis", ""),
        domain=h.get("domain", ""),
        novelty_status=h.get("novelty_status", ""),
        confidence=float(h.get("confidence", 0.5)),
        extra={k: v for k, v in h.items() if k not in
               ("hypothesis", "domain", "novelty_status", "confidence")},
    )


def _norm_text(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", t.lower())[:120]


def _dedup(pool: list[HypothesisRecord]) -> list[HypothesisRecord]:
    """Proximity-agent stand-in: drop near-duplicate texts, keep higher Elo."""
    seen: dict[str, HypothesisRecord] = {}
    for r in sorted(pool, key=lambda x: -x.elo):
        key = _norm_text(r.hypothesis)
        if key not in seen:
            seen[key] = r
    return list(seen.values())


# ── meta-review weakness mining for hypotheses ────────────────────────────────

def _mine_weaknesses(pool: list[HypothesisRecord]) -> list[dict]:
    """Derive review issues from the bottom half of the tournament.

    Mirrors the paper's recurrent/tournament review: losing hypotheses'
    weaknesses (no explicit test, vagueness, restating known results) become
    the recurring issues the meta-review agent synthesizes.
    """
    issues = []
    ranked = sorted(pool, key=lambda r: -r.elo)
    bottom = ranked[len(ranked) // 2:]
    for r in bottom:
        text = r.hypothesis.lower()
        if not any(m in text for m in ("test", "measur", "compar", "predict")):
            issues.append({"severity": "high",
                           "message": "hypothesis has no explicit test procedure (falsifiability)",
                           "suggestion": "append 'Testable via: <concrete procedure>'"})
        if len(r.hypothesis) < 90:
            issues.append({"severity": "medium",
                           "message": "hypothesis is vague — no named quantities or ranges",
                           "suggestion": "name quantities, thresholds, baselines"})
        if r.novelty_status == "known_control":
            issues.append({"severity": "medium",
                           "message": "hypothesis restates a known control / textbook result",
                           "suggestion": "propose a candidate deviation instead"})
    return issues


# ── one run of the loop ───────────────────────────────────────────────────────

async def run_loop(arm: str, topic_spec: dict, cycles: int, seed: int,
                   evolutions_per_cycle: int = 2) -> dict:
    domain = topic_spec["domain"]
    results = topic_spec["results"]
    rng = random.Random(10_000 * seed + 7)

    # Initial pool from the existing hypothesis generator (paper: Generation agent).
    pool = [_record_from_dict(dict(h, domain=domain))
            for h in generate_hypothesis(domain, results)]
    # Ensure a minimum pool so tournaments are meaningful.
    while len(pool) < 4:
        pool.append(_record_from_dict({
            "hypothesis": f"The {domain} results are consistent with standard theory.",
            "novelty_status": "known_control", "confidence": 0.5, "domain": domain}))

    meta = MetaReviewAgent() if arm in ("full", "full_weights") else None
    belief_state: dict = {}

    # Seed tournament: initial round-robin so cycle-0 ratings are settled.
    pairs = [(i, j) for i in range(len(pool)) for j in range(i + 1, len(pool))]
    rng.shuffle(pairs)
    for i, j in pairs:
        _play_match(pool[i], pool[j])

    trajectory = []

    def snapshot(cycle: int):
        ranked = sorted(pool, key=lambda r: -r.elo)
        top3 = ranked[:3]
        trajectory.append({
            "cycle": cycle,
            "best_elo": round(ranked[0].elo, 1),
            "top3_avg_elo": round(sum(r.elo for r in top3) / len(top3), 1),
            "pool_size": len(pool),
            "best_is_evolved": "strategy" in (ranked[0].extra or {}),
        })

    snapshot(0)

    feedback = ""
    llm_children = 0
    det_children = 0
    for cycle in range(1, cycles + 1):
        # 1a. PLACEBO (pool-dynamics control): inject new entrants with the SAME
        #     cadence as evolution but ZERO quality change — a lightly perturbed
        #     clone of a mid-ranked incumbent. Isolates the new-entrant /
        #     pool-cap mechanics from genuine hypothesis improvement, per the
        #     adversarial verifiers' Elo-inflation critique.
        if arm == "placebo":
            ranked = sorted(pool, key=lambda r: -r.elo)
            for k in range(evolutions_per_cycle):
                donor = ranked[len(ranked) // 2 % len(ranked)]
                clone_text = donor.hypothesis.replace("may ", "might ").replace("The ", "This ", 1)
                rec = _record_from_dict({
                    "hypothesis": clone_text, "domain": domain,
                    "novelty_status": donor.novelty_status,
                    "confidence": donor.confidence,
                    "strategy": "placebo_clone",
                })
                rec.elo = INITIAL_ELO
                pool.append(rec)

        # 1b. EVOLUTION (paper §3.3.5) — evolution arms only.
        if arm in ("evolution", "full", "full_weights"):
            ranked = sorted(pool, key=lambda r: -r.elo)
            for k in range(evolutions_per_cycle):
                parent = ranked[min(k, len(ranked) - 1)]
                strategy = STRATEGIES[(cycle + k) % len(STRATEGIES)]
                second = ranked[min(k + 1, len(ranked) - 1)] if strategy == "combination" else None
                parent_dict = {"hypothesis": parent.hypothesis, "elo": parent.elo,
                               "tournament_record": f"{parent.wins}W-{parent.losses}L-{parent.draws}D",
                               "novelty_status": parent.novelty_status,
                               "confidence": parent.confidence, "domain": domain}
                second_dict = None
                if second is not None:
                    second_dict = {"hypothesis": second.hypothesis, "elo": second.elo}
                child = await evolve_hypothesis(
                    parent_dict, strategy=strategy, domain=domain, results=results,
                    second_parent=second_dict,
                    feedback=feedback if arm in ("full", "full_weights") else None,
                )
                if child.get("evolver") == "llm":
                    llm_children += 1
                else:
                    det_children += 1
                # weights arm: learned belief confidence sets the child's
                # confidence (judge weighs confidence at 20%) — real causal path.
                if arm == "full_weights" and belief_state:
                    avg_conf = sum(b["confidence"] for b in belief_state.values()) / len(belief_state)
                    child["confidence"] = max(0.3, min(0.9, avg_conf))
                rec = _record_from_dict(dict(child, domain=domain))
                rec.elo = INITIAL_ELO  # paper: new entrants start at 1200
                pool.append(rec)

        pool[:] = _dedup(pool)

        # 2. TOURNAMENT MATCHES this cycle (persistent Elo).
        ranked = sorted(pool, key=lambda r: -r.elo)
        new_entrants = [r for r in pool if r.matches < 4]
        incumbents = [r for r in pool if r.matches >= 4] or ranked
        for entrant in new_entrants:
            for opp in rng.sample(incumbents, min(5, len(incumbents))):
                if opp is not entrant:
                    _play_match(entrant, opp)
        # Top-4 round robin (paper: top-ranked get the most matches).
        top4 = sorted(pool, key=lambda r: -r.elo)[:4]
        for i in range(len(top4)):
            for j in range(i + 1, len(top4)):
                _play_match(top4[i], top4[j])

        # Cap pool (keep best 16) to bound compute, after matches.
        pool[:] = sorted(pool, key=lambda r: -r.elo)[:16]

        # 3. META-REVIEW (paper §3.3.6) — full arms: mine recurring weaknesses,
        #    synthesize, propagate to next cycle's evolution prompt.
        if meta is not None:
            meta.ingest_review({"issues": _mine_weaknesses(pool)})
            feedback = meta.synthesize().as_prompt_suffix()

        # 4. WEIGHTS (full_weights): belief re-estimation from cycle outcomes.
        if arm == "full_weights":
            ranked = sorted(pool, key=lambda r: -r.elo)
            top_half = ranked[: len(ranked) // 2]
            evolved_in_top = sum(1 for r in top_half if "strategy" in (r.extra or {}))
            b = belief_state.setdefault("evolution_works",
                                        {"confidence": 0.5, "confirmed": 0, "contradicted": 0})
            if evolved_in_top > 0:
                b["confirmed"] += 1
            else:
                b["contradicted"] += 1
            total = b["confirmed"] + b["contradicted"]
            b["confidence"] = round(0.5 * b["confidence"] + 0.5 * (b["confirmed"] / total), 4)

        snapshot(cycle)

    best0, bestF = trajectory[0]["best_elo"], trajectory[-1]["best_elo"]
    t30, t3F = trajectory[0]["top3_avg_elo"], trajectory[-1]["top3_avg_elo"]
    n_children = llm_children + det_children
    final_pool = [
        {"elo": round(r.elo, 1), "matches": r.matches,
         "evolver": (r.extra or {}).get("evolver"),
         "strategy": (r.extra or {}).get("strategy"),
         "hypothesis": r.hypothesis}
        for r in sorted(pool, key=lambda x: -x.elo)
    ]
    return {
        "arm": arm, "domain": domain, "topic": topic_spec["topic"], "seed": seed,
        "trajectory": trajectory,
        "d_best": round(bestF - best0, 1), "d_top3": round(t3F - t30, 1),
        "final_best_is_evolved": trajectory[-1]["best_is_evolved"],
        # Degradation accounting — the prior run silently fell back to the
        # deterministic evolver on 100% of calls; never let that hide again.
        "llm_children": llm_children, "det_children": det_children,
        "llm_share": round(llm_children / n_children, 3) if n_children else None,
        "final_pool": final_pool,
    }


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="none,evolution,full,full_weights")
    ap.add_argument("--topic-index", type=int, default=None)
    ap.add_argument("--topics", type=int, default=len(TOPICS))
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--cycles", type=int, default=8)
    ap.add_argument("--evolutions-per-cycle", type=int, default=2)
    args = ap.parse_args()

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    topics = [TOPICS[args.topic_index]] if args.topic_index is not None else TOPICS[: args.topics]

    print(f"Elo loop: arms={arms} topics={len(topics)} seeds={args.seeds} "
          f"cycles={args.cycles} evolutions/cycle={args.evolutions_per_cycle}")

    runs = []
    t0 = time.time()
    for arm in arms:
        for topic in topics:
            for seed in range(args.seeds):
                run = await run_loop(arm, topic, args.cycles, seed,
                                     args.evolutions_per_cycle)
                runs.append(run)
                tr = run["trajectory"]
                print(f"  {arm:12s} | {run['domain']:11s} | seed {seed} | "
                      f"best {tr[0]['best_elo']}->{tr[-1]['best_elo']} d_best={run['d_best']} "
                      f"top3 {tr[0]['top3_avg_elo']}->{tr[-1]['top3_avg_elo']} d_top3={run['d_top3']} "
                      f"evolved_won={run['final_best_is_evolved']} "
                      f"llm_share={run['llm_share']}")

    # Aggregate per arm (raw per-run values preserved).
    def stats(vals):
        n = len(vals)
        if not n:
            return {"n": 0, "mean": None, "std": None}
        m = sum(vals) / n
        sd = (sum((v - m) ** 2 for v in vals) / n) ** 0.5
        return {"n": n, "mean": round(m, 1), "std": round(sd, 1)}

    summary = {}
    for arm in arms:
        d_best = [r["d_best"] for r in runs if r["arm"] == arm]
        d_top3 = [r["d_top3"] for r in runs if r["arm"] == arm]
        evolved_won = [r["final_best_is_evolved"] for r in runs if r["arm"] == arm]
        llm_shares = [r["llm_share"] for r in runs if r["arm"] == arm and r["llm_share"] is not None]
        summary[arm] = {
            "d_best": stats(d_best), "d_top3": stats(d_top3),
            "raw_d_best": d_best, "raw_d_top3": d_top3,
            "evolved_won_share": round(sum(evolved_won) / len(evolved_won), 3) if evolved_won else None,
            "llm_share_mean": round(sum(llm_shares) / len(llm_shares), 3) if llm_shares else None,
        }
    # Control-adjusted: arm improvement minus the none arm's drift.
    none_mean = summary.get("none", {}).get("d_best", {}).get("mean") or 0.0
    for arm in arms:
        m = summary[arm]["d_best"]["mean"]
        summary[arm]["d_best_minus_control"] = round(m - none_mean, 1) if m is not None else None

    out = {
        "config": vars(args) | {"arms": arms, "topics": [t["topic"] for t in topics]},
        "summary": summary,
        "runs": runs,
        "wall_seconds": round(time.time() - t0, 1),
    }
    # Unique filename: the second-resolution stamp alone collided when two
    # parallel cells finished in the same second (corrupted a control-arm file
    # in the first run — caught by the verifiers). uuid suffix removes that.
    import uuid
    stamp = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    out_path = OUT_DIR / f"elo_loop_{'_'.join(arms)}_{stamp}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("\n" + "=" * 72)
    print("SUMMARY — Google's metric (Figure 4): Δ best-hypothesis Elo over cycles")
    print("=" * 72)
    print(f"{'arm':13s} {'Δbest(mean±std)':>18s} {'Δtop3(mean±std)':>18s} {'Δbest−control':>14s} {'evolved won':>12s}")
    for arm in arms:
        s = summary[arm]
        db, dt = s["d_best"], s["d_top3"]
        db_str = f"{db['mean']}±{db['std']}"
        dt_str = f"{dt['mean']}±{dt['std']}"
        print(f"{arm:13s} {db_str:>18s} {dt_str:>18s} "
              f"{str(s['d_best_minus_control']):>14s} {str(s['evolved_won_share']):>12s}")
    print(f"\nWrote {out_path}  ({out['wall_seconds']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
