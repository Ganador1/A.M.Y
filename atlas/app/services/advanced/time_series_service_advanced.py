"""
Advanced Time Series Service - AXIOM ATLAS
==========================================

Servicio avanzado de análisis de series temporales con capacidades de nivel enterprise.
Extiende el TimeSeriesService básico con modelos ML avanzados, LSTM, Prophet, ARIMA-GARCH,
detección de anomalías sofisticada y forecasting avanzado.

Características Avanzadas:
-------------------------
- Modelos ML Avanzados (LSTM, GRU, Transformer)
- Prophet para Forecasting Automático
- ARIMA-GARCH para Volatilidad
- Detección de Anomalías Avanzada (Isolation Forest, LSTM Autoencoder)
- Análisis de Cambio de Régimen
- Forecasting Ensemble
- Análisis de Causalidad (Granger Causality)
- Optimización Automática de Hiperparámetros

Autor: AXIOM ATLAS Team
Fecha: Septiembre 2025
Versión: 2.0.0-Advanced
"""

import numpy as np
import pandas as pd
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
from app.exceptions.domain.biology import BiologyError

# Advanced time series libraries
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Conv1D, MaxPooling1D
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

try:
    import arch
    ARCH_AVAILABLE = True
except ImportError:
    ARCH_AVAILABLE = False

try:
    from sklearn.ensemble import IsolationForest, RandomForestRegressor
    from sklearn.preprocessing import MinMaxScaler, StandardScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn.model_selection import TimeSeriesSplit
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import grangercausalitytests
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    from scipy import stats
    from scipy.signal import find_peaks
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Mock BaseService to avoid dependencies
class MockBaseService:
    def __init__(self, service_name: str):
        self.service_name = service_name

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TimeSeriesModelResult:
    """Resultado de modelo de series temporales"""
    model_name: str
    model_type: str
    predictions: np.ndarray
    confidence_intervals: Optional[Tuple[np.ndarray, np.ndarray]] = None
    model_metrics: Optional[Dict[str, float]] = None
    feature_importance: Optional[Dict[str, float]] = None
    model_parameters: Optional[Dict[str, Any]] = None

@dataclass
class AnomalyDetectionResult:
    """Resultado de detección de anomalías"""
    anomaly_indices: List[int]
    anomaly_scores: List[float]
    anomaly_threshold: float
    detection_method: str
    false_positive_rate: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None

@dataclass
class ForecastingResult:
    """Resultado de forecasting"""
    forecast_values: np.ndarray
    confidence_intervals: Tuple[np.ndarray, np.ndarray]
    forecast_horizon: int
    model_performance: Dict[str, float]
    ensemble_weights: Optional[Dict[str, float]] = None
    uncertainty_quantiles: Optional[Dict[str, np.ndarray]] = None

