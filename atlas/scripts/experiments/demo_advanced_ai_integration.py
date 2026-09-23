#!/usr/bin/env python3
"""
AXIOM META 4.1 - Advanced AI Integration Demo
Test real API integrations with 2024-2025 vanguard scientific tools.

Este demo muestra:
1. Literatura científica via arXiv API v2
2. Descubrimiento de materiales via Materials Project
3. Templates cuánticos optimizados (Qiskit v2.x)
4. Targets biomoleculares AlphaFold3 de alta incertidumbre
5. Regiones de anomalías climáticas (Earth Engine proxy)
6. Integración completa en loops autónomos

Ejecutar: python demo_advanced_ai_integration.py
"""

import sys
import json
import time
import asyncio
from pathlib import Path
from typing import List

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

async def test_advanced_apis():
    """Test all advanced APIs with real integrations."""
    print("🚀 AXIOM META 4.1 - Advanced AI Integration Demo")
    print("=" * 60)

    try:
        from app.autonomous.interfaces.external_apis import (
            fetch_literature_snippets,
            fetch_material_candidates,
            fetch_quantum_circuit_templates,
            fetch_biomolecular_targets,
            fetch_climate_anomaly_regions
        )

        results = {}

        # Test 1: Literature Mining (arXiv API v2)
        print("\n1. 📚 Testing arXiv Literature Mining...")
        lit_results = await fetch_literature_snippets("machine learning quantum chemistry", limit=3)
        print(f"   Found {len(lit_results)} papers:")
        for paper in lit_results[:2]:
            print(f"   • {paper['title'][:80]}...")
            print(f"     arXiv ID: {paper.get('arxiv_id', 'N/A')}, Citations: {paper.get('citation_count', 0)}")
        results['literature'] = len(lit_results)

        # Test 2: Materials Discovery (Materials Project API)
        print("\n2. 🔬 Testing Materials Project Integration...")
        mat_results = await fetch_material_candidates("Li2O", limit=3)
        print(f"   Found {len(mat_results)} materials:")
        for material in mat_results:
            formula = material.get('formula', 'Unknown')
            stability = material.get('predicted_stability', 0)
            source = material.get('source', 'unknown')
            print(f"   • {formula}: stability={stability:.3f} (source: {source})")
        results['materials'] = len(mat_results)

        # Test 3: Quantum Circuit Templates (Qiskit v2.x)
        print("\n3. ⚛️  Testing Quantum Circuit Templates...")
        quantum_results = fetch_quantum_circuit_templates(limit=3)
        print(f"   Found {len(quantum_results)} circuit templates:")
        for circuit in quantum_results:
            name = circuit.get('name', 'Unknown')
            depth = circuit.get('depth', 0)
            gates = circuit.get('two_qubit_gates', 0)
            efficiency = circuit.get('hardware_efficiency', 0)
            print(f"   • {name}: depth={depth}, 2Q-gates={gates}, efficiency={efficiency:.2f}")
        results['quantum'] = len(quantum_results)

        # Test 4: Biomolecular Targets (AlphaFold3 Integration)
        print("\n4. 🧬 Testing AlphaFold3 High-Uncertainty Targets...")
        bio_results = fetch_biomolecular_targets(limit=3)
        print(f"   Found {len(bio_results)} high-uncertainty targets:")
        for target in bio_results:
            uniprot = target.get('uniprot', 'Unknown')
            gene = target.get('gene_name', target.get('uniprot', 'N/A'))
            uncertainty = target.get('uncertainty', 0)
            plddt = target.get('avg_plddt', 0)
            print(f"   • {gene} ({uniprot}): uncertainty={uncertainty:.2f}, pLDDT={plddt:.1f}")
        results['biology'] = len(bio_results)

        # Test 5: Climate Anomaly Regions (Earth Engine proxy)
        print("\n5. 🌍 Testing Climate Anomaly Detection...")
        climate_results = fetch_climate_anomaly_regions(limit=3)
        print(f"   Found {len(climate_results)} anomaly regions:")
        for region in climate_results:
            region_id = region.get('region_id', 'Unknown')
            anomaly_type = region.get('anomaly_type', 'unknown')
            severity = region.get('severity', 0)
            impact = region.get('impact_score', 0)
            print(f"   • {region_id}: {anomaly_type}, severity={severity:.2f}, impact={impact:.2f}")
        results['climate'] = len(climate_results)

        # Summary
        print("\n" + "=" * 60)
        print("📊 API Integration Results:")
        total_data_points = sum(results.values())
        for domain, count in results.items():
            print(f"   {domain.capitalize()}: {count} data points")
        print(f"\nTotal scientific data points retrieved: {total_data_points}")

        return results

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory.")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_loop_integrations():
    """Test integration with autonomous loops."""
    print("\n🔄 Testing Loop Integrations...")
    print("-" * 40)

    try:
        from app.autonomous.pipelines.climate_loop import ClimateLoop
        from app.autonomous.pipelines.biology_loop import BiologyLoop
        from app.autonomous.pipelines.mathematics_loop import MathematicsLoop
        from app.autonomous.metrics.telemetry_collector import AutonomousTelemetry

        # Test Climate Loop with real data
        print("\n🌍 Climate Loop Integration:")
        climate_loop = ClimateLoop(telemetry=AutonomousTelemetry())
        climate_result = climate_loop.run_iteration(top_n=2)
        print(f"   Processed {len(climate_result.get('selected', []))} climate regions")
        climate_novelty: List[float] = []
        for outcome in climate_result.get('outcomes', {}).values():
            if isinstance(outcome, dict):
                novelty = outcome.get('novelty_score')
                if isinstance(novelty, (int, float)):
                    climate_novelty.append(float(novelty))
        if climate_novelty:
            print(f"   Average novelty: {sum(climate_novelty) / len(climate_novelty):.3f}")
        else:
            print("   Average novelty: N/A")

        # Test Biology Loop with real data
        print("\n🧬 Biology Loop Integration:")
        biology_loop = BiologyLoop(telemetry=AutonomousTelemetry())
        biology_result = biology_loop.run_iteration(top_n=2)
        print(f"   Analyzed {len(biology_result.get('selected', []))} protein targets")
        biology_novelty: List[float] = []
        for outcome in biology_result.get('outcomes', {}).values():
            if isinstance(outcome, dict):
                novelty = outcome.get('novelty_score')
                if isinstance(novelty, (int, float)):
                    biology_novelty.append(float(novelty))
        if biology_novelty:
            print(f"   Average novelty: {sum(biology_novelty) / len(biology_novelty):.3f}")
        else:
            print("   Average novelty: N/A")
        print("\n🔢 Mathematics Loop Integration:")
        math_loop = MathematicsLoop(telemetry=AutonomousTelemetry())

        def math_provider():
            return [
                {
                    'id': 'riemann_demo',
                    'statement': 'Los ceros críticos de ζ(s) se concentran en Re(s)=1/2.',
                    'domain': 'number_theory',
                    'metadata': {'source': 'demo', 'topic': 'prime_distribution'},
                },
                {
                    'id': 'prime_gap_bounds',
                    'statement': 'Existen infinitos primos consecutivos separados por menos de log(n)^2.',
                    'domain': 'number_theory',
                    'metadata': {'source': 'demo', 'topic': 'prime_gaps'},
                },
            ]

        math_loop.provider = math_provider
        math_result = math_loop.run_iteration(iteration=1, limit=3, domain='number_theory')
        print(f"   Evaluated {len(math_result.get('selected', []))} mathematical conjectures")
        math_novelty: List[float] = []
        for outcome in math_result.get('outcomes', {}).values():
            if isinstance(outcome, dict):
                novelty = outcome.get('novelty_score')
                if isinstance(novelty, (int, float)):
                    math_novelty.append(float(novelty))
        if math_novelty:
            print(f"   Average novelty: {sum(math_novelty) / len(math_novelty):.3f}")
        else:
            print("   Average novelty: N/A")

        return {"climate": climate_result, "biology": biology_result, "mathematics": math_result}

    except Exception as e:
        print(f"❌ Loop integration error: {e}")
        return None


