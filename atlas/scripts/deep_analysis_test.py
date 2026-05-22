#!/usr/bin/env python3
"""
Deep Analysis Test: Graph Theory with Full Paper Output
========================================================
Saves complete papers and provides detailed analysis.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, "/Volumes/Ganador disk/atlas")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

OUTPUT_DIR = "/Volumes/Ganador disk/atlas/artifacts/research_papers"


async def run_deep_test(topic: str, model: str = "minimax-m2.1:cloud"):
    """Run full pipeline and save all outputs."""
    from app.run_agent_with_tools_legacy import autonomous_research_agent
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("=" * 70)
    print(f"🔬 DEEP ANALYSIS TEST")
    print(f"📝 Topic: {topic}")
    print(f"🤖 Model: {model}")
    print(f"📁 Output: {OUTPUT_DIR}")
    print("=" * 70)
    
    result = await autonomous_research_agent(
        domain="mathematics",
        topic=topic,
        max_iterations=2,
        target_score=7,
        model_name=model
    )
    
    # Save complete result
    result_file = f"{OUTPUT_DIR}/{timestamp}_result.json"
    with open(result_file, "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n📊 RESULTS:")
    print(f"   Final Score: {result.get('final_score', 0)}")
    print(f"   Status: {result.get('status', 'unknown')}")
    print(f"   Iterations: {result.get('iterations_used', 0)}")
    
    # Extract paper content if available
    paper = result.get("paper_draft") or result.get("paper") or ""
    if paper:
        paper_file = f"{OUTPUT_DIR}/{timestamp}_paper.md"
        with open(paper_file, "w") as f:
            f.write(paper if isinstance(paper, str) else str(paper))
        print(f"   📄 Paper saved: {paper_file}")
    
    # Extract hypothesis
    hypothesis = result.get("hypothesis", {})
    if hypothesis:
        hyp_file = f"{OUTPUT_DIR}/{timestamp}_hypothesis.json"
        with open(hyp_file, "w") as f:
            json.dump(hypothesis, f, indent=2, default=str)
        print(f"   💡 Hypothesis saved: {hyp_file}")
    
    # Extract peer review
    peer_review = result.get("peer_review", {})
    if peer_review:
        review_file = f"{OUTPUT_DIR}/{timestamp}_peer_review.json"
        with open(review_file, "w") as f:
            json.dump(peer_review, f, indent=2, default=str)
        print(f"   📋 Peer review saved: {review_file}")
    
    # Extract tool evidence
    tools_used = result.get("tools_used", [])
    if tools_used:
        tools_file = f"{OUTPUT_DIR}/{timestamp}_tools_used.json"
        with open(tools_file, "w") as f:
            json.dump(tools_used, f, indent=2, default=str)
        print(f"   🔧 Tools saved: {tools_file}")
    
    print(f"\n📁 All files saved to: {OUTPUT_DIR}")
    
    return result


async def main():
    # Test 1: Graph Theory (original)
    print("\n\n" + "=" * 70)
    print("TEST 1: GRAPH THEORY")
    print("=" * 70)
    
    r1 = await run_deep_test(
        "graph coloring and chromatic number properties for planar graphs"
    )
    
    await asyncio.sleep(3)
    
    # Test 2: Topology / Manifolds (uses VietorisRipsBuilder)
    print("\n\n" + "=" * 70)
    print("TEST 2: TOPOLOGY - EULER CHARACTERISTIC")
    print("=" * 70)
    
    r2 = await run_deep_test(
        "Euler characteristic of closed surfaces and genus computation"
    )
    
    await asyncio.sleep(3)
    
    # Test 3: Sequences (uses SequenceAnalyzer)
    print("\n\n" + "=" * 70)
    print("TEST 3: SEQUENCES - FIBONACCI PROPERTIES")
    print("=" * 70)
    
    r3 = await run_deep_test(
        "Fibonacci sequence divisibility patterns and Lucas numbers relationships"
    )
    
    # Summary
    print("\n\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    
    tests = [
        ("Graph Theory", r1),
        ("Topology", r2),
        ("Sequences", r3)
    ]
    
    for name, result in tests:
        score = result.get("final_score", 0)
        status = "✅" if result.get("status") == "accepted" else "❌"
        iters = result.get("iterations_used", 0)
        print(f"   {status} {name}: Score {score} ({iters} iterations)")


if __name__ == "__main__":
    asyncio.run(main())
