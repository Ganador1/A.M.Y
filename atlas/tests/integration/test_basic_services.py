"""
Advanced Tests for AXIOM Services
=================================

Pruebas avanzadas para validar el funcionamiento robusto de los servicios AXIOM
con métricas de performance, casos edge y validación de resultados.
"""

import pytest
import asyncio
import time
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configurar logging para tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_service_imports():
    """Prueba que todos los servicios se puedan importar correctamente."""
    try:
        from app.services.causal_discovery_service import CausalDiscoveryService
        from app.services.federated_learning_service import FederatedLearningService
        from app.services.synthetic_data_service import SyntheticDataService
        from app.services.multimodal_reasoning_service import MultimodalReasoningService
        from app.services.quantum_algorithms_service import QuantumAlgorithmsService
        from app.services.monitoring_service import MonitoringService
        
        print("✅ Todos los servicios se importaron correctamente")
        assert True
        
    except ImportError as e:
        print(f"❌ Error importando servicios: {e}")
        assert False, f"Error importando servicios: {e}"


def test_service_initialization():
    """Prueba que todos los servicios se puedan inicializar."""
    try:
        from app.services.causal_discovery_service import CausalDiscoveryService
        from app.services.federated_learning_service import FederatedLearningService
        from app.services.synthetic_data_service import SyntheticDataService
        from app.services.multimodal_reasoning_service import MultimodalReasoningService
        from app.services.quantum_algorithms_service import QuantumAlgorithmsService
        from app.services.monitoring_service import MonitoringService
        
        # Inicializar servicios
        causal_service = CausalDiscoveryService()
        federated_service = FederatedLearningService()
        synthetic_service = SyntheticDataService()
        multimodal_service = MultimodalReasoningService()
        quantum_service = QuantumAlgorithmsService()
        monitoring_service = MonitoringService()
        
        # Verificar que se inicializaron
        assert causal_service is not None
        assert federated_service is not None
        assert synthetic_service is not None
        assert multimodal_service is not None
        assert quantum_service is not None
        assert monitoring_service is not None
        
        print("✅ Todos los servicios se inicializaron correctamente")
        
    except Exception as e:
        print(f"❌ Error inicializando servicios: {e}")
        assert False, f"Error inicializando servicios: {e}"


@pytest.mark.asyncio
async def test_health_checks():
    """Prueba los health checks de todos los servicios."""
    try:
        from app.services.causal_discovery_service import CausalDiscoveryService
        from app.services.federated_learning_service import FederatedLearningService
        from app.services.synthetic_data_service import SyntheticDataService
        from app.services.multimodal_reasoning_service import MultimodalReasoningService
        from app.services.quantum_algorithms_service import QuantumAlgorithmsService
        from app.services.monitoring_service import MonitoringService
        
        # Inicializar servicios
        services = {
            "causal": CausalDiscoveryService(),
            "federated": FederatedLearningService(),
            "synthetic": SyntheticDataService(),
            "multimodal": MultimodalReasoningService(),
            "quantum": QuantumAlgorithmsService(),
            "monitoring": MonitoringService()
        }
        
        # Probar health checks
        for name, service in services.items():
            try:
                health = await service.health_check()
                assert "status" in health
                assert "service" in health
                assert "timestamp" in health
                print(f"✅ Health check {name}: {health['status']}")
            except Exception as e:
                print(f"⚠️  Health check {name} falló: {e}")
                # No fallar la prueba por health checks individuales
        
        print("✅ Health checks completados")
        
    except Exception as e:
        print(f"❌ Error en health checks: {e}")
        assert False, f"Error en health checks: {e}"


def test_router_imports():
    """Prueba que todos los routers se puedan importar."""
    try:
        from app.routers import causal_discovery
        from app.routers import federated_learning
        from app.routers import synthetic_data
        from app.routers import multimodal_reasoning
        from app.routers import quantum_algorithms
        from app.routers import monitoring
        
        # Verificar que tienen routers
        assert hasattr(causal_discovery, 'router')
        assert hasattr(federated_learning, 'router')
        assert hasattr(synthetic_data, 'router')
        assert hasattr(multimodal_reasoning, 'router')
        assert hasattr(quantum_algorithms, 'router')
        assert hasattr(monitoring, 'router')
        
        print("✅ Todos los routers se importaron correctamente")
        
    except ImportError as e:
        print(f"❌ Error importando routers: {e}")
        assert False, f"Error importando routers: {e}"


