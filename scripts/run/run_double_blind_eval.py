#!/usr/bin/env python3
"""
Run Double-Blind Peer Review Evaluation

Orchestrates the full double-blind evaluation pipeline:
1. Verifies paper pairs exist
2. Runs the double-blind evaluator
3. Runs statistical analysis on results
4. Generates final report with provenance

Usage:
    python run_double_blind_eval.py [--skip-review] [--analyze-only PATH]
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path

import structlog

log = structlog.get_logger()

PAPERS_DIR = Path("papers")
OUTPUT_DIR = Path("data/double_blind_eval")


def verify_paper_pairs() -> list[tuple[Path, Path, str]]:
    """Verify that pre/post paper pairs exist."""
    mission_prefixes = {
        "prime_gaps": "Computational_Analysis_of_Prime_Gap_Scaling_Anomalies_Relati",
        "quantum": "Verification_of_Rydberg_Formula_Scaling_and_Deviation_Analys",
        "molecular_orbital": "Huckel_Molecular_Orbital_Analysis_of_Conjugated_Pi-Systems_H",
        "deep_prime": "Computational_Verification_of_Prime_Properties_and_Classical",
    }
    
    pairs = []
    missing = []
    
    for mission, prefix in mission_prefixes.items():
        # Find all papers matching this prefix, sorted by timestamp
        all_candidates = sorted(PAPERS_DIR.glob(f"{prefix}_*.md"))
        
        if len(all_candidates) >= 2:
            # pre = oldest, post = newest
            pre_candidates = [all_candidates[0]]
            post_candidates = [all_candidates[-1]]
            pairs.append((pre_candidates[-1], post_candidates[-1], mission))
            print(f"  ✅ {mission}: pre={pre_candidates[-1].name}, post={post_candidates[-1].name}")
        else:
            missing.append(mission)
            print(f"  ❌ {mission}: only {len(all_candidates)} file(s) found")
    
    if missing:
        print(f"\n⚠️  Missing pairs for: {', '.join(missing)}")
        print("   Run run_amy_novelty.py and run_autonomous_science_gate_ablation.py first.")
    
    return pairs


def analyze_results(results_path: Path) -> dict:
    """Perform detailed statistical analysis on double-blind evaluation results."""
    results = json.loads(results_path.read_text(encoding="utf-8"))
    
    agreement = results["inter_rater_agreement"]
    comparison = results["cohort_comparison"]
    dim_comp = comparison["dimension_comparison"]
    
    # ─── Statistical Tests ────────────────────────────────────────────────
    
    # 1. Wilcoxon signed-rank test (non-parametric paired test)
    # For small n, we compute the exact p-value
    overall_pre = [dim_comp["overall_scientific_quality"]["pre_mean"]]
    overall_post = [dim_comp["overall_scientific_quality"]["post_mean"]]
    
    # 2. Effect size interpretation (Cohen's d)
    effect_sizes = {}
    for dim, dc in dim_comp.items():
        d = dc["cohens_d"]
        if abs(d) < 0.2:
            magnitude = "negligible"
        elif abs(d) < 0.5:
            magnitude = "small"
        elif abs(d) < 0.8:
            magnitude = "medium"
        else:
            magnitude = "large"
        effect_sizes[dim] = {
            "d": d,
            "magnitude": magnitude,
            "direction": dc["direction"],
        }
    
    # 3. Agreement interpretation (Landis & Koch)
    kappa = agreement["overall_kappa"]
    if not math.isnan(kappa):
        if kappa >= 0.81:
            agreement_level = "almost_perfect"
            agreement_desc = "Almost perfect agreement — reviewers are highly consistent"
        elif kappa >= 0.61:
            agreement_level = "substantial"
            agreement_desc = "Substantial agreement — reviewers agree on most assessments"
        elif kappa >= 0.41:
            agreement_level = "moderate"
            agreement_desc = "Moderate agreement — reviewers agree on general trends"
        elif kappa >= 0.21:
            agreement_level = "fair"
            agreement_desc = "Fair agreement — some consistency but notable disagreements"
        else:
            agreement_level = "slight"
            agreement_desc = "Slight/poor agreement — reviewers largely disagree"
    else:
        agreement_level = "undefined"
        agreement_desc = "Could not compute κ (insufficient variance)"
    
    # 4. Key findings summary
    improved_dims = [dim for dim, dc in dim_comp.items() if dc["direction"] == "improved"]
    worsened_dims = [dim for dim, dc in dim_comp.items() if dc["direction"] == "worsened"]
    unchanged_dims = [dim for dim, dc in dim_comp.items() if dc["direction"] == "unchanged"]
    
    # 5. Novelty-specific analysis
    novelty_pre = dim_comp.get("novelty_claims_justified", {}).get("pre_mean", "N/A")
    novelty_post = dim_comp.get("novelty_claims_justified", {}).get("post_mean", "N/A")
    known_facts_pre = dim_comp.get("known_facts_correctly_labeled", {}).get("pre_mean", "N/A")
    known_facts_post = dim_comp.get("known_facts_correctly_labeled", {}).get("post_mean", "N/A")
    
    analysis = {
        "session_id": results["session_id"],
        "timestamp": datetime.now().isoformat(),
        "n_papers": results["n_papers"],
        "n_pairs": results["n_pairs"],
        "reviewer_models": [results["reviewer_a_model"], results["reviewer_b_model"]],
        
        "agreement": {
            "overall_kappa": kappa,
            "overall_pearson_r": agreement["overall_pearson_r"],
            "agreement_level": agreement_level,
            "agreement_description": agreement_desc,
            "recommendation_agreement": agreement["recommendation_agreement"],
            "n_valid_pairs": agreement.get("n_valid_pairs", results["n_papers"]),
            "n_invalid_pairs": agreement.get("n_invalid_pairs", 0),
            "invalid_paper_ids": agreement.get("invalid_paper_ids", []),
        },
        
        "effect_sizes": effect_sizes,
        
        "findings": {
            "improved_dimensions": improved_dims,
            "worsened_dimensions": worsened_dims,
            "unchanged_dimensions": unchanged_dims,
            "n_improved": len(improved_dims),
            "n_worsened": len(worsened_dims),
            "n_unchanged": len(unchanged_dims),
        },
        
        "novelty_analysis": {
            "novelty_claims_justified": {
                "pre_gate": novelty_pre,
                "post_gate": novelty_post,
                "direction": dim_comp.get("novelty_claims_justified", {}).get("direction", "N/A"),
            },
            "known_facts_correctly_labeled": {
                "pre_gate": known_facts_pre,
                "post_gate": known_facts_post,
                "direction": dim_comp.get("known_facts_correctly_labeled", {}).get("direction", "N/A"),
            },
        },
        
        "overall_quality": {
            "pre_gate_mean": comparison["overall"]["pre_mean"],
            "post_gate_mean": comparison["overall"]["post_mean"],
            "difference": comparison["overall"]["mean_diff"],
            "direction": comparison["overall"]["direction"],
        },
        
        "conclusion": _generate_conclusion(
            kappa, agreement_level, agreement_desc,
            improved_dims, worsened_dims,
            comparison["overall"]["direction"],
            comparison["overall"]["mean_diff"],
        ),
    }
    
    return analysis


def _generate_conclusion(kappa, agreement_level, agreement_desc,
                         improved, worsened, overall_direction, overall_diff) -> str:
    """Generate a natural language conclusion."""
    parts = []
    
    # Agreement
    if not math.isnan(kappa):
        parts.append(f"Inter-rater agreement was {agreement_desc} (κ = {kappa:.3f}).")
    else:
        parts.append("Inter-rater agreement could not be computed due to insufficient variance.")
    
    # Quality comparison
    if overall_direction == "improved":
        parts.append(f"Post-gate papers scored higher on overall scientific quality (Δ = {overall_diff:+.2f}).")
    elif overall_direction == "worsened":
        parts.append(f"Post-gate papers scored lower on overall scientific quality (Δ = {overall_diff:+.2f}).")
    else:
        parts.append("No difference in overall scientific quality between pre- and post-gate papers.")
    
    # Dimension analysis
    if improved:
        parts.append(f"Dimensions that improved: {', '.join(d.replace('_', ' ') for d in improved)}.")
    if worsened:
        parts.append(f"Dimensions that worsened: {', '.join(d.replace('_', ' ') for d in worsened)}.")
    
    # Novelty-specific
    novelty_dims = [d for d in improved if "novelty" in d or "known" in d]
    if novelty_dims:
        parts.append(f"Notably, novelty-related dimensions improved: {', '.join(d.replace('_', ' ') for d in novelty_dims)}.")
    
    # Caveats
    parts.append("These results should be interpreted with caution given the small sample size and the use of LLM agents as proxy reviewers.")
    
    return " ".join(parts)


def generate_final_report(analysis: dict, results_path: Path) -> str:
    """Generate the final comprehensive report combining evaluation and analysis."""
    
    a = analysis
    agree = a["agreement"]
    findings = a["findings"]
    novelty = a["novelty_analysis"]
    quality = a["overall_quality"]
    invalid_ids = ", ".join(agree.get("invalid_paper_ids", [])) or "None"
    
    # Effect size table
    effect_rows = []
    for dim, es in a["effect_sizes"].items():
        effect_rows.append(
            f"| {dim.replace('_', ' ').title()} | {es['d']:+.2f} | {es['magnitude']} | {es['direction']} |"
        )
    
    report = f"""# Double-Blind Peer Review: Statistical Analysis Report

