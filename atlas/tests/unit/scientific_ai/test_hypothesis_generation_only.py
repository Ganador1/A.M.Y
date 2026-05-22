"""Test rápido: Solo generación de hipótesis con literatura"""
import asyncio
import sys
import json
from app.autonomous.generators.hypothesis_generator import HypothesisGenerator

async def test_hypothesis_with_literatura():
    print("🧪 TEST: Generación de hipótesis con literatura search")
    print("=" * 70)
    
    # Inicializar generador
    generator = HypothesisGenerator()
    
    # Contexto con literatura enabled
    context = {
        'mode': 'production',
        'use_real_services': True,
        'novelty_threshold': 0.7,
        'require_evidence': True,
        'enable_literature_search': True,
        'literature_year': 2024,
        'literature_limit': 20
    }
    
    print("\n📚 Contexto:", json.dumps(context, indent=2))
    print("\n⏳ Generando hipótesis... (esto puede tardar 2-3 min)")
    
    try:
        # Generar hipótesis
        hypothesis = await generator.generate_hypothesis(
            domain='biology',
            context=context
        )
        
        print("\n✅ HIPÓTESIS GENERADA:")
        print("=" * 70)
        print(json.dumps(hypothesis, indent=2, ensure_ascii=False))
        
        # Guardar en archivo
        with open('hypothesis_with_literatura_20251105.json', 'w') as f:
            json.dump(hypothesis, f, indent=2, ensure_ascii=False)
        
        print("\n📄 Guardada en: hypothesis_with_literatura_20251105.json")
        return hypothesis
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    hypothesis = asyncio.run(test_hypothesis_with_literatura())
    print("\n🎉 TEST COMPLETADO")
