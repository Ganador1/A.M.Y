#!/usr/bin/env python3
"""Test full paper enhancement pipeline."""
import asyncio
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'atlas')

from communication.paper_enhancer import PaperEnhancer

async def test_full_enhancement():
    enhancer = PaperEnhancer()
    
    # Simulate results from a physics mission
    results = [
        {'tool': 'quantum_energy_levels', 'description': 'Hydrogen n=3', 'result': 'Hydrogen atom energy level n=3: E_3 = -1.5111 eV', 'success': True},
        {'tool': 'quantum_energy_levels', 'description': 'Hydrogen n=5', 'result': 'Hydrogen atom energy level n=5: E_5 = -0.5440 eV', 'success': True},
    ]
    
    sections = [
        {'heading': 'Introduction', 'content': 'Study of Quantum Energy Analysis using computational methods.'},
        {'heading': 'Methods', 'content': 'Used 2 Atlas tools.'},
        {'heading': 'Results', 'content': '### Hydrogen n=3\nE_3 = -1.5111 eV\n\n### Hydrogen n=5\nE_5 = -0.5440 eV'},
        {'heading': 'Discussion', 'content': 'Results demonstrate computational verification.'},
        {'heading': 'Conclusion', 'content': 'Analysis confirms findings.'},
    ]
    
    enhanced = await enhancer.enhance_paper(
        domain='physics',
        topic='Quantum Energy Analysis',
        results=results,
        sections=sections,
        knowledge_facts=[{'subject': 'physics', 'predicate': 'analyzed', 'object': 'Atlas', 'confidence': 0.95}],
        experiment_ids=['physics_quantum_energy_levels_0', 'physics_quantum_energy_levels_1'],
    )
    
    print("=" * 70)
    print("ENHANCED PAPER PREVIEW")
    print("=" * 70)
    print(f"\n📝 ABSTRACT:\n{enhanced['abstract'][:300]}...")
    print(f"\n📚 REFERENCES ({len(enhanced['references'])}):")
    for r in enhanced['references']:
        print(f"  • {r[:80]}...")
    print(f"\n🔬 HYPOTHESES ({len(enhanced['hypotheses'])}):")
    for h in enhanced['hypotheses']:
        print(f"  • Conf: {h['confidence']:.0%} | {h['hypothesis'][:80]}...")
    print(f"\n📊 PEER REVIEW:")
    review = enhanced['peer_review']
    print(f"  Overall: {review['overall_score']}/10 - {review['decision']}")
    for criterion, score in review['scores'].items():
        print(f"  {criterion}: {score:.1f}/10")
    print(f"\n📄 SECTIONS:")
    for s in enhanced['sections']:
        content = s['content'][:100]
        print(f"  ## {s['heading']}")
        print(f"     {content}...")
    
    print("\n✅ Full enhancement pipeline works!")

asyncio.run(test_full_enhancement())