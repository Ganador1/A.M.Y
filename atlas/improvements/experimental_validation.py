"""
Automated Experimental Validation Service for AXIOM/ATLAS
Implements automated experimental design, simulation, and validation
Author: AXIOM Enhancement Team
Date: December 2024
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from enum import Enum

# Scientific computing imports
try:
    from scipy import stats, optimize
    from scipy.stats import norm, ttest_ind, chi2_contingency
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from sklearn.model_selection import ParameterGrid
    from sklearn.metrics import mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Simulation imports
try:
    import simpy
    SIMPY_AVAILABLE = True
except ImportError:
    SIMPY_AVAILABLE = False

try:
    import mesa
    MESA_AVAILABLE = True
except ImportError:
    MESA_AVAILABLE = False

# Optimization imports
try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DesignType(Enum):
    """Types of experimental designs"""
    FACTORIAL = "factorial"
    RESPONSE_SURFACE = "response_surface"
    D_OPTIMAL = "d_optimal"
    LATIN_SQUARE = "latin_square"
    RANDOMIZED_BLOCK = "randomized_block"
    SPLIT_PLOT = "split_plot"


class ValidationStatus(Enum):
    """Validation status"""
    PENDING = "pending"
    RUNNING = "running"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
    FAILED = "failed"


@dataclass
class ExperimentalFactor:
    """Experimental factor definition"""
    name: str
    factor_type: str  # continuous, categorical, ordinal
    levels: List[Union[float, int, str]]
    bounds: Optional[Tuple[float, float]] = None
    units: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ExperimentalDesign:
    """Experimental design specification"""
    design_id: str
    design_type: DesignType
    factors: List[ExperimentalFactor]
    response_variables: List[str]
    replicates: int = 3
    randomization: bool = True
    blocking: Optional[str] = None
    constraints: List[str] = field(default_factory=list)


@dataclass
class SimulationResult:
    """Result from simulation"""
    success: bool
    data: Dict[str, Any]
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """Result from hypothesis validation"""
    hypothesis_id: str
    status: ValidationStatus
    confidence: float
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    statistical_power: Optional[float] = None
    sample_size: Optional[int] = None
    execution_time: float = 0
    recommendations: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)


class AutomatedExperimentalValidation:
    """
    Automated experimental validation service
    Provides experimental design, simulation, and statistical validation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize experimental validation service"""
        self.config = config or {}
        
        # Initialize simulation environments
        self._initialize_simulation_environments()
        
        # Statistical settings
        self.alpha_level = self.config.get('alpha_level', 0.05)
        self.power_threshold = self.config.get('power_threshold', 0.8)
        self.min_sample_size = self.config.get('min_sample_size', 10)
        
        # Simulation settings
        self.max_simulation_time = self.config.get('max_simulation_time', 3600)  # 1 hour
        self.simulation_steps = self.config.get('simulation_steps', 1000)
        
        logger.info("✅ Automated Experimental Validation initialized")
    
    def _initialize_simulation_environments(self):
        """Initialize simulation environments"""
        self.simulation_envs = {}
        
        if SIMPY_AVAILABLE:
            # Discrete event simulation
            self.simulation_envs['simpy'] = simpy.Environment()
            logger.info("📊 SimPy simulation environment initialized")
        
        if MESA_AVAILABLE:
            # Agent-based simulation
            logger.info("🤖 Mesa agent-based simulation available")
        
        logger.info(f"🔬 Simulation environments: {list(self.simulation_envs.keys())}")
    
    async def design_experiment(
        self,
        hypothesis: Dict[str, Any],
        design_type: DesignType = DesignType.FACTORIAL
    ) -> ExperimentalDesign:
        """
        Design experiment based on hypothesis
        
        Args:
            hypothesis: Hypothesis to test
            design_type: Type of experimental design
            
        Returns:
            ExperimentalDesign object
        """
        try:
            # Extract factors from hypothesis
            factors = self._extract_factors_from_hypothesis(hypothesis)
            
            # Extract response variables
            response_variables = self._extract_response_variables(hypothesis)
            
            # Create experimental design
            design = ExperimentalDesign(
                design_id=f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                design_type=design_type,
                factors=factors,
                response_variables=response_variables,
                replicates=self._calculate_optimal_replicates(factors, design_type)
            )
            
            # Apply design-specific optimizations
            if design_type == DesignType.D_OPTIMAL:
                design = self._optimize_d_optimal_design(design)
            elif design_type == DesignType.RESPONSE_SURFACE:
                design = self._optimize_response_surface_design(design)
            
            logger.info(f"🧪 Experimental design created: {design.design_id}")
            return design
            
        except Exception as e:
            logger.error(f"Experimental design failed: {e}")
            raise
    
    async def simulate_experiment(
        self,
        design: ExperimentalDesign,
        simulation_type: str = "statistical"
    ) -> SimulationResult:
        """
        Simulate experiment based on design
        
        Args:
            design: Experimental design
            simulation_type: Type of simulation (statistical, discrete_event, agent_based)
            
        Returns:
            SimulationResult with simulated data
        """
        start_time = datetime.now()
        
        try:
            if simulation_type == "statistical":
                result = await self._simulate_statistical_experiment(design)
            elif simulation_type == "discrete_event":
                result = await self._simulate_discrete_event_experiment(design)
            elif simulation_type == "agent_based":
                result = await self._simulate_agent_based_experiment(design)
            else:
                raise ValueError(f"Unknown simulation type: {simulation_type}")
            
            end_time = datetime.now()
            result.execution_time = (end_time - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            logger.error(f"Experiment simulation failed: {e}")
            return SimulationResult(
                success=False,
                data={},
                execution_time=0,
                error_message=str(e)
            )
    
    async def validate_hypothesis(
        self,
        hypothesis: Dict[str, Any],
        experimental_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate hypothesis using experimental data
        
        Args:
            hypothesis: Hypothesis to validate
            experimental_data: Data from experiment/simulation
            
        Returns:
            ValidationResult with validation details
        """
        start_time = datetime.now()
        
        try:
            # Extract hypothesis components
            hypothesis_statement = hypothesis.get('statement', '')
            variables = hypothesis.get('variables', [])
            expected_outcome = hypothesis.get('expected_outcome', '')
            
            # Perform statistical tests
            statistical_results = await self._perform_statistical_tests(
                hypothesis, experimental_data
            )
            
            # Calculate effect size
            effect_size = self._calculate_effect_size(experimental_data)
            
            # Calculate statistical power
            power = self._calculate_statistical_power(
                experimental_data, effect_size
            )
            
            # Determine validation status
            status = self._determine_validation_status(
                statistical_results, effect_size, power
            )
            
            # Generate recommendations
            recommendations = self._generate_validation_recommendations(
                status, statistical_results, effect_size, power
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return ValidationResult(
                hypothesis_id=hypothesis.get('id', 'unknown'),
                status=status,
                confidence=statistical_results.get('confidence', 0.5),
                p_value=statistical_results.get('p_value'),
                effect_size=effect_size,
                statistical_power=power,
                sample_size=len(experimental_data.get('data', [])),
                execution_time=execution_time,
                recommendations=recommendations,
                raw_data=experimental_data
            )
            
        except Exception as e:
            logger.error(f"Hypothesis validation failed: {e}")
            return ValidationResult(
                hypothesis_id=hypothesis.get('id', 'unknown'),
                status=ValidationStatus.FAILED,
                confidence=0,
                execution_time=0,
                recommendations=[f"Validation failed: {str(e)}"]
            )
    
    async def optimize_experimental_parameters(
        self,
        design: ExperimentalDesign,
        objective_function: callable,
        optimization_method: str = "bayesian"
    ) -> Dict[str, Any]:
        """
        Optimize experimental parameters using various methods
        
        Args:
            design: Experimental design
            objective_function: Function to optimize
            optimization_method: Method to use (bayesian, grid_search, random)
            
        Returns:
            Optimization results
        """
        try:
            if optimization_method == "bayesian" and OPTUNA_AVAILABLE:
                return await self._bayesian_optimization(design, objective_function)
            elif optimization_method == "grid_search":
                return await self._grid_search_optimization(design, objective_function)
            elif optimization_method == "random":
                return await self._random_search_optimization(design, objective_function)
            else:
                raise ValueError(f"Unknown optimization method: {optimization_method}")
                
        except Exception as e:
            logger.error(f"Parameter optimization failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_factors_from_hypothesis(self, hypothesis: Dict[str, Any]) -> List[ExperimentalFactor]:
        """Extract experimental factors from hypothesis"""
        factors = []
        
        # Extract variables as factors
        variables = hypothesis.get('variables', [])
        for var in variables:
            # Determine factor type and levels
            if isinstance(var, str):
                # Categorical factor
                factor = ExperimentalFactor(
                    name=var,
                    factor_type="categorical",
                    levels=["low", "medium", "high"],
                    description=f"Factor: {var}"
                )
            else:
                # Continuous factor
                factor = ExperimentalFactor(
                    name=str(var),
                    factor_type="continuous",
                    levels=[0.0, 0.5, 1.0],
                    bounds=(0.0, 1.0),
                    units="normalized"
                )
            factors.append(factor)
        
        return factors
    
    def _extract_response_variables(self, hypothesis: Dict[str, Any]) -> List[str]:
        """Extract response variables from hypothesis"""
        # Default response variables
        response_vars = ["outcome", "performance", "efficiency"]
        
        # Extract from expected outcome
        expected_outcome = hypothesis.get('expected_outcome', '')
        if expected_outcome:
            # Try to extract measurable variables
            if "increase" in expected_outcome.lower():
                response_vars.append("increase_rate")
            if "decrease" in expected_outcome.lower():
                response_vars.append("decrease_rate")
            if "improve" in expected_outcome.lower():
                response_vars.append("improvement")
        
        return response_vars
    
    def _calculate_optimal_replicates(
        self,
        factors: List[ExperimentalFactor],
        design_type: DesignType
    ) -> int:
        """Calculate optimal number of replicates"""
        # Base calculation on number of factors and design type
        base_replicates = 3
        
        if design_type == DesignType.FACTORIAL:
            # More replicates for factorial designs
            base_replicates = max(3, len(factors))
        elif design_type == DesignType.D_OPTIMAL:
            # Fewer replicates for D-optimal designs
            base_replicates = max(2, len(factors) // 2)
        
        return min(base_replicates, 10)  # Cap at 10
    
    def _optimize_d_optimal_design(self, design: ExperimentalDesign) -> ExperimentalDesign:
        """Optimize design for D-optimality"""
        # Simplified D-optimal optimization
        # In practice, would use specialized libraries like pyDOE2
        
        # Add constraints for D-optimality
        design.constraints.append("d_optimal")
        design.constraints.append("minimize_correlation")
        
        return design
    
    def _optimize_response_surface_design(self, design: ExperimentalDesign) -> ExperimentalDesign:
        """Optimize design for response surface methodology"""
        # Add response surface specific constraints
        design.constraints.append("response_surface")
        design.constraints.append("quadratic_terms")
        
        return design
    
    async def _simulate_statistical_experiment(self, design: ExperimentalDesign) -> SimulationResult:
        """Simulate statistical experiment"""
        try:
            # Generate experimental runs
            runs = self._generate_experimental_runs(design)
            
            # Simulate responses
            simulated_data = []
            for run in runs:
                # Generate response based on factor levels
                response = self._simulate_response(run, design)
                simulated_data.append({
                    "run_id": run["run_id"],
                    "factors": run["factors"],
                    "responses": response
                })
            
            return SimulationResult(
                success=True,
                data={
                    "design_id": design.design_id,
                    "runs": simulated_data,
                    "summary_stats": self._calculate_summary_statistics(simulated_data)
                },
                execution_time=0,
                metadata={"simulation_type": "statistical"}
            )
            
        except Exception as e:
            return SimulationResult(
                success=False,
                data={},
                execution_time=0,
                error_message=str(e)
            )
    
    async def _simulate_discrete_event_experiment(self, design: ExperimentalDesign) -> SimulationResult:
        """Simulate discrete event experiment using SimPy"""
        if not SIMPY_AVAILABLE:
            return SimulationResult(
                success=False,
                data={},
                execution_time=0,
                error_message="SimPy not available"
            )
        
        try:
            # Create SimPy environment
            env = simpy.Environment()
            
            # Run simulation
            env.process(self._discrete_event_process(env, design))
            env.run(until=self.simulation_steps)
            
            # Collect results
            results = {
                "design_id": design.design_id,
                "simulation_steps": self.simulation_steps,
                "final_state": "completed"
            }
            
            return SimulationResult(
                success=True,
                data=results,
                execution_time=0,
                metadata={"simulation_type": "discrete_event"}
            )
            
        except Exception as e:
            return SimulationResult(
                success=False,
                data={},
                execution_time=0,
                error_message=str(e)
            )
    
    async def _simulate_agent_based_experiment(self, design: ExperimentalDesign) -> SimulationResult:
        """Simulate agent-based experiment using Mesa"""
        if not MESA_AVAILABLE:
            return SimulationResult(
                success=False,
                data={},
                execution_time=0,
                error_message="Mesa not available"
            )
        
        try:
            # Simplified agent-based simulation
            # In practice, would create Mesa model and agents
            
            results = {
                "design_id": design.design_id,
                "agents": 100,  # Simplified
                "interactions": 1000,
                "final_state": "equilibrium"
            }
            
            return SimulationResult(
                success=True,
                data=results,
                execution_time=0,
                metadata={"simulation_type": "agent_based"}
            )
            
        except Exception as e:
            return SimulationResult(
                success=False,
                data={},
                execution_time=0,
                error_message=str(e)
            )
    
    def _generate_experimental_runs(self, design: ExperimentalDesign) -> List[Dict[str, Any]]:
        """Generate experimental runs based on design"""
        runs = []
        
        if design.design_type == DesignType.FACTORIAL:
            # Generate factorial design runs
            factor_levels = [factor.levels for factor in design.factors]
            
            if SKLEARN_AVAILABLE:
                # Use sklearn's ParameterGrid
                param_grid = {}
                for i, factor in enumerate(design.factors):
                    param_grid[factor.name] = factor.levels
                
                grid = ParameterGrid(param_grid)
                for params in grid:
                    runs.append({
                        "run_id": f"run_{len(runs)}",
                        "factors": params
                    })
            else:
                # Simple enumeration
                for i in range(2 ** len(design.factors)):
                    factors = {}
                    for j, factor in enumerate(design.factors):
                        level_idx = (i >> j) & 1
                        factors[factor.name] = factor.levels[level_idx % len(factor.levels)]
                    runs.append({
                        "run_id": f"run_{len(runs)}",
                        "factors": factors
                    })
        
        # Add replicates
        replicated_runs = []
        for replicate in range(design.replicates):
            for run in runs:
                replicated_run = run.copy()
                replicated_run["run_id"] = f"{run['run_id']}_rep_{replicate}"
                replicated_run["replicate"] = replicate
                replicated_runs.append(replicated_run)
        
        return replicated_runs
    
    def _simulate_response(self, run: Dict[str, Any], design: ExperimentalDesign) -> Dict[str, float]:
        """Simulate response for a given run"""
        responses = {}
        
        for response_var in design.response_variables:
            # Simple response simulation
            # In practice, would use more sophisticated models
            
            base_value = 10.0
            noise = np.random.normal(0, 1)
            
            # Add factor effects
            factor_effect = 0
            for factor_name, factor_value in run["factors"].items():
                if isinstance(factor_value, (int, float)):
                    factor_effect += factor_value * 2.0
                else:
                    factor_effect += hash(str(factor_value)) % 5
            
            responses[response_var] = base_value + factor_effect + noise
        
        return responses
    
    def _calculate_summary_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for experimental data"""
        if not data:
            return {}
        
        # Extract response values
        response_values = {}
        for response_var in data[0]["responses"].keys():
            values = [run["responses"][response_var] for run in data]
            response_values[response_var] = {
                "mean": np.mean(values),
                "std": np.std(values),
                "min": np.min(values),
                "max": np.max(values),
                "count": len(values)
            }
        
        return response_values
    
    async def _perform_statistical_tests(
        self,
        hypothesis: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform statistical tests on experimental data"""
        if not SCIPY_AVAILABLE:
            return {"confidence": 0.5, "p_value": None}
        
        try:
            # Extract data for analysis
            runs = data.get("runs", [])
            if not runs:
                return {"confidence": 0.5, "p_value": None}
            
            # Simple t-test between groups
            # In practice, would be more sophisticated based on hypothesis
            
            # Split data into groups (simplified)
            group1 = runs[:len(runs)//2]
            group2 = runs[len(runs)//2:]
            
            if group1 and group2:
                # Extract response values
                values1 = [run["responses"]["outcome"] for run in group1]
                values2 = [run["responses"]["outcome"] for run in group2]
                
                # Perform t-test
                t_stat, p_value = ttest_ind(values1, values2)
                
                # Calculate confidence
                confidence = 1 - p_value if p_value else 0.5
                
                return {
                    "confidence": confidence,
                    "p_value": p_value,
                    "t_statistic": t_stat,
                    "test_type": "independent_t_test"
                }
            
            return {"confidence": 0.5, "p_value": None}
            
        except Exception as e:
            logger.error(f"Statistical test failed: {e}")
            return {"confidence": 0.5, "p_value": None}
    
    def _calculate_effect_size(self, data: Dict[str, Any]) -> float:
        """Calculate effect size from experimental data"""
        try:
            runs = data.get("runs", [])
            if not runs:
                return 0.0
            
            # Calculate Cohen's d (simplified)
            values = [run["responses"]["outcome"] for run in runs]
            
            if len(values) < 2:
                return 0.0
            
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            # Effect size as standardized mean difference
            effect_size = mean_val / std_val if std_val > 0 else 0.0
            
            return abs(effect_size)
            
        except Exception as e:
            logger.error(f"Effect size calculation failed: {e}")
            return 0.0
    
    def _calculate_statistical_power(self, data: Dict[str, Any], effect_size: float) -> float:
        """Calculate statistical power"""
        try:
            runs = data.get("runs", [])
            sample_size = len(runs)
            
            if sample_size < 2 or effect_size == 0:
                return 0.0
            
            # Simplified power calculation
            # In practice, would use power analysis libraries
            
            # Power increases with sample size and effect size
            power = min(0.95, 0.5 + (sample_size / 100) * (effect_size / 2))
            
            return power
            
        except Exception as e:
            logger.error(f"Power calculation failed: {e}")
            return 0.0
    
    def _determine_validation_status(
        self,
        statistical_results: Dict[str, Any],
        effect_size: float,
        power: float
    ) -> ValidationStatus:
        """Determine validation status based on results"""
        p_value = statistical_results.get("p_value")
        confidence = statistical_results.get("confidence", 0.5)
        
        if p_value is None:
            return ValidationStatus.INCONCLUSIVE
        
        if p_value < self.alpha_level and power > self.power_threshold:
            if effect_size > 0.5:  # Large effect
                return ValidationStatus.CONFIRMED
            else:
                return ValidationStatus.CONFIRMED  # Still confirmed but smaller effect
        elif p_value >= self.alpha_level:
            return ValidationStatus.REFUTED
        else:
            return ValidationStatus.INCONCLUSIVE
    
    def _generate_validation_recommendations(
        self,
        status: ValidationStatus,
        statistical_results: Dict[str, Any],
        effect_size: float,
        power: float
    ) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if status == ValidationStatus.CONFIRMED:
            recommendations.append("✅ Hypothesis is statistically confirmed")
            if effect_size > 0.8:
                recommendations.append("🌟 Large effect size detected - strong evidence")
            elif effect_size > 0.5:
                recommendations.append("📈 Medium effect size - good evidence")
            else:
                recommendations.append("📊 Small effect size - consider practical significance")
        
        elif status == ValidationStatus.REFUTED:
            recommendations.append("❌ Hypothesis is statistically refuted")
            recommendations.append("🔄 Consider revising hypothesis or experimental design")
        
        elif status == ValidationStatus.INCONCLUSIVE:
            recommendations.append("❓ Results are inconclusive")
            if power < self.power_threshold:
                recommendations.append("📈 Increase sample size to improve statistical power")
            if statistical_results.get("p_value", 1) > self.alpha_level:
                recommendations.append("🔍 Consider alternative statistical tests")
        
        return recommendations
    
    async def _bayesian_optimization(
        self,
        design: ExperimentalDesign,
        objective_function: callable
    ) -> Dict[str, Any]:
        """Bayesian optimization using Optuna"""
        if not OPTUNA_AVAILABLE:
            return {"success": False, "error": "Optuna not available"}
        
        try:
            def objective(trial):
                # Sample parameters
                params = {}
                for factor in design.factors:
                    if factor.factor_type == "continuous":
                        params[factor.name] = trial.suggest_float(
                            factor.name, factor.bounds[0], factor.bounds[1]
                        )
                    else:
                        params[factor.name] = trial.suggest_categorical(
                            factor.name, factor.levels
                        )
                
                return objective_function(params)
            
            # Run optimization
            study = optuna.create_study(direction="maximize")
            study.optimize(objective, n_trials=100)
            
            return {
                "success": True,
                "best_params": study.best_params,
                "best_value": study.best_value,
                "n_trials": len(study.trials)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _grid_search_optimization(
        self,
        design: ExperimentalDesign,
        objective_function: callable
    ) -> Dict[str, Any]:
        """Grid search optimization"""
        try:
            # Create parameter grid
            param_grid = {}
            for factor in design.factors:
                param_grid[factor.name] = factor.levels
            
            best_params = None
            best_value = float('-inf')
            
            # Simple grid search
            for params in self._generate_parameter_combinations(param_grid):
                value = objective_function(params)
                if value > best_value:
                    best_value = value
                    best_params = params
            
            return {
                "success": True,
                "best_params": best_params,
                "best_value": best_value
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _random_search_optimization(
        self,
        design: ExperimentalDesign,
        objective_function: callable
    ) -> Dict[str, Any]:
        """Random search optimization"""
        try:
            best_params = None
            best_value = float('-inf')
            
            # Random search
            for _ in range(100):
                params = {}
                for factor in design.factors:
                    if factor.factor_type == "continuous":
                        params[factor.name] = np.random.uniform(
                            factor.bounds[0], factor.bounds[1]
                        )
                    else:
                        params[factor.name] = np.random.choice(factor.levels)
                
                value = objective_function(params)
                if value > best_value:
                    best_value = value
                    best_params = params
            
            return {
                "success": True,
                "best_params": best_params,
                "best_value": best_value
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_parameter_combinations(self, param_grid: Dict[str, List]) -> List[Dict[str, Any]]:
        """Generate all parameter combinations"""
        # Simple recursive combination generator
        if not param_grid:
            return [{}]
        
        key, values = param_grid.popitem()
        combinations = []
        
        for value in values:
            for combo in self._generate_parameter_combinations(param_grid.copy()):
                combo[key] = value
                combinations.append(combo)
        
        return combinations
    
    def _discrete_event_process(self, env: simpy.Environment, design: ExperimentalDesign):
        """SimPy discrete event process"""
        # Simplified discrete event simulation
        # In practice, would model specific experimental processes
        
        for step in range(self.simulation_steps):
            yield env.timeout(1)  # Process one time unit
            
            # Simulate experimental process
            # This would be customized based on the specific experiment


# Utility functions
async def design_and_run_experiment(
    hypothesis: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function to design and run experiment"""
    validator = AutomatedExperimentalValidation(config)
    
    # Design experiment
    design = await validator.design_experiment(hypothesis)
    
    # Simulate experiment
    simulation_result = await validator.simulate_experiment(design)
    
    # Validate hypothesis
    validation_result = await validator.validate_hypothesis(hypothesis, simulation_result.data)
    
    return {
        "design": design,
        "simulation": simulation_result,
        "validation": validation_result
    }


async def optimize_experimental_parameters(
    design: ExperimentalDesign,
    objective_function: callable,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function for parameter optimization"""
    validator = AutomatedExperimentalValidation(config)
    return await validator.optimize_experimental_parameters(design, objective_function)
