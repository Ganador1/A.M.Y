"""
Tests para Uncertainty Quantification Suite
===========================================

Tests comprehensivos para cuantificación de incertidumbre usando
múltiples métodos: Monte Carlo Dropout, Ensemble, Conformal Prediction.

Tests incluidos:
- Monte Carlo Dropout
- Ensemble Methods
- Conformal Prediction
- Bootstrap
- Comparación de métodos
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.uncertainty_quantification import (
    UncertaintyQuantificationService,
    MonteCarloDropoutQuantifier,
    EnsembleQuantifier,
    BootstrapQuantifier,
    UncertaintyConfig
)
from app.services.conformal_prediction import conformal_service


client = TestClient(app)


class TestMonteCarloDropout:
    """Tests para Monte Carlo Dropout"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.quantifier = MonteCarloDropoutQuantifier()
        self.config = UncertaintyConfig(
            method="dropout",
            num_samples=100,
            confidence_level=0.95,
            dropout_rate=0.1
        )
    
    @pytest.mark.asyncio
    async def test_monte_carlo_dropout_basic(self):
        """Test básico de Monte Carlo Dropout"""
        # Mock model
        mock_model = Mock()
        mock_model.train = Mock()
        
        test_data = np.array([[1, 2], [3, 4], [5, 6]])
        
        result = await self.quantifier.quantify_uncertainty(mock_model, test_data, self.config)
        
        assert result.method_used == "monte_carlo_dropout"
        assert 'epistemic_uncertainty' in result.uncertainty_metrics
        assert 'aleatoric_uncertainty' in result.uncertainty_metrics
        assert 'mutual_information' in result.uncertainty_metrics
        assert len(result.mean_prediction) == len(test_data)
    
    @pytest.mark.asyncio
    async def test_monte_carlo_dropout_confidence_intervals(self):
        """Test intervalos de confianza"""
        mock_model = Mock()
        test_data = np.array([[1, 2]])
        
        result = await self.quantifier.quantify_uncertainty(mock_model, test_data, self.config)
        
        assert 'confidence_intervals' in result.__dict__
        intervals = result.confidence_intervals
        assert 'lower_bound' in intervals
        assert 'upper_bound' in intervals
        assert 'confidence_level' in intervals
        assert intervals['confidence_level'] == 0.95
    
    def test_mc_dropout_prediction_callable_model(self):
        """Test predicción con modelo callable"""
        def mock_model(data):
            return np.mean(data, axis=1)
        
        test_data = np.array([[1, 2], [3, 4]])
        result = self.quantifier._mc_dropout_prediction(mock_model, test_data, 0.1)
        
        assert len(result) == 2
        assert isinstance(result, np.ndarray)
    
    def test_mc_dropout_prediction_fallback(self):
        """Test predicción con fallback"""
        mock_model = "not_callable"  # Non-callable model
        test_data = np.array([[1, 2], [3, 4]])
        
        result = self.quantifier._mc_dropout_prediction(mock_model, test_data, 0.1)
        
        assert len(result) == 2
        assert isinstance(result, np.ndarray)
    
    def test_compute_mutual_information(self):
        """Test cálculo de información mutua"""
        predictions = np.array([
            [0.1, 0.9],
            [0.2, 0.8], 
            [0.15, 0.85]
        ])
        
        mi = self.quantifier._compute_mutual_information(predictions)
        
        assert isinstance(mi, float)
        assert mi >= 0  # Mutual information is non-negative


