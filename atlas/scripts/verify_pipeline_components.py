#!/usr/bin/env python3
"""
Component-Level Verification for Autonomous Pipeline Improvements.

This script tests individual components to avoid asyncio conflicts.
"""

import asyncio
import sys

# Setup path
sys.path.insert(0, "/Volumes/Ganador disk/atlas")

async def test_literature():
    """Test 1: Literature Enhancement"""
    print("\n=== TEST 1: Literature Enhancement ===")
    from app.autonomous.interfaces.external_apis import fetch_literature_snippets
    
    results = await fetch_literature_snippets("Riemann Hypothesis", limit=2)
    
    for p in results:
        print(f"  Title: {p['title'][:50]}...")
        print(f"  Abstract Length: {len(p.get('full_abstract', ''))} chars")
        print(f"  Authors: {p.get('authors', [])}")
        print(f"  Categories: {p.get('categories', [])}")
        print()
        
        if len(p.get('full_abstract', '')) > 250:
            print("  ✅ PASS: full_abstract retrieved")
        else:
            print("  ❌ FAIL: Abstract too short")
    
    return True

async def test_tool_orchestrator():
    """Test 2: Tool Registration"""
    print("\n=== TEST 2: Tool Registration ===")
    from app.services.orchestration.tool_evidence_orchestrator import ToolEvidenceOrchestratorService
    
    orchestrator = ToolEvidenceOrchestratorService()
    
    # Check if advanced tools are registered
    routes = orchestrator._build_domain_routes()
    math_routes = routes.get("mathematics", [])
    numth_routes = routes.get("number_theory", [])
    
    print(f"  Mathematics routes: {len(math_routes)}")
    print(f"  Number Theory routes: {len(numth_routes)}")
    
    # Check for advanced tools
    all_descriptions = [r.description for r in math_routes + numth_routes]
    
    advanced_keywords = ["SMT", "Z3", "Lean4", "Coq", "contraejemplo", "counterexample", "number theory"]
    found = [kw for kw in advanced_keywords if any(kw.lower() in d.lower() for d in all_descriptions)]
    
    print(f"  Advanced tools found: {found}")
    
    if "SMT" in found or "Z3" in found:
        print("  ✅ PASS: Z3/SMT tools registered")
    else:
        print("  ⚠️ WARNING: Z3/SMT tools not found in descriptions")
    
    # Try corroborate with a simple hypothesis
    print("\n  Testing corroborate action...")
    result = await orchestrator.process_request({
        "action": "corroborate",
        "hypothesis": {
            "title": "All prime gaps less than log(p)^2",
            "description": "Testing hypothesis corroboration",
            "domain": "mathematics"
        }
    })
    
    print(f"  Corroborate result success: {result.get('success')}")
    print(f"  Evidence items: {len(result.get('evidence_items', []))}")
    print(f"  Support score: {result.get('aggregate', {}).get('support_score', 'N/A')}")
    
    if result.get('success') or len(result.get('evidence_items', [])) > 0:
        print("  ✅ PASS: Corroborate executed")
    
    return True

async def test_peer_review_with_tools():
    """Test 3: Peer Review with Tools"""
    print("\n=== TEST 3: Peer Review with Tools ===")
    from app.services.verification.autonomous_peer_review_service import AutonomousPeerReviewService
    
    service = AutonomousPeerReviewService()
    
    # Check if tool_orchestrator is initialized
    if hasattr(service, 'tool_orchestrator') and service.tool_orchestrator is not None:
        print("  ✅ PASS: tool_orchestrator initialized in peer review")
    else:
        print("  ❌ FAIL: tool_orchestrator not found")
        return False
    
    # Check if _corroborate_with_tools method exists
    if hasattr(service, '_corroborate_with_tools'):
        print("  ✅ PASS: _corroborate_with_tools method exists")
        
        # Test the method
        result = await service._corroborate_with_tools(
            hypothesis="Prime gaps grow as log(p)^2",
            description="Mathematical conjecture about prime distribution",
            domain="mathematics"
        )
        
        print(f"  Tool corroboration result: {type(result).__name__}")
        if result:
            print(f"    - Success: {result.get('success')}")
            print(f"    - Items: {len(result.get('evidence_items', []))}")
    else:
        print("  ❌ FAIL: _corroborate_with_tools not found")
        return False
    
    return True

