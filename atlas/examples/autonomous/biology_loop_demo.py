"""
Autonomous BiologyLoop Demonstration

This example demonstrates the autonomous research loop that generates biological
hypotheses, designs experiments, executes them, and validates results using
multi-agent AI coordination.

Requirements:
    - AXIOM ATLAS running at http://localhost:8000
    - Ollama running locally with required models:
        - llama3:8b (Orchestrator)
        - mistral:7b (Bio Hypothesis Generator)
        - codellama:7b (PhysChem Coder)
        - qwen:7b (Reviewer)
    - httpx installed: pip install httpx

Setup Ollama:
    ollama pull llama3:8b
    ollama pull mistral:7b
    ollama pull codellama:7b
    ollama pull qwen:7b

Usage:
    python examples/autonomous/biology_loop_demo.py
"""

import asyncio
import httpx
from typing import Dict, Any, List
from datetime import datetime


async def run_biology_loop(
    k_targets: int = 5,
    enable_ethics: bool = True,
    enable_reviewer: bool = True
) -> Dict[str, Any]:
    """
    Run one iteration of the autonomous BiologyLoop.

    Args:
        k_targets: Number of biological targets to analyze
        enable_ethics: Enable ethics gate validation
        enable_reviewer: Enable critical review of hypotheses

    Returns:
        Dict with generated hypotheses and experiment results
    """
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(base_url=base_url, timeout=300.0) as client:
        print(f"🤖 Starting autonomous BiologyLoop...")
        print(f"   Targets: {k_targets}")
        print(f"   Ethics Gate: {'Enabled' if enable_ethics else 'Disabled'}")
        print(f"   Critical Review: {'Enabled' if enable_reviewer else 'Disabled'}\n")

        try:
            response = await client.post(
                "/api/autonomous/biology-loop/run",
                json={
                    "k_targets": k_targets,
                    "enable_ethics_check": enable_ethics,
                    "enable_reviewer": enable_reviewer,
                    "max_iterations": 1
                }
            )
            response.raise_for_status()
            result = response.json()

        except httpx.HTTPStatusError as e:
            print(f"❌ API Error: {e.response.status_code}")
            print(f"   Details: {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"❌ Connection Error: {e}")
            print("   Ensure AXIOM ATLAS is running at http://localhost:8000")
            print("   Ensure Ollama is running at http://localhost:11434")
            raise

        return result


def display_hypotheses(hypotheses: List[Dict[str, Any]]) -> None:
    """
    Display generated hypotheses with metrics.

    Args:
        hypotheses: List of hypothesis objects
    """
    print(f"\n{'='*80}")
    print(f"📋 Generated Hypotheses ({len(hypotheses)})")
    print(f"{'='*80}\n")

    for i, hyp in enumerate(hypotheses, 1):
        statement = hyp.get('statement', 'N/A')
        priority = hyp.get('priority_score', 0.0)
        novelty = hyp.get('novelty_score', 0.0)
        feasibility = hyp.get('feasibility_score', 0.0)
        domain = hyp.get('domain', 'Unknown')

        print(f"{i}. {statement}")
        print(f"   Domain: {domain}")
        print(f"   Priority: {priority:.2f} | Novelty: {novelty:.2f} | Feasibility: {feasibility:.2f}")

        # Predicted outcomes
        predictions = hyp.get('predicted_outcomes', [])
        if predictions:
            print(f"   Predictions:")
            for pred in predictions[:2]:  # Show first 2
                print(f"     - {pred}")

        # Review comments (if available)
        review = hyp.get('review_comments', '')
        if review:
            print(f"   Review: {review[:100]}...")

        print()


def display_experiments(experiments: List[Dict[str, Any]]) -> None:
    """
    Display executed experiments and results.

    Args:
        experiments: List of experiment objects
    """
    print(f"\n{'='*80}")
    print(f"🔬 Experiments Executed ({len(experiments)})")
    print(f"{'='*80}\n")

    for i, exp in enumerate(experiments, 1):
        exp_type = exp.get('experiment_type', 'Unknown')
        status = exp.get('status', 'Unknown')
        runtime = exp.get('runtime_seconds', 0.0)

        print(f"{i}. {exp_type}")
        print(f"   Status: {status}")
        print(f"   Runtime: {runtime:.2f}s")

        # Results summary
        results = exp.get('results', {})
        if results:
            print(f"   Results:")
            for key, value in list(results.items())[:3]:  # Show first 3 items
                print(f"     {key}: {value}")

        # Validation
        validation = exp.get('validation', {})
        if validation:
            is_valid = validation.get('is_valid', False)
            confidence = validation.get('confidence', 0.0)
            print(f"   Validation: {'✓' if is_valid else '✗'} ({confidence:.1%} confidence)")

        print()


def display_agent_activity(result: Dict[str, Any]) -> None:
    """
    Display agent activity and coordination metrics.

    Args:
        result: BiologyLoop result with agent logs
    """
    agent_logs = result.get('agent_activity', {})

    if not agent_logs:
        return

    print(f"\n{'='*80}")
    print(f"🤖 Agent Activity")
    print(f"{'='*80}\n")

    agents = {
        'orchestrator': 'Orchestrator (Planning)',
        'bio_hypothesis': 'Bio Hypothesis Generator',
        'physchem_coder': 'PhysChem Coder (Experiments)',
        'reviewer': 'Critical Reviewer'
    }

    for agent_key, agent_name in agents.items():
        if agent_key in agent_logs:
            log = agent_logs[agent_key]
            calls = log.get('calls', 0)
            tokens = log.get('tokens_used', 0)
            avg_time = log.get('avg_response_time', 0.0)

            print(f"   {agent_name}")
            print(f"     Calls: {calls} | Tokens: {tokens:,} | Avg Time: {avg_time:.2f}s")


async def continuous_research_loop(iterations: int = 3, interval: int = 60):
    """
    Run multiple iterations of the BiologyLoop continuously.

    Args:
        iterations: Number of iterations to run
        interval: Seconds between iterations
    """
    print(f"\n{'='*80}")
    print(f"🔄 Continuous Research Mode ({iterations} iterations)")
    print(f"{'='*80}\n")

    all_hypotheses = []

    for i in range(1, iterations + 1):
        print(f"\n{'─'*80}")
        print(f"Iteration {i}/{iterations}")
        print(f"{'─'*80}")

        result = await run_biology_loop(k_targets=3, enable_ethics=True)

        hypotheses = result.get('hypotheses', [])
        all_hypotheses.extend(hypotheses)

        display_hypotheses(hypotheses)

        # Sleep between iterations (except last)
        if i < iterations:
            print(f"\n⏳ Waiting {interval}s before next iteration...")
            await asyncio.sleep(interval)

    # Final summary
    print(f"\n{'='*80}")
    print(f"📊 Final Summary")
    print(f"{'='*80}")
    print(f"   Total Hypotheses: {len(all_hypotheses)}")
    print(f"   Avg Priority: {sum(h.get('priority_score', 0) for h in all_hypotheses) / len(all_hypotheses):.2f}")


async def main():
    """Main execution."""

    print("="*80)
    print("Autonomous BiologyLoop - AI-Driven Research")
    print("="*80)

    # Check Ollama connection
    print("\n🔍 Checking Ollama service...")
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running ({len(models)} models available)")
        else:
            print("⚠️  Ollama responded but with unexpected status")
    except httpx.RequestError:
        print("❌ Ollama not running!")
        print("   Start with: ollama serve")
        print("   Pull models:")
        print("     ollama pull llama3:8b")
        print("     ollama pull mistral:7b")
        print("     ollama pull codellama:7b")
        print("     ollama pull qwen:7b")
        return

    # Example 1: Single BiologyLoop iteration
    print("\n" + "="*80)
    print("📍 Example 1: Single Research Iteration")
    print("="*80)

    result = await run_biology_loop(k_targets=5, enable_ethics=True, enable_reviewer=True)

    # Display results
    hypotheses = result.get('hypotheses', [])
    experiments = result.get('experiments', [])

    display_hypotheses(hypotheses)
    display_experiments(experiments)
    display_agent_activity(result)

    # Example 2: Continuous research (optional - uncomment to run)
    # print("\n" + "="*80)
    # print("📍 Example 2: Continuous Research (3 iterations)")
    # print("="*80)
    # await continuous_research_loop(iterations=3, interval=30)

    print("\n✅ Demo complete!")
    print("\nℹ️  The BiologyLoop autonomously:")
    print("   1. Analyzes biological targets")
    print("   2. Generates falsifiable hypotheses")
    print("   3. Designs computational experiments")
    print("   4. Executes and validates results")
    print("   5. Applies ethics and safety checks")


if __name__ == "__main__":
    # Check if server is running
    print("🔍 Checking AXIOM ATLAS server...")

    try:
        import httpx
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        if response.status_code == 200:
            print("✅ Server is running\n")
            asyncio.run(main())
        else:
            print(f"⚠️  Server returned status: {response.status_code}")
            print("   Try restarting with: uvicorn main_refactored:app --reload")
    except httpx.RequestError:
        print("❌ Server not running!")
        print("   Start with: uvicorn main_refactored:app --reload")
        print("   Then run this script again.")