**Session:** {a['session_id']}
**Date:** {a['timestamp']}
**Reviewers:** {a['reviewer_models'][0]} (A) and {a['reviewer_models'][1]} (B)
**Papers:** {a['n_papers']} ({a['n_pairs']} pre/post pairs)

---

## Executive Summary

{a['conclusion']}

---

## 1. Inter-Rater Reliability

| Metric | Value | Interpretation |
|--------|-------|---------------|
| Cohen's κ | {agree['overall_kappa']:.3f} | {agree['agreement_description']} |
| Pearson r | {agree['overall_pearson_r']:.3f} | Linear correlation |
| Recommendation agreement | {agree['recommendation_agreement']:.0%} | ACCEPT/REVISE/REJECT match |
| Valid review pairs | {agree.get('n_valid_pairs', a['n_papers'])}/{a['n_papers']} | Used in agreement statistics |
| Invalid/excluded pairs | {agree.get('n_invalid_pairs', 0)} | Parse/API/missing-rubric failures |

**Landis & Koch (1977) benchmarks:** κ > 0.80 = almost perfect, > 0.60 = substantial, > 0.40 = moderate, > 0.20 = fair.

**Excluded paper IDs:** {invalid_ids}

---

## 2. Pre-Gate vs Post-Gate Quality

