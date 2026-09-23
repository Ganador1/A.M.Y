#!/usr/bin/env python3
"""
Suite de pruebas comprehensivas para Agente 1 - Matemáticas y Física Computacional
Valida todos los servicios implementados y su orquestación inteligente
"""

import asyncio
import sys
import json
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

async def test_z3_smt_service():
    """Prueba el servicio Z3 SMT"""
    print("🔧 Probando Z3 SMT Service...")
    
    try:
        from app.services.theorem_proving.z3_smt_service import Z3SMTService
        
        service = Z3SMTService()
        
        # Prueba 1: Verificación simple
        result = await service.verify_simple_tautology("x > 0 => x + 1 > 1")
        print(f"   ✅ Tautología simple: {result['verified']}")
        
        # Prueba 2: Optimización
        constraints = ["x > 0", "y > 0", "x + y < 10"]
        objective = "x + y"
        result = await service.optimize_parameters(objective, constraints)
        print(f"   ✅ Optimización: valor óptimo = {result.get('optimal_value', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en Z3 SMT: {e}")
        return False

async def test_sagemath_service():
    """Prueba el servicio SageMath"""
    print("🧮 Probando SageMath Service...")
    
    try:
        from app.services.sagemath_service import SageMathService
        
        service = SageMathService()
        
        # Prueba 1: Análisis de teoría de números
        result = await service.analyze_number_theory(n=100)
        print(f"   ✅ Teoría de números: analizados {len(result.get('primes', []))} primos")
        
        # Prueba 2: Grupo de Galois
        polynomial = "x^4 - 10*x^2 + 5"  # Ejemplo polinomial
        result = await service.compute_galois_group(polynomial)
        print(f"   ✅ Grupo de Galois: {result.get('group_type', 'N/A')}")
        
        # Prueba 3: Curva elíptica
        result = await service.analyze_elliptic_curve("y^2 = x^3 - x")
        print(f"   ✅ Curva elíptica: rank = {result.get('rank', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en SageMath: {e}")
        return False

async def test_cvc5_service():
    """Prueba el servicio CVC5"""
    print("⚡ Probando CVC5 Service...")
    
    try:
        from app.services.cvc5_service import CVC5Service
        
        service = CVC5Service()
        
        # Prueba 1: Verificación de teoría de strings
        result = await service.verify_string_constraints("len(str) > 5")
        print(f"   ✅ String constraints: {result['status']}")
        
        # Prueba 2: Verificación de teoría de conjuntos  
        result = await service.verify_set_theory("A ∪ B = B ∪ A")
        print(f"   ✅ Set theory: {result['verified']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en CVC5: {e}")
        return False

async def test_quantum_chemistry_service():
    """Prueba el servicio de Química Cuántica"""
    print("⚛️ Probando Quantum Chemistry Service...")
    
    try:
        from app.services.quantum_chemistry_service import QuantumChemistryService, MolecularGeometry
        
        service = QuantumChemistryService()
        
        # Crear geometría molecular H2
        geometry = MolecularGeometry(
            atoms=[("H", (0.0, 0.0, 0.0)), ("H", (0.74, 0.0, 0.0))],
            charge=0,
            spin=0
        )
        
        # Prueba cálculo SCF
        result = await service.run_scf_calculation(geometry)
        print(f"   ✅ SCF calculation: energía = {result.get('total_energy', 'N/A')} Ha")
        
        # Prueba predicción de propiedades
        result = await service.predict_molecular_properties(geometry)
        print(f"   ✅ Propiedades: {len(result.get('properties', {}))} calculadas")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en Quantum Chemistry: {e}")
        return False

async def test_chemml_service():
    """Prueba el servicio ChemML"""
    print("🧬 Probando ChemML Service...")
    
    try:
        from app.services.chemml_service import ChemMLService
        
        service = ChemMLService()
        
        # Prueba predicción de propiedades moleculares
        smiles = ["CCO", "CC(=O)O", "c1ccccc1"]  # etanol, ácido acético, benceno
        result = await service.predict_molecular_properties(smiles)
        print(f"   ✅ Predicción propiedades: {len(result.get('predictions', []))} moléculas")
        
        # Prueba drug-likeness
        result = await service.drug_likeness_assessment(smiles)
        print(f"   ✅ Drug-likeness: promedio = {result.get('average_score', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en ChemML: {e}")
        return False

