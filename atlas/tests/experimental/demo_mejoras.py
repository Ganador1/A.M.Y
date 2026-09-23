#!/usr/bin/env python3
"""
Demostración completa de las mejoras implementadas en AXIOM/ATLAS
Muestra el uso de Advanced Plausibility Scorer y Real Scientific Databases
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add improvements to path
sys.path.insert(0, str(Path(__file__).parent / 'improvements'))

from app.services.plausibility_scoring_service_improved import PlausibilityScoringService
from app.services.literature_search_improved import LiteratureSearchService

async def demo_advanced_plausibility_scorer():
    """Demostrar el Advanced Plausibility Scorer V2"""
    print("\n" + "="*60)
    print("🎯 DEMOSTRACIÓN: ADVANCED PLAUSIBILITY SCORER V2")
    print("="*60)

    # Crear el servicio mejorado
    scorer = PlausibilityScoringService()

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
    start_time = datetime.now()

    result = await scorer.score_hypothesis(hypothesis)

    end_time = datetime.now()
    evaluation_time = (end_time - start_time).total_seconds()

    print("\n✅ Resultados:")
    print(f"   📊 Puntuación Final: {result['composite']:.3f}")
    print(f"   🧠 Puntuación Semántica: {result['components']['semantic']:.3f}")
    print(f"   📚 Puntuación Literatura: {result['components'].get('literature', 0):.3f}")
    print(f"   🔗 Puntuación Causal: {result['components'].get('causal', 0):.3f}")
    print(f"   ✨ Puntuación Novedad: {result['components'].get('novelty', 0):.3f}")
    print(f"   🎯 Puntuación Modelo: {result['model_score']:.3f}")
    print(f"   ⏱️ Tiempo de Evaluación: {evaluation_time:.2f} segundos")

    # Mostrar recomendaciones
    if result.get('warnings'):
        print("\n⚠️ Recomendaciones:")
        for warning in result['warnings']:
            print(f"   • {warning}")

    # Mostrar hipótesis similares exitosas
    similar = result.get('similar_successful_hypotheses', [])
    if similar:
        print(f"\n🔍 Hipótesis similares exitosas encontradas: {len(similar)}")
        for sim in similar[:2]:
            print(f"   • {sim['title']} (similitud: {sim['similarity']:.2f}")

    return result['composite'] > 0.5

async def demo_real_scientific_databases():
    """Demostrar las Real Scientific Databases V2"""
    print("\n" + "="*60)
    print("🔍 DEMOSTRACIÓN: REAL SCIENTIFIC DATABASES V2")
    print("="*60)

    # Crear el servicio de búsqueda mejorado
    search_service = LiteratureSearchService()

    # Consulta de ejemplo
    query = "machine learning applications in drug discovery"
    print(f"🔎 Buscando: '{query}'")

    print("\n📊 Buscando en bases de datos científicas reales...")
    start_time = datetime.now()

    # Buscar en múltiples bases de datos
    results = await search_service.search_literature({
        "query": query,
        "domain": "drug_discovery",
        "max_results": 10
    })

    end_time = datetime.now()
    search_time = (end_time - start_time).total_seconds()

    print("\n✅ Resultados:")
    print(f"   📄 Papers Encontrados: {len(results.get('papers', []))}")
    print(f"   ⏱️ Tiempo de Búsqueda: {search_time:.2f} segundos")

    if results.get('papers'):
        print("\n📚 Top Papers:")
        for i, paper in enumerate(results['papers'][:5], 1):
            print(f"   {i}. {paper['title']}")
            print(f"      📅 Año: {paper['year']} | 📖 Journal: {paper.get('journal', 'N/A')}")
            print(f"      👥 Autores: {', '.join(paper['authors'][:3])}")
            if paper.get('doi'):
                print(f"      🔗 DOI: {paper['doi']}")
            print()

    # Demostrar validación de hipótesis
    print("🔬 Validando hipótesis contra literatura...")
    validation = await search_service.validate_hypothesis(
        "Machine learning can significantly accelerate drug discovery by predicting molecular properties"
    )

    print("\n✅ Validación:")
    print(f"   📊 Estado: {validation['validation_status']}")
    print(f"   🎯 Confianza: {validation['confidence']:.2f}")
    print(f"   📄 Papers Analizados: {validation['total_papers_analyzed']}")

    return len(results.get('papers', [])) > 0

async def demo_integration():
    """Demostrar la integración completa"""
    print("\n" + "="*60)
    print("🔗 DEMOSTRACIÓN: INTEGRACIÓN COMPLETA")
    print("="*60)

    print("🚀 Probando pipeline completo de investigación científica...")

    # Paso 1: Generar y evaluar hipótesis
    hypothesis = {
        "title": "Deep Learning para predicción de interacciones proteína-ligando",
        "description": "Desarrollar un modelo de deep learning que prediga con alta precisión las interacciones entre proteínas y ligandos usando datos de estructuras 3D",
        "variables": ["arquitectura_red", "datos_entrenamiento", "funcion_perdida", "regularizacion"],
        "domain": "drug_discovery",
        "assumptions": ["Datos de estructuras 3D disponibles", "Computación suficiente"],
        "expected_outcome": "Precisión >95% en predicción de binding affinity"
    }

    # Paso 2: Evaluar plausibilidad
    scorer = PlausibilityScoringService()
    plausibility_result = await scorer.score_hypothesis(hypothesis)

    print(f"✅ Paso 1 - Evaluación de Plausibilidad: {'APROBADA' if plausibility_result['composite'] > 0.5 else 'RECHAZADA'}")
    print(f"   Puntuación: {plausibility_result['composite']:.3f}")

    if plausibility_result['composite'] > 0.5:
        # Paso 3: Buscar literatura relevante
        search_service = LiteratureSearchService()
        literature_result = await search_service.search_literature({
            "query": hypothesis['title'],
            "domain": hypothesis['domain'],
            "max_results": 5
        })

        print(f"✅ Paso 2 - Búsqueda en Literatura: {len(literature_result.get('papers', []))} papers encontrados")

        # Paso 4: Validar contra literatura
        validation_result = await search_service.validate_hypothesis(hypothesis['description'])

        print("✅ Paso 3 - Validación contra Literatura:")
        print(f"   Estado: {validation_result['validation_status']}")
        print(f"   Confianza: {validation_result['confidence']:.2f}")
        print(f"   Evidencia: {validation_result['total_papers_analyzed']} papers analizados")

        # Resultado final
        if validation_result['validation_status'] in ['strongly_supported', 'supported']:
            print("\n🎉 RESULTADO: Hipótesis VALIDADA y lista para experimentación!")
            return True
        else:
            print("\n⚠️ RESULTADO: Hipótesis necesita refinamiento")
            return False
    else:
        print("\n❌ RESULTADO: Hipótesis rechazada por baja plausibilidad")
        return False

async def main():
    """Ejecutar toda la demostración"""
    print("🚀 AXIOM/ATLAS - DEMOSTRACIÓN DE MEJORAS STATE-OF-THE-ART")
    print("Sistema de investigación científica avanzado con ML y bases de datos reales")

    try:
        # Verificar que estamos en el entorno virtual correcto
        if 'venv_improvements' not in sys.executable:
            print("⚠️ Advertencia: Ejecuta este script con el entorno virtual:")
            print("   source venv_improvements/bin/activate")
            print("   python demo_mejoras.py")
            return

        print(f"🐍 Python: {sys.executable}")

        # Ejecutar demostraciones
        demo1_passed = await demo_advanced_plausibility_scorer()
        demo2_passed = await demo_real_scientific_databases()
        integration_passed = await demo_integration()

        # Resumen final
        print("\n" + "="*60)
        print("📊 RESUMEN DE DEMOSTRACIÓN")
        print("="*60)

        tests = [
            ("Advanced Plausibility Scorer V2", demo1_passed),
            ("Real Scientific Databases V2", demo2_passed),
            ("Integración Completa", integration_passed)
        ]

        passed = 0
        for test_name, result in tests:
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1

        print(f"\n🎯 Resultado General: {passed}/3 demostraciones exitosas")

        if passed == 3:
            print("\n🎉 ¡FELICITACIONES! Todas las mejoras están funcionando perfectamente.")
            print("   AXIOM/ATLAS ahora es una plataforma de investigación científica de vanguardia.")
        else:
            print(f"\n⚠️ {3-passed} demostraciones necesitan atención.")

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