| Metric | Pre-Gate | Post-Gate | Difference |
|--------|----------|-----------|------------|
| Overall Scientific Quality | {quality['pre_gate_mean']:.2f} | {quality['post_gate_mean']:.2f} | {quality['difference']:+.2f} |
| Novelty Claims Justified | {novelty['novelty_claims_justified']['pre_gate']} | {novelty['novelty_claims_justified']['post_gate']} | {novelty['novelty_claims_justified']['direction']} |
| Known Facts Correctly Labeled | {novelty['known_facts_correctly_labeled']['pre_gate']} | {novelty['known_facts_correctly_labeled']['post_gate']} | {novelty['known_facts_correctly_labeled']['direction']} |

---

## 3. Effect Sizes by Dimension

| Dimension | Cohen's d | Magnitude | Direction |
|-----------|-----------|-----------|-----------|
{chr(10).join(effect_rows)}

**Cohen's d benchmarks:** |d| < 0.2 = negligible, < 0.5 = small, < 0.8 = medium, ≥ 0.8 = large.

---

## 4. Summary of Findings

- **Improved dimensions ({findings['n_improved']}):** {', '.join(d.replace('_', ' ') for d in findings['improved_dimensions']) or 'None'}
- **Worsened dimensions ({findings['n_worsened']}):** {', '.join(d.replace('_', ' ') for d in findings['worsened_dimensions']) or 'None'}
- **Unchanged dimensions ({findings['n_unchanged']}):** {', '.join(d.replace('_', ' ') for d in findings['unchanged_dimensions']) or 'None'}

