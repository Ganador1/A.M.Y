"""
Unit tests for Quantum Loop Advanced Services Integration

Tests the integration of:
- QuantumAlgorithmsService (quantum advantage analysis)
- PhysicsInformedNNService (PINN simulations)
- QuantumChemistryService (molecular calculations)
"""

import pytest
import asyncio
from unittest.mock import AsyncMock
from app.autonomous.pipelines.quantum_loop import QuantumLoop


class TestQuantumLoopAdvancedServicesInitialization:
    """Test advanced quantum services initialization"""

    @pytest.fixture
    def quantum_loop(self):
        """Create QuantumLoop instance for testing"""
        return QuantumLoop()

    def test_all_quantum_services_initialized(self, quantum_loop):
        """Test that all 3 advanced quantum services are initialized"""
        assert hasattr(quantum_loop, 'quantum_algorithms_service')
        assert hasattr(quantum_loop, 'physics_informed_nn_service')
        assert hasattr(quantum_loop, 'quantum_chemistry_service')
        
        assert quantum_loop.quantum_algorithms_service is not None
        assert quantum_loop.physics_informed_nn_service is not None
        assert quantum_loop.quantum_chemistry_service is not None


class TestQuantumAdvantageAnalysis:
    """Test QuantumAlgorithmsService quantum advantage analysis"""

    @pytest.fixture
    def quantum_loop(self):
        return QuantumLoop()

    @pytest.fixture
    def mock_candidate(self):
        """Mock quantum circuit candidate"""
        return {
            "id": "q_circuit_001",
            "algorithm": "vqe",
            "n_qubits": 3,
            "depth": 2,
            "parameters": {"problem_size": 4, "layers": 2}
        }

    @pytest.fixture
    def mock_quantum_advantage_result(self):
        """Mock quantum advantage analysis result"""
        return {
            "problem_size": 3,
            "quantum_speedup_factor": 2.5,
            "classical_complexity": "O(2^n)",
            "quantum_complexity": "O(n^3)",
            "advantage_threshold": 50,
            "current_advantage": "moderate",
            "scalability_score": 0.75
        }

    @pytest.mark.asyncio
    async def test_quantum_advantage_analysis(self, quantum_loop, mock_candidate, mock_quantum_advantage_result):
        """Test quantum advantage analysis integration"""
        # Mock quantum algorithms service
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            return_value=mock_quantum_advantage_result
        )
        
        # Mock other services
        quantum_loop.physics_informed_nn_service.solve_pde_pytorch = AsyncMock(
            return_value={"method": "pytorch_pinn", "final_loss": 0.01}
        )
        quantum_loop.quantum_chemistry_service.molecular_energy_calculation = AsyncMock(
            return_value={"energy": -1.15}
        )

        # Call evaluation
        evaluation = await quantum_loop._evaluate_candidate_async(mock_candidate)

        # Verify quantum advantage was called
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage.assert_called_once()
        
        # Check call arguments
        call_args = quantum_loop.quantum_algorithms_service.analyze_quantum_advantage.call_args
        assert call_args.args[0] == mock_candidate["n_qubits"]

        # Verify evaluation structure
        assert "advanced_analysis" in evaluation
        assert "quantum_advantage" in evaluation["advanced_analysis"]

    @pytest.mark.asyncio
    async def test_quantum_advantage_for_different_qubit_sizes(self, quantum_loop):
        """Test quantum advantage analysis for various qubit counts"""
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            return_value={"quantum_speedup_factor": 3.0}
        )

        for n_qubits in [2, 3, 4, 5]:
            candidate = {
                "id": f"q_{n_qubits}",
                "algorithm": "qaoa",
                "n_qubits": n_qubits,
                "depth": 2
            }
            
            evaluation = await quantum_loop._evaluate_candidate_async(candidate)
            
            # Should have quantum advantage analysis
            assert "advanced_analysis" in evaluation
            assert "quantum_advantage" in evaluation["advanced_analysis"]


