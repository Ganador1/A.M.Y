#!/usr/bin/env python3
"""
Test REAL del workflow de AXIOM ATLAS
Usa endpoints que realmente existen en el sistema
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime
from typing import Dict, Any


BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 120.0


class RealWorkflowTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "data_collected": {}
        }

    def log_test(self, name: str, passed: bool, details: Any = None, error: str = None):
        """Registrar resultado de prueba"""
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        self.results["summary"]["total"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
            print(f"✅ {name}")
            if details:
                print(f"   📊 {json.dumps(details, indent=4)[:200]}...")
        else:
            self.results["summary"]["failed"] += 1
            print(f"❌ {name}")
            if error:
                print(f"   ⚠️  Error: {error}")

    async def test_01_health_check(self, client: httpx.AsyncClient):
        """Test 1: Health check del sistema"""
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=30.0)
            result = response.json() if response.status_code == 200 else {}
            self.log_test("01. System Health Check", response.status_code == 200, result)
            return response.status_code == 200
        except Exception as e:
            self.log_test("01. System Health Check", False, error=str(e))
            return False

    async def test_02_dnabert2_sequence_encoding(self, client: httpx.AsyncClient):
        """Test 2: Codificación de secuencia genómica con DNABERT2"""
        try:
            payload = {
                "sequence": "ATGCGATCGATCGATCGATCGATCGATCG",
                "k": 6
            }
            response = await client.post(
                f"{BASE_URL}/api/dnabert2/encode-sequence",
                json=payload,
                timeout=TIMEOUT
            )
            result = response.json() if response.status_code == 200 else {}
            self.results["data_collected"]["dnabert2_encoding"] = result
            self.log_test("02. DNABERT2 Sequence Encoding", response.status_code == 200, result)
            return result
        except Exception as e:
            self.log_test("02. DNABERT2 Sequence Encoding", False, error=str(e))
            return {}

    async def test_03_dnabert2_predict_motifs(self, client: httpx.AsyncClient):
        """Test 3: Predicción de motivos genéticos"""
        try:
            payload = {
                "sequence": "ATGCGATCGATCGATCGATCGATCGATCGTACGATCGATCG",
                "k": 6,
                "threshold": 0.7
            }
            response = await client.post(
                f"{BASE_URL}/api/dnabert2/predict-motifs",
                json=payload,
                timeout=TIMEOUT
            )
            result = response.json() if response.status_code == 200 else {}
            self.results["data_collected"]["motif_predictions"] = result
            self.log_test("03. DNABERT2 Motif Prediction", response.status_code == 200, result)
            return result
        except Exception as e:
            self.log_test("03. DNABERT2 Motif Prediction", False, error=str(e))
            return {}

    async def test_04_create_experiment_job(self, client: httpx.AsyncClient):
        """Test 4: Crear job experimental"""
        try:
            payload = {
                "name": "Test Genomic Analysis Job",
                "experiment_type": "genomics",
                "priority": "high",
                "parameters": {
                    "analysis_type": "motif_discovery",
                    "sequence_count": 100
                },
                "estimated_duration": 300
            }
            response = await client.post(
                f"{BASE_URL}/api/infrastructure/experiment-scheduler/scheduler/jobs",
                json=payload,
                timeout=TIMEOUT
            )
            result = response.json() if response.status_code in [200, 201] else {}
            job_id = result.get("job_uuid", result.get("id", ""))
            self.results["data_collected"]["job_id"] = job_id
            self.log_test("04. Create Experiment Job", response.status_code in [200, 201], result)
            return job_id
        except Exception as e:
            self.log_test("04. Create Experiment Job", False, error=str(e))
            return ""

    async def test_05_query_job_status(self, client: httpx.AsyncClient, job_id: str):
        """Test 5: Consultar estado del job"""
        try:
            if not job_id:
                self.log_test("05. Query Job Status", False, error="No job ID available")
                return {}

            response = await client.get(
                f"{BASE_URL}/api/infrastructure/experiment-scheduler/scheduler/jobs/{job_id}",
                timeout=30.0
            )
            result = response.json() if response.status_code == 200 else {}
            self.log_test("05. Query Job Status", response.status_code == 200, result)
            return result
        except Exception as e:
            self.log_test("05. Query Job Status", False, error=str(e))
            return {}

    async def test_06_start_experiment_tracking(self, client: httpx.AsyncClient):
        """Test 6: Iniciar tracking de experimento"""
        try:
            payload = {
                "experiment_name": "Genomics Workflow Test",
                "tags": ["test", "genomics", "workflow"],
                "parameters": {
                    "domain": "biology",
                    "method": "motif_analysis"
                }
            }
            response = await client.post(
                f"{BASE_URL}/api/infrastructure/experiment-tracking/experiments",
                json=payload,
                timeout=TIMEOUT
            )
            result = response.json() if response.status_code in [200, 201] else {}
            exp_id = result.get("experiment_id", result.get("id", ""))
            self.results["data_collected"]["experiment_id"] = exp_id
            self.log_test("06. Start Experiment Tracking", response.status_code in [200, 201], result)
            return exp_id
        except Exception as e:
            self.log_test("06. Start Experiment Tracking", False, error=str(e))
            return ""

    async def test_07_log_experiment_metric(self, client: httpx.AsyncClient, exp_id: str):
        """Test 7: Registrar métrica del experimento"""
        try:
            if not exp_id:
                self.log_test("07. Log Experiment Metric", False, error="No experiment ID")
                return False

            payload = {
                "experiment_id": exp_id,
                "metric_name": "accuracy",
                "metric_value": 0.87,
                "step": 1
            }
            response = await client.post(
                f"{BASE_URL}/api/infrastructure/experiment-tracking/log-metric",
                json=payload,
                timeout=30.0
            )
            result = response.json() if response.status_code == 200 else {}
            self.log_test("07. Log Experiment Metric", response.status_code == 200, result)
            return response.status_code == 200
        except Exception as e:
            self.log_test("07. Log Experiment Metric", False, error=str(e))
            return False

    async def test_08_cache_operations(self, client: httpx.AsyncClient):
        """Test 8: Operaciones de caché"""
        try:
            response = await client.get(
                f"{BASE_URL}/api/infrastructure/cache/stats",
                timeout=30.0
            )
            result = response.json() if response.status_code == 200 else {}
            self.log_test("08. Cache Statistics", response.status_code == 200, result)
            return result
        except Exception as e:
            self.log_test("08. Cache Statistics", False, error=str(e))
            return {}

    async def test_09_async_task_submission(self, client: httpx.AsyncClient):
        """Test 9: Envío de tarea asíncrona"""
        try:
            payload = {
                "task_type": "scientific_computation",
                "parameters": {
                    "computation": "sequence_analysis",
                    "data_size": 1000
                }
            }
            response = await client.post(
                f"{BASE_URL}/api/infrastructure/async-processor/async/submit",
                json=payload,
                timeout=TIMEOUT
            )
            result = response.json() if response.status_code in [200, 201] else {}
            task_id = result.get("task_id", "")
            self.results["data_collected"]["async_task_id"] = task_id
            self.log_test("09. Async Task Submission", response.status_code in [200, 201], result)
            return task_id
        except Exception as e:
            self.log_test("09. Async Task Submission", False, error=str(e))
            return ""

    async def test_10_query_async_task(self, client: httpx.AsyncClient, task_id: str):
        """Test 10: Consultar estado de tarea asíncrona"""
        try:
            if not task_id:
                self.log_test("10. Query Async Task", False, error="No task ID")
                return {}

            response = await client.get(
                f"{BASE_URL}/api/infrastructure/async-processor/async/status/{task_id}",
                timeout=30.0
            )
            result = response.json() if response.status_code == 200 else {}
            self.log_test("10. Query Async Task", response.status_code == 200, result)
            return result
        except Exception as e:
            self.log_test("10. Query Async Task", False, error=str(e))
            return {}

    async def test_11_data_versioning_init(self, client: httpx.AsyncClient):
        """Test 11: Inicializar versionado de datos"""
        try:
            payload = {
                "dataset_name": "test_genomic_dataset",
                "description": "Dataset de prueba para análisis genómico",
                "metadata": {
                    "source": "test_workflow",
                    "type": "genomics"
                }
            }
            response = await client.post(
                f"{BASE_URL}/api/infrastructure/data-versioning/init-dataset",
                json=payload,
                timeout=30.0
            )
            result = response.json() if response.status_code in [200, 201] else {}
            self.log_test("11. Initialize Data Versioning", response.status_code in [200, 201], result)
            return result
        except Exception as e:
            self.log_test("11. Initialize Data Versioning", False, error=str(e))
            return {}

    async def test_12_agent_bridge_health(self, client: httpx.AsyncClient):
        """Test 12: Health check del agent bridge"""
        try:
            response = await client.get(
                f"{BASE_URL}/api/agent2-bridge/health",
                timeout=30.0
            )
            result = response.json() if response.status_code == 200 else {}
            self.log_test("12. Agent Bridge Health", response.status_code == 200, result)
            return result
        except Exception as e:
            self.log_test("12. Agent Bridge Health", False, error=str(e))
            return {}

    async def test_13_agent_bridge_services(self, client: httpx.AsyncClient):
        """Test 13: Listar servicios disponibles en agent bridge"""
        try:
            response = await client.get(
                f"{BASE_URL}/api/agent2-bridge/services",
                timeout=30.0
            )
            result = response.json() if response.status_code == 200 else {}
            self.results["data_collected"]["available_services"] = result
            self.log_test("13. List Agent Bridge Services", response.status_code == 200, result)
            return result
        except Exception as e:
            self.log_test("13. List Agent Bridge Services", False, error=str(e))
            return {}

    async def test_14_system_metrics(self, client: httpx.AsyncClient):
        """Test 14: Obtener métricas del sistema"""
        try:
            response = await client.get(f"{BASE_URL}/metrics", timeout=30.0)
            result = response.json() if response.status_code == 200 else {}
            self.log_test("14. System Metrics", response.status_code == 200, result)
            return result
        except Exception as e:
            self.log_test("14. System Metrics", False, error=str(e))
            return {}

    async def run_complete_workflow(self):
        """Ejecutar el workflow completo de pruebas REALES"""
        print("\n" + "="*80)
        print("🧪 AXIOM ATLAS - Test de Workflow REAL (Endpoints Existentes)")
        print("="*80 + "\n")

        async with httpx.AsyncClient() as client:
            # Test 1: Health check
            print("🏥 Test 1: System Health")
            if not await self.test_01_health_check(client):
                print("\n⚠️  Health check falló. Continuando con otros tests...")

            # Test 2-3: DNABERT2 (Biology domain)
            print("\n🧬 Tests 2-3: DNABERT2 Genomics Analysis")
            await self.test_02_dnabert2_sequence_encoding(client)
            await self.test_03_dnabert2_predict_motifs(client)

            # Test 4-5: Experiment Scheduler
            print("\n📅 Tests 4-5: Experiment Scheduling")
            job_id = await self.test_04_create_experiment_job(client)
            if job_id:
                await asyncio.sleep(1)  # Breve pausa
                await self.test_05_query_job_status(client, job_id)

            # Test 6-7: Experiment Tracking
            print("\n📊 Tests 6-7: Experiment Tracking")
            exp_id = await self.test_06_start_experiment_tracking(client)
            if exp_id:
                await self.test_07_log_experiment_metric(client, exp_id)

            # Test 8: Cache
            print("\n💾 Test 8: Cache Operations")
            await self.test_08_cache_operations(client)

            # Test 9-10: Async Processing
            print("\n⚡ Tests 9-10: Async Task Processing")
            task_id = await self.test_09_async_task_submission(client)
            if task_id:
                await asyncio.sleep(1)
                await self.test_10_query_async_task(client, task_id)

            # Test 11: Data Versioning
            print("\n🔄 Test 11: Data Versioning")
            await self.test_11_data_versioning_init(client)

            # Test 12-13: Agent Bridge
            print("\n🤖 Tests 12-13: Multi-Agent Bridge")
            await self.test_12_agent_bridge_health(client)
            await self.test_13_agent_bridge_services(client)

            # Test 14: System Metrics
            print("\n📈 Test 14: System-Wide Metrics")
            await self.test_14_system_metrics(client)

        # Resumen final
        self.print_summary()
        self.save_results()

    def print_summary(self):
        """Imprimir resumen de resultados"""
        print("\n" + "="*80)
        print("📋 RESUMEN FINAL DE PRUEBAS")
        print("="*80)

        summary = self.results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"\n📊 Estadísticas:")
        print(f"  • Total de pruebas ejecutadas: {total}")
        print(f"  • ✅ Exitosas: {passed}")
        print(f"  • ❌ Fallidas: {failed}")
        print(f"  • 📈 Tasa de éxito: {success_rate:.1f}%")

        if failed > 0:
            print(f"\n⚠️  Pruebas fallidas ({failed}):")
            for test in self.results["tests"]:
                if not test["passed"]:
                    print(f"  • {test['name']}")
                    if test.get('error'):
                        print(f"    └─ {test['error']}")

        if self.results["data_collected"]:
            print(f"\n📦 Datos recolectados:")
            for key, value in self.results["data_collected"].items():
                print(f"  • {key}: {type(value).__name__}")

        print("\n" + "="*80 + "\n")

    def save_results(self):
        """Guardar resultados detallados"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"real_workflow_test_{timestamp}.json"
        filepath = f"./reports/{filename}"

        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"✅ Resultados detallados guardados en: {filepath}\n")
        except Exception as e:
            print(f"⚠️  Error al guardar resultados: {e}\n")


async def main():
    tester = RealWorkflowTester()
    await tester.run_complete_workflow()

    # Código de salida basado en resultados
    if tester.results["summary"]["failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())