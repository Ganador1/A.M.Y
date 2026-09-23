"""
Bayesian Optimization Service for AXIOM
Implements Bayesian optimization for experimental design and parameter optimization
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from scipy.stats import norm

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.bayesian_optimization_types import (
    ProcessRequestResult,
    CreateOptimizerResult,
    RunOptimizationResult,
    SuggestNextPointResult,
    AddObservationResult,
    GetOptimizerStatusResult,
    GetOptimizationResultsResult,
    OptimizeDesignResult,
)


@dataclass
class OptimizationResult:
    """Result of a Bayesian optimization iteration"""
    iteration: int
    parameters: Dict[str, float]
    objective_value: float
    acquisition_value: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BayesianOptimizer:
    """Bayesian optimization instance"""
    optimizer_id: str
    parameter_bounds: Dict[str, Tuple[float, float]]
    objective_function: callable
    acquisition_function: str = "expected_improvement"
    kernel_type: str = "rbf"
    max_iterations: int = 50
    initial_points: int = 5
    exploration_weight: float = 0.01

    # Optimization state
    X_observed: List[List[float]] = field(default_factory=list)
    y_observed: List[float] = field(default_factory=list)
    best_value: Optional[float] = None
    best_parameters: Optional[Dict[str, float]] = None
    iteration_results: List[OptimizationResult] = field(default_factory=list)

    def __post_init__(self):
        self.parameter_names = list(self.parameter_bounds.keys())
        self.n_parameters = len(self.parameter_names)


class BayesianOptimizationService(BaseService):
    """
    Service for Bayesian optimization of experimental parameters
    Uses Gaussian processes to model objective functions and optimize parameters efficiently
    """

    def __init__(self):
        super().__init__("BayesianOptimization")
        self.active_optimizers: Dict[str, BayesianOptimizer] = {}
        self.optimization_history: Dict[str, List[Dict[str, Any]]] = {}

        logger.info("✅ BayesianOptimizationService initialized")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process Bayesian optimization requests"""
        try:
            action = request_data.get("action", "")

            if action == "create_optimizer":
                return await self.create_optimizer(request_data)
            elif action == "run_optimization":
                return await self.run_optimization(request_data)
            elif action == "suggest_next_point":
                return await self.suggest_next_point(request_data)
            elif action == "add_observation":
                return await self.add_observation(request_data)
            elif action == "get_optimizer_status":
                return self.get_optimizer_status(request_data)
            elif action == "get_optimization_results":
                return self.get_optimization_results(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "create_optimizer", "run_optimization", "suggest_next_point",
                        "add_observation", "get_optimizer_status", "get_optimization_results"
                    ]
                }

        except BiologyError as e:
            return self.handle_error(e, "process_request")

    async def create_optimizer(self, request_data: CreateOptimizerResult) -> CreateOptimizerResult:
        """Create a new Bayesian optimizer"""
        try:
            import uuid

            optimizer_id = str(uuid.uuid4())
            parameter_bounds = request_data.get("parameter_bounds", {})
            objective_config = request_data.get("objective_config", {})

            if not parameter_bounds:
                return {
                    "success": False,
                    "error": "parameter_bounds are required"
                }

            # Create objective function wrapper
            objective_function = self._create_objective_function(objective_config)

            optimizer = BayesianOptimizer(
                optimizer_id=optimizer_id,
                parameter_bounds=parameter_bounds,
                objective_function=objective_function,
                acquisition_function=request_data.get("acquisition_function", "expected_improvement"),
                kernel_type=request_data.get("kernel_type", "rbf"),
                max_iterations=request_data.get("max_iterations", 50),
                initial_points=request_data.get("initial_points", 5),
                exploration_weight=request_data.get("exploration_weight", 0.01)
            )

            self.active_optimizers[optimizer_id] = optimizer

            logger.info(f"✅ Created Bayesian optimizer: {optimizer_id}")

            return {
                "success": True,
                "message": "Bayesian optimizer created successfully",
                "optimizer_id": optimizer_id,
                "parameter_names": optimizer.parameter_names,
                "n_parameters": optimizer.n_parameters
            }

        except BiologyError as e:
            return self.handle_error(e, "create_optimizer")

    def _create_objective_function(self, objective_config: Dict[str, Any]) -> callable:
        """Create objective function from configuration"""
        objective_type = objective_config.get("type", "simulation")

        if objective_type == "simulation":
            # For simulation-based objectives, we'll use a placeholder
            # In real implementation, this would call actual simulation services
            def simulation_objective(x):
                # Simple quadratic function for demonstration
                return sum((xi - 0.5)**2 for xi in x)

            return simulation_objective

        elif objective_type == "analytical":
            # For analytical functions
            # expression = objective_config.get("expression", "x**2")  # Not used in simplified implementation

            def analytical_objective(x):
                # Simple evaluation - in real implementation use sympy or similar
                if len(x) == 1:
                    return x[0]**2
                else:
                    return sum(xi**2 for xi in x)

            return analytical_objective

        else:
            # Default objective
            def default_objective(x):
                return sum(xi**2 for xi in x)

            return default_objective

    async def run_optimization(self, request_data: RunOptimizationResult) -> RunOptimizationResult:
        """Run complete Bayesian optimization"""
        try:
            optimizer_id = request_data.get("optimizer_id")

            if not optimizer_id or optimizer_id not in self.active_optimizers:
                return {
                    "success": False,
                    "error": f"Optimizer {optimizer_id} not found"
                }

            optimizer = self.active_optimizers[optimizer_id]

            # Generate initial points
            await self._generate_initial_points(optimizer)

            # Run optimization iterations
            for iteration in range(optimizer.max_iterations):
                if len(optimizer.X_observed) >= optimizer.max_iterations + optimizer.initial_points:
                    break

                # Suggest next point
                next_point = await self._suggest_next_point(optimizer)

                # Evaluate objective function
                objective_value = optimizer.objective_function(next_point)

                # Add observation
                await self._add_observation(optimizer, next_point, objective_value)

                # Update best values
                if optimizer.best_value is None or objective_value < optimizer.best_value:
                    optimizer.best_value = objective_value
                    optimizer.best_parameters = {
                        name: value for name, value in zip(optimizer.parameter_names, next_point)
                    }

                logger.info(f"✅ Optimization iteration {iteration + 1}: value = {objective_value:.4f}")

            return {
                "success": True,
                "message": f"Optimization completed after {len(optimizer.iteration_results)} iterations",
                "optimizer_id": optimizer_id,
                "best_value": optimizer.best_value,
                "best_parameters": optimizer.best_parameters,
                "total_evaluations": len(optimizer.X_observed),
                "convergence_info": {
                    "final_best_value": optimizer.best_value,
                    "iterations_completed": len(optimizer.iteration_results)
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "run_optimization")

    async def _generate_initial_points(self, optimizer: BayesianOptimizer):
        """Generate initial random points for optimization"""
        np.random.seed(42)  # For reproducibility

        for _ in range(optimizer.initial_points):
            # Generate random point within bounds
            point = []
            for param_name in optimizer.parameter_names:
                bounds = optimizer.parameter_bounds[param_name]
                value = np.random.uniform(bounds[0], bounds[1])
                point.append(value)

            # Evaluate objective
            objective_value = optimizer.objective_function(point)

            # Add to observations
            await self._add_observation(optimizer, point, objective_value)

    async def suggest_next_point(self, request_data: SuggestNextPointResult) -> SuggestNextPointResult:
        """Suggest next point for evaluation"""
        try:
            optimizer_id = request_data.get("optimizer_id")

            if not optimizer_id or optimizer_id not in self.active_optimizers:
                return {
                    "success": False,
                    "error": f"Optimizer {optimizer_id} not found"
                }

            optimizer = self.active_optimizers[optimizer_id]
            next_point = await self._suggest_next_point(optimizer)

            return {
                "success": True,
                "optimizer_id": optimizer_id,
                "suggested_point": {
                    name: value for name, value in zip(optimizer.parameter_names, next_point)
                },
                "point_array": next_point
            }

        except BiologyError as e:
            return self.handle_error(e, "suggest_next_point")

    async def _suggest_next_point(self, optimizer: BayesianOptimizer) -> List[float]:
        """Suggest next point using acquisition function"""
        if len(optimizer.X_observed) < optimizer.initial_points:
            # Still in initial phase - suggest random point
            return await self._suggest_random_point(optimizer)

        # Use acquisition function optimization
        return await self._optimize_acquisition_function(optimizer)

    async def _suggest_random_point(self, optimizer: BayesianOptimizer) -> List[float]:
        """Suggest a random point within bounds"""
        point = []
        for param_name in optimizer.parameter_names:
            bounds = optimizer.parameter_bounds[param_name]
            value = np.random.uniform(bounds[0], bounds[1])
            point.append(value)
        return point

    async def _optimize_acquisition_function(self, optimizer: BayesianOptimizer) -> List[float]:
        """Optimize acquisition function to suggest next point"""
        # Simple implementation - in practice would use proper GP and acquisition optimization
        # For now, use a simple heuristic

        # Try multiple random candidates and pick the best
        best_point = None
        best_acquisition = -np.inf

        for _ in range(100):  # Try 100 random candidates
            candidate = []
            for param_name in optimizer.parameter_names:
                bounds = optimizer.parameter_bounds[param_name]
                value = np.random.uniform(bounds[0], bounds[1])
                candidate.append(value)

            # Evaluate acquisition function (simplified)
            acquisition_value = await self._evaluate_acquisition_function(optimizer, candidate)

            if acquisition_value > best_acquisition:
                best_acquisition = acquisition_value
                best_point = candidate

        return best_point

    async def _evaluate_acquisition_function(self, optimizer: BayesianOptimizer, point: List[float]) -> float:
        """Evaluate acquisition function at a point"""
        if optimizer.acquisition_function == "expected_improvement":
            return await self._expected_improvement(optimizer, point)
        elif optimizer.acquisition_function == "upper_confidence_bound":
            return await self._upper_confidence_bound(optimizer, point)
        else:
            # Default to expected improvement
            return await self._expected_improvement(optimizer, point)

    async def _expected_improvement(self, optimizer: BayesianOptimizer, point: List[float]) -> float:
        """Calculate expected improvement acquisition function"""
        # Simplified EI calculation
        if optimizer.best_value is None:
            return 1.0  # High improvement if no observations yet

        # Mock GP prediction - in real implementation would use actual GP
        predicted_mean = np.mean(optimizer.y_observed)  # Simplified
        predicted_std = np.std(optimizer.y_observed) if len(optimizer.y_observed) > 1 else 1.0

        # Expected improvement calculation
        z = (optimizer.best_value - predicted_mean) / predicted_std
        ei = (optimizer.best_value - predicted_mean) * norm.cdf(z) + predicted_std * norm.pdf(z)

        return max(0, ei)

    async def _upper_confidence_bound(self, optimizer: BayesianOptimizer, point: List[float]) -> float:
        """Calculate upper confidence bound acquisition function"""
        # Simplified UCB calculation
        if optimizer.best_value is None:
            return 1.0

        # Mock GP prediction
        predicted_mean = np.mean(optimizer.y_observed)
        predicted_std = np.std(optimizer.y_observed) if len(optimizer.y_observed) > 1 else 1.0

        # UCB = mean + exploration_weight * std
        ucb = predicted_mean + optimizer.exploration_weight * predicted_std

        return ucb

    async def add_observation(self, request_data: AddObservationResult) -> AddObservationResult:
        """Add observation to optimizer"""
        try:
            optimizer_id = request_data.get("optimizer_id")
            point = request_data.get("point", [])
            value = request_data.get("value")

            if not optimizer_id or optimizer_id not in self.active_optimizers:
                return {
                    "success": False,
                    "error": f"Optimizer {optimizer_id} not found"
                }

            if not point or value is None:
                return {
                    "success": False,
                    "error": "point and value are required"
                }

            optimizer = self.active_optimizers[optimizer_id]
            await self._add_observation(optimizer, point, value)

            return {
                "success": True,
                "message": f"Observation added to optimizer {optimizer_id}",
                "optimizer_id": optimizer_id,
                "total_observations": len(optimizer.X_observed)
            }

        except BiologyError as e:
            return self.handle_error(e, "add_observation")

    async def _add_observation(self, optimizer: BayesianOptimizer, point: List[float], value: float):
        """Add observation to optimizer state"""
        optimizer.X_observed.append(point)
        optimizer.y_observed.append(value)

        # Update best values
        if optimizer.best_value is None or value < optimizer.best_value:
            optimizer.best_value = value
            optimizer.best_parameters = {
                name: value for name, value in zip(optimizer.parameter_names, point)
            }

        # Record iteration result
        iteration_result = OptimizationResult(
            iteration=len(optimizer.iteration_results) + 1,
            parameters={name: value for name, value in zip(optimizer.parameter_names, point)},
            objective_value=value,
            acquisition_value=0.0  # Would be calculated properly in real implementation
        )

        optimizer.iteration_results.append(iteration_result)

    def get_optimizer_status(self, request_data: GetOptimizerStatusResult) -> GetOptimizerStatusResult:
        """Get optimizer status"""
        try:
            optimizer_id = request_data.get("optimizer_id")

            if not optimizer_id or optimizer_id not in self.active_optimizers:
                return {
                    "success": False,
                    "error": f"Optimizer {optimizer_id} not found"
                }

            optimizer = self.active_optimizers[optimizer_id]

            return {
                "success": True,
                "optimizer_id": optimizer_id,
                "status": {
                    "total_observations": len(optimizer.X_observed),
                    "best_value": optimizer.best_value,
                    "best_parameters": optimizer.best_parameters,
                    "iterations_completed": len(optimizer.iteration_results),
                    "max_iterations": optimizer.max_iterations,
                    "acquisition_function": optimizer.acquisition_function,
                    "kernel_type": optimizer.kernel_type
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "get_optimizer_status")

    def get_optimization_results(self, request_data: GetOptimizationResultsResult) -> GetOptimizationResultsResult:
        """Get optimization results"""
        try:
            optimizer_id = request_data.get("optimizer_id")

            if not optimizer_id or optimizer_id not in self.active_optimizers:
                return {
                    "success": False,
                    "error": f"Optimizer {optimizer_id} not found"
                }

            optimizer = self.active_optimizers[optimizer_id]

            results = []
            for result in optimizer.iteration_results:
                results.append({
                    "iteration": result.iteration,
                    "parameters": result.parameters,
                    "objective_value": result.objective_value,
                    "acquisition_value": result.acquisition_value,
                    "timestamp": result.timestamp.isoformat()
                })

            return {
                "success": True,
                "optimizer_id": optimizer_id,
                "results": results,
                "summary": {
                    "total_iterations": len(results),
                    "best_value": optimizer.best_value,
                    "best_parameters": optimizer.best_parameters,
                    "convergence_achieved": len(results) >= optimizer.max_iterations
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "get_optimization_results")

    async def optimize_design(self, design_problem: OptimizeDesignResult) -> OptimizeDesignResult:
        """High-level method for design optimization"""
        try:
            # Extract design parameters
            parameter_bounds = design_problem.get("parameter_bounds", {})
            constraints = design_problem.get("constraints", [])
            objective_type = design_problem.get("objective_type", "minimize")

            # Create optimizer
            optimizer_config = {
                "parameter_bounds": parameter_bounds,
                "objective_config": {
                    "type": "design_optimization",
                    "constraints": constraints,
                    "objective_type": objective_type
                },
                "max_iterations": design_problem.get("max_iterations", 30),
                "acquisition_function": "expected_improvement"
            }

            create_result = await self.create_optimizer(optimizer_config)

            if not create_result.get("success"):
                return create_result

            optimizer_id = create_result["optimizer_id"]

            # Run optimization
            optimization_result = await self.run_optimization({"optimizer_id": optimizer_id})

            return {
                "success": True,
                "message": "Design optimization completed",
                "optimizer_id": optimizer_id,
                "optimal_design": optimization_result.get("best_parameters"),
                "optimal_value": optimization_result.get("best_value"),
                "optimization_details": optimization_result
            }

        except BiologyError as e:
            return self.handle_error(e, "optimize_design")
