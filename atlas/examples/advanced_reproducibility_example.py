"""
Advanced Reproducibility Example - AXIOM META 4
Demonstrates advanced reproducibility analysis with perturbation engine and database.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.active_reproducibility_engine import get_reproducibility_engine
from app.services.perturbation_engine import PerturbationEngine
from app.services.reproducibility_database import ReproducibilityDatabase


async def example_advanced_robustness_analysis():
    """Example of advanced robustness analysis"""
    print("🔬 Advanced Robustness Analysis Example...")
    
    engine = await get_reproducibility_engine()
    
    # Sample experiment configuration
    experiment_config = {
        "paper_id": "robustness_test_2025",
        "title": "Advanced Robustness Analysis Test",
        "experiment_type": "molecular_dynamics",
        "description": "Testing robustness of molecular dynamics simulations"
    }
    
    # Sample parameters for perturbation
    parameters = [
        {
            "name": "temperature",
            "min_value": 280.0,
            "max_value": 320.0,
            "default_value": 300.0,
            "unit": "K",
            "distribution": "gaussian",
            "std_dev": 5.0
        },
        {
            "name": "pressure",
            "min_value": 0.8,
            "max_value": 1.2,
            "default_value": 1.0,
            "unit": "atm",
            "distribution": "gaussian",
            "std_dev": 0.05
        },
        {
            "name": "timestep",
            "min_value": 0.001,
            "max_value": 0.005,
            "default_value": 0.002,
            "unit": "ps",
            "distribution": "uniform"
        }
    ]
    
    result = await engine.advanced_robustness_analysis({
        "experiment_config": experiment_config,
        "parameters": parameters,
        "num_iterations": 20
    })
    
    if result["success"]:
        print(f"✅ Advanced robustness analysis completed")
        print(f"📊 Robustness score: {result['robustness_metrics']['robustness_score']:.3f}")
        print(f"🎯 Success rate: {result['robustness_metrics']['successful_reproductions']}/{result['robustness_metrics']['total_experiments']}")
        print(f"⏱️ Average reproducibility score: {result['robustness_metrics']['average_reproducibility_score']:.3f}")
        print(f"💾 Database recorded: {result['database_recorded']}")
    else:
        print(f"❌ Robustness analysis failed: {result['error']}")


async def example_sensitivity_analysis():
    """Example of sensitivity analysis using perturbation engine"""
    print("\n📈 Sensitivity Analysis Example...")
    
    perturbation_engine = PerturbationEngine()
    
    # Sample parameters for sensitivity analysis
    parameters = [
        {
            "name": "concentration",
            "min_value": 0.1,
            "max_value": 10.0,
            "default_value": 1.0,
            "unit": "mM"
        },
        {
            "name": "pH",
            "min_value": 6.0,
            "max_value": 8.0,
            "default_value": 7.0,
            "unit": ""
        },
        {
            "name": "incubation_time",
            "min_value": 10,
            "max_value": 60,
            "default_value": 30,
            "unit": "minutes"
        }
    ]
    
    experimental_data = {
        "experiment_type": "enzyme_kinetics",
        "output_measurement": "reaction_rate",
        "expected_range": [0.1, 2.0]
    }
    
    result = await perturbation_engine.sensitivity_analysis({
        "action": "sensitivity_analysis",
        "parameters": parameters,
        "method": "sobol",
        "experimental_data": experimental_data,
        "num_samples": 500
    })
    
    if result["success"]:
        print(f"✅ Sensitivity analysis completed using {result['method']} method")
        print(f"📊 Total parameters analyzed: {result['interpretation']['total_parameters']}")
        print(f"🔴 High sensitivity parameters: {result['interpretation']['high_sensitivity_count']}")
        print(f"🟡 Moderate sensitivity parameters: {result['interpretation']['moderate_sensitivity_count']}")
        print(f"🟢 Low sensitivity parameters: {result['interpretation']['low_sensitivity_count']}")
        print(f"🎯 Overall robustness: {result['interpretation']['overall_robustness']}")
        print(f"⭐ Most sensitive parameter: {result['interpretation']['most_sensitive_parameter']}")
    else:
        print(f"❌ Sensitivity analysis failed: {result['error']}")


async def example_critical_conditions_detection():
    """Example of critical conditions detection"""
    print("\n⚠️ Critical Conditions Detection Example...")
    
    perturbation_engine = PerturbationEngine()
    
    # Sample parameters
    parameters = [
        {
            "name": "temperature",
            "min_value": 20.0,
            "max_value": 40.0,
            "default_value": 37.0,
            "unit": "°C"
        },
        {
            "name": "oxygen_concentration",
            "min_value": 5.0,
            "max_value": 21.0,
            "default_value": 20.0,
            "unit": "%"
        },
        {
            "name": "glucose_concentration",
            "min_value": 1.0,
            "max_value": 25.0,
            "default_value": 5.0,
            "unit": "mM"
        }
    ]
    
    experimental_data = {
        "experiment_type": "cell_culture",
        "output_measurement": "cell_viability",
        "critical_threshold": 0.8
    }
    
    result = await perturbation_engine.detect_critical_conditions({
        "action": "critical_conditions_detection",
        "experimental_data": experimental_data,
        "parameters": parameters,
        "threshold": 0.2
    })
    
    if result["success"]:
        print(f"✅ Critical conditions detection completed")
        print(f"🔍 Total parameters analyzed: {result['total_parameters']}")
        print(f"⚠️ Critical parameters found: {result['summary']['critical_count']}")
        print(f"🔴 High criticality parameters: {result['summary']['high_criticality_count']}")
        print(f"🔗 Significant interactions: {result['summary']['significant_interactions']}")
        
        if result["critical_parameters"]:
            print("\n📋 Critical Parameters:")
            for cp in result["critical_parameters"][:3]:  # Show top 3
                print(f"   - {cp['parameter']}: {cp['criticality_level']} criticality (sensitivity: {cp['sensitivity_index']:.3f})")
    else:
        print(f"❌ Critical conditions detection failed: {result['error']}")


async def example_failure_pattern_analysis():
    """Example of failure pattern analysis"""
    print("\n🔍 Failure Pattern Analysis Example...")
    
    # First, let's record some sample failed attempts
    reproducibility_db = ReproducibilityDatabase()
    
    # Record some sample failed attempts
    sample_failures = [
        {
            "attempt_id": "failure_001",
            "paper_id": "test_paper_1",
            "paper_title": "Test Paper 1",
            "experiment_type": "protein_folding",
            "parameters": {"temperature": 300, "pressure": 1.0, "timestep": 0.002},
            "success": False,
            "reproducibility_score": 0.3,
            "execution_time": 120.5,
            "error_message": "Convergence failure in energy minimization"
        },
        {
            "attempt_id": "failure_002",
            "paper_id": "test_paper_1",
            "paper_title": "Test Paper 1",
            "experiment_type": "protein_folding",
            "parameters": {"temperature": 300, "pressure": 1.0, "timestep": 0.002},
            "success": False,
            "reproducibility_score": 0.2,
            "execution_time": 95.2,
            "error_message": "Convergence failure in energy minimization"
        },
        {
            "attempt_id": "failure_003",
            "paper_id": "test_paper_2",
            "paper_title": "Test Paper 2",
            "experiment_type": "protein_folding",
            "parameters": {"temperature": 310, "pressure": 1.1, "timestep": 0.001},
            "success": False,
            "reproducibility_score": 0.4,
            "execution_time": 150.8,
            "error_message": "Memory allocation error"
        }
    ]
    
    # Record the failures
    for failure in sample_failures:
        await reproducibility_db.process_request({
            "action": "record_attempt",
            "attempt_data": failure
        })
    
    # Now analyze failure patterns
    engine = await get_reproducibility_engine()
    
    result = await engine.analyze_failure_patterns({
        "experiment_type": "protein_folding",
        "min_frequency": 2
    })
    
    if result["success"]:
        print(f"✅ Failure pattern analysis completed")
        print(f"📊 Total patterns identified: {result['total_patterns']}")
        print(f"🔍 Analyzed attempts: {result['analyzed_attempts']}")
        
        if result["patterns"]:
            print("\n📋 Identified Patterns:")
            for pattern in result["patterns"][:3]:  # Show top 3 patterns
                print(f"   - {pattern['description']}")
                print(f"     Frequency: {pattern['frequency']}, Confidence: {pattern['confidence']:.3f}")
                print(f"     Type: {pattern['pattern_type']}")
    else:
        print(f"❌ Failure pattern analysis failed: {result['error']}")


async def example_reproducibility_recommendations():
    """Example of reproducibility recommendations generation"""
    print("\n💡 Reproducibility Recommendations Example...")
    
    engine = await get_reproducibility_engine()
    
    result = await engine.generate_reproducibility_recommendations({
        "experiment_type": "protein_folding",
        "priority_threshold": "medium"
    })
    
    if result["success"]:
        print(f"✅ Reproducibility recommendations generated")
        print(f"📊 Total recommendations: {result['total_recommendations']}")
        print(f"🔴 High priority recommendations: {result['high_priority_count']}")
        
        if result["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in result["recommendations"][:3]:  # Show top 3 recommendations
                print(f"   - {rec['title']}")
                print(f"     Priority: {rec['priority']}, Expected improvement: {rec['expected_improvement']:.3f}")
                print(f"     Implementation effort: {rec['implementation_effort']}")
    else:
        print(f"❌ Recommendations generation failed: {result['error']}")


async def example_reproducibility_statistics():
    """Example of reproducibility statistics"""
    print("\n📊 Reproducibility Statistics Example...")
    
    engine = await get_reproducibility_engine()
    
    result = await engine.get_reproducibility_statistics({
        "experiment_type": None,  # All experiment types
        "time_range": 30  # Last 30 days
    })
    
    if result["success"]:
        stats = result["statistics"]
        print(f"✅ Reproducibility statistics retrieved")
        print(f"📊 Total attempts: {stats['total_attempts']}")
        print(f"✅ Successful attempts: {stats['successful_attempts']}")
        print(f"❌ Failed attempts: {stats['failed_attempts']}")
        print(f"📈 Success rate: {stats['success_rate']:.3f}")
        print(f"📉 Failure rate: {stats['failure_rate']:.3f}")
        print(f"⭐ Average reproducibility score: {stats['average_reproducibility_score']:.3f}")
        print(f"⏱️ Average execution time: {stats['average_execution_time']:.2f} seconds")
        
        if stats.get("experiment_types"):
            print(f"🔬 Experiment types: {', '.join(stats['experiment_types'])}")
    else:
        print(f"❌ Statistics retrieval failed: {result['error']}")


async def example_comprehensive_robustness_report():
    """Example of comprehensive robustness report generation"""
    print("\n📋 Comprehensive Robustness Report Example...")
    
    perturbation_engine = PerturbationEngine()
    
    # Sample parameters for comprehensive analysis
    parameters = [
        {
            "name": "temperature",
            "min_value": 280.0,
            "max_value": 320.0,
            "default_value": 300.0,
            "unit": "K"
        },
        {
            "name": "pressure",
            "min_value": 0.8,
            "max_value": 1.2,
            "default_value": 1.0,
            "unit": "atm"
        },
        {
            "name": "concentration",
            "min_value": 0.1,
            "max_value": 10.0,
            "default_value": 1.0,
            "unit": "mM"
        }
    ]
    
    experimental_data = {
        "experiment_type": "molecular_dynamics",
        "description": "Comprehensive robustness test for MD simulations"
    }
    
    result = await perturbation_engine.generate_robustness_report({
        "action": "generate_robustness_report",
        "experiment_id": "comprehensive_test_2025",
        "parameters": parameters,
        "experimental_data": experimental_data
    })
    
    if result["success"]:
        report = result["report"]
        print(f"✅ Comprehensive robustness report generated")
        print(f"📊 Robustness score: {result['robustness_score']:.3f}")
        print(f"⚠️ Critical parameters: {result['critical_parameters_count']}")
        print(f"💡 Recommendations: {result['recommendations_count']}")
        
        print(f"\n📋 Report Summary:")
        print(f"   - Total perturbations: {report['total_perturbations']}")
        print(f"   - Successful reproductions: {report['successful_reproductions']}")
        print(f"   - Failed reproductions: {report['failed_reproductions']}")
        print(f"   - Critical parameters: {', '.join(report['critical_parameters'])}")
        
        if report["recommendations"]:
            print(f"\n💡 Top Recommendations:")
            for rec in report["recommendations"][:3]:
                print(f"   - {rec}")
    else:
        print(f"❌ Robustness report generation failed: {result['error']}")


async def main():
    """Run all advanced reproducibility examples"""
    print("🚀 AXIOM META 4 - Advanced Reproducibility Examples")
    print("=" * 70)
    
    try:
        # Run all examples
        await example_advanced_robustness_analysis()
        await example_sensitivity_analysis()
        await example_critical_conditions_detection()
        await example_failure_pattern_analysis()
        await example_reproducibility_recommendations()
        await example_reproducibility_statistics()
        await example_comprehensive_robustness_report()
        
        print("\n" + "=" * 70)
        print("✅ All advanced reproducibility examples completed successfully!")
        print("🎯 AXIOM META 4 now has comprehensive reproducibility analysis capabilities!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
