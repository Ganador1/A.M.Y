"""
Training Metadata Model - AXIOM META 4
Pydantic v2 model for comprehensive training metadata and reproducibility tracking.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict, validator
from enum import Enum
import hashlib
import json


class TrainingStatus(str, Enum):
    """Status of training process"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DataSplit(BaseModel):
    """Information about data splits"""
    
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Split name (e.g., 'train', 'val', 'test')")
    size: int = Field(..., ge=0, description="Number of samples in split")
    hash_sha256: str = Field(..., description="SHA256 hash of the split data")
    stratified: bool = Field(default=False, description="Whether split was stratified")
    random_seed: Optional[int] = Field(None, description="Random seed used for splitting")


class HyperparameterConfig(BaseModel):
    """Hyperparameter configuration"""
    
    model_config = ConfigDict(extra="forbid")
    
    parameters: Dict[str, Any] = Field(..., description="Hyperparameter values")
    search_method: Optional[str] = Field(None, description="Search method used (grid, random, bayesian)")
    search_space: Optional[Dict[str, Any]] = Field(None, description="Search space definition")
    optimization_metric: Optional[str] = Field(None, description="Metric optimized during search")
    n_trials: Optional[int] = Field(None, ge=1, description="Number of trials in search")


class ResourceUsage(BaseModel):
    """Resource usage during training"""
    
    model_config = ConfigDict(extra="forbid")
    
    # Time metrics
    wall_time_seconds: float = Field(..., ge=0.0, description="Wall clock time in seconds")
    cpu_time_seconds: float = Field(..., ge=0.0, description="CPU time in seconds")
    
    # Memory metrics
    peak_memory_mb: Optional[float] = Field(None, ge=0.0, description="Peak memory usage in MB")
    avg_memory_mb: Optional[float] = Field(None, ge=0.0, description="Average memory usage in MB")
    
    # GPU metrics (if applicable)
    gpu_memory_mb: Optional[float] = Field(None, ge=0.0, description="GPU memory usage in MB")
    gpu_utilization_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="GPU utilization %")
    
    # Compute metrics
    cpu_cores_used: Optional[int] = Field(None, ge=1, description="Number of CPU cores used")
    gpu_count: Optional[int] = Field(None, ge=0, description="Number of GPUs used")


class ValidationMetrics(BaseModel):
    """Validation metrics during training"""
    
    model_config = ConfigDict(extra="forbid")
    
    # Core metrics
    primary_metric: float = Field(..., description="Primary optimization metric")
    primary_metric_name: str = Field(..., description="Name of primary metric")
    
    # Additional metrics
    metrics: Dict[str, float] = Field(default_factory=dict, description="Additional validation metrics")
    
    # Learning curves
    train_scores: Optional[List[float]] = Field(None, description="Training scores per epoch/iteration")
    val_scores: Optional[List[float]] = Field(None, description="Validation scores per epoch/iteration")
    
    # Early stopping
    best_epoch: Optional[int] = Field(None, ge=0, description="Best epoch/iteration")
    early_stopped: bool = Field(default=False, description="Whether training was early stopped")
    patience_used: Optional[int] = Field(None, ge=0, description="Patience epochs used")


class EnvironmentInfo(BaseModel):
    """Environment and dependency information"""
    
    model_config = ConfigDict(extra="forbid")
    
    # System info
    python_version: str = Field(..., description="Python version")
    platform: str = Field(..., description="Platform/OS information")
    hostname: Optional[str] = Field(None, description="Hostname where training ran")
    
    # Dependencies
    requirements_hash: Optional[str] = Field(None, description="Hash of requirements.txt")
    conda_env_hash: Optional[str] = Field(None, description="Hash of conda environment")
    pip_freeze: Optional[List[str]] = Field(None, description="Output of pip freeze")
    
    # Hardware
    cpu_info: Optional[str] = Field(None, description="CPU information")
    gpu_info: Optional[List[str]] = Field(None, description="GPU information")
    total_memory_gb: Optional[float] = Field(None, ge=0.0, description="Total system memory in GB")


