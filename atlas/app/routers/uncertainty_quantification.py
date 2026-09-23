"""
Router de Uncertainty Quantification para AXIOM
===============================================

Endpoints especializados para cuantificación de incertidumbre usando
múltiples métodos: Monte Carlo Dropout, Ensemble, Bootstrap, Fiducial
y Conformal Prediction.

Endpoints:
- POST /monte-carlo: Monte Carlo Dropout uncertainty
- POST /ensemble: Ensemble uncertainty quantification
- POST /conformal: Conformal prediction intervals
- POST /bootstrap: Bootstrap confidence intervals
- POST /compare-methods: Comparar múltiples métodos
- GET /methods: Métodos disponibles y configuraciones

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import numpy as np

from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.quality.uncertainty_quantification import (
    UncertaintyQuantificationService,
    UncertaintyConfig,
    MonteCarloDropoutQuantifier,
    EnsembleQuantifier,
    BootstrapQuantifier,
)
from app.services.conformal_prediction import conformal_service
from app.types.uncertainty_quantification_types import (
    MonteCarloUncertaintyResult,
    EnsembleUncertaintyResult,
    ConformalPredictionResult,
    BootstrapUncertaintyResult,
    CompareUncertaintyMethodsResult,
    GetAvailableMethodsResult,
)

router = APIRouter()

# Global service instance
uncertainty_service = UncertaintyQuantificationService()


class UncertaintyRequest(BaseModel):
    """Request base para uncertainty quantification"""
    test_data: List[List[float]] = Field(..., description="Datos de prueba")
    method: str = Field("dropout", description="Método de quantificación")
    num_samples: int = Field(1000, ge=100, le=10000, description="Número de muestras")
    confidence_level: float = Field(0.95, ge=0.8, le=0.99, description="Nivel de confianza")
    dropout_rate: float = Field(0.1, ge=0.01, le=0.5, description="Tasa de dropout")
    ensemble_size: int = Field(5, ge=2, le=20, description="Tamaño del ensemble")


class MonteCarloRequest(UncertaintyRequest):
    """Request para Monte Carlo Dropout"""
    model_type: str = Field("synthetic", description="Tipo de modelo")
    enable_epistemic: bool = Field(True, description="Calcular incertidumbre epistémica")
    enable_aleatoric: bool = Field(True, description="Calcular incertidumbre aleatórica")


class EnsembleRequest(UncertaintyRequest):
    """Request para Ensemble methods"""
    ensemble_diversity: bool = Field(True, description="Calcular diversidad del ensemble")
    voting_scheme: str = Field("soft", description="Esquema de votación")


class ConformalRequest(BaseModel):
    """Request para Conformal Prediction"""
    X_train: List[List[float]] = Field(..., description="Datos de entrenamiento (features)")
    y_train: List[float] = Field(..., description="Targets de entrenamiento")
    X_test: List[List[float]] = Field(..., description="Datos de prueba (features)")
    method: str = Field("split", description="Método conformal")
    confidence_level: float = Field(0.9, ge=0.8, le=0.99, description="Nivel de confianza")
    calibration_ratio: float = Field(0.3, ge=0.1, le=0.5, description="Ratio de calibración")


class ComparisonRequest(BaseModel):
    """Request para comparar múltiples métodos"""
    test_data: List[List[float]] = Field(..., description="Datos de prueba")
    methods: List[str] = Field(["dropout", "ensemble", "bootstrap"], description="Métodos a comparar")
    confidence_level: float = Field(0.95, description="Nivel de confianza")


@router.post("/monte-carlo")
async def monte_carlo_uncertainty(request: MonteCarloRequest) -> MonteCarloUncertaintyResult:
    """
    🎲 Monte Carlo Dropout Uncertainty Quantification
    
    Utiliza Monte Carlo Dropout para estimar incertidumbre epistémica
    y aleatórica en predicciones de modelos neuronales.
    
    **Características:**
    - Múltiples forward passes con dropout activado
    - Separación de incertidumbre epistémica/aleatórica
    - Información mutua para epistemic uncertainty
    - Intervalos de confianza calibrados
    
    **Respuesta:**
    ```json
    {
        "method": "monte_carlo_dropout",
        "uncertainty_metrics": {
            "epistemic_uncertainty": 0.15,
            "aleatoric_uncertainty": 0.08,
            "total_uncertainty": 0.23,
            "mutual_information": 0.12
        },
        "predictions": {
            "mean": [2.3, 4.1, 1.8],
            "std": [0.4, 0.3, 0.2],
            "confidence_intervals": {
                "lower_bound": [1.9, 3.8, 1.6],
                "upper_bound": [2.7, 4.4, 2.0]
            }
        },
        "reliability_score": 0.87,
        "computation_time": 0.23
    }
    ```
    """
    try:
        logger.info("🎲 Iniciando Monte Carlo Dropout uncertainty quantification")
        
        # Configuración
        config = UncertaintyConfig(
            method="dropout",
            num_samples=request.num_samples,
            confidence_level=request.confidence_level,
            dropout_rate=request.dropout_rate
        )
        
        # Mock model para demostración
        class MockModel:
            """Mock model for Monte Carlo Dropout demonstration."""
            def train(self): pass
            def predict(self, data):
                # Simulación de predicción con variabilidad
                base = np.mean(np.array(data), axis=1)
                noise = np.random.normal(0, request.dropout_rate, base.shape)
                return base + noise
        
        mock_model = MockModel()
        test_data = np.array(request.test_data)
        
        # Quantificador Monte Carlo Dropout
        quantifier = MonteCarloDropoutQuantifier()
        result = await quantifier.quantify_uncertainty(mock_model, test_data, config)
        
        logger.info("✅ Monte Carlo Dropout completado")
        
        return {
            "method": result.method_used,
            "uncertainty_metrics": result.uncertainty_metrics,
            "predictions": {
                "mean": result.mean_prediction.tolist(),
                "std": result.std_prediction.tolist(),
                "confidence_intervals": {
                    "lower_bound": result.confidence_intervals['lower_bound'].tolist(),
                    "upper_bound": result.confidence_intervals['upper_bound'].tolist(),
                    "confidence_level": result.confidence_intervals['confidence_level']
                }
            },
            "reliability_score": result.reliability_score,
            "coverage_probability": result.coverage_probability,
            "computation_time": result.computation_time,
            "config": {
                "num_samples": request.num_samples,
                "dropout_rate": request.dropout_rate,
                "model_type": request.model_type
            }
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error en Monte Carlo Dropout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ensemble")
async def ensemble_uncertainty(request: EnsembleRequest) -> EnsembleUncertaintyResult:
    """
    🤝 Ensemble Uncertainty Quantification
    
    Utiliza múltiples modelos para estimar incertidumbre mediante
    diversidad de predicciones y métricas de acuerdo.
    
    **Características:**
    - Deep ensembles con diversidad
    - Métricas de acuerdo entre modelos
    - Varianza de ensemble
    - Correlación entre predicciones
    
    **Respuesta:**
    ```json
    {
        "method": "ensemble",
        "uncertainty_metrics": {
            "ensemble_variance": 0.18,
            "ensemble_diversity": 0.34,
            "ensemble_agreement": 0.76
        },
        "predictions": {
            "mean": [2.1, 3.8, 1.9],
            "std": [0.3, 0.4, 0.2]
        },
        "ensemble_info": {
            "size": 5,
            "voting_scheme": "soft"
        }
    }
    ```
    """
    try:
        logger.info("🤝 Iniciando Ensemble uncertainty quantification")
        
        # Configuración
        config = UncertaintyConfig(
            method="ensemble",
            num_samples=request.num_samples,
            confidence_level=request.confidence_level,
            ensemble_size=request.ensemble_size
        )
        
        # Mock ensemble de modelos
        class MockEnsembleModel:
            def __init__(self, model_id):
                self.model_id = model_id
                self.noise_scale = 0.1 + (model_id * 0.05)  # Diversidad
            
            def predict(self, data):
                base = np.mean(np.array(data), axis=1)
                noise = np.random.normal(0, self.noise_scale, base.shape)
                return base + noise
        
        # Crear ensemble
        models = [MockEnsembleModel(i) for i in range(request.ensemble_size)]
        test_data = np.array(request.test_data)
        
        # Quantificador Ensemble
        quantifier = EnsembleQuantifier()
        result = await quantifier.quantify_uncertainty(models, test_data, config)
        
        logger.info("✅ Ensemble uncertainty completado")
        
        return {
            "method": result.method_used,
            "uncertainty_metrics": result.uncertainty_metrics,
            "predictions": {
                "mean": result.mean_prediction.tolist(),
                "std": result.std_prediction.tolist(),
                "confidence_intervals": {
                    "lower_bound": result.confidence_intervals['lower_bound'].tolist(),
                    "upper_bound": result.confidence_intervals['upper_bound'].tolist()
                }
            },
            "ensemble_info": {
                "size": request.ensemble_size,
                "voting_scheme": request.voting_scheme,
                "diversity_enabled": request.ensemble_diversity
            },
            "reliability_score": result.reliability_score,
            "computation_time": result.computation_time
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error en Ensemble uncertainty: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conformal")
async def conformal_prediction(request: ConformalRequest) -> ConformalPredictionResult:
    """
    📐 Conformal Prediction Intervals
    
    Genera intervalos de predicción calibrados con garantías
    estadísticas de cobertura usando conformal prediction.
    
    **Métodos disponibles:**
    - `split`: Split conformal prediction
    - `jackknife`: Jackknife+ prediction
    - `quantile`: Conformalized quantile regression
    
    **Respuesta:**
    ```json
    {
        "method": "split_conformal",
        "predictions": [2.3, 4.1, 1.8],
        "intervals": {
            "lower_bound": [1.8, 3.6, 1.4],
            "upper_bound": [2.8, 4.6, 2.2],
            "width": [1.0, 1.0, 0.8]
        },
        "calibration": {
            "confidence_level": 0.9,
            "quantile_used": 0.91,
            "training_size": 140,
            "calibration_size": 60
        }
    }
    ```
    """
    try:
        logger.info("📐 Iniciando Conformal Prediction")
        
        # Convertir a numpy arrays
        X_train = np.array(request.X_train)
        y_train = np.array(request.y_train)
        X_test = np.array(request.X_test)
        
        # Ejecutar conformal prediction
        result = await conformal_service.fit_and_predict(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            method=request.method,
            confidence_level=request.confidence_level,
            calibration_ratio=request.calibration_ratio
        )
        
        logger.info("✅ Conformal prediction completado")
        
        return {
            "method": f"{request.method}_conformal",
            "predictions": result['predictions'].tolist(),
            "intervals": {
                "lower_bound": result['lower_bound'].tolist(),
                "upper_bound": result['upper_bound'].tolist(),
                "width": result['interval_width'].tolist()
            },
            "calibration": {
                "confidence_level": result['confidence_level'],
                "training_size": result['training_size'],
                "calibration_size": result['calibration_size'],
                "test_size": result['test_size']
            },
            "sklearn_available": result['sklearn_available']
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error en Conformal Prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bootstrap")
async def bootstrap_uncertainty(request: UncertaintyRequest) -> BootstrapUncertaintyResult:
    """
    🔄 Bootstrap Confidence Intervals
    
    Utiliza re-muestreo bootstrap para estimar intervalos de
    confianza y robustez de predicciones.
    
    **Características:**
    - Re-muestreo con reemplazo
    - Intervalos percentil
    - Métricas de sesgo bootstrap
    - Estimación de robustez
    """
    try:
        logger.info("🔄 Iniciando Bootstrap uncertainty quantification")
        
        # Configuración
        config = UncertaintyConfig(
            method="bootstrap",
            num_samples=request.num_samples,
            confidence_level=request.confidence_level,
            bootstrap_iterations=min(request.num_samples, 1000)
        )
        
        # Mock model
        class MockBootstrapModel:
            """Mock model for Bootstrap demonstration."""
            def predict(self, data):
                return np.mean(np.array(data), axis=1)
        
        mock_model = MockBootstrapModel()
        test_data = np.array(request.test_data)
        
        # Quantificador Bootstrap
        quantifier = BootstrapQuantifier()
        result = await quantifier.quantify_uncertainty(mock_model, test_data, config)
        
        logger.info("✅ Bootstrap uncertainty completado")
        
        return {
            "method": result.method_used,
            "uncertainty_metrics": result.uncertainty_metrics,
            "predictions": {
                "mean": result.mean_prediction.tolist(),
                "std": result.std_prediction.tolist(),
                "confidence_intervals": {
                    "lower_bound": result.confidence_intervals['lower_bound'].tolist(),
                    "upper_bound": result.confidence_intervals['upper_bound'].tolist()
                }
            },
            "bootstrap_info": {
                "iterations": config.bootstrap_iterations,
                "resampling": "with_replacement"
            },
            "reliability_score": result.reliability_score,
            "computation_time": result.computation_time
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error en Bootstrap uncertainty: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-methods")
async def compare_uncertainty_methods(request: ComparisonRequest) -> CompareUncertaintyMethodsResult:
    """
    🔬 Comparar Métodos de Uncertainty Quantification
    
    Ejecuta múltiples métodos de cuantificación de incertidumbre
    en los mismos datos para comparar resultados y rendimiento.
    
    **Respuesta:**
    ```json
    {
        "comparison_results": {
            "dropout": {
                "uncertainty_metrics": {...},
                "computation_time": 0.23
            },
            "ensemble": {
                "uncertainty_metrics": {...},
                "computation_time": 0.45
            }
        },
        "summary": {
            "fastest_method": "dropout",
            "highest_uncertainty": "ensemble",
            "recommended": "dropout"
        }
    }
    ```
    """
    try:
        logger.info("🔬 Iniciando comparación de métodos UQ")
        
        test_data = np.array(request.test_data)
        results = {}
        
        for method in request.methods:
            try:
                config = UncertaintyConfig(
                    method=method,
                    confidence_level=request.confidence_level
                )
                
                # Mock models para cada método
                if method == "dropout":
                    class MockDropoutModel:
                        def train(self): pass
                        def predict(self, data):
                            return np.mean(data, axis=1) + np.random.normal(0, 0.1, len(data))
                    
                    quantifier = MonteCarloDropoutQuantifier()
                    result = await quantifier.quantify_uncertainty(MockDropoutModel(), test_data, config)
                    
                elif method == "ensemble":
                    models = [lambda x: np.mean(x, axis=1) + np.random.normal(0, 0.1, len(x)) for _ in range(5)]
                    quantifier = EnsembleQuantifier()
                    result = await quantifier.quantify_uncertainty(models, test_data, config)
                    
                elif method == "bootstrap":
                    class MockBootstrapModel:
                        """Mock bootstrap model for comparison demonstration."""
                        def predict(self, data): return np.mean(data, axis=1)
                    
                    quantifier = BootstrapQuantifier()
                    result = await quantifier.quantify_uncertainty(MockBootstrapModel(), test_data, config)
                    
                else:
                    continue
                
                results[method] = {
                    "uncertainty_metrics": result.uncertainty_metrics,
                    "mean_prediction": result.mean_prediction.tolist(),
                    "std_prediction": result.std_prediction.tolist(),
                    "computation_time": result.computation_time,
                    "reliability_score": result.reliability_score
                }
                
            except BiologyError as e:
                results[method] = {"error": str(e)}
        
        # Análisis comparativo
        valid_results = {k: v for k, v in results.items() if "error" not in v}
        
        summary = {}
        if valid_results:
            # Método más rápido
            fastest = min(valid_results.keys(), 
                         key=lambda x: valid_results[x]["computation_time"])
            summary["fastest_method"] = fastest
            
            # Mayor incertidumbre
            if all("prediction_variance" in valid_results[k]["uncertainty_metrics"] for k in valid_results):
                highest_uncertainty = max(valid_results.keys(),
                                        key=lambda x: valid_results[x]["uncertainty_metrics"]["prediction_variance"])
                summary["highest_uncertainty"] = highest_uncertainty
            
            # Recomendación (balance velocidad/precision)
            summary["recommended"] = fastest  # Simplificado
        
        logger.info("✅ Comparación de métodos completada")
        
        return {
            "comparison_results": results,
            "summary": summary,
            "methods_compared": request.methods,
            "test_data_shape": list(test_data.shape)
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error en comparación de métodos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/methods")
async def get_available_methods() -> GetAvailableMethodsResult:
    """
    📋 Métodos Disponibles de Uncertainty Quantification
    
    Retorna información sobre todos los métodos disponibles,
    sus configuraciones y casos de uso recomendados.
    """
    return {
        "available_methods": {
            "monte_carlo_dropout": {
                "description": "Monte Carlo Dropout para incertidumbre epistémica/aleatórica",
                "use_cases": ["Neural networks", "Deep learning models"],
                "parameters": ["num_samples", "dropout_rate"],
                "output_metrics": ["epistemic_uncertainty", "aleatoric_uncertainty", "mutual_information"]
            },
            "ensemble": {
                "description": "Ensemble methods con múltiples modelos",
                "use_cases": ["Model averaging", "Robustness assessment"],
                "parameters": ["ensemble_size", "voting_scheme"],
                "output_metrics": ["ensemble_variance", "diversity", "agreement"]
            },
            "conformal_prediction": {
                "description": "Intervalos calibrados con garantías de cobertura",
                "use_cases": ["Critical applications", "Coverage guarantees"],
                "methods": ["split", "jackknife", "quantile"],
                "output_metrics": ["coverage_guarantee", "interval_width"]
            },
            "bootstrap": {
                "description": "Re-muestreo bootstrap para intervalos de confianza",
                "use_cases": ["Small datasets", "Robustness analysis"],
                "parameters": ["bootstrap_iterations"],
                "output_metrics": ["bootstrap_bias", "percentile_intervals"]
            },
            "fiducial": {
                "description": "Inferencia fiducial para PINNs",
                "use_cases": ["Physics-informed models", "PDEs"],
                "parameters": ["perturbation_scale"],
                "output_metrics": ["fiducial_intervals", "reliability_score"]
            }
        },
        "dependencies": {
            "numpy": "required",
            "scikit_learn": "optional (for conformal prediction)",
            "deepxde": "optional (for PINN integration)",
            "tensorflow_pytorch": "optional (for dropout)"
        },
        "recommended_configs": {
            "fast_exploration": {
                "method": "monte_carlo_dropout",
                "num_samples": 100,
                "dropout_rate": 0.1
            },
            "high_precision": {
                "method": "ensemble",
                "ensemble_size": 10,
                "num_samples": 1000
            },
            "guaranteed_coverage": {
                "method": "conformal_prediction",
                "confidence_level": 0.9
            }
        }
    }