def demonstrate_full_pipeline():
    """Demonstrate full scientific discovery pipeline."""
    print("\n🔬 Full Scientific Discovery Pipeline Demo")
    print("-" * 50)

    start_time = time.time()

    # Phase 1: API Integration Test
    # Run async test in its own event loop
    api_results = asyncio.run(test_advanced_apis())
    if not api_results:
        return False
        
    # Phase 2: Loop Integration Test
    # Run sync test (which manages its own loops)
    loop_results = test_loop_integrations()
    if not loop_results:
        return False
        
    # Phase 3: Performance Metrics
    elapsed_time = time.time() - start_time
    print("\n⚡ Performance Metrics:")
    print(f"   Total execution time: {elapsed_time:.2f}s")
    print(f"   API calls completed: {sum(api_results.values())}")
    print(f"   Loop iterations: {len(loop_results)}")
    # Phase 4: Export Results
    export_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "api_results": api_results,
        "loop_results": {
            k: {"iteration": v.get("iteration"), "selected_count": len(v.get("selected", []))}
            for k, v in loop_results.items()
        },
        "performance": {
            "execution_time_s": elapsed_time,
            "total_api_calls": sum(api_results.values()),
            "loop_iterations": len(loop_results)
        }
    }
    # Save results
    output_file = f"axiom_meta_41_demo_results_{int(time.time())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)
    print(f"💾 Results exported to: {output_file}")
    return True


if __name__ == "__main__":
    print("Starting AXIOM META 4.1 Advanced AI Integration Demo...")

    success = demonstrate_full_pipeline()

    if success:
        print("\n✅ AXIOM META 4.1 Demo completed successfully!")
        print("\n🚀 Ready for Phase 5: Advanced AI Integration")
        print("\nNext steps:")
        print("  • Configure API keys for full functionality")
        print("  • Deploy to production environment")
        print("  • Enable continuous integration monitoring")
        print("  • Scale to multi-agent orchestration")
    else:
        print("\n❌ Demo encountered errors. Check configuration and dependencies.")

    print("\n" + "=" * 60)
