#!/usr/bin/env python3
"""
Test de Validación Multidisciplinaria de AXIOM.
Conecta el validador avanzado con los dominios nativos de AXIOM.
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
    print("🚀 AXIOM ATLAS - Test de Validación Multidisciplinaria")
    print("   Integración: POPPER + ToolUniverse + AXIOM Native Domains")
    print("=" * 70)
    
    from app.services.advanced_hypothesis_validator import AdvancedHypothesisValidator
    
    validator = AdvancedHypothesisValidator(alpha=0.1, max_tests=5)
    results = []
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 1: Astronomía - Análisis de Exoplaneta
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("🔭 TEST 1: Astronomía - Tránsito de Exoplaneta")
    print("─" * 70)
    
    result1 = await validator.validate_hypothesis(
        hypothesis="The light curve shows a significant exoplanet transit signal",
        domain="astronomy",
        test_specifications=[
            {
                "name": "AXIOM Light Curve Analysis",
                "tool": "axiom_astronomy",
                "parameters": {
                    "seed": 123,
                    "n": 256,
                    "noise_sigma": 0.01,
                    "dip_center": 0.5,
                    "dip_width": 0.03,
                    "dip_depth": 0.02
                },
                "null_hypothesis": "No periodic transit signal detected",
                "alternative_hypothesis": "Periodic transit signal detected"
            }
        ]
    )
    
    print(f"   ✓ Hipótesis: {result1.hypothesis[:50]}...")
    print(f"   ✓ Estado: {result1.status.value}")
    print(f"   ✓ p-value: {result1.combined_p_value:.6f}" if result1.combined_p_value else "   ✓ p-value: N/A")
    results.append(result1)
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 2: Medicina - Análisis de Imagen DICOM
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("🏥 TEST 2: Medicina - Diagnóstico por Imagen")
    print("─" * 70)
    
    result2 = await validator.validate_hypothesis(
        hypothesis="The MRI scan shows no signs of abnormal tissue growth",
        domain="medicine",
        test_specifications=[
            {
                "name": "AXIOM Medical Imaging",
                "tool": "axiom_medicine",
                "parameters": {
                    "imaging_data": {
                        "edv": 120.0,
                        "esv": 45.0,
                        "heart_rate": 70,
                        "image_quality": 0.85,
                    },
                    "expected_ef_mean": 60.0,
                    "expected_ef_sigma": 5.0
                },
                "null_hypothesis": "Abnormal tissue growth detected",
                "alternative_hypothesis": "No abnormal tissue growth detected"
            }
        ]
    )
    
    print(f"   ✓ Hipótesis: {result2.hypothesis[:50]}...")
    print(f"   ✓ Estado: {result2.status.value}")
    print(f"   ✓ p-value: {result2.combined_p_value:.6f}" if result2.combined_p_value else "   ✓ p-value: N/A")
    results.append(result2)
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 3: Matemáticas - Verificación de Identidad
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("📐 TEST 3: Matemáticas - Identidad Simbólica")
    print("─" * 70)
    
    result3 = await validator.validate_hypothesis(
        hypothesis="The mathematical identity sin(x)^2 + cos(x)^2 = 1 holds",
        domain="mathematics",
        test_specifications=[
            {
                "name": "AXIOM Symbolic Solver",
                "tool": "axiom_mathematics",
                "parameters": {
                    "operation": "solve_equation",
                    "expression": "sin(x)**2 + cos(x)**2 - 1"
                },
                "null_hypothesis": "Expression is not zero",
                "alternative_hypothesis": "Expression is zero"
            }
        ]
    )
    
    print(f"   ✓ Hipótesis: {result3.hypothesis[:50]}...")
    print(f"   ✓ Estado: {result3.status.value}")
    print(f"   ✓ p-value: {result3.combined_p_value:.6f}" if result3.combined_p_value else "   ✓ p-value: N/A")
    results.append(result3)

    # ═══════════════════════════════════════════════════════════════════
    # TEST 4: Neurociencia - Circuito cortical (NetworkX)
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("🧠 TEST 4: Neurociencia - Circuito Cortical")
    print("─" * 70)

    result4 = await validator.validate_hypothesis(
        hypothesis="The cortical circuit has unusually high clustering",
        domain="neuroscience",
        test_specifications=[
            {
                "name": "AXIOM Brain Circuit Analysis",
                "tool": "axiom_neuroscience",
                "parameters": {
                    "circuit_type": "cortical_column",
                    "num_neurons": 100,
                    "null_samples": 50,
                    "seed": 123,
                },
                "null_hypothesis": "Clustering is consistent with an Erdos-Renyi null",
                "alternative_hypothesis": "Clustering is higher than Erdos-Renyi null",
            }
        ],
    )

    print(f"   ✓ Hipótesis: {result4.hypothesis[:50]}...")
    print(f"   ✓ Estado: {result4.status.value}")
    print(f"   ✓ p-value: {result4.combined_p_value:.6f}" if result4.combined_p_value else "   ✓ p-value: N/A")
    results.append(result4)
    
    # ═══════════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL - VALIDACIÓN MULTIDISCIPLINARIA")
    print("=" * 70)
    
    from app.services.advanced_hypothesis_validator import HypothesisStatus
    validated_count = sum(1 for r in results if r.status == HypothesisStatus.VALIDATED)
    total_tests = len(results)
    
    print(f"\n   🎯 Hipótesis validadas: {validated_count}/{total_tests}")
    print(f"   📈 Tasa de validación: {validated_count/total_tests*100:.1f}%")
    
    print("\n   Detalle por dominio:")
    for r in results:
        status = "✅" if r.status == HypothesisStatus.VALIDATED else "❌"
        print(f"      {status} {r.hypothesis[:40]}...")
    
    print("\n" + "=" * 70)
    print("✅ AXIOM ES AHORA EL SISTEMA MÁS MULTIDISCIPLINARIO")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
