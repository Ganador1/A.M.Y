#!/usr/bin/env python3
"""
Test de servicios de mejora: References Generator + Statistical Analysis
Valida que los nuevos servicios funcionan correctamente
"""

import sys
import json
from pathlib import Path

# Agregar app al path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.reference_generator import (
    ReferenceGeneratorService,
    add_references_to_paper
)
from app.services.statistical_analysis import (
    StatisticalAnalysisService,
    enhance_paper_with_statistics,
    extract_numerical_results
)


def test_reference_generator():
    """Test generación de referencias"""
    print("\n" + "="*80)
    print("TEST 1: REFERENCE GENERATOR SERVICE")
    print("="*80)
    
    # Simular tool evidence
    tool_evidence = {
        "evidence_items": [
            {
                "tool_name": "pubmed",
                "metadata": {
                    "title": "Deep learning for medical image analysis",
                    "authors": "Smith, J. et al.",
                    "year": "2023",
                    "journal": "Nature Medicine",
                    "pmid": "37123456"
                },
                "content": "We present a novel deep learning approach...",
                "signal_strength": 0.92
            },
            {
                "tool_name": "arxiv",
                "metadata": {
                    "title": "Quantum error correction in NISQ devices",
                    "authors": "Doe, A. and Lee, B.",
                    "year": "2024",
                    "arxiv_id": "2401.12345"
                },
                "content": "Quantum computing in the NISQ era...",
                "signal_strength": 0.85
            },
            {
                "tool_name": "crossref",
                "metadata": {
                    "title": "Molecular dynamics of protein folding",
                    "authors": "Garcia, M. et al.",
                    "year": "2023",
                    "journal": "Science",
                    "doi": "10.1126/science.abc1234"
                },
                "content": "Protein folding simulations reveal...",
                "signal_strength": 0.88
            }
        ]
    }
    
    # Generar referencias
    generator = ReferenceGeneratorService()
    
    # Test estilo APA
    print("\n📚 Estilo APA:")
    print("-" * 80)
    references_apa = generator.generate_references_section(
        tool_evidence=tool_evidence,
        domain="neuroscience",
        style="APA"
    )
    print(references_apa)
    
    # Test estilo IEEE
    print("\n📚 Estilo IEEE:")
    print("-" * 80)
    references_ieee = generator.generate_references_section(
        tool_evidence=tool_evidence,
        domain="physics",
        style="IEEE"
    )
    print(references_ieee)
    
    # Test estilo Nature
    print("\n📚 Estilo Nature:")
    print("-" * 80)
    references_nature = generator.generate_references_section(
        tool_evidence=tool_evidence,
        domain="chemistry",
        style="Nature"
    )
    print(references_nature)
    
    # Verificación
    assert "## References" in references_apa, "❌ No se generó sección References"
    assert "Smith, J." in references_apa, "❌ No se encontró autor Smith"
    assert "Doe, A." in references_apa, "❌ No se encontró autor Doe"
    assert "10.1126/science.abc1234" in references_apa, "❌ No se encontró DOI"
    
    print("\n✅ TEST 1 PASADO - Reference Generator funciona correctamente")
    return True


