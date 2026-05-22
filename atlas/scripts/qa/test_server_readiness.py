#!/usr/bin/env python3
"""
Script de prueba para verificar que AXIOM esté funcionando antes de ejecutar ejemplos avanzados
"""

import requests
import time
import subprocess
import sys


def check_server_health():
    """Verificar que el servidor AXIOM esté funcionando"""
    print("🔍 Verificando estado del servidor AXIOM...")

    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor AXIOM está funcionando correctamente")
            return True
        else:
            print(f"⚠️  Servidor responde con código: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar al servidor: {str(e)}")
        return False


def start_server_if_needed():
    """Iniciar el servidor si no está funcionando"""
    if check_server_health():
        return True

    print("🚀 Iniciando servidor AXIOM...")

    try:
        # Iniciar el servidor en background
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="."
        )

        print("⏳ Esperando que el servidor inicie...")
        time.sleep(5)  # Esperar 5 segundos

        # Verificar nuevamente
        if check_server_health():
            print("✅ Servidor iniciado exitosamente")
            return True
        else:
            print("❌ El servidor no pudo iniciarse correctamente")
            return False

    except Exception as e:
        print(f"❌ Error al iniciar el servidor: {str(e)}")
        return False


def test_basic_endpoints():
    """Probar algunos endpoints básicos"""
    print("\n🧪 Probando endpoints básicos...")

    endpoints = [
        "/api/arithmetic/add",
        "/api/calculus/derivative",
        "/api/pde/info"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8002{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"⚠️  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {str(e)}")


def main():
    """Función principal"""
    print("🧮 Verificación de AXIOM antes de ejecutar ejemplos avanzados")
    print("=" * 60)

    # Verificar e iniciar servidor
    if not start_server_if_needed():
        print("\n❌ No se pudo verificar el servidor AXIOM")
        print("💡 Asegúrate de que el servidor esté ejecutándose")
        return False

    # Probar endpoints básicos
    test_basic_endpoints()

    print("\n✅ Verificación completada. El servidor AXIOM está listo.")
    print("🚀 Puedes ejecutar los ejemplos avanzados ahora.")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
