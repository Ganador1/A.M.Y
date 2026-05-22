#!/usr/bin/env python3
"""
AXIOM ATLAS - Script de Testing Avanzado
Demuestra todas las mejoras de testing implementadas

Características:
- Testing paralelo con pytest-xdist
- Coverage reporting mejorado
- Mutation testing con mutmut
- Benchmarks de performance
- Testing de calidad de código

Uso:
    python test_improvements.py --parallel      # Testing paralelo
    python test_improvements.py --mutation     # Mutation testing
    python test_improvements.py --benchmark    # Benchmarks
    python test_improvements.py --quality      # Calidad de código
    python test_improvements.py --all          # Todo
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import argparse


class AxiomTestingSuite:
    """Suite de testing avanzado para AXIOM ATLAS"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.start_time = time.time()

    def print_header(self, title):
        """Imprimir header decorado"""
        print("\n" + "=" * 60)
        print(f"🧪 {title}")
        print("=" * 60)

    def run_command(self, command, description, cwd=None):
        """Ejecutar comando con timing"""
        print(f"\n🚀 {description}")
        print(f"📝 Comando: {command}")

        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=False,
                text=True
            )
            elapsed = time.time() - start_time

            if result.returncode == 0:
                print(f"✅ Exitoso ({elapsed:.2f}s)")
                return True, elapsed
            else:
                print(f"❌ Error (código {result.returncode}, {elapsed:.2f}s)")
                return False, elapsed
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Excepción: {e} ({elapsed:.2f}s)")
            return False, elapsed

    def test_parallel(self):
        """Testing paralelo con pytest-xdist"""
        self.print_header("TESTING PARALELO CON PYTEST-XDIST")

        # Testing básico
        success, time_basic = self.run_command(
            "pytest -v tests/ -k 'test_' --tb=short",
            "Testing básico secuencial"
        )

        # Testing paralelo
        success_parallel, time_parallel = self.run_command(
            "pytest -v tests/ -k 'test_' --tb=short -n auto",
            "Testing paralelo con pytest-xdist"
        )

        if success and success_parallel:
            speedup = time_basic / time_parallel if time_parallel > 0 else 1
            print(f"\n📊 SPEEDUP: {speedup:.1f}x más rápido")
            print(f"   Secuencial: {time_basic:.2f}s")
            print(f"   Paralelo:   {time_parallel:.2f}s")

        return success and success_parallel

    def test_coverage(self):
        """Testing con coverage mejorado"""
        self.print_header("COVERAGE REPORTING MEJORADO")

        success, elapsed = self.run_command(
            "pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml --cov-fail-under=70",
            "Testing con coverage mejorado (70% mínimo)"
        )

        # Verificar que se generaron los reportes
        htmlcov_dir = self.project_root / "htmlcov"
        coverage_xml = self.project_root / "coverage.xml"

        if htmlcov_dir.exists():
            print(f"✅ Reporte HTML generado: {htmlcov_dir}")
        if coverage_xml.exists():
            print(f"✅ Reporte XML generado: {coverage_xml}")

        return success

    def test_mutation(self):
        """Mutation testing con mutmut"""
        self.print_header("MUTATION TESTING CON MUTMUT")

        # Instalar mutmut si no está
        if not self._check_mutmut():
            print("⚠️ mutmut no instalado, instalando...")
            self.run_command("pip install mutmut", "Instalando mutmut")

        # Mutation testing (limitado para demo)
        success, elapsed = self.run_command(
            "mutmut run --paths-to-mutate=app/ --tests-dir=tests/ --runner='pytest -x' | head -50",
            "Mutation testing (primeros 50 mutantes)"
        )

        return success

    def test_benchmark(self):
        """Benchmarks de performance"""
        self.print_header("BENCHMARKS DE PERFORMANCE")

        benchmarks = [
            ("Import time", "python -c 'import time; start=time.time(); import app.main; print(f\"Import: {time.time()-start:.2f}s\")'"),
            ("Basic endpoint", "python -c 'import requests; requests.get(\"http://localhost:8000/health\")'"),
        ]

        results = []
        for name, cmd in benchmarks:
            success, elapsed = self.run_command(cmd, f"Benchmark: {name}")
            results.append((name, elapsed, success))

        print("\n📊 RESULTADOS DE BENCHMARKS:")
        for name, elapsed, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {name}: {elapsed:.3f}s")

        return all(success for _, _, success in results)

    def test_quality(self):
        """Testing de calidad de código"""
        self.print_header("CALIDAD DE CÓDIGO")

        # Pre-commit hooks
        success1, _ = self.run_command(
            "pre-commit run --all-files | head -20",
            "Ejecutando pre-commit hooks"
        )

        # Ruff linting
        success2, _ = self.run_command(
            "ruff check app/ --fix | head -15",
            "Linting con Ruff"
        )

        # Black formatting
        success3, _ = self.run_command(
            "black --check --diff app/ | head -15",
            "Verificando formato con Black"
        )

        return success1 and success2 and success3

    def test_all(self):
        """Ejecutar toda la suite"""
        self.print_header("AXIOM ATLAS - SUITE COMPLETA DE TESTING")

        tests = [
            (self.test_parallel, "Testing Paralelo"),
            (self.test_coverage, "Coverage Reporting"),
            (self.test_mutation, "Mutation Testing"),
            (self.test_benchmark, "Benchmarks"),
            (self.test_quality, "Calidad de Código"),
        ]

        results = []
        total_time = 0

        for test_func, description in tests:
            print(f"\n📦 Ejecutando: {description}")
            success = test_func()
            elapsed = time.time() - self.start_time - total_time
            total_time += elapsed
            results.append((description, success, elapsed))

        self._print_final_summary(results, total_time)
        return all(success for _, success, _ in results)

    def _check_mutmut(self):
        """Verificar si mutmut está instalado"""
        try:
            import mutmut
            return True
        except ImportError:
            return False

    def _print_final_summary(self, results, total_time):
        """Imprimir resumen final"""
        print("\n" + "=" * 80)
        print("🏆 RESULTADO FINAL DE LA SUITE DE TESTING")
        print("=" * 80)

        passed = 0
        failed = 0

        for description, success, elapsed in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"  {status} | {description} ({elapsed:.1f}s)")
            if success:
                passed += 1
            else:
                failed += 1

        print("\n📊 ESTADÍSTICAS:")
        print(f"  Tests ejecutados: {len(results)}")
        print(f"  Tests pasados:    {passed}")
        print(f"  Tests fallidos:   {failed}")
        print(f"  Tiempo total:     {total_time:.1f}s")
        print(f"  Tasa de éxito:    {(passed/len(results)*100):.1f}%")

        if failed == 0:
            print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
            print("🚀 AXIOM ATLAS está listo para producción")
        else:
            print(f"\n⚠️ {failed} test(s) fallaron. Revisa los errores arriba.")

        print("\n💡 RECOMENDACIONES:")
        if failed == 0:
            print("  • Considera ejecutar la suite completa en CI/CD")
            print("  • Configura alertas para coverage < 70%")
            print("  • Ejecuta mutation testing regularmente")
            print("  • Monitorea benchmarks de performance")

        print("\n" + "=" * 80)


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Suite avanzada de testing para AXIOM ATLAS")
    parser.add_argument("--parallel", action="store_true", help="Solo testing paralelo")
    parser.add_argument("--coverage", action="store_true", help="Solo coverage")
    parser.add_argument("--mutation", action="store_true", help="Solo mutation testing")
    parser.add_argument("--benchmark", action="store_true", help="Solo benchmarks")
    parser.add_argument("--quality", action="store_true", help="Solo calidad de código")
    parser.add_argument("--all", action="store_true", help="Ejecutar toda la suite")

    args = parser.parse_args()

    suite = AxiomTestingSuite()

    if args.all:
        success = suite.test_all()
    elif args.parallel:
        success = suite.test_parallel()
    elif args.coverage:
        success = suite.test_coverage()
    elif args.mutation:
        success = suite.test_mutation()
    elif args.benchmark:
        success = suite.test_benchmark()
    elif args.quality:
        success = suite.test_quality()
    else:
        print("❌ Especifica qué ejecutar:")
        print("  --all         : Toda la suite")
        print("  --parallel    : Testing paralelo")
        print("  --coverage    : Coverage reporting")
        print("  --mutation    : Mutation testing")
        print("  --benchmark   : Benchmarks")
        print("  --quality     : Calidad de código")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