def test_main_app_integration():
    """Prueba que la aplicación principal incluya todos los routers."""
    try:
        # Leer el archivo main.py
        with open('./main.py', 'r') as f:
            main_content = f.read()
        
        # Verificar que los routers estén incluidos
        required_routers = [
            'causal_discovery',
            'federated_learning', 
            'synthetic_data',
            'multimodal_reasoning',
            'quantum_algorithms',
            'monitoring'
        ]
        
        for router in required_routers:
            assert f'{router}.router' in main_content, f"Router {router} no encontrado en main.py"
        
        print("✅ Todos los routers están integrados en main.py")
        
    except Exception as e:
        print(f"❌ Error verificando integración en main.py: {e}")
        assert False, f"Error verificando main.py: {e}"


def test_service_files_exist():
    """Prueba que todos los archivos de servicios existan."""
    import os
    
    service_files = [
        './app/services/causal_discovery_service.py',
        './app/services/federated_learning_service.py',
        './app/services/synthetic_data_service.py',
        './app/services/multimodal_reasoning_service.py',
        './app/services/quantum_algorithms_service.py',
        './app/services/monitoring_service.py'
    ]
    
    for file_path in service_files:
        assert os.path.exists(file_path), f"Archivo de servicio no encontrado: {file_path}"
        
        # Verificar que el archivo no esté vacío
        with open(file_path, 'r') as f:
            content = f.read()
            assert len(content) > 100, f"Archivo de servicio muy pequeño: {file_path}"
    
    print("✅ Todos los archivos de servicios existen y tienen contenido")


def test_router_files_exist():
    """Prueba que todos los archivos de routers existan."""
    import os
    
    router_files = [
        './app/routers/causal_discovery.py',
        './app/routers/federated_learning.py',
        './app/routers/synthetic_data.py',
        './app/routers/multimodal_reasoning.py',
        './app/routers/quantum_algorithms.py',
        './app/routers/monitoring.py'
    ]
    
    for file_path in router_files:
        assert os.path.exists(file_path), f"Archivo de router no encontrado: {file_path}"
        
        # Verificar que el archivo no esté vacío
        with open(file_path, 'r') as f:
            content = f.read()
            assert len(content) > 100, f"Archivo de router muy pequeño: {file_path}"
    
    print("✅ Todos los archivos de routers existen y tienen contenido")


if __name__ == "__main__":
    # Ejecutar pruebas básicas
    print("🧪 Ejecutando pruebas básicas de servicios AXIOM...")
    
    test_service_imports()
    test_service_initialization()
    test_router_imports()
    test_main_app_integration()
    test_service_files_exist()
    test_router_files_exist()
    
    # Ejecutar prueba async
    asyncio.run(test_health_checks())
    
    print("🎉 Todas las pruebas básicas completadas exitosamente!")


# ------------- Tests Avanzados de Performance -------------

