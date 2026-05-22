#!/usr/bin/env python3
"""
Meta 4 Detailed Diagnostics
Diagnóstico específico de las funcionalidades científicas implementadas
"""

import asyncio
import traceback

async def diagnose_computational_chemistry():
    """Diagnóstico detallado de Química Computacional"""
    print("\n🧪 DIAGNÓSTICO: Química Computacional")
    print("=" * 50)
    
    try:
        from app.services.computational_chemistry import ComputationalChemistryService
        service = ComputationalChemistryService()
        print("✅ Servicio inicializado correctamente")
        
        # Test crystal structure analysis
        print("\n🔍 Test: Análisis de estructuras cristalinas")
        try:
            request = {
                "structure_type": "perovskite",
                "composition": {"A": "Ca", "B": "Ti", "X": "O"},
                "analysis_level": "basic"
            }
            result = await service.analyze_crystal_structure(request)
            print(f"Resultado: {result}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            
        # Test metabolic network
        print("\n🔍 Test: Redes metabólicas")
        try:
            request = {
                "model_name": "test_model",
                "objective": "biomass",
                "analysis_type": "fba"
            }
            result = await service.metabolic_network_analysis(request)
            print(f"Resultado: {result}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error en servicio: {str(e)}")
        traceback.print_exc()

async def diagnose_solid_state_physics():
    """Diagnóstico detallado de Física Computacional"""
    print("\n🔬 DIAGNÓSTICO: Física Computacional")
    print("=" * 50)
    
    try:
        from app.services.solid_state_physics import SolidStatePhysicsService
        service = SolidStatePhysicsService()
        print("✅ Servicio inicializado correctamente")
        
        # Test astrophysical analysis
        print("\n🔍 Test: Análisis astrofísico")
        try:
            request = {
                "material_type": "stellar_core",
                "composition": {"H": 0.7, "He": 0.28, "metals": 0.02},
                "conditions": {"temperature": 1.5e7, "density": 150}
            }
            result = await service.astrophysical_material_analysis(request)
            print(f"Resultado: {result}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            
        # Test cosmological simulation
        print("\n🔍 Test: Simulación cosmológica")
        try:
            request = {
                "simulation_type": "dark_matter",
                "box_size": 100,
                "resolution": 64,
                "redshift_range": [0, 2]
            }
            result = await service.cosmological_simulation(request)
            print(f"Resultado: {result}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error en servicio: {str(e)}")
        traceback.print_exc()

async def diagnose_computational_biology():
    """Diagnóstico detallado de Biología Computacional"""
    print("\n🧬 DIAGNÓSTICO: Biología Computacional")
    print("=" * 50)
    
    try:
        from app.services.computational_biology import ComputationalBiologyService
        service = ComputationalBiologyService()
        print("✅ Servicio inicializado correctamente")
        
        # Test neural simulation
        print("\n🔍 Test: Simulación neural")
        try:
            request = {
                "network_type": "spiking",
                "neurons": 100,
                "simulation_time": 10,
                "input_current": 1.0
            }
            result = await service.neural_network_simulation(request)
            print(f"Resultado: {result}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            
        # Test ecosystem simulation (should work)
        print("\n🔍 Test: Simulación de ecosistemas")
        try:
            request = {
                "model_type": "predator_prey",
                "species": ["wolves", "rabbits"],
                "parameters": {"alpha": 1.0, "beta": 0.1, "gamma": 1.5, "delta": 0.075},
                "time_span": [0, 10],
                "initial_conditions": [10, 5]
            }
            result = await service.ecosystem_simulation(request)
            print(f"Resultado: {result}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error en servicio: {str(e)}")
        traceback.print_exc()

async def test_basic_functionality():
    """Test de funcionalidades básicas que deberían funcionar"""
    print("\n✅ TESTS BÁSICOS")
    print("=" * 50)
    
    # Test imports
    try:
        import pymatgen
        print("✅ pymatgen - Available")
    except ImportError as e:
        print(f"❌ pymatgen: {e}")
    
    try:
        import cobra
        print(f"✅ cobra {cobra.__version__}")
    except ImportError as e:
        print(f"❌ cobra: {e}")
        
    try:
        import astropy
        print(f"✅ astropy {astropy.__version__}")
    except ImportError as e:
        print(f"❌ astropy: {e}")
        
    try:
        import yt
        print("✅ yt - Available")
    except ImportError as e:
        print(f"❌ yt: {e}")
        
    try:
        import brian2
        print(f"✅ brian2 {brian2.__version__}")
    except ImportError as e:
        print(f"❌ brian2: {e}")

async def main():
    """Main diagnosis"""
    print("🔍 AXIOM Meta 4 - Diagnóstico Detallado")
    print("=" * 60)
    
    # Basic tests
    await test_basic_functionality()
    
    # Service diagnostics
    await diagnose_computational_chemistry()
    await diagnose_solid_state_physics()
    await diagnose_computational_biology()
    
    print("\n" + "=" * 60)
    print("🏁 Diagnóstico completado")

if __name__ == "__main__":
    asyncio.run(main())
