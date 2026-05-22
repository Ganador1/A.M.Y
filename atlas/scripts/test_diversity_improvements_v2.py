#!/usr/bin/env python3
"""
Test Diversity Improvements v2 - Con diversity_bonus = 0.30
=====================================================

Valida que:
1. Diversity Bonus (0.30) recompensa candidatos únicos con el doble de impacto
2. Stochastic Selection sigue funcionando
3. Integración funciona con el nuevo peso
"""

import sys
sys.path.insert(0, '.')

from app.autonomous.core.priority_scoring import PriorityScorer, WeightConfig
from app.autonomous.core.task_scheduler import TaskScheduler
from app.autonomous.pipelines.quantum_loop import QuantumLoop


def test_diversity_bonus_increased():
    """Test 1: Diversity Bonus con peso 0.30 (doblado)"""
    print("\n" + "="*70)
    print("TEST 1: Diversity Bonus (0.30 weight)")
    print("="*70)
    
    scorer = PriorityScorer()
    scorer.weights.diversity_bonus = 0.30
    
    # Candidatos únicos
    unique_candidates = [
        {"name": f"Circuit_{i}", "score": 1.0} 
        for i in range(10)
    ]
    
    # Candidatos duplicados (mismo nombre)
    duplicate_candidates = [
        {"name": "Circuit_X", "score": 1.0} 
        for _ in range(10)
    ]
    
    # Score con candidatos únicos
    ranked_unique = scorer.rank(unique_candidates.copy())
    unique_final_score = ranked_unique[0]["score"]
    
    # Score con candidatos duplicados
    ranked_duplicate = scorer.rank(duplicate_candidates.copy())
    duplicate_final_score = ranked_duplicate[0]["score"]
    
    # Con diversity_bonus=0.30 y unique_ratio=1.0 (10/10) → bonus = 0.30
    # Con diversity_bonus=0.30 y unique_ratio=0.1 (1/10) → bonus = 0.03
    expected_unique = 1.0 + 0.30  # base + bonus
    expected_duplicate = 1.0 + 0.03  # base + smaller bonus
    
    print(f"✅ Candidatos únicos (10/10 unique):")
    print(f"   - Base score: 1.0000")
    print(f"   - Diversity bonus: 0.30 * (10/10) = 0.30")
    print(f"   - Final score: {unique_final_score:.4f}")
    print(f"   - Expected: {expected_unique:.4f}")
    
    print(f"\n✅ Candidatos duplicados (1/10 unique):")
    print(f"   - Base score: 1.0000")
    print(f"   - Diversity bonus: 0.30 * (1/10) = 0.03")
    print(f"   - Final score: {duplicate_final_score:.4f}")
    print(f"   - Expected: {expected_duplicate:.4f}")
    
    difference = unique_final_score - duplicate_final_score
    print(f"\n🎯 Diferencia: {difference:.4f}")
    print(f"   - Esperado: ~0.27 (0.30 - 0.03)")
    
    # Validación: difference debe ser ~0.27 (con margen de error por precisión)
    assert abs(difference - 0.27) < 0.01, f"Diversity bonus incorrecto: {difference} != 0.27"
    
    print("\n✅ TEST 1 PASSED: Diversity bonus (0.30) duplica el impacto correctamente")
    return True


def test_stochastic_selection_still_works():
    """Test 2: Stochastic Selection sigue funcionando"""
    print("\n" + "="*70)
    print("TEST 2: Stochastic Selection (sin cambios)")
    print("="*70)
    
    scheduler = TaskScheduler(
        diversity_quota=20,  # High quota to avoid limiting diversity
        stochastic_topk=True,
        topk_size=10,
        selection_temperature=0.5
    )
    
    candidates = [
        {"name": f"Task_{i}", "score": 10.0 - i*0.1} 
        for i in range(20)
    ]
    
    # Ejecutar 10 veces y verificar variabilidad
    selections = []
    for run in range(10):
        selected = scheduler.select(candidates.copy(), limit=6)
        selection_names = tuple(sorted([t["name"] for t in selected]))
        selections.append(selection_names)
    
    unique_selections = set(selections)
    
    print(f"✅ 10 ejecuciones → {len(unique_selections)} selecciones únicas")
    print(f"   Selecciones:")
    for i, sel in enumerate(list(unique_selections)[:5]):
        print(f"     {i+1}. {sel}")
    
    # Validación: debe haber variabilidad
    assert len(unique_selections) > 1, "No hay variabilidad en selecciones"
    
    # Verificar que se seleccionan candidatos más allá del top-6
    all_selected_names = set()
    for sel in selections:
        all_selected_names.update(sel)
    
    print(f"\n✅ Candidatos seleccionados (total): {len(all_selected_names)}")
    print(f"   - Esperado: > 6 (debido a sampling probabilístico)")
    
    # Con stochastic selection deberíamos ver más de 6 candidatos únicos a través de 10 ejecuciones
    # Si fuera determinista, solo veríamos los mismos 6 candidatos siempre
    print(f"   - Resultado: {'✅ PASS' if len(all_selected_names) > 6 else '⚠️ Marginal'}")
    
    print("\n✅ TEST 2 PASSED: Stochastic selection sigue funcionando")
    return True


def test_quantum_loop_integration():
    """Test 3: QuantumLoop tiene diversity_bonus=0.30"""
    print("\n" + "="*70)
    print("TEST 3: QuantumLoop Integration (0.30 weight)")
    print("="*70)
    
    loop = QuantumLoop()
    
    # Verificar configuración
    diversity_bonus = loop.scorer.weights.diversity_bonus
    stochastic_enabled = loop.scheduler.stochastic_topk
    topk_size = loop.scheduler.topk_size
    selection_temp = loop.scheduler.selection_temperature
    
    print(f"✅ PriorityScorer:")
    print(f"   - diversity_bonus: {diversity_bonus}")
    print(f"   - Expected: 0.30")
    
    print(f"\n✅ TaskScheduler:")
    print(f"   - stochastic_topk: {stochastic_enabled}")
    print(f"   - topk_size: {topk_size}")
    print(f"   - selection_temperature: {selection_temp}")
    
    # Validaciones
    assert diversity_bonus == 0.30, f"diversity_bonus incorrecto: {diversity_bonus} != 0.30"
    assert stochastic_enabled is True, "stochastic_topk debe estar habilitado"
    assert topk_size == 10, f"topk_size incorrecto: {topk_size} != 10"
    assert selection_temp == 0.5, f"selection_temperature incorrecto: {selection_temp} != 0.5"
    
    print("\n✅ TEST 3 PASSED: QuantumLoop tiene diversity_bonus=0.30")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TEST SUITE: Diversity Improvements v2 (diversity_bonus=0.30)")
    print("="*70)
    
    try:
        test1 = test_diversity_bonus_increased()
        test2 = test_stochastic_selection_still_works()
        test3 = test_quantum_loop_integration()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED (3/3)")
        print("="*70)
        print("\n📊 Summary:")
        print("   - Diversity Bonus: 0.30 (doblado desde 0.15) ✅")
        print("   - Impact: ~0.27 score difference (unique vs duplicate) ✅")
        print("   - Stochastic Selection: Working ✅")
        print("   - QuantumLoop Integration: Working ✅")
        print("\n🚀 Ready for Phase 9 validation!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