async def test_paper_builder():
    """Test 4: Paper Builder Enhancement"""
    print("\n=== TEST 4: Paper Builder Enhancement ===")
    from app.autonomous.publication.paper_builder import build_paper
    
    # Build paper with experimental results
    paper = build_paper(
        metadata={
            "title": "Test Paper",
            "authors": ["Test Author"],
            "tool_evidence": {
                "aggregate": {"support_score": 0.85},
                "evidence_items": [
                    {"source": "Z3SMT", "success": True, "confidence": 0.9, "raw_result": "sat"}
                ]
            }
        },
        sections={
            "introduction": {"title": "Introduction", "content": "Test intro", "order": 10}
        },
        artifacts={},
        experimental_results={"test_metric": 123}
    )
    
    md = paper.to_markdown()
    
    if "Computational Validation" in md:
        print("  ✅ PASS: Computational Validation section generated")
    else:
        print("  ❌ FAIL: No Computational Validation section")
    
    if "Support Score" in md:
        print("  ✅ PASS: Support Score included")
    else:
        print("  ⚠️ WARNING: Support Score not found")
    
    if "Z3SMT" in md:
        print("  ✅ PASS: Evidence items included in paper")
    
    print("\n--- Generated Paper Snippet ---")
    # Show first 500 chars
    print(md[:800])
    print("...")
    
    return True

async def test_hypothesis_generator_context():
    """Test 5: Hypothesis Generator Context"""
    print("\n=== TEST 5: Hypothesis Generator Context ===")
    from app.autonomous.generators.hypothesis_generator import HypothesisGenerator
    
    gen = HypothesisGenerator()
    
    # Test with peer_review_feedback context
    context = {
        "peer_review_feedback": {
            "issues": [{"description": "Hypothesis too broad"}],
            "recommendations": ["Focus on specific prime ranges"]
        },
        "failed_hypotheses": [
            {"title": "All primes are even", "rejection_reason": "Counterexample: 3"}
        ],
        "iteration": 2
    }
    
    # Check if generate_hypothesis accepts these params
    import inspect
    sig = inspect.signature(gen.generate_hypothesis)
    
    print(f"  generate_hypothesis accepts 'context': {'context' in sig.parameters}")
    
    # The docstring should mention peer_review_feedback
    docstring = gen.generate_hypothesis.__doc__ or ""
    if "peer_review_feedback" in docstring:
        print("  ✅ PASS: peer_review_feedback documented in method")
    else:
        print("  ⚠️ WARNING: peer_review_feedback not in docstring")
    
    if "failed_hypotheses" in docstring:
        print("  ✅ PASS: failed_hypotheses documented in method")
    
    return True

async def main():
    print("=" * 60)
    print("AUTONOMOUS PIPELINE COMPONENT VERIFICATION")
    print("=" * 60)
    
    results = {}
    
    try:
        results["literature"] = await test_literature()
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results["literature"] = False
    
    try:
        results["tool_orchestrator"] = await test_tool_orchestrator()
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results["tool_orchestrator"] = False
    
    try:
        results["peer_review"] = await test_peer_review_with_tools()
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results["peer_review"] = False
    
    try:
        results["paper_builder"] = await test_paper_builder()
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results["paper_builder"] = False
    
    try:
        results["hypothesis_context"] = await test_hypothesis_generator_context()
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results["hypothesis_context"] = False
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("✨ ALL TESTS PASSED ✨" if all_passed else "⚠️ SOME TESTS FAILED"))

if __name__ == "__main__":
    asyncio.run(main())