class TestEnsembleMethods:
    """Tests para Ensemble Methods"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.quantifier = EnsembleQuantifier()
        self.config = UncertaintyConfig(
            method="ensemble",
            num_samples=100,
            confidence_level=0.95,
            ensemble_size=5
        )
    
    @pytest.mark.asyncio
    async def test_ensemble_quantification_basic(self):
        """Test básico de ensemble quantification"""
        # Mock models
        mock_models = []
        for i in range(3):
            model = Mock()
            model.predict = Mock(return_value=np.array([1.0 + i*0.1, 2.0 + i*0.1]))
            mock_models.append(model)
        
        test_data = np.array([[1, 2], [3, 4]])
        
        result = await self.quantifier.quantify_uncertainty(mock_models, test_data, self.config)
        
        assert result.method_used == "ensemble"
        assert 'ensemble_variance' in result.uncertainty_metrics
        assert 'ensemble_diversity' in result.uncertainty_metrics
        assert 'ensemble_agreement' in result.uncertainty_metrics
    
    @pytest.mark.asyncio
    async def test_ensemble_single_model(self):
        """Test ensemble con un solo modelo"""
        mock_model = Mock()
        mock_model.predict = Mock(return_value=np.array([1.0, 2.0]))
        
        test_data = np.array([[1, 2]])
        
        result = await self.quantifier.quantify_uncertainty(mock_model, test_data, self.config)
        
        assert result.method_used == "ensemble"
        # Should replicate the model
        assert len(result.mean_prediction) == 1
    
    def test_compute_ensemble_diversity(self):
        """Test cálculo de diversidad del ensemble"""
        predictions = np.array([
            [1.0, 2.0],  # Model 1
            [1.1, 2.1],  # Model 2  
            [0.9, 1.9]   # Model 3
        ])
        
        diversity = self.quantifier._compute_ensemble_diversity(predictions)
        
        assert isinstance(diversity, float)
        assert diversity >= 0
    
    def test_compute_ensemble_agreement(self):
        """Test cálculo de acuerdo del ensemble"""
        # Predictions que deberían tener alta correlación
        predictions = np.array([
            [1.0, 2.0, 3.0],
            [1.1, 2.1, 3.1], 
            [1.2, 2.2, 3.2]
        ])
        
        agreement = self.quantifier._compute_ensemble_agreement(predictions)
        
        assert isinstance(agreement, float)
        assert -1 <= agreement <= 1  # Correlation bounds


class TestConformalPrediction:
    """Tests para Conformal Prediction"""
    
    @pytest.mark.asyncio
    async def test_split_conformal_basic(self):
        """Test básico de split conformal prediction"""
        # Generate synthetic data
        X_train = np.random.randn(100, 2)
        y_train = np.sum(X_train, axis=1) + np.random.randn(100) * 0.1
        X_test = np.random.randn(10, 2)
        
        try:
            result = await conformal_service.fit_and_predict(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                method='split',
                confidence_level=0.9
            )
            
            assert 'predictions' in result
            assert 'lower_bound' in result
            assert 'upper_bound' in result
            assert 'interval_width' in result
            assert len(result['predictions']) == len(X_test)
            
        except RuntimeError as e:
            if "scikit-learn not available" in str(e):
                pytest.skip("scikit-learn not available")
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_jackknife_conformal(self):
        """Test Jackknife+ conformal prediction"""
        X_train = np.random.randn(20, 2)  # Smaller for Jackknife
        y_train = np.sum(X_train, axis=1)
        X_test = np.random.randn(5, 2)
        
        try:
            result = await conformal_service.fit_and_predict(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                method='jackknife',
                confidence_level=0.9
            )
            
            assert 'predictions' in result
            assert result['method'] == 'jackknife'
            
        except RuntimeError as e:
            if "scikit-learn not available" in str(e):
                pytest.skip("scikit-learn not available")
            else:
                raise
    
    def test_evaluate_coverage(self):
        """Test evaluación de cobertura"""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        lower_bound = np.array([0.5, 1.5, 2.5, 3.5, 4.5])
        upper_bound = np.array([1.5, 2.5, 3.5, 4.5, 5.5])
        
        coverage = conformal_service.evaluate_coverage(y_true, lower_bound, upper_bound)
        
        assert 'empirical_coverage' in coverage
        assert 'mean_interval_width' in coverage
        assert coverage['empirical_coverage'] == 1.0  # Perfect coverage
        assert coverage['coverage_count'] == 5


class TestBootstrapQuantification:
    """Tests para Bootstrap Quantification"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.quantifier = BootstrapQuantifier()
        self.config = UncertaintyConfig(
            method="bootstrap",
            num_samples=100,
            confidence_level=0.95,
            bootstrap_iterations=50
        )
    
    @pytest.mark.asyncio
    async def test_bootstrap_quantification_basic(self):
        """Test básico de bootstrap quantification"""
        mock_model = Mock()
        mock_model.predict = Mock(return_value=np.array([1.0, 2.0]))
        
        test_data = np.array([[1, 2], [3, 4]])
        
        result = await self.quantifier.quantify_uncertainty(mock_model, test_data, self.config)
        
        assert result.method_used == "bootstrap"
        assert len(result.mean_prediction) == len(test_data)


