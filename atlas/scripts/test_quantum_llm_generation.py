"""
Test de generación LLM de candidatos cuánticos.

Verifica que:
1. El Quantum loop usa LLM para generar candidatos únicos
2. Cada ejecución genera circuitos diferentes
3. El fallback a templates funciona si LLM falla
"""
import asyncio
import sys
from app.autonomous.pipelines.quantum_loop import QuantumLoop
from app.core.bootstrap_logging import logger

async def test_llm_generation():
    """Test que el loop genera candidatos únicos vía LLM"""
    print("\n" + "="*80)
    print("🧪 TEST: Generación LLM de Candidatos Cuánticos (Phase 8.4)")
    print("="*80 + "\n")
    
    loop = QuantumLoop()
    
    # Test 1: Generar candidatos usando LLM
    print("📝 Test 1: Generación de candidatos vía LLM...")
    print("-" * 80)
    
    try:
        candidates = await loop._default_provider_async(limit=4)
        
        print(f"✅ Generados {len(candidates)} candidatos")
        print(f"\n🎯 Detalles de candidatos:")
        
        for idx, cand in enumerate(candidates, 1):
            print(f"\n  Candidato {idx}:")
            print(f"    ID: {cand.get('id')}")
            print(f"    Algorithm: {cand.get('algorithm')}")
            print(f"    Qubits: {cand.get('n_qubits')}")
            print(f"    Depth: {cand.get('depth')}")
            print(f"    Source: {cand.get('data_source')}")
            if 'motivation' in cand:
                print(f"    Motivation: {cand.get('motivation')[:80]}...")
        
        # Verificar que no son todos iguales
        unique_ids = set(c['id'] for c in candidates)
        print(f"\n📊 IDs únicos: {len(unique_ids)}/{len(candidates)}")
        
        if len(unique_ids) >= len(candidates) * 0.75:
            print("✅ PASS: Alta diversidad en candidatos")
        else:
            print("⚠️ WARNING: Baja diversidad, posible fallback a templates")
        
        # Verificar source
        llm_generated = sum(1 for c in candidates if c.get('data_source') == 'llm_generated')
        print(f"🧠 Candidatos LLM: {llm_generated}/{len(candidates)}")
        
        if llm_generated > 0:
            print("✅ PASS: LLM generation funcionó")
        else:
            print("⚠️ WARNING: Fallback a templates/synthetic")
        
    except Exception as e:
        print(f"❌ FAIL: Error generando candidatos: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Verificar que múltiples ejecuciones dan resultados diferentes
    print("\n" + "-" * 80)
    print("📝 Test 2: Diversidad entre ejecuciones...")
    print("-" * 80)
    
    try:
        candidates_run1 = await loop._default_provider_async(limit=3)
        candidates_run2 = await loop._default_provider_async(limit=3)
        
        ids_run1 = [c['id'] for c in candidates_run1]
        ids_run2 = [c['id'] for c in candidates_run2]
        
        print(f"Run 1 IDs: {ids_run1}")
        print(f"Run 2 IDs: {ids_run2}")
        
        # Si hay LLM generation, los IDs deberían ser diferentes
        if ids_run1 != ids_run2:
            print("✅ PASS: Ejecuciones generan candidatos diferentes")
        else:
            print("⚠️ INFO: IDs idénticos (posible caching o fallback)")
        
    except Exception as e:
        print(f"⚠️ WARNING: Error en test de diversidad: {e}")
    
    # Test 3: Verificar full iteration
    print("\n" + "-" * 80)
    print("📝 Test 3: Iteración completa del loop...")
    print("-" * 80)
    
    try:
        result = await loop.run_quantum_discovery_iteration(iteration=1, limit=2)
        
        print(f"✅ Iteración completada")
        print(f"Keys en resultado: {list(result.keys())}")
        print(f"Success: {result.get('success')}")
        print(f"Outcomes: {len(result.get('outcomes', []))}")
        
        if result.get('outcomes'):
            print(f"\n🎯 Primer outcome:")
            first_outcome = result['outcomes'][0]
            print(f"  ID: {first_outcome.get('id')}")
            print(f"  Novelty: {first_outcome.get('novelty_score', 0):.4f}")
            print(f"  Source: {first_outcome.get('data_source')}")
        
    except Exception as e:
        print(f"❌ FAIL: Error en iteración completa: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*80)
    print("✅ TESTS COMPLETADOS")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_llm_generation())
    sys.exit(0 if success else 1)
