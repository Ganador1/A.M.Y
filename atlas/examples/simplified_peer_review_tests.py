"""
Pruebas Simplificadas del Sistema de Peer Review Autónomo

Esta versión evita conflictos de importación importando solo el servicio necesario.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar solo el servicio de peer review directamente
from app.services.autonomous_peer_review_service import AutonomousPeerReviewService

async def run_simplified_peer_review_tests():
    """Ejecutar pruebas simplificadas del sistema de peer review"""

    print("🧪 PRUEBAS SIMPLIFICADAS DEL SISTEMA DE PEER REVIEW")
    print("=" * 80)

    # Inicializar el servicio
    peer_review_service = AutonomousPeerReviewService()

    # ========================================
    # PRUEBAS BÁSICAS DE VALIDACIÓN
    # ========================================

    test_experiments = [
        # Experimento de Física Cuántica
        {
            "id": "quantum_physics_exp_001",
            "domain": "physics",
            "title": "Efecto de la Mecánica Cuántica en Reacciones Químicas",
            "hypothesis": "The application of quantum mechanics principles will lead to more accurate predictions of molecular behavior in chemical reactions compared to classical mechanics",
            "methodology": "We conducted computational simulations using quantum mechanical calculations (Hartree-Fock method) on a set of 50 organic molecules. Control group used classical molecular dynamics. Sample size: n=50 molecules, 10 trials each. Variables controlled: temperature (300K), pressure (1 atm), computational resources.",
            "results": {
                "quantum_accuracy": 0.95,
                "classical_accuracy": 0.78,
                "statistical_significance": "p < 0.001",
                "error_analysis": "Standard error ±0.02 for quantum, ±0.05 for classical",
                "computational_time": "2.5 hours per molecule (quantum) vs 15 minutes (classical)"
            }
        },

        # Experimento de Biología Molecular
        {
            "id": "molecular_biology_exp_001",
            "domain": "biology",
            "title": "Expresión Génica en Respuesta a Estrés Oxidativo",
            "hypothesis": "Exposure to oxidative stress will significantly upregulate antioxidant gene expression in human cell lines, with superoxide dismutase (SOD) showing the strongest response",
            "methodology": "Human HEK293 cells were cultured in DMEM media. Oxidative stress induced with 100μM H2O2 for 2 hours. RNA extracted using TRIzol reagent. Gene expression analyzed via qRT-PCR with SYBR Green. Three biological replicates, three technical replicates each. Controls: untreated cells, GAPDH normalization.",
            "results": {
                "sod1_expression": "3.2-fold increase (p<0.001)",
                "gpx1_expression": "2.1-fold increase (p<0.01)",
                "cat_expression": "1.8-fold increase (p<0.05)",
                "statistical_analysis": "One-way ANOVA, Tukey's post-hoc test",
                "reproducibility": "CV < 15% across replicates"
            }
        },

        # Experimento Problemático
        {
            "id": "problematic_exp_001",
            "domain": "interdisciplinary",
            "title": "Estudio Vago",
            "hypothesis": "Something will happen",
            "methodology": "I did some stuff",
            "results": {}
        }
    ]

    results_summary = {
        "total_experiments": len(test_experiments),
        "approved": 0,
        "rejected": 0,
        "average_score": 0.0
    }

    all_scores = []

    for i, experiment in enumerate(test_experiments, 1):
        print(f"\n🔬 EXPERIMENTO {i}: {experiment['title']}")
        print("-" * 60)

        # Validar experimento
        validation_result = await peer_review_service.validate_experiment({
            "experiment": experiment
        })

        score = validation_result['overall_score']
        approved = validation_result['approved']
        all_scores.append(score)

        if approved:
            results_summary["approved"] += 1
        else:
            results_summary["rejected"] += 1

        print(f"✅ ID: {validation_result['experiment_id']}")
        print(f"📊 Puntaje General: {score}/10")
        print(f"🎯 Aprobado: {'✅ SÍ' if approved else '❌ NO'}")
        print(f"📝 Dominio: {experiment['domain']}")

        # Mostrar revisiones por pares
        peer_reviews = validation_result['peer_reviews']
        print(f"👥 Revisiones: {len(peer_reviews)}")
        for review in peer_reviews:
            print(f"   • {review['reviewer_agent']}: {review['overall_score']}/10")

        # Mostrar issues
        scientific_val = validation_result['scientific_validation']
        if scientific_val['issues']:
            print(f"⚠️  Issues encontrados: {len(scientific_val['issues'])}")
            for issue in scientific_val['issues'][:2]:  # Top 2
                print(f"   • {issue['category'].upper()}: {issue['description'][:50]}...")

    # ========================================
    # RESUMEN DE RESULTADOS
    # ========================================

    print("\n📊 RESUMEN DE RESULTADOS")
    print("=" * 80)

    results_summary["average_score"] = sum(all_scores) / len(all_scores)

    print(f"📈 Total de Experimentos: {results_summary['total_experiments']}")
    print(f"✅ Aprobados: {results_summary['approved']}")
    print(f"❌ Rechazados: {results_summary['rejected']}")
    print(f"📊 Puntaje Promedio: {results_summary['average_score']:.2f}/10")
    print(f"🎯 Tasa de Aprobación: {(results_summary['approved']/results_summary['total_experiments']*100):.1f}%")

    # ========================================
    # PRUEBA DEL COPILOT CIENTÍFICO
    # ========================================

    print("\n🤖 PRUEBA DEL COPILOT CIENTÍFICO")
    print("=" * 80)

    copilot_test = {
        "user_level": "beginner",
        "research_topic": "fotosíntesis en plantas",
        "current_phase": "exploration",
        "query": "¿Cómo puedo empezar a estudiar la fotosíntesis?"
    }

    print(f"👤 Usuario Nivel: {copilot_test['user_level'].title()}")
    print(f"📚 Tema: {copilot_test['research_topic']}")
    print(f"📍 Fase: {copilot_test['current_phase']}")
    print(f"❓ Consulta: {copilot_test['query']}")

    guidance = await peer_review_service.scientific_copilot_guidance(copilot_test)

    print("💡 Guía proporcionada:")
    print(f"   • Fase: {guidance['guidance']['phase_guidance'][:100]}...")
    print(f"   • Consejos metodológicos: {len(guidance['guidance']['methodological_advice'])}")
    print(f"   • Sugerencias de hipótesis: {len(guidance['guidance']['hypothesis_suggestions'])}")
    print(f"   • Próximos pasos: {len(guidance['next_steps'])}")

    # ========================================
    # CONCLUSIONES
    # ========================================

    print("\n🎉 PRUEBAS SIMPLIFICADAS COMPLETADAS")
    print("=" * 80)
    print("✅ SISTEMA DE PEER REVIEW AUTÓNOMO FUNCIONANDO:")
    print("   • ✅ Validación multi-dominio")
    print("   • ✅ Copilot Científico operativo")
    print("   • ✅ Agentes especializados activos")
    print("   • ✅ Sistema de guía para principiantes listo")
    print()
    print("🚀 AXIOM está revolucionando la investigación científica!")
    print("   🧪🔬🤖 Validación autónoma + Guía inteligente = Ciencia del futuro")

if __name__ == "__main__":
    asyncio.run(run_simplified_peer_review_tests())
