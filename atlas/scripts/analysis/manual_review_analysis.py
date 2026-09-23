#!/usr/bin/env python3

"""
Manual Review Analysis - Detailed analysis of remaining blocking I/O patterns
"""

import os
import re
import ast
from pathlib import Path

def analyze_blocking_patterns(filepath):
    """Analyze specific blocking patterns in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip if no async functions
        if 'async def' not in content:
            return None

        issues = []

        # Check for time.sleep (should be none now)
        if 'time.sleep' in content:
            issues.append({
                'pattern': 'time.sleep',
                'severity': 'critical',
                'description': 'time.sleep blocks event loop'
            })

        # Check for requests usage
        if 'requests.' in content and 'httpx' not in content:
            issues.append({
                'pattern': 'requests.*',
                'severity': 'high',
                'description': 'requests library is blocking - should use httpx'
            })

        # Check for open() usage
        if 'open(' in content and 'aiofiles' not in content:
            issues.append({
                'pattern': 'open(.*)',
                'severity': 'medium',
                'description': 'open() is blocking - should use aiofiles.open()'
            })

        # Check for urllib usage
        if 'urllib' in content and 'httpx' not in content:
            issues.append({
                'pattern': 'urllib.*',
                'severity': 'high',
                'description': 'urllib is blocking - should use httpx'
            })

        # Check for JSON operations
        if ('json.load' in content or 'json.dump' in content) and 'asyncio' not in content:
            issues.append({
                'pattern': r'json\.(load|dump)',
                'severity': 'low',
                'description': 'JSON operations could be async but not critical'
            })

        # Check for file operations without aiofiles
        file_ops = ['open(', 'read(', 'write(', 'close(']
        for op in file_ops:
            if op in content and 'aiofiles' not in content and op == 'open(':
                # Count occurrences
                count = content.count(op)
                if count > 0:
                    issues.append({
                        'pattern': op,
                        'severity': 'medium',
                        'description': f'{count} file operations without aiofiles'
                    })
                break

        if issues:
            return {
                'filepath': filepath,
                'issues': issues,
                'has_async': True,
                'priority': max((issue['severity'] for issue in issues), key=lambda x: ['low', 'medium', 'high', 'critical'].index(x))
            }

    except Exception as e:
        return {
            'filepath': filepath,
            'error': str(e),
            'issues': [],
            'has_async': False
        }

    return None

def main():
    """Analyze remaining files with blocking I/O."""
    print("🔍 MANUAL REVIEW ANALYSIS")
    print("=" * 50)
    print("Analyzing specific blocking patterns in remaining 83 files...")

    # Get the list of problematic files from the verification scan
    problematic_files = [
        "app/routers/system.py",
        "app/routers/run_multiple_scientific_experiments.py",
        "app/routers/publications.py",
        "app/routers/run_comprehensive_scientific_experiments.py",
        "app/routers/sandbox_executor.py",
        "app/routers/run_advanced_scientific_tools.py",
        "app/routers/conjectures.py",
        "app/routers/earth_sciences_light.py",
        "app/connectors/astronomical_data_connector.py",
        "app/middleware/profiling.py",
        "app/domains/astronomy/routers/api.py",
        "app/domains/astronomy/services/integrated_astronomy_pipeline.py",
        "app/domains/chemistry/routers/api.py",
        "app/domains/chemistry/analytical/differential_scanning_calorimetry_service.py",
        "app/domains/chemistry/services/differential_scanning_calorimetry_service.py",
        "app/domains/mathematics/routers/api.py",
        "app/domains/medicine/advanced_clinical_validation_service.py",
        "app/domains/medicine/routers/api.py",
        "app/domains/medicine/registry/medicine_registry_old.py",
        "app/domains/medicine/registry/medicine_registry_clean.py",
        "app/domains/medicine/registry/medicine_registry.py",
        "app/domains/medicine/services/websocket_handler.py",
        "app/domains/medicine/services/medical_realtime_service.py",
        "app/domains/physics/routers/api.py",
        "app/domains/physics/services/particle_physics_service.py",
        "app/domains/physics/quantum/particle_physics_service.py",
        "app/domains/engineering/routers/core/api.py",
        "app/domains/engineering/services/hardware_abstraction_service.py",
        "app/domains/biology/routers/api.py",
        "app/core/metrics.py",
        "app/core/cache.py",
        "app/cache/unified_cache.py",
        "app/distributed/distributed_scaling_manager.py",
        "app/distributed/scalability.py",
        "app/config/database_config.py",
        "app/security/security_dashboard.py",
        "app/security/audit_logger.py",
        "app/security/integrity_verification.py",
        "app/adapters/tool_adapter.py",
        "app/monitoring/automated_alerts.py",
        "app/monitoring/service_profiler.py",
        "app/monitoring/async_metrics.py",
        "app/infrastructure/service_registry_discovery.py",
        "app/services/experiment_scheduler_service.py",
        "app/services/iterative_improvement_service.py",
        "app/services/scientific_data_lake_service.py",
        "app/services/ai_scientist_service.py",
        "app/services/supplementary_materials_generator.py",
        "app/services/model_management_service.py",
        "app/services/mlflow_auto_promotion_service.py",
        "app/services/cost_metrics_service.py",
        "app/services/scientific_figure_generator.py",
        "app/services/cvc5_service.py",
        "app/services/molecular_dynamics.py",
        "app/services/code_scientist_service.py",
        "app/services/reproducibility.py",
        "app/services/experiment_scheduler_service_v2.py",
        "app/services/agent2_bridge_service.py",
        "app/services/domain_templates_service.py",
        "app/services/experiment_scheduler_v3.py",
        "app/services/multi_agent_coordinator.py",
        "app/services/literature_mining_service.py",
        "app/services/local_llm_service.py",
        "app/services/circuit_breaker_service.py",
        "app/services/reproducibility_database.py",
        "app/services/ollama_service.py",
        "app/services/tool_evidence_orchestrator.py",
        "app/services/literature_search.py",
        "app/services/scientific_hypothesis_agent.py",
        "app/services/publication_generator.py",
        "app/services/experimental_protocols.py",
        "app/services/master_orchestration_service_cleaned.py",
        "app/services/master_orchestration_service.py",
        "app/services/multimodal_reasoning_service.py",
        "app/services/data_versioning.py",
        "app/services/lean4_installer_improved.py",
        "app/services/sandbox_executor_service.py",
        "app/services/theorem_proving/lean4_integration.py",
        "app/services/orchestration/monitoring/__init__.py",
        "app/validation/blockchain_validation.py",
        "app/advanced_ops/advanced_fastapi_operations.py"
    ]

    analysis_results = []
    critical_issues = []
    high_issues = []
    medium_issues = []

    print(f"\nProcessing {len(problematic_files)} files...")

    for filepath in problematic_files:
        if os.path.exists(filepath):
            result = analyze_blocking_patterns(filepath)
            if result:
                analysis_results.append(result)

                # Categorize by severity
                for issue in result['issues']:
                    if issue['severity'] == 'critical':
                        critical_issues.append(result)
                    elif issue['severity'] == 'high':
                        high_issues.append(result)
                    elif issue['severity'] == 'medium':
                        medium_issues.append(result)

    print("\n📊 ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Files analyzed: {len(analysis_results)}")
    print(f"Files with critical issues: {len(critical_issues)}")
    print(f"Files with high priority issues: {len(high_issues)}")
    print(f"Files with medium priority issues: {len(medium_issues)}")

    if critical_issues:
        print("\n🚨 CRITICAL ISSUES (Require immediate attention):")
        for result in critical_issues[:5]:  # Show top 5
            print(f"  • {result['filepath']}")
            for issue in result['issues']:
                print(f"    - {issue['description']}")

    if high_issues:
        print("\n⚠️  HIGH PRIORITY ISSUES (Should be addressed):")
        for result in high_issues[:10]:  # Show top 10
            print(f"  • {result['filepath']}")
            for issue in result['issues']:
                if issue['severity'] == 'high':
                    print(f"    - {issue['description']}")

    if medium_issues:
        print("\n📝 MEDIUM PRIORITY ISSUES (Optional improvements):")
        medium_count = len(medium_issues)
        print(f"  • {medium_count} files with file operations that could use aiofiles")

    print("\n💡 RECOMMENDATIONS:")
    print("• Critical issues: Fix immediately (time.sleep blocks event loop)")
    print("• High priority: Replace blocking HTTP requests with httpx")
    print("• Medium priority: Consider aiofiles for file operations when convenient")
    print("• Low priority: JSON operations are minor and can remain as-is")

    # Save detailed analysis
    with open("scripts/analysis/manual_review_analysis.json", 'w') as f:
        import json
        json.dump({
            'summary': {
                'files_analyzed': len(analysis_results),
                'critical_issues': len(critical_issues),
                'high_issues': len(high_issues),
                'medium_issues': len(medium_issues)
            },
            'results': analysis_results
        }, f, indent=2)

    print("\n📄 Detailed analysis saved to: scripts/analysis/manual_review_analysis.json")
    return len(critical_issues), len(high_issues), len(medium_issues)

if __name__ == "__main__":
    critical, high, medium = main()
    if critical == 0:
        print("\n✅ GOOD NEWS: No critical blocking issues found!")
    else:
        print(f"\n⚠️  {critical} critical issues require immediate attention")