class TrainingMetadata(BaseModel):
    """
    Comprehensive training metadata for reproducibility and tracking.
    Used in pipeline_metadata_v4.py for complete training lineage.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    # Core identification
    training_id: str = Field(..., description="Unique identifier for this training run")
    experiment_name: str = Field(..., description="Name of the experiment")
    run_name: str = Field(..., description="Name of this specific run")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Training start time")
    completed_at: Optional[datetime] = Field(None, description="Training completion time")
    
    # Status and progress
    status: TrainingStatus = Field(default=TrainingStatus.PENDING, description="Current training status")
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Training progress percentage")
    
    # Model and algorithm info
    model_type: str = Field(..., description="Type of model being trained")
    algorithm: str = Field(..., description="Training algorithm used")
    framework: str = Field(..., description="ML framework (sklearn, pytorch, etc.)")
    framework_version: str = Field(..., description="Framework version")
    
    # Data information
    data_splits: List[DataSplit] = Field(..., min_items=1, description="Information about data splits")
    total_samples: int = Field(..., ge=1, description="Total number of training samples")
    feature_count: int = Field(..., ge=1, description="Number of features")
    class_distribution: Optional[Dict[str, int]] = Field(None, description="Class distribution in training data")
    
    # Hyperparameters and configuration
    hyperparameters: HyperparameterConfig = Field(..., description="Hyperparameter configuration")
    
    # Performance and validation
    validation_metrics: Optional[ValidationMetrics] = Field(None, description="Validation metrics")
    cross_validation: Optional[Dict[str, Any]] = Field(None, description="Cross-validation results")
    
    # Resource usage
    resource_usage: Optional[ResourceUsage] = Field(None, description="Resource usage during training")
    
    # Environment and reproducibility
    environment: EnvironmentInfo = Field(..., description="Environment information")
    random_seed: int = Field(..., description="Random seed for reproducibility")
    git_commit: Optional[str] = Field(None, description="Git commit hash")
    git_branch: Optional[str] = Field(None, description="Git branch name")
    git_dirty: bool = Field(default=False, description="Whether git working directory was dirty")
    
    # Artifacts and outputs
    model_artifacts: List[str] = Field(default_factory=list, description="Paths to model artifacts")
    log_files: List[str] = Field(default_factory=list, description="Paths to log files")
    checkpoint_paths: List[str] = Field(default_factory=list, description="Paths to model checkpoints")
    
    # MLflow integration
    mlflow_run_id: Optional[str] = Field(None, description="MLflow run ID")
    mlflow_experiment_id: Optional[str] = Field(None, description="MLflow experiment ID")
    mlflow_tracking_uri: Optional[str] = Field(None, description="MLflow tracking URI")
    
    # Metadata and tags
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    notes: Optional[str] = Field(None, description="Human-readable notes")
    parent_run_id: Optional[str] = Field(None, description="Parent run ID for nested runs")
    
    def get_duration(self) -> Optional[timedelta]:
        """Get training duration if completed"""
        if self.completed_at and self.created_at:
            return self.completed_at - self.created_at
        return None
    
    def get_duration_seconds(self) -> Optional[float]:
        """Get training duration in seconds"""
        duration = self.get_duration()
        return duration.total_seconds() if duration else None
    
    def compute_metadata_hash(self) -> str:
        """Compute hash of metadata for integrity checking"""
        # Create a deterministic representation
        metadata_dict = {
            "training_id": self.training_id,
            "model_type": self.model_type,
            "algorithm": self.algorithm,
            "hyperparameters": self.hyperparameters.parameters,
            "random_seed": self.random_seed,
            "git_commit": self.git_commit,
            "data_splits": [
                {"name": split.name, "size": split.size, "hash": split.hash_sha256}
                for split in self.data_splits
            ]
        }
        
        # Sort keys for deterministic hashing
        metadata_json = json.dumps(metadata_dict, sort_keys=True)
        return hashlib.sha256(metadata_json.encode()).hexdigest()
    
    def is_reproducible(self) -> bool:
        """Check if training run has sufficient info for reproduction"""
        return all([
            self.random_seed is not None,
            self.git_commit is not None,
            not self.git_dirty,
            len(self.data_splits) > 0,
            all(split.hash_sha256 for split in self.data_splits)
        ])
    
    def to_mlflow_params(self) -> Dict[str, Any]:
        """Convert to MLflow parameters format"""
        params = {
            "model_type": self.model_type,
            "algorithm": self.algorithm,
            "framework": self.framework,
            "framework_version": self.framework_version,
            "random_seed": self.random_seed,
            "total_samples": self.total_samples,
            "feature_count": self.feature_count
        }
        
        # Add hyperparameters
        for key, value in self.hyperparameters.parameters.items():
            params[f"hp_{key}"] = value
        
        # Add environment info
        params["python_version"] = self.environment.python_version
        params["platform"] = self.environment.platform
        
        if self.git_commit:
            params["git_commit"] = self.git_commit
        if self.git_branch:
            params["git_branch"] = self.git_branch
        
        return params
    
    def to_mlflow_metrics(self) -> Dict[str, float]:
        """Convert to MLflow metrics format"""
        metrics = {}
        
        if self.validation_metrics:
            metrics[self.validation_metrics.primary_metric_name] = self.validation_metrics.primary_metric
            metrics.update(self.validation_metrics.metrics)
        
        if self.resource_usage:
            metrics["wall_time_seconds"] = self.resource_usage.wall_time_seconds
            metrics["cpu_time_seconds"] = self.resource_usage.cpu_time_seconds
            if self.resource_usage.peak_memory_mb:
                metrics["peak_memory_mb"] = self.resource_usage.peak_memory_mb
        
        duration = self.get_duration_seconds()
        if duration:
            metrics["training_duration_seconds"] = duration
        
        return metrics