class TestPINNSimulations:
    """Test PhysicsInformedNN service integration"""

    @pytest.fixture
    def quantum_loop(self):
        return QuantumLoop()

    @pytest.fixture
    def mock_small_candidate(self):
        """Mock candidate with small qubit count (suitable for PINN)"""
        return {
            "id": "q_small_001",
            "algorithm": "vqe",
            "n_qubits": 2,  # Small enough for PINN
            "depth": 1
        }

    @pytest.fixture
    def mock_pinn_result(self):
        """Mock PINN simulation result"""
        return {
            "method": "pytorch_pinn",
            "pde_type": "schrodinger",
            "configuration": {
                "epochs": 50,
                "learning_rate": 0.001,
                "num_collocation": 200
            },
            "training": {
                "final_loss": 0.0023,
                "loss_history": [0.5, 0.3, 0.1, 0.05, 0.0023]
            },
            "predictions": [[0.1, 0.2], [0.3, 0.4]],
            "physics_residual": 0.001
        }

    @pytest.mark.asyncio
    async def test_pinn_schrodinger_simulation(self, quantum_loop, mock_small_candidate, mock_pinn_result):
        """Test PINN simulation for Schrödinger equation"""
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            return_value={"quantum_speedup_factor": 1.5}
        )
        quantum_loop.physics_informed_nn_service.solve_pde_pytorch = AsyncMock(
            return_value=mock_pinn_result
        )

        evaluation = await quantum_loop._evaluate_candidate_async(mock_small_candidate)

        # Verify PINN was called for small system
        quantum_loop.physics_informed_nn_service.solve_pde_pytorch.assert_called_once()
        
        # Check config
        call_args = quantum_loop.physics_informed_nn_service.solve_pde_pytorch.call_args
        config = call_args.args[0]
        assert config["pde_type"] == "schrodinger"
        assert "num_collocation" in config
        assert "epochs" in config

        # Verify evaluation
        assert "pinn_simulation" in evaluation["advanced_analysis"]

    @pytest.mark.asyncio
    async def test_pinn_skipped_for_large_systems(self, quantum_loop):
        """Test that PINN is skipped for large qubit counts"""
        large_candidate = {
            "id": "q_large_001",
            "algorithm": "qaoa",
            "n_qubits": 10,  # Too large for PINN
            "depth": 3
        }
        
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            return_value={}
        )

        evaluation = await quantum_loop._evaluate_candidate_async(large_candidate)

        # PINN should not be in advanced_analysis (or should be None/error)
        if "pinn_simulation" in evaluation.get("advanced_analysis", {}):
            # If present, should indicate skipped or None
            assert evaluation["advanced_analysis"]["pinn_simulation"] is None or \
                   "error" in str(evaluation["advanced_analysis"]["pinn_simulation"])


class TestQuantumChemistryCalculations:
    """Test QuantumChemistryService integration"""

    @pytest.fixture
    def quantum_loop(self):
        return QuantumLoop()

    @pytest.fixture
    def mock_vqe_candidate(self):
        """Mock VQE candidate for quantum chemistry"""
        return {
            "id": "q_vqe_001",
            "algorithm": "vqe",
            "n_qubits": 4,
            "depth": 2,
            "parameters": {"molecule": "H2"}
        }

    @pytest.fixture
    def mock_qchem_result(self):
        """Mock quantum chemistry calculation result"""
        return {
            "molecule": "H2",
            "method": "hf",
            "energy": -1.1372,
            "basis": "sto-3g",
            "dipole_moment": [0.0, 0.0, 0.0],
            "optimization_converged": True,
            "num_iterations": 12
        }

    @pytest.mark.asyncio
    async def test_quantum_chemistry_vqe_analysis(self, quantum_loop, mock_vqe_candidate, mock_qchem_result):
        """Test quantum chemistry analysis for VQE algorithm"""
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            return_value={}
        )
        quantum_loop.quantum_chemistry_service.molecular_energy_calculation = AsyncMock(
            return_value=mock_qchem_result
        )

        evaluation = await quantum_loop._evaluate_candidate_async(mock_vqe_candidate)

        # Verify quantum chemistry was called for VQE
        quantum_loop.quantum_chemistry_service.molecular_energy_calculation.assert_called_once()
        
        # Check parameters
        call_args = quantum_loop.quantum_chemistry_service.molecular_energy_calculation.call_args
        params = call_args.args[0]
        assert "molecule" in params
        assert params["molecule"] == "H2"
        assert "method" in params

        # Verify evaluation
        assert "quantum_chemistry" in evaluation["advanced_analysis"]

    @pytest.mark.asyncio
    async def test_quantum_chemistry_skipped_for_non_vqe(self, quantum_loop):
        """Test that quantum chemistry is skipped for non-VQE algorithms"""
        qaoa_candidate = {
            "id": "q_qaoa_001",
            "algorithm": "qaoa",
            "n_qubits": 4,
            "depth": 2
        }
        
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            return_value={}
        )

        evaluation = await quantum_loop._evaluate_candidate_async(qaoa_candidate)

        # Quantum chemistry should not be called for QAOA
        assert "quantum_chemistry" not in evaluation.get("advanced_analysis", {}) or \
               evaluation["advanced_analysis"].get("quantum_chemistry") is None


