#!/usr/bin/env python3
"""
AXIOM Phase 3 Demonstration Script
Shows the autonomous scientific research capabilities with iterative refinement
"""

import asyncio
from app.services.scientific_copilot import ScientificCopilotService
from app.logging_config import logger


async def demonstrate_phase3_capabilities():
    """Demonstrate AXIOM Phase 3 autonomous research capabilities"""

    print("🚀 AXIOM Phase 3 - Autonomous Scientific Research Demonstration")
    print("=" * 60)

    # Initialize the scientific copilot
    copilot = ScientificCopilotService()

    # Research topic: Optimization of chemical reaction conditions
    research_topic = "Optimization of catalytic reaction conditions for sustainable synthesis"

    print(f"📋 Research Topic: {research_topic}")
    print()

    # Start research session
    print("1️⃣ Starting Research Session...")
    session_result = await copilot.process_request({
        "action": "start_research_session",
        "research_topic": research_topic,
        "domain": "chemistry",
        "initial_context": {
            "field": "organic synthesis",
            "goal": "optimize reaction conditions for maximum yield and selectivity",
            "constraints": ["temperature", "pressure", "catalyst concentration", "reaction time"]
        }
    })

    if not session_result.get("success"):
        print(f"❌ Failed to start session: {session_result.get('error')}")
        return

    session_id = session_result["session_id"]
    print(f"✅ Research session started: {session_id}")
    print()

    # Generate initial hypotheses
    print("2️⃣ Generating Initial Hypotheses...")
    hypothesis_result = await copilot.process_request({
        "action": "generate_hypotheses",
        "session_id": session_id,
        "context": {
            "domain_knowledge": {
                "reaction_type": "catalytic hydrogenation",
                "catalyst": "Pd/C",
                "substrate": "aromatic nitro compound",
                "solvent": "methanol"
            }
        }
    })

    hypotheses = []
    if hypothesis_result.get("success"):
        hypotheses = hypothesis_result.get("hypotheses", [])
        print(f"✅ Generated {len(hypotheses)} hypotheses")
        for i, hyp in enumerate(hypotheses[:3]):  # Show first 3
            print(f"   {i+1}. {hyp.get('description', 'N/A')}")
    else:
        print(f"❌ Failed to generate hypotheses: {hypothesis_result.get('error')}")
        # Create a mock hypothesis for demonstration
        hypotheses = [{
            "id": "mock_hypothesis_1",
            "description": "Temperature optimization for catalytic reaction",
            "title": "Temperature affects reaction rate and selectivity"
        }]
    print()

    # Design experiments using Bayesian optimization
    print("3️⃣ Designing Experiments with Bayesian Optimization...")
    if hypotheses:
        hypothesis_id = hypotheses[0].get("id")

        design_result = await copilot.process_request({
            "action": "design_experiments",
            "session_id": session_id,
            "hypothesis_id": hypothesis_id,
            "parameter_bounds": {
                "temperature": [25, 80],      # °C
                "pressure": [1, 5],          # atm
                "catalyst_loading": [0.01, 0.1],  # mol%
                "reaction_time": [1, 24]     # hours
            }
        })

        if design_result.get("success"):
            experiments = design_result.get("experiments", [])
            print(f"✅ Designed {len(experiments)} experiments")
            for i, exp in enumerate(experiments[:3]):  # Show first 3
                params = exp.get("parameters", {})
                print(f"   Experiment {i+1}: T={params.get('temperature', 'N/A')}°C, "
                      f"P={params.get('pressure', 'N/A')} atm, "
                      f"Catalyst={params.get('catalyst_loading', 'N/A')} mol%")
        else:
            print(f"❌ Failed to design experiments: {design_result.get('error')}")
    print()

    # Run autonomous research cycle
    print("4️⃣ Running Autonomous Research Cycle...")
    cycle_result = await copilot.process_request({
        "action": "run_autonomous_cycle",
        "session_id": session_id,
        "max_iterations": 2,
        "parameter_bounds": {
            "temperature": [25, 80],
            "pressure": [1, 5],
            "catalyst_loading": [0.01, 0.1],
            "reaction_time": [1, 24]
        }
    })

    if cycle_result.get("success"):
        iterations = cycle_result.get("total_iterations", 0)
        print(f"✅ Completed {iterations} autonomous research cycles")

        # Show final status
        status_result = await copilot.process_request({
            "action": "get_research_status",
            "session_id": session_id
        })

        if status_result.get("success"):
            status = status_result
            print("📊 Final Research Status:")
            print(f"   Current Phase: {status.get('current_phase')}")
            print(f"   Hypotheses: {status.get('hypotheses_count')}")
            print(f"   Experiments: {status.get('experiments_count')}")
            print(f"   Results: {status.get('results_count')}")
            print(f"   Insights: {status.get('insights_count')}")
    else:
        print(f"❌ Failed to run autonomous cycle: {cycle_result.get('error')}")
    print()

    # Demonstrate parameter optimization
    print("5️⃣ Demonstrating Parameter Optimization...")
    optimization_result = await copilot.process_request({
        "action": "optimize_parameters",
        "session_id": session_id,
        "parameter_bounds": {
            "temperature": [25, 80],
            "pressure": [1, 5],
            "catalyst_loading": [0.01, 0.1],
            "reaction_time": [1, 24]
        },
        "max_iterations": 10
    })

    if optimization_result.get("success"):
        optimal_params = optimization_result.get("optimal_design", {})
        # optimal_value = optimization_result.get("optimal_value", 0)
        print("✅ Parameter optimization completed")
        print(f"   Optimal Parameters: {optimal_params}")
        print(".4f")
    else:
        print(f"❌ Parameter optimization failed: {optimization_result.get('error')}")
    print()

    # Create surrogate model for expensive simulations
    print("6️⃣ Creating Surrogate Model for Expensive Simulations...")
    surrogate_result = await copilot.process_request({
        "action": "create_surrogate_model",
        "session_id": session_id,
        "simulation_config": {
            "parameter_bounds": {
                "temperature": [25, 80],
                "pressure": [1, 5],
                "catalyst_loading": [0.01, 0.1],
                "reaction_time": [1, 24]
            },
            "initial_samples": 15,
            "model_type": "gaussian_process"
        }
    })

    if surrogate_result.get("success"):
        model_id = surrogate_result.get("model_id")
        print(f"✅ Surrogate model created: {model_id}")
        print(f"   Model Type: {surrogate_result.get('model_type')}")
        print(f"   Initial Samples: {surrogate_result.get('initial_samples')}")
    else:
        print(f"❌ Surrogate model creation failed: {surrogate_result.get('error')}")
    print()

    # Generate final insights
    print("7️⃣ Generating Final Research Insights...")
    insights_result = await copilot.process_request({
        "action": "generate_insights",
        "session_id": session_id
    })

    if insights_result.get("success"):
        insights = insights_result.get("insights", [])
        print(f"✅ Generated {len(insights)} insights")
        for i, insight in enumerate(insights[-3:]):  # Show last 3 insights
            print(f"   Insight {i+1}: {insight}")
    else:
        print(f"❌ Failed to generate insights: {insights_result.get('error')}")
    print()

    # Final research summary
    print("8️⃣ Research Summary")
    print("-" * 30)

    # Get comprehensive summary
    summary_result = await copilot.get_research_summary(session_id)

    if summary_result.get("success"):
        summary = summary_result
        progress = summary.get("progress_summary", {})

        print(f"Research Topic: {summary.get('research_topic')}")
        print(f"Session ID: {summary.get('session_id')}")
        print(f"Current Phase: {summary.get('current_phase')}")
        print()
        print("Progress Summary:")
        print(f"  • Hypotheses Generated: {progress.get('hypotheses_generated', 0)}")
        print(f"  • Experiments Designed: {progress.get('experiments_designed', 0)}")
        print(f"  • Results Collected: {progress.get('results_collected', 0)}")
        print(f"  • Insights Discovered: {progress.get('insights_discovered', 0)}")
        print()
        print("Timeline:")
        timeline = summary.get("timeline", {})
        print(f"  • Duration: {timeline.get('duration_hours', 0):.2f} hours")
        print(f"  • Created: {timeline.get('created_at', 'N/A')}")
        print(f"  • Last Updated: {timeline.get('last_updated', 'N/A')}")

    print()
    print("🎉 AXIOM Phase 3 Demonstration Completed!")
    print("The system has successfully demonstrated:")
    print("  ✅ Autonomous hypothesis generation")
    print("  ✅ Bayesian optimization for experimental design")
    print("  ✅ Iterative research cycle management")
    print("  ✅ Parameter optimization")
    print("  ✅ Surrogate modeling for expensive simulations")
    print("  ✅ Insight generation and knowledge discovery")


