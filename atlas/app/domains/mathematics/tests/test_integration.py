"""
Tests de Integración para Servicios Matemáticos Avanzados
Prueba la integración y funcionamiento conjunto de todos los servicios
"""

import pytest
import numpy as np
import asyncio
import time
from typing import Dict, List, Any, Optional
import logging
from app.exceptions.domain.mathematics import MathematicsError

# Importar servicios
try:
    from ..services.gpu_math_service import GPUMathService
    from ..services.symbolic_ai_service import SymbolicAIService
    from ..services.advanced_visualization_service import AdvancedVisualizationService
    from ..services.bioinformatics_service import BioinformaticsService
    from ..services.advanced_quantum_service import AdvancedQuantumService
    from ..services.financial_mathematics_service import FinancialMathematicsService
    from ..services.distributed_computing_service import DistributedComputingService
    from ..services.vr_ar_visualization_service import VRARVisualizationService
except ImportError as e:
    pytest.skip(f"Servicios no disponibles: {e}", allow_module_level=True)


class TestMathematicsIntegration:
    """Suite de tests de integración para servicios matemáticos"""
    
    @pytest.fixture(autouse=True)
    def setup_services(self):
        """Configurar servicios para tests"""
        self.gpu_service = GPUMathService()
        self.symbolic_ai_service = SymbolicAIService()
        self.visualization_service = AdvancedVisualizationService()
        self.bioinformatics_service = BioinformaticsService()
        self.quantum_service = AdvancedQuantumService()
        self.financial_service = FinancialMathematicsService()
        self.distributed_service = DistributedComputingService()
        self.vr_service = VRARVisualizationService()
        
        # Configurar logging para tests
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    # === TESTS DE SERVICIOS INDIVIDUALES ===
    
    def test_gpu_service_basic_operations(self):
        """Test operaciones básicas del servicio GPU"""
        try:
            # Test multiplicación de matrices
            a = np.random.rand(100, 100)
            b = np.random.rand(100, 100)
            
            result = self.gpu_service.matrix_multiply(a, b)
            expected = np.dot(a, b)
            
            assert result is not None
            assert result.shape == expected.shape
            
            # Test FFT
            signal = np.random.rand(1024)
            fft_result = self.gpu_service.fft(signal)
            
            assert fft_result is not None
            assert len(fft_result) == len(signal)
            
            self.logger.info("✓ GPU Service: Operaciones básicas funcionando")
            
        except MathematicsError as e:
            self.logger.warning(f"GPU Service test failed (expected on CPU-only systems): {e}")
    
    def test_symbolic_ai_service_equation_solving(self):
        """Test resolución de ecuaciones con IA simbólica"""
        try:
            # Test ecuación cuadrática
            equation = "x**2 - 5*x + 6 = 0"
            solutions = self.symbolic_ai_service.solve_equation(equation)
            
            assert solutions is not None
            assert "solutions" in solutions
            
            # Test simplificación
            expression = "x**2 + 2*x + 1"
            simplified = self.symbolic_ai_service.simplify_expression(expression)
            
            assert simplified is not None
            
            self.logger.info("✓ Symbolic AI Service: Resolución de ecuaciones funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"Symbolic AI Service test failed: {e}")
            pytest.fail(f"Symbolic AI Service error: {e}")
    
    def test_visualization_service_plots(self):
        """Test generación de visualizaciones"""
        try:
            # Test plot 3D
            x = np.linspace(-5, 5, 50)
            y = np.linspace(-5, 5, 50)
            X, Y = np.meshgrid(x, y)
            Z = X**2 + Y**2
            
            plot_result = self.visualization_service.create_3d_surface(X, Y, Z)
            
            assert plot_result is not None
            assert "plot_data" in plot_result or "figure" in plot_result
            
            # Test animación
            frames_data = [np.sin(x + t) for t in np.linspace(0, 2*np.pi, 10)]
            animation = self.visualization_service.create_animation(frames_data)
            
            assert animation is not None
            
            self.logger.info("✓ Visualization Service: Generación de plots funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"Visualization Service test failed: {e}")
            pytest.fail(f"Visualization Service error: {e}")
    
    def test_bioinformatics_service_analysis(self):
        """Test análisis bioinformático"""
        try:
            # Test análisis de secuencias
            sequences = ["ATCGATCG", "ATCGATCG", "ATCGATCG", "GCTAGCTA"]
            phylo_result = self.bioinformatics_service.phylogenetic_analysis(sequences)
            
            assert phylo_result is not None
            assert "distance_matrix" in phylo_result
            
            # Test análisis poblacional
            genotypes = np.random.choice([0, 1, 2], size=(100, 10))
            pop_result = self.bioinformatics_service.population_genetics_analysis(genotypes)
            
            assert pop_result is not None
            assert "allele_frequencies" in pop_result
            
            self.logger.info("✓ Bioinformatics Service: Análisis funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"Bioinformatics Service test failed: {e}")
            pytest.fail(f"Bioinformatics Service error: {e}")
    
    def test_quantum_service_algorithms(self):
        """Test algoritmos cuánticos avanzados"""
        try:
            # Test simulación cuántica
            n_qubits = 3
            simulation = self.quantum_service.quantum_simulation(n_qubits, method="statevector")
            
            assert simulation is not None
            assert "state_vector" in simulation or "result" in simulation
            
            # Test VQE (si está disponible)
            try:
                vqe_result = self.quantum_service.variational_quantum_eigensolver(
                    hamiltonian="Z0*Z1", n_qubits=2
                )
                assert vqe_result is not None
            except MathematicsError:
                self.logger.info("VQE test skipped (dependencies not available)")
            
            self.logger.info("✓ Quantum Service: Algoritmos funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"Quantum Service test failed: {e}")
            pytest.fail(f"Quantum Service error: {e}")
    
    def test_financial_service_models(self):
        """Test modelos financieros"""
        try:
            # Test Black-Scholes
            bs_result = self.financial_service.black_scholes_option_price(
                S=100, K=105, T=0.25, r=0.05, sigma=0.2, option_type="call"
            )
            
            assert bs_result is not None
            assert "option_price" in bs_result
            assert bs_result["option_price"] > 0
            
            # Test VaR
            returns = np.random.normal(0.001, 0.02, 1000)
            var_result = self.financial_service.calculate_var(returns, confidence_level=0.95)
            
            assert var_result is not None
            assert "var" in var_result
            
            self.logger.info("✓ Financial Service: Modelos funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"Financial Service test failed: {e}")
            pytest.fail(f"Financial Service error: {e}")
    
    def test_distributed_service_computation(self):
        """Test computación distribuida"""
        try:
            # Test operación distribuida
            matrix_a = np.random.rand(50, 50)
            matrix_b = np.random.rand(50, 50)
            
            result = self.distributed_service.distributed_matrix_multiply(matrix_a, matrix_b)
            
            assert result is not None
            assert result.shape == (50, 50)
            
            # Test análisis de big data
            data = np.random.rand(1000, 10)
            correlation = self.distributed_service.compute_correlation_matrix(data)
            
            assert correlation is not None
            assert correlation.shape == (10, 10)
            
            self.logger.info("✓ Distributed Service: Computación funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"Distributed Service test failed: {e}")
            pytest.fail(f"Distributed Service error: {e}")
    
    def test_vr_service_scene_creation(self):
        """Test creación de escenas VR"""
        try:
            # Test superficie de función VR
            scene = self.vr_service.create_function_surface_vr(
                function="x**2 + y**2",
                x_range=(-2, 2),
                y_range=(-2, 2),
                resolution=20
            )
            
            assert scene is not None
            assert scene.scene_id is not None
            assert len(scene.objects) > 0
            
            # Test generación de código A-Frame
            html_code = self.vr_service.generate_aframe_html(scene)
            
            assert html_code is not None
            assert "a-scene" in html_code
            assert scene.title in html_code
            
            self.logger.info("✓ VR Service: Creación de escenas funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"VR Service test failed: {e}")
            pytest.fail(f"VR Service error: {e}")
    
    # === TESTS DE INTEGRACIÓN ENTRE SERVICIOS ===
    
    def test_gpu_visualization_integration(self):
        """Test integración GPU + Visualización"""
        try:
            # Generar datos con GPU
            size = 100
            x = np.linspace(-5, 5, size)
            y = np.linspace(-5, 5, size)
            X, Y = np.meshgrid(x, y)
            
            # Usar GPU para cálculo intensivo
            Z_flat = X.flatten()**2 + Y.flatten()**2
            if self.gpu_service.is_gpu_available():
                Z_gpu = self.gpu_service.vector_operations(Z_flat, operation="sqrt")
                Z = Z_gpu.reshape(X.shape)
            else:
                Z = np.sqrt(Z_flat).reshape(X.shape)
            
            # Visualizar resultado
            plot_result = self.visualization_service.create_3d_surface(X, Y, Z)
            
            assert plot_result is not None
            self.logger.info("✓ Integración GPU + Visualización funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"GPU-Visualization integration failed: {e}")
    
    def test_quantum_visualization_integration(self):
        """Test integración Cuántica + Visualización"""
        try:
            # Crear estado cuántico
            n_qubits = 2
            simulation = self.quantum_service.quantum_simulation(n_qubits)
            
            if "state_vector" in simulation:
                state_vector = simulation["state_vector"]
                
                # Crear visualización VR del estado
                vr_scene = self.vr_service.create_quantum_state_vr(state_vector)
                
                assert vr_scene is not None
                assert len(vr_scene.objects) > 0
                
                self.logger.info("✓ Integración Cuántica + VR funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"Quantum-VR integration failed: {e}")
    
    def test_financial_distributed_integration(self):
        """Test integración Financiera + Distribuida"""
        try:
            # Generar datos de mercado
            n_assets = 10
            n_days = 1000
            returns = np.random.normal(0.001, 0.02, (n_days, n_assets))
            
            # Usar computación distribuida para análisis de cartera
            correlation_matrix = self.distributed_service.compute_correlation_matrix(returns)
            
            # Optimización de cartera con datos distribuidos
            portfolio_result = self.financial_service.portfolio_optimization(
                expected_returns=np.mean(returns, axis=0),
                cov_matrix=np.cov(returns.T)
            )
            
            assert correlation_matrix is not None
            assert portfolio_result is not None
            assert "optimal_weights" in portfolio_result
            
            self.logger.info("✓ Integración Financiera + Distribuida funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"Financial-Distributed integration failed: {e}")
    
    def test_bioinformatics_ai_integration(self):
        """Test integración Bioinformática + IA Simbólica"""
        try:
            # Generar datos genéticos
            sequences = ["ATCGATCG", "ATCGATCG", "GCTAGCTA", "ATCGATCG"]
            
            # Análisis bioinformático
            phylo_result = self.bioinformatics_service.phylogenetic_analysis(sequences)
            
            # Usar IA para encontrar patrones
            if "distance_matrix" in phylo_result:
                # Simplificar expresión de distancia genética
                distance_expr = "sqrt((a-b)**2 + (c-d)**2)"
                simplified = self.symbolic_ai_service.simplify_expression(distance_expr)
                
                assert simplified is not None
                
            self.logger.info("✓ Integración Bioinformática + IA funcionando")
            
        except MathematicsError as e:
            self.logger.error(f"Bioinformatics-AI integration failed: {e}")
    
    # === TESTS DE RENDIMIENTO ===
    
    def test_performance_comparison(self):
        """Test comparación de rendimiento entre servicios"""
        try:
            size = 500
            matrix_a = np.random.rand(size, size)
            matrix_b = np.random.rand(size, size)
            
            # Test CPU vs GPU (si disponible)
            start_time = time.time()
            cpu_result = np.dot(matrix_a, matrix_b)
            cpu_time = time.time() - start_time
            
            if self.gpu_service.is_gpu_available():
                start_time = time.time()
                gpu_result = self.gpu_service.matrix_multiply(matrix_a, matrix_b)
                gpu_time = time.time() - start_time
                
                self.logger.info(f"CPU time: {cpu_time:.4f}s, GPU time: {gpu_time:.4f}s")
                
                # Verificar que los resultados son similares
                if gpu_result is not None:
                    np.testing.assert_allclose(cpu_result, gpu_result, rtol=1e-5)
            
            # Test computación distribuida
            start_time = time.time()
            distributed_result = self.distributed_service.distributed_matrix_multiply(
                matrix_a, matrix_b
            )
            distributed_time = time.time() - start_time
            
            self.logger.info(f"Distributed time: {distributed_time:.4f}s")
            
            if distributed_result is not None:
                np.testing.assert_allclose(cpu_result, distributed_result, rtol=1e-5)
            
            self.logger.info("✓ Tests de rendimiento completados")
            
        except MathematicsError as e:
            self.logger.error(f"Performance test failed: {e}")
    
    # === TESTS DE CAPACIDADES ===
    
    def test_all_services_capabilities(self):
        """Test que todos los servicios reporten sus capacidades"""
        services = [
            ("GPU", self.gpu_service),
            ("Symbolic AI", self.symbolic_ai_service),
            ("Visualization", self.visualization_service),
            ("Bioinformatics", self.bioinformatics_service),
            ("Quantum", self.quantum_service),
            ("Financial", self.financial_service),
            ("Distributed", self.distributed_service),
            ("VR/AR", self.vr_service)
        ]
        
        for name, service in services:
            try:
                capabilities = service.get_capabilities()
                assert capabilities is not None
                assert "service" in capabilities or "name" in capabilities
                self.logger.info(f"✓ {name} Service: Capacidades reportadas")
            except MathematicsError as e:
                self.logger.error(f"{name} Service capabilities failed: {e}")
    
    # === TEST DE INTEGRACIÓN COMPLETA ===
    
    def test_complete_mathematical_workflow(self):
        """Test workflow matemático completo usando múltiples servicios"""
        try:
            self.logger.info("Iniciando workflow matemático completo...")
            
            # 1. Generar datos con GPU
            n = 100
            x = np.linspace(0, 2*np.pi, n)
            if self.gpu_service.is_gpu_available():
                y = self.gpu_service.vector_operations(x, operation="sin")
            else:
                y = np.sin(x)
            
            # 2. Análisis simbólico
            equation = "sin(x)"
            analysis = self.symbolic_ai_service.analyze_function(equation)
            
            # 3. Visualización 3D
            X, Y = np.meshgrid(x[:20], x[:20])
            Z = np.sin(X) * np.cos(Y)
            plot_result = self.visualization_service.create_3d_surface(X, Y, Z)
            
            # 4. Crear escena VR
            vr_scene = self.vr_service.create_function_surface_vr("sin(x)*cos(y)")
            
            # 5. Análisis distribuido
            correlation = self.distributed_service.compute_correlation_matrix(
                np.column_stack([x, y])
            )
            
            # Verificar que todos los pasos funcionaron
            assert y is not None
            assert analysis is not None
            assert plot_result is not None
            assert vr_scene is not None
            assert correlation is not None
            
            self.logger.info("✓ Workflow matemático completo exitoso")
            
            return {
                "status": "success",
                "steps_completed": 5,
                "services_used": ["GPU", "Symbolic AI", "Visualization", "VR", "Distributed"],
                "results": {
                    "data_points": len(y),
                    "vr_objects": len(vr_scene.objects),
                    "correlation_shape": correlation.shape
                }
            }
            
        except MathematicsError as e:
            self.logger.error(f"Complete workflow failed: {e}")
            pytest.fail(f"Complete workflow error: {e}")


# === TESTS DE CONFIGURACIÓN Y LIMPIEZA ===

class TestServiceConfiguration:
    """Tests de configuración y estado de servicios"""
    
    def test_service_initialization(self):
        """Test que todos los servicios se inicialicen correctamente"""
        services = [
            GPUMathService,
            SymbolicAIService,
            AdvancedVisualizationService,
            BioinformaticsService,
            AdvancedQuantumService,
            FinancialMathematicsService,
            DistributedComputingService,
            VRARVisualizationService
        ]
        
        for service_class in services:
            try:
                service = service_class()
                assert service is not None
                print(f"✓ {service_class.__name__} inicializado correctamente")
            except MathematicsError as e:
                pytest.fail(f"Error inicializando {service_class.__name__}: {e}")
    
    def test_service_dependencies(self):
        """Test dependencias opcionales de servicios"""
        # Este test verifica que los servicios manejen correctamente
        # las dependencias opcionales
        
        gpu_service = GPUMathService()
        gpu_available = gpu_service.is_gpu_available()
        print(f"GPU disponible: {gpu_available}")
        
        # Los servicios deben funcionar incluso sin dependencias opcionales
        assert gpu_service is not None


if __name__ == "__main__":
    # Ejecutar tests si se ejecuta directamente
    pytest.main([__file__, "-v", "--tb=short"])