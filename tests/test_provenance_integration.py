#!/usr/bin/env python3
"""Test provenance + novelty + peer review integration."""
import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "atlas"))

from core.provenance import ProvenanceManager
from communication.paper_enhancer import PaperEnhancer, PeerReviewer, generate_hypothesis, DOMAIN_INSIGHTS
from run_amy_novelty import is_known_conjecture

print("=" * 60)
print("TEST 1: ProvenanceManager")
print("=" * 60)

pm = ProvenanceManager(base_dir=Path("data/experiments"))

# Record a fake execution
record = pm.record_execution(
    tool_name="prime_gap_analysis",
    tool_input="1000",
    tool_output="Prime gaps up to 1000: Mean gap: 6.09, Max gap: 20, Number of primes: 168",
    success=True,
    duration_seconds=0.5,
    domain="mathematics",
)
print(f"  ✅ Recorded: {record['experiment_id']}")
print(f"  📁 Path: {pm.get_provenance_path(record['experiment_id'])}")

# Verify it exists
verification = pm.verify_experiment_id(record['experiment_id'])
print(f"  🔍 Verified: exists={verification['exists']}")
assert verification['exists'], "Provenance file should exist!"

# Verify a non-existent ID
fake_verification = pm.verify_experiment_id("fake_nonexistent_id")
print(f"  🔍 Fake ID: exists={fake_verification['exists']}")
assert not fake_verification['exists'], "Fake ID should not exist!"

# List experiments
experiments = pm.list_experiments()
print(f"  📋 Total experiments on disk: {len(experiments)}")

print()
print("=" * 60)
print("TEST 2: Known Conjecture Filter")
print("=" * 60)

test_cases = [
    ("Goldbach conjecture: every even integer > 2 is the sum of two primes", True),
    ("Twin prime conjecture: infinitely many twin primes", True),
    ("Collatz conjecture: 3n+1 problem eventually reaches 1", True),
    ("Riemann hypothesis: all non-trivial zeros of zeta(s)", True),
    ("The Cramér model overestimates max prime gaps by factor 2.3x", False),
    ("HOMO-LUMO gap scales as 4.95/n + 1.15", False),
]

for text, expected in test_cases:
    result = is_known_conjecture(text)
    status = "✅" if result == expected else "❌"
    print(f"  {status} '{text[:50]}...' → known={result} (expected={expected})")

print()
print("=" * 60)
print("TEST 3: Peer Review with Provenance Verification")
print("=" * 60)

reviewer = PeerReviewer()

# Test with real provenance IDs
real_ids = [record['experiment_id']]
fake_ids = ["fake_id_1", "fake_id_2"]

# Review with real IDs
review_real = reviewer.review_paper(
    domain="mathematics",
    topic="Prime Gap Analysis",
    results=[{"tool": "prime_gap_analysis", "success": True, "result": "Mean gap: 6.09"}],
    sections=[{"heading": "Results", "content": "experiment data"}],
    hypotheses=[{"hypothesis": "Test", "confidence": 0.7, "testable": True, "method": "Test"}],
    references=["Ref1", "Ref2", "Ref3"],
    experiment_ids=real_ids,
)
print(f"  Real provenance: reproducibility={review_real['scores']['reproducibility']:.1f}")

# Review with fake IDs
review_fake = reviewer.review_paper(
    domain="mathematics",
    topic="Prime Gap Analysis",
    results=[{"tool": "prime_gap_analysis", "success": True, "result": "Mean gap: 6.09"}],
    sections=[{"heading": "Results", "content": "experiment data"}],
    hypotheses=[{"hypothesis": "Test", "confidence": 0.7, "testable": True, "method": "Test"}],
    references=["Ref1", "Ref2", "Ref3"],
    experiment_ids=fake_ids,
)
print(f"  Fake provenance: reproducibility={review_fake['scores']['reproducibility']:.1f}")

assert review_real['scores']['reproducibility'] > review_fake['scores']['reproducibility'], \
    "Real provenance should score higher than fake!"

print()
print("=" * 60)
print("TEST 4: Hypothesis Deduplication")
print("=" * 60)

# Multiple results from same tool type should generate only 1 hypothesis
results_same_tool = [
    {"tool": "prime_gap_analysis", "success": True, "result": "Mean gap: 6.09, Max gap: 20"},
    {"tool": "prime_gap_analysis", "success": True, "result": "Mean gap: 8.12, Max gap: 36"},
    {"tool": "prime_gap_analysis", "success": True, "result": "Mean gap: 9.15, Max gap: 72"},
]

hypotheses = generate_hypothesis("mathematics", results_same_tool)
print(f"  3 results from same tool → {len(hypotheses)} hypotheses (should be 1)")
assert len(hypotheses) <= 1, f"Should deduplicate to 1 hypothesis, got {len(hypotheses)}"

# Different tools should generate different hypotheses
results_diff_tools = [
    {"tool": "prime_gap_analysis", "success": True, "result": "Mean gap: 6.09"},
    {"tool": "sympy_derivative", "success": True, "result": "f'(x) = 3x²"},
    {"tool": "number_theory_advanced", "success": True, "result": "Goldbach verified"},
]

hypotheses2 = generate_hypothesis("mathematics", results_diff_tools)
print(f"  3 different tools → {len(hypotheses2)} hypotheses (should be 2-3)")
assert len(hypotheses2) >= 2, f"Should generate 2+ hypotheses for different tools, got {len(hypotheses2)}"

print()
print("=" * 60)
print("TEST 5: MO Discussion Match")
print("=" * 60)

enhancer = PaperEnhancer()
# Simulate MO results
mo_results = [
    {"tool": "molecular_orbital_energy", "success": True, "result": "HOMO: -4.887 eV, LUMO: -7.113 eV", "description": "4-carbon system"},
]

discussion = enhancer._build_discussion("chemistry", mo_results, DOMAIN_INSIGHTS["chemistry"])
has_mo_content = "Hückel" in discussion or "HOMO" in discussion or "orbital" in discussion.lower()
has_weight_content = "molecular weight" in discussion.lower() or "stoichiometric" in discussion.lower()
print(f"  Has MO content: {has_mo_content}")
print(f"  Has weight content (should be False): {has_weight_content}")
assert has_mo_content, "Discussion should mention MO/orbital content"
assert not has_weight_content, "Discussion should NOT mention molecular weight for MO tool"

print()
print("=" * 60)
print("ALL TESTS PASSED ✅")
print("=" * 60)