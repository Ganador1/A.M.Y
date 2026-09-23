"""
Anomaly Detection Service for PINN Solutions

This module implements advanced anomaly detection techniques for Physics-Informed
Neural Networks (PINN) to identify unusual patterns in model behavior, security
metrics, and prediction quality.

Key Features:
- Statistical anomaly detection (Z-score, Mahalanobis distance)
- Machine learning-based detection (Isolation Forest, One-Class SVM)
- Real-time monitoring and alerting
- Integration with uncertainty quantification and robustness metrics
- Automated threshold adaptation

Author: AXIOM Research Team
Date: September 2025
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from app.services.base_service import BaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies that can be detected"""
    STATISTICAL_OUTLIER = "statistical_outlier"
    PREDICTION_SPIKE = "prediction_spike"
    UNCERTAINTY_SPIKE = "uncertainty_spike"
    CONVERGENCE_FAILURE = "convergence_failure"
    BOUNDARY_VIOLATION = "boundary_violation"
    PHYSICAL_CONSTRAINT_VIOLATION = "physical_constraint_violation"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_METRIC_ANOMALY = "security_metric_anomaly"


class DetectionMethod(Enum):
    """Anomaly detection methods available"""
    Z_SCORE = "z_score"
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    MAHALANOBIS_DISTANCE = "mahalanobis_distance"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"
    AUTOENCODER = "autoencoder"


@dataclass
class AnomalyConfig:
    """Configuration for anomaly detection"""
    method: DetectionMethod = DetectionMethod.Z_SCORE
    threshold: float = 3.0  # Standard deviations for Z-score
    window_size: int = 100  # Rolling window size
    contamination: float = 0.1  # Expected proportion of anomalies
    min_samples: int = 50  # Minimum samples for training
    update_interval: int = 60  # Seconds between model updates
    alert_threshold: float = 0.8  # Threshold for triggering alerts
    adaptive_threshold: bool = True  # Whether to adapt thresholds


@dataclass
class AnomalyResult:
    """Result of anomaly detection"""
    timestamp: datetime
    anomaly_type: AnomalyType
    detection_method: DetectionMethod
    anomaly_score: float
    confidence: float
    affected_metrics: List[str]
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    recommendations: List[str]


@dataclass
class AnomalyMetrics:
    """Metrics for anomaly detection performance"""
    total_anomalies_detected: int
    false_positive_rate: float
    detection_accuracy: float
    average_response_time: float
    anomaly_types_distribution: Dict[str, int]


class StatisticalAnomalyDetector:
    """Statistical anomaly detection using Z-score and Mahalanobis distance"""

    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.baseline_stats = {}
        self.historical_data = []

    def fit(self, data: np.ndarray, labels: Optional[List[str]] = None) -> None:
        """Fit the detector on baseline data"""
        try:
            self.historical_data = data.tolist() if hasattr(data, 'tolist') else data

            # Calculate baseline statistics for each metric
            if labels:
                for i, label in enumerate(labels):
                    metric_data = data[:, i] if len(data.shape) > 1 else data
                    self.baseline_stats[label] = {
                        'mean': np.mean(metric_data),
                        'std': np.std(metric_data),
                        'median': np.median(metric_data),
                        'q25': np.percentile(metric_data, 25),
                        'q75': np.percentile(metric_data, 75)
                    }
            else:
                # Single metric case
                self.baseline_stats['default'] = {
                    'mean': np.mean(data),
                    'std': np.std(data),
                    'median': np.median(data),
                    'q25': np.percentile(data, 25),
                    'q75': np.percentile(data, 75)
                }

            logger.info(f"Statistical detector fitted on {len(data)} samples")

        except Exception as e:
            logger.error(f"Failed to fit statistical detector: {str(e)}")
            raise

    def detect(self, data: np.ndarray, labels: Optional[List[str]] = None) -> List[AnomalyResult]:
        """Detect anomalies in new data"""
        anomalies = []

        try:
            if not self.baseline_stats:
                raise ValueError("Detector must be fitted before detection")

            # Handle single metric vs multiple metrics
            if len(data.shape) == 1:
                data = data.reshape(-1, 1)
                labels = labels or ['default']

            for i, point in enumerate(data):
                for j, label in enumerate(labels or [f'metric_{k}' for k in range(data.shape[1])]):
                    value = point[j] if len(point.shape) > 0 else point

                    # Calculate Z-score
                    baseline = self.baseline_stats.get(label, self.baseline_stats.get('default', {}))
                    if not baseline:
                        continue

                    z_score = abs((value - baseline['mean']) / (baseline['std'] + 1e-10))

                    if z_score > self.config.threshold:
                        anomaly = AnomalyResult(
                            timestamp=datetime.now(),
                            anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                            detection_method=DetectionMethod.Z_SCORE,
                            anomaly_score=z_score,
                            confidence=min(z_score / (self.config.threshold * 2), 1.0),
                            affected_metrics=[label],
                            description=f"Statistical outlier detected in {label}: Z-score = {z_score:.2f}",
                            severity=self._calculate_severity(z_score),
                            recommendations=self._generate_recommendations(z_score, label)
                        )
                        anomalies.append(anomaly)

            return anomalies

        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return []

    def _calculate_severity(self, z_score: float) -> str:
        """Calculate anomaly severity based on Z-score"""
        if z_score > 5.0:
            return 'critical'
        elif z_score > 4.0:
            return 'high'
        elif z_score > 3.5:
            return 'medium'
        else:
            return 'low'

    def _generate_recommendations(self, z_score: float, metric: str) -> List[str]:
        """Generate recommendations based on anomaly severity"""
        recommendations = []

        if z_score > 5.0:
            recommendations.extend([
                f"Critical anomaly in {metric} - immediate investigation required",
                "Check system stability and data quality",
                "Consider model retraining or parameter adjustment"
            ])
        elif z_score > 4.0:
            recommendations.extend([
                f"High severity anomaly in {metric}",
                "Monitor closely for trend development",
                "Review recent changes to system configuration"
            ])
        elif z_score > 3.5:
            recommendations.extend([
                f"Medium severity anomaly in {metric}",
                "Add to monitoring watchlist",
                "Consider threshold adjustment if false positive"
            ])
        else:
            recommendations.extend([
                f"Low severity anomaly in {metric}",
                "Log for trend analysis",
                "Monitor for pattern development"
            ])

        return recommendations


class MLAnomalyDetector:
    """Machine learning-based anomaly detection"""

    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.model = None
        self.is_fitted = False

    def fit(self, data: np.ndarray, labels: Optional[List[str]] = None) -> None:
        """Fit the ML model on baseline data"""
        try:
            if len(data) < self.config.min_samples:
                raise ValueError(f"Need at least {self.config.min_samples} samples for training")

            if self.config.method == DetectionMethod.ISOLATION_FOREST:
                self._fit_isolation_forest(data)
            elif self.config.method == DetectionMethod.ONE_CLASS_SVM:
                self._fit_one_class_svm(data)
            else:
                raise ValueError(f"Unsupported ML method: {self.config.method}")

            self.is_fitted = True
            logger.info(f"ML detector fitted using {self.config.method.value} on {len(data)} samples")

        except Exception as e:
            logger.error(f"Failed to fit ML detector: {str(e)}")
            raise

    def _fit_isolation_forest(self, data: np.ndarray) -> None:
        """Fit Isolation Forest model"""
        try:
            from sklearn.ensemble import IsolationForest
            self.model = IsolationForest(
                contamination=self.config.contamination,
                random_state=42,
                n_estimators=100
            )
            self.model.fit(data)
        except ImportError:
            logger.warning("scikit-learn not available, using fallback")
            self.model = None

    def _fit_one_class_svm(self, data: np.ndarray) -> None:
        """Fit One-Class SVM model"""
        try:
            from sklearn.svm import OneClassSVM
            self.model = OneClassSVM(
                nu=self.config.contamination,
                kernel='rbf',
                gamma='auto'
            )
            self.model.fit(data)
        except ImportError:
            logger.warning("scikit-learn not available, using fallback")
            self.model = None

    def detect(self, data: np.ndarray, labels: Optional[List[str]] = None) -> List[AnomalyResult]:
        """Detect anomalies using ML model"""
        anomalies = []

        try:
            if not self.is_fitted or self.model is None:
                return []

            # Get anomaly scores
            if hasattr(self.model, 'decision_function'):
                scores = self.model.decision_function(data)
                predictions = self.model.predict(data)
            elif hasattr(self.model, 'score_samples'):
                scores = self.model.score_samples(data)
                predictions = self.model.predict(data)
            else:
                return []

            # Convert scores to anomaly scores (higher = more anomalous)
            if self.config.method == DetectionMethod.ISOLATION_FOREST:
                # Isolation Forest: negative scores are anomalies
                anomaly_scores = -scores
            else:
                # One-Class SVM: negative predictions are anomalies
                anomaly_scores = -np.minimum(scores, 0)

            # Find anomalies
            threshold = np.percentile(anomaly_scores, (1 - self.config.contamination) * 100)

            for i, (score, pred) in enumerate(zip(anomaly_scores, predictions)):
                if score > threshold or pred == -1:  # Anomaly detected
                    anomaly = AnomalyResult(
                        timestamp=datetime.now(),
                        anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                        detection_method=self.config.method,
                        anomaly_score=float(score),
                        confidence=min(score / (threshold * 1.5), 1.0),
                        affected_metrics=labels or [f'metric_{j}' for j in range(data.shape[1] if len(data.shape) > 1 else 1)],
                        description=f"ML anomaly detected: score = {score:.3f}",
                        severity=self._calculate_ml_severity(float(score), float(threshold)),
                        recommendations=["Investigate anomaly pattern", "Consider model retraining"]
                    )
                    anomalies.append(anomaly)

            return anomalies

        except Exception as e:
            logger.error(f"ML anomaly detection failed: {str(e)}")
            return []

    def _calculate_ml_severity(self, score: float, threshold: float) -> str:
        """Calculate severity for ML-based detection"""
        ratio = score / (threshold + 1e-10)
        if ratio > 2.0:
            return 'critical'
        elif ratio > 1.5:
            return 'high'
        elif ratio > 1.2:
            return 'medium'
        else:
            return 'low'


class AnomalyDetectionService(BaseService):
    """Main service for anomaly detection in PINN solutions"""

    def __init__(self):
        super().__init__("AnomalyDetectionService")
        self.statistical_detector = None
        self.ml_detector = None
        self.monitoring_active = False
        self.anomaly_history = []
        self.alerts = []
        self.metrics = AnomalyMetrics(0, 0.0, 0.0, 0.0, {})
        self.logger = logging.getLogger(__name__)

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process anomaly detection request

        Args:
            request_data: Configuration and data for anomaly detection
                - method: Detection method to use
                - data: Data to analyze for anomalies
                - labels: Metric labels (optional)
                - config: Additional configuration (optional)

        Returns:
            Dictionary with anomaly detection results
        """
        try:
            # Parse configuration
            config = AnomalyConfig()
            if 'config' in request_data:
                for key, value in request_data['config'].items():
                    if hasattr(config, key):
                        setattr(config, key, value)

            # Override method if specified
            if 'method' in request_data:
                config.method = DetectionMethod(request_data['method'])

            # Get data and labels
            data = np.array(request_data['data'])
            labels = request_data.get('labels', None)

            # Initialize detectors if needed
            await self._initialize_detectors(config)

            # Perform anomaly detection
            anomalies = await self._detect_anomalies(data, labels, config)

            # Update metrics
            self._update_metrics(anomalies)

            # Format response
            response = {
                'anomalies_detected': len(anomalies),
                'anomaly_details': [
                    {
                        'type': anomaly.anomaly_type.value,
                        'method': anomaly.detection_method.value,
                        'score': anomaly.anomaly_score,
                        'confidence': anomaly.confidence,
                        'severity': anomaly.severity,
                        'description': anomaly.description,
                        'recommendations': anomaly.recommendations,
                        'timestamp': anomaly.timestamp.isoformat()
                    }
                    for anomaly in anomalies
                ],
                'metrics': {
                    'total_anomalies': self.metrics.total_anomalies_detected,
                    'false_positive_rate': self.metrics.false_positive_rate,
                    'detection_accuracy': self.metrics.detection_accuracy,
                    'anomaly_types': self.metrics.anomaly_types_distribution
                },
                'status': 'success'
            }

            self.logger.info(f"Anomaly detection completed: {len(anomalies)} anomalies found")
            return response

        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'anomalies_detected': 0
            }

    async def _initialize_detectors(self, config: AnomalyConfig) -> None:
        """Initialize anomaly detectors"""
        try:
            # Initialize statistical detector
            if not self.statistical_detector:
                self.statistical_detector = StatisticalAnomalyDetector(config)

            # Initialize ML detector if needed
            if config.method in [DetectionMethod.ISOLATION_FOREST, DetectionMethod.ONE_CLASS_SVM]:
                if not self.ml_detector or self.ml_detector.config.method != config.method:
                    self.ml_detector = MLAnomalyDetector(config)

        except Exception as e:
            logger.error(f"Failed to initialize detectors: {str(e)}")
            raise

    async def _detect_anomalies(self, data: np.ndarray, labels: Optional[List[str]],
                               config: AnomalyConfig) -> List[AnomalyResult]:
        """Detect anomalies using configured methods"""
        all_anomalies = []

        try:
            # Statistical detection
            if self.statistical_detector:
                # Fit on historical data if available
                if len(self.anomaly_history) >= config.min_samples:
                    historical_data = np.array([a.anomaly_score for a in self.anomaly_history[-config.window_size:]])
                    if len(historical_data.shape) == 1:
                        historical_data = historical_data.reshape(-1, 1)
                    self.statistical_detector.fit(historical_data)

                # Detect anomalies
                stat_anomalies = self.statistical_detector.detect(data, labels)
                all_anomalies.extend(stat_anomalies)

            # ML-based detection
            if self.ml_detector and config.method in [DetectionMethod.ISOLATION_FOREST, DetectionMethod.ONE_CLASS_SVM]:
                # Fit on historical data if available
                if len(self.anomaly_history) >= config.min_samples:
                    historical_data = np.array([a.anomaly_score for a in self.anomaly_history[-config.window_size:]])
                    if len(historical_data.shape) == 1:
                        historical_data = historical_data.reshape(-1, 1)
                    self.ml_detector.fit(historical_data)

                # Detect anomalies
                ml_anomalies = self.ml_detector.detect(data, labels)
                all_anomalies.extend(ml_anomalies)

            # Store anomalies in history
            self.anomaly_history.extend(all_anomalies)

            # Keep only recent history
            if len(self.anomaly_history) > config.window_size * 2:
                self.anomaly_history = self.anomaly_history[-config.window_size:]

            return all_anomalies

        except Exception as e:
            logger.error(f"Anomaly detection process failed: {str(e)}")
            return []

    def _update_metrics(self, anomalies: List[AnomalyResult]) -> None:
        """Update anomaly detection metrics"""
        try:
            self.metrics.total_anomalies_detected += len(anomalies)

            # Update anomaly types distribution
            for anomaly in anomalies:
                anomaly_type = anomaly.anomaly_type.value
                if anomaly_type not in self.metrics.anomaly_types_distribution:
                    self.metrics.anomaly_types_distribution[anomaly_type] = 0
                self.metrics.anomaly_types_distribution[anomaly_type] += 1

        except Exception as e:
            logger.error(f"Failed to update metrics: {str(e)}")

    async def start_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start real-time anomaly monitoring"""
        try:
            if self.monitoring_active:
                return {'status': 'error', 'message': 'Monitoring already active'}

            self.monitoring_active = True

            # Start monitoring task
            monitoring_config = AnomalyConfig()
            if config:
                for key, value in config.items():
                    if hasattr(monitoring_config, key):
                        setattr(monitoring_config, key, value)

            # Run monitoring in background
            asyncio.create_task(self._monitoring_loop(monitoring_config))

            self.logger.info("Anomaly monitoring started")
            return {
                'status': 'success',
                'message': 'Anomaly monitoring started',
                'config': {
                    'method': monitoring_config.method.value,
                    'threshold': monitoring_config.threshold,
                    'update_interval': monitoring_config.update_interval
                }
            }

        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop real-time anomaly monitoring"""
        try:
            self.monitoring_active = False
            self.logger.info("Anomaly monitoring stopped")
            return {'status': 'success', 'message': 'Anomaly monitoring stopped'}

        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _monitoring_loop(self, config: AnomalyConfig) -> None:
        """Main monitoring loop for real-time anomaly detection"""
        try:
            while self.monitoring_active:
                # Simulate monitoring data (in real implementation, this would come from actual metrics)
                monitoring_data = np.random.normal(0, 1, (10, 5))  # 10 samples, 5 metrics

                # Detect anomalies
                anomalies = await self._detect_anomalies(monitoring_data, None, config)

                # Process alerts
                if anomalies:
                    await self._process_alerts(anomalies)

                # Wait for next update
                await asyncio.sleep(config.update_interval)

        except Exception as e:
            logger.error(f"Monitoring loop failed: {str(e)}")
            self.monitoring_active = False

    async def _process_alerts(self, anomalies: List[AnomalyResult]) -> None:
        """Process and handle anomaly alerts"""
        try:
            for anomaly in anomalies:
                if anomaly.confidence > 0.8:  # High confidence anomalies
                    alert = {
                        'timestamp': anomaly.timestamp,
                        'severity': anomaly.severity,
                        'description': anomaly.description,
                        'recommendations': anomaly.recommendations
                    }
                    self.alerts.append(alert)

                    # Log critical alerts
                    if anomaly.severity in ['high', 'critical']:
                        self.logger.warning(f"CRITICAL ANOMALY: {anomaly.description}")

        except Exception as e:
            logger.error(f"Failed to process alerts: {str(e)}")

    async def get_anomaly_report(self, time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """Generate anomaly detection report"""
        try:
            # Filter anomalies by time range
            if time_range:
                cutoff_time = datetime.now() - time_range
                filtered_anomalies = [a for a in self.anomaly_history if a.timestamp > cutoff_time]
            else:
                filtered_anomalies = self.anomaly_history

            # Generate report
            report = {
                'total_anomalies': len(filtered_anomalies),
                'anomaly_types': {},
                'severity_distribution': {},
                'recent_alerts': self.alerts[-10:],  # Last 10 alerts
                'metrics': {
                    'total_detected': self.metrics.total_anomalies_detected,
                    'false_positive_rate': self.metrics.false_positive_rate,
                    'detection_accuracy': self.metrics.detection_accuracy,
                    'average_response_time': self.metrics.average_response_time
                },
                'status': 'success'
            }

            # Anomaly type distribution
            for anomaly in filtered_anomalies:
                anomaly_type = anomaly.anomaly_type.value
                if anomaly_type not in report['anomaly_types']:
                    report['anomaly_types'][anomaly_type] = 0
                report['anomaly_types'][anomaly_type] += 1

                # Severity distribution
                severity = anomaly.severity
                if severity not in report['severity_distribution']:
                    report['severity_distribution'][severity] = 0
                report['severity_distribution'][severity] += 1

            return report

        except Exception as e:
            self.logger.error(f"Failed to generate report: {str(e)}")
            return {'status': 'error', 'error': str(e)}


# Export main service
__all__ = ['AnomalyDetectionService', 'AnomalyConfig', 'AnomalyResult', 'AnomalyType', 'DetectionMethod']