class TestEvaluationPipeline:
    """Test complete evaluation pipeline with all quantum services"""

    @pytest.fixture
    def quantum_loop(self):
        return QuantumLoop()

    @pytest.fixture
    def mock_candidate(self):
        return {
            "id": "q_pipeline_001",
            "algorithm": "vqe",
            "n_qubits": 3,
            "depth": 2,
            "parameters": {"problem_size": 3}
        }

    @pytest.mark.asyncio
    async def test_complete_evaluation_pipeline(self, quantum_loop, mock_candidate):
        """Test that all quantum services run in evaluation pipeline"""
        # Mock all services
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            return_value={"quantum_speedup_factor": 2.8}
        )
        quantum_loop.physics_informed_nn_service.solve_pde_pytorch = AsyncMock(
            return_value={"final_loss": 0.002, "method": "pytorch_pinn"}
        )
        quantum_loop.quantum_chemistry_service.molecular_energy_calculation = AsyncMock(
            return_value={"energy": -1.14, "molecule": "H2"}
        )

        evaluation = await quantum_loop._evaluate_candidate_async(mock_candidate)

        # All applicable services should have been called
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage.assert_called_once()
        
        # PINN should be called for small system (n_qubits=3)
        quantum_loop.physics_informed_nn_service.solve_pde_pytorch.assert_called_once()
        
        # Quantum chemistry should be called for VQE
        quantum_loop.quantum_chemistry_service.molecular_energy_calculation.assert_called_once()

        # Evaluation should have all components
        assert "algorithm" in evaluation
        assert "simulation" in evaluation
        assert "advanced_analysis" in evaluation
        assert "quantum_advantage" in evaluation["advanced_analysis"]
        assert "pinn_simulation" in evaluation["advanced_analysis"]
        assert "quantum_chemistry" in evaluation["advanced_analysis"]

    @pytest.mark.asyncio
    async def test_pipeline_partial_failure_resilience(self, quantum_loop, mock_candidate):
        """Test pipeline continues even if some services fail"""
        # Quantum advantage fails
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            side_effect=Exception("Quantum advantage analysis failed")
        )
        
        # PINN succeeds
        quantum_loop.physics_informed_nn_service.solve_pde_pytorch = AsyncMock(
            return_value={"final_loss": 0.01}
        )
        
        # Quantum chemistry fails
        quantum_loop.quantum_chemistry_service.molecular_energy_calculation = AsyncMock(
            side_effect=Exception("Quantum chemistry failed")
        )

        # Should not raise exception
        evaluation = await quantum_loop._evaluate_candidate_async(mock_candidate)

        # Should have structure
        assert isinstance(evaluation, dict)
        assert "advanced_analysis" in evaluation


