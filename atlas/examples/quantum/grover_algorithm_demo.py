"""
Grover's Algorithm Demonstration

This example demonstrates quantum search using Grover's algorithm via AXIOM ATLAS,
showing how to find target states in an unstructured database with quadratic speedup.

Requirements:
    - AXIOM ATLAS running at http://localhost:8000
    - httpx installed: pip install httpx

Usage:
    python examples/quantum/grover_algorithm_demo.py

Background:
    Grover's algorithm provides O(√N) speedup for searching unstructured databases,
    compared to O(N) for classical search. For 8 items, classical needs ~4 queries
    on average, while Grover needs ~2.8 queries.
"""

import asyncio
import httpx
from typing import Dict, Any


async def grover_search(
    target_state: str,
    num_qubits: int = 3,
    backend: str = "qasm_simulator"
) -> Dict[str, Any]:
    """
    Run Grover's algorithm to find a target state.

    Args:
        target_state: Binary string to search for (e.g., "101")
        num_qubits: Number of qubits (determines search space size = 2^n)
        backend: Qiskit backend ('qasm_simulator' or 'statevector_simulator')

    Returns:
        Dict with search results and quantum circuit info
    """
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(base_url=base_url, timeout=60.0) as client:
        print(f"🔍 Searching for state '{target_state}' in {2**num_qubits}-item database...")

        try:
            response = await client.post(
                "/api/quantum-computing/grover-search",
                json={
                    "target_state": target_state,
                    "num_qubits": num_qubits,
                    "backend": backend,
                    "shots": 1024  # Number of measurements
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
            raise

        return result


def display_results(result: Dict[str, Any], target: str) -> None:
    """
    Display Grover's algorithm results.

    Args:
        result: API response with search results
        target: Target state that was searched
    """
    print(f"\n{'='*60}")
    print(f"📊 Grover Search Results")
    print(f"{'='*60}")

    # Success metrics
    success_prob = result.get('success_probability', 0)
    iterations = result.get('iterations', 0)
    search_space_size = result.get('search_space_size', 0)

    print(f"\n🎯 Target State: {target}")
    print(f"   Search Space: {search_space_size} items")
    print(f"   Grover Iterations: {iterations}")
    print(f"   Success Probability: {success_prob*100:.1f}%")

    # Measurement counts
    counts = result.get('counts', {})
    print(f"\n📈 Measurement Results (top 5):")

    # Sort by count (most frequent first)
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]

    for state, count in sorted_counts:
        percentage = (count / sum(counts.values())) * 100
        bar = "█" * int(percentage / 2)  # Visual bar
        marker = " ✓" if state == target else ""
        print(f"   |{state}⟩: {count:4d} ({percentage:5.1f}%) {bar}{marker}")

    # Classical comparison
    classical_queries = search_space_size // 2  # Average case
    quantum_queries = iterations
    speedup = classical_queries / quantum_queries if quantum_queries > 0 else 1

    print(f"\n⚡ Speedup Analysis:")
    print(f"   Classical (avg): ~{classical_queries} queries")
    print(f"   Quantum: {quantum_queries} iterations")
    print(f"   Speedup: {speedup:.2f}x")


async def demonstrate_scaling():
    """
    Demonstrate Grover's algorithm scaling with different search space sizes.
    """
    print(f"\n{'='*60}")
    print(f"🔬 Grover Scaling Demonstration")
    print(f"{'='*60}\n")

    test_cases = [
        (2, "11"),   # 4 items
        (3, "101"),  # 8 items
        (4, "1010"), # 16 items
    ]

    for num_qubits, target in test_cases:
        result = await grover_search(target, num_qubits)
        display_results(result, target)
        print(f"\n{'-'*60}\n")
        await asyncio.sleep(1)  # Avoid overwhelming the server


async def compare_backends():
    """
    Compare statevector vs qasm simulator for Grover's algorithm.
    """
    print(f"\n{'='*60}")
    print(f"🔬 Backend Comparison")
    print(f"{'='*60}\n")

    target = "101"
    backends = ["statevector_simulator", "qasm_simulator"]

    for backend in backends:
        print(f"\n▶ Running with {backend}...")
        result = await grover_search(target, num_qubits=3, backend=backend)

        success_prob = result.get('success_probability', 0)
        iterations = result.get('iterations', 0)

        print(f"   Iterations: {iterations}")
        print(f"   Success Probability: {success_prob*100:.1f}%")


async def main():
    """Main execution."""

    print("="*60)
    print("Grover's Algorithm - Quantum Search Demo")
    print("="*60)

    # Example 1: Basic search
    print("\n📍 Example 1: Basic Search")
    print("-" * 60)

    target = "101"  # Search for state |101⟩ in 8-item database
    result = await grover_search(target, num_qubits=3)
    display_results(result, target)

    # Example 2: Scaling demonstration
    await demonstrate_scaling()

    # Example 3: Backend comparison (optional - uncomment to run)
    # await compare_backends()

    print("\n✅ Demo complete!")
    print("\nℹ️  Key Takeaway: Grover's algorithm finds items in O(√N) time,")
    print("   providing quadratic speedup over classical O(N) search.")


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
        print("   Ensure you have Qiskit installed: pip install qiskit")
        print("   Then run this script again.")
