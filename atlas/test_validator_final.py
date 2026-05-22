#!/usr/bin/env python3
"""
Test final del AdvancedHypothesisValidator integrado.
Valida hipótesis científicas reales usando herramientas POPPER + ToolUniverse.
"""
import sys
import json
from datetime import datetime

# Add project path
sys.path.insert(0, '/Volumes/Ganador disk/atlas')

def main():
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
    
    result1 = validator.validate_hypothesis(
        hypothesis_text="Caffeine has moderate lipophilicity with LogP between -0.5 and 0.5",
        domain="chemistry",
        tools_to_use=["lipinski_rules", "molecular_descriptors"],
        test_data={
            "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Cafeína
            "property": "LogP",
            "expected_range": (-0.5, 0.5)
        }
    )
    
    print(f"   ✓ Hipótesis: {result1['hypothesis'][:50]}...")
    print(f"   ✓ Validada: {'✅ SÍ' if result1['validated'] else '❌ NO'}")
    print(f"   ✓ p-value combinado: {result1['combined_p']:.6f}")
    print(f"   ✓ Método agregación: {result1['aggregation_method']}")
    print(f"   ✓ Tests ejecutados: {len(result1['tests_executed'])}")
    for t in result1['tests_executed']:
        print(f"      └─ {t['tool']}: p={t['p_value']:.4f}")
    results.append({"test": "Caffeine LogP", **result1})
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 2: Materiales - Conductividad Térmica
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("📋 TEST 2: Materiales - Conductividad Térmica de Compuesto")
    print("─" * 70)
    
    result2 = validator.validate_hypothesis(
        hypothesis_text="Copper-diamond composite has thermal conductivity > 400 W/mK",
        domain="materials",
        tools_to_use=["thermal_conductivity", "statistical_tests"],
        test_data={
            "matrix_k": 400,      # Cobre W/mK
            "filler_k": 2000,     # Diamante W/mK
            "filler_fraction": 0.3,
            "expected_min": 400
        }
    )
    
    print(f"   ✓ Hipótesis: {result2['hypothesis'][:50]}...")
    print(f"   ✓ Validada: {'✅ SÍ' if result2['validated'] else '❌ NO'}")
    print(f"   ✓ p-value combinado: {result2['combined_p']:.6f}")
    print(f"   ✓ Tests ejecutados: {len(result2['tests_executed'])}")
    for t in result2['tests_executed']:
        print(f"      └─ {t['tool']}: p={t['p_value']:.4f}")
    results.append({"test": "Thermal Conductivity", **result2})
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 3: Biología - Contenido GC de Secuencia
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("📋 TEST 3: Biología - Contenido GC de Secuencia")
    print("─" * 70)
    
    result3 = validator.validate_hypothesis(
        hypothesis_text="The DNA sequence has GC content above 50%",
        domain="biology",
        tools_to_use=["sequence_analysis", "statistical_tests"],
        test_data={
            "sequence": "ATGCGCGCATGCGCGCATGCGCGCATGCGCGC",  # Alta GC
            "property": "gc_content",
            "expected_min": 0.5
        }
    )
    
    print(f"   ✓ Hipótesis: {result3['hypothesis'][:50]}...")
    print(f"   ✓ Validada: {'✅ SÍ' if result3['validated'] else '❌ NO'}")
    print(f"   ✓ p-value combinado: {result3['combined_p']:.6f}")
    print(f"   ✓ Tests ejecutados: {len(result3['tests_executed'])}")
    for t in result3['tests_executed']:
        print(f"      └─ {t['tool']}: p={t['p_value']:.4f}")
    results.append({"test": "GC Content", **result3})
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 4: Estadístico - Normalidad de Datos
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("📋 TEST 4: Estadístico - Test de Normalidad")
    print("─" * 70)
    
    import numpy as np
    np.random.seed(42)
    normal_data = np.random.normal(100, 15, 100).tolist()
    
    result4 = validator.validate_hypothesis(
        hypothesis_text="The experimental data follows a normal distribution",
        domain="statistics",
        tools_to_use=["statistical_tests"],
        test_data={
            "data": normal_data,
            "test_type": "normality",
            "alpha": 0.05
        }
    )
    
    print(f"   ✓ Hipótesis: {result4['hypothesis'][:50]}...")
    print(f"   ✓ Validada: {'✅ SÍ' if result4['validated'] else '❌ NO'}")
    print(f"   ✓ p-value combinado: {result4['combined_p']:.6f}")
    print(f"   ✓ Tests ejecutados: {len(result4['tests_executed'])}")
    for t in result4['tests_executed']:
        print(f"      └─ {t['tool']}: p={t['p_value']:.4f}")
    results.append({"test": "Normality", **result4})
    
    # ═══════════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL - VALIDACIÓN AVANZADA DE HIPÓTESIS")
    print("=" * 70)
    
    validated_count = sum(1 for r in results if r['validated'])
    total_tests = len(results)
    
    print(f"\n   🎯 Hipótesis validadas: {validated_count}/{total_tests}")
    print(f"   📈 Tasa de validación: {validated_count/total_tests*100:.1f}%")
    print(f"   🔬 Nivel de significancia: α = {validator.alpha}")
    print(f"   📐 Método de agregación: {validator.aggregation_method}")
    
    print("\n   Detalle por hipótesis:")
    for r in results:
        status = "✅" if r['validated'] else "❌"
        print(f"      {status} {r['test']}: p={r['combined_p']:.6f}")
    
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
        "results": results
    }
    
    output_file = f"advanced_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        # Convertir a serializable
        def clean(obj):
            if isinstance(obj, dict):
                return {k: clean(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean(v) for v in obj]
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return str(obj)
        json.dump(clean(output), f, indent=2)
    
    print(f"\n   💾 Resultados guardados en: {output_file}")
    print("\n" + "=" * 70)
    print("✅ INTEGRACIÓN POPPER + TOOLUNIVERSE + AXIOM COMPLETADA")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    main()