class TestQuantumServicesErrorHandling:
    """Test error handling for quantum service failures"""

    @pytest.fixture
    def quantum_loop(self):
        return QuantumLoop()

    @pytest.fixture
    def mock_candidate(self):
        return {"id": "test", "algorithm": "vqe", "n_qubits": 2, "depth": 1}

    @pytest.mark.asyncio
    async def test_quantum_advantage_timeout(self, quantum_loop, mock_candidate):
        """Test handling of quantum advantage analysis timeout"""
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            side_effect=asyncio.TimeoutError("Analysis timeout")
        )

        evaluation = await quantum_loop._evaluate_candidate_async(mock_candidate)
        
        # Should have advanced_analysis with error info
        assert "advanced_analysis" in evaluation
        assert "quantum_advantage" in evaluation["advanced_analysis"]

    @pytest.mark.asyncio
    async def test_pinn_computation_error(self, quantum_loop, mock_candidate):
        """Test handling of PINN computation errors"""
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            return_value={}
        )
        quantum_loop.physics_informed_nn_service.solve_pde_pytorch = AsyncMock(
            side_effect=RuntimeError("PINN convergence failed")
        )

        evaluation = await quantum_loop._evaluate_candidate_async(mock_candidate)
        
        # Should handle gracefully
        assert "advanced_analysis" in evaluation

    @pytest.mark.asyncio
    async def test_all_quantum_services_fail_gracefully(self, quantum_loop, mock_candidate):
        """Test that evaluation continues even if all advanced services fail"""
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(
            side_effect=Exception("Failed")
        )
        quantum_loop.physics_informed_nn_service.solve_pde_pytorch = AsyncMock(
            side_effect=Exception("Failed")
        )
        quantum_loop.quantum_chemistry_service.molecular_energy_calculation = AsyncMock(
            side_effect=Exception("Failed")
        )

        # Should not crash
        evaluation = await quantum_loop._evaluate_candidate_async(mock_candidate)
        
        # Should still have base evaluation
        assert isinstance(evaluation, dict)
        assert "algorithm" in evaluation


class TestQuantumServiceScalability:
    """Test scalability constraints for quantum services"""

    @pytest.fixture
    def quantum_loop(self):
        return QuantumLoop()

    @pytest.mark.asyncio
    async def test_pinn_only_runs_for_small_qubits(self, quantum_loop):
        """Test PINN only runs for n_qubits <= 3"""
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(return_value={})
        
        # Test small system (should run PINN)
        small_candidate = {"id": "small", "algorithm": "vqe", "n_qubits": 2, "depth": 1}
        quantum_loop.physics_informed_nn_service.solve_pde_pytorch = AsyncMock(return_value={"loss": 0.01})
        
        evaluation_small = await quantum_loop._evaluate_candidate_async(small_candidate)
        assert quantum_loop.physics_informed_nn_service.solve_pde_pytorch.called
        
        # Reset mock
        quantum_loop.physics_informed_nn_service.solve_pde_pytorch.reset_mock()
        
        # Test large system (should NOT run PINN)
        large_candidate = {"id": "large", "algorithm": "vqe", "n_qubits": 5, "depth": 1}
        
        evaluation_large = await quantum_loop._evaluate_candidate_async(large_candidate)
        assert not quantum_loop.physics_informed_nn_service.solve_pde_pytorch.called

    @pytest.mark.asyncio
    async def test_quantum_chemistry_only_for_small_vqe(self, quantum_loop):
        """Test quantum chemistry only runs for VQE with n_qubits <= 4"""
        quantum_loop.quantum_algorithms_service.analyze_quantum_advantage = AsyncMock(return_value={})
        
        # Small VQE (should run)
        small_vqe = {"id": "small", "algorithm": "vqe", "n_qubits": 3, "depth": 1}
        quantum_loop.quantum_chemistry_service.molecular_energy_calculation = AsyncMock(return_value={"energy": -1.1})
        
        await quantum_loop._evaluate_candidate_async(small_vqe)
        assert quantum_loop.quantum_chemistry_service.molecular_energy_calculation.called
        
        # Reset
        quantum_loop.quantum_chemistry_service.molecular_energy_calculation.reset_mock()
        
        # Large VQE (should NOT run)
        large_vqe = {"id": "large", "algorithm": "vqe", "n_qubits": 8, "depth": 2}
        
        await quantum_loop._evaluate_candidate_async(large_vqe)
        assert not quantum_loop.quantum_chemistry_service.molecular_energy_calculation.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
