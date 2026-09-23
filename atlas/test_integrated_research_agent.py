#!/usr/bin/env python3
"""
Test Integrated Research Agent
==============================
Tests the autonomous research agent across multiple scientific domains,
demonstrating the integration of LangChain migration, Groq cloud models,
and dynamic tool discovery with 40+ available tools.

Author: AXIOM ATLAS
"""

import asyncio
import json
from datetime import datetime


async def test_domain(domain: str, topic: str, max_iterations: int = 4):
    """Test autonomous research for a specific domain."""
    from run_agent_with_tools import autonomous_research_agent, DynamicToolRegistry
    
    print(f"\n{'='*80}")
    print(f"🔬 DOMAIN: {domain.upper()}")
    print(f"📋 TOPIC: {topic}")
    print(f"{'='*80}")
    
    # Get tool stats
    registry = DynamicToolRegistry()
    all_tools = registry.list_tools()
    domain_tools = registry.list_tools(domain)
    
    print(f"\n📦 Tools: {len(all_tools)} total, {len(domain_tools)} for {domain}")
    if domain_tools:
        print(f"   Domain tools: {domain_tools[:5]}...")
    
    # Run research with extended iterations for acceptance
    start = datetime.now()
    result = await autonomous_research_agent(domain, topic, max_iterations=max_iterations)
    elapsed = (datetime.now() - start).total_seconds()
    
    print(f"\n⏱️  Completed in {elapsed:.1f}s")
    return result


async def main():
    """Run multi-domain research tests."""
    print("\n" + "🧪"*40)
    print("   AXIOM ATLAS - Integrated Research Agent Tests")
    print("   LangChain Migration + Groq Cloud + Dynamic Tools")
    print("🧪"*40)
    
    # Test cases across domains
    test_cases = [
        ("mathematics", "prime gap distribution patterns"),
        ("chemistry", "molecular orbital energy in conjugated systems"),
        ("biology", "DNA GC content correlation with thermal stability"),
        ("physics", "hydrogen atom energy level transitions"),
    ]
    
    results = {}
    
    for domain, topic in test_cases:
        try:
            result = await test_domain(domain, topic)
            results[domain] = {
                "status": "success",
                "topic": topic,
                "result": result
            }
        except Exception as e:
            print(f"\n❌ Error in {domain}: {e}")
            results[domain] = {
                "status": "error",
                "topic": topic,
                "error": str(e)
            }
        
        print("\n" + "-"*80)
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    for domain, data in results.items():
        status = "✅" if data["status"] == "success" else "❌"
        print(f"   {status} {domain.upper()}: {data['status']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"integrated_research_results_{timestamp}.json"
    
    with open(output_file, "w") as f:
        # Convert result to serializable format
        serializable_results = {}
        for k, v in results.items():
            serializable_results[k] = {
                "status": v["status"],
                "topic": v["topic"]
            }
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    # Run single quick test
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test - just mathematics with more iterations
        asyncio.run(test_domain("mathematics", "prime gap patterns", max_iterations=3))
    else:
        # Full multi-domain test
        asyncio.run(main())
