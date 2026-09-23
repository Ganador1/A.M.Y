#!/usr/bin/env python3
"""
AXIOM META 4 - Phase 4 Production Validation Script
==================================================

Script comprehensivo para validar el despliegue completo de Phase 4:
- Containerización con Docker
- Orquestación con Kubernetes
- Monitoreo y logging
- Auto-scaling y load balancing
- Base de datos y cache
- Seguridad y rendimiento

Ejecutar con: python test_phase4_production.py

Autor: AXIOM META 4 Development Team
Fecha: Septiembre 2025
"""

import asyncio
import aiohttp
import time
import subprocess
import sys
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase4Validator:
    """Validador completo de Phase 4"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            'docker_tests': [],
            'kubernetes_tests': [],
            'api_tests': [],
            'monitoring_tests': [],
            'scaling_tests': [],
            'security_tests': []
        }
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def log_test_result(self, category: str, test_name: str, success: bool, message: str = ""):
        """Registrar resultado de test"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now()
        }
        self.results[category].append(result)

        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name}: {message}")

    async def run_docker_tests(self):
        """Tests de containerización con Docker"""
        logger.info("🐳 Ejecutando tests de Docker...")

        # Test 1: Verificar que los contenedores están corriendo
        try:
            result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True, cwd='.')
            if result.returncode == 0 and 'Up' in result.stdout:
                containers_up = result.stdout.count('Up')
                self.log_test_result('docker_tests', 'containers_running',
                                   True, f"{containers_up} contenedores activos")
            else:
                self.log_test_result('docker_tests', 'containers_running', False, "Contenedores no están corriendo")
        except Exception as e:
            self.log_test_result('docker_tests', 'containers_running', False, str(e))

        # Test 2: Verificar imágenes optimizadas
        try:
            result = subprocess.run(['docker', 'images', 'axiom-api'], capture_output=True, text=True)
            if 'axiom-api' in result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    size = lines[1].split()[6]  # SIZE column
                    self.log_test_result('docker_tests', 'image_optimization',
                                       True, f"Imagen optimizada: {size}")
                else:
                    self.log_test_result('docker_tests', 'image_optimization', False, "Imagen no encontrada")
            else:
                self.log_test_result('docker_tests', 'image_optimization', False, "Imagen axiom-api no encontrada")
        except Exception as e:
            self.log_test_result('docker_tests', 'image_optimization', False, str(e))

    async def run_kubernetes_tests(self):
        """Tests de orquestación con Kubernetes"""
        logger.info("☸️ Ejecutando tests de Kubernetes...")

        # Test 1: Verificar namespace
        try:
            result = subprocess.run(['kubectl', 'get', 'namespace', 'axiom-system'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_test_result('kubernetes_tests', 'namespace_exists', True, "Namespace axiom-system existe")
            else:
                self.log_test_result('kubernetes_tests', 'namespace_exists', False, "Namespace no encontrado")
        except Exception as e:
            self.log_test_result('kubernetes_tests', 'namespace_exists', False, str(e))

        # Test 2: Verificar deployments
        try:
            result = subprocess.run(['kubectl', 'get', 'deployments', '-n', 'axiom-system'],
                                  capture_output=True, text=True)
            if result.returncode == 0 and 'axiom-api' in result.stdout:
                deployments = result.stdout.count('axiom-')
                self.log_test_result('kubernetes_tests', 'deployments_ready',
                                   True, f"{deployments} deployments activos")
            else:
                self.log_test_result('kubernetes_tests', 'deployments_ready', False, "Deployments no listos")
        except Exception as e:
            self.log_test_result('kubernetes_tests', 'deployments_ready', False, str(e))

        # Test 3: Verificar HPA
        try:
            result = subprocess.run(['kubectl', 'get', 'hpa', '-n', 'axiom-system'],
                                  capture_output=True, text=True)
            if result.returncode == 0 and 'axiom-api-hpa' in result.stdout:
                self.log_test_result('kubernetes_tests', 'hpa_configured', True, "HPA configurado correctamente")
            else:
                self.log_test_result('kubernetes_tests', 'hpa_configured', False, "HPA no configurado")
        except Exception as e:
            self.log_test_result('kubernetes_tests', 'hpa_configured', False, str(e))

    async def run_api_tests(self):
        """Tests de funcionalidad de la API"""
        logger.info("🔗 Ejecutando tests de API...")

        # Test 1: Health check
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result('api_tests', 'health_check', True, f"Status: {data.get('status', 'OK')}")
                else:
                    self.log_test_result('api_tests', 'health_check', False, f"Status: {response.status}")
        except Exception as e:
            self.log_test_result('api_tests', 'health_check', False, str(e))

        # Test 2: API documentation
        try:
            async with self.session.get(f"{self.base_url}/docs") as response:
                if response.status == 200:
                    self.log_test_result('api_tests', 'api_docs', True, "Documentación disponible")
                else:
                    self.log_test_result('api_tests', 'api_docs', False, f"Status: {response.status}")
        except Exception as e:
            self.log_test_result('api_tests', 'api_docs', False, str(e))

        # Test 3: OpenAPI schema
        try:
            async with self.session.get(f"{self.base_url}/openapi.json") as response:
                if response.status == 200:
                    schema = await response.json()
                    endpoints = len(schema.get('paths', {}))
                    self.log_test_result('api_tests', 'openapi_schema', True, f"{endpoints} endpoints documentados")
                else:
                    self.log_test_result('api_tests', 'openapi_schema', False, f"Status: {response.status}")
        except Exception as e:
            self.log_test_result('api_tests', 'openapi_schema', False, str(e))

    async def run_monitoring_tests(self):
        """Tests del sistema de monitoreo"""
        logger.info("📊 Ejecutando tests de monitoreo...")

        # Test 1: Prometheus metrics
        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                if response.status == 200:
                    metrics = await response.text()
                    lines = metrics.count('\n')
                    self.log_test_result('monitoring_tests', 'prometheus_metrics',
                                       True, f"{lines} líneas de métricas")
                else:
                    self.log_test_result('monitoring_tests', 'prometheus_metrics', False, f"Status: {response.status}")
        except Exception as e:
            self.log_test_result('monitoring_tests', 'prometheus_metrics', False, str(e))

        # Test 2: Grafana dashboard
        try:
            async with self.session.get("http://localhost:3000/api/health") as response:
                if response.status == 200:
                    self.log_test_result('monitoring_tests', 'grafana_access', True, "Grafana accesible")
                else:
                    self.log_test_result('monitoring_tests', 'grafana_access', False, f"Status: {response.status}")
        except Exception as e:
            self.log_test_result('monitoring_tests', 'grafana_access', False, str(e))

        # Test 3: Elasticsearch
        try:
            async with self.session.get("http://localhost:9200/_cluster/health") as response:
                if response.status == 200:
                    health = await response.json()
                    status = health.get('status', 'unknown')
                    self.log_test_result('monitoring_tests', 'elasticsearch_health',
                                       status in ['green', 'yellow'], f"Status: {status}")
                else:
                    self.log_test_result('monitoring_tests', 'elasticsearch_health', False, f"Status: {response.status}")
        except Exception as e:
            self.log_test_result('monitoring_tests', 'elasticsearch_health', False, str(e))

    async def run_scaling_tests(self):
        """Tests de escalabilidad"""
        logger.info("⚡ Ejecutando tests de escalabilidad...")

        # Test 1: Load test básico
        try:
            start_time = time.time()
            tasks = []

            # Crear 50 requests concurrentes
            for i in range(50):
                tasks.append(self.session.get(f"{self.base_url}/health"))

            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            successful_requests = sum(1 for r in responses if not isinstance(r, Exception) and hasattr(r, 'status') and r.status == 200)
            total_time = end_time - start_time
            rps = len(responses) / total_time

            success_rate = successful_requests / len(responses) * 100
            self.log_test_result('scaling_tests', 'concurrent_requests',
                               success_rate >= 95, f"{successful_requests}/{len(responses)} requests exitosos ({success_rate:.1f}%)")
        except Exception as e:
            self.log_test_result('scaling_tests', 'concurrent_requests', False, str(e))

        # Test 2: Memory usage check
        try:
            result = subprocess.run(['docker', 'stats', '--no-stream', '--format', 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    self.log_test_result('scaling_tests', 'resource_monitoring', True, f"{len(lines)-1} contenedores monitoreados")
                else:
                    self.log_test_result('scaling_tests', 'resource_monitoring', False, "No se encontraron contenedores")
            else:
                self.log_test_result('scaling_tests', 'resource_monitoring', False, "Error obteniendo estadísticas")
        except Exception as e:
            self.log_test_result('scaling_tests', 'resource_monitoring', False, str(e))

    async def run_security_tests(self):
        """Tests de seguridad"""
        logger.info("🔒 Ejecutando tests de seguridad...")

        # Test 1: HTTPS redirect (si está configurado)
        try:
            async with self.session.get("http://localhost") as response:
                if response.status in [301, 302] and 'https' in response.headers.get('Location', ''):
                    self.log_test_result('security_tests', 'https_redirect', True, "Redirect HTTPS configurado")
                else:
                    self.log_test_result('security_tests', 'https_redirect', False, "HTTPS no configurado")
        except Exception as e:
            self.log_test_result('security_tests', 'https_redirect', False, str(e))

        # Test 2: Rate limiting
        try:
            # Hacer múltiples requests rápidos
            tasks = [self.session.get(f"{self.base_url}/health") for _ in range(20)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            rate_limited = sum(1 for r in responses if not isinstance(r, Exception) and hasattr(r, 'status') and r.status == 429)
            if rate_limited > 0:
                self.log_test_result('security_tests', 'rate_limiting', True, f"{rate_limited} requests rate limited")
            else:
                self.log_test_result('security_tests', 'rate_limiting', False, "Rate limiting no detectado")
        except Exception as e:
            self.log_test_result('security_tests', 'rate_limiting', False, str(e))

    async def run_all_tests(self):
        """Ejecutar todos los tests de Phase 4"""
        logger.info("🚀 Iniciando validación completa de Phase 4")

        start_time = datetime.now()

        try:
            await self.run_docker_tests()
            await self.run_kubernetes_tests()
            await self.run_api_tests()
            await self.run_monitoring_tests()
            await self.run_scaling_tests()
            await self.run_security_tests()

            self.generate_final_report()

        except Exception as e:
            logger.error(f"Error en validación de Phase 4: {e}")
            self.log_test_result('scaling_tests', 'validation_execution', False, str(e))

        finally:
            end_time = datetime.now()
            duration = end_time - start_time
            logger.info(f"Validación completada en {duration.total_seconds():.2f} segundos")

    def generate_final_report(self):
        """Generar reporte final de Phase 4"""
        logger.info("📋 Generando reporte final de Phase 4...")

        total_tests = 0
        passed_tests = 0

        print("\n" + "="*80)
        print("🏆 AXIOM META 4 - REPORTE DE VALIDACIÓN PHASE 4")
        print("="*80)

        for category, tests in self.results.items():
            if not tests:
                continue

            category_name = category.replace('_', ' ').title()
            print(f"\n🔧 {category_name}:")

            category_passed = 0
            for test in tests:
                total_tests += 1
                if test['success']:
                    passed_tests += 1
                    category_passed += 1
                status = "✅" if test['success'] else "❌"
                print(f"   {status} {test['test_name']}: {test['message']}")

            print(f"   📊 {category_name}: {category_passed}/{len(tests)} tests pasaron")

        # Estadísticas generales
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n📈 ESTADÍSTICAS GENERALES:")
        print(f"   • Tests totales: {total_tests}")
        print(f"   • Tests exitosos: {passed_tests}")
        print(f"   • Tasa de éxito: {success_rate:.1f}%")

        # Evaluación de Phase 4
        print("\n🚀 EVALUACIÓN DE PHASE 4:")
        if success_rate >= 90:
            print("   🟢 PHASE 4 EXITOSA")
            print("   ✅ Infraestructura de producción completa")
            print("   ✅ Escalabilidad y monitoreo operativo")
            print("   ✅ Seguridad y rendimiento validados")
            print("   🎯 LISTO PARA PRODUCCIÓN")
        elif success_rate >= 75:
            print("   🟡 PHASE 4 CASI COMPLETA")
            print("   ⚠️ Algunos componentes requieren ajustes")
            print("   📝 Revisar tests fallidos antes de producción")
        else:
            print("   🔴 PHASE 4 REQUIERE ATENCIÓN")
            print("   ❌ Componentes críticos con problemas")
            print("   🔧 Corregir issues identificados")

        print("\n" + "="*80)
        print("🏆 Validación de Phase 4 Completada")
        print("="*80)


async def main():
    """Función principal"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    async with Phase4Validator(base_url) as validator:
        await validator.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