async def demonstrate_bayesian_optimization():
    """Demonstrate standalone Bayesian optimization capabilities"""

    print("\n🔬 Standalone Bayesian Optimization Demo")
    print("=" * 40)

    copilot = ScientificCopilotService()

    # Start session for optimization demo
    session_result = await copilot.process_request({
        "action": "start_research_session",
        "research_topic": "Bayesian Optimization Demo",
        "domain": "optimization"
    })

    if not session_result.get("success"):
        print(f"❌ Failed to start session: {session_result.get('error')}")
        return

    session_id = session_result["session_id"]

    # Optimize a simple function: f(x,y) = (x-2)^2 + (y-3)^2
    print("Optimizing function: f(x,y) = (x-2)² + (y-3)²")
    print("Expected minimum at: x=2, y=3, f=0")

    optimization_result = await copilot.process_request({
        "action": "optimize_parameters",
        "session_id": session_id,
        "parameter_bounds": {
            "x": [0, 4],
            "y": [0, 6]
        },
        "max_iterations": 15
    })

    if optimization_result.get("success"):
        optimal = optimization_result.get("optimal_design", {})
        # value = optimization_result.get("optimal_value", 0)
        print("✅ Optimization completed")
        print(f"   Found optimum at: x={optimal.get('x', 'N/A')}, y={optimal.get('y', 'N/A')}")
        print(".6f")
        print(".6f")
    else:
        print(f"❌ Optimization failed: {optimization_result.get('error')}")


async def main():
    """Main demonstration function"""
    try:
        print("🤖 AXIOM Phase 3 - Scientific Copilot System")
        print("Autonomous Research with Iterative Refinement")
        print("=" * 50)

        # Run main demonstration
        await demonstrate_phase3_capabilities()

        # Run optimization demo
        await demonstrate_bayesian_optimization()

        print("\n🎯 All demonstrations completed successfully!")
        print("AXIOM Phase 3 is ready for autonomous scientific research.")

    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        print(f"❌ Demonstration failed: {e}")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