def test_statistical_analysis():
    """Test análisis estadístico"""
    print("\n" + "="*80)
    print("TEST 2: STATISTICAL ANALYSIS SERVICE")
    print("="*80)
    
    # Datos experimentales simulados
    accuracy_values = [0.891, 0.895, 0.889, 0.893, 0.890]
    f1_values = [0.875, 0.881, 0.878, 0.880, 0.876]
    precision_values = [0.912, 0.915, 0.910, 0.914, 0.911]
    
    service = StatisticalAnalysisService()
    
    # Test error bounds
    print("\n📊 Error Bounds:")
    print("-" * 80)
    acc_stats = service.calculate_error_bounds(accuracy_values, confidence_level=95)
    print(f"Mean: {acc_stats.mean:.4f}")
    print(f"Std Dev: {acc_stats.std_dev:.4f}")
    print(f"Std Error: {acc_stats.std_error:.4f}")
    print(f"95% CI: [{acc_stats.confidence_interval_95[0]:.4f}, {acc_stats.confidence_interval_95[1]:.4f}]")
    print(f"Sample Size: n = {acc_stats.sample_size}")
    
    # Test p-value
    print("\n📊 T-Test (Accuracy vs F1):")
    print("-" * 80)
    p_value = service.calculate_p_value_ttest(accuracy_values, f1_values)
    print(f"p-value: {p_value:.4f}")
    print(f"Significant: {'YES' if p_value < 0.05 else 'NO'} (α=0.05)")
    
    # Test effect size
    print("\n📊 Effect Size (Cohen's d):")
    print("-" * 80)
    effect_size = service.calculate_effect_size_cohens_d(accuracy_values, f1_values)
    print(f"Cohen's d: {effect_size:.4f}")
    magnitude = "SMALL" if effect_size < 0.2 else "MEDIUM" if effect_size < 0.5 else "LARGE"
    print(f"Magnitude: {magnitude}")
    
    # Test Bayesian credible interval
    print("\n📊 Bayesian Credible Interval:")
    print("-" * 80)
    credible_interval = service.calculate_bayesian_credible_interval(
        accuracy_values,
        prior_mean=0.85,
        prior_std=0.1
    )
    print(f"95% Credible Interval: [{credible_interval[0]:.4f}, {credible_interval[1]:.4f}]")
    
    # Test generación de sección completa
    print("\n📊 Sección Estadística Completa:")
    print("-" * 80)
    results_data = {
        "accuracy": accuracy_values,
        "f1_score": f1_values,
        "precision": precision_values
    }
    
    stats_section = service.generate_statistical_analysis_section(
        results_data,
        domain="machine_learning"
    )
    print(stats_section)
    
    # Verificaciones
    assert acc_stats.sample_size == 5, "❌ Sample size incorrecto"
    assert 0.889 < acc_stats.mean < 0.893, "❌ Mean fuera de rango"
    assert acc_stats.std_dev > 0, "❌ Std dev debe ser > 0"
    assert len(acc_stats.confidence_interval_95) == 2, "❌ CI debe tener 2 valores"
    assert "Statistical Analysis and Error Bounds" in stats_section, "❌ Falta título de sección"
    assert "95% Confidence Interval" in stats_section, "❌ Falta confidence interval"
    
    print("\n✅ TEST 2 PASADO - Statistical Analysis funciona correctamente")
    return True


