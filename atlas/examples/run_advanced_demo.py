#!/usr/bin/env python3
"""
Script integrado para ejecutar ejemplos avanzados de EDP con servidor AXIOM
"""

import subprocess
import time
import signal
import sys
import os
from pde_advanced_examples_clean import PDEAdvancedExamples


def start_server():
    """Iniciar el servidor AXIOM"""
    print("🚀 Iniciando servidor AXIOM...")

    # Cambiar al directorio del proyecto
    os.chdir(".")

    # Activar entorno virtual e iniciar servidor
    env = os.environ.copy()
    env['PATH'] = './.venv/bin:' + env['PATH']

    process = subprocess.Popen(
        ['python', 'main.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    print("⏳ Esperando que el servidor inicie...")
    time.sleep(8)  # Esperar más tiempo

    return process


def stop_server(process):
    """Detener el servidor AXIOM"""
    print("\n🛑 Deteniendo servidor AXIOM...")
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process.wait(timeout=5)
    except:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except:
            pass


def main():
    """Función principal"""
    print("🧮 AXIOM - Demostración Integrada de EDP")
    print("=" * 50)

    server_process = None

    try:
        # Iniciar servidor
        server_process = start_server()

        # Verificar que el servidor esté funcionando
        print("🔍 Verificando servidor...")

        # Intentar importar y usar requests para verificar
        try:
            import requests
            response = requests.get("http://localhost:8002/health", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor AXIOM funcionando correctamente")
            else:
                print(f"⚠️  Servidor responde con código: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Error conectando al servidor: {str(e)}")
            return

        # Ejecutar ejemplos avanzados
        print("\n🎯 Ejecutando ejemplos avanzados de EDP...")
        examples = PDEAdvancedExamples()
        results = examples.run_all_examples()

        print("\n✅ Demostración completada exitosamente!")

        # Mostrar resumen de resultados
        if results:
            print("\n📊 Resumen de resultados:")
            for key, value in results.items():
                if value:
                    print(f"  ✅ {key}: Resuelto")
                else:
                    print(f"  ❌ {key}: Error")

    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {str(e)}")
    finally:
        if server_process:
            stop_server(server_process)


if __name__ == "__main__":
    main()