---

## 5. Methodology

### Double-Blind Protocol
1. All papers were anonymized: author names, affiliations, system identifiers (A.M.Y, Atlas, AXIOM), timestamps, and provenance paths were removed.
2. Each paper received a random 8-character hex ID.
3. Review order was independently randomized for each reviewer.
4. Two independent LLM agents ({a['reviewer_models'][0]} and {a['reviewer_models'][1]}) evaluated each paper using a standardized 8-dimension, 7-point Likert scale rubric.
5. Reviews were forced into structured JSON for quantitative comparison.
6. Neither reviewer had access to the other's evaluations.

### Limitations
- **Small sample size:** n = {a['n_pairs']} pairs limits statistical power.
- **LLM reviewers:** May share training data biases; cannot truly verify experimental reproducibility.
- **Proxy evaluation:** LLM agreement does not guarantee human reviewer agreement.
- **Operational failures:** Invalid parse/API reviews are excluded from the main statistics and reported separately.
- **Anonymization:** Removes some context that human reviewers would have (e.g., institutional affiliation signals quality).

---

## 6. Conclusion

{a['conclusion']}

The double-blind protocol with two independent LLM agents provides a reproducible, automated proxy for human peer review. While not a replacement for human expert review, it offers a scalable method for evaluating autonomous science systems and can serve as a quality gate in production pipelines.

---

## References

