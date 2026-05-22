#!/usr/bin/env python3
"""
Phase 8.5: Test de Diversidad Mejorada con Temperature Boost + Prompt Variability

OBJETIVOS:
- Verificar temperature boost de +0.4 (target: 0.75-0.85)
- Confirmar config_id único y seen_names pasados correctamente
- Medir diversidad de nombres (target: >90% únicos)
"""

import asyncio
import sys
from pathlib import Path

# Agregar app al path
sys.path.insert(0, str(Path(__file__).parent))

from app.autonomous.pipelines.quantum_loop import QuantumLoop


async def test_diversity_single_config():
    """Test con una sola configuración para verificar diversidad"""
    
    print("=" * 80)
    print("PHASE 8.5 - TEST DE DIVERSIDAD MEJORADA")
    print("=" * 80)
    print()
    
    # Crear loop
    loop = QuantumLoop()
    
    # Ejecutar 3 iteraciones para acumular seen_names
    all_names = []
    
    for iteration in range(1, 4):
        print(f"\n{'='*60}")
        print(f"ITERACIÓN {iteration}/3")
        print(f"{'='*60}")
        
        result = await loop.run_quantum_discovery_iteration(iteration=iteration, limit=4)
        
        if not result.get("success", True):
            print(f"❌ Iteración {iteration} falló: {result.get('reason', 'unknown')}")
            continue
        
        # Extraer nombres de candidatos
        candidates = result.get("candidates", [])
        iteration_names = [c.get("id", "unknown") for c in candidates]
        
        print(f"\n📋 Candidatos generados ({len(iteration_names)}):")
        for idx, name in enumerate(iteration_names, 1):
            print(f"  {idx}. {name}")
        
        all_names.extend(iteration_names)
        
        # Mostrar seen_names acumulados
        print(f"\n📊 Seen names acumulados: {len(loop._seen_names)}")
        print(f"   Últimos 5: {loop._seen_names[-5:]}")
    
    # Análisis de diversidad
    print(f"\n{'='*60}")
    print("ANÁLISIS DE DIVERSIDAD")
    print(f"{'='*60}")
    
    total_generated = len(all_names)
    unique_names = len(set(all_names))
    diversity_pct = (unique_names / total_generated * 100) if total_generated > 0 else 0
    
    print(f"\n📊 MÉTRICAS:")
    print(f"   Total candidatos generados: {total_generated}")
    print(f"   Nombres únicos: {unique_names}")
    print(f"   Diversidad: {diversity_pct:.1f}%")
    print(f"   Duplicados: {total_generated - unique_names}")
    
    # Verificar objetivo
    TARGET_DIVERSITY = 90.0
    print(f"\n🎯 OBJETIVO: >={TARGET_DIVERSITY}% diversidad")
    
    if diversity_pct >= TARGET_DIVERSITY:
        print(f"   ✅ OBJETIVO ALCANZADO ({diversity_pct:.1f}% >= {TARGET_DIVERSITY}%)")
        status = "PASS"
    elif diversity_pct >= 75.0:
        print(f"   ⚠️  MEJORA PARCIAL ({diversity_pct:.1f}% vs anterior ~60%)")
        status = "PARTIAL"
    else:
        print(f"   ❌ OBJETIVO NO ALCANZADO ({diversity_pct:.1f}% < {TARGET_DIVERSITY}%)")
        status = "FAIL"
    
    # Mostrar nombres duplicados si hay
    if unique_names < total_generated:
        from collections import Counter
        name_counts = Counter(all_names)
        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        
        print(f"\n⚠️  NOMBRES DUPLICADOS:")
        for name, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {name}: {count} veces")
    
    print(f"\n{'='*60}")
    print(f"RESULTADO FINAL: {status}")
    print(f"{'='*60}\n")
    
    return {
        "status": status,
        "diversity_pct": diversity_pct,
        "unique_names": unique_names,
        "total_generated": total_generated
    }


if __name__ == "__main__":
    result = asyncio.run(test_diversity_single_config())
    
    # Exit code basado en resultado
    if result["status"] == "PASS":
        sys.exit(0)  # Success
    elif result["status"] == "PARTIAL":
        sys.exit(1)  # Partial improvement
    else:
        sys.exit(2)  # Failure
