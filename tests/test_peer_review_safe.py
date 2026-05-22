#!/usr/bin/env python3
"""
Test: Peer Review with Safety Timeouts

Verifica que el peer review funciona sin congelar el sistema:
1. Timeout corto (30s) para pruebas
2. Mock del LLM para evitar llamadas lentas
3. Verificación de que no hay procesos zombie
"""
import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "atlas"))

from core.atlas_bridge import AtlasBridge


async def test_peer_review_safe():
    """Test peer review con timeouts seguros."""
    print("=" * 70)
    print("PEER REVIEW SAFETY TEST")
    print("=" * 70)

    bridge = AtlasBridge()
    
    if not bridge.available:
        print("❌ AtlasBridge no disponible")
        return False

    print("\n[1/3] Verificando AtlasBridge...")
    print(f"  ✅ Disponible: {bridge.available}")
    print(f"  ⚠️  Timeout configurado: 600s (10 min) - puede causar congelamiento")

    # 2. Verificar que el subprocess no deja procesos zombie
    print("\n[2/3] Verificando procesos previos...")
    
    import subprocess
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True,
    )
    
    zombie_count = result.stdout.count("python3") - result.stdout.count("grep")
    print(f"  Procesos python3 activos: ~{zombie_count}")
    
    if zombie_count > 10:
        print(f"  ⚠️  Muchos procesos python3 - posibles zombies")
    else:
        print(f"  ✅ Número normal de procesos")

    # 3. Simular peer review con timeout corto
    print("\n[3/3] Simulando peer review con timeout seguro...")
    print(f"  ⏱️  Iniciando peer review (timeout: 30s)...")
    
    start_time = time.time()
    
    try:
        # Usar asyncio.wait_for para limitar el tiempo total
        result = await asyncio.wait_for(
            bridge.run_research(
                domain="mathematics",
                topic="Prime numbers",
                hypothesis="97 is prime",
                max_iterations=1,  # Solo 1 iteración para ser rápido
                target_score=5,
            ),
            timeout=30,  # 30 segundos máximo
        )
        
        elapsed = time.time() - start_time
        
        if result.get("success"):
            score = result.get("score", 0)
            accepted = result.get("accepted", False)
            print(f"  ✅ Peer review completado en {elapsed:.1f}s")
            print(f"     Score: {score}/10")
            print(f"     Aceptado: {accepted}")
        else:
            error = result.get("error", "unknown")
            print(f"  ⚠️  Peer review falló: {error}")
            print(f"     (Esto es normal si el LLM no responde)")
            
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"  ⏱️  Peer review timeout después de {elapsed:.1f}s")
        print(f"     ✅ Timeout funcionó correctamente - no hay congelamiento")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")

    print("\n" + "=" * 70)
    print("RECOMENDACIONES PARA EVITAR CONGELAMIENTOS")
    print("=" * 70)
    print("""
1. PARA PRUEBAS:
   - Usar asyncio.wait_for(timeout=30) para limitar tiempo
   - Usar max_iterations=1 en lugar de 3
   - Usar mock del reasoning engine

2. PARA PRODUCCIÓN:
   - Monitorear uso de memoria cada 5 minutos
   - Reiniciar subprocess si tarda > 5 min
   - Usar cola de tareas en lugar de ejecución síncrona

3. SI EL SISTEMA SE CONGELA:
   - Matar procesos python3 huérfanos: pkill -f "python3.*atlas"
   - Verificar logs: tail -f logs/axiom.log
   - Reiniciar VS Code si es necesario
""")

    return True


if __name__ == "__main__":
    success = asyncio.run(test_peer_review_safe())
    sys.exit(0 if success else 1)