async def test_particle_physics_service():
    """Prueba el servicio de Física de Partículas"""
    print("🔬 Probando Particle Physics Service...")
    
    try:
        from app.services.particle_physics_service import ParticlePhysicsService
        
        service = ParticlePhysicsService()
        
        # Generar datos de prueba simulados
        test_data = {
            "event_id": 12345,
            "particles": [
                {"pt": 25.5, "eta": 1.2, "phi": 0.8, "mass": 0.511},  # electrón
                {"pt": 30.0, "eta": -0.5, "phi": 2.1, "mass": 0.511}   # positrón
            ]
        }
        
        # Prueba análisis de eventos
        result = await service.analyze_events([test_data])
        print(f"   ✅ Análisis eventos: {len(result.get('analyzed_events', []))} eventos")
        
        # Prueba reconstrucción de jets
        result = await service.reconstruct_jets(test_data)
        print(f"   ✅ Reconstrucción jets: {len(result.get('jets', []))} jets encontrados")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en Particle Physics: {e}")
        return False

async def test_materials_discovery_service():
    """Prueba el servicio de Descubrimiento de Materiales"""
    print("💎 Probando Materials Discovery Service...")
    
    try:
        from app.services.materials_discovery_service import MaterialsDiscoveryService
        
        service = MaterialsDiscoveryService()
        
        # Prueba descubrimiento de materiales para aplicación específica
        result = await service.discover_materials_for_application("solar_cell")
        print(f"   ✅ Materials discovery: {len(result.get('candidates', []))} candidatos")
        
        # Prueba predicción de propiedades
        composition = "LiFePO4"  # Ejemplo: material de batería
        result = await service.predict_material_properties(composition)
        print(f"   ✅ Predicción propiedades: {len(result.get('properties', {}))} propiedades")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en Materials Discovery: {e}")
        return False

async def test_math_physics_orchestrator():
    """Prueba el orquestador principal"""
    print("🎯 Probando Math Physics Orchestrator...")
    
    try:
        from app.services.math_physics_orchestrator import MathPhysicsOrchestrator
        
        orchestrator = MathPhysicsOrchestrator()
        
        # Prueba 1: Hipótesis matemática
        math_request = {
            "domain": "mathematics",
            "subdomain": "number_theory",
            "statement": "Every even integer greater than 2 can be expressed as the sum of two primes",
            "hypothesis_type": "conjecture",
            "complexity": "high"
        }
        
        result = await orchestrator.process_request(math_request)
        print(f"   ✅ Hipótesis matemática: confianza = {result.get('confidence', 'N/A')}")
        
        # Prueba 2: Análisis químico
        chem_request = {
            "domain": "chemistry",
            "subdomain": "quantum_chemistry", 
            "molecular_system": True,
            "molecular_formula": "H2O",
            "analysis_type": "property_prediction"
        }
        
        result = await orchestrator.process_request(chem_request)
        print(f"   ✅ Análisis químico: servicios ejecutados = {len(result.get('results', {}))}")
        
        # Prueba 3: Análisis de física
        physics_request = {
            "domain": "physics",
            "subdomain": "particle_physics",
            "data_source": "collision_events",
            "analysis_type": "event_reconstruction"
        }
        
        result = await orchestrator.process_request(physics_request)
        print(f"   ✅ Análisis física: resultados = {len(result.get('results', {}))}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en Orchestrator: {e}")
        return False

async def run_comprehensive_test():
    """Ejecuta la suite completa de pruebas"""
    print("🚀 INICIANDO SUITE COMPREHENSIVA DE PRUEBAS - AGENTE 1")
    print("=" * 70)
    
    test_results = {}
    
    # Ejecutar todas las pruebas
    tests = [
        ("Z3 SMT Service", test_z3_smt_service),
        ("SageMath Service", test_sagemath_service),
        ("CVC5 Service", test_cvc5_service),
        ("Quantum Chemistry Service", test_quantum_chemistry_service),
        ("ChemML Service", test_chemml_service),
        ("Particle Physics Service", test_particle_physics_service),
        ("Materials Discovery Service", test_materials_discovery_service),
        ("Math Physics Orchestrator", test_math_physics_orchestrator),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print()
        try:
            success = await test_func()
            test_results[test_name] = success
            if success:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            test_results[test_name] = False
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Resumen final
    print()
    print("=" * 70)
    print(f"📊 RESUMEN FINAL DE PRUEBAS")
    print(f"   Pruebas ejecutadas: {total}")
    print(f"   Pruebas exitosas: {passed}")
    print(f"   Pruebas fallidas: {total - passed}")
    print(f"   Tasa de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! Agente 1 está 100% funcional")
    elif passed >= total * 0.7:
        print("✅ Mayoría de pruebas exitosas. Agente 1 está mayormente funcional")
    else:
        print("⚠️  Varias pruebas fallaron. Revisar implementaciones")
    
    # Guardar resultados
    with open("test_results_agent1.json", "w") as f:
        json.dump({
            "timestamp": asyncio.get_event_loop().time(),
            "results": test_results,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "success_rate": (passed/total)*100
            }
        }, f, indent=2)
    
    print(f"📄 Resultados guardados en: test_results_agent1.json")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
