#!/usr/bin/env python3
"""
Test final del AdvancedHypothesisValidator integrado.
Valida hipótesis científicas reales usando herramientas POPPER + ToolUniverse.
"""
import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project path dynamically
sys.path.insert(0, str(Path(__file__).resolve().parent))

async def main():
    print("=" * 70)
    print("🔬 AXIOM ATLAS - Test de Validación Avanzada de Hipótesis")
    print("   Integración: POPPER (Stanford) + ToolUniverse (Harvard)")
    print("=" * 70)
    
    from app.services.advanced_hypothesis_validator import AdvancedHypothesisValidator
    
    validator = AdvancedHypothesisValidator(alpha=0.1, max_tests=3)
    results = []
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 1: Química - Lipofilicidad de Cafeína
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("📋 TEST 1: Química - Lipofilicidad de Cafeína")
    print("─" * 70)
    
    result1 = await validator.validate_hypothesis(
        hypothesis="Caffeine has moderate lipophilicity with LogP between -0.5 and 0.5",
        domain="chemistry",
        test_specifications=[
            {
                "name": "Lipinski Rules Check",
                "tool": "lipinski_rules",
                "parameters": {"smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"},
                "null_hypothesis": "Molecule violates Lipinski rules",
                "alternative_hypothesis": "Molecule passes Lipinski rules"
            },
            {
                "name": "Molecular Descriptors",
                "tool": "molecular_descriptors", 
                "parameters": {"smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"},
                "null_hypothesis": "LogP outside range",
                "alternative_hypothesis": "LogP in expected range"
            }
        ]
    )
    
    print(f"   ✓ Hipótesis: {result1.hypothesis[:50]}...")
    print(f"   ✓ Estado: {result1.status.value}")
    print(f"   ✓ Confianza: {result1.confidence:.2%}")
    print(f"   ✓ p-value combinado: {result1.combined_p_value:.6f}" if result1.combined_p_value else "   ✓ p-value: N/A")
    print(f"   ✓ Tests ejecutados: {len(result1.tests_run)}")
    for t in result1.tests_run:
        p_str = f"p={t.p_value:.4f}" if t.p_value else "error"
        print(f"      └─ {t.test_name}: {p_str}")
    results.append(result1)
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 2: Materiales - Conductividad Térmica
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("📋 TEST 2: Materiales - Conductividad Térmica de Compuesto")
    print("─" * 70)
    
    result2 = await validator.validate_hypothesis(
        hypothesis="Copper-diamond composite has thermal conductivity > 400 W/mK",
        domain="materials",
        test_specifications=[
            {
                "name": "Thermal Conductivity Model",
                "tool": "thermal_conductivity",
                "parameters": {
                    "matrix_k": 400,      # Cobre W/mK
                    "filler_k": 2000,     # Diamante W/mK
                    "filler_fraction": 0.3
                },
                "null_hypothesis": "Conductivity <= 400 W/mK",
                "alternative_hypothesis": "Conductivity > 400 W/mK"
            }
        ]
    )
    
    print(f"   ✓ Hipótesis: {result2.hypothesis[:50]}...")
    print(f"   ✓ Estado: {result2.status.value}")
    print(f"   ✓ Confianza: {result2.confidence:.2%}")
    print(f"   ✓ p-value combinado: {result2.combined_p_value:.6f}" if result2.combined_p_value else "   ✓ p-value: N/A")
    print(f"   ✓ Tests ejecutados: {len(result2.tests_run)}")
    for t in result2.tests_run:
        p_str = f"p={t.p_value:.4f}" if t.p_value else "error"
        print(f"      └─ {t.test_name}: {p_str}")
    results.append(result2)
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 3: Biología - Contenido GC de Secuencia
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("📋 TEST 3: Biología - Contenido GC de Secuencia")
    print("─" * 70)
    
    result3 = await validator.validate_hypothesis(
        hypothesis="The DNA sequence has GC content above 50%",
        domain="biology",
        test_specifications=[
            {
                "name": "Sequence GC Analysis",
                "tool": "sequence_analysis",
                "parameters": {"sequence": "ATGCGCGCATGCGCGCATGCGCGCATGCGCGC"},
                "null_hypothesis": "GC content <= 50%",
                "alternative_hypothesis": "GC content > 50%"
            }
        ]
    )
    
    print(f"   ✓ Hipótesis: {result3.hypothesis[:50]}...")
    print(f"   ✓ Estado: {result3.status.value}")
    print(f"   ✓ Confianza: {result3.confidence:.2%}")
    print(f"   ✓ p-value combinado: {result3.combined_p_value:.6f}" if result3.combined_p_value else "   ✓ p-value: N/A")
    print(f"   ✓ Tests ejecutados: {len(result3.tests_run)}")
    for t in result3.tests_run:
        p_str = f"p={t.p_value:.4f}" if t.p_value else "error"
        print(f"      └─ {t.test_name}: {p_str}")
    results.append(result3)
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 4: Estadístico - Normalidad de Datos
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("📋 TEST 4: Estadístico - Test de Normalidad")
    print("─" * 70)
    
    import numpy as np
    np.random.seed(42)
    normal_data = np.random.normal(100, 15, 100).tolist()
    
    result4 = await validator.validate_hypothesis(
        hypothesis="The experimental data follows a normal distribution",
        domain="statistics",
        test_specifications=[
            {
                "name": "Shapiro-Wilk Normality Test",
                "tool": "statistical_tests",
                "parameters": {
                    "data": normal_data,
                    "test_type": "normality"
                },
                "null_hypothesis": "Data is not normally distributed",
                "alternative_hypothesis": "Data is normally distributed"
            }
        ]
    )
    
    print(f"   ✓ Hipótesis: {result4.hypothesis[:50]}...")
    print(f"   ✓ Estado: {result4.status.value}")
    print(f"   ✓ Confianza: {result4.confidence:.2%}")
    print(f"   ✓ p-value combinado: {result4.combined_p_value:.6f}" if result4.combined_p_value else "   ✓ p-value: N/A")
    print(f"   ✓ Tests ejecutados: {len(result4.tests_run)}")
    for t in result4.tests_run:
        p_str = f"p={t.p_value:.4f}" if t.p_value else "error"
        print(f"      └─ {t.test_name}: {p_str}")
    results.append(result4)
    
    # ═══════════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL - VALIDACIÓN AVANZADA DE HIPÓTESIS")
    print("=" * 70)
    
    from app.services.advanced_hypothesis_validator import HypothesisStatus
    validated_count = sum(1 for r in results if r.status == HypothesisStatus.VALIDATED)
    total_tests = len(results)
    
    print(f"\n   🎯 Hipótesis validadas: {validated_count}/{total_tests}")
    print(f"   📈 Tasa de validación: {validated_count/total_tests*100:.1f}%")
    print(f"   🔬 Nivel de significancia: α = {validator.alpha}")
    print(f"   📐 Método de agregación: {validator.aggregation_method}")
    
    print("\n   Detalle por hipótesis:")
    for r in results:
        status = "✅" if r.status == HypothesisStatus.VALIDATED else "❌"
        p_str = f"p={r.combined_p_value:.6f}" if r.combined_p_value else "N/A"
        print(f"      {status} {r.hypothesis[:40]}...: {p_str}")
    
    # Guardar resultados
    output = {
        "timestamp": datetime.now().isoformat(),
        "validator_config": {
            "alpha": validator.alpha,
            "max_tests": validator.max_tests,
            "aggregation_method": validator.aggregation_method
        },
        "summary": {
            "total": total_tests,
            "validated": validated_count,
            "rate": validated_count / total_tests
        },
        "results": [r.to_dict() for r in results]
    }
    
    output_file = f"advanced_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n   💾 Resultados guardados en: {output_file}")
    print("\n" + "=" * 70)
    print("✅ INTEGRACIÓN POPPER + TOOLUNIVERSE + AXIOM COMPLETADA")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
