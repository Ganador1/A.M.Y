#!/usr/bin/env python3
"""
Analyze Phase 9 Results - All Domains
======================================

Analiza resultados completos de Phase 9 con todos los dominios
para determinar el mejor modelo para producción.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

def load_latest_results():
    """Find and load the latest results file"""
    results_files = sorted(Path('.').glob('model_comparison_phase8_*.json'))
    if not results_files:
        print("❌ No results files found!")
        sys.exit(1)
    
    latest = results_files[-1]
    print(f"📂 Loading: {latest}")
    
    with open(latest, 'r', encoding='utf-8') as f:
        return json.load(f), latest.name

def analyze_results(data, filename):
    """Analyze and generate comprehensive report"""
    
    print("\n" + "="*100)
    print("🔬 PHASE 9 - COMPREHENSIVE ANALYSIS (ALL DOMAINS)")
    print("="*100)
    
    print(f"\n📊 Execution Summary")
    print(f"{'='*100}")
    print(f"File: {filename}")
    print(f"Execution date: {data.get('execution_date', 'N/A')}")
    print(f"Total duration: {data.get('total_duration_seconds', 0):.1f}s")
    
    # Get domains and configs
    summary = data.get('summary', {})
    by_config = summary.get('by_config', {})
    by_domain = summary.get('by_domain', {})
    
    domains = list(by_domain.keys())
    configs = list(by_config.keys())
    
    print(f"Domains tested: {', '.join(domains)}")
    print(f"Configurations tested: {len(configs)}")
    
    # Configuration-wise analysis
    print(f"\n{'='*100}")
    print(f"📊 CONFIGURATION COMPARISON (Average across all domains)")
    print(f"{'='*100}\n")
    
    config_scores = {}
    for config_id, config_data in by_config.items():
        config_name = config_data.get('name', config_id)
        avg_score = config_data.get('avg_score', 0.0)
        avg_duration = config_data.get('avg_duration', 0.0)
        successful_runs = config_data.get('successful_runs', 0)
        
        config_scores[config_id] = {
            'name': config_name,
            'score': avg_score,
            'duration': avg_duration,
            'runs': successful_runs,
            'role_models': config_data.get('role_models', {})
        }
        
        print(f"{config_id:25s}")
        print(f"  Name: {config_name}")
        print(f"  Avg Score: {avg_score:.4f}")
        print(f"  Avg Duration: {avg_duration:.2f}s")
        print(f"  Successful runs: {successful_runs}/{len(domains)}")
        print()
    
    # Ranking
    sorted_configs = sorted(config_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    
    print(f"{'='*100}")
    print(f"🏆 CONFIGURATION RANKING")
    print(f"{'='*100}\n")
    
    for rank, (config_id, data) in enumerate(sorted_configs, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"  {rank}."
        print(f"{medal} {config_id:25s} Score: {data['score']:.4f}  Duration: {data['duration']:.2f}s")
    
    # Score difference analysis
    scores = [v['score'] for v in config_scores.values()]
    max_score = max(scores)
    min_score = min(scores)
    diff = max_score - min_score
    diff_pct = (diff / max_score * 100) if max_score > 0 else 0
    
    print(f"\n{'='*100}")
    print(f"🎯 EMPATE ANALYSIS")
    print(f"{'='*100}\n")
    print(f"Max score: {max_score:.4f}")
    print(f"Min score: {min_score:.4f}")
    print(f"Difference: {diff:.4f} ({diff_pct:.2f}%)")
    
    threshold = 2.0
    if diff_pct > threshold:
        print(f"\n✅ EMPATE RESOLVED: {diff_pct:.2f}% > {threshold}% threshold")
        empate_status = "RESOLVED"
    else:
        print(f"\n⚠️ EMPATE PERSISTS: {diff_pct:.2f}% < {threshold}% threshold")
        empate_status = "PERSISTS"
    
    # Domain-wise analysis
    print(f"\n{'='*100}")
    print(f"🔬 DOMAIN-WISE PERFORMANCE")
    print(f"{'='*100}\n")
    
    for domain, domain_data in by_domain.items():
        print(f"{domain.upper():15s}:")
        print(f"  - Avg score: {domain_data.get('avg_score', 0):.4f}")
        print(f"  - Avg evidence: {domain_data.get('avg_evidence', 0):.4f}")
        print(f"  - Avg duration: {domain_data.get('avg_duration', 0):.2f}s")
        print(f"  - Iterations: {domain_data.get('iterations', 0)}")
        print()
    
    # Find best config per domain from detailed results
    print(f"{'='*100}")
    print(f"🎯 BEST CONFIGURATION PER DOMAIN")
    print(f"{'='*100}\n")
    
    results = data.get('results', [])
    domain_best = defaultdict(lambda: {'score': 0, 'config': None})
    
    for result in results:
        domain = result.get('domain')
        config_id = result.get('config_id')
        score = result.get('avg_priority_score', 0)
        
        if score > domain_best[domain]['score']:
            domain_best[domain] = {'score': score, 'config': config_id}
    
    for domain in sorted(domain_best.keys()):
        best = domain_best[domain]
        config_name = config_scores.get(best['config'], {}).get('name', best['config'])
        print(f"{domain.upper():15s}: {best['config']:25s} (Score: {best['score']:.4f})")
    
    # Model configurations
    print(f"\n{'='*100}")
    print(f"🤖 MODEL CONFIGURATIONS")
    print(f"{'='*100}\n")
    
    for config_id, data in sorted_configs:
        print(f"{config_id}:")
        role_models = data['role_models']
        for role in ['orchestrator', 'bio_hypothesis', 'physchem_coder', 'reviewer', 'publisher']:
            if role in role_models:
                print(f"  • {role:20s}: {role_models[role]}")
        print()
    
    # Recommendations
    print(f"{'='*100}")
    print(f"💡 PRODUCTION RECOMMENDATIONS")
    print(f"{'='*100}\n")
    
    winner = sorted_configs[0]
    winner_id = winner[0]
    winner_data = winner[1]
    
    print(f"🏆 RECOMMENDED CONFIGURATION: {winner_id}")
    print(f"   Name: {winner_data['name']}")
    print(f"   Overall Score: {winner_data['score']:.4f}")
    print(f"   Avg Duration: {winner_data['duration']:.2f}s")
    print(f"   Success Rate: {winner_data['runs']}/{len(domains)} domains")
    print()
    
    print(f"📊 Key Strengths:")
    # Analyze which domains this config won
    domains_won = [d for d, b in domain_best.items() if b['config'] == winner_id]
    if domains_won:
        print(f"   • Won in domains: {', '.join([d.upper() for d in domains_won])}")
    print(f"   • Consistent performance across domains")
    print(f"   • {('Fast' if winner_data['duration'] < 5 else 'Moderate')} execution time")
    print()
    
    # Alternative recommendations
    if len(sorted_configs) > 1:
        runner_up = sorted_configs[1]
        runner_id = runner_up[0]
        runner_data = runner_up[1]
        
        print(f"🥈 ALTERNATIVE: {runner_id}")
        print(f"   Name: {runner_data['name']}")
        print(f"   Score: {runner_data['score']:.4f} (Δ{abs(winner_data['score'] - runner_data['score']):.4f})")
        print(f"   Duration: {runner_data['duration']:.2f}s")
        print()
    
    # Deployment checklist
    print(f"{'='*100}")
    print(f"✅ DEPLOYMENT CHECKLIST")
    print(f"{'='*100}\n")
    
    checklist_items = [
        (empate_status == "RESOLVED", "Empate resolved (score difference >2%)"),
        (all(data['runs'] >= len(domains) for data in config_scores.values()), "All configs completed successfully"),
        (max(data['duration'] for data in config_scores.values()) < 30, "Execution times acceptable (<30s)"),
        (len(domains) == 4, "All 4 domains tested"),
    ]
    
    for status, item in checklist_items:
        icon = "✅" if status else "⚠️"
        print(f"{icon} {item}")
    
    print(f"\n{'='*100}")
    print(f"📝 SUMMARY")
    print(f"{'='*100}\n")
    
    all_passed = all(status for status, _ in checklist_items)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - READY FOR PRODUCTION DEPLOYMENT")
    else:
        print("⚠️ SOME CHECKS FAILED - REVIEW REQUIRED BEFORE DEPLOYMENT")
    
    print(f"\nRecommended configuration: {winner_id}")
    print(f"Empate status: {empate_status}")
    print(f"Score difference: {diff_pct:.2f}%")
    print(f"Total domains: {len(domains)}")
    print(f"Total configurations: {len(configs)}")
    print(f"\n{'='*100}")
    
    return {
        'winner': winner_id,
        'winner_score': winner_data['score'],
        'empate_status': empate_status,
        'score_difference_pct': diff_pct,
        'domains_tested': len(domains),
        'configs_tested': len(configs)
    }

def main():
    data, filename = load_latest_results()
    result = analyze_results(data, filename)
    
    # Save summary
    summary_file = filename.replace('.json', '_analysis_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Analysis summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
