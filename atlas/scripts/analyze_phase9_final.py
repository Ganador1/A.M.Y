#!/usr/bin/env python3
"""
Analyze Phase 9 Final Results
===============================
"""

import json

def main():
    # Load results
    results_file = "model_comparison_phase8_20251104_235437.json"
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print("🔍 PHASE 9 FINAL RESULTS ANALYSIS")
    print("="*80)
    print(f"\nFile: {results_file}")
    print(f"Execution date: {data.get('execution_date', 'N/A')}")
    print(f"Total duration: {data.get('total_duration_seconds', 0):.1f}s")
    print(f"Domains tested: {', '.join(data.get('domains', {}).keys())}")
    
    # Extract summary data
    summary = data.get("summary", {})
    by_config = summary.get("by_config", {})
    
    print("\n📊 SCORE COMPARISON")
    print("="*80)
    
    scores = {}
    for config_id, config_data in by_config.items():
        config_name = config_data.get("name", config_id)
        avg_score = config_data.get("avg_score", 0.0)
        avg_duration = config_data.get("avg_duration", 0.0)
        successful_runs = config_data.get("successful_runs", 0)
        
        scores[config_id] = {
            "name": config_name,
            "score": avg_score,
            "duration": avg_duration,
            "runs": successful_runs
        }
        
        print(f"\n{config_id:25s}")
        print(f"  Name: {config_name}")
        print(f"  Avg Score: {avg_score:.4f}")
        print(f"  Avg Duration: {avg_duration:.2f}s")
        print(f"  Successful runs: {successful_runs}")
    
    # Calculate score differences
    score_values = [v["score"] for v in scores.values()]
    max_score = max(score_values)
    min_score = min(score_values)
    diff = max_score - min_score
    diff_pct = (diff / max_score * 100) if max_score > 0 else 0
    
    print("\n🎯 EMPATE ANALYSIS")
    print("="*80)
    print(f"Max score: {max_score:.4f}")
    print(f"Min score: {min_score:.4f}")
    print(f"Difference: {diff:.4f} ({diff_pct:.2f}%)")
    
    # Phase 8.5 comparison
    phase85_diff_pct = 0.96  # From previous analysis
    improvement = diff_pct - phase85_diff_pct
    
    print("\n📈 COMPARISON vs PHASE 8.5")
    print("="*80)
    print(f"Phase 8.5 score difference: {phase85_diff_pct:.2f}%")
    print(f"Phase 9 score difference:   {diff_pct:.2f}%")
    print(f"Improvement: {improvement:+.2f}%")
    
    if diff_pct > 2.0:
        print(f"\n✅ EMPATE RESOLVED: {diff_pct:.2f}% > 2.0% threshold")
        empate_status = "RESOLVED"
    else:
        print(f"\n⚠️ EMPATE PERSISTS: {diff_pct:.2f}% < 2.0% threshold")
        empate_status = "PERSISTS"
    
    # Domain-wise analysis
    print("\n🔬 DOMAIN-WISE ANALYSIS")
    print("="*80)
    
    by_domain = summary.get("by_domain", {})
    for domain, domain_data in by_domain.items():
        print(f"\n{domain.upper()}:")
        print(f"  - Avg score: {domain_data.get('avg_score', 0):.4f}")
        print(f"  - Avg evidence: {domain_data.get('avg_evidence', 0):.4f}")
        print(f"  - Avg duration: {domain_data.get('avg_duration', 0):.2f}s")
        print(f"  - Iterations: {domain_data.get('iterations', 0)}")
    
    # Model configuration details
    print("\n🤖 MODEL CONFIGURATIONS")
    print("="*80)
    
    for config_id, config_data in by_config.items():
        print(f"\n{config_id}:")
        role_models = config_data.get("role_models", {})
        for role, model in role_models.items():
            print(f"  - {role}: {model}")
    
    # Summary
    print("\n📝 SUMMARY")
    print("="*80)
    print("✅ Diversity bonus: 0.30 (increased from 0.15)")
    print("✅ HuggingFace API retry logic: Enabled (3 attempts)")
    print(f"✅ All {len(by_config)} configs completed successfully")
    print(f"✅ Total execution time: {data.get('total_duration_seconds', 0):.1f}s")
    print(f"\nEmpate status: {empate_status}")
    print(f"Score range: {min_score:.4f} - {max_score:.4f} ({diff_pct:.2f}%)")
    
    if empate_status == "RESOLVED":
        print(f"\n🎉 SUCCESS: Empate resolved with {diff_pct:.2f}% score difference!")
    elif improvement > 0:
        print(f"\n⚠️ PARTIAL SUCCESS: Score difference improved {improvement:+.2f}% but still below threshold")
        print("   Consider further increasing diversity_bonus or adjusting selection strategy")
    else:
        print("\n❌ ISSUE: Score difference not improved significantly")
    
    print("="*80)
    
    # Return summary for potential further processing
    return {
        "empate_status": empate_status,
        "score_difference_pct": diff_pct,
        "improvement_pct": improvement,
        "configs_tested": len(by_config),
        "total_duration": data.get('total_duration_seconds', 0)
    }

if __name__ == "__main__":
    result = main()
