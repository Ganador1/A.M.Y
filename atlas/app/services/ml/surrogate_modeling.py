"""
Surrogate Modeling Service for AXIOM
Implements surrogate models for expensive simulations and function approximations
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.surrogate_modeling_types import (
    ProcessRequestResult,
    CreateModelResult,
    TrainModelResult,
    PredictResult,
    BatchPredictResult,
    GetModelInfoResult,
    EvaluateModelResult,
    UpdateModelResult,
    CreateSurrogateForSimulationResult,
)


@dataclass
class SurrogateModel:
    """Surrogate model instance"""
    model_id: str
    model_type: str = "gaussian_process"  # gaussian_process, random_forest, neural_network
    input_dimensions: int = 0
    trained: bool = False
    training_data_size: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    # Model components
    scaler: Optional[StandardScaler] = None
    model: Optional[Any] = None

    # Training data
    X_train: Optional[np.ndarray] = None
    y_train: Optional[np.ndarray] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_trained: Optional[datetime] = None


@dataclass
class PredictionResult:
    """Result of a surrogate model prediction"""
    prediction: float
    uncertainty: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    model_type: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class SurrogateModelingService(BaseService):
    """
    Service for creating and using surrogate models to approximate expensive functions
    Supports Gaussian Processes, Random Forests, and Neural Networks
    """

    def __init__(self):
        super().__init__("SurrogateModeling")
        self.models: Dict[str, SurrogateModel] = {}
        self.model_history: Dict[str, List[Dict[str, Any]]] = {}

        logger.info("✅ SurrogateModelingService initialized")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process surrogate modeling requests"""
        try:
            action = request_data.get("action", "")

            if action == "create_model":
                return await self.create_model(request_data)
            elif action == "train_model":
                return await self.train_model(request_data)
            elif action == "predict":
                return await self.predict(request_data)
            elif action == "batch_predict":
                return await self.batch_predict(request_data)
            elif action == "get_model_info":
                return self.get_model_info(request_data)
            elif action == "evaluate_model":
                return await self.evaluate_model(request_data)
            elif action == "update_model":
                return await self.update_model(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "create_model", "train_model", "predict", "batch_predict",
                        "get_model_info", "evaluate_model", "update_model"
                    ]
                }

        except BiologyError as e:
            return self.handle_error(e, "process_request")

    async def create_model(self, request_data: CreateModelResult) -> CreateModelResult:
        """Create a new surrogate model"""
        try:
            import uuid

            model_id = str(uuid.uuid4())
            model_type = request_data.get("model_type", "gaussian_process")
            input_dimensions = request_data.get("input_dimensions", 1)

            if model_type not in ["gaussian_process", "random_forest", "neural_network"]:
                return {
                    "success": False,
                    "error": f"Unsupported model type: {model_type}",
                    "supported_types": ["gaussian_process", "random_forest", "neural_network"]
                }

            model = SurrogateModel(
                model_id=model_id,
                model_type=model_type,
                input_dimensions=input_dimensions,
                trained=False
            )

            self.models[model_id] = model

            logger.info(f"✅ Created surrogate model: {model_id} ({model_type})")

            return {
                "success": True,
                "message": f"Surrogate model created successfully ({model_type})",
                "model_id": model_id,
                "model_type": model_type,
                "input_dimensions": input_dimensions
            }

        except BiologyError as e:
            return self.handle_error(e, "create_model")

    async def train_model(self, request_data: TrainModelResult) -> TrainModelResult:
        """Train a surrogate model with data"""
        try:
            model_id = request_data.get("model_id")
            X_data = request_data.get("X_data", [])
            y_data = request_data.get("y_data", [])

            if not model_id or model_id not in self.models:
                return {
                    "success": False,
                    "error": f"Model {model_id} not found"
                }

            if not X_data or not y_data:
                return {
                    "success": False,
                    "error": "Training data (X_data and y_data) is required"
                }

            if len(X_data) != len(y_data):
                return {
                    "success": False,
                    "error": "X_data and y_data must have the same length"
                }

            model = self.models[model_id]

            # Convert to numpy arrays
            X = np.array(X_data)
            y = np.array(y_data)

            # Validate dimensions
            if X.shape[1] != model.input_dimensions:
                return {
                    "success": False,
                    "error": f"Input data has {X.shape[1]} dimensions, but model expects {model.input_dimensions}"
                }

            # Scale the data
            model.scaler = StandardScaler()
            X_scaled = model.scaler.fit_transform(X)

            # Create and train the model
            if model.model_type == "gaussian_process":
                model.model = self._create_gaussian_process()
            elif model.model_type == "random_forest":
                model.model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif model.model_type == "neural_network":
                model.model = MLPRegressor(hidden_layer_sizes=(50, 50), max_iter=1000, random_state=42)

            # Train the model
            model.model.fit(X_scaled, y)

            # Store training data
            model.X_train = X
            model.y_train = y
            model.trained = True
            model.training_data_size = len(X)
            model.last_trained = datetime.now()

            # Calculate basic performance metrics
            model.performance_metrics = await self._calculate_performance_metrics(model, X_scaled, y)

            logger.info(f"✅ Trained surrogate model: {model_id} with {len(X)} samples")

            return {
                "success": True,
                "message": f"Model trained successfully with {len(X)} samples",
                "model_id": model_id,
                "training_samples": len(X),
                "performance_metrics": model.performance_metrics
            }

        except BiologyError as e:
            return self.handle_error(e, "train_model")

    def _create_gaussian_process(self):
        """Create Gaussian Process model"""
        # Define kernel
        kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2))

        # Create GP model
        gp = GaussianProcessRegressor(
            kernel=kernel,
            n_restarts_optimizer=10,
            alpha=1e-6,
            normalize_y=True,
            random_state=42
        )

        return gp

    async def _calculate_performance_metrics(self, model: SurrogateModel, X_scaled: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Calculate performance metrics for the model"""
        try:
            # Make predictions on training data
            y_pred = model.model.predict(X_scaled)

            # Calculate metrics
            mse = np.mean((y - y_pred) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(y - y_pred))

            # R² score
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

            return {
                "mse": float(mse),
                "rmse": float(rmse),
                "mae": float(mae),
                "r2_score": float(r2)
            }

        except BiologyError as e:
            logger.warning(f"Error calculating performance metrics: {e}")
            return {"error": "Could not calculate metrics"}

    async def predict(self, request_data: PredictResult) -> PredictResult:
        """Make a prediction using the surrogate model"""
        try:
            model_id = request_data.get("model_id")
            input_data = request_data.get("input_data", [])

            if not model_id or model_id not in self.models:
                return {
                    "success": False,
                    "error": f"Model {model_id} not found"
                }

            model = self.models[model_id]

            if not model.trained:
                return {
                    "success": False,
                    "error": f"Model {model_id} is not trained yet"
                }

            if not input_data:
                return {
                    "success": False,
                    "error": "input_data is required"
                }

            # Convert to numpy array
            X = np.array([input_data])

            # Validate dimensions
            if X.shape[1] != model.input_dimensions:
                return {
                    "success": False,
                    "error": f"Input data has {X.shape[1]} dimensions, but model expects {model.input_dimensions}"
                }

            # Scale input
            X_scaled = model.scaler.transform(X)

            # Make prediction
            if model.model_type == "gaussian_process":
                y_pred, y_std = model.model.predict(X_scaled, return_std=True)
                prediction = float(y_pred[0])
                uncertainty = float(y_std[0])

                # Calculate confidence interval (95%)
                confidence_interval = (
                    prediction - 1.96 * uncertainty,
                    prediction + 1.96 * uncertainty
                )
            else:
                y_pred = model.model.predict(X_scaled)
                prediction = float(y_pred[0])
                uncertainty = None
                confidence_interval = None

            result = PredictionResult(
                prediction=prediction,
                uncertainty=uncertainty,
                confidence_interval=confidence_interval,
                model_type=model.model_type
            )

            return {
                "success": True,
                "model_id": model_id,
                "prediction": result.prediction,
                "uncertainty": result.uncertainty,
                "confidence_interval": result.confidence_interval,
                "model_type": result.model_type
            }

        except BiologyError as e:
            return self.handle_error(e, "predict")

    async def batch_predict(self, request_data: BatchPredictResult) -> BatchPredictResult:
        """Make batch predictions using the surrogate model"""
        try:
            model_id = request_data.get("model_id")
            input_data_batch = request_data.get("input_data_batch", [])

            if not model_id or model_id not in self.models:
                return {
                    "success": False,
                    "error": f"Model {model_id} not found"
                }

            model = self.models[model_id]

            if not model.trained:
                return {
                    "success": False,
                    "error": f"Model {model_id} is not trained yet"
                }

            if not input_data_batch:
                return {
                    "success": False,
                    "error": "input_data_batch is required"
                }

            # Convert to numpy array
            X = np.array(input_data_batch)

            # Validate dimensions
            if X.shape[1] != model.input_dimensions:
                return {
                    "success": False,
                    "error": f"Input data has {X.shape[1]} dimensions, but model expects {model.input_dimensions}"
                }

            # Scale input
            X_scaled = model.scaler.transform(X)

            # Make predictions
            predictions = []
            if model.model_type == "gaussian_process":
                y_pred, y_std = model.model.predict(X_scaled, return_std=True)

                for i in range(len(y_pred)):
                    prediction = float(y_pred[i])
                    uncertainty = float(y_std[i])
                    confidence_interval = (
                        prediction - 1.96 * uncertainty,
                        prediction + 1.96 * uncertainty
                    )

                    predictions.append({
                        "prediction": prediction,
                        "uncertainty": uncertainty,
                        "confidence_interval": confidence_interval
                    })
            else:
                y_pred = model.model.predict(X_scaled)

                for pred in y_pred:
                    predictions.append({
                        "prediction": float(pred),
                        "uncertainty": None,
                        "confidence_interval": None
                    })

            return {
                "success": True,
                "model_id": model_id,
                "predictions": predictions,
                "batch_size": len(predictions),
                "model_type": model.model_type
            }

        except BiologyError as e:
            return self.handle_error(e, "batch_predict")

    def get_model_info(self, request_data: GetModelInfoResult) -> GetModelInfoResult:
        """Get information about a surrogate model"""
        try:
            model_id = request_data.get("model_id")

            if not model_id or model_id not in self.models:
                return {
                    "success": False,
                    "error": f"Model {model_id} not found"
                }

            model = self.models[model_id]

            return {
                "success": True,
                "model_id": model_id,
                "model_info": {
                    "model_type": model.model_type,
                    "input_dimensions": model.input_dimensions,
                    "trained": model.trained,
                    "training_data_size": model.training_data_size,
                    "performance_metrics": model.performance_metrics,
                    "created_at": model.created_at.isoformat(),
                    "last_trained": model.last_trained.isoformat() if model.last_trained else None
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "get_model_info")

    async def evaluate_model(self, request_data: EvaluateModelResult) -> EvaluateModelResult:
        """Evaluate model performance on test data"""
        try:
            model_id = request_data.get("model_id")
            X_test = request_data.get("X_test", [])
            y_test = request_data.get("y_test", [])

            if not model_id or model_id not in self.models:
                return {
                    "success": False,
                    "error": f"Model {model_id} not found"
                }

            model = self.models[model_id]

            if not model.trained:
                return {
                    "success": False,
                    "error": f"Model {model_id} is not trained yet"
                }

            if not X_test or not y_test:
                return {
                    "success": False,
                    "error": "Test data (X_test and y_test) is required"
                }

            # Convert to numpy arrays
            X = np.array(X_test)
            y = np.array(y_test)

            # Scale test data
            X_scaled = model.scaler.transform(X)

            # Make predictions
            if model.model_type == "gaussian_process":
                y_pred, y_std = model.model.predict(X_scaled, return_std=True)
            else:
                y_pred = model.model.predict(X_scaled)

            # Calculate test metrics
            mse = np.mean((y - y_pred) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(y - y_pred))

            # R² score
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

            test_metrics = {
                "test_mse": float(mse),
                "test_rmse": float(rmse),
                "test_mae": float(mae),
                "test_r2_score": float(r2)
            }

            return {
                "success": True,
                "model_id": model_id,
                "test_metrics": test_metrics,
                "test_samples": len(X),
                "predictions": y_pred.tolist(),
                "actual_values": y.tolist()
            }

        except BiologyError as e:
            return self.handle_error(e, "evaluate_model")

    async def update_model(self, request_data: UpdateModelResult) -> UpdateModelResult:
        """Update model with new training data"""
        try:
            model_id = request_data.get("model_id")
            X_new = request_data.get("X_new", [])
            y_new = request_data.get("y_new", [])

            if not model_id or model_id not in self.models:
                return {
                    "success": False,
                    "error": f"Model {model_id} not found"
                }

            model = self.models[model_id]

            if not X_new or not y_new:
                return {
                    "success": False,
                    "error": "New training data (X_new and y_new) is required"
                }

            # Convert to numpy arrays
            X_new = np.array(X_new)
            y_new = np.array(y_new)

            # Combine with existing data if available
            if model.X_train is not None and model.y_train is not None:
                X_combined = np.vstack([model.X_train, X_new])
                y_combined = np.concatenate([model.y_train, y_new])
            else:
                X_combined = X_new
                y_combined = y_new

            # Retrain the model
            train_request = {
                "model_id": model_id,
                "X_data": X_combined.tolist(),
                "y_data": y_combined.tolist()
            }

            return await self.train_model(train_request)

        except BiologyError as e:
            return self.handle_error(e, "update_model")

    async def create_surrogate_for_simulation(self, simulation_config: CreateSurrogateForSimulationResult) -> CreateSurrogateForSimulationResult:
        """High-level method to create surrogate model for expensive simulation"""
        try:
            # Extract simulation parameters
            parameter_bounds = simulation_config.get("parameter_bounds", {})
            simulation_function = simulation_config.get("simulation_function")
            initial_samples = simulation_config.get("initial_samples", 20)
            model_type = simulation_config.get("model_type", "gaussian_process")

            if not parameter_bounds:
                return {
                    "success": False,
                    "error": "parameter_bounds are required for simulation surrogate"
                }

            input_dimensions = len(parameter_bounds)

            # Create model
            create_result = await self.create_model({
                "model_type": model_type,
                "input_dimensions": input_dimensions
            })

            if not create_result.get("success"):
                return create_result

            model_id = create_result["model_id"]

            # Generate initial training data
            X_train = []
            y_train = []

            np.random.seed(42)  # For reproducibility

            for _ in range(initial_samples):
                # Sample random point within bounds
                point = []
                for param_name, bounds in parameter_bounds.items():
                    value = np.random.uniform(bounds[0], bounds[1])
                    point.append(value)

                X_train.append(point)

                # Evaluate simulation function
                if simulation_function:
                    # In real implementation, this would call the actual simulation
                    y_value = simulation_function(point)
                else:
                    # Default: simple quadratic function
                    y_value = sum((xi - 0.5)**2 for xi in point)

                y_train.append(y_value)

            # Train the model
            train_result = await self.train_model({
                "model_id": model_id,
                "X_data": X_train,
                "y_data": y_train
            })

            return {
                "success": True,
                "message": "Simulation surrogate model created and trained",
                "model_id": model_id,
                "model_type": model_type,
                "input_dimensions": input_dimensions,
                "initial_samples": initial_samples,
                "training_result": train_result
            }

        except BiologyError as e:
            return self.handle_error(e, "create_surrogate_for_simulation")
