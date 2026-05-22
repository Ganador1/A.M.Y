#!/usr/bin/env python3
"""Regression tests for the autonomous science gate ablation study."""
from pathlib import Path
from tempfile import TemporaryDirectory

from run_autonomous_science_gate_ablation import compare_cohorts, score_paper_text


def test_score_paper_text_flags_confirmed_novelty_and_domain_leakage():
    text = """
    ## Results
    **[NOVEL]**: n=50 rounded Rydberg deviation.
    H1. The molecular weight ratios predict reaction yields with >95% accuracy.
    Status: ALL VERIFIED ✓
    """

    score = score_paper_text(text)

    assert score["confirmed_novelty_claim"] is True
    assert score["domain_leakage"] is True
    assert score["decorative_marker"] is True


def test_compare_cohorts_reports_paired_false_novelty_reduction():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        pre = []
        post = []
        for i in range(4):
            pre_path = root / f"pre_{i}.md"
            post_path = root / f"post_{i}.md"
            pre_path.write_text("**[NOVEL]**: finite observation upgraded to novelty.", encoding="utf-8")
            post_path.write_text("[OBSERVATION]: finite observation; no novelty claim.", encoding="utf-8")
            pre.append(pre_path)
            post.append(post_path)

        result = compare_cohorts(pre, post)

    assert result["n_pairs"] == 4
    assert result["pre"]["confirmed_novelty_claim_rate"] == 1.0
    assert result["post"]["confirmed_novelty_claim_rate"] == 0.0
    assert result["paired"]["confirmed_novelty_claim_reductions"] == 4
    assert result["paired"]["confirmed_novelty_risk_difference"] == -1.0


def main():
    tests = [
        test_score_paper_text_flags_confirmed_novelty_and_domain_leakage,
        test_compare_cohorts_reports_paired_false_novelty_reduction,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()
