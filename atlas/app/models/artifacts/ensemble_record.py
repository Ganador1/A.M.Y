"""
Ensemble Record Model - AXIOM META 4
Pydantic v2 model for tracking ensemble models, calibration and performance metrics.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal, Union
from pydantic import BaseModel, Field, ConfigDict, validator
from enum import Enum
import json


class EnsembleMethod(str, Enum):
    """Methods for ensemble combination"""
    VOTING = "voting"
    WEIGHTED_AVERAGE = "weighted_average"
    STACKING = "stacking"
    BLENDING = "blending"
    BAYESIAN_AVERAGING = "bayesian_averaging"


class CalibrationMethod(str, Enum):
    """Calibration methods for probability outputs"""
    PLATT_SCALING = "platt_scaling"
    ISOTONIC_REGRESSION = "isotonic_regression"
    BETA_CALIBRATION = "beta_calibration"
    TEMPERATURE_SCALING = "temperature_scaling"


class ModelInfo(BaseModel):
    """Information about individual models in the ensemble"""
    
    model_config = ConfigDict(extra="forbid")
    
    model_id: str = Field(..., description="Unique identifier for the model")
    model_type: str = Field(..., description="Type of model (e.g., 'RandomForest', 'LogisticRegression')")
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight in ensemble")
    performance_score: float = Field(..., ge=0.0, le=1.0, description="Individual model performance")
    calibration_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Calibration quality score")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters")


class CalibrationMetrics(BaseModel):
    """Calibration quality metrics"""
    
    model_config = ConfigDict(extra="forbid")
    
    ece: float = Field(..., ge=0.0, le=1.0, description="Expected Calibration Error")
    brier_score: float = Field(..., ge=0.0, le=2.0, description="Brier Score")
    reliability: float = Field(..., ge=0.0, le=1.0, description="Reliability score")
    resolution: float = Field(..., ge=0.0, le=1.0, description="Resolution score")
    sharpness: float = Field(..., ge=0.0, le=1.0, description="Sharpness score")
    
    # Additional calibration metrics
    max_calibration_error: Optional[float] = Field(None, ge=0.0, le=1.0, description="Maximum calibration error")
    avg_calibration_error: Optional[float] = Field(None, ge=0.0, le=1.0, description="Average calibration error")


class PerformanceMetrics(BaseModel):
    """Performance metrics for the ensemble"""
    
    model_config = ConfigDict(extra="forbid")
    
    # Classification metrics
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Classification accuracy")
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="F1 score")
    
    # Ranking metrics
    roc_auc: float = Field(..., ge=0.0, le=1.0, description="ROC AUC score")
    pr_auc: float = Field(..., ge=0.0, le=1.0, description="Precision-Recall AUC")
    
    # Cross-validation metrics
    cv_mean: float = Field(..., description="Cross-validation mean score")
    cv_std: float = Field(..., ge=0.0, description="Cross-validation standard deviation")
    
    # Additional metrics
    log_loss: Optional[float] = Field(None, ge=0.0, description="Logarithmic loss")
    matthews_corr: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Matthews correlation coefficient")


class EnsembleRecord(BaseModel):
    """
    Record for tracking ensemble models, their calibration and performance.
    Used in pipeline_metadata_v4.py for reproducible ensemble training.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    # Core identification
    ensemble_id: str = Field(..., description="Unique identifier for this ensemble")
    name: str = Field(..., description="Human-readable name for the ensemble")
    version: str = Field(..., description="Version string (e.g., 'v1.2.0')")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    # Ensemble configuration
    ensemble_method: EnsembleMethod = Field(..., description="Method used for combining models")
    base_models: List[ModelInfo] = Field(..., min_items=2, description="Individual models in the ensemble")
    
    # Calibration information
    calibration_method: Optional[CalibrationMethod] = Field(None, description="Calibration method applied")
    calibration_metrics: Optional[CalibrationMetrics] = Field(None, description="Calibration quality metrics")
    is_calibrated: bool = Field(default=False, description="Whether ensemble is calibrated")
    
    # Performance metrics
    performance: PerformanceMetrics = Field(..., description="Ensemble performance metrics")
    
    # Training information
    training_dataset_hash: str = Field(..., description="Hash of training dataset")
    validation_dataset_hash: Optional[str] = Field(None, description="Hash of validation dataset")
    test_dataset_hash: Optional[str] = Field(None, description="Hash of test dataset")
    
    # Reproducibility
    random_seed: int = Field(..., description="Random seed for reproducibility")
    git_commit: Optional[str] = Field(None, description="Git commit hash")
    environment_hash: Optional[str] = Field(None, description="Environment/dependencies hash")
    
    # Metadata and lineage
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Ensemble hyperparameters")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    description: Optional[str] = Field(None, description="Human-readable description")
    
    # MLflow integration
    mlflow_run_id: Optional[str] = Field(None, description="MLflow run ID")
    mlflow_experiment_id: Optional[str] = Field(None, description="MLflow experiment ID")
    
    # Validation
    @validator('base_models')
    def validate_weights_sum_to_one(cls, v):
        """Ensure model weights sum to approximately 1.0"""
        if v:
            total_weight = sum(model.weight for model in v)
            if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
                raise ValueError(f"Model weights must sum to 1.0, got {total_weight}")
        return v
    
    def get_model_by_id(self, model_id: str) -> Optional[ModelInfo]:
        """Get model info by ID"""
        for model in self.base_models:
            if model.model_id == model_id:
                return model
        return None
    
    def get_weighted_performance(self) -> float:
        """Calculate weighted average performance of base models"""
        if not self.base_models:
            return 0.0
        
        weighted_sum = sum(model.performance_score * model.weight for model in self.base_models)
        return weighted_sum
    
    def is_well_calibrated(self, ece_threshold: float = 0.1) -> bool:
        """Check if ensemble is well calibrated based on ECE threshold"""
        if not self.calibration_metrics:
            return False
        return self.calibration_metrics.ece <= ece_threshold
    
    def to_mlflow_params(self) -> Dict[str, Any]:
        """Convert to MLflow parameters format"""
        params = {
            "ensemble_method": self.ensemble_method.value,
            "num_base_models": len(self.base_models),
            "is_calibrated": self.is_calibrated,
            "random_seed": self.random_seed
        }
        
        if self.calibration_method:
            params["calibration_method"] = self.calibration_method.value
        
        # Add base model info
        for i, model in enumerate(self.base_models):
            params[f"model_{i}_type"] = model.model_type
            params[f"model_{i}_weight"] = model.weight
        
        return params
    
    def to_mlflow_metrics(self) -> Dict[str, float]:
        """Convert to MLflow metrics format"""
        metrics = {
            "accuracy": self.performance.accuracy,
            "precision": self.performance.precision,
            "recall": self.performance.recall,
            "f1_score": self.performance.f1_score,
            "roc_auc": self.performance.roc_auc,
            "pr_auc": self.performance.pr_auc,
            "cv_mean": self.performance.cv_mean,
            "cv_std": self.performance.cv_std
        }
        
        if self.calibration_metrics:
            metrics.update({
                "ece": self.calibration_metrics.ece,
                "brier_score": self.calibration_metrics.brier_score,
                "reliability": self.calibration_metrics.reliability,
                "resolution": self.calibration_metrics.resolution,
                "sharpness": self.calibration_metrics.sharpness
            })
        
        return metrics