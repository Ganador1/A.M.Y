"""
Quick Literatura Search Test
==============================

Test rápido para validar que LiteratureAnalyzer funciona correctamente.
No requiere LLM ni todo el sistema de hipótesis - solo prueba el análisis de literatura.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import json
from datetime import datetime


async def test_literature_analyzer():
    """Test básico de LiteratureAnalyzer"""
    from app.services.literature_analyzer import LiteratureAnalyzer
    
    print("=" * 80)
    print("🧪 QUICK TEST: LiteratureAnalyzer")
    print("=" * 80)
    
    analyzer = LiteratureAnalyzer()
    
    # Test 1: Analyze biology domain
    print("\n📚 Test 1: Analyzing biology domain...")
    
    result = await analyzer.analyze_domain(
        domain='biology',
        year=2024,
        limit=10  # Small limit for speed
    )
    
    print(f"\n✅ Analysis complete!")
    print(f"   Papers fetched: {result['papers_count']}")
    print(f"   Topics extracted: {len(result['studied_topics'])}")
    print(f"   Gaps identified: {len(result['identified_gaps'])}")
    print(f"   Saturated keywords: {len(result['saturated_keywords'])}")
    
    # Print details
    print(f"\n📊 Top 5 studied topics:")
    for i, topic in enumerate(result['studied_topics'][:5], 1):
        print(f"   {i}. {topic}")
    
    print(f"\n🎯 Top 3 identified gaps:")
    for i, gap in enumerate(result['identified_gaps'][:3], 1):
        print(f"   {i}. {gap}")
    
    print(f"\n⚠️ Top 5 saturated keywords:")
    for i, keyword in enumerate(result['saturated_keywords'][:5], 1):
        print(f"   {i}. {keyword}")
    
    # Test 2: Validate novelty
    print("\n\n📈 Test 2: Validating novelty...")
    
    # Hypothesis 1: Muy similar a papers existentes (baja novelty esperada)
    hyp_low_novelty = {
        'title': "Protein expression and biological mechanisms",
        'description': "Study of protein regulation and biological systems analysis"
    }
    
    novelty_low = analyzer.validate_novelty(hyp_low_novelty, result['papers'])
    print(f"\n   Hypothesis A (generic): {hyp_low_novelty['title']}")
    print(f"   Novelty score: {novelty_low:.3f} (esperado: bajo ~0.2-0.4)")
    
    # Hypothesis 2: Muy específica y única (alta novelty esperada)
    hyp_high_novelty = {
        'title': "Circadian-metabolic-epigenetic tripartite coupling in pancreatic stellate cells",
        'description': "Investigation of temporal dynamics linking circadian rhythms, metabolic flux, and chromatin remodeling in pancreatic stellate cells during fibrosis"
    }
    
    novelty_high = analyzer.validate_novelty(hyp_high_novelty, result['papers'])
    print(f"\n   Hypothesis B (specific): {hyp_high_novelty['title']}")
    print(f"   Novelty score: {novelty_high:.3f} (esperado: alto ~0.6-0.9)")
    
    # Test 3: Papers summary
    print("\n\n📄 Test 3: Papers summary (first 5):")
    print(result['papers_summary'].split('\n')[:5])
    
    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'domain': 'biology',
        'papers_count': result['papers_count'],
        'topics_count': len(result['studied_topics']),
        'gaps_count': len(result['identified_gaps']),
        'saturated_count': len(result['saturated_keywords']),
        'novelty_test': {
            'generic_hypothesis': {
                'title': hyp_low_novelty['title'],
                'novelty': novelty_low
            },
            'specific_hypothesis': {
                'title': hyp_high_novelty['title'],
                'novelty': novelty_high
            }
        },
        'topics': result['studied_topics'][:10],
        'gaps': result['identified_gaps'][:5],
        'saturated': result['saturated_keywords'][:10]
    }
    
    output_file = f"quick_test_literatura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n\n💾 Results saved to: {output_file}")
    
    # Success check
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    
    success_checks = []
    
    # Check 1: Papers fetched
    if result['papers_count'] >= 5:
        print("✅ Papers fetched successfully")
        success_checks.append(True)
    else:
        print("⚠️ Few papers fetched (may be fallback mode)")
        success_checks.append(False)
    
    # Check 2: Topics extracted
    if len(result['studied_topics']) >= 5:
        print("✅ Topics extracted successfully")
        success_checks.append(True)
    else:
        print("❌ Topic extraction failed")
        success_checks.append(False)
    
    # Check 3: Gaps identified
    if len(result['identified_gaps']) >= 3:
        print("✅ Gaps identified successfully")
        success_checks.append(True)
    else:
        print("⚠️ Limited gaps identified")
        success_checks.append(False)
    
    # Check 4: Novelty validation works
    if novelty_high > novelty_low:
        print(f"✅ Novelty validation works (specific > generic: {novelty_high:.2f} > {novelty_low:.2f})")
        success_checks.append(True)
    else:
        print(f"❌ Novelty validation failed (expected specific > generic)")
        success_checks.append(False)
    
    if all(success_checks):
        print("\n🎉 ALL TESTS PASSED!")
        return True
    elif sum(success_checks) >= 3:
        print(f"\n⚠️ PARTIAL SUCCESS ({sum(success_checks)}/4 checks passed)")
        return True
    else:
        print(f"\n❌ TESTS FAILED ({sum(success_checks)}/4 checks passed)")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_literature_analyzer())
    sys.exit(0 if success else 1)
