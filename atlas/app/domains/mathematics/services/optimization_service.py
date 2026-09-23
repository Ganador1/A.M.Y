"""
Optimization Service for Mathematics AI
Provides optimization algorithms and mathematical optimization capabilities
"""

import numpy as np
from typing import Dict, List, Any, Optional
from app.exceptions.domain.mathematics import MathematicsError
try:
    import cvxpy as cp
except ImportError:
    cp = None
from scipy.optimize import minimize, linprog, basinhopping
import sympy as sp

# Advanced optimization libraries
try:
    import deap
    from deap import base, creator, tools, algorithms
    DEAP_AVAILABLE = True
except ImportError:
    DEAP_AVAILABLE = False
    
try:
    import skopt
    from skopt import gp_minimize
    from skopt.space import Real, Integer, Categorical
    from skopt.utils import use_named_args
    SKOPT_AVAILABLE = True
except ImportError:
    SKOPT_AVAILABLE = False
    
try:
    import cma
    CMA_AVAILABLE = True
except ImportError:
    CMA_AVAILABLE = False
    
try:
    import platypus
    from platypus import NSGAII, SPEA2, Problem, Real, Integer
    PLATYPUS_AVAILABLE = True
except ImportError:
    PLATYPUS_AVAILABLE = False
    
try:
    import pymoo
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.moead import MOEAD
    from pymoo.factory import get_problem, get_reference_directions
    from pymoo.optimize import minimize
    from pymoo.core.problem import Problem as PymooProblem
    PYMOO_AVAILABLE = True
except ImportError:
    PYMOO_AVAILABLE = False


