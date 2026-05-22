"""Review every all-domain paper:
- score with rubric
- run reflection
- search for novelty signals (candidate_novelty status, Elo > 1530, etc)
- check tool execution coverage
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from experiments.ab_test.scoring.score_paper import score_paper, score_directory
from cognition.reflection_agent import reflect


PAPERS_DIR = REPO_ROOT / "experiments" / "all_domains" / "papers"


def detect_novelty_signals(md: str) -> dict:
    """Look for signals that suggest a paper has actual novelty (not just controls)."""
    signals = {
        "candidate_novelty_count": len(re.findall(r"candidate_novelty", md, flags=re.IGNORECASE)),
        "testable_hypothesis_count": len(re.findall(r"testable_hypothesis", md, flags=re.IGNORECASE)),
        "known_control_count": len(re.findall(r"known_control", md, flags=re.IGNORECASE)),
        "max_elo": 0,
        "has_falsifiable_predictions": bool(re.search(r"falsifiable", md, flags=re.IGNORECASE)),
        "has_quantitative_predictions": False,
        "n_hypotheses": 0,
        "novelty_score": 0.0,
    }
    elos = [float(m) for m in re.findall(r"Elo:\s*(\d+(?:\.\d+)?)", md)]
    if elos:
        signals["max_elo"] = max(elos)
    h_block = re.search(r"##\s*Testable Predictions?(.+?)(?=##|\Z)", md, flags=re.DOTALL | re.IGNORECASE)
    if h_block:
        signals["n_hypotheses"] = len(re.findall(r"H\d+\.", h_block.group(1)))
        # Quantitative predictions: numbers + comparison operators in hypothesis text
        if re.search(r"H\d+\.[^H]+?(?:≥|≤|>|<|±|within|exceed|less than)\s*[\d.]+", h_block.group(1)):
            signals["has_quantitative_predictions"] = True

    # Composite novelty score 0-100
    novelty = 0.0
    novelty += min(40, signals["candidate_novelty_count"] * 10)
    novelty += min(20, signals["testable_hypothesis_count"] * 5)
    novelty += min(20, (signals["max_elo"] - 1500) if signals["max_elo"] > 1500 else 0)
    if signals["has_falsifiable_predictions"]:
        novelty += 10
    if signals["has_quantitative_predictions"]:
        novelty += 10
    # Penalize all-controls papers
    if signals["candidate_novelty_count"] == 0 and signals["testable_hypothesis_count"] == 0:
        novelty *= 0.3
    signals["novelty_score"] = min(100, novelty)
    return signals


def main():
    papers = sorted(PAPERS_DIR.glob("*.md"))
    if not papers:
        print("No papers found in", PAPERS_DIR)
        return 1

    # Need peer abstracts for uniqueness score
    abstracts = []
    for p in papers:
        m = re.search(r"##\s*Abstract\s*(.+?)(?=##)", p.read_text(errors="ignore"),
                      flags=re.DOTALL | re.IGNORECASE)
        if m:
            abstracts.append(m.group(1))

    report = []
    print(f"\n{'paper':60s} {'rubric':>7s} {'refl':>7s} {'novelty':>8s} {'verdict':>10s}")
    print("-" * 100)

    for i, p in enumerate(papers):
        md = p.read_text(encoding="utf-8")
        peer = [a for j, a in enumerate(abstracts) if j != i]
        score = score_paper(p, peer)
        refl = reflect(md)
        novelty = detect_novelty_signals(md)

        verdict = "STRONG" if (score.total >= 70 and refl.score >= 80 and novelty["novelty_score"] >= 30) \
            else "GOOD" if (score.total >= 60 and refl.score >= 70) \
            else "WEAK"

        print(f"  {p.name[:58]:58s} {score.total:>7.2f} {refl.score:>7.1f} {novelty['novelty_score']:>7.1f}  {verdict:>10s}")
        report.append({
            "paper": p.name,
            "domain": score.domain,
            "rubric_score": score.total,
            "rubric_per_dim": {f: getattr(score, f) for f in
                ['provenance_integrity','tool_diversity','falsifiability',
                 'explicit_limitations','numerical_claims_grounded',
                 'citation_accuracy','abstract_uniqueness',
                 'statistical_rigor','reproducibility_info']},
            "reflection_score": refl.score,
            "reflection_pass": refl.pass_overall,
            "reflection_issues": [{"severity": i["severity"], "section": i["section"],
                                   "message": i["message"]} for i in refl.issues],
            "novelty": novelty,
            "verdict": verdict,
        })

    print("-" * 100)
    avg_rubric = sum(r["rubric_score"] for r in report) / len(report)
    avg_refl = sum(r["reflection_score"] for r in report) / len(report)
    avg_novelty = sum(r["novelty"]["novelty_score"] for r in report) / len(report)
    n_strong = sum(1 for r in report if r["verdict"] == "STRONG")
    n_good = sum(1 for r in report if r["verdict"] == "GOOD")
    n_weak = sum(1 for r in report if r["verdict"] == "WEAK")
    print(f"  {'AVERAGES':58s} {avg_rubric:>7.2f} {avg_refl:>7.1f} {avg_novelty:>7.1f}")
    print(f"  Verdict tally: STRONG={n_strong}  GOOD={n_good}  WEAK={n_weak}")

    out = REPO_ROOT / "experiments" / "all_domains" / "REVIEW.json"
    out.write_text(json.dumps({
        "n_papers": len(report),
        "avg_rubric": avg_rubric,
        "avg_reflection": avg_refl,
        "avg_novelty": avg_novelty,
        "verdict_counts": {"STRONG": n_strong, "GOOD": n_good, "WEAK": n_weak},
        "papers": report,
    }, indent=2))
    print(f"\nDetailed review: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