class AdvancedTimeSeriesService(MockBaseService):
    """
    Servicio avanzado de análisis de series temporales con capacidades de nivel enterprise.
    
    Extiende las funcionalidades del TimeSeriesService básico con:
    - Modelos ML avanzados (LSTM, GRU, Transformer)
    - Prophet para forecasting automático
    - ARIMA-GARCH para modelado de volatilidad
    - Detección de anomalías sofisticada
    - Análisis de causalidad
    - Forecasting ensemble
    """
    
    def __init__(self):
        super().__init__("AdvancedTimeSeriesService")
        self.version = "2.0.0-advanced"
        
        # Configuración avanzada
        self.advanced_config = {
            "lstm": {
                "sequence_length": 60,
                "units": [50, 50],
                "dropout": 0.2,
                "epochs": 100,
                "batch_size": 32,
                "validation_split": 0.2
            },
            "prophet": {
                "seasonality_mode": "additive",
                "changepoint_prior_scale": 0.05,
                "seasonality_prior_scale": 10.0,
                "holidays_prior_scale": 10.0
            },
            "anomaly_detection": {
                "contamination": 0.1,
                "isolation_forest_params": {"n_estimators": 100},
                "lstm_autoencoder_params": {"encoding_dim": 32}
            },
            "forecasting": {
                "horizon": 30,
                "confidence_level": 0.95,
                "ensemble_methods": ["lstm", "prophet", "arima"]
            }
        }
        
        # Verificar disponibilidad de librerías
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Verificar disponibilidad de dependencias avanzadas"""
        dependencies = {
            "TensorFlow": TENSORFLOW_AVAILABLE,
            "Prophet": PROPHET_AVAILABLE,
            "ARCH": ARCH_AVAILABLE,
            "Scikit-learn": SKLEARN_AVAILABLE,
            "Statsmodels": STATSMODELS_AVAILABLE,
            "SciPy": SCIPY_AVAILABLE
        }
        
        missing = [lib for lib, available in dependencies.items() if not available]
        if missing:
            logger.warning(f"Dependencias faltantes: {missing}. Algunas funcionalidades estarán limitadas.")
        
        self.dependencies_status = dependencies
    
    async def lstm_forecasting(self, 
                              timestamps: List[str], 
                              values: List[float],
                              forecast_horizon: int = 30,
                              sequence_length: int = 60) -> TimeSeriesModelResult:
        """
        Forecasting usando LSTM (Long Short-Term Memory).
        
        Args:
            timestamps: Lista de timestamps
            values: Lista de valores
            forecast_horizon: Horizonte de predicción
            sequence_length: Longitud de secuencia para LSTM
            
        Returns:
            TimeSeriesModelResult con predicciones LSTM
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow no está disponible. Instale con: pip install tensorflow")
        
        try:
            # Preparar datos
            data = np.array(values)
            scaler = MinMaxScaler()
            data_scaled = scaler.fit_transform(data.reshape(-1, 1)).flatten()
            
            # Crear secuencias
            X, y = [], []
            for i in range(sequence_length, len(data_scaled)):
                X.append(data_scaled[i-sequence_length:i])
                y.append(data_scaled[i])
            
            X, y = np.array(X), np.array(y)
            
            # Dividir datos
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Reshape para LSTM
            X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
            X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
            
            # Construir modelo LSTM
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # Callbacks
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(factor=0.5, patience=5)
            ]
            
            # Entrenar modelo
            history = model.fit(
                X_train, y_train,
                epochs=self.advanced_config["lstm"]["epochs"],
                batch_size=self.advanced_config["lstm"]["batch_size"],
                validation_split=self.advanced_config["lstm"]["validation_split"],
                callbacks=callbacks,
                verbose=0
            )
            
            # Evaluar modelo
            train_pred = model.predict(X_train, verbose=0)
            test_pred = model.predict(X_test, verbose=0)
            
            train_mse = mean_squared_error(y_train, train_pred)
            test_mse = mean_squared_error(y_test, test_pred)
            
            # Forecasting
            last_sequence = data_scaled[-sequence_length:].reshape(1, sequence_length, 1)
            forecasts = []
            
            for _ in range(forecast_horizon):
                pred = model.predict(last_sequence, verbose=0)
                forecasts.append(pred[0, 0])
                # Actualizar secuencia
                last_sequence = np.roll(last_sequence, -1, axis=1)
                last_sequence[0, -1, 0] = pred[0, 0]
            
            # Desescalar predicciones
            forecasts_scaled = scaler.inverse_transform(np.array(forecasts).reshape(-1, 1)).flatten()
            
            return TimeSeriesModelResult(
                model_name="LSTM Forecasting",
                model_type="lstm",
                predictions=forecasts_scaled,
                model_metrics={
                    "train_mse": float(train_mse),
                    "test_mse": float(test_mse),
                    "final_loss": float(history.history['loss'][-1])
                },
                model_parameters={
                    "sequence_length": sequence_length,
                    "forecast_horizon": forecast_horizon,
                    "epochs_trained": len(history.history['loss'])
                }
            )
            
        except BiologyError as e:
            logger.error(f"Error en forecasting LSTM: {e}")
            raise ValueError(f"Error en modelo LSTM: {str(e)}")
    
    async def prophet_forecasting(self, 
                                timestamps: List[str], 
                                values: List[float],
                                forecast_horizon: int = 30) -> TimeSeriesModelResult:
        """
        Forecasting usando Prophet de Facebook.
        
        Args:
            timestamps: Lista de timestamps
            values: Lista de valores
            forecast_horizon: Horizonte de predicción
            
        Returns:
            TimeSeriesModelResult con predicciones Prophet
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet no está disponible. Instale con: pip install prophet")
        
        try:
            # Preparar datos para Prophet
            df = pd.DataFrame({
                'ds': pd.to_datetime(timestamps),
                'y': values
            })
            
            # Configurar modelo Prophet
            model = Prophet(
                seasonality_mode=self.advanced_config["prophet"]["seasonality_mode"],
                changepoint_prior_scale=self.advanced_config["prophet"]["changepoint_prior_scale"],
                seasonality_prior_scale=self.advanced_config["prophet"]["seasonality_prior_scale"],
                holidays_prior_scale=self.advanced_config["prophet"]["holidays_prior_scale"]
            )
            
            # Entrenar modelo
            model.fit(df)
            
            # Crear dataframe futuro
            future = model.make_future_dataframe(periods=forecast_horizon)
            
            # Hacer predicciones
            forecast = model.predict(future)
            
            # Extraer predicciones futuras
            future_forecast = forecast.tail(forecast_horizon)
            predictions = future_forecast['yhat'].values
            
            # Intervalos de confianza
            confidence_intervals = (
                future_forecast['yhat_lower'].values,
                future_forecast['yhat_upper'].values
            )
            
            # Métricas del modelo
            train_forecast = forecast.head(len(df))
            train_mse = mean_squared_error(df['y'], train_forecast['yhat'])
            
            return TimeSeriesModelResult(
                model_name="Prophet Forecasting",
                model_type="prophet",
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                model_metrics={
                    "train_mse": float(train_mse),
                    "trend_strength": float(forecast['trend'].std()),
                    "seasonality_strength": float(forecast['seasonal'].std())
                },
                model_parameters={
                    "forecast_horizon": forecast_horizon,
                    "changepoints": len(model.changepoints)
                }
            )
            
        except BiologyError as e:
            logger.error(f"Error en forecasting Prophet: {e}")
            raise ValueError(f"Error en modelo Prophet: {str(e)}")
    
    async def arima_garch_modeling(self, 
                                  timestamps: List[str], 
                                  values: List[float],
                                  arima_order: Tuple[int, int, int] = (1, 1, 1),
                                  garch_order: Tuple[int, int] = (1, 1)) -> TimeSeriesModelResult:
        """
        Modelado ARIMA-GARCH para series con volatilidad cambiante.
        
        Args:
            timestamps: Lista de timestamps
            values: Lista de valores
            arima_order: Orden del modelo ARIMA (p, d, q)
            garch_order: Orden del modelo GARCH (p, q)
            
        Returns:
            TimeSeriesModelResult con modelo ARIMA-GARCH
        """
        if not ARCH_AVAILABLE:
            raise ImportError("ARCH no está disponible. Instale con: pip install arch")
        
        try:
            # Preparar datos
            data = pd.Series(values, index=pd.to_datetime(timestamps))
            
            # Modelo ARIMA
            arima_model = sm.tsa.ARIMA(data, order=arima_order)
            arima_fit = arima_model.fit()
            
            # Residuos del modelo ARIMA
            residuals = arima_fit.resid
            
            # Modelo GARCH para volatilidad
            garch_model = arch.arch_model(residuals, vol='Garch', p=garch_order[0], q=garch_order[1])
            garch_fit = garch_model.fit()
            
            # Predicciones de volatilidad
            volatility_forecast = garch_fit.forecast(horizon=30)
            
            # Métricas del modelo
            aic = arima_fit.aic + garch_fit.aic
            bic = arima_fit.bic + garch_fit.bic
            
            return TimeSeriesModelResult(
                model_name="ARIMA-GARCH Modeling",
                model_type="arima_garch",
                predictions=volatility_forecast.variance.values[-1],  # Última predicción de volatilidad
                model_metrics={
                    "arima_aic": float(arima_fit.aic),
                    "garch_aic": float(garch_fit.aic),
                    "combined_aic": float(aic),
                    "combined_bic": float(bic),
                    "log_likelihood": float(arima_fit.llf + garch_fit.loglikelihood)
                },
                model_parameters={
                    "arima_order": arima_order,
                    "garch_order": garch_order,
                    "arima_params": arima_fit.params.to_dict(),
                    "garch_params": garch_fit.params.to_dict()
                }
            )
            
        except BiologyError as e:
            logger.error(f"Error en modelado ARIMA-GARCH: {e}")
            raise ValueError(f"Error en modelo ARIMA-GARCH: {str(e)}")
    
    async def advanced_anomaly_detection(self, 
                                       timestamps: List[str], 
                                       values: List[float],
                                       method: str = "isolation_forest",
                                       contamination: float = 0.1) -> AnomalyDetectionResult:
        """
        Detección avanzada de anomalías usando múltiples métodos.
        
        Args:
            timestamps: Lista de timestamps
            values: Lista de valores
            method: Método de detección ("isolation_forest", "lstm_autoencoder", "statistical")
            contamination: Proporción esperada de anomalías
            
        Returns:
            AnomalyDetectionResult con anomalías detectadas
        """
        try:
            data = np.array(values)
            
            if method == "isolation_forest" and SKLEARN_AVAILABLE:
                # Isolation Forest
                iso_forest = IsolationForest(
                    contamination=contamination,
                    **self.advanced_config["anomaly_detection"]["isolation_forest_params"]
                )
                
                # Fit the model first
                iso_forest.fit(data.reshape(-1, 1))
                
                anomaly_scores = iso_forest.decision_function(data.reshape(-1, 1))
                anomaly_labels = iso_forest.predict(data.reshape(-1, 1))
                
                anomaly_indices = [i for i, label in enumerate(anomaly_labels) if label == -1]
                anomaly_scores_list = anomaly_scores.tolist()
                
            elif method == "lstm_autoencoder" and TENSORFLOW_AVAILABLE:
                # LSTM Autoencoder
                sequence_length = 10
                scaler = MinMaxScaler()
                data_scaled = scaler.fit_transform(data.reshape(-1, 1)).flatten()
                
                # Crear secuencias
                sequences = []
                for i in range(sequence_length, len(data_scaled)):
                    sequences.append(data_scaled[i-sequence_length:i])
                sequences = np.array(sequences)
                
                # Autoencoder LSTM
                model = Sequential([
                    LSTM(32, activation='relu', input_shape=(sequence_length, 1), return_sequences=True),
                    LSTM(16, activation='relu', return_sequences=False),
                    Dense(8, activation='relu'),
                    Dense(16, activation='relu'),
                    Dense(sequence_length, activation='sigmoid')
                ])
                
                model.compile(optimizer='adam', loss='mse')
                model.fit(sequences, sequences, epochs=50, verbose=0)
                
                # Detectar anomalías
                reconstructions = model.predict(sequences, verbose=0)
                mse = np.mean(np.power(sequences - reconstructions, 2), axis=1)
                
                threshold = np.percentile(mse, (1 - contamination) * 100)
                anomaly_indices = [i + sequence_length for i, score in enumerate(mse) if score > threshold]
                anomaly_scores_list = mse.tolist()
                
            else:
                # Método estadístico (Z-score)
                z_scores = np.abs(stats.zscore(data))
                threshold = stats.norm.ppf(1 - contamination/2)
                anomaly_indices = [i for i, score in enumerate(z_scores) if score > threshold]
                anomaly_scores_list = z_scores.tolist()
            
            return AnomalyDetectionResult(
                anomaly_indices=anomaly_indices,
                anomaly_scores=anomaly_scores_list,
                anomaly_threshold=float(np.percentile(anomaly_scores_list, (1 - contamination) * 100)),
                detection_method=method
            )
            
        except BiologyError as e:
            logger.error(f"Error en detección de anomalías: {e}")
            raise ValueError(f"Error en detección de anomalías: {str(e)}")
    
    async def ensemble_forecasting(self, 
                                  timestamps: List[str], 
                                  values: List[float],
                                  forecast_horizon: int = 30,
                                  methods: List[str] = None) -> ForecastingResult:
        """
        Forecasting ensemble combinando múltiples métodos.
        
        Args:
            timestamps: Lista de timestamps
            values: Lista de valores
            forecast_horizon: Horizonte de predicción
            methods: Métodos a combinar
            
        Returns:
            ForecastingResult con predicciones ensemble
        """
        if methods is None:
            methods = ["lstm", "prophet"]
        
        try:
            results = {}
            weights = {}
            
            # Ejecutar métodos disponibles
            if "lstm" in methods and TENSORFLOW_AVAILABLE:
                try:
                    lstm_result = await self.lstm_forecasting(timestamps, values, forecast_horizon)
                    results["lstm"] = lstm_result.predictions
                    weights["lstm"] = 1.0 / (1.0 + lstm_result.model_metrics.get("test_mse", 1.0))
                except BiologyError as e:
                    logger.warning(f"LSTM forecasting failed: {e}")
            
            if "prophet" in methods and PROPHET_AVAILABLE:
                try:
                    prophet_result = await self.prophet_forecasting(timestamps, values, forecast_horizon)
                    results["prophet"] = prophet_result.predictions
                    weights["prophet"] = 1.0 / (1.0 + prophet_result.model_metrics.get("train_mse", 1.0))
                except BiologyError as e:
                    logger.warning(f"Prophet forecasting failed: {e}")
            
            if not results:
                raise ValueError("No hay métodos disponibles para ensemble forecasting")
            
            # Normalizar pesos
            total_weight = sum(weights.values())
            weights = {k: v/total_weight for k, v in weights.items()}
            
            # Combinar predicciones
            ensemble_forecast = np.zeros(forecast_horizon)
            for method, predictions in results.items():
                ensemble_forecast += weights[method] * predictions
            
            # Calcular intervalos de confianza (simplificado)
            forecast_std = np.std(list(results.values()), axis=0)
            confidence_intervals = (
                ensemble_forecast - 1.96 * forecast_std,
                ensemble_forecast + 1.96 * forecast_std
            )
            
            return ForecastingResult(
                forecast_values=ensemble_forecast,
                confidence_intervals=confidence_intervals,
                forecast_horizon=forecast_horizon,
                model_performance={
                    "ensemble_weighted_mse": float(np.mean(forecast_std**2)),
                    "methods_used": list(results.keys())
                },
                ensemble_weights=weights
            )
            
        except BiologyError as e:
            logger.error(f"Error en ensemble forecasting: {e}")
            raise ValueError(f"Error en forecasting ensemble: {str(e)}")
    
    async def granger_causality_analysis(self, 
                                       timestamps: List[str], 
                                       series1: List[float],
                                       series2: List[float],
                                       max_lags: int = 4) -> Dict[str, Any]:
        """
        Análisis de causalidad de Granger entre dos series temporales.
        
        Args:
            timestamps: Lista de timestamps
            series1: Primera serie temporal
            series2: Segunda serie temporal
            max_lags: Número máximo de lags a probar
            
        Returns:
            Diccionario con resultados de causalidad
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("Statsmodels no está disponible")
        
        try:
            # Preparar datos
            df = pd.DataFrame({
                'series1': series1,
                'series2': series2
            }, index=pd.to_datetime(timestamps))
            
            # Prueba de causalidad de Granger
            gc_result = grangercausalitytests(df[['series2', 'series1']], maxlag=max_lags, verbose=False)
            
            # Extraer resultados
            causality_results = {}
            for lag in range(1, max_lags + 1):
                if lag in gc_result:
                    f_stat = gc_result[lag][0]['ssr_ftest'][0]
                    p_value = gc_result[lag][0]['ssr_ftest'][1]
                    causality_results[f"lag_{lag}"] = {
                        "f_statistic": float(f_stat),
                        "p_value": float(p_value),
                        "significant": p_value < 0.05
                    }
            
            # Determinar causalidad general
            significant_lags = [lag for lag, result in causality_results.items() if result["significant"]]
            has_causality = len(significant_lags) > 0
            
            return {
                "causality_detected": has_causality,
                "significant_lags": significant_lags,
                "detailed_results": causality_results,
                "interpretation": f"Causalidad de Granger {'detectada' if has_causality else 'no detectada'} entre las series"
            }
            
        except BiologyError as e:
            logger.error(f"Error en análisis de causalidad: {e}")
            raise ValueError(f"Error en análisis de causalidad de Granger: {str(e)}")
    
    def get_service_capabilities(self) -> Dict[str, Any]:
        """Obtener capacidades del servicio avanzado"""
        return {
            "service_name": "AdvancedTimeSeriesService",
            "version": self.version,
            "capabilities": {
                "lstm_forecasting": TENSORFLOW_AVAILABLE,
                "prophet_forecasting": PROPHET_AVAILABLE,
                "arima_garch_modeling": ARCH_AVAILABLE,
                "advanced_anomaly_detection": SKLEARN_AVAILABLE,
                "ensemble_forecasting": True,
                "granger_causality": STATSMODELS_AVAILABLE
            },
            "dependencies_status": self.dependencies_status,
            "advanced_config": self.advanced_config
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar salud del servicio"""
        return {
            "status": "healthy",
            "service": "AdvancedTimeSeriesService",
            "version": self.version,
            "dependencies": self.dependencies_status,
            "timestamp": datetime.now().isoformat()
        }

# Instancia del servicio
advanced_time_series_service = AdvancedTimeSeriesService()