class OptimizationService:
    """Service for mathematical optimization operations"""
    
    def __init__(self):
        self.supported_methods = [
            'linear_programming',
            'nonlinear_optimization',
            'convex_optimization',
            'integer_programming',
            'quadratic_programming',
            'global_optimization',
            'simulated_annealing',
            'genetic_algorithm',
            'particle_swarm_optimization',
            'complex_constrained_optimization',
            'multi_objective_optimization',
            'stochastic_optimization',
            # Advanced methods
            'nsga2_optimization',
            'moead_optimization',
            'spea2_optimization',
            'cma_es_optimization',
            'differential_evolution_advanced',
            'bayesian_optimization',
            'gaussian_process_optimization',
            'hyperparameter_tuning',
            'multi_start_optimization',
            'island_model_ga',
            'multi_population_ga',
            'advanced_global_optimization'
        ]
    
    def linear_programming(self, c: List[float], A_ub: List[List[float]], 
                          b_ub: List[float], bounds: Optional[List[tuple]] = None) -> Dict[str, Any]:
        """
        Solve linear programming problem: min c^T x subject to A_ub x <= b_ub
        """
        try:
            result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
            
            return {
                'optimal_value': float(result.fun) if result.success else None,
                'optimal_variables': result.x.tolist() if result.success else None,
                'status': 'optimal' if result.success else 'infeasible',
                'message': result.message,
                'iterations': result.nit if hasattr(result, 'nit') else 0
            }
        except MathematicsError as e:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': str(e),
                'iterations': 0
            }
    
    def nonlinear_optimization(self, objective: str, variables: List[str], 
                              constraints: Optional[List[str]] = None, 
                              bounds: Optional[Dict[str, List[float]]] = None,
                              initial_guess: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Solve nonlinear optimization problem using scipy.optimize
        """
        try:
            # Convert symbolic expressions to functions
            var_symbols = [sp.Symbol(var) for var in variables]
            objective_expr = sp.sympify(objective)
            
            # Create objective function
            objective_func = sp.lambdify(var_symbols, objective_expr, 'numpy')
            
            # Initial guess
            if initial_guess is None:
                x0 = [0.0] * len(variables)
            else:
                x0 = [initial_guess.get(var, 0.0) for var in variables]
            
            # Bounds
            bounds_tuple = None
            if bounds:
                bounds_tuple = [(bounds[var][0], bounds[var][1]) for var in variables]
            
            # Constraints
            constraints_list = []
            if constraints:
                for constraint in constraints:
                    constraint_expr = sp.sympify(constraint)
                    constraint_func = sp.lambdify(var_symbols, constraint_expr, 'numpy')
                    constraints_list.append({'type': 'ineq', 'fun': constraint_func})
            
            # Solve
            result = minimize(objective_func, x0, bounds=bounds_tuple, constraints=constraints_list)
            
            return {
                'optimal_value': float(result.fun) if result.success else None,
                'optimal_variables': {var: float(val) for var, val in zip(variables, result.x)} if result.success else None,
                'status': 'optimal' if result.success else 'failed',
                'message': result.message,
                'iterations': result.nit if hasattr(result, 'nit') else 0
            }
        except MathematicsError as e:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': str(e),
                'iterations': 0
            }
    
    def global_optimization(self, objective_function: str, variables: List[str],
                            bounds: Optional[Dict[str, List[float]]] = None,
                            initial_guess: Optional[Dict[str, float]] = None,
                            method: str = "basinhopping") -> Dict[str, Any]:
        """
        Solve global optimization problem using scipy.optimize.basinhopping or differential_evolution.
        """
        try:
            var_symbols = [sp.Symbol(var) for var in variables]
            objective_expr = sp.sympify(objective_function)
            # Create objective function that accepts a numpy array
            def objective_func(x_array):
                subs_dict = {var_symbols[i]: x_array[i] for i in range(len(variables))}
                return float(objective_expr.subs(subs_dict))

            # Prepare bounds for scipy
            scipy_bounds = None
            if bounds:
                scipy_bounds = [(bounds[var][0], bounds[var][1]) for var in variables]
            
            # Prepare initial guess for scipy
            x0 = np.array([initial_guess.get(var, 0.0) for var in variables]) if initial_guess else np.zeros(len(variables))

            if method == "basinhopping":
                result = basinhopping(objective_func, x0, minimizer_kwargs={"bounds": scipy_bounds})
            elif method == "differential_evolution":
                from scipy.optimize import differential_evolution
                if not scipy_bounds:
                    raise ValueError("Bounds are required for differential_evolution method.")
                result = differential_evolution(objective_func, scipy_bounds)
            else:
                raise ValueError(f"Unsupported global optimization method: {method}")

            return {
                'objective_function': objective_function,
                'optimal_value': float(result.fun) if result.success else None,
                'optimal_variables': {var: float(val) for var, val in zip(variables, result.x)} if result.success else None,
                'status': 'optimal' if result.success else 'failed',
                'message': "".join(result.message) if isinstance(result.message, list) else result.message if hasattr(result, 'message') else "",
                'iterations': result.nit if hasattr(result, 'nit') else 0
            }
        except MathematicsError as e:
            return {
                'objective_function': objective_function,
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': str(e),
                'iterations': 0
            }

    def simulated_annealing(self, objective_function: str, variables: List[str],
                           bounds: Dict[str, List[float]], initial_temperature: float = 100.0,
                           cooling_rate: float = 0.95, max_iterations: int = 1000,
                           initial_guess: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Solve optimization problem using Simulated Annealing algorithm
        """
        try:
            import random
            import math

            var_symbols = [sp.Symbol(var) for var in variables]
            obj_expr = sp.sympify(objective_function)
            obj_func = sp.lambdify(var_symbols, obj_expr, 'numpy')

            # Initialize solution
            if initial_guess:
                current_solution = np.array([initial_guess.get(var, 0.0) for var in variables])
            else:
                current_solution = np.array([(bounds[var][0] + bounds[var][1]) / 2 for var in variables])

            current_energy = obj_func(*current_solution)
            best_solution = current_solution.copy()
            best_energy = current_energy

            temperature = initial_temperature
            iteration = 0

            # Track convergence
            energy_history = [current_energy]

            while temperature > 1e-3 and iteration < max_iterations:
                # Generate neighbor solution
                neighbor = current_solution.copy()
                for i in range(len(variables)):
                    var = variables[i]
                    # Random perturbation within bounds
                    perturbation = random.uniform(-0.1, 0.1) * (bounds[var][1] - bounds[var][0])
                    neighbor[i] = np.clip(neighbor[i] + perturbation, bounds[var][0], bounds[var][1])

                # Calculate neighbor energy
                neighbor_energy = obj_func(*neighbor)

                # Acceptance probability
                if neighbor_energy < current_energy:
                    acceptance_prob = 1.0
                else:
                    acceptance_prob = math.exp((current_energy - neighbor_energy) / temperature)

                # Accept or reject neighbor
                if random.random() < acceptance_prob:
                    current_solution = neighbor
                    current_energy = neighbor_energy

                    # Update best solution
                    if current_energy < best_energy:
                        best_solution = current_solution.copy()
                        best_energy = current_energy

                # Cool down
                temperature *= cooling_rate
                iteration += 1

                # Record energy every 10 iterations
                if iteration % 10 == 0:
                    energy_history.append(current_energy)

            return {
                'optimal_value': float(best_energy),
                'optimal_variables': {var: float(val) for var, val in zip(variables, best_solution)},
                'status': 'optimal',
                'method': 'simulated_annealing',
                'iterations': iteration,
                'final_temperature': temperature,
                'energy_history': energy_history,
                'convergence': len(energy_history) > 1 and abs(energy_history[-1] - energy_history[0]) < 1e-6
            }

        except MathematicsError as e:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': f"Simulated annealing failed: {str(e)}",
                'method': 'simulated_annealing'
            }

    def genetic_algorithm(self, objective_function: str, variables: List[str],
                         bounds: Dict[str, List[float]], population_size: int = 50,
                         generations: int = 100, mutation_rate: float = 0.1,
                         crossover_rate: float = 0.8, elitism: bool = True) -> Dict[str, Any]:
        """
        Solve optimization problem using Genetic Algorithm
        """
        try:
            import random

            var_symbols = [sp.Symbol(var) for var in variables]
            obj_expr = sp.sympify(objective_function)
            obj_func = sp.lambdify(var_symbols, obj_expr, 'numpy')

            def create_individual():
                """Create random individual within bounds"""
                return np.array([random.uniform(bounds[var][0], bounds[var][1]) for var in variables])

            def evaluate_fitness(individual):
                """Evaluate fitness of individual (minimize objective)"""
                return obj_func(*individual)

            def tournament_selection(population, fitnesses, tournament_size=3):
                """Tournament selection"""
                selected = []
                for _ in range(len(population)):
                    tournament = random.sample(list(zip(population, fitnesses)), tournament_size)
                    winner = min(tournament, key=lambda x: x[1])
                    selected.append(winner[0])
                return selected

            def crossover(parent1, parent2):
                """Single point crossover"""
                if random.random() < crossover_rate:
                    point = random.randint(1, len(parent1) - 1)
                    child1 = np.concatenate([parent1[:point], parent2[point:]])
                    child2 = np.concatenate([parent2[:point], parent1[point:]])
                    return child1, child2
                return parent1.copy(), parent2.copy()

            def mutate(individual):
                """Gaussian mutation"""
                for i in range(len(individual)):
                    if random.random() < mutation_rate:
                        var = variables[i]
                        # Gaussian mutation within bounds
                        mutation = random.gauss(0, 0.1 * (bounds[var][1] - bounds[var][0]))
                        individual[i] = np.clip(individual[i] + mutation, bounds[var][0], bounds[var][1])
                return individual

            # Initialize population
            population = [create_individual() for _ in range(population_size)]
            fitnesses = [evaluate_fitness(ind) for ind in population]

            best_fitness_history = []
            avg_fitness_history = []

            for generation in range(generations):
                # Track best and average fitness
                best_fitness = min(fitnesses)
                avg_fitness = sum(fitnesses) / len(fitnesses)
                best_fitness_history.append(best_fitness)
                avg_fitness_history.append(avg_fitness)

                # Elitism: preserve best individual
                if elitism:
                    best_idx = fitnesses.index(best_fitness)
                    elite = population[best_idx].copy()

                # Selection
                selected = tournament_selection(population, fitnesses)

                # Crossover
                offspring = []
                for i in range(0, len(selected), 2):
                    if i + 1 < len(selected):
                        child1, child2 = crossover(selected[i], selected[i + 1])
                        offspring.extend([child1, child2])
                    else:
                        offspring.append(selected[i])

                # Mutation
                offspring = [mutate(ind) for ind in offspring]

                # Elitism replacement
                if elitism:
                    # Find elite (best individual)
                    elite_idx = fitnesses.index(min(fitnesses))
                    elite = population[elite_idx]
                    # Replace worst individual with elite
                    worst_idx = fitnesses.index(max(fitnesses))
                    offspring[worst_idx] = elite

                # Update population
                population = offspring
                fitnesses = [evaluate_fitness(ind) for ind in population]

            # Find best solution
            best_idx = fitnesses.index(min(fitnesses))
            best_solution = population[best_idx]
            best_fitness = fitnesses[best_idx]

            return {
                'optimal_value': float(best_fitness),
                'optimal_variables': {var: float(val) for var, val in zip(variables, best_solution)},
                'status': 'optimal',
                'method': 'genetic_algorithm',
                'generations': generations,
                'population_size': population_size,
                'best_fitness_history': best_fitness_history,
                'avg_fitness_history': avg_fitness_history,
                'convergence': len(best_fitness_history) > 1 and abs(best_fitness_history[-1] - best_fitness_history[-10]) < 1e-6
            }

        except MathematicsError as e:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': f"Genetic algorithm failed: {str(e)}",
                'method': 'genetic_algorithm'
            }

    def particle_swarm_optimization(self, objective_function: str, variables: List[str],
                                   bounds: Dict[str, List[float]], num_particles: int = 30,
                                   max_iterations: int = 100, inertia_weight: float = 0.7,
                                   cognitive_weight: float = 1.4, social_weight: float = 1.4) -> Dict[str, Any]:
        """
        Solve optimization problem using Particle Swarm Optimization (PSO)
        """
        try:
            var_symbols = [sp.Symbol(var) for var in variables]
            obj_expr = sp.sympify(objective_function)
            obj_func = sp.lambdify(var_symbols, obj_expr, 'numpy')

            # Initialize particles
            num_variables = len(variables)
            particles = np.random.rand(num_particles, num_variables)
            velocities = np.random.rand(num_particles, num_variables) * 0.1

            # Scale particles to bounds
            for i, var in enumerate(variables):
                min_val, max_val = bounds[var]
                particles[:, i] = particles[:, i] * (max_val - min_val) + min_val

            # Initialize personal bests
            personal_best_positions = particles.copy()
            personal_best_fitness = np.array([obj_func(*particle) for particle in particles])

            # Initialize global best
            global_best_idx = np.argmin(personal_best_fitness)
            global_best_position = personal_best_positions[global_best_idx].copy()
            global_best_fitness = personal_best_fitness[global_best_idx]

            # Track convergence
            fitness_history = [global_best_fitness]

            for iteration in range(max_iterations):
                for i in range(num_particles):
                    # Update velocity
                    r1, r2 = np.random.rand(2)
                    cognitive_component = cognitive_weight * r1 * (personal_best_positions[i] - particles[i])
                    social_component = social_weight * r2 * (global_best_position - particles[i])
                    velocities[i] = inertia_weight * velocities[i] + cognitive_component + social_component

                    # Update position
                    particles[i] += velocities[i]

                    # Apply bounds
                    for j, var in enumerate(variables):
                        min_val, max_val = bounds[var]
                        particles[i, j] = np.clip(particles[i, j], min_val, max_val)

                    # Evaluate fitness
                    fitness = obj_func(*particles[i])

                    # Update personal best
                    if fitness < personal_best_fitness[i]:
                        personal_best_positions[i] = particles[i].copy()
                        personal_best_fitness[i] = fitness

                        # Update global best
                        if fitness < global_best_fitness:
                            global_best_position = particles[i].copy()
                            global_best_fitness = fitness

                fitness_history.append(global_best_fitness)

            return {
                'optimal_value': float(global_best_fitness),
                'optimal_variables': {var: float(val) for var, val in zip(variables, global_best_position)},
                'status': 'optimal',
                'method': 'particle_swarm_optimization',
                'iterations': max_iterations,
                'particles': num_particles,
                'fitness_history': fitness_history,
                'convergence': len(fitness_history) > 10 and abs(fitness_history[-1] - fitness_history[-10]) < 1e-6
            }

        except MathematicsError as e:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': f"Particle swarm optimization failed: {str(e)}",
                'method': 'particle_swarm_optimization'
            }

    def convex_optimization(self, objective: str, variables: List[str],
                           constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Solve convex optimization problem using CVXPY
        """
        if cp is None:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': 'CVXPY not available. Install with: pip install cvxpy'
            }
        
        try:
            # Create variables
            vars_dict = {var: cp.Variable() for var in variables}
            
            # Parse objective (simplified - would need more sophisticated parsing)
            # For now, handle simple quadratic objectives
            if 'x**2' in objective:
                obj = cp.Minimize(vars_dict[variables[0]]**2)
            else:
                obj = cp.Minimize(vars_dict[variables[0]])
            
            # Parse constraints (simplified)
            constraints_list = []
            if constraints:
                for constraint in constraints:
                    if '<=' in constraint:
                        left, right = constraint.split('<=')
                        constraints_list.append(vars_dict[variables[0]] <= float(right.strip()))
                    elif '>=' in constraint:
                        left, right = constraint.split('>=')
                        constraints_list.append(vars_dict[variables[0]] >= float(right.strip()))
            
            # Solve
            prob = cp.Problem(obj, constraints_list)
            prob.solve()
            
            return {
                'optimal_value': prob.value,
                'optimal_variables': {var: vars_dict[var].value for var in variables} if prob.status == 'optimal' else None,
                'status': prob.status,
                'message': f"Problem solved with status: {prob.status}"
            }
        except MathematicsError as e:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': str(e)
            }
    
    def quadratic_programming(self, Q: List[List[float]], c: List[float], 
                             A: List[List[float]], b: List[float]) -> Dict[str, Any]:
        """
        Solve quadratic programming problem: min 0.5 x^T Q x + c^T x subject to A x <= b
        """
        if cp is None:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': 'CVXPY not available for quadratic programming'
            }
        
        try:
            n = len(c)
            x = cp.Variable((n, 1))
            
            # Objective
            objective = cp.Minimize(0.5 * cp.quad_form(x, cp.Constant(Q)) + cp.Constant(c) @ x)
            
            # Constraints
            constraints = [cp.Constant(np.array(A)) @ x <= cp.Constant(np.array(b))]
            
            # Solve
            prob = cp.Problem(objective, constraints)
            prob.solve()
            
            return {
                'optimal_value': prob.value,
                'optimal_variables': x.value.flatten().tolist() if prob.status == 'optimal' and x.value is not None else None,
                'status': prob.status,
                'message': f"Quadratic program solved with status: {prob.status}"
            }
        except MathematicsError as e:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': str(e)
            }

    def get_optimization_methods(self) -> List[str]:
        """Get list of supported optimization methods"""
        return self.supported_methods
    
    def solve_optimization_problem(self, problem_type: str, **kwargs) -> Dict[str, Any]:
        """
        Solve optimization problem based on type
        """
        if problem_type == 'linear_programming':
            return self.linear_programming(**kwargs)
        elif problem_type == 'nonlinear_optimization':
            return self.nonlinear_optimization(**kwargs)
        elif problem_type == 'convex_optimization':
            return self.convex_optimization(**kwargs)
        elif problem_type == 'quadratic_programming':
            return self.quadratic_programming(**kwargs)
        elif problem_type == 'global_optimization':
            return self.global_optimization(**kwargs)
        else:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': f'Unsupported optimization method: {problem_type}'
            }
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process optimization request - required for workflow orchestration
        """
        try:
            problem_type = request_data.get('problem_type', 'nonlinear_optimization')
            return self.solve_optimization_problem(problem_type, **request_data)
        except MathematicsError as e:
            return {
                'optimal_value': None,
                'optimal_variables': None,
                'status': 'error',
                'message': str(e)
            }





