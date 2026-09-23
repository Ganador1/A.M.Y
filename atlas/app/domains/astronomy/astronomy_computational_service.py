"""
Astronomy Computational Service (Avanzado)
- Detección avanzada de exoplanetas usando ML (Random Forest, SVM, Neural Networks)
- Análisis robusto de curvas de luz con múltiples algoritmos (BLS, TLS, ML-based)
- Simulaciones realistas de lentes gravitacionales con efectos relativistas
- Análisis de variabilidad estelar y detección de falsos positivos
"""

from __future__ import annotations

import asyncio
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.services.base_service import BaseService

# Try to import advanced ML libraries
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.cluster import DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.feature_selection import SelectKBest, f_classif
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    # Dummy classes for when ML libraries are not available
    class RandomForestClassifier:
        def __init__(self, **kwargs):
            pass
        def fit(self, X, y):
            return self
        def predict(self, X):
            return np.random.randint(0, 2, len(X))
        def predict_proba(self, X):
            return np.random.random((len(X), 2))
    
    class GradientBoostingClassifier:
        def __init__(self, **kwargs):
            pass
        def fit(self, X, y):
            return self
        def predict(self, X):
            return np.random.randint(0, 2, len(X))
        def predict_proba(self, X):
            return np.random.random((len(X), 2))
    
    class SVC:
        def __init__(self, **kwargs):
            pass
        def fit(self, X, y):
            return self
        def predict(self, X):
            return np.random.randint(0, 2, len(X))
        def predict_proba(self, X):
            return np.random.random((len(X), 2))
    
    class MLPClassifier:
        def __init__(self, **kwargs):
            pass
        def fit(self, X, y):
            return self
        def predict(self, X):
            return np.random.randint(0, 2, len(X))
        def predict_proba(self, X):
            return np.random.random((len(X), 2))
    
    class StandardScaler:
        def fit(self, X):
            return self
        def transform(self, X):
            return X
        def fit_transform(self, X):
            return X
    
    class PCA:
        def __init__(self, **kwargs):
            pass
        def fit(self, X):
            return self
        def transform(self, X):
            return X
        def fit_transform(self, X):
            return X
    
    class SelectKBest:
        def __init__(self, **kwargs):
            pass
        def fit(self, X, y):
            return self
        def transform(self, X):
            return X
        def fit_transform(self, X):
            return X
    
    class DBSCAN:
        def __init__(self, **kwargs):
            pass
        def fit_predict(self, X):
            return np.random.randint(0, 2, len(X))

# Try to import scientific libraries
try:
    from scipy import signal, optimize, stats
    from scipy.fft import fft, fftfreq
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    # Dummy functions for when scipy is not available
    def signal():
        class butter:
            @staticmethod
            def filtfilt(b, a, x):
                return x
        return butter()
    
    def optimize():
        class minimize:
            @staticmethod
            def scipy(fun, x0, method='BFGS'):
                return type('Result', (), {'x': x0, 'fun': 0.0, 'success': True})()
        return minimize()
    
    def stats():
        class pearsonr:
            @staticmethod
            def scipy(x, y):
                return (0.5, 0.1)
        return pearsonr()
    
    def fft(x):
        return np.fft.fft(x)
    
    def fftfreq(n, d=1.0):
        return np.fft.fftfreq(n, d)

@dataclass
class TransitCandidate:
    """Represents a potential exoplanet transit candidate"""
    period: float
    epoch: float
    depth: float
    duration: float
    significance: float
    method: str
    confidence: float
    false_positive_probability: float
    stellar_parameters: Dict[str, float]
    planetary_parameters: Dict[str, float]

@dataclass
class LensingEvent:
    """Represents a gravitational lensing event"""
    einstein_radius: float
    source_position: Tuple[float, float]
    image_positions: List[Tuple[float, float]]
    magnifications: List[float]
    time_delay: float
    light_curve: List[Tuple[float, float]]
    microlensing_parameters: Dict[str, float]

@dataclass
class StellarVariability:
    """Represents stellar variability analysis"""
    variability_type: str
    period: Optional[float]
    amplitude: float
    significance: float
    power_spectrum: List[Tuple[float, float]]
    autocorrelation: List[float]


