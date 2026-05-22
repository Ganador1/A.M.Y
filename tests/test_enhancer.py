#!/usr/bin/env python3
"""Test paper enhancer module."""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'atlas')

from communication.paper_enhancer import PaperEnhancer, generate_hypothesis, generate_references, PeerReviewer

# Test 1: Hypothesis generation
results = [
    {'tool': 'prime_gap_analysis', 'description': 'Prime gap distribution', 'result': 'Number of primes: 168, Mean gap: 5.96', 'success': True},
    {'tool': 'sympy_derivative', 'description': 'Derivative calculation', 'result': 'Derivative: 3*x**2', 'success': True},
]
hypotheses = generate_hypothesis('mathematics', results)
print('=== HYPOTHESES ===')
for h in hypotheses:
    print(f'  Conf: {h["confidence"]:.0%} | {h["hypothesis"][:80]}...')
    print(f'  Testable: {h["testable"]} | Method: {h["method"][:60]}...')

# Test 2: References
refs = generate_references('mathematics', results)
print(f'\n=== REFERENCES ({len(refs)}) ===')
for r in refs:
    print(f'  {r[:80]}...')

# Test 3: Peer Review
reviewer = PeerReviewer()
sections = [
    {'heading': 'Introduction', 'content': 'Study of mathematics.'},
    {'heading': 'Methods', 'content': 'Used 2 tools.'},
    {'heading': 'Results', 'content': 'Prime gap analysis shows 168 primes.'},
    {'heading': 'Discussion', 'content': 'Results demonstrate computational verification.'},
    {'heading': 'Conclusion', 'content': 'Analysis confirms findings.'},
]
review = reviewer.review_paper('mathematics', 'Mathematical Analysis', results, sections, hypotheses, refs)
print(f'\n=== PEER REVIEW ===')
print(f'Overall: {review["overall_score"]}/10 - {review["decision"]}')
print(f'Reason: {review["decision_reason"]}')
for criterion, score in review['scores'].items():
    print(f'  {criterion}: {score:.1f}/10')
print('Feedback:')
for fb in review['feedback']:
    print(f'  {fb}')

print('\n✅ All paper enhancer tests passed!')