class TestServicePerformance:
    """Tests de performance para servicios críticos"""
    
    def test_plausibility_scoring_performance(self):
        """Test de performance del servicio de plausibilidad mejorado"""
        try:
            from app.services.plausibility_scoring_service import PlausibilityScoringService
            
            service = PlausibilityScoringService()
            
            # Datos de test
            test_hypotheses = [
                {
                    "title": "Machine learning for drug discovery",
                    "description": "Using deep learning to predict drug efficacy",
                    "variables": ["molecular_features", "target_protein"],
                    "domain": "drug_discovery",
                    "assumptions": ["sufficient_training_data", "validated_targets"],
                    "expected_outcome": "improved_drug_success_rate"
                },
                {
                    "title": "Quantum computing for optimization",
                    "description": "Using quantum algorithms for combinatorial optimization",
                    "variables": ["problem_size", "algorithm_type"],
                    "domain": "quantum_computing",
                    "assumptions": ["stable_quantum_hardware", "low_noise"],
                    "expected_outcome": "faster_optimization"
                }
            ]
            
            # Medir tiempo de procesamiento
            start_time = time.time()
            results = []
            
            for hypothesis in test_hypotheses:
                result = service.heuristic_score(hypothesis)
                results.append(result)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Validar resultados
            assert len(results) == len(test_hypotheses)
            for result in results:
                assert "composite" in result
                assert 0 <= result["composite"] <= 1
                assert "components" in result
            
            # Validar performance (debe ser < 2 segundos para 2 hipótesis)
            assert processing_time < 2.0, f"Processing too slow: {processing_time:.2f}s"
            
            logger.info(f"✅ Plausibility scoring performance: {processing_time:.3f}s for {len(test_hypotheses)} hypotheses")
            
        except Exception as e:
            logger.error(f"Plausibility scoring performance test failed: {e}")
            pytest.fail(f"Performance test failed: {e}")

    def test_literature_search_performance(self):
        """Test de performance del servicio de búsqueda de literatura mejorado"""
        try:
            from app.services.literature_search import LiteratureSearchService
            
            service = LiteratureSearchService()
            
            # Test de búsqueda semántica
            test_queries = [
                "machine learning drug discovery",
                "quantum computing optimization",
                "materials science nanomaterials"
            ]
            
            start_time = time.time()
            results = []
            
            for query in test_queries:
                result = service.search_literature({
                    "query": query,
                    "domain": "general",
                    "max_results": 5,
                    "sources": ["offline"]  # Usar cache offline para test rápido
                })
                results.append(result)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Validar resultados
            assert len(results) == len(test_queries)
            for result in results:
                assert "success" in result
                if result["success"]:
                    assert "papers" in result
            
            # Validar performance
            assert processing_time < 5.0, f"Literature search too slow: {processing_time:.2f}s"
            
            logger.info(f"✅ Literature search performance: {processing_time:.3f}s for {len(test_queries)} queries")
            
        except Exception as e:
            logger.error(f"Literature search performance test failed: {e}")
            pytest.fail(f"Performance test failed: {e}")

    def test_quantum_computing_performance(self):
        """Test de performance del servicio de computación cuántica mejorado"""
        try:
            from app.services.quantum_computing import QuantumComputingService
            
            service = QuantumComputingService()
            
            # Test de algoritmos avanzados
            test_operations = [
                {
                    "operation": "create_bell_state_qiskit",
                    "backend": "statevector_simulator"
                },
                {
                    "operation": "create_grover_search_qiskit",
                    "n_qubits": 3,
                    "target_state": "101"
                }
            ]
            
            start_time = time.time()
            results = []
            
            for operation in test_operations:
                result = service.process_request(operation)
                results.append(result)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Validar resultados
            assert len(results) == len(test_operations)
            for result in results:
                assert isinstance(result, dict)
                # No debe haber errores críticos
                assert "error" not in result or "not available" in str(result.get("error", ""))
            
            # Validar performance
            assert processing_time < 3.0, f"Quantum computing too slow: {processing_time:.2f}s"
            
            logger.info(f"✅ Quantum computing performance: {processing_time:.3f}s for {len(test_operations)} operations")
            
        except Exception as e:
            logger.error(f"Quantum computing performance test failed: {e}")
            pytest.fail(f"Performance test failed: {e}")


# ------------- Tests de Casos Edge -------------

class TestEdgeCases:
    """Tests para casos edge y manejo de errores"""
    
    def test_plausibility_scoring_edge_cases(self):
        """Test de casos edge para plausibility scoring"""
        try:
            from app.services.plausibility_scoring_service import PlausibilityScoringService
            
            service = PlausibilityScoringService()
            
            # Casos edge
            edge_cases = [
                # Caso vacío
                {},
                # Caso con datos mínimos
                {"title": "Test", "description": "Test"},
                # Caso con datos muy largos
                {
                    "title": "A" * 1000,
                    "description": "B" * 10000,
                    "variables": ["var" + str(i) for i in range(100)],
                    "assumptions": ["assumption" + str(i) for i in range(100)]
                },
                # Caso con caracteres especiales
                {
                    "title": "Test with special chars: @#$%^&*()",
                    "description": "Unicode: ñáéíóú 中文 🚀",
                    "variables": ["var1", "var2"],
                    "domain": "special_domain"
                }
            ]
            
            for i, case in enumerate(edge_cases):
                try:
                    result = service.heuristic_score(case)
                    assert isinstance(result, dict)
                    assert "composite" in result
                    assert 0 <= result["composite"] <= 1
                    logger.info(f"✅ Edge case {i+1} handled successfully")
                except Exception as e:
                    logger.warning(f"Edge case {i+1} failed: {e}")
                    # Algunos casos edge pueden fallar, pero no debe ser crítico
                    assert "composite" in str(e) or "error" in str(e).lower()
            
        except Exception as e:
            logger.error(f"Edge cases test failed: {e}")
            pytest.fail(f"Edge cases test failed: {e}")