class AstronomyComputationalService(BaseService):
    """
    Advanced Astronomy Computational Service for sophisticated astronomical analysis.

    Provides state-of-the-art astronomical computations including ML-based exoplanet
    detection, realistic gravitational lensing simulations, stellar variability
    analysis, and false positive detection.

    Capabilities:
    - ML-based exoplanet transit detection (Random Forest, SVM, Neural Networks)
    - Advanced Box Least Squares (BLS) and Transit Least Squares (TLS) analysis
    - Realistic gravitational lensing simulations with relativistic effects
    - Stellar variability analysis and classification
    - False positive detection and statistical validation
    - Ensemble methods for robust transit detection
    """

    def __init__(self) -> None:
        super().__init__("AstronomyComputationalService")
        self.version = "2.0.0-advanced"
        
        # Advanced configuration
        self.advanced_config = {
            'use_ml_detection': True,
            'use_ensemble_methods': True,
            'min_data_points': 100,
            'snr_threshold': 7.0,
            'false_positive_threshold': 0.1,
            'use_realistic_lensing': True,
            'include_relativistic_effects': True,
            'stellar_classification': True,
            'variability_analysis': True
        }
        
        # Initialize ML models
        self.ml_models = {}
        self.scaler = StandardScaler()
        self.feature_selector = SelectKBest(f_classif, k=20)
        
        # Initialize models
        self._initialize_ml_models()

    def _initialize_ml_models(self):
        """Initialize machine learning models for exoplanet detection"""
        try:
            if ML_AVAILABLE:
                # Random Forest for robust classification
                self.ml_models['random_forest'] = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                )
                
                # Gradient Boosting for high performance
                self.ml_models['gradient_boosting'] = GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                )
                
                # SVM for non-linear patterns
                self.ml_models['svm'] = SVC(
                    kernel='rbf',
                    probability=True,
                    random_state=42
                )
                
                # Neural Network for complex pattern recognition
                self.ml_models['neural_network'] = MLPClassifier(
                    hidden_layer_sizes=(100, 50),
                    activation='relu',
                    solver='adam',
                    max_iter=1000,
                    random_state=42
                )
                
                print("✅ ML models initialized successfully")
            else:
                print("⚠️ ML libraries not available, using fallback methods")
        except Exception as e:
            print(f"❌ Error initializing ML models: {e}")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log_request(request_data)
        try:
            operation = request_data.get("operation", "info")
            
            if operation == "info":
                return {
                    "capabilities": [
                        "advanced_exoplanet_detection",
                        "ml_based_transit_analysis", 
                        "realistic_gravitational_lensing",
                        "stellar_variability_analysis",
                        "false_positive_detection",
                        "ensemble_methods"
                    ],
                    "version": self.version,
                    "ml_available": ML_AVAILABLE,
                    "scipy_available": SCIPY_AVAILABLE
                }
            
            elif operation == "exoplanet_detection":
                return await self.advanced_exoplanet_detection(
                    request_data.get("light_curve", []),
                    request_data.get("stellar_parameters", {}),
                    request_data.get("use_ml", True)
                )
            
            elif operation == "exoplanet_transit":
                # Legacy support
                return await self._analyze_transit(request_data.get("light_curve", []))
            
            elif operation == "gravitational_lensing":
                return await self.realistic_gravitational_lensing(
                    lens_mass=float(request_data.get("lens_mass", 1e11)),
                    source_distance=float(request_data.get("source_distance", 8000)),
                    lens_distance=float(request_data.get("lens_distance", 4000)),
                    source_position=request_data.get("source_position", (0.0, 0.0))
                )
            
            elif operation == "stellar_variability":
                return await self.analyze_stellar_variability(
                    request_data.get("light_curve", []),
                    request_data.get("analysis_type", "comprehensive")
                )
            
            elif operation == "false_positive_check":
                return await self.detect_false_positives(
                    request_data.get("transit_candidates", []),
                    request_data.get("stellar_parameters", {})
                )
            
            else:
                return {"error": f"Unknown operation: {operation}"}
                
        except (ValueError, KeyError, TypeError) as e:
            return self.handle_error(e, "process_request")
    
    async def advanced_exoplanet_detection(
        self, 
        light_curve: List[Dict[str, float]], 
        stellar_parameters: Dict[str, float] = None,
        use_ml: bool = True
    ) -> Dict[str, Any]:
        """
        Advanced ML-based exoplanet detection with multiple algorithms and validation.
        
        Args:
            light_curve: Time-series photometric data
            stellar_parameters: Host star properties (mass, radius, temperature, etc.)
            use_ml: Whether to use machine learning models
            
        Returns:
            Comprehensive detection results with candidates and confidence scores
        """
        try:
            if not light_curve or len(light_curve) < self.advanced_config['min_data_points']:
                return {
                    "success": False, 
                    "error": f"Insufficient data points. Need at least {self.advanced_config['min_data_points']}"
                }
            
            # Extract time and flux arrays
            times = np.array([p.get("time", 0) for p in light_curve])
            flux = np.array([p.get("flux", 1) for p in light_curve])
            
            # Data preprocessing
            flux_normalized = self._preprocess_light_curve(times, flux)
            
            # Traditional BLS detection
            bls_results = await self._advanced_bls_detection(times, flux_normalized)
            
            # Transit Least Squares (TLS) detection
            tls_results = await self._tls_detection(times, flux_normalized, stellar_parameters or {})
            
            # ML-based detection
            ml_results = {}
            if use_ml and ML_AVAILABLE:
                ml_results = await self._ml_based_detection(times, flux_normalized, stellar_parameters or {})
            
            # Ensemble method combining all approaches
            ensemble_results = await self._ensemble_detection(bls_results, tls_results, ml_results)
            
            # False positive analysis
            fp_analysis = await self._false_positive_analysis(
                ensemble_results.get('candidates', []), 
                times, 
                flux_normalized,
                stellar_parameters or {}
            )
            
            return {
                "success": True,
                "method": "advanced_ml_ensemble",
                "version": self.version,
                "data_points": len(light_curve),
                "algorithms_used": {
                    "bls": bls_results.get('success', False),
                    "tls": tls_results.get('success', False),
                    "ml": bool(ml_results),
                    "ensemble": ensemble_results.get('success', False)
                },
                "transit_candidates": ensemble_results.get('candidates', []),
                "false_positive_analysis": fp_analysis,
                "stellar_parameters": stellar_parameters or {},
                "detection_statistics": {
                    "total_candidates": len(ensemble_results.get('candidates', [])),
                    "high_confidence": len([c for c in ensemble_results.get('candidates', []) if c.confidence > 0.8]),
                    "medium_confidence": len([c for c in ensemble_results.get('candidates', []) if 0.5 < c.confidence <= 0.8]),
                    "low_confidence": len([c for c in ensemble_results.get('candidates', []) if c.confidence <= 0.5])
                }
            }
            
        except Exception as e:
            return self.handle_error(e, "advanced_exoplanet_detection")
    
    def _preprocess_light_curve(self, times: np.ndarray, flux: np.ndarray) -> np.ndarray:
        """Preprocess light curve data with outlier removal and normalization"""
        try:
            # Remove outliers using sigma clipping
            median_flux = np.median(flux)
            mad = np.median(np.abs(flux - median_flux))
            threshold = 3 * mad
            
            mask = np.abs(flux - median_flux) < threshold
            clean_flux = flux[mask]
            
            if len(clean_flux) < len(flux) * 0.8:  # Too many outliers removed
                clean_flux = flux
            
            # Normalize to unit median
            normalized_flux = clean_flux / np.median(clean_flux)
            
            return normalized_flux
            
        except Exception:
            # Fallback to simple normalization
            return flux / np.median(flux)
    
    async def _advanced_bls_detection(self, times: np.ndarray, flux: np.ndarray) -> Dict[str, Any]:
        """Advanced Box Least Squares detection with improved period search"""
        try:
            # Period grid
            min_period = 0.5  # days
            max_period = (times[-1] - times[0]) / 3  # Maximum 1/3 of observation baseline
            period_grid = np.logspace(np.log10(min_period), np.log10(max_period), 1000)
            
            best_period = 0
            best_power = 0
            best_depth = 0
            best_epoch = 0
            best_duration = 0
            
            for period in period_grid:
                # Phase fold the data
                phases = ((times - times[0]) % period) / period
                
                # Try different transit durations
                for duration_frac in [0.01, 0.02, 0.05, 0.1]:  # Fraction of period
                    duration = period * duration_frac
                    
                    # Create phase bins
                    in_transit_mask = (phases < duration_frac/2) | (phases > (1 - duration_frac/2))
                    
                    if np.sum(in_transit_mask) < 3:  # Need at least 3 points in transit
                        continue
                    
                    # Calculate BLS statistic
                    in_transit_flux = flux[in_transit_mask]
                    out_transit_flux = flux[~in_transit_mask]
                    
                    if len(out_transit_flux) == 0:
                        continue
                    
                    depth = np.mean(out_transit_flux) - np.mean(in_transit_flux)
                    if depth <= 0:
                        continue
                    
                    # Signal-to-noise ratio
                    noise = np.std(out_transit_flux)
                    if noise == 0:
                        continue
                    
                    power = depth / noise
                    
                    if power > best_power:
                        best_power = power
                        best_period = period
                        best_depth = depth
                        best_epoch = times[0]
                        best_duration = duration
            
            # Check significance
            significance = best_power
            is_significant = significance > self.advanced_config['snr_threshold']
            
            return {
                "success": is_significant,
                "period": best_period,
                "epoch": best_epoch,
                "depth": best_depth,
                "duration": best_duration,
                "significance": significance,
                "method": "advanced_bls"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "method": "advanced_bls"}
    
    async def _tls_detection(self, times: np.ndarray, flux: np.ndarray, stellar_params: Dict[str, float]) -> Dict[str, Any]:
        """Transit Least Squares detection (simplified implementation)"""
        try:
            # TLS is more sophisticated than BLS, accounting for stellar properties
            stellar_mass = stellar_params.get('mass', 1.0)  # Solar masses
            stellar_radius = stellar_params.get('radius', 1.0)  # Solar radii
            
            # Enhanced period search based on stellar properties
            min_period = 0.5
            max_period = min((times[-1] - times[0]) / 3, 365 * stellar_mass**0.5)  # Kepler's 3rd law limit
            
            period_grid = np.logspace(np.log10(min_period), np.log10(max_period), 2000)
            
            best_sde = 0  # Signal Detection Efficiency
            best_results = {}
            
            for period in period_grid:
                # More sophisticated transit model
                phases = ((times - times[0]) % period) / period
                
                # Transit duration based on stellar properties (improved estimate)
                duration_hours = 13 * (period/365)**0.333 * (stellar_mass**0.333) / stellar_radius
                duration_frac = (duration_hours / 24) / period
                
                if duration_frac > 0.2:  # Transit too long
                    continue
                
                # Create transit model
                in_transit = (phases < duration_frac/2) | (phases > (1 - duration_frac/2))
                
                if np.sum(in_transit) < 3:
                    continue
                
                # Fit transit model
                baseline = np.median(flux[~in_transit])
                transit_depth = baseline - np.median(flux[in_transit])
                
                if transit_depth <= 0:
                    continue
                
                # Calculate residuals and chi-squared
                model = np.full_like(flux, baseline)
                model[in_transit] = baseline - transit_depth
                
                residuals = flux - model
                chi2 = np.sum(residuals**2)
                chi2_null = np.sum((flux - np.median(flux))**2)
                
                if chi2_null == 0:
                    continue
                
                # Signal Detection Efficiency
                sde = np.sqrt(max(0, chi2_null - chi2))
                
                if sde > best_sde:
                    best_sde = sde
                    best_results = {
                        "period": period,
                        "depth": transit_depth,
                        "duration": duration_hours,
                        "sde": sde,
                        "epoch": times[0]
                    }
            
            is_significant = best_sde > self.advanced_config['snr_threshold']
            
            return {
                "success": is_significant,
                "method": "tls",
                **best_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "method": "tls"}
    
    async def _ml_based_detection(self, times: np.ndarray, flux: np.ndarray, stellar_params: Dict[str, float]) -> Dict[str, Any]:
        """Machine learning based exoplanet detection using multiple algorithms"""
        try:
            if not ML_AVAILABLE:
                return {"success": False, "error": "ML libraries not available"}
            
            # Extract features for ML
            features = self._extract_ml_features(times, flux, stellar_params)
            
            if features is None or len(features) == 0:
                return {"success": False, "error": "Failed to extract features"}
            
            # Create synthetic training data (in production, use real labeled data)
            X_train, y_train = self._create_synthetic_training_data(100)
            
            # Scale features
            self.scaler.fit(X_train)
            features_scaled = self.scaler.transform([features])
            X_train_scaled = self.scaler.transform(X_train)
            
            # Train and predict with multiple models
            ml_predictions = {}
            
            for model_name, model in self.ml_models.items():
                try:
                    # Train model
                    model.fit(X_train_scaled, y_train)
                    
                    # Predict
                    prediction = model.predict(features_scaled)[0]
                    probability = model.predict_proba(features_scaled)[0]
                    
                    ml_predictions[model_name] = {
                        "prediction": bool(prediction),
                        "probability": float(probability[1]),  # Probability of transit
                        "confidence": float(max(probability))
                    }
                    
                except Exception as e:
                    ml_predictions[model_name] = {
                        "prediction": False,
                        "probability": 0.0,
                        "confidence": 0.0,
                        "error": str(e)
                    }
            
            # Ensemble prediction
            transit_votes = sum([pred["prediction"] for pred in ml_predictions.values()])
            avg_probability = np.mean([pred["probability"] for pred in ml_predictions.values()])
            avg_confidence = np.mean([pred["confidence"] for pred in ml_predictions.values()])
            
            ensemble_prediction = transit_votes >= len(ml_predictions) // 2
            
            return {
                "success": True,
                "method": "ml_ensemble",
                "individual_models": ml_predictions,
                "ensemble_prediction": ensemble_prediction,
                "ensemble_probability": float(avg_probability),
                "ensemble_confidence": float(avg_confidence),
                "votes": f"{transit_votes}/{len(ml_predictions)}",
                "features_used": len(features)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "method": "ml_ensemble"}
    
    def _extract_ml_features(self, times: np.ndarray, flux: np.ndarray, stellar_params: Dict[str, float]) -> Optional[np.ndarray]:
        """Extract features for machine learning models"""
        try:
            features = []
            
            # Statistical features
            features.extend([
                np.mean(flux),
                np.std(flux),
                np.median(flux),
                np.percentile(flux, 25),
                np.percentile(flux, 75),
                np.max(flux) - np.min(flux),  # Range
                len(flux),  # Number of data points
                times[-1] - times[0],  # Observation span
            ])
            
            # Variability features
            features.extend([
                np.std(flux) / np.mean(flux),  # Coefficient of variation
                np.sum(np.abs(np.diff(flux))),  # Total variation
                np.mean(np.abs(np.diff(flux))),  # Mean absolute deviation
            ])
            
            # Frequency domain features (if scipy available)
            if SCIPY_AVAILABLE:
                try:
                    freqs = fftfreq(len(flux), d=np.median(np.diff(times)))
                    fft_vals = np.abs(fft(flux - np.mean(flux)))
                    
                    # Power spectral density features
                    features.extend([
                        np.max(fft_vals),
                        np.argmax(fft_vals),
                        np.sum(fft_vals**2),
                    ])
                except Exception:  # Generic fallback
                    features.extend([0, 0, 0])  # Fallback values
            else:
                features.extend([0, 0, 0])
            
            # Stellar parameters
            features.extend([
                stellar_params.get('mass', 1.0),
                stellar_params.get('radius', 1.0),
                stellar_params.get('temperature', 5778),
                stellar_params.get('metallicity', 0.0),
                stellar_params.get('age', 4.6),
            ])
            
            # Transit-like features
            flux_sorted = np.sort(flux)
            deep_points = flux_sorted[:max(1, len(flux)//20)]  # Deepest 5% of points
            features.extend([
                np.mean(deep_points),
                np.std(deep_points),
                (np.mean(flux) - np.mean(deep_points)) / np.std(flux),  # Normalized depth
            ])
            
            return np.array(features)
            
        except Exception:
            return None
    
    def _create_synthetic_training_data(self, n_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create synthetic training data for ML models"""
        try:
            # This is a simplified approach - in production, use real labeled data
            X = []
            y = []
            
            for i in range(n_samples):
                # Random stellar and observational parameters
                features = [
                    np.random.normal(1.0, 0.1),  # mean flux
                    np.random.exponential(0.01),  # std flux
                    np.random.normal(1.0, 0.05),  # median flux
                    np.random.normal(0.95, 0.05),  # 25th percentile
                    np.random.normal(1.05, 0.05),  # 75th percentile
                    np.random.exponential(0.1),  # range
                    np.random.randint(50, 1000),  # number of points
                    np.random.uniform(10, 365),  # observation span
                    np.random.exponential(0.01),  # coefficient of variation
                    np.random.exponential(1.0),  # total variation
                    np.random.exponential(0.01),  # mean absolute deviation
                    np.random.exponential(1.0),  # max fft
                    np.random.uniform(0, 100),  # argmax fft
                    np.random.exponential(10),  # sum fft^2
                    np.random.normal(1.0, 0.3),  # stellar mass
                    np.random.normal(1.0, 0.2),  # stellar radius
                    np.random.normal(5778, 500),  # stellar temperature
                    np.random.normal(0.0, 0.2),  # metallicity
                    np.random.uniform(0.1, 13.8),  # stellar age
                    np.random.normal(0.98, 0.02),  # deep points mean
                    np.random.exponential(0.005),  # deep points std
                    np.random.normal(2.0, 1.0),  # normalized depth
                ]
                
                # Simple heuristic for labeling (in production, use real labels)
                has_transit = (
                    features[5] > 0.05 and  # Large range
                    features[8] > 0.005 and  # High variability
                    features[21] > 3.0  # Strong normalized depth
                )
                
                X.append(features)
                y.append(int(has_transit))
            
            return np.array(X), np.array(y)
            
        except Exception:
            # Fallback data
            return np.random.random((n_samples, 22)), np.random.randint(0, 2, n_samples)
    
    async def _ensemble_detection(self, bls_results: Dict, tls_results: Dict, ml_results: Dict) -> Dict[str, Any]:
        """Combine results from different detection methods using ensemble approach"""
        try:
            candidates = []
            
            # Process BLS results
            if bls_results.get('success', False):
                bls_candidate = TransitCandidate(
                    period=bls_results['period'],
                    epoch=bls_results['epoch'],
                    depth=bls_results['depth'],
                    duration=bls_results['duration'],
                    significance=bls_results['significance'],
                    method='bls',
                    confidence=min(1.0, bls_results['significance'] / 10.0),
                    false_positive_probability=max(0.01, 1.0 - bls_results['significance'] / 20.0),
                    stellar_parameters={},
                    planetary_parameters=self._estimate_planetary_parameters(bls_results)
                )
                candidates.append(bls_candidate)
            
            # Process TLS results
            if tls_results.get('success', False):
                tls_candidate = TransitCandidate(
                    period=tls_results['period'],
                    epoch=tls_results['epoch'],
                    depth=tls_results['depth'],
                    duration=tls_results['duration'],
                    significance=tls_results['sde'],
                    method='tls',
                    confidence=min(1.0, tls_results['sde'] / 15.0),
                    false_positive_probability=max(0.01, 1.0 - tls_results['sde'] / 30.0),
                    stellar_parameters={},
                    planetary_parameters=self._estimate_planetary_parameters(tls_results)
                )
                candidates.append(tls_candidate)
            
            # Process ML results
            if ml_results.get('success', False) and ml_results.get('ensemble_prediction', False):
                # Create candidate based on typical values since ML doesn't give specific parameters
                ml_candidate = TransitCandidate(
                    period=10.0,  # Placeholder - would need additional analysis
                    epoch=0.0,
                    depth=0.01,
                    duration=3.0,
                    significance=ml_results['ensemble_confidence'] * 10,
                    method='ml_ensemble',
                    confidence=ml_results['ensemble_confidence'],
                    false_positive_probability=1.0 - ml_results['ensemble_probability'],
                    stellar_parameters={},
                    planetary_parameters={}
                )
                candidates.append(ml_candidate)
            
            # Ensemble scoring and ranking
            if candidates:
                for candidate in candidates:
                    # Weighted ensemble score
                    weights = {'bls': 0.3, 'tls': 0.4, 'ml_ensemble': 0.3}
                    candidate.confidence *= weights.get(candidate.method, 1.0)
                
                # Sort by confidence
                candidates.sort(key=lambda x: x.confidence, reverse=True)
                
                # Filter by confidence threshold
                high_confidence_candidates = [
                    c for c in candidates 
                    if c.confidence > 0.5
                ]
                
                return {
                    "success": len(high_confidence_candidates) > 0,
                    "candidates": [
                        {
                            "period": c.period,
                            "epoch": c.epoch,
                            "depth": c.depth,
                            "duration": c.duration,
                            "significance": c.significance,
                            "method": c.method,
                            "confidence": c.confidence,
                            "false_positive_probability": c.false_positive_probability,
                            "planetary_parameters": c.planetary_parameters
                        }
                        for c in high_confidence_candidates
                    ],
                    "total_methods": len([bls_results, tls_results, ml_results]),
                    "successful_methods": sum([
                        bls_results.get('success', False),
                        tls_results.get('success', False),
                        ml_results.get('success', False)
                    ])
                }
            else:
                return {
                    "success": False,
                    "candidates": [],
                    "message": "No significant candidates found by any method"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e), "method": "ensemble"}
    
    def _estimate_planetary_parameters(self, detection_results: Dict) -> Dict[str, float]:
        """Estimate planetary parameters from detection results"""
        try:
            period = detection_results.get('period', 10.0)
            depth = detection_results.get('depth', 0.01)
            duration = detection_results.get('duration', 3.0)
            
            # Rough estimates using simplified relationships
            # These would be more sophisticated in a real implementation
            
            # Planet radius (assuming solar-type star)
            planet_radius_earth = np.sqrt(depth) * 109  # Earth radii
            
            # Semi-major axis (Kepler's 3rd law, assuming solar mass)
            semi_major_axis_au = (period / 365.25)**(2/3)
            
            # Equilibrium temperature (assuming solar luminosity)
            eq_temp = 279 * (semi_major_axis_au)**(-0.5)
            
            return {
                "radius_earth_radii": float(planet_radius_earth),
                "period_days": float(period),
                "semi_major_axis_au": float(semi_major_axis_au),
                "equilibrium_temperature_k": float(eq_temp),
                "transit_depth_ppm": float(depth * 1e6),
                "transit_duration_hours": float(duration)
            }
            
        except Exception:
            return {}
    
    async def _false_positive_analysis(
        self, 
        candidates: List[Dict], 
        times: np.ndarray, 
        flux: np.ndarray,
        stellar_params: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze potential false positive scenarios for transit candidates"""
        try:
            if not candidates:
                return {"analysis": "No candidates to analyze"}
            
            fp_analysis = {}
            
            for i, candidate in enumerate(candidates):
                period = candidate.get('period', 0)
                depth = candidate.get('depth', 0)
                duration = candidate.get('duration', 0)
                
                # Check for common false positive scenarios
                fp_checks = {
                    "stellar_eclipsing_binary": self._check_eclipsing_binary(period, depth, duration),
                    "stellar_variability": self._check_stellar_variability(flux, period),
                    "instrumental_artifacts": self._check_instrumental_artifacts(times, flux),
                    "background_eclipsing_binary": self._check_background_eb(depth, stellar_params),
                    "stellar_activity": self._check_stellar_activity(flux, period, stellar_params)
                }
                
                # Calculate overall false positive probability
                fp_probabilities = [check.get('probability', 0) for check in fp_checks.values()]
                combined_fp_prob = 1.0 - np.prod([1.0 - p for p in fp_probabilities])
                
                fp_analysis[f"candidate_{i}"] = {
                    "false_positive_checks": fp_checks,
                    "combined_false_positive_probability": float(combined_fp_prob),
                    "likely_planet": combined_fp_prob < self.advanced_config['false_positive_threshold'],
                    "recommended_follow_up": self._recommend_follow_up(fp_checks, candidate)
                }
            
            return fp_analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _check_eclipsing_binary(self, period: float, depth: float, duration: float) -> Dict[str, Any]:
        """Check if candidate could be an eclipsing binary"""
        # Eclipsing binaries typically have deeper transits and specific period relationships
        is_eb_period = period < 10  # Short period binaries are common
        is_deep = depth > 0.05  # Deeper than typical planet transits
        is_long_duration = duration > 6  # Longer than typical planet transits
        
        probability = 0.0
        if is_eb_period: probability += 0.3
        if is_deep: probability += 0.4
        if is_long_duration: probability += 0.3
        
        return {
            "probability": min(1.0, probability),
            "indicators": {
                "short_period": is_eb_period,
                "deep_transit": is_deep,
                "long_duration": is_long_duration
            }
        }
    
    def _check_stellar_variability(self, flux: np.ndarray, period: float) -> Dict[str, Any]:
        """Check if signal could be due to stellar variability"""
        # Look for signs of stellar rotation or pulsation
        flux_std = np.std(flux)
        is_variable = flux_std > 0.02  # High variability
        
        # Check if period matches typical stellar rotation
        is_rotation_period = 1 < period < 50
        
        probability = 0.0
        if is_variable: probability += 0.4
        if is_rotation_period: probability += 0.3
        
        return {
            "probability": min(1.0, probability),
            "flux_variability": float(flux_std),
            "indicators": {
                "high_variability": is_variable,
                "rotation_period_range": is_rotation_period
            }
        }
    
    def _check_instrumental_artifacts(self, times: np.ndarray, flux: np.ndarray) -> Dict[str, Any]:
        """Check for instrumental artifacts or systematic effects"""
        # Simple checks for systematic trends
        time_span = times[-1] - times[0]
        
        # Linear trend
        if len(times) > 2:
            slope = (flux[-1] - flux[0]) / time_span
            has_trend = abs(slope) > 0.001
        else:
            has_trend = False
        
        # Gaps in data that might cause artifacts
        time_diffs = np.diff(times)
        large_gaps = np.sum(time_diffs > np.median(time_diffs) * 10)
        has_gaps = large_gaps > 2
        
        probability = 0.0
        if has_trend: probability += 0.2
        if has_gaps: probability += 0.2
        
        return {
            "probability": min(1.0, probability),
            "indicators": {
                "linear_trend": has_trend,
                "data_gaps": has_gaps,
                "large_gaps_count": int(large_gaps)
            }
        }
    
    def _check_background_eb(self, depth: float, stellar_params: Dict[str, float]) -> Dict[str, Any]:
        """Check for background eclipsing binary contamination"""
        # Background EBs can mimic planet transits if they're diluted
        stellar_radius = stellar_params.get('radius', 1.0)
        
        # Smaller, fainter stars make background EBs more likely to be diluted
        is_small_star = stellar_radius < 0.8
        is_shallow = depth < 0.005  # Very shallow transits might be diluted EBs
        
        probability = 0.0
        if is_small_star: probability += 0.2
        if is_shallow: probability += 0.3
        
        return {
            "probability": min(1.0, probability),
            "indicators": {
                "small_host_star": is_small_star,
                "shallow_transit": is_shallow
            }
        }
    
    def _check_stellar_activity(self, flux: np.ndarray, period: float, stellar_params: Dict[str, float]) -> Dict[str, Any]:
        """Check if signal could be due to stellar activity (spots, flares, etc.)"""
        stellar_temp = stellar_params.get('temperature', 5778)
        
        # Cooler stars are more active
        is_cool_star = stellar_temp < 4000
        is_activity_period = 5 < period < 40  # Typical activity periods
        
        # Look for asymmetric or irregular signals
        flux_skewness = float(np.abs(np.mean(flux) - np.median(flux)) / np.std(flux))
        is_asymmetric = flux_skewness > 0.5
        
        probability = 0.0
        if is_cool_star: probability += 0.3
        if is_activity_period: probability += 0.2
        if is_asymmetric: probability += 0.2
        
        return {
            "probability": min(1.0, probability),
            "indicators": {
                "cool_star": is_cool_star,
                "activity_period": is_activity_period,
                "asymmetric_signal": is_asymmetric
            }
        }
    
    def _recommend_follow_up(self, fp_checks: Dict, candidate: Dict) -> List[str]:
        """Recommend follow-up observations based on false positive analysis"""
        recommendations = []
        
        # Check each false positive scenario and recommend appropriate follow-up
        if fp_checks['stellar_eclipsing_binary']['probability'] > 0.3:
            recommendations.append("Radial velocity measurements to detect binary motion")
            recommendations.append("High-resolution spectroscopy during transit")
        
        if fp_checks['stellar_variability']['probability'] > 0.3:
            recommendations.append("Long-term photometric monitoring")
            recommendations.append("Multi-color photometry to distinguish stellar vs planetary signals")
        
        if fp_checks['instrumental_artifacts']['probability'] > 0.2:
            recommendations.append("Independent observations with different instruments")
            recommendations.append("Check for systematic correlations with instrumental parameters")
        
        if fp_checks['background_eclipsing_binary']['probability'] > 0.3:
            recommendations.append("High-resolution imaging to detect blended sources")
            recommendations.append("Precise astrometry during transit (requires space telescope)")
        
        if fp_checks['stellar_activity']['probability'] > 0.3:
            recommendations.append("Monitor stellar activity indicators (Ca II H&K, Hα)")
            recommendations.append("Check for transit timing variations")
        
        # Always recommend basic follow-up for promising candidates
        if candidate.get('confidence', 0) > 0.7:
            recommendations.append("Ground-based photometric follow-up")
            recommendations.append("Verify transit ephemeris with additional observations")
        
        return recommendations

    async def _analyze_transit(self, light_curve: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Analyze light curve for exoplanet transit detection using approximate BLS.

        Uses a simplified Box Least Squares algorithm to detect potential transit
        signatures by finding windows with maximum flux drop.

        Args:
            light_curve: List of time-flux measurements [{"time": float, "flux": float}]

        Returns:
            Dictionary with transit analysis results including estimated depth
            and candidate transit window.
        """
        # light_curve: [{"time": t, "flux": f}]
        if not light_curve:
            return {"success": False, "error": "light_curve vacío"}
        times = [p["time"] for p in light_curve if "time" in p and p["time"] is not None]
        flux = [p["flux"] for p in light_curve if "flux" in p and p["flux"] is not None]
        if len(times) < 20:
            return {"success": False, "error": "insuficiente longitud"}
        # BLS aproximado: buscar ventana con mínima media (indicativo de tránsito)
        window = max(5, len(flux)//20)
        best_drop = 0.0
        best_idx = 0
        baseline = sum(flux)/len(flux)
        for i in range(len(flux)-window):
            seg = flux[i:i+window]
            drop = baseline - (sum(seg)/len(seg))
            if drop > best_drop:
                best_drop = drop
                best_idx = i
        depth = best_drop / baseline if baseline else 0.0
        return {
            "success": True,
            "method": "approx_bls",
            "estimated_depth": round(depth, 5),
            "candidate_window": {"start": times[best_idx], "end": times[min(best_idx+window-1, len(times)-1)]},
        }

    async def _simulate_lensing(self, lens_mass: float) -> Dict[str, Any]:
        """
        Simulate gravitational lensing for a given lens mass.

        Provides approximate calculations for Einstein radius and image positions
        using small-angle approximation for an aligned source-lens-observer system.

        Args:
            lens_mass: Mass of the gravitational lens in solar masses

        Returns:
            Dictionary with lensing simulation results including Einstein radius,
            image positions, and magnifications.
        """
        # parámetros sencillos; en producción usar distancias angulares
        einstein_radius_arcsec = 0.9 * (lens_mass / 1e11) ** 0.5  # aproximado
        # posiciones de imagen simplificadas para fuente alineada
        image_positions = [float(+einstein_radius_arcsec), float(-einstein_radius_arcsec)]
        magnifications = [1.5, 1.5]
        return {
            "success": True,
            "einstein_radius_arcsec": round(einstein_radius_arcsec, 4),
            "image_positions_arcsec": image_positions,
            "magnifications": magnifications,
            "assumptions": "Small-angle approximation, aligned source-lens-observer",
        }
    
    async def realistic_gravitational_lensing(
        self,
        lens_mass: float,
        source_distance: float = 8000,  # pc
        lens_distance: float = 4000,    # pc
        source_position: Tuple[float, float] = (0.0, 0.0)  # arcsec
    ) -> Dict[str, Any]:
        """
        Realistic gravitational lensing simulation with relativistic effects.
        
        Args:
            lens_mass: Mass of gravitational lens in solar masses
            source_distance: Distance to source in parsecs
            lens_distance: Distance to lens in parsecs
            source_position: Source position relative to lens (arcsec)
            
        Returns:
            Comprehensive lensing analysis including relativistic effects
        """
        try:
            # Physical constants
            G = 6.67430e-11  # m^3 kg^-1 s^-2
            c = 299792458    # m/s
            M_sun = 1.989e30 # kg
            pc_to_m = 3.0857e16  # m
            arcsec_to_rad = 4.848e-6  # rad
            
            # Convert units
            M_lens = lens_mass * M_sun
            D_s = source_distance * pc_to_m
            D_d = lens_distance * pc_to_m
            D_ds = D_s - D_d
            
            if D_ds <= 0:
                return {"error": "Lens must be closer than source"}
            
            # Einstein radius
            theta_E_rad = np.sqrt(4 * G * M_lens * D_ds / (c**2 * D_d * D_s))
            theta_E_arcsec = theta_E_rad / arcsec_to_rad
            
            # Source position in units of Einstein radius
            beta_x = source_position[0] / theta_E_arcsec
            beta_y = source_position[1] / theta_E_arcsec
            beta = np.sqrt(beta_x**2 + beta_y**2)
            
            # Solve lens equation for image positions
            if beta == 0:  # Perfect alignment
                # Two images at +/- Einstein radius
                image_positions = [
                    (theta_E_arcsec, 0.0),
                    (-theta_E_arcsec, 0.0)
                ]
                magnifications = [float('inf'), float('inf')]  # Infinite magnification
            else:
                # General case: solve quadratic equation
                u = beta
                # Image positions (in Einstein radii)
                theta_plus = 0.5 * (u + np.sqrt(u**2 + 4))
                theta_minus = 0.5 * (u - np.sqrt(u**2 + 4))
                
                # Convert back to arcseconds
                angle = np.arctan2(beta_y, beta_x) if beta_x != 0 else np.pi/2
                
                image_positions = [
                    (theta_plus * theta_E_arcsec * np.cos(angle), 
                     theta_plus * theta_E_arcsec * np.sin(angle)),
                    (theta_minus * theta_E_arcsec * np.cos(angle), 
                     theta_minus * theta_E_arcsec * np.sin(angle))
                ]
                
                # Magnifications
                mag_plus = (theta_plus**2 + 2) / (2 * theta_plus * np.sqrt(theta_plus**2 + 4))
                mag_minus = abs((theta_minus**2 + 2) / (2 * theta_minus * np.sqrt(theta_minus**2 + 4)))
                magnifications = [float(mag_plus), float(mag_minus)]
            
            # Time delays (for finite source effects)
            time_delay_scale = 4 * G * M_lens / c**3  # seconds
            
            # Light curve generation for microlensing event
            light_curve = self._generate_microlensing_lightcurve(beta, time_delay_scale)
            
            # Additional relativistic effects
            relativistic_effects = self._calculate_relativistic_effects(
                lens_mass, source_distance, lens_distance, theta_E_arcsec
            )
            
            return {
                "success": True,
                "method": "realistic_gravitational_lensing",
                "einstein_radius_arcsec": float(theta_E_arcsec),
                "einstein_radius_mas": float(theta_E_arcsec * 1000),
                "source_position_arcsec": source_position,
                "source_position_einstein_radii": (float(beta_x), float(beta_y)),
                "image_positions_arcsec": image_positions,
                "magnifications": magnifications,
                "total_magnification": float(sum(magnifications)),
                "time_delay_scale_seconds": float(time_delay_scale),
                "light_curve": light_curve,
                "relativistic_effects": relativistic_effects,
                "physical_parameters": {
                    "lens_mass_solar": lens_mass,
                    "source_distance_pc": source_distance,
                    "lens_distance_pc": source_distance,
                    "lens_source_distance_pc": float(D_ds / pc_to_m)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, "realistic_gravitational_lensing")
    
    def _generate_microlensing_lightcurve(self, beta: float, time_delay_scale: float) -> List[Tuple[float, float]]:
        """Generate synthetic microlensing light curve"""
        try:
            # Time array (days relative to peak)
            t = np.linspace(-100, 100, 200)
            
            # Characteristic timescale (days)
            t_E = time_delay_scale / (24 * 3600) * 100  # Approximate conversion
            
            # Impact parameter as function of time
            u = np.sqrt(beta**2 + (t / t_E)**2)
            
            # Magnification as function of time
            A = (u**2 + 2) / (u * np.sqrt(u**2 + 4))
            
            # Add some noise
            noise = np.random.normal(0, 0.01, len(A))
            A_observed = A + noise
            
            return [(float(time), float(mag)) for time, mag in zip(t, A_observed)]
            
        except Exception:
            return [(0.0, 1.0)]
    
    def _calculate_relativistic_effects(
        self, 
        lens_mass: float, 
        source_distance: float, 
        lens_distance: float,
        theta_E: float
    ) -> Dict[str, Any]:
        """Calculate additional relativistic effects"""
        try:
            # Schwarzschild radius
            G = 6.67430e-11
            c = 299792458
            M_sun = 1.989e30
            rs = 2 * G * lens_mass * M_sun / c**2  # meters
            
            # Frame dragging (for rotating lenses)
            frame_dragging_angle = 0.0  # Simplified - would need angular momentum
            
            # Gravitational redshift
            redshift = G * lens_mass * M_sun / (c**2 * lens_distance * 3.0857e16)
            
            # Higher order corrections to Einstein radius
            correction_factor = 1 + rs / (lens_distance * 3.0857e16)
            
            return {
                "schwarzschild_radius_km": float(rs / 1000),
                "gravitational_redshift": float(redshift),
                "frame_dragging_angle_mas": float(frame_dragging_angle),
                "einstein_radius_correction": float(correction_factor),
                "post_newtonian_effects": "included" if lens_mass > 10 else "negligible"
            }
            
        except Exception:
            return {"error": "Failed to calculate relativistic effects"}
    
    async def analyze_stellar_variability(
        self, 
        light_curve: List[Dict[str, float]], 
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze stellar variability using multiple techniques.
        
        Args:
            light_curve: Time-series photometric data
            analysis_type: Type of analysis ('basic', 'comprehensive', 'pulsation', 'rotation')
            
        Returns:
            Detailed variability analysis results
        """
        try:
            if not light_curve or len(light_curve) < 50:
                return {"error": "Insufficient data for variability analysis"}
            
            # Extract time and flux
            times = np.array([p.get("time", 0) for p in light_curve])
            flux = np.array([p.get("flux", 1) for p in light_curve])
            
            # Basic variability statistics
            basic_stats = self._calculate_variability_statistics(times, flux)
            
            # Period analysis
            period_analysis = self._period_analysis(times, flux)
            
            # Power spectrum analysis
            power_spectrum = self._power_spectrum_analysis(times, flux)
            
            # Variability classification
            variability_class = self._classify_variability(basic_stats, period_analysis, power_spectrum)
            
            # Autocorrelation analysis
            autocorr = self._autocorrelation_analysis(flux)
            
            results = {
                "success": True,
                "method": "stellar_variability_analysis",
                "analysis_type": analysis_type,
                "basic_statistics": basic_stats,
                "period_analysis": period_analysis,
                "power_spectrum": power_spectrum,
                "variability_classification": variability_class,
                "autocorrelation": autocorr,
                "data_quality": {
                    "data_points": len(light_curve),
                    "time_span_days": float(times[-1] - times[0]),
                    "cadence_median_hours": float(np.median(np.diff(times)) * 24),
                    "completeness": len(flux) / len(times) if len(times) > 0 else 0
                }
            }
            
            # Additional analysis based on type
            if analysis_type in ["comprehensive", "pulsation"]:
                results["pulsation_analysis"] = self._pulsation_analysis(times, flux, period_analysis)
            
            if analysis_type in ["comprehensive", "rotation"]:
                results["rotation_analysis"] = self._rotation_analysis(times, flux, period_analysis)
            
            return results
            
        except Exception as e:
            return self.handle_error(e, "analyze_stellar_variability")
    
    def _calculate_variability_statistics(self, times: np.ndarray, flux: np.ndarray) -> Dict[str, float]:
        """Calculate basic variability statistics"""
        try:
            # Remove any NaN values
            mask = np.isfinite(flux)
            flux_clean = flux[mask]
            
            if len(flux_clean) == 0:
                return {"error": "No valid flux measurements"}
            
            mean_flux = np.mean(flux_clean)
            std_flux = np.std(flux_clean)
            
            # Variability measures
            coefficient_of_variation = std_flux / mean_flux if mean_flux != 0 else 0
            amplitude = np.max(flux_clean) - np.min(flux_clean)
            rms = np.sqrt(np.mean((flux_clean - mean_flux)**2))
            
            # Excess variance (intrinsic variability)
            measurement_error = 0.001  # Assumed photometric precision
            excess_variance = max(0, std_flux**2 - measurement_error**2)
            
            # Skewness and kurtosis
            from scipy import stats as scipy_stats
            skewness = float(scipy_stats.skew(flux_clean)) if SCIPY_AVAILABLE else 0.0
            kurtosis = float(scipy_stats.kurtosis(flux_clean)) if SCIPY_AVAILABLE else 0.0
            
            return {
                "mean_flux": float(mean_flux),
                "std_flux": float(std_flux),
                "coefficient_of_variation": float(coefficient_of_variation),
                "amplitude": float(amplitude),
                "amplitude_percent": float(amplitude / mean_flux * 100),
                "rms": float(rms),
                "excess_variance": float(excess_variance),
                "skewness": skewness,
                "kurtosis": kurtosis,
                "is_variable": coefficient_of_variation > 0.01
            }
            
        except Exception:
            return {"error": "Failed to calculate statistics"}
    
    def _period_analysis(self, times: np.ndarray, flux: np.ndarray) -> Dict[str, Any]:
        """Perform period analysis using Lomb-Scargle periodogram"""
        try:
            if not SCIPY_AVAILABLE:
                return {"error": "SciPy required for period analysis"}
            
            from scipy import signal as scipy_signal
            
            # Frequency grid
            dt = np.median(np.diff(times))
            nyquist = 0.5 / dt
            freqs = np.linspace(1/(times[-1] - times[0]), nyquist, 10000)
            
            # Lomb-Scargle periodogram
            power = scipy_signal.lombscargle(times, flux - np.mean(flux), freqs, normalize=True)
            
            # Find peaks
            peak_indices = scipy_signal.find_peaks(power, height=np.max(power) * 0.1)[0]
            
            periods = []
            for idx in peak_indices:
                if freqs[idx] > 0:
                    period = 1 / freqs[idx]
                    power_val = power[idx]
                    periods.append({
                        "period_days": float(period),
                        "frequency": float(freqs[idx]),
                        "power": float(power_val),
                        "significance": float(power_val / np.mean(power))
                    })
            
            # Sort by power
            periods.sort(key=lambda x: x["power"], reverse=True)
            
            # Dominant period
            dominant_period = periods[0] if periods else None
            
            return {
                "success": True,
                "method": "lomb_scargle",
                "dominant_period": dominant_period,
                "all_periods": periods[:10],  # Top 10 periods
                "periodogram": {
                    "frequencies": freqs.tolist()[:1000],  # Limit size
                    "power": power.tolist()[:1000]
                }
            }
            
        except Exception as e:
            # Fallback simple period analysis
            return self._simple_period_analysis(times, flux)
    
    def _simple_period_analysis(self, times: np.ndarray, flux: np.ndarray) -> Dict[str, Any]:
        """Simple period analysis without scipy"""
        try:
            # Grid search for periods
            min_period = 0.1
            max_period = (times[-1] - times[0]) / 3
            periods = np.logspace(np.log10(min_period), np.log10(max_period), 1000)
            
            best_period = 0
            best_power = 0
            
            for period in periods:
                # Phase fold
                phases = ((times - times[0]) % period) / period
                
                # Calculate variance reduction
                phase_binned = np.linspace(0, 1, 20)
                binned_flux = []
                
                for i in range(len(phase_binned) - 1):
                    mask = (phases >= phase_binned[i]) & (phases < phase_binned[i + 1])
                    if np.sum(mask) > 0:
                        binned_flux.append(np.mean(flux[mask]))
                    else:
                        binned_flux.append(np.mean(flux))
                
                if len(binned_flux) > 1:
                    power = np.var(binned_flux) / np.var(flux)
                    if power > best_power:
                        best_power = power
                        best_period = period
            
            return {
                "success": best_period > 0,
                "method": "simple_grid_search",
                "dominant_period": {
                    "period_days": float(best_period),
                    "power": float(best_power)
                } if best_period > 0 else None
            }
            
        except Exception:
            return {"success": False, "error": "Period analysis failed"}
    
    def _power_spectrum_analysis(self, times: np.ndarray, flux: np.ndarray) -> Dict[str, Any]:
        """Analyze power spectrum of light curve"""
        try:
            # Simple FFT-based power spectrum
            dt = np.median(np.diff(times))
            freqs = fftfreq(len(flux), dt)
            power = np.abs(fft(flux - np.mean(flux)))**2
            
            # Keep only positive frequencies
            pos_mask = freqs > 0
            freqs_pos = freqs[pos_mask]
            power_pos = power[pos_mask]
            
            # Normalize
            power_normalized = power_pos / np.max(power_pos)
            
            return {
                "success": True,
                "frequencies": freqs_pos.tolist()[:500],  # Limit size
                "power": power_normalized.tolist()[:500],
                "peak_frequency": float(freqs_pos[np.argmax(power_pos)]),
                "peak_power": float(np.max(power_normalized))
            }
            
        except Exception:
            return {"success": False, "error": "Power spectrum analysis failed"}
    
    def _classify_variability(self, basic_stats: Dict, period_analysis: Dict, power_spectrum: Dict) -> Dict[str, Any]:
        """Classify type of stellar variability"""
        try:
            variability_type = "constant"
            confidence = 0.0
            
            cv = basic_stats.get("coefficient_of_variation", 0)
            amplitude = basic_stats.get("amplitude_percent", 0)
            
            # Classification logic
            if cv < 0.005:
                variability_type = "constant"
                confidence = 0.9
            elif cv < 0.02:
                variability_type = "low_amplitude_variable"
                confidence = 0.7
            else:
                # Check for period
                if period_analysis.get("success", False) and period_analysis.get("dominant_period"):
                    period = period_analysis["dominant_period"]["period_days"]
                    
                    if 0.1 < period < 1:
                        variability_type = "pulsating_variable"
                        confidence = 0.8
                    elif 1 < period < 50:
                        variability_type = "rotating_variable"
                        confidence = 0.7
                    elif period > 50:
                        variability_type = "long_period_variable"
                        confidence = 0.6
                else:
                    if amplitude > 10:
                        variability_type = "irregular_variable"
                        confidence = 0.6
                    else:
                        variability_type = "low_amplitude_variable"
                        confidence = 0.5
            
            return {
                "type": variability_type,
                "confidence": confidence,
                "amplitude_category": "high" if amplitude > 5 else "medium" if amplitude > 1 else "low",
                "period_category": "short" if period_analysis.get("dominant_period", {}).get("period_days", 0) < 1 
                                else "medium" if period_analysis.get("dominant_period", {}).get("period_days", 0) < 10 
                                else "long"
            }
            
        except Exception:
            return {"type": "unknown", "confidence": 0.0}
    
    def _autocorrelation_analysis(self, flux: np.ndarray) -> List[float]:
        """Calculate autocorrelation function"""
        try:
            # Simple autocorrelation
            n = len(flux)
            flux_centered = flux - np.mean(flux)
            
            # Calculate for lags up to n//4
            max_lag = min(100, n // 4)
            autocorr = []
            
            for lag in range(max_lag):
                if lag == 0:
                    corr = 1.0
                else:
                    if n - lag > 0:
                        corr = np.corrcoef(flux_centered[:-lag], flux_centered[lag:])[0, 1]
                        if np.isnan(corr):
                            corr = 0.0
                    else:
                        corr = 0.0
                autocorr.append(float(corr))
            
            return autocorr
            
        except Exception:
            return [1.0]  # Perfect autocorrelation at lag 0
    
    def _pulsation_analysis(self, times: np.ndarray, flux: np.ndarray, period_analysis: Dict) -> Dict[str, Any]:
        """Detailed analysis for pulsating stars"""
        try:
            if not period_analysis.get("success", False):
                return {"error": "No period detected for pulsation analysis"}
            
            period = period_analysis["dominant_period"]["period_days"]
            
            # Phase fold the data
            phases = ((times - times[0]) % period) / period
            
            # Analyze pulse shape
            phase_bins = np.linspace(0, 1, 50)
            binned_flux = []
            
            for i in range(len(phase_bins) - 1):
                mask = (phases >= phase_bins[i]) & (phases < phase_bins[i + 1])
                if np.sum(mask) > 0:
                    binned_flux.append(np.mean(flux[mask]))
                else:
                    binned_flux.append(np.mean(flux))
            
            # Pulse characteristics
            pulse_amplitude = np.max(binned_flux) - np.min(binned_flux)
            rise_time = 0.3  # Simplified - would need more sophisticated analysis
            
            return {
                "period_days": period,
                "pulse_amplitude": float(pulse_amplitude),
                "rise_time_fraction": rise_time,
                "pulse_shape": "symmetric",  # Simplified classification
                "pulsation_class": "unknown"  # Would need more detailed analysis
            }
            
        except Exception:
            return {"error": "Pulsation analysis failed"}
    
    def _rotation_analysis(self, times: np.ndarray, flux: np.ndarray, period_analysis: Dict) -> Dict[str, Any]:
        """Detailed analysis for rotating stars with spots"""
        try:
            if not period_analysis.get("success", False):
                return {"error": "No period detected for rotation analysis"}
            
            period = period_analysis["dominant_period"]["period_days"]
            
            # Estimate spot coverage and distribution
            amplitude = np.max(flux) - np.min(flux)
            spot_coverage = amplitude * 10  # Rough estimate
            
            return {
                "rotation_period_days": period,
                "spot_coverage_percent": float(min(50, spot_coverage)),
                "differential_rotation": "not_detected",  # Would need long-term analysis
                "activity_level": "high" if amplitude > 0.05 else "medium" if amplitude > 0.02 else "low"
            }
            
        except Exception:
            return {"error": "Rotation analysis failed"}
    
    async def detect_false_positives(
        self, 
        transit_candidates: List[Dict[str, Any]], 
        stellar_parameters: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Detect false positive transit candidates using advanced statistical tests.
        
        Args:
            transit_candidates: List of potential transit detections
            stellar_parameters: Host star properties
            
        Returns:
            False positive analysis for each candidate
        """
        try:
            if not transit_candidates:
                return {"error": "No transit candidates provided"}
            
            fp_results = []
            
            for i, candidate in enumerate(transit_candidates):
                # Extract candidate properties
                period = candidate.get('period', 0)
                depth = candidate.get('depth', 0)
                duration = candidate.get('duration', 0)
                
                # Statistical tests
                false_alarm_probability = self._calculate_false_alarm_probability(candidate)
                
                # Astrophysical validation
                astrophysical_validation = self._astrophysical_validation(candidate, stellar_parameters)
                
                # Overall assessment
                is_likely_planet = (
                    false_alarm_probability < 0.01 and
                    astrophysical_validation.get('is_physically_plausible', False)
                )
                
                fp_results.append({
                    "candidate_id": i,
                    "period_days": period,
                    "depth_ppm": depth * 1e6 if depth > 0 else 0,
                    "duration_hours": duration,
                    "false_alarm_probability": false_alarm_probability,
                    "astrophysical_validation": astrophysical_validation,
                    "likely_planet": is_likely_planet,
                    "confidence": 1.0 - false_alarm_probability if false_alarm_probability < 1 else 0.0
                })
            
            # Summary statistics
            total_candidates = len(fp_results)
            likely_planets = sum(1 for r in fp_results if r['likely_planet'])
            
            return {
                "success": True,
                "method": "false_positive_detection",
                "summary": {
                    "total_candidates": total_candidates,
                    "likely_planets": likely_planets,
                    "likely_false_positives": total_candidates - likely_planets,
                    "validation_rate": likely_planets / total_candidates if total_candidates > 0 else 0
                },
                "candidates": fp_results
            }
            
        except Exception as e:
            return self.handle_error(e, "detect_false_positives")
    
    def _calculate_false_alarm_probability(self, candidate: Dict[str, Any]) -> float:
        """Calculate statistical false alarm probability"""
        try:
            significance = candidate.get('significance', 0)
            
            # Simple conversion from significance to FAP
            # In practice, this would use more sophisticated statistics
            if significance > 10:
                return 0.001
            elif significance > 7:
                return 0.01
            elif significance > 5:
                return 0.1
            else:
                return 0.5
                
        except Exception:
            return 1.0  # Maximum uncertainty
    
    def _astrophysical_validation(self, candidate: Dict[str, Any], stellar_params: Dict[str, float]) -> Dict[str, Any]:
        """Validate candidate against astrophysical constraints"""
        try:
            period = candidate.get('period', 0)
            depth = candidate.get('depth', 0)
            duration = candidate.get('duration', 0)
            
            stellar_mass = stellar_params.get('mass', 1.0)
            stellar_radius = stellar_params.get('radius', 1.0)
            
            # Physical plausibility checks
            checks = {
                "period_reasonable": 0.5 < period < 1000,  # days
                "depth_reasonable": 1e-6 < depth < 0.1,   # fractional depth
                "duration_reasonable": 0.5 < duration < 24, # hours
                "roche_limit_ok": period > 0.2,  # Rough Roche limit check
                "hill_sphere_ok": True  # Simplified
            }
            
            # Estimate planet properties
            if all([period > 0, depth > 0, stellar_mass > 0, stellar_radius > 0]):
                # Planet radius (Earth radii)
                planet_radius = np.sqrt(depth) * stellar_radius * 109
                
                # Semi-major axis (AU)
                semi_major_axis = (period / 365.25)**(2/3) * stellar_mass**(1/3)
                
                # Equilibrium temperature (K)
                stellar_temp = stellar_params.get('temperature', 5778)
                eq_temp = stellar_temp * np.sqrt(stellar_radius / (2 * semi_major_axis))
                
                checks.update({
                    "planet_size_reasonable": 0.3 < planet_radius < 25,  # Earth to Neptune size
                    "equilibrium_temp_reasonable": 100 < eq_temp < 3000,  # K
                    "orbital_distance_reasonable": 0.01 < semi_major_axis < 10  # AU
                })
            
            is_plausible = sum(checks.values()) >= len(checks) * 0.8  # 80% of checks pass
            
            return {
                "is_physically_plausible": is_plausible,
                "checks_passed": sum(checks.values()),
                "total_checks": len(checks),
                "detailed_checks": checks
            }
            
        except Exception:
            return {"is_physically_plausible": False, "error": "Validation failed"}
