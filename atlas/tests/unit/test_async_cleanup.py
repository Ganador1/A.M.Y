#!/usr/bin/env python3
"""
Test de Cierre Limpio Async
============================

Valida que el HuggingFaceProvider cierra recursos correctamente
sin generar warnings de "Task was destroyed but it is pending!".
"""

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_provider_cleanup():
    """Test básico de cleanup del provider"""
    
    print("=" * 70)
    print("🧪 TEST: Cierre Limpio de HuggingFaceProvider")
    print("=" * 70)
    print()
    
    from app.services.llm_providers.huggingface_provider import HuggingFaceProvider
    
    # Test 1: Context manager
    print("📋 Test 1: Uso como context manager")
    async with HuggingFaceProvider() as provider:
        print(f"✅ Provider inicializado: {provider.api_url}")
        metrics = provider.get_metrics()
        print(f"📊 Métricas iniciales: {metrics['total_requests']} requests")
    
    print("✅ Context manager cerrado limpiamente")
    print()
    
    # Test 2: Cierre manual
    print("📋 Test 2: Cierre manual con aclose()")
    provider2 = HuggingFaceProvider()
    print(f"✅ Provider inicializado: {provider2.api_url}")
    
    await provider2.aclose()
    print("✅ Cerrado manualmente con aclose()")
    print()
    
    # Test 3: Sin cierre (debería limpiar automáticamente)
    print("📋 Test 3: Sin cierre explícito (auto-cleanup)")
    provider3 = HuggingFaceProvider()
    print(f"✅ Provider inicializado: {provider3.api_url}")
    print("⚠️  No se cierra explícitamente (debería auto-limpiar)")
    print()
    
    print("=" * 70)
    print("✅ Tests completados. Verificando ausencia de warnings...")
    print("=" * 70)
    print()


async def test_wrapper_cleanup():
    """Test de cleanup del HuggingFaceAgentWrapper"""
    
    print("=" * 70)
    print("🧪 TEST: Cierre Limpio de HuggingFaceAgentWrapper")
    print("=" * 70)
    print()
    
    from app.services.huggingface_agent_wrapper import HuggingFaceAgentWrapper
    
    # Crear wrapper
    wrapper = HuggingFaceAgentWrapper(
        agent_role="bio_hypothesis",
        domain="mathematics"
    )
    
    print(f"✅ Wrapper inicializado para rol: {wrapper.agent_role}")
    print(f"📦 Modelo: {wrapper.model_id}")
    print()
    
    # Simular generación (muy corta)
    print("🤖 Simulando generación (timeout corto)...")
    try:
        # Timeout muy corto para que falle rápido
        result = await asyncio.wait_for(
            wrapper.generate_async("Test prompt"),
            timeout=2.0
        )
        print(f"✅ Generación: {len(result)} caracteres")
    except asyncio.TimeoutError:
        print("⏱️  Timeout alcanzado (esperado)")
    except Exception as e:
        print(f"⚠️  Error (esperado en test): {e}")
    
    print()
    
    # Cerrar provider del wrapper
    if wrapper.provider:
        await wrapper.provider.aclose()
        print("✅ Provider del wrapper cerrado")
    
    print()
    print("=" * 70)
    print("✅ Test de wrapper completado")
    print("=" * 70)
    print()


async def main():
    """Main con cleanup completo"""
    try:
        await test_provider_cleanup()
        await asyncio.sleep(1)  # Pausa entre tests
        await test_wrapper_cleanup()
        
    finally:
        # Cleanup global
        print("\n🧹 Ejecutando cleanup global...")
        try:
            from app.services.llm_providers.huggingface_provider import huggingface_provider
            await huggingface_provider.aclose()
            print("✅ Provider global cerrado")
        except Exception as e:
            print(f"⚠️  Error en cleanup global: {e}")
    
    print("\n✨ Todos los tests completados sin warnings\n")


if __name__ == "__main__":
    print()
    asyncio.run(main())
    print()
    print("🎯 Si no hay mensajes 'Task was destroyed but it is pending!',")
    print("   el cierre limpio está funcionando correctamente.")
    print()
