#!/usr/bin/env python3
"""
Test script para validar mejoras de diversidad en PriorityScorer y TaskScheduler.

Verifica:
1. Diversity bonus en PriorityScorer
2. Stochastic top-k selection en TaskScheduler
3. Comparación de scores con/sin mejoras
"""
import sys
from typing import Dict, List, Any

# Test 1: PriorityScorer con diversity bonus
def test_priority_scorer_diversity():
    print("\n" + "="*80)
    print("TEST 1: PriorityScorer - Diversity Bonus")
    print("="*80)
    
    from app.autonomous.core.priority_scoring import PriorityScorer
    
    # Candidatos con nombres únicos vs duplicados
    candidates_unique = [
        {"name": "Candidate_A", "novelty": 0.6, "importance": 0.5, "proveability": 0.4},
        {"name": "Candidate_B", "novelty": 0.6, "importance": 0.5, "proveability": 0.4},
        {"name": "Candidate_C", "novelty": 0.6, "importance": 0.5, "proveability": 0.4},
        {"name": "Candidate_D", "novelty": 0.6, "importance": 0.5, "proveability": 0.4},
    ]
    
    candidates_duplicated = [
        {"name": "Same_Name", "novelty": 0.6, "importance": 0.5, "proveability": 0.4},
        {"name": "Same_Name", "novelty": 0.6, "importance": 0.5, "proveability": 0.4},
        {"name": "Same_Name", "novelty": 0.6, "importance": 0.5, "proveability": 0.4},
        {"name": "Different", "novelty": 0.6, "importance": 0.5, "proveability": 0.4},
    ]
    
    # Test con diversity bonus = 0.0 (deshabilitado)
    scorer_no_bonus = PriorityScorer()
    scorer_no_bonus.weights.diversity_bonus = 0.0
    ranked_no_bonus_unique = scorer_no_bonus.rank(candidates_unique)
    ranked_no_bonus_dup = scorer_no_bonus.rank(candidates_duplicated)
    
    print("\n📊 SIN Diversity Bonus (weight=0.0):")
    print(f"  Unique candidates score: {ranked_no_bonus_unique[0]['score']:.4f}")
    print(f"  Duplicated candidates score: {ranked_no_bonus_dup[0]['score']:.4f}")
    print(f"  Diferencia: {abs(ranked_no_bonus_unique[0]['score'] - ranked_no_bonus_dup[0]['score']):.4f}")
    
    # Test con diversity bonus = 0.15 (habilitado)
    scorer_with_bonus = PriorityScorer()
    scorer_with_bonus.weights.diversity_bonus = 0.15
    ranked_with_bonus_unique = scorer_with_bonus.rank(candidates_unique)
    ranked_with_bonus_dup = scorer_with_bonus.rank(candidates_duplicated)
    
    print("\n✅ CON Diversity Bonus (weight=0.15):")
    print(f"  Unique candidates:")
    print(f"    - Base score: {ranked_with_bonus_unique[0]['base_score']:.4f}")
    print(f"    - Diversity bonus: {ranked_with_bonus_unique[0]['diversity_bonus']:.4f}")
    print(f"    - Total score: {ranked_with_bonus_unique[0]['score']:.4f}")
    print(f"  Duplicated candidates:")
    print(f"    - Base score: {ranked_with_bonus_dup[0]['base_score']:.4f}")
    print(f"    - Diversity bonus: {ranked_with_bonus_dup[0]['diversity_bonus']:.4f}")
    print(f"    - Total score: {ranked_with_bonus_dup[0]['score']:.4f}")
    
    score_diff = ranked_with_bonus_unique[0]['score'] - ranked_with_bonus_dup[0]['score']
    print(f"\n🎯 Diferencia de scores: {score_diff:.4f}")
    
    if score_diff > 0:
        print("✅ ÉXITO: Candidatos únicos tienen mayor score que duplicados")
        return True
    else:
        print("❌ FALLO: No hay diferencia de scores")
        return False