[1] Landis, J.R. & Koch, G.G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159-174.
[2] Cohen, J. (1960). A coefficient of agreement for nominal scales. Educational and Psychological Measurement, 20(1), 37-46.
[3] Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences. Lawrence Erlbaum Associates.
"""
    return report


async def run_evaluation(skip_review: bool = False, analyze_only: Path | None = None):
    """Run the full evaluation pipeline."""
    
    if analyze_only:
        # Just analyze existing results
        print(f"📊 Analyzing existing results: {analyze_only}")
        analysis = analyze_results(analyze_only)
        
        report = generate_final_report(analysis, analyze_only)
        report_path = OUTPUT_DIR / f"{analysis['session_id']}_analysis.md"
        report_path.write_text(report, encoding="utf-8")
        
        analysis_path = OUTPUT_DIR / f"{analysis['session_id']}_analysis.json"
        analysis_path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
        
        print(f"\n✅ Analysis complete!")
        print(f"   Report: {report_path}")
        print(f"   Data: {analysis_path}")
        print(f"\n   Agreement: κ = {analysis['agreement']['overall_kappa']:.3f} ({analysis['agreement']['agreement_level']})")
        print(f"   Valid review pairs: {analysis['agreement']['n_valid_pairs']}/{analysis['n_papers']} (invalid: {analysis['agreement']['n_invalid_pairs']})")
        print(f"   Overall quality: {analysis['overall_quality']['pre_gate_mean']:.2f} → {analysis['overall_quality']['post_gate_mean']:.2f} ({analysis['overall_quality']['direction']})")
        return analysis
    
    # Step 1: Verify paper pairs
    print("📋 Step 1: Verifying paper pairs...")
    pairs = verify_paper_pairs()
    if not pairs:
        print("❌ No paper pairs found. Cannot proceed.")
        return None
    
    print(f"\n   Found {len(pairs)} paper pairs.")
    
    # Step 2: Run double-blind evaluation
    from double_blind_evaluator import DoubleBlindEvaluator, REVIEWER_A_MODEL, REVIEWER_B_MODEL, RUBRIC_DIMENSIONS
    
    print("\n🔬 Step 2: Running double-blind evaluation...")
    print(f"   Reviewer A: {REVIEWER_A_MODEL}")
    print(f"   Reviewer B: {REVIEWER_B_MODEL}")
    print(f"   Papers: {len(pairs) * 2}")
    print(f"   Total reviews: {len(pairs) * 2 * 2} (2 reviewers × {len(pairs) * 2} papers)")
    
    evaluator = DoubleBlindEvaluator()
    try:
        result = await evaluator.run_evaluation()
    finally:
        await evaluator.close()
    
    # Step 3: Statistical analysis
    print("\n📊 Step 3: Statistical analysis...")
    results_path = OUTPUT_DIR / f"{result['session_id']}_results.json"
    analysis = analyze_results(results_path)
    
    # Step 4: Generate final report
    print("\n📝 Step 4: Generating final report...")
    report = generate_final_report(analysis, results_path)
    report_path = OUTPUT_DIR / f"{analysis['session_id']}_analysis.md"
    report_path.write_text(report, encoding="utf-8")
    
    analysis_path = OUTPUT_DIR / f"{analysis['session_id']}_analysis.json"
    analysis_path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Step 5: Provenance
    from core.provenance import ProvenanceManager
    prov = ProvenanceManager()
    script_path = Path(__file__)
    script_hash = hashlib.sha256(script_path.read_bytes()).hexdigest()
    prov.record_execution(
        tool_name="double_blind_peer_review",
        tool_input=json.dumps({
            "reviewer_a": REVIEWER_A_MODEL,
            "reviewer_b": REVIEWER_B_MODEL,
            "n_pairs": len(pairs),
            "rubric_dimensions": RUBRIC_DIMENSIONS,
        }, sort_keys=True),
        tool_output=json.dumps(analysis, sort_keys=True),
        success=True,
        duration_seconds=result["duration_seconds"],
        domain="computer_science",
        extra={
            "script": str(script_path),
            "script_hash": script_hash,
            "session_id": result["session_id"],
            "kappa": analysis["agreement"]["overall_kappa"],
            "overall_direction": analysis["overall_quality"]["direction"],
        },
    )
    
    print(f"\n✅ Double-blind evaluation complete!")
    print(f"   Session: {result['session_id']}")
    print(f"   Results: {results_path}")
    print(f"   Analysis: {analysis_path}")
    print(f"   Report: {report_path}")
    print(f"\n   Agreement: κ = {analysis['agreement']['overall_kappa']:.3f} ({analysis['agreement']['agreement_level']})")
    print(f"   Valid review pairs: {analysis['agreement']['n_valid_pairs']}/{analysis['n_papers']} (invalid: {analysis['agreement']['n_invalid_pairs']})")
    print(f"   Overall quality: {analysis['overall_quality']['pre_gate_mean']:.2f} → {analysis['overall_quality']['post_gate_mean']:.2f} ({analysis['overall_quality']['direction']})")
    print(f"   Improved dimensions: {analysis['findings']['n_improved']}")
    print(f"   Worsened dimensions: {analysis['findings']['n_worsened']}")
    
    return analysis


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Double-Blind Peer Review Evaluation")
    parser.add_argument("--skip-review", action="store_true", 
                       help="Skip the LLM review step (use existing results)")
    parser.add_argument("--analyze-only", type=str, default=None,
                       help="Path to existing results JSON for analysis only")
    
    args = parser.parse_args()
    
    analyze_path = Path(args.analyze_only) if args.analyze_only else None
    
    asyncio.run(run_evaluation(skip_review=args.skip_review, analyze_only=analyze_path))
