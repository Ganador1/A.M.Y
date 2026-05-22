#!/usr/bin/env python3
"""Test enhanced paper generation end-to-end."""
import asyncio
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'atlas')

from communication.paper_generator import PaperGenerator

async def test_enhanced_paper():
    pg = PaperGenerator(reasoning_engine=None, enhance=True)
    
    results = [
        {'tool': 'prime_gap_analysis', 'description': 'Prime gap distribution', 'result': 'Prime gap analysis up to 1000: Number of primes: 168, Mean gap: 5.9581, Std dev: 3.5467, Max gap: 20', 'success': True},
        {'tool': 'sympy_derivative', 'description': 'Derivative calculation', 'result': 'Derivative: 3*x**2', 'success': True},
        {'tool': 'number_theory_advanced', 'description': 'Goldbach conjecture', 'result': 'Goldbach Conjecture Verification for n in [4, 100]: Status: All even numbers verified', 'success': True},
    ]
    
    sections = [
        {'heading': 'Introduction', 'content': 'Study of Mathematical Analysis using computational methods.'},
        {'heading': 'Methods', 'content': 'Used 3 Atlas tools.'},
        {'heading': 'Results', 'content': '### Prime gap distribution\n168 primes found\n\n### Derivative\n3*x**2\n\n### Goldbach\nAll verified'},
        {'heading': 'Discussion', 'content': 'Results demonstrate computational verification.'},
        {'heading': 'Conclusion', 'content': 'Analysis confirms findings.'},
    ]
    
    paper = await pg.generate_paper(
        title="Computational Analysis of Mathematical Analysis",
        abstract="Analysis of Mathematical Analysis using 3 computational tools.",
        sections=sections,
        references=["A.M.Y (2026). AXIOM Atlas Platform."],
        knowledge_facts=[{"subject": "mathematics", "predicate": "analyzed", "object": "Atlas", "confidence": 0.95}],
        experiment_ids=["math_prime_gap_0", "math_derivative_1", "math_goldbach_2"],
        domain="mathematics",
        tool_results=results,
    )
    
    print(f"📄 Paper generated: {paper['word_count']} words")
    print(f"📁 Markdown: {paper['markdown_path']}")
    print(f"📁 PDF: {paper['pdf_path']}")
    
    # Read and show the paper
    from pathlib import Path
    md_path = Path(paper['markdown_path'])
    content = md_path.read_text()
    
    print("\n" + "=" * 70)
    print("ENHANCED PAPER CONTENT")
    print("=" * 70)
    print(content[:3000])
    print("...")
    print(f"\n[Total: {len(content)} chars, {len(content.split())} words]")

asyncio.run(test_enhanced_paper())