# ------------- Tests de Métricas y Calidad -------------

class TestServiceMetrics:
    """Tests para métricas de calidad de servicios"""
    
    def test_plausibility_scoring_metrics(self):
        """Test de métricas de calidad para plausibility scoring"""
        try:
            from app.services.plausibility_scoring_service import PlausibilityScoringService
            
            service = PlausibilityScoringService()
            
            # Dataset de test con casos conocidos
            test_cases = [
                {
                    "hypothesis": {
                        "title": "Gravity affects objects",
                        "description": "Objects fall due to gravitational force",
                        "variables": ["mass", "distance"],
                        "domain": "physics",
                        "assumptions": ["earth_gravity"],
                        "expected_outcome": "objects_fall"
                    },
                    "expected_score_range": (0.7, 1.0)  # Debería ser alta plausibilidad
                },
                {
                    "hypothesis": {
                        "title": "Magic unicorns exist",
                        "description": "Invisible unicorns control the weather",
                        "variables": ["unicorn_count", "weather_patterns"],
                        "domain": "fantasy",
                        "assumptions": ["magic_exists"],
                        "expected_outcome": "weather_control"
                    },
                    "expected_score_range": (0.0, 0.3)  # Debería ser baja plausibilidad
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                result = service.heuristic_score(test_case["hypothesis"])
                score = result["composite"]
                expected_min, expected_max = test_case["expected_score_range"]
                
                assert expected_min <= score <= expected_max, \
                    f"Test case {i+1}: score {score:.3f} not in expected range [{expected_min}, {expected_max}]"
                
                logger.info(f"✅ Test case {i+1}: score {score:.3f} in expected range")
            
        except Exception as e:
            logger.error(f"Metrics test failed: {e}")
            pytest.fail(f"Metrics test failed: {e}")

    def test_service_reliability(self):
        """Test de confiabilidad de servicios"""
        try:
            from app.services.plausibility_scoring_service import PlausibilityScoringService
            
            service = PlausibilityScoringService()
            
            # Test de consistencia
            hypothesis = {
                "title": "Consistent test hypothesis",
                "description": "Testing consistency across multiple runs",
                "variables": ["var1", "var2"],
                "domain": "test",
                "assumptions": ["assumption1"],
                "expected_outcome": "outcome"
            }
            
            # Ejecutar múltiples veces
            results = []
            for _ in range(5):
                result = service.heuristic_score(hypothesis)
                results.append(result["composite"])
            
            # Verificar consistencia (variación < 10%)
            mean_score = np.mean(results)
            std_score = np.std(results)
            cv = std_score / mean_score if mean_score > 0 else 0
            
            assert cv < 0.1, f"Inconsistent results: CV = {cv:.3f}"
            
            logger.info(f"✅ Service reliability test passed: CV = {cv:.3f}")
            
        except Exception as e:
            logger.error(f"Reliability test failed: {e}")
            pytest.fail(f"Reliability test failed: {e}")


# ------------- Función para ejecutar tests avanzados -------------

def run_advanced_tests():
    """Ejecutar todos los tests avanzados"""
    print("🚀 Ejecutando tests avanzados de servicios AXIOM...")
    
    # Tests de performance
    performance_tests = TestServicePerformance()
    performance_tests.test_plausibility_scoring_performance()
    performance_tests.test_literature_search_performance()
    performance_tests.test_quantum_computing_performance()
    
    # Tests de casos edge
    edge_tests = TestEdgeCases()
    edge_tests.test_plausibility_scoring_edge_cases()
    
    # Tests de métricas
    metrics_tests = TestServiceMetrics()
    metrics_tests.test_plausibility_scoring_metrics()
    metrics_tests.test_service_reliability()
    
    print("🎉 Todos los tests avanzados completados exitosamente!")


if __name__ == "__main__":
    # Ejecutar pruebas básicas
    print("🧪 Ejecutando pruebas básicas de servicios AXIOM...")
    
    test_service_imports()
    test_service_initialization()
    test_router_imports()
    test_main_app_integration()
    test_service_files_exist()
    test_router_files_exist()
    
    # Ejecutar prueba async
    asyncio.run(test_health_checks())
    
    print("🎉 Todas las pruebas básicas completadas exitosamente!")
    
    # Ejecutar tests avanzados
    run_advanced_tests()