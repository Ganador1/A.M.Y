"""
Ejemplo de uso del Autonomous Peer Review Service para AXIOM

Este ejemplo demuestra cómo usar el servicio de validación por pares autónomo
para validar experimentos científicos antes de su publicación.
"""

import asyncio
from app.services.autonomous_peer_review_service import AutonomousPeerReviewService

async def main():
    """Ejemplo de uso del servicio de peer review autónomo"""

    # Inicializar el servicio
    peer_review_service = AutonomousPeerReviewService()

    # Ejemplo 1: Experimento de física
    physics_experiment = {
        "id": "physics_exp_001",
        "domain": "physics",
        "hypothesis": "The application of quantum mechanics principles will lead to more accurate predictions of molecular behavior in chemical reactions compared to classical mechanics",
        "methodology": "We conducted computational simulations using quantum mechanical calculations (Hartree-Fock method) on a set of 50 organic molecules. Control group used classical molecular dynamics. Sample size: n=50 molecules, 10 trials each. Variables controlled: temperature (300K), pressure (1 atm), computational resources.",
        "results": {
            "quantum_accuracy": 0.95,
            "classical_accuracy": 0.78,
            "statistical_significance": "p < 0.001",
            "error_analysis": "Standard error ±0.02 for quantum, ±0.05 for classical",
            "computational_time": "2.5 hours per molecule (quantum) vs 15 minutes (classical)"
        }
    }

    print("🔬 VALIDANDO EXPERIMENTO DE FÍSICA CUÁNTICA")
    print("=" * 60)

    # Validar experimento
    validation_result = await peer_review_service.validate_experiment({
        "experiment": physics_experiment
    })

    print(f"✅ Experimento ID: {validation_result['experiment_id']}")
    print(f"📊 Puntaje General: {validation_result['overall_score']}/10")
    print(f"🎯 Aprobado: {'✅ SÍ' if validation_result['approved'] else '❌ NO'}")
    print()

    # Mostrar validación científica
    scientific_val = validation_result['scientific_validation']
    print("🧪 VALIDACIÓN CIENTÍFICA:")
    print(f"   • Válido: {'✅' if scientific_val['valid'] else '❌'}")
    print(f"   • Puntaje: {scientific_val['score']}/10")
    print(f"   • Issues encontrados: {len(scientific_val['issues'])}")
    print()

    # Mostrar revisiones por pares
    print("👥 REVISIONES POR PARES:")
    for i, review in enumerate(validation_result['peer_reviews'], 1):
        print(f"   {i}. {review['reviewer_agent'].replace('_', ' ').title()}")
        print(f"      • Puntaje: {review['overall_score']}/10")
        print(f"      • Validez Científica: {review['scientific_validity']}/10")
        print(f"      • Rigor Metodológico: {review['methodological_rigor']}/10")
        print(f"      • Contribución Novedosa: {review['novelty_contribution']}/10")
        print(f"      • Aprobado: {'✅' if review['approved'] else '❌'}")
        print(f"      • Issues: {len(review['issues'])}")
        print()

    # Mostrar recomendaciones
    print("💡 RECOMENDACIONES:")
    for rec in validation_result['recommendations'][:5]:  # Top 5
        print(f"   • {rec}")
    print()

    # Ejemplo 2: Experimento problemático (para mostrar detección de issues)
    print("🔬 VALIDANDO EXPERIMENTO PROBLEMÁTICO")
    print("=" * 60)

    problematic_experiment = {
        "id": "bad_exp_001",
        "domain": "chemistry",
        "hypothesis": "This will work",  # Hipótesis vaga
        "methodology": "I mixed some stuff",  # Metodología insuficiente
        "results": {}  # Sin resultados
    }

    validation_result_2 = await peer_review_service.validate_experiment({
        "experiment": problematic_experiment
    })

    print(f"❌ Experimento ID: {validation_result_2['experiment_id']}")
    print(f"📊 Puntaje General: {validation_result_2['overall_score']}/10")
    print(f"🎯 Aprobado: {'✅ SÍ' if validation_result_2['approved'] else '❌ NO'}")
    print()

    # Mostrar issues críticos
    scientific_val_2 = validation_result_2['scientific_validation']
    print("🚨 ISSUES CRÍTICOS ENCONTRADOS:")
    for issue in scientific_val_2['issues']:
        severity_icon = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': 'ℹ️',
            'low': '💡'
        }.get(issue['severity'], '❓')
        print(f"   {severity_icon} {issue['category'].upper()}: {issue['description']}")
        print(f"      Sugerencia: {issue['suggestion']}")
        print()

    print("🎉 DEMOSTRACIÓN COMPLETADA")
    print("El servicio de peer review autónomo puede detectar automáticamente:")
    print("   • Experimentos con fundamentos científicos sólidos")
    print("   • Issues metodológicos y éticos")
    print("   • Falta de rigor científico")
    print("   • Necesidad de revisiones antes de publicación")

if __name__ == "__main__":
    asyncio.run(main())
