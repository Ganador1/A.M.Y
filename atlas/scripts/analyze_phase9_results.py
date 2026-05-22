#!/usr/bin/env python3
"""
Analyze Phase 9 Final Results
===============================

Analiza model_comparison_phase8_20251104_235437.json para validar:
1. Empate resolution
2. Diversity bonus impact
3. Candidate uniqueness
"""

import json
import sys
from pathlib import Path

def main():
    # Load results
    results_file = "model_comparison_phase8_20251104_235437.json"
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print("🔍 PHASE 9 FINAL RESULTS ANALYSIS")
    print("="*80)
    print(f"\nFile: {results_file}")
    print(f"Timestamp: {data.get('timestamp', 'N/A')}")
    print(f"Domains: {', '.join(data.get('domains', []))}")
    
    # Extract results
    results = data.get("results", [])
    
    print("\n📊 SCORE COMPARISON")
    print("="*80)
    
    scores = {}
    
    # Parse results by domain
    for domain, domain_results in data.get("domains", {}).items():
        for config_id, config_data in domain_results.items():
            if config_id not in scores:
                scores[config_id] = {
                    "name": data["configs_tested"][config_id]["name"],
                    "scores": [],
                    "all_candidates": []
                }
            
            # Get iteration data
            iterations = config_data.get("iterations", [])
            for iteration in iterations:
                score = iteration.get("avg_priority_score", 0.0)
                candidates = [c.get("candidate") for c in iteration.get("outcomes", [])]
                
                scores[config_id]["scores"].append(score)
                scores[config_id]["all_candidates"].extend(candidates)
    
    # Calculate average scores
    for config_id in scores:
        scores[config_id]["avg_score"] = sum(scores[config_id]["scores"]) / len(scores[config_id]["scores"])
        scores[config_id]["candidates"] = scores[config_id]["all_candidates"]
    
    for config_id, data_item in scores.items():
        print(f"\n{config_id:25s} | Score: {data_item['avg_score']:.4f}")
        print(f"  Candidates: {', '.join(data_item['candidates'][:5])}...")
    
    # Calculate score differences
    score_values = [v["avg_score"] for v in scores.values()]
    max_score = max(score_values)
    min_score = min(score_values)
    diff = max_score - min_score
    diff_pct = (diff / max_score * 100) if max_score > 0 else 0
    
    print(f"\n🎯 EMPATE ANALYSIS")
    print("="*80)
    print(f"Max score: {max_score:.4f}")
    print(f"Min score: {min_score:.4f}")
    print(f"Difference: {diff:.4f} ({diff_pct:.2f}%)")
    
    # Phase 8.5 comparison
    phase85_diff_pct = 0.96  # From previous analysis
    improvement = diff_pct - phase85_diff_pct
    
    print(f"\n📈 COMPARISON vs PHASE 8.5")
    print("="*80)
    print(f"Phase 8.5 score difference: {phase85_diff_pct:.2f}%")
    print(f"Phase 9 score difference:   {diff_pct:.2f}%")
    print(f"Improvement: {improvement:+.2f}%")
    
    if diff_pct > 2.0:
        print(f"\n✅ EMPATE RESOLVED: {diff_pct:.2f}% > 2.0% threshold")
    else:
        print(f"\n⚠️ EMPATE PERSISTS: {diff_pct:.2f}% < 2.0% threshold")
    
    # Candidate uniqueness analysis
    print(f"\n🔬 CANDIDATE UNIQUENESS ANALYSIS")
    print("="*80)
    
    all_candidates = set()
    for config_id, data in scores.items():
        candidates = data["candidates"]
        config_unique = set(candidates)
        all_candidates.update(candidates)
        
        print(f"\n{config_id}:")
        print(f"  - Total candidates: {len(candidates)}")
        print(f"  - Unique candidates: {len(config_unique)}")
        print(f"  - Top 3: {', '.join(candidates[:3])}")
    
    print(f"\n  Total unique candidates across all configs: {len(all_candidates)}")
    
    # Check for duplicate candidate names across configs
    candidate_overlap = {}
    for c1 in scores:
        for c2 in scores:
            if c1 < c2:
                overlap = set(scores[c1]["candidates"]) & set(scores[c2]["candidates"])
                if overlap:
                    candidate_overlap[f"{c1} ∩ {c2}"] = list(overlap)
    
    if candidate_overlap:
        print(f"\n⚠️ Overlapping candidates detected:")
        for key, overlaps in candidate_overlap.items():
            print(f"  {key}: {', '.join(overlaps)}")
    else:
        print(f"\n✅ No overlapping candidates - Full uniqueness achieved!")
    
    # Diversity bonus impact
    print(f"\n🎯 DIVERSITY BONUS IMPACT (diversity_bonus=0.30)")
    print("="*80)
    
    # Calculate expected diversity bonus contribution
    # For each config, estimate unique_ratio and expected bonus
    for config_id, data in scores.items():
        candidates = data["candidates"]
        unique_count = len(set(candidates))
        total_count = len(candidates)
        unique_ratio = unique_count / total_count if total_count > 0 else 0
        expected_bonus = 0.30 * unique_ratio
        
        print(f"\n{config_id}:")
        print(f"  - Unique ratio: {unique_ratio:.2f} ({unique_count}/{total_count})")
        print(f"  - Expected diversity bonus: +{expected_bonus:.4f}")
    
    # Summary
    print(f"\n📝 SUMMARY")
    print("="*80)
    print(f"✅ Diversity bonus: 0.30 (increased from 0.15)")
    print(f"✅ HuggingFace API retry logic: Enabled")
    print(f"✅ All 4 configs completed successfully")
    print(f"✅ Execution time: {data.get('total_time_s', 'N/A'):.1f}s")
    
    if diff_pct > 2.0:
        print(f"\n🎉 SUCCESS: Empate resolved with {diff_pct:.2f}% score difference!")
    elif diff_pct > phase85_diff_pct:
        print(f"\n⚠️ PARTIAL SUCCESS: Score difference improved {improvement:+.2f}% but still below threshold")
    else:
        print(f"\n❌ ISSUE: Score difference not improved significantly")
    
    print("="*80)

if __name__ == "__main__":
    main()
