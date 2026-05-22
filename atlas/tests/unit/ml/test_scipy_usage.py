#!/usr/bin/env python3
"""
Script para probar que SciPy se está usando correctamente en el PhysicsToolkit
"""

import asyncio
import sys
import os

# Añadir el directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.experimental_toolkit_hub import PhysicsToolkit

async def test_scipy_usage():
    """Probar que PhysicsToolkit detecta y usa SciPy correctamente"""
    
    print("🔬 Probando uso de SciPy en PhysicsToolkit...")
    
    # Crear instancia del toolkit
    toolkit = PhysicsToolkit()
    
    # Inicializar (debería detectar SciPy)
    initialized = await toolkit.initialize()
    print(f"✅ Toolkit inicializado: {initialized}")
    print(f"✅ SciPy disponible: {toolkit.scipy_available}")
    
    if toolkit.scipy_available:
        print("🎯 SciPy está disponible y debería usarse en las simulaciones")
    else:
        print("⚠️  SciPy no está disponible, usando implementaciones básicas")
    
    # Probar simulación de partícula en caja
    print("\n🧪 Probando simulación de partícula en caja...")
    params = {
        "box_length": 1.0,  # nm
        "mass": 9.109e-31,  # kg (electrón)
        "n_levels": 3
    }
    
    result = await toolkit.run_quantum_simulation("particle_in_box", params)
    print(f"✅ Simulación completada: {len(result.logs)} logs")
    
    # Mostrar logs para ver si se usó SciPy
    for log in result.logs:
        print(f"   📝 {log}")
    
    if result.errors:
        print(f"❌ Errores: {result.errors}")
    else:
        print(f"✅ Energías calculadas: {result.outputs.get('energy_levels_eV', [])}")
    
    # Probar oscilador armónico
    print("\n🧪 Probando oscilador armónico cuántico...")
    params = {
        "spring_constant": 1.0,  # N/m
        "mass": 9.109e-31,  # kg (electrón)
        "n_levels": 3
    }
    
    result = await toolkit.run_quantum_simulation("harmonic_oscillator", params)
    print(f"✅ Simulación completada: {len(result.logs)} logs")
    
    for log in result.logs:
        print(f"   📝 {log}")
    
    if result.errors:
        print(f"❌ Errores: {result.errors}")
    else:
        print(f"✅ Energías calculadas: {result.outputs.get('energy_levels_eV', [])}")
    
    print("\n🎯 Prueba completada!")

if __name__ == "__main__":
    asyncio.run(test_scipy_usage())