class TestUncertaintyEndpoints:
    """Tests para los endpoints de uncertainty quantification"""
    
    def test_monte_carlo_endpoint(self):
        """Test endpoint de Monte Carlo Dropout"""
        payload = {
            "test_data": [[1, 2], [3, 4]],
            "method": "dropout",
            "num_samples": 100,
            "confidence_level": 0.95,
            "dropout_rate": 0.1,
            "model_type": "synthetic",
            "enable_epistemic": True,
            "enable_aleatoric": True
        }
        
        response = client.post("/api/uncertainty-quantification/monte-carlo", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data['method'] == "monte_carlo_dropout"
        assert 'uncertainty_metrics' in data
        assert 'predictions' in data
    
    def test_ensemble_endpoint(self):
        """Test endpoint de Ensemble Methods"""
        payload = {
            "test_data": [[1, 2], [3, 4]],
            "method": "ensemble",
            "num_samples": 100,
            "ensemble_size": 5,
            "ensemble_diversity": True,
            "voting_scheme": "soft"
        }
        
        response = client.post("/api/uncertainty-quantification/ensemble", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data['method'] == "ensemble"
        assert 'ensemble_info' in data
    
    def test_conformal_endpoint(self):
        """Test endpoint de Conformal Prediction"""
        payload = {
            "X_train": [[1, 2], [3, 4], [5, 6], [7, 8]],
            "y_train": [3, 7, 11, 15],
            "X_test": [[2, 3], [4, 5]],
            "method": "split",
            "confidence_level": 0.9,
            "calibration_ratio": 0.3
        }
        
        response = client.post("/api/uncertainty-quantification/conformal", json=payload)
        
        # May fail if scikit-learn not available, but should return proper error
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data['method'] == "split_conformal"
            assert 'predictions' in data
            assert 'intervals' in data
    
    def test_bootstrap_endpoint(self):
        """Test endpoint de Bootstrap"""
        payload = {
            "test_data": [[1, 2], [3, 4]],
            "method": "bootstrap",
            "num_samples": 100
        }
        
        response = client.post("/api/uncertainty-quantification/bootstrap", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data['method'] == "bootstrap"
        assert 'bootstrap_info' in data
    
    def test_compare_methods_endpoint(self):
        """Test endpoint de comparación de métodos"""
        payload = {
            "test_data": [[1, 2], [3, 4]],
            "methods": ["dropout", "ensemble", "bootstrap"],
            "confidence_level": 0.95
        }
        
        response = client.post("/api/uncertainty-quantification/compare-methods", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert 'comparison_results' in data
        assert 'summary' in data
        assert len(data['comparison_results']) <= 3  # Some may fail
    
    def test_methods_info_endpoint(self):
        """Test endpoint de información de métodos"""
        response = client.get("/api/uncertainty-quantification/methods")
        
        assert response.status_code == 200
        data = response.json()
        assert 'available_methods' in data
        assert 'dependencies' in data
        assert 'recommended_configs' in data
        
        # Verificar métodos específicos
        methods = data['available_methods']
        assert 'monte_carlo_dropout' in methods
        assert 'ensemble' in methods
        assert 'conformal_prediction' in methods
    
    def test_invalid_request_validation(self):
        """Test validación de requests inválidos"""
        # Test Monte Carlo con dropout rate inválido
        payload = {
            "test_data": [[1, 2]],
            "dropout_rate": 1.5  # Invalid: > 1.0
        }
        
        response = client.post("/api/uncertainty-quantification/monte-carlo", json=payload)
        assert response.status_code == 422
        
        # Test ensemble con tamaño inválido
        payload = {
            "test_data": [[1, 2]],
            "ensemble_size": 0  # Invalid: must be >= 2
        }
        
        response = client.post("/api/uncertainty-quantification/ensemble", json=payload)
        assert response.status_code == 422


class TestUncertaintyIntegration:
    """Tests de integración para uncertainty quantification"""
    
    @pytest.mark.asyncio
    async def test_full_uncertainty_workflow(self):
        """Test workflow completo de uncertainty quantification"""
        # 1. Obtener métodos disponibles
        response = client.get("/api/uncertainty-quantification/methods")
        assert response.status_code == 200
        methods_info = response.json()
        
        # 2. Ejecutar Monte Carlo Dropout
        mc_payload = {
            "test_data": [[1, 2], [3, 4]],
            "num_samples": 50,  # Reduced for speed
            "dropout_rate": 0.1
        }
        response = client.post("/api/uncertainty-quantification/monte-carlo", json=mc_payload)
        assert response.status_code == 200
        mc_result = response.json()
        
        # 3. Ejecutar Ensemble
        ensemble_payload = {
            "test_data": [[1, 2], [3, 4]],
            "ensemble_size": 3
        }
        response = client.post("/api/uncertainty-quantification/ensemble", json=ensemble_payload)
        assert response.status_code == 200
        ensemble_result = response.json()
        
        # 4. Comparar métodos
        compare_payload = {
            "test_data": [[1, 2], [3, 4]],
            "methods": ["dropout", "ensemble"]
        }
        response = client.post("/api/uncertainty-quantification/compare-methods", json=compare_payload)
        assert response.status_code == 200
        comparison = response.json()
        
        # Verificar que el workflow es consistente
        assert 'fastest_method' in comparison['summary']
    
    def test_error_handling_and_resilience(self):
        """Test manejo de errores y resilencia"""
        # Test con datos vacíos
        payload = {"test_data": []}
        response = client.post("/api/uncertainty-quantification/monte-carlo", json=payload)
        assert response.status_code == 422
        
        # Test con confidence level inválido
        payload = {
            "test_data": [[1, 2]],
            "confidence_level": 1.5  # Invalid
        }
        response = client.post("/api/uncertainty-quantification/bootstrap", json=payload)
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
