"""
Test Suite for AXIOM Services Integration
========================================

Pruebas de integración completas para validar el funcionamiento
de todos los servicios AXIOM implementados.

Servicios a probar:
- Causal Discovery Service
- Federated Learning Service  
- Synthetic Data Service
- Multimodal Reasoning Service
- Quantum Algorithms Service
- Monitoring Service
"""

import pytest
import asyncio
import json
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Union
import logging

# Imports de servicios
from app.services.causal_discovery_service import CausalDiscoveryService
from app.services.federated_learning_service import FederatedLearningService
from app.services.synthetic_data_service import SyntheticDataService
from app.services.multimodal_reasoning_service import MultimodalReasoningService
from app.services.quantum_algorithms_service import QuantumAlgorithmsService
from app.services.monitoring_service import MonitoringService

# Configurar logging para tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAXIOMServicesIntegration:
    """Suite de pruebas de integración para servicios AXIOM."""
    
    @pytest.fixture(autouse=True)
    def setup_services(self):
        """Configurar servicios para pruebas."""
        self.causal_service = CausalDiscoveryService()
        self.federated_service = FederatedLearningService()
        self.synthetic_service = SyntheticDataService()
        self.multimodal_service = MultimodalReasoningService()
        self.quantum_service = QuantumAlgorithmsService()
        self.monitoring_service = MonitoringService()
        
        logger.info("Servicios AXIOM inicializados para pruebas")
    
    @pytest.mark.asyncio
    async def test_causal_discovery_service(self):
        """Prueba el servicio de descubrimiento causal."""
        logger.info("Probando Causal Discovery Service...")
        
        # Datos de prueba
        test_data = {
            "variables": ["X", "Y", "Z"],
            "data": [
                [1.0, 2.0, 3.0],
                [2.0, 4.0, 6.0],
                [3.0, 6.0, 9.0],
                [4.0, 8.0, 12.0]
            ]
        }
        
        # Test health check
        health = await self.causal_service.health_check()
        assert health["status"] == "healthy"
        assert health["service"] == "causal_discovery"
        
        # Test structure discovery
        result = await self.causal_service.discover_causal_structure(
            data=test_data,
            method="pc",
            significance_level=0.05
        )
        
        assert result["success"] is True
        assert "causal_graph" in result
        assert "edges" in result["causal_graph"]
        assert "confidence_scores" in result
        
        logger.info("✅ Causal Discovery Service: PASSED")
    
    @pytest.mark.asyncio
    async def test_federated_learning_service(self):
        """Prueba el servicio de aprendizaje federado."""
        logger.info("Probando Federated Learning Service...")
        
        # Test health check
        health = await self.federated_service.health_check()
        assert health["status"] == "healthy"
        assert health["service"] == "federated_learning"
        
        # Test session creation
        session_config = {
            "model_type": "linear_regression",
            "num_clients": 3,
            "rounds": 2,
            "strategy": "fedavg"
        }
        
        result = await self.federated_service.create_session(
            session_config=session_config
        )
        
        assert result["success"] is True
        assert "session_id" in result
        assert result["status"] == "created"
        
        # Test getting available strategies
        strategies = await self.federated_service.get_available_strategies()
        assert len(strategies) > 0
        assert "fedavg" in strategies
        
        logger.info("✅ Federated Learning Service: PASSED")
    
    @pytest.mark.asyncio
    async def test_synthetic_data_service(self):
        """Prueba el servicio de datos sintéticos."""
        logger.info("Probando Synthetic Data Service...")
        
        # Test health check
        health = await self.synthetic_service.health_check()
        assert health["status"] == "healthy"
        assert health["service"] == "synthetic_data"
        
        # Test tabular data generation
        schema = {
            "columns": {
                "age": {"type": "int", "min": 18, "max": 80},
                "income": {"type": "float", "min": 20000, "max": 100000}
            }
        }
        
        result = await self.synthetic_service.generate_tabular_data(
            data_schema=schema,
            num_samples=100,
            model_type="gaussian_copula",
            privacy_level="medium"
        )
        
        assert result["success"] is True
        assert result["num_samples"] == 100
        assert "synthetic_data" in result
        assert "column_statistics" in result
        
        # Test available models
        models = await self.synthetic_service.get_available_models()
        assert len(models) > 0
        
        logger.info("✅ Synthetic Data Service: PASSED")
    
    @pytest.mark.asyncio
    async def test_multimodal_reasoning_service(self):
        """Prueba el servicio de razonamiento multimodal."""
        logger.info("Probando Multimodal Reasoning Service...")
        
        # Test health check
        health = await self.multimodal_service.health_check()
        assert health["status"] == "healthy"
        assert health["service"] == "multimodal_reasoning"
        
        # Test document analysis
        document_data = {
            "text": "This is a test document for analysis.",
            "metadata": {"type": "research_paper", "domain": "AI"}
        }
        
        result = await self.multimodal_service.analyze_document(
            document=document_data,
            analysis_type="comprehensive",
            include_entities=True,
            include_sentiment=True
        )
        
        assert result["success"] is True
        assert "analysis_results" in result
        assert "entities" in result["analysis_results"]
        assert "sentiment" in result["analysis_results"]
        
        # Test available models
        models = await self.multimodal_service.get_available_models()
        assert len(models) > 0
        
        logger.info("✅ Multimodal Reasoning Service: PASSED")
    
    @pytest.mark.asyncio
    async def test_quantum_algorithms_service(self):
        """Prueba el servicio de algoritmos cuánticos."""
        logger.info("Probando Quantum Algorithms Service...")
        
        # Test health check
        health = await self.quantum_service.health_check()
        assert health["status"] == "healthy"
        assert health["service"] == "quantum_algorithms"
        
        # Test QAOA optimization (problema simple)
        problem_data = {
            "graph": [[0, 1], [1, 0]],
            "weights": [1.0, 1.0]
        }
        
        result = await self.quantum_service.run_qaoa(
            problem_type="max_cut",
            problem_data=problem_data,
            p_layers=1,
            optimizer="COBYLA",
            max_iterations=10,
            backend="qasm_simulator",
            shots=100
        )
        
        assert result["success"] is True
        assert "optimal_parameters" in result
        assert "optimal_value" in result
        
        # Test available backends
        backends = await self.quantum_service.get_available_backends()
        assert len(backends) > 0
        assert "qasm_simulator" in backends
        
        logger.info("✅ Quantum Algorithms Service: PASSED")
    
    @pytest.mark.asyncio
    async def test_monitoring_service(self):
        """Prueba el servicio de monitoreo."""
        logger.info("Probando Monitoring Service...")
        
        # Test health check
        health = await self.monitoring_service.health_check()
        assert health["status"] == "healthy"
        assert health["service"] == "monitoring"
        
        # Test metrics collection
        await self.monitoring_service.start_monitoring()
        
        # Esperar un momento para recopilar métricas
        await asyncio.sleep(1)
        
        metrics = await self.monitoring_service.collect_metrics()
        assert "system_metrics" in metrics
        assert "service_metrics" in metrics
        assert "timestamp" in metrics
        
        # Test stopping monitoring
        await self.monitoring_service.stop_monitoring()
        
        logger.info("✅ Monitoring Service: PASSED")
    
    @pytest.mark.asyncio
    async def test_services_integration_workflow(self):
        """Prueba un flujo de trabajo integrado usando múltiples servicios."""
        logger.info("Probando flujo de trabajo integrado...")
        
        # 1. Generar datos sintéticos
        schema = {
            "columns": {
                "feature1": {"type": "float", "min": 0, "max": 10},
                "feature2": {"type": "float", "min": 0, "max": 10},
                "target": {"type": "int", "min": 0, "max": 1}
            }
        }
        
        synthetic_result = await self.synthetic_service.generate_tabular_data(
            data_schema=schema,
            num_samples=50,
            model_type="gaussian_copula"
        )
        
        assert synthetic_result["success"] is True
        
        # 2. Usar datos sintéticos para descubrimiento causal
        synthetic_data = synthetic_result["synthetic_data"]
        
        causal_result = await self.causal_service.discover_causal_structure(
            data={
                "variables": list(schema["columns"].keys()),
                "data": synthetic_data["data"][:10]  # Usar subset para prueba
            },
            method="pc"
        )
        
        assert causal_result["success"] is True
        
        # 3. Iniciar monitoreo durante el proceso
        await self.monitoring_service.start_monitoring()
        
        # 4. Crear sesión de aprendizaje federado
        fl_result = await self.federated_service.create_session({
            "model_type": "linear_regression",
            "num_clients": 2,
            "rounds": 1
        })
        
        assert fl_result["success"] is True
        
        # 5. Recopilar métricas finales
        final_metrics = await self.monitoring_service.collect_metrics()
        assert "system_metrics" in final_metrics
        
        await self.monitoring_service.stop_monitoring()
        
        logger.info("✅ Flujo de trabajo integrado: PASSED")
    
    @pytest.mark.asyncio
    async def test_error_handling_and_resilience(self):
        """Prueba el manejo de errores y la resiliencia de los servicios."""
        logger.info("Probando manejo de errores y resiliencia...")
        
        # Test con datos inválidos en causal discovery
        invalid_data = {"variables": [], "data": []}
        
        result = await self.causal_service.discover_causal_structure(
            data=invalid_data,
            method="invalid_method"
        )
        
        assert result["success"] is False
        assert "error" in result
        
        # Test con configuración inválida en federated learning
        invalid_config = {"model_type": "invalid_model"}
        
        result = await self.federated_service.create_session(
            session_config=invalid_config
        )
        
        assert result["success"] is False
        assert "error" in result
        
        # Test con esquema inválido en synthetic data
        invalid_schema = {"columns": {}}
        
        result = await self.synthetic_service.generate_tabular_data(
            data_schema=invalid_schema,
            num_samples=10
        )
        
        assert result["success"] is False
        assert "error" in result
        
        logger.info("✅ Manejo de errores: PASSED")
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self):
        """Prueba benchmarks de rendimiento básicos."""
        logger.info("Ejecutando benchmarks de rendimiento...")
        
        start_time = datetime.now()
        
        # Benchmark: Generación de datos sintéticos
        schema = {
            "columns": {
                "x": {"type": "float", "min": 0, "max": 1},
                "y": {"type": "float", "min": 0, "max": 1}
            }
        }
        
        result = await self.synthetic_service.generate_tabular_data(
            data_schema=schema,
            num_samples=1000
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        assert result["success"] is True
        assert generation_time < 30  # Debe completarse en menos de 30 segundos
        
        logger.info(f"Generación de 1000 muestras: {generation_time:.2f}s")
        
        # Benchmark: Health checks de todos los servicios
        start_time = datetime.now()
        
        health_checks = await asyncio.gather(
            self.causal_service.health_check(),
            self.federated_service.health_check(),
            self.synthetic_service.health_check(),
            self.multimodal_service.health_check(),
            self.quantum_service.health_check(),
            self.monitoring_service.health_check()
        )
        
        health_check_time = (datetime.now() - start_time).total_seconds()
        
        assert all(h["status"] == "healthy" for h in health_checks)
        assert health_check_time < 5  # Todos los health checks en menos de 5 segundos
        
        logger.info(f"Health checks de 6 servicios: {health_check_time:.2f}s")
        logger.info("✅ Benchmarks de rendimiento: PASSED")


# Funciones de utilidad para pruebas
def generate_test_data(size: int = 100) -> Dict[str, Any]:
    """Genera datos de prueba sintéticos."""
    np.random.seed(42)
    return {
        "variables": ["X", "Y", "Z"],
        "data": np.random.randn(size, 3).tolist()
    }


def validate_service_response(response: Dict[str, Any], required_fields: List[str]) -> bool:
    """Valida que una respuesta de servicio tenga los campos requeridos."""
    return all(field in response for field in required_fields)


# Configuración de pytest
@pytest.fixture(scope="session")
def event_loop():
    """Crear event loop para pruebas async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Ejecutar pruebas directamente
    pytest.main([__file__, "-v", "--tb=short"])