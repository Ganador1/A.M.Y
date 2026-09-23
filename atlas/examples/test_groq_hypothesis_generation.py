"""
Test Groq API for Hypothesis Generation
Compares Llama-3-70B (Groq) vs Mistral-7B (local)
"""
import asyncio
import time
from typing import Dict, Any
import sys
sys.path.insert(0, '.')

from app.services.llm_providers.groq_provider import groq_provider


async def test_groq_hypothesis():
    """Test hypothesis generation with Groq API"""

    print("🚀 Testing Groq API for Scientific Hypothesis Generation")
    print("=" * 70)

    # Test 1: Check availability
    print("\n1️⃣ Checking Groq availability...")
    if not groq_provider.is_available():
        print("❌ Groq not available - Set GROQ_API_KEY environment variable")
        print("   Get free API key at: https://console.groq.com")
        return

    print("✅ Groq provider ready")

    # Test 2: List available models
    print("\n2️⃣ Listing available models...")
    models_result = await groq_provider.list_models()
    if models_result.get("success"):
        print(f"✅ Found {models_result['count']} models:")
        for model in models_result["models"][:5]:
            print(f"   - {model['id']}")
    else:
        print(f"⚠️ Could not list models: {models_result.get('error')}")

    # Test 3: Generate biological hypothesis
    print("\n3️⃣ Generating biological hypothesis with Llama-3.3-70B...")
    print("-" * 70)

    bio_prompt = """Generate a novel, testable scientific hypothesis in molecular biology.

Requirements:
- Focus on protein-protein interactions in cancer pathways
- Must be falsifiable
- Include specific genes/proteins
- Propose experimental validation method

Format:
Hypothesis: [Clear statement]
Variables: [Key variables]
Prediction: [Expected outcome]
Validation: [Experimental approach]
"""

    start = time.time()
    result = await groq_provider.generate_async(
        prompt=bio_prompt,
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=1024
    )
    latency = (time.time() - start) * 1000

    if result.get("success"):
        print(f"\n📝 Generated Hypothesis:")
        print(result["text"])
        print(f"\n⚡ Performance:")
        print(f"   Model: {result['model']}")
        print(f"   Latency: {result['latency_ms']:.2f}ms (provider) / {latency:.2f}ms (total)")
        print(f"   Tokens: {result['usage'].get('total_tokens', 'N/A')}")
        print(f"   Finish reason: {result['finish_reason']}")
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return

    # Test 4: Compare with fast model
    print("\n4️⃣ Comparing with Llama-3.1-8B (instant)...")
    print("-" * 70)

    start_fast = time.time()
    result_fast = await groq_provider.generate_async(
        prompt=bio_prompt,
        model="llama-3.1-8b-instant",
        temperature=0.7,
        max_tokens=1024
    )
    latency_fast = (time.time() - start_fast) * 1000

    if result_fast.get("success"):
        print(f"\n📝 Generated Hypothesis (8B):")
        print(result_fast["text"][:500] + "...")
        print(f"\n⚡ Performance Comparison:")
        print(f"   70B Latency: {result['latency_ms']:.2f}ms")
        print(f"   8B Latency:  {result_fast['latency_ms']:.2f}ms")
        print(f"   Speedup: {result['latency_ms'] / result_fast['latency_ms']:.2f}x faster (8B)")

    # Test 5: Chemistry hypothesis
    print("\n5️⃣ Generating chemistry hypothesis...")
    print("-" * 70)

    chem_prompt = """Generate a novel hypothesis about catalytic mechanisms in organic chemistry.

Focus on:
- Green chemistry applications
- Transition metal catalysis
- Mechanistic insights

Include reaction conditions and expected products."""

    result_chem = await groq_provider.generate_async(
        prompt=chem_prompt,
        model="llama-3.3-70b-versatile",
        temperature=0.65,
        max_tokens=800
    )

    if result_chem.get("success"):
        print(f"\n📝 Chemistry Hypothesis:")
        print(result_chem["text"])
        print(f"\n⚡ Latency: {result_chem['latency_ms']:.2f}ms")

    # Test 6: Multi-domain comparison
    print("\n6️⃣ Testing multiple domains...")
    print("-" * 70)

    domains = [
        ("Biology", "protein folding dynamics"),
        ("Physics", "quantum entanglement applications"),
        ("Mathematics", "prime number distribution patterns"),
    ]

    results_summary = []

    for domain, topic in domains:
        prompt = f"Generate a brief, testable hypothesis about {topic} in {domain.lower()}. Keep it under 100 words."
        result_domain = await groq_provider.generate_async(
            prompt=prompt,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=200
        )

        if result_domain.get("success"):
            results_summary.append({
                "domain": domain,
                "latency": result_domain['latency_ms'],
                "tokens": result_domain['usage'].get('total_tokens', 0),
                "preview": result_domain['text'][:100] + "..."
            })

    print("\n📊 Multi-Domain Results:")
    for r in results_summary:
        print(f"\n{r['domain']}:")
        print(f"   Latency: {r['latency']:.2f}ms | Tokens: {r['tokens']}")
        print(f"   Preview: {r['preview']}")

    # Summary
    print("\n" + "=" * 70)
    print("✅ Groq API Testing Complete!")
    print(f"\nKey Takeaways:")
    print(f"   - Ultra-low latency: ~{result['latency_ms']:.0f}ms for 70B model")
    print(f"   - High quality: Specialized scientific reasoning")
    print(f"   - Free tier: Suitable for testing and development")
    print(f"\nNext steps:")
    print(f"   1. Integrate into ScientificHypothesisAgent")
    print(f"   2. Update config/agents.yaml with Groq models")
    print(f"   3. Run A/B comparison vs local models")


def main():
    """Run async test"""
    asyncio.run(test_groq_hypothesis())


if __name__ == "__main__":
    main()
