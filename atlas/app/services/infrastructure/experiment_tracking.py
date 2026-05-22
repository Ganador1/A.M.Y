"""
Experiment Tracking Service for AXIOM
Tracks scientific experiments and their results for reproducibility
"""

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from dataclasses import dataclass, field

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.experiment_tracking_types import (
    ProcessRequestResult,
    StartExperimentResult,
    LogMetricResult,
    LogParameterResult,
    LogArtifactResult,
    EndExperimentResult,
    GetExperimentResult,
    ListExperimentsResult,
    CompareExperimentsResult,
)


@dataclass
class Experiment:
    """Scientific experiment representation"""
    experiment_id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    status: str = "running"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    run_id: Optional[str] = None


class ExperimentTrackingService(BaseService):
    """
    Service for tracking scientific experiments
    Provides experiment versioning, metrics tracking, and artifact management
    """

    def __init__(self):
        super().__init__("ExperimentTracking")
        self.client = MlflowClient()
        self.active_experiments: Dict[str, Experiment] = {}

        # Set MLflow tracking URI (can be configured via environment)
        mlflow.set_tracking_uri("file:./mlruns")  # Local tracking for now

        logger.info("✅ ExperimentTrackingService initialized with MLflow")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process experiment tracking requests"""
        try:
            action = request_data.get("action", "")

            if action == "start_experiment":
                return await self.start_experiment(request_data)
            elif action == "log_metric":
                return self.log_metric(request_data)
            elif action == "log_parameter":
                return self.log_parameter(request_data)
            elif action == "log_artifact":
                return self.log_artifact(request_data)
            elif action == "end_experiment":
                return self.end_experiment(request_data)
            elif action == "get_experiment":
                return self.get_experiment(request_data)
            elif action == "list_experiments":
                return self.list_experiments()
            elif action == "compare_experiments":
                return self.compare_experiments(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "start_experiment", "log_metric", "log_parameter",
                        "log_artifact", "end_experiment", "get_experiment",
                        "list_experiments", "compare_experiments"
                    ]
                }

        except BiologyError as e:
            return self.handle_error(e, "process_request")

    async def start_experiment(self, request_data: StartExperimentResult) -> StartExperimentResult:
        """Start a new scientific experiment"""
        try:
            experiment_name = request_data.get("name", "")
            description = request_data.get("description", "")
            parameters = request_data.get("parameters", {})
            tags = request_data.get("tags", {})

            if not experiment_name:
                return {
                    "success": False,
                    "error": "Experiment name is required"
                }

            # Ensure parameters and tags are dictionaries
            if not isinstance(parameters, dict):
                parameters = {}
            if not isinstance(tags, dict):
                tags = {}

            # Create MLflow experiment
            try:
                mlflow_experiment_id = mlflow.create_experiment(experiment_name)
            except mlflow.exceptions.MlflowException:
                # Experiment already exists
                mlflow_experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id

            # Start MLflow run
            with mlflow.start_run(experiment_id=mlflow_experiment_id) as run:
                run_id = run.info.run_id

                # Log initial parameters
                for key, value in parameters.items():
                    mlflow.log_param(key, value)

                # Log tags
                for key, value in tags.items():
                    mlflow.set_tag(key, value)

                # Create internal experiment object
                experiment = Experiment(
                    experiment_id=str(uuid.uuid4()),
                    name=experiment_name,
                    description=description,
                    parameters=parameters,
                    tags=tags,
                    run_id=run_id
                )

                self.active_experiments[experiment.experiment_id] = experiment

                logger.info(f"✅ Started experiment: {experiment_name} (ID: {experiment.experiment_id})")

                return {
                    "success": True,
                    "message": f"Experiment '{experiment_name}' started successfully",
                    "experiment_id": experiment.experiment_id,
                    "run_id": run_id,
                    "mlflow_experiment_id": mlflow_experiment_id
                }

        except BiologyError as e:
            return self.handle_error(e, "start_experiment")

    def log_metric(self, request_data: LogMetricResult) -> LogMetricResult:
        """Log a metric for an experiment"""
        try:
            experiment_id = request_data.get("experiment_id")
            metric_name = request_data.get("metric_name")
            metric_value = request_data.get("metric_value")
            step = request_data.get("step", 0)

            if not experiment_id or experiment_id not in self.active_experiments:
                return {
                    "success": False,
                    "error": f"Experiment {experiment_id} not found"
                }

            if not metric_name:
                return {
                    "success": False,
                    "error": "metric_name is required"
                }

            experiment = self.active_experiments[experiment_id]

            # Log to MLflow
            with mlflow.start_run(run_id=experiment.run_id):
                mlflow.log_metric(metric_name, metric_value, step=step)

            # Update internal tracking
            if "metrics" not in experiment.metrics:
                experiment.metrics["metrics"] = {}
            experiment.metrics["metrics"][metric_name] = metric_value

            logger.info(f"📊 Logged metric: {metric_name} = {metric_value} for experiment {experiment_id}")

            return {
                "success": True,
                "message": f"Metric '{metric_name}' logged successfully",
                "experiment_id": experiment_id,
                "metric_name": metric_name,
                "metric_value": metric_value
            }

        except BiologyError as e:
            return self.handle_error(e, "log_metric")

    def log_parameter(self, request_data: LogParameterResult) -> LogParameterResult:
        """Log a parameter for an experiment"""
        try:
            experiment_id = request_data.get("experiment_id")
            param_name = request_data.get("param_name")
            param_value = request_data.get("param_value")

            if not experiment_id or experiment_id not in self.active_experiments:
                return {
                    "success": False,
                    "error": f"Experiment {experiment_id} not found"
                }

            if not param_name:
                return {
                    "success": False,
                    "error": "param_name is required"
                }

            experiment = self.active_experiments[experiment_id]

            # Log to MLflow
            with mlflow.start_run(run_id=experiment.run_id):
                mlflow.log_param(param_name, param_value)

            # Update internal tracking
            experiment.parameters[param_name] = param_value

            logger.info(f"🔧 Logged parameter: {param_name} = {param_value} for experiment {experiment_id}")

            return {
                "success": True,
                "message": f"Parameter '{param_name}' logged successfully",
                "experiment_id": experiment_id,
                "param_name": param_name,
                "param_value": param_value
            }

        except BiologyError as e:
            return self.handle_error(e, "log_parameter")

    def log_artifact(self, request_data: LogArtifactResult) -> LogArtifactResult:
        """Log an artifact for an experiment"""
        try:
            experiment_id = request_data.get("experiment_id")
            artifact_path = request_data.get("artifact_path")
            artifact_name = request_data.get("artifact_name", "")

            if not experiment_id or experiment_id not in self.active_experiments:
                return {
                    "success": False,
                    "error": f"Experiment {experiment_id} not found"
                }

            if not artifact_path:
                return {
                    "success": False,
                    "error": "artifact_path is required"
                }

            experiment = self.active_experiments[experiment_id]

            # Log to MLflow
            with mlflow.start_run(run_id=experiment.run_id):
                mlflow.log_artifact(artifact_path, artifact_name or "artifacts")

            # Update internal tracking
            experiment.artifacts.append(artifact_path)

            logger.info(f"📎 Logged artifact: {artifact_path} for experiment {experiment_id}")

            return {
                "success": True,
                "message": f"Artifact '{artifact_path}' logged successfully",
                "experiment_id": experiment_id,
                "artifact_path": artifact_path
            }

        except BiologyError as e:
            return self.handle_error(e, "log_artifact")

    def end_experiment(self, request_data: EndExperimentResult) -> EndExperimentResult:
        """End an experiment"""
        try:
            experiment_id = request_data.get("experiment_id")
            status = request_data.get("status", "completed")

            if not experiment_id or experiment_id not in self.active_experiments:
                return {
                    "success": False,
                    "error": f"Experiment {experiment_id} not found"
                }

            experiment = self.active_experiments[experiment_id]

            # End MLflow run
            with mlflow.start_run(run_id=experiment.run_id):
                mlflow.set_tag("status", status)
                mlflow.end_run()

            # Update internal tracking
            experiment.status = status
            experiment.completed_at = datetime.now()

            logger.info(f"🏁 Ended experiment: {experiment_id} with status {status}")

            return {
                "success": True,
                "message": f"Experiment '{experiment.name}' ended successfully",
                "experiment_id": experiment_id,
                "status": status,
                "duration_seconds": (experiment.completed_at - experiment.created_at).total_seconds()
            }

        except BiologyError as e:
            return self.handle_error(e, "end_experiment")

    def get_experiment(self, request_data: GetExperimentResult) -> GetExperimentResult:
        """Get experiment details"""
        try:
            experiment_id = request_data.get("experiment_id")

            if not experiment_id or experiment_id not in self.active_experiments:
                return {
                    "success": False,
                    "error": f"Experiment {experiment_id} not found"
                }

            experiment = self.active_experiments[experiment_id]

            return {
                "success": True,
                "experiment": {
                    "experiment_id": experiment.experiment_id,
                    "name": experiment.name,
                    "description": experiment.description,
                    "parameters": experiment.parameters,
                    "metrics": experiment.metrics,
                    "artifacts": experiment.artifacts,
                    "tags": experiment.tags,
                    "status": experiment.status,
                    "created_at": experiment.created_at.isoformat(),
                    "completed_at": experiment.completed_at.isoformat() if experiment.completed_at else None,
                    "run_id": experiment.run_id
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "get_experiment")

    def list_experiments(self) -> ListExperimentsResult:
        """List all tracked experiments"""
        try:
            experiments = []
            for exp_id, experiment in self.active_experiments.items():
                experiments.append({
                    "experiment_id": exp_id,
                    "name": experiment.name,
                    "description": experiment.description,
                    "status": experiment.status,
                    "created_at": experiment.created_at.isoformat(),
                    "run_id": experiment.run_id
                })

            return {
                "success": True,
                "experiments": experiments,
                "total_count": len(experiments)
            }

        except BiologyError as e:
            return self.handle_error(e, "list_experiments")

    def compare_experiments(self, request_data: CompareExperimentsResult) -> CompareExperimentsResult:
        """Compare multiple experiments"""
        try:
            experiment_ids = request_data.get("experiment_ids", [])

            if not experiment_ids:
                return {
                    "success": False,
                    "error": "experiment_ids list is required"
                }

            comparisons = []
            for exp_id in experiment_ids:
                if exp_id in self.active_experiments:
                    experiment = self.active_experiments[exp_id]
                    comparisons.append({
                        "experiment_id": exp_id,
                        "name": experiment.name,
                        "parameters": experiment.parameters,
                        "metrics": experiment.metrics,
                        "status": experiment.status
                    })
                else:
                    comparisons.append({
                        "experiment_id": exp_id,
                        "error": "Experiment not found"
                    })

            return {
                "success": True,
                "comparisons": comparisons,
                "compared_count": len(comparisons)
            }

        except BiologyError as e:
            return self.handle_error(e, "compare_experiments")
