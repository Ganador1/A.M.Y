#!/usr/bin/env python3
"""
Demostración simple de las mejoras implementadas en AXIOM/ATLAS
Muestra el uso directo de las mejoras sin dependencias de la app principal
"""

import asyncio
import sys
from pathlib import Path

# Add improvements to path
sys.path.insert(0, str(Path(__file__).parent / 'improvements'))

# Import improvements directly
from improvements.advanced_plausibility_scorer import AdvancedPlausibilityScorerV2
from improvements.real_scientific_databases import RealScientificDatabasesV2

async def demo_advanced_plausibility_scorer():
    """Demostrar el Advanced Plausibility Scorer V2"""
    print("\n" + "="*60)
    print("🎯 DEMOSTRACIÓN: ADVANCED PLAUSIBILITY SCORER V2")
    print("="*60)

    # Crear el servicio mejorado
    scorer = AdvancedPlausibilityScorerV2()

    # Hipótesis de ejemplo
    hypothesis = {
        "title": "IA cuántica para descubrimiento de fármacos",
        "description": "Utilizando algoritmos cuánticos para optimizar el diseño molecular y acelerar el descubrimiento de nuevos fármacos contra enfermedades neurodegenerativas",
        "variables": ["algoritmo_cuantico", "tamano_molecula", "energia_binding", "toxicidad"],
        "domain": "drug_discovery",
        "assumptions": ["La computación cuántica es accesible", "Los algoritmos VQE son aplicables"],
        "expected_outcome": "Reducción del 90% en tiempo de descubrimiento de candidatos a fármacos"
    }

    print(f"📝 Hipótesis: {hypothesis['title']}")
    print(f"📄 Descripción: {hypothesis['description'][:100]}...")

    # Evaluar la hipótesis
    print("\n🔬 Evaluando hipótesis con ML avanzado...")
    result = await scorer.score_hypothesis(hypothesis)

    print("\n✅ Resultados:")
    print(f"   📊 Puntuación Final: {result.get('final_score', 0):.3f}")
    print(f"   🧠 Puntuación Semántica: {result.get('confidence_breakdown', {}).get('semantic', 0):.3f}")
    print(f"   📚 Puntuación Literatura: {result.get('confidence_breakdown', {}).get('literature', 0):.3f}")
    print(f"   🔗 Puntuación Causal: {result.get('confidence_breakdown', {}).get('causal', 0):.3f}")
    print(f"   ✨ Puntuación Novedad: {result.get('confidence_breakdown', {}).get('novelty', 0):.3f}")

    # Mostrar recomendaciones
    if result.get('recommendations'):
        print("\n⚠️ Recomendaciones:")
        for recommendation in result['recommendations']:
            print(f"   • {recommendation}")

    return result['final_score'] > 0.5

async def demo_real_scientific_databases():
    """Demostrar las Real Scientific Databases V2"""
    print("\n" + "="*60)
    print("🔍 DEMOSTRACIÓN: REAL SCIENTIFIC DATABASES V2")
    print("="*60)

    # Crear el servicio de búsqueda mejorado
    db = RealScientificDatabasesV2()

    # Consulta de ejemplo
    query = "machine learning applications in drug discovery"
    print(f"🔎 Buscando: '{query}'")

    print("\n📊 Buscando en bases de datos científicas reales...")
    results = await db.search_all_databases(
        query,
        databases=["crossref"],  # Use crossref which doesn't require API keys
        max_results_per_db=5
    )

    print("\n✅ Resultados:")
    print(f"   📄 Papers Encontrados: {len(results.get('papers', []))}")
    print(f"   🧪 Compuestos Encontrados: {len(results.get('compounds', []))}")
    print(f"   🧬 Proteínas Encontradas: {len(results.get('proteins', []))}")

    if results.get('papers'):
        print("\n📚 Top Papers:")
        for i, paper in enumerate(results['papers'][:3], 1):
            print(f"   {i}. {paper.title}")
            print(f"      👥 Autores: {', '.join(paper.authors[:2])}")
            if paper.year:
                print(f"      📅 Año: {paper.year}")
            if paper.journal:
                print(f"      📖 Journal: {paper.journal}")
            print()

    # Demostrar validación de hipótesis
    print("🔬 Validando hipótesis contra literatura...")
    validation = await db.validate_hypothesis_against_literature(
        "Machine learning can significantly accelerate drug discovery by predicting molecular properties"
    )

    print("\n✅ Validación:")
    print(f"   📊 Estado: {validation['validation_status']}")
    print(f"   🎯 Confianza: {validation['confidence']:.2f}")
    print(f"   📄 Papers Analizados: {validation['total_papers_analyzed']}")

    return len(results.get('papers', [])) > 0

async def main():
    """Ejecutar toda la demostración"""
    print("🚀 AXIOM/ATLAS - DEMOSTRACIÓN DE MEJORAS STATE-OF-THE-ART")
    print("Sistema de investigación científica avanzado con ML y bases de datos reales")

    try:
        # Verificar que estamos en el entorno virtual correcto
        if 'venv_improvements' not in sys.executable:
            print("⚠️ Advertencia: Ejecuta este script con el entorno virtual:")
            print("   source venv_improvements/bin/activate")
            print("   python demo_mejoras_simple.py")
            return

        print(f"🐍 Python: {sys.executable}")

        # Ejecutar demostraciones
        demo1_passed = await demo_advanced_plausibility_scorer()
        demo2_passed = await demo_real_scientific_databases()

        # Resumen final
        print("\n" + "="*60)
        print("📊 RESUMEN DE DEMOSTRACIÓN")
        print("="*60)

        tests = [
            ("Advanced Plausibility Scorer V2", demo1_passed),
            ("Real Scientific Databases V2", demo2_passed)
        ]

        passed = 0
        for test_name, result in tests:
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1

        print(f"\n🎯 Resultado General: {passed}/2 demostraciones exitosas")

        if passed == 2:
            print("\n🎉 ¡FELICITACIONES! Todas las mejoras están funcionando perfectamente.")
            print("   AXIOM/ATLAS ahora es una plataforma de investigación científica de vanguardia.")
        else:
            print(f"\n⚠️ {2-passed} demostraciones necesitan atención.")

        print("\n📚 Para más información:")
        print("   • Revisa MEJORAS_IMPLEMENTADAS.md")
        print("   • Consulta improvements/README.md")
        print("   • Ejecuta test_improvements_manual.py para pruebas técnicas")

    except Exception as e:
        print(f"\n❌ Error durante la demostración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
