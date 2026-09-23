#!/usr/bin/env python3
"""Test simple de un solo loop para debugging"""
import asyncio
import sys
import json
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.multi_agent_coordinator import MultiAgentCoordinator

async def test_simple_biology():
    """Test simplificado del biology loop"""
    print("\n" + "="*80)
    print("🧬 TEST SIMPLIFICADO: BIOLOGY LOOP")
    print("="*80)
    
    coordinator = MultiAgentCoordinator()
    
    research_goal = """
    Investigate CRISPR-Cas9 off-target effects in gene therapy.
    Hypothesis: Computational prediction models can reduce off-target effects by 80%.
    """
    
    try:
        print("\n📋 Fase 1: Planning...")
        plan = await coordinator.plan_async(research_goal)
        print(f"   ✓ Plan: {len(plan)} chars")
        
        print("\n🧪 Fase 2: Generando hipótesis...")
        hypothesis = await coordinator.generate_bio_hypothesis_async(research_goal)
        print(f"   ✓ Hipótesis: {len(hypothesis)} chars")
        
        print("\n💻 Fase 3: Generando código...")
        code = await coordinator.design_and_code_async(hypothesis)
        print(f"   ✓ Código: {len(code)} chars, {len(code.split(chr(10)))} líneas")
        
        print("\n📝 Fase 4: Review...")
        review = await coordinator.critical_review_async(hypothesis, code)
        print(f"   ✓ Review: {len(review)} chars")
        
        print("\n✅ Test completado exitosamente")
        
        # Guardar resultados
        results = {
            "plan_length": len(plan),
            "hypothesis_length": len(hypothesis),
            "code_lines": len(code.split('\n')),
            "review_length": len(review),
            "status": "SUCCESS"
        }
        
        with open("test_simple_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Resultados guardados en: test_simple_results.json")
        return results
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    try:
        results = asyncio.run(test_simple_biology())
        sys.exit(0 if results.get("status") == "SUCCESS" else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrumpido")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
