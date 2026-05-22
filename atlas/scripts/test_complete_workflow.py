#!/usr/bin/env python3
"""
Test completo del workflow de AXIOM ATLAS
Prueba el flujo end-to-end: Hipótesis -> Plausibilidad -> Scheduler -> Workflow -> Análisis
"""

import asyncio
import httpx
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List


BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 120.0


class WorkflowTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"total": 0, "passed": 0, "failed": 0}
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
        else:
            self.results["summary"]["failed"] += 1
            print(f"❌ {name}")
            if error:
                print(f"   Error: {error}")

    async def test_health_check(self, client: httpx.AsyncClient):
        """Test 1: Health check básico"""
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=30.0)
            passed = response.status_code == 200
            self.log_test("Health Check", passed, response.json() if passed else None)
            return passed
        except Exception as e:
            self.log_test("Health Check", False, error=str(e))
            return False

    async def test_generate_hypothesis(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Test 2: Generación de hipótesis científica"""
        try:
            # Intentar con el endpoint de plausibilidad
            payload = {
                "hypothesis": "La conductividad térmica de nanoestructuras de grafeno aumenta linealmente con la concentración de defectos hasta un punto crítico",
                "domain": "materials_science",
                "context": {
                    "material": "graphene",
                    "property": "thermal_conductivity",
                    "temperature_range": [300, 500]
                },
                "metadata": {
                    "researcher": "workflow_test",
                    "priority": "high"
                }
            }

            response = await client.post(
                f"{BASE_URL}/api/plausibility/evaluate",
                json=payload,
                timeout=TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                passed = result.get("success", False) or "plausibility_score" in result
                self.log_test("Generate Hypothesis", passed, result)
                return result
            else:
                # Intentar endpoint alternativo
                alt_response = await client.post(
                    f"{BASE_URL}/api/scientific-hypothesis/generate-hypothesis",
                    json={
                        "domain": "materials_science",
                        "research_question": "¿Cómo afectan los defectos a la conductividad térmica del grafeno?",
                        "context_data": payload["context"]
                    },
                    timeout=TIMEOUT
                )

                if alt_response.status_code == 200:
                    result = alt_response.json()
                    self.log_test("Generate Hypothesis (alt)", True, result)
                    return result
                else:
                    self.log_test("Generate Hypothesis", False, error=f"Status: {response.status_code}")
                    return {}

        except Exception as e:
            self.log_test("Generate Hypothesis", False, error=str(e))
            return {}

    async def test_plausibility_evaluation(self, client: httpx.AsyncClient, hypothesis: str) -> float:
        """Test 3: Evaluación de plausibilidad"""
        try:
            payload = {
                "hypothesis": hypothesis,
                "domain": "materials_science",
                "check_literature": False,  # Desactivar para pruebas rápidas
                "require_prior_evidence": False
            }

            response = await client.post(
                f"{BASE_URL}/api/plausibility/evaluate",
                json=payload,
                timeout=TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                score = result.get("plausibility_score", result.get("score", 0.0))
                self.log_test("Plausibility Evaluation", True, {"score": score, "details": result})
                return score
            else:
                self.log_test("Plausibility Evaluation", False, error=f"Status: {response.status_code}")
                return 0.0

        except Exception as e:
            self.log_test("Plausibility Evaluation", False, error=str(e))
            return 0.0

    async def test_schedule_experiment(self, client: httpx.AsyncClient, hypothesis_data: Dict) -> str:
        """Test 4: Agendar experimento"""
        try:
            job_payload = {
                "name": "Test Graphene Conductivity Experiment",
                "experiment_type": "computational_simulation",
                "priority": "high",
                "parameters": {
                    "hypothesis_id": hypothesis_data.get("id", "test_hyp_001"),
                    "simulation_type": "molecular_dynamics",
                    "material": "graphene",
                    "temperature": 400
                },
                "estimated_duration": 300,
                "resources": {
                    "cpu_cores": 4,
                    "memory_gb": 8,
                    "gpu_required": False
                }
            }

            response = await client.post(
                f"{BASE_URL}/api/scheduler/jobs",
                json=job_payload,
                timeout=TIMEOUT
            )

            if response.status_code in [200, 201]:
                result = response.json()
                job_id = result.get("job_id", result.get("id", ""))
                self.log_test("Schedule Experiment", True, {"job_id": job_id, "details": result})
                return job_id
            else:
                self.log_test("Schedule Experiment", False, error=f"Status: {response.status_code}")
                return ""

        except Exception as e:
            self.log_test("Schedule Experiment", False, error=str(e))
            return ""

    async def test_create_workflow(self, client: httpx.AsyncClient, job_id: str) -> str:
        """Test 5: Crear workflow de ejecución"""
        try:
            workflow_payload = {
                "name": "Materials Testing Workflow",
                "description": "Workflow automático para pruebas de materiales",
                "steps": [
                    {
                        "id": "step_1",
                        "name": "Initialize Simulation",
                        "type": "initialization",
                        "parameters": {"job_id": job_id}
                    },
                    {
                        "id": "step_2",
                        "name": "Run Computation",
                        "type": "computation",
                        "dependencies": ["step_1"]
                    },
                    {
                        "id": "step_3",
                        "name": "Analyze Results",
                        "type": "analysis",
                        "dependencies": ["step_2"]
                    }
                ],
                "metadata": {
                    "domain": "materials_science",
                    "job_id": job_id
                }
            }

            response = await client.post(
                f"{BASE_URL}/api/workflows/create",
                json=workflow_payload,
                timeout=TIMEOUT
            )

            if response.status_code in [200, 201]:
                result = response.json()
                workflow_id = result.get("workflow_id", result.get("id", ""))
                self.log_test("Create Workflow", True, {"workflow_id": workflow_id})
                return workflow_id
            else:
                self.log_test("Create Workflow", False, error=f"Status: {response.status_code}")
                return ""

        except Exception as e:
            self.log_test("Create Workflow", False, error=str(e))
            return ""

    async def test_execute_workflow(self, client: httpx.AsyncClient, workflow_id: str) -> bool:
        """Test 6: Ejecutar workflow"""
        try:
            if not workflow_id:
                self.log_test("Execute Workflow", False, error="No workflow ID provided")
                return False

            response = await client.post(
                f"{BASE_URL}/api/workflows/execute",
                json={"workflow_id": workflow_id, "async_mode": True},
                timeout=TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                self.log_test("Execute Workflow", True, result)
                return True
            else:
                self.log_test("Execute Workflow", False, error=f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Execute Workflow", False, error=str(e))
            return False

    async def test_biology_loop(self, client: httpx.AsyncClient) -> Dict:
        """Test 7: Biology autonomous loop"""
        try:
            response = await client.post(
                f"{BASE_URL}/api/autonomous/biology/run",
                json={"iterations": 1, "save_state": False},
                timeout=TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                self.log_test("Biology Autonomous Loop", True, result)
                return result
            else:
                self.log_test("Biology Autonomous Loop", False, error=f"Status: {response.status_code}")
                return {}

        except Exception as e:
            self.log_test("Biology Autonomous Loop", False, error=str(e))
            return {}

    async def test_mathematics_computation(self, client: httpx.AsyncClient) -> Dict:
        """Test 8: Cálculo matemático avanzado"""
        try:
            response = await client.post(
                f"{BASE_URL}/api/mathematics/calculus/derivative",
                json={
                    "expression": "x**3 + 2*x**2 - 5*x + 3",
                    "variable": "x"
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                self.log_test("Mathematics Computation", True, result)
                return result
            else:
                self.log_test("Mathematics Computation", False, error=f"Status: {response.status_code}")
                return {}

        except Exception as e:
            self.log_test("Mathematics Computation", False, error=str(e))
            return {}

    async def test_system_metrics(self, client: httpx.AsyncClient) -> Dict:
        """Test 9: Métricas del sistema"""
        try:
            response = await client.get(f"{BASE_URL}/metrics", timeout=30.0)

            if response.status_code == 200:
                result = response.json()
                self.log_test("System Metrics", True, result)
                return result
            else:
                self.log_test("System Metrics", False, error=f"Status: {response.status_code}")
                return {}

        except Exception as e:
            self.log_test("System Metrics", False, error=str(e))
            return {}

    async def run_complete_workflow(self):
        """Ejecutar el workflow completo de pruebas"""
        print("\n" + "="*80)
        print("🧪 AXIOM ATLAS - Test de Workflow Completo")
        print("="*80 + "\n")

        async with httpx.AsyncClient() as client:
            # Test 1: Health check
            if not await self.test_health_check(client):
                print("\n⚠️  Health check falló. Abortando pruebas.")
                return

            # Test 2: Generar hipótesis
            print("\n📝 Generando hipótesis científica...")
            hypothesis_data = await self.test_generate_hypothesis(client)
            hypothesis_text = hypothesis_data.get("hypothesis",
                "La conductividad térmica de grafeno varía con defectos estructurales")

            # Test 3: Evaluar plausibilidad
            print("\n🔍 Evaluando plausibilidad...")
            plausibility_score = await self.test_plausibility_evaluation(client, hypothesis_text)

            # Test 4: Agendar experimento
            print("\n📅 Agendando experimento...")
            job_id = await self.test_schedule_experiment(client, hypothesis_data)

            # Test 5: Crear workflow
            print("\n🔄 Creando workflow...")
            workflow_id = await self.test_create_workflow(client, job_id)

            # Test 6: Ejecutar workflow
            if workflow_id:
                print("\n▶️  Ejecutando workflow...")
                await self.test_execute_workflow(client, workflow_id)

            # Test 7: Biology loop (opcional)
            print("\n🧬 Probando loop autónomo de biología...")
            await self.test_biology_loop(client)

            # Test 8: Cálculo matemático
            print("\n🔢 Probando cálculo matemático...")
            await self.test_mathematics_computation(client)

            # Test 9: Métricas del sistema
            print("\n📊 Obteniendo métricas del sistema...")
            await self.test_system_metrics(client)

        # Resumen final
        self.print_summary()

        # Guardar resultados
        self.save_results()

    def print_summary(self):
        """Imprimir resumen de resultados"""
        print("\n" + "="*80)
        print("📋 RESUMEN DE PRUEBAS")
        print("="*80)

        summary = self.results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"\nTotal de pruebas: {total}")
        print(f"✅ Exitosas: {passed}")
        print(f"❌ Fallidas: {failed}")
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")

        if failed > 0:
            print("\n⚠️  Pruebas fallidas:")
            for test in self.results["tests"]:
                if not test["passed"]:
                    print(f"  - {test['name']}: {test.get('error', 'Unknown error')}")

        print("\n" + "="*80 + "\n")

    def save_results(self):
        """Guardar resultados en archivo JSON"""
        filename = f"workflow_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"./reports/{filename}"

        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"✅ Resultados guardados en: {filepath}")
        except Exception as e:
            print(f"⚠️  No se pudieron guardar los resultados: {e}")


async def main():
    tester = WorkflowTester()
    await tester.run_complete_workflow()

    # Retornar código de salida basado en resultados
    if tester.results["summary"]["failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())