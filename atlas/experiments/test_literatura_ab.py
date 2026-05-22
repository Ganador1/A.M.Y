"""
A/B Test: Literatura Search Impact
====================================

Compara la generación de hipótesis CON y SIN literatura search.

Baseline (A): Sin literatura search (sistema actual)
Treatment (B): Con literatura search (nuevo sistema)

Métrica principal: Keyword overlap con papers existentes
- Baseline esperado: ~60-80% overlap (alta duplicación)
- Treatment esperado: ~20-40% overlap (baja duplicación)
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Any

from app.services.literature_analyzer import LiteratureAnalyzer
from app.autonomous.generators.hypothesis_generator import HypothesisGenerator


async def generate_hypothesis_baseline(domain: str) -> Dict[str, Any]:
    """
    Generación BASELINE: Sin literatura search (sistema actual).
    
    Returns:
        Hypothesis dict con title, description, novelty_score
    """
    print("\n🔵 [BASELINE] Generando hipótesis sin literatura...")
    
    generator = HypothesisGenerator()
    
    context = {
        'mode': 'autonomous',
        'use_real_services': False,  # Offline mode
        'novelty_threshold': 0.7,
        'require_evidence': True,
        'enable_literature_search': False  # CRÍTICO: Deshabilitar literatura search para baseline
    }
    
    hypothesis = await generator.generate_hypothesis(domain, context)
    
    print(f"   ✅ Hipótesis generada: {hypothesis.get('title', 'N/A')[:80]}")
    print(f"   📊 Novelty (self-reported): {hypothesis.get('novelty_score', 0):.2f}")
    
    return hypothesis


async def generate_hypothesis_treatment(domain: str) -> Dict[str, Any]:
    """
    Generación TREATMENT: CON literatura search (nuevo sistema).
    
    Returns:
        Hypothesis dict con title, description, novelty_score, literature_context
    """
    print(f"\n🟢 [TREATMENT] Generando hipótesis con literatura...")
    
    # Step 1: Analyze literatura
    analyzer = LiteratureAnalyzer()
    lit_analysis = await analyzer.analyze_domain(domain, year=2024, limit=20)
    
    print(f"   📚 Literatura encontrada: {lit_analysis['papers_count']} papers")
    print(f"   🎯 Gaps identificados: {len(lit_analysis['identified_gaps'])}")
    print(f"   ⚠️ Keywords saturados: {len(lit_analysis['saturated_keywords'])}")
    
    # Step 2: Build literatura context for prompt
    literature_context = {
        'papers_summary': lit_analysis['papers_summary'],
        'studied_topics': lit_analysis['studied_topics'][:15],
        'identified_gaps': lit_analysis['identified_gaps'][:5],
        'saturated_keywords': lit_analysis['saturated_keywords'][:10]
    }
    
    # Step 3: Generate hypothesis with literatura context
    generator = HypothesisGenerator()
    
    context = {
        'mode': 'autonomous',
        'use_real_services': False,
        'novelty_threshold': 0.7,
        'require_evidence': True,
        'literature_context': literature_context  # NUEVO
    }
    
    hypothesis = await generator.generate_hypothesis(domain, context)
    
    # Step 4: Validate novelty
    validated_novelty = analyzer.validate_novelty(hypothesis, lit_analysis['papers'])
    
    hypothesis['validated_novelty'] = validated_novelty
    hypothesis['literature_context'] = literature_context
    
    print(f"   ✅ Hipótesis generada: {hypothesis.get('title', 'N/A')[:80]}")
    print(f"   📊 Novelty (self-reported): {hypothesis.get('novelty_score', 0):.2f}")
    print(f"   📈 Novelty (validated): {validated_novelty:.2f}")
    
    return hypothesis


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text (words ≥6 chars)"""
    return list(set(re.findall(r'\b[a-z]{6,}\b', text.lower())))


def calculate_overlap_ratio(
    hypothesis: Dict,
    papers: List[Dict]
) -> float:
    """
    Calculate keyword overlap ratio.
    
    Returns:
        Ratio 0.0-1.0 (1.0 = 100% overlap = muy duplicado)
    """
    # Extract hypothesis keywords
    hyp_text = (
        hypothesis.get('title', '') + ' ' +
        hypothesis.get('description', '')
    )
    hyp_keywords = set(extract_keywords(hyp_text))
    
    if not hyp_keywords:
        return 0.0
    
    # Extract papers keywords
    papers_keywords = set()
    for paper in papers:
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')[:300]
        
        keywords = extract_keywords(title + ' ' + abstract)
        papers_keywords.update(keywords)
    
    # Calculate overlap
    overlap = hyp_keywords & papers_keywords
    
    ratio = len(overlap) / len(hyp_keywords)
    
    return ratio


async def run_ab_test(domain: str = 'biology') -> Dict[str, Any]:
    """
    Ejecuta test A/B completo.
    
    Returns:
        Dict con resultados comparativos
    """
    print("=" * 80)
    print("🧪 INICIANDO TEST A/B: LITERATURA SEARCH IMPACT")
    print("=" * 80)
    print(f"📋 Domain: {domain}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Fetch papers una sola vez (para comparación justa)
    print("📚 Obteniendo papers de referencia...")
    analyzer = LiteratureAnalyzer()
    reference_papers = await analyzer.fetch_recent_papers(domain, year=2024, limit=20)
    print(f"   ✅ {len(reference_papers)} papers fetched")
    
    # ========================================
    # Test A: BASELINE (sin literatura)
    # ========================================
    baseline_hyp = await generate_hypothesis_baseline(domain)
    
    baseline_overlap = calculate_overlap_ratio(baseline_hyp, reference_papers)
    baseline_keywords = extract_keywords(
        baseline_hyp.get('title', '') + ' ' + baseline_hyp.get('description', '')
    )
    
    print(f"\n📊 [BASELINE] Overlap ratio: {baseline_overlap:.2%}")
    print(f"   Keywords totales: {len(baseline_keywords)}")
    print(f"   Overlap con papers: {int(baseline_overlap * len(baseline_keywords))}/{len(baseline_keywords)}")
    
    # ========================================
    # Test B: TREATMENT (con literatura)
    # ========================================
    treatment_hyp = await generate_hypothesis_treatment(domain)
    
    treatment_overlap = calculate_overlap_ratio(treatment_hyp, reference_papers)
    treatment_keywords = extract_keywords(
        treatment_hyp.get('title', '') + ' ' + treatment_hyp.get('description', '')
    )
    
    print(f"\n📊 [TREATMENT] Overlap ratio: {treatment_overlap:.2%}")
    print(f"   Keywords totales: {len(treatment_keywords)}")
    print(f"   Overlap con papers: {int(treatment_overlap * len(treatment_keywords))}/{len(treatment_keywords)}")
    
    # ========================================
    # COMPARISON
    # ========================================
    overlap_reduction = (baseline_overlap - treatment_overlap) / baseline_overlap if baseline_overlap > 0 else 0
    novelty_improvement = treatment_hyp.get('validated_novelty', 0) - baseline_hyp.get('novelty_score', 0)
    
    print("\n" + "=" * 80)
    print("📈 RESULTADOS COMPARATIVOS")
    print("=" * 80)
    print(f"Overlap reduction: {overlap_reduction:.1%}")
    print(f"Novelty improvement: {novelty_improvement:+.2f} points")
    
    # Success criteria
    success = False
    if overlap_reduction >= 0.30 and novelty_improvement >= 0.20:
        print("\n✅ ÉXITO TOTAL: Literatura search mejora significativamente la novelty")
        success = True
    elif overlap_reduction >= 0.10 or novelty_improvement >= 0.10:
        print("\n⚠️ ÉXITO PARCIAL: Mejora modesta, revisar parámetros")
        success = True
    else:
        print("\n❌ FALLO: No hay mejora significativa")
    
    # Build result
    result = {
        'test_id': f"ab_test_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'domain': domain,
        'timestamp': datetime.now().isoformat(),
        'reference_papers_count': len(reference_papers),
        'baseline': {
            'hypothesis': baseline_hyp,
            'overlap_ratio': baseline_overlap,
            'keywords_count': len(baseline_keywords),
            'novelty_score': baseline_hyp.get('novelty_score', 0)
        },
        'treatment': {
            'hypothesis': treatment_hyp,
            'overlap_ratio': treatment_overlap,
            'keywords_count': len(treatment_keywords),
            'novelty_score': treatment_hyp.get('validated_novelty', 0)
        },
        'comparison': {
            'overlap_reduction': overlap_reduction,
            'novelty_improvement': novelty_improvement,
            'success': success
        }
    }
    
    return result


async def main():
    """Run A/B test"""
    result = await run_ab_test(domain='biology')
    
    # Save results
    output_file = f"ab_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("📋 RESUMEN EJECUTIVO")
    print("=" * 80)
    print(f"✅ Test completado: {result['test_id']}")
    print(f"📊 Overlap reduction: {result['comparison']['overlap_reduction']:.1%}")
    print(f"📈 Novelty improvement: {result['comparison']['novelty_improvement']:+.2f}")
    print(f"🎯 Success: {result['comparison']['success']}")
    
    return result


if __name__ == "__main__":
    asyncio.run(main())