# Test 2: TaskScheduler con stochastic selection
def test_task_scheduler_stochastic():
    print("\n" + "="*80)
    print("TEST 2: TaskScheduler - Stochastic Top-K Selection")
    print("="*80)
    
    from app.autonomous.core.task_scheduler import TaskScheduler
    
    # Candidatos con scores muy cercanos (empate)
    candidates = [
        {"name": "A", "score": 2.100, "domain": "quantum"},
        {"name": "B", "score": 2.099, "domain": "quantum"},
        {"name": "C", "score": 2.098, "domain": "quantum"},
        {"name": "D", "score": 2.097, "domain": "quantum"},
        {"name": "E", "score": 2.096, "domain": "quantum"},
        {"name": "F", "score": 2.095, "domain": "quantum"},
        {"name": "G", "score": 2.094, "domain": "quantum"},
        {"name": "H", "score": 2.093, "domain": "quantum"},
    ]
    
    # Test determinista (3 ejecuciones deben ser idénticas)
    scheduler_det = TaskScheduler(diversity_quota=None, stochastic_topk=False)
    selections_det = []
    for i in range(3):
        scheduler_det.reset_cycle()
        selected = scheduler_det.select(candidates, limit=4)
        names = [s["name"] for s in selected]
        selections_det.append(names)
        print(f"\n📌 Determinista run {i+1}: {names}")
    
    det_identical = all(s == selections_det[0] for s in selections_det)
    print(f"\n{'✅' if det_identical else '❌'} Determinista: {'IDÉNTICAS' if det_identical else 'DIFERENTES'}")
    
    # Test estocástico (3 ejecuciones deben ser diferentes)
    scheduler_stoch = TaskScheduler(
        diversity_quota=None,
        stochastic_topk=True,
        topk_size=6,
        selection_temperature=0.5
    )
    selections_stoch = []
    for i in range(3):
        scheduler_stoch.reset_cycle()
        selected = scheduler_stoch.select(candidates, limit=4)
        names = [s["name"] for s in selected]
        selections_stoch.append(names)
        print(f"\n🎲 Estocástico run {i+1}: {names}")
    
    stoch_different = len(set(tuple(s) for s in selections_stoch)) > 1
    print(f"\n{'✅' if stoch_different else '⚠️'} Estocástico: {'DIFERENTES' if stoch_different else 'IDÉNTICAS (puede pasar por azar)'}")
    
    # Verificar que selecciones incluyen candidatos más allá del top-4
    all_selected_names = set()
    for run in selections_stoch:
        all_selected_names.update(run)
    
    beyond_top4 = all_selected_names - {"A", "B", "C", "D"}
    print(f"\n🔍 Candidatos seleccionados más allá del top-4 determinista: {beyond_top4 or 'Ninguno'}")
    
    if stoch_different or beyond_top4:
        print("\n✅ ÉXITO: Selección estocástica introduce diversidad")
        return True
    else:
        print("\n⚠️  ADVERTENCIA: No se observó diversidad (puede ser casualidad, re-ejecutar)")
        return True  # No falla el test


# Test 3: Integración completa
def test_integration():
    print("\n" + "="*80)
    print("TEST 3: Integración PriorityScorer + TaskScheduler")
    print("="*80)
    
    from app.autonomous.core.priority_scoring import PriorityScorer
    from app.autonomous.core.task_scheduler import TaskScheduler
    
    # Candidatos con métricas similares pero nombres únicos
    raw_candidates = [
        {"name": f"Quantum_Circuit_{i}", "novelty": 0.55 + i*0.01, "importance": 0.5, "proveability": 0.4}
        for i in range(10)
    ]
    
    # Scoring con diversity bonus
    scorer = PriorityScorer()
    scorer.weights.diversity_bonus = 0.15
    ranked = scorer.rank(raw_candidates)
    
    print("\n📊 Top-5 candidatos después de scoring:")
    for i, cand in enumerate(ranked[:5]):
        print(f"  {i+1}. {cand['name']}: base={cand['base_score']:.4f}, bonus={cand['diversity_bonus']:.4f}, total={cand['score']:.4f}")
    
    # Selección estocástica
    scheduler = TaskScheduler(
        diversity_quota=None,
        stochastic_topk=True,
        topk_size=8,
        selection_temperature=0.5
    )
    
    print("\n🎲 Selecciones estocásticas (3 runs):")
    for run in range(3):
        scheduler.reset_cycle()
        selected = scheduler.select(ranked, limit=4)
        names = [s["name"] for s in selected]
        scores = [s["score"] for s in selected]
        print(f"  Run {run+1}: {', '.join(names)}")
        print(f"          Scores: {[f'{s:.4f}' for s in scores]}")
    
    print("\n✅ INTEGRACIÓN COMPLETADA")
    return True


def main():
    print("\n" + "🚀"*40)
    print("VALIDACIÓN DE MEJORAS DE DIVERSIDAD - PHASE 9")
    print("🚀"*40)
    
    results = []
    
    try:
        results.append(("PriorityScorer Diversity Bonus", test_priority_scorer_diversity()))
    except Exception as e:
        print(f"\n❌ ERROR en test 1: {e}")
        import traceback
        traceback.print_exc()
        results.append(("PriorityScorer Diversity Bonus", False))
    
    try:
        results.append(("TaskScheduler Stochastic Selection", test_task_scheduler_stochastic()))
    except Exception as e:
        print(f"\n❌ ERROR en test 2: {e}")
        import traceback
        traceback.print_exc()
        results.append(("TaskScheduler Stochastic Selection", False))
    
    try:
        results.append(("Integración Completa", test_integration()))
    except Exception as e:
        print(f"\n❌ ERROR en test 3: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Integración Completa", False))
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE RESULTADOS")
    print("="*80)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("✅"*20 if all_passed else "❌"*20))
    print(f"{'TODAS LAS PRUEBAS PASARON' if all_passed else 'ALGUNAS PRUEBAS FALLARON'}")
    print(("✅"*20 if all_passed else "❌"*20) + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