def test_integration_paper_enhancement():
    """Test integración completa: agregar referencias y estadísticas a un paper"""
    print("\n" + "="*80)
    print("TEST 3: INTEGRACIÓN COMPLETA - PAPER ENHANCEMENT")
    print("="*80)
    
    # Paper de ejemplo (simplificado)
    sample_paper = """# Quantum Error Correction in NISQ Devices

## Abstract
We present a novel approach to quantum error correction in Noisy Intermediate-Scale Quantum (NISQ) devices...

## Introduction
Quantum computing promises exponential speedup for certain computational problems...

## Methods
We implemented variational quantum eigensolver (VQE) algorithms on superconducting qubits...

## Results
Our experiments achieved the following metrics:
- Accuracy: 0.891
- F1 Score: 0.875
- Precision: 0.912

Additional runs showed accuracy: 0.895, 0.889, 0.893, 0.890.

## Discussion
The results demonstrate significant improvements over baseline methods...

## Conclusions
We have successfully demonstrated quantum error correction in NISQ devices...
"""
    
    # Tool evidence simulado
    tool_evidence = {
        "evidence_items": [
            {
                "tool_name": "arxiv",
                "metadata": {
                    "title": "Quantum error correction codes",
                    "authors": "Preskill, J.",
                    "year": "2018",
                    "arxiv_id": "1801.00862"
                },
                "content": "Review of quantum error correction...",
                "signal_strength": 0.95
            }
        ]
    }
    
    # Paso 1: Agregar referencias
    print("\n📚 Agregando referencias...")
    paper_with_refs = add_references_to_paper(
        paper_text=sample_paper,
        tool_evidence=tool_evidence,
        domain="physics",
        style="APA"
    )
    
    # Paso 2: Agregar análisis estadístico
    print("\n📊 Agregando análisis estadístico...")
    results_data = {
        "accuracy": [0.891, 0.895, 0.889, 0.893, 0.890],
        "f1_score": [0.875],
        "precision": [0.912]
    }
    
    final_paper = enhance_paper_with_statistics(
        paper_text=paper_with_refs,
        results_data=results_data
    )
    
    # Mostrar resultado
    print("\n" + "="*80)
    print("PAPER MEJORADO (EXTRACTO):")
    print("="*80)
    
    # Mostrar solo las secciones nuevas
    if "### Statistical Analysis" in final_paper:
        stats_start = final_paper.index("### Statistical Analysis")
        print(final_paper[stats_start:stats_start + 500] + "...\n")
    
    if "## References" in final_paper:
        refs_start = final_paper.index("## References")
        print(final_paper[refs_start:refs_start + 400] + "...\n")
    
    # Verificaciones
    assert "## References" in final_paper, "❌ No se agregaron referencias"
    assert "Statistical Analysis" in final_paper, "❌ No se agregó análisis estadístico"
    assert "95% Confidence Interval" in final_paper, "❌ Falta confidence interval"
    assert "Preskill" in final_paper, "❌ No se encontró referencia de Preskill"
    
    print("✅ TEST 3 PASADO - Integración completa funciona correctamente")
    
    # Guardar paper mejorado
    output_file = Path(__file__).parent / "test_enhanced_paper.md"
    output_file.write_text(final_paper)
    print(f"\n💾 Paper mejorado guardado en: {output_file}")
    
    return True


def test_extraction_utilities():
    """Test utilidades de extracción"""
    print("\n" + "="*80)
    print("TEST 4: UTILIDADES DE EXTRACCIÓN")
    print("="*80)
    
    # Texto con resultados numéricos
    sample_text = """
    Our experiments achieved accuracy: 0.891 and F1 score = 0.875.
    The precision was 0.912, while recall = 0.850.
    Training loss: 0.123 and validation loss: 0.145.
    """
    
    # Extraer resultados
    print("\n🔍 Extrayendo resultados numéricos...")
    results = extract_numerical_results(sample_text)
    
    print(f"Resultados extraídos: {json.dumps(results, indent=2)}")
    
    # Verificaciones
    assert "accuracy" in results, "❌ No se extrajo accuracy"
    assert "f1_score" in results or "f1" in results, "❌ No se extrajo F1 score"
    assert len(results) > 0, "❌ No se extrajeron resultados"
    
    print("\n✅ TEST 4 PASADO - Extracción de resultados funciona correctamente")
    return True


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*80)
    print("🧪 INICIANDO TEST SUITE - SERVICIOS DE MEJORA")
    print("="*80)
    
    tests = [
        ("Reference Generator", test_reference_generator),
        ("Statistical Analysis", test_statistical_analysis),
        ("Integration - Paper Enhancement", test_integration_paper_enhancement),
        ("Extraction Utilities", test_extraction_utilities)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results[test_name] = "✅ PASADO" if success else "❌ FALLIDO"
        except Exception as e:
            print(f"\n❌ ERROR EN {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = f"❌ ERROR: {str(e)}"
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*80)
    
    for test_name, result in results.items():
        print(f"{test_name:.<50} {result}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if "✅" in r)
    
    print("\n" + "="*80)
    print(f"TESTS PASADOS: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 TODOS LOS TESTS PASARON - SERVICIOS LISTOS PARA PRODUCCIÓN")
    else:
        print("⚠️ ALGUNOS TESTS FALLARON - REVISAR ERRORES")
    
    print("="*80)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
