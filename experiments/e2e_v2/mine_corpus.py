#!/usr/bin/env python3
"""
Mine the paper corpus into a longitudinal quality dataset.

The hundreds of papers generated during the hardening + ablation work are not
throwaway — partitioned by file mtime they form a record of A.M.Y's output
quality across its development. This scores every paper on the full rubric AND
the Discussion-only judge, buckets by ERA, and writes a dataset + summary.

Eras (by mtime; the project's own development milestones):
  pre_hardening   : before 2026-05-22  (legacy versions)
  hardening       : 2026-05-22 .. 2026-06-08
  e2e_v2          : 2026-06-09 onward  (new tools live)
Plus directory-based cohorts: showcase, all_domains, e2e_v2/.

Run:
    .venv/bin/python experiments/e2e_v2/mine_corpus.py [--limit N] [--sample N]
"""
from __future__ import annotations

import argparse
import glob
import json
import random
import statistics as st
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.ab_test.scoring.score_paper import score_paper  # noqa: E402
from experiments.ab_test.scoring.score_discussion import score_discussion  # noqa: E402

# Era boundaries as epoch seconds (UTC-ish; mtime based).
import datetime as _dt
def _ts(y, m, d):
    return time.mktime(_dt.datetime(y, m, d).timetuple())
ERA_HARDENING_START = _ts(2026, 5, 22)
ERA_E2E_START = _ts(2026, 6, 9)


def _era(mtime: float) -> str:
    if mtime < ERA_HARDENING_START:
        return "pre_hardening"
    if mtime < ERA_E2E_START:
        return "hardening"
    return "e2e_v2_window"


def _cohort(path: str) -> str:
    if "/showcase/" in path:
        return "showcase"
    if "/all_domains/" in path:
        return "all_domains"
    if "/e2e_v2/" in path:
        return "e2e_v2"
    if "/rejected/" in path:
        return "rejected"
    return "papers_flat"


def _summ(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0}
    return {"n": len(vals), "mean": round(st.mean(vals), 1),
            "median": round(st.median(vals), 1),
            "std": round(st.pstdev(vals), 1) if len(vals) > 1 else 0.0,
            "min": round(min(vals), 1), "max": round(max(vals), 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="cap total papers (0=all)")
    ap.add_argument("--sample", type=int, default=0, help="random sample size (0=all)")
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    paths = []
    for pat in ("papers/*.md", "papers/showcase/*.md", "papers/rejected/*.md",
                "papers/e2e_v2/*.md", "experiments/all_domains/papers/*.md",
                "experiments/flagship/papers/*.md"):
        paths.extend(glob.glob(str(ROOT / pat)))
    paths = sorted(set(paths))
    if args.sample and len(paths) > args.sample:
        random.Random(args.seed).shuffle(paths)
        paths = paths[: args.sample]
    if args.limit:
        paths = paths[: args.limit]

    print(f"Scoring {len(paths)} papers…")
    records = []
    t0 = time.time()
    for i, p in enumerate(paths):
        try:
            mtime = Path(p).stat().st_mtime
            rubric = score_paper(Path(p), peer_abstracts=[]).total
            disc = score_discussion(Path(p)).total
            records.append({"path": p, "cohort": _cohort(p), "era": _era(mtime),
                            "rubric": round(rubric, 1), "discussion": round(disc, 1),
                            "mtime": mtime})
        except Exception as e:
            records.append({"path": p, "error": str(e)[:80]})
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(paths)}")

    ok = [r for r in records if "rubric" in r]
    by_era, by_cohort = {}, {}
    for r in ok:
        by_era.setdefault(r["era"], []).append(r)
        by_cohort.setdefault(r["cohort"], []).append(r)

    summary = {
        "n_scored": len(ok), "n_errored": len(records) - len(ok),
        "overall_rubric": _summ([r["rubric"] for r in ok]),
        "overall_discussion": _summ([r["discussion"] for r in ok]),
        "by_era": {e: {"rubric": _summ([r["rubric"] for r in rs]),
                       "discussion": _summ([r["discussion"] for r in rs])}
                   for e, rs in sorted(by_era.items())},
        "by_cohort": {c: {"rubric": _summ([r["rubric"] for r in rs]),
                          "discussion": _summ([r["discussion"] for r in rs])}
                      for c, rs in sorted(by_cohort.items())},
    }

    out_dir = ROOT / "experiments" / "e2e_v2"
    (out_dir / "corpus_dataset.json").write_text(
        json.dumps({"records": ok, "summary": summary,
                    "wall_seconds": round(time.time() - t0, 1)}, indent=2),
        encoding="utf-8")

    print("\n=== CORPUS QUALITY BY ERA (rubric 0-100) ===")
    for e, s in summary["by_era"].items():
        r = s["rubric"]
        print(f"  {e:18s} n={r['n']:4d}  rubric {r.get('mean')}±{r.get('std')}  "
              f"(median {r.get('median')}, max {r.get('max')})")
    print("\n=== BY COHORT ===")
    for c, s in summary["by_cohort"].items():
        r = s["rubric"]
        print(f"  {c:14s} n={r['n']:4d}  rubric {r.get('mean')}±{r.get('std')}  "
              f"disc {s['discussion'].get('mean')}")
    print(f"\nWrote {out_dir / 'corpus_dataset.json'}  ({summary['n_scored']} scored)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
