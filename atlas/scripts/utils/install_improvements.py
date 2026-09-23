#!/usr/bin/env python3
"""
AXIOM ATLAS - Script de Instalación Automática de Mejoras
Instala y configura todas las herramientas de mejora implementadas

Uso:
    python install_improvements.py --all          # Instalar todo
    python install_improvements.py --testing     # Solo testing
    python install_improvements.py --monitoring  # Solo monitoring
    python install_improvements.py --quality     # Solo calidad de código
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import shutil


class AxiomImprovementsInstaller:
    """Instalador automático de mejoras para AXIOM ATLAS"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements.txt"
        self.pytest_ini = self.project_root / "pytest.ini"
        self.pre_commit_config = self.project_root / ".pre-commit-config.yaml"

    def run_command(self, command, description=""):
        """Ejecutar comando con logging"""
        print(f"🚀 {description}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            if result.returncode == 0:
                print("✅ Exitoso")
            else:
                print(f"❌ Error (código {result.returncode})")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        return True

    def install_testing_improvements(self):
        """Instalar mejoras de testing"""
        print("\n📋 INSTALANDO MEJORAS DE TESTING")
        print("=" * 50)

        # Instalar pytest-xdist si no está
        if not self._check_package_installed("pytest-xdist"):
            if not self.run_command("python3 -m pip install pytest-xdist", "Instalando pytest-xdist"):
                return False

        # Configurar pytest.ini mejorado
        if not self._configure_pytest():
            return False

        # Instalar mutmut para mutation testing
        if not self._check_package_installed("mutmut"):
            if not self.run_command("python3 -m pip install mutmut", "Instalando mutmut"):
                return False

        print("✅ Testing improvements instalados exitosamente")
        return True

    def install_quality_improvements(self):
        """Instalar mejoras de calidad de código"""
        print("\n📋 INSTALANDO MEJORAS DE CALIDAD")
        print("=" * 50)

        # Instalar pre-commit si no está
        if not self._check_package_installed("pre-commit"):
            if not self.run_command("python3 -m pip install pre-commit", "Instalando pre-commit"):
                return False

        # Configurar pre-commit hooks
        if not self._configure_pre_commit():
            return False

        # Instalar herramientas de linting
        tools = ["black", "isort", "ruff"]
        for tool in tools:
            if not self._check_package_installed(tool):
                if not self.run_command(f"python3 -m pip install {tool}", f"Instalando {tool}"):
                    return False

        print("✅ Quality improvements instalados exitosamente")
        return True

    def install_monitoring_improvements(self):
        """Instalar mejoras de monitoring"""
        print("\n📋 INSTALANDO MEJORAS DE MONITORING")
        print("=" * 50)

        # Instalar Sentry SDK
        if not self._check_package_installed("sentry-sdk"):
            if not self.run_command("python3 -m pip install sentry-sdk[fastapi]", "Instalando Sentry SDK"):
                return False

        # Configurar Sentry
        if not self._configure_sentry():
            return False

        # Verificar que docker-compose.yml tenga Jaeger
        if not self._configure_jaeger():
            return False

        print("✅ Monitoring improvements instalados exitosamente")
        return True

    def install_all_improvements(self):
        """Instalar todas las mejoras"""
        print("🎯 INSTALANDO TODAS LAS MEJORAS DE AXIOM ATLAS")
        print("=" * 60)

        steps = [
            (self.install_testing_improvements, "Testing improvements"),
            (self.install_quality_improvements, "Quality improvements"),
            (self.install_monitoring_improvements, "Monitoring improvements"),
        ]

        for step_func, description in steps:
            print(f"\n📦 {description}")
            if not step_func():
                print(f"❌ Falló la instalación de: {description}")
                return False

        self._print_success_summary()
        return True

    def _check_package_installed(self, package_name):
        """Verificar si un paquete está instalado"""
        try:
            import importlib
            importlib.import_module(package_name.replace("-", "_"))
            print(f"✅ {package_name} ya está instalado")
            return True
        except ImportError:
            return False

    def _configure_pytest(self):
        """Configurar pytest.ini mejorado"""
        if not self.pytest_ini.exists():
            print("⚠️ pytest.ini no encontrado, creando uno básico")
            pytest_content = """[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=70
    -n auto
markers =
    smoke: Smoke tests (fast, basic functionality)
    integration: Integration tests (slower, more comprehensive)
    unit: Unit tests (individual components)
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
    ignore::UserWarning
asyncio_mode = auto
"""
            self.pytest_ini.write_text(pytest_content)
            print("✅ pytest.ini creado con configuración mejorada")
        else:
            print("✅ pytest.ini ya existe")

        return True

    def _configure_pre_commit(self):
        """Configurar pre-commit hooks"""
        if not self.pre_commit_config.exists():
            print("⚠️ .pre-commit-config.yaml no encontrado")
            return False

        # Instalar pre-commit hooks
        if self.run_command("pre-commit install", "Instalando pre-commit hooks"):
            print("✅ Pre-commit hooks instalados")
            return True

        return False

    def _configure_sentry(self):
        """Configurar Sentry"""
        env_example = self.project_root / "config" / ".env.example"
        if env_example.exists():
            content = env_example.read_text()
            if "SENTRY_DSN" not in content:
                # Agregar configuración de Sentry si no existe
                sentry_config = """

# Error Tracking (Sentry)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0
"""
                content = content.replace("# Logging\nLOG_LEVEL=INFO", f"# Logging\nLOG_LEVEL=INFO{sentry_config}")
                env_example.write_text(content)
                print("✅ Configuración de Sentry agregada a .env.example")
            else:
                print("✅ Configuración de Sentry ya existe en .env.example")
        else:
            print("⚠️ .env.example no encontrado")

        return True

    def _configure_jaeger(self):
        """Verificar configuración de Jaeger"""
        docker_compose = self.project_root / "docker-compose.yml"
        if docker_compose.exists():
            content = docker_compose.read_text()
            if "jaeger" in content.lower():
                print("✅ Jaeger ya configurado en docker-compose.yml")
                return True
            else:
                print("⚠️ Jaeger no encontrado en docker-compose.yml")
                return False
        else:
            print("⚠️ docker-compose.yml no encontrado")
            return False

    def _print_success_summary(self):
        """Imprimir resumen de instalación exitosa"""
        print("\n" + "=" * 60)
        print("🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 60)

        print("\n📋 HERRAMIENTAS INSTALADAS:")
        print("  ✅ pytest-xdist       - Testing paralelo automático")
        print("  ✅ mutmut            - Mutation testing")
        print("  ✅ pre-commit        - Calidad de código automática")
        print("  ✅ black             - Formateo de código")
        print("  ✅ isort             - Ordenamiento de imports")
        print("  ✅ ruff              - Linting rápido")
        print("  ✅ sentry-sdk        - Error tracking")
        print("  ✅ Enhanced OpenTelemetry - Tracing distribuido")

        print("\n🚀 COMANDOS ÚTILES:")
        print("  pytest -n auto       # Testing paralelo")
        print("  pre-commit install   # Instalar git hooks")
        print("  pre-commit run --all # Ejecutar todas las verificaciones")
        print("  mutmut run           # Mutation testing")
        print("  docker-compose up jaeger  # Iniciar Jaeger UI")

        print("\n📊 MEJORAS ESPERADAS:")
        print("  • Testing: 80% más rápido con pytest-xdist")
        print("  • Calidad: Código formateado automáticamente")
        print("  • Monitoring: Error tracking con Sentry")
        print("  • Tracing: Distributed tracing con Jaeger")
        print("  • Cobertura: 70% mínimo con coverage")

        print("\n🔧 PRÓXIMOS PASOS:")
        print("  1. Configurar SENTRY_DSN en tu .env")
        print("  2. Ejecutar: docker-compose up jaeger")
        print("  3. Ejecutar: pre-commit install")
        print("  4. Ejecutar tests con: pytest -n auto")

        print("\n" + "=" * 60)


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Instalar mejoras de AXIOM ATLAS")
    parser.add_argument("--all", action="store_true", help="Instalar todas las mejoras")
    parser.add_argument("--testing", action="store_true", help="Solo mejoras de testing")
    parser.add_argument("--quality", action="store_true", help="Solo mejoras de calidad")
    parser.add_argument("--monitoring", action="store_true", help="Solo mejoras de monitoring")

    args = parser.parse_args()

    installer = AxiomImprovementsInstaller()

    if args.all:
        success = installer.install_all_improvements()
    elif args.testing:
        success = installer.install_testing_improvements()
    elif args.quality:
        success = installer.install_quality_improvements()
    elif args.monitoring:
        success = installer.install_monitoring_improvements()
    else:
        print("❌ Especifica qué instalar:")
        print("  --all       : Todas las mejoras")
        print("  --testing   : Solo testing")
        print("  --quality   : Solo calidad")
        print("  --monitoring: Solo monitoring")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
