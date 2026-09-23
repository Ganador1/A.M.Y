# Facade de servicios para el dominio Mathematics
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.exceptions.domain.mathematics import MathematicsError
from .mathematical_computation import (
    SymbolicMath,
    NumericalMath,
    LinearAlgebra,
    SpecialFunctions,
    StatisticalMath,
)

# Importar servicios de forma resiliente para evitar cargas pesadas en import-time
from .calculus_service import CalculusService

# Optional compatibility exports are resolved on first explicit access. Importing
# calculus must not instantiate SymbolicAIService or contact Hugging Face before
# the deterministic Atlas worker can answer its startup ping.
from importlib import import_module

_LAZY_CLASSES = {
    "ArithmeticService": "arithmetic_service",
    "EquationService": "equation_service",
    "StatisticsService": "statistics_service",
    "GraphingService": "graphing_service",
    "TopologyService": "topology_service",
    "AdvancedSymPyService": "advanced_sympy_service",
    "SageMathService": "sagemath_service",
    "JuliaService": "julia_service",
    "SymEngineService": "symengine_service",
    "MathematicalDiscoveryEngine": "discovery_engine",
    "AdvancedTopologyService": "advanced_topology_service",
    "QuantumMathematicsService": "quantum_math_service",
    "MathematicalMLService": "math_ml_service",
    "MathVisualizationService": "math_visualization_service",
    "AdvancedMathAIService": "advanced_math_ai_service",
    "AdvancedNumberTheoryService": "advanced_number_theory_service",
    "AutomatedTheoremProvingService": "automated_theorem_proving_service",
    "DistributedComputingService": "distributed_computing_service",
    "DifferentialEquationService": "differential_equations_service",
    "NumberTheoryService": "number_theory_service",
    "CombinatoricsService": "combinatorics_service",
    "AdvancedAlgebraService": "advanced_algebra_service",
    "GPUMathService": "gpu_math_service",
    "SymbolicAIService": "symbolic_ai_service",
    "AdvancedVisualizationService": "advanced_visualization_service",
    "BioinformaticsService": "bioinformatics_service",
    "AdvancedQuantumService": "advanced_quantum_service",
    "FinancialMathematicsService": "financial_mathematics_service",
    "VRARVisualizationService": "vr_ar_visualization_service",
}
_LAZY_INSTANCES = {module: name for name, module in _LAZY_CLASSES.items()}
calculus_service = CalculusService()


def __getattr__(name: str):
    if name not in _LAZY_CLASSES and name not in _LAZY_INSTANCES and name != "mathematics_service_manager":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        if name in _LAZY_CLASSES:
            module = import_module(f".{_LAZY_CLASSES[name]}", __name__)
            value = getattr(module, name)
            # Python also publishes imported submodules on their parent. These
            # names historically expose service instances, not module objects;
            # keep them absent until their own lazy instance lookup occurs.
            module_alias = _LAZY_CLASSES[name]
            if globals().get(module_alias) is module:
                globals().pop(module_alias)
        elif name in _LAZY_INSTANCES:
            class_name = _LAZY_INSTANCES[name]
            service_type = globals().get(class_name) or __getattr__(class_name)
            value = service_type() if service_type is not None else None
        else:
            value = import_module(".service_manager", __name__).mathematics_service_manager
    except Exception:
        # Preserve the facade's existing unavailable-service convention while
        # preventing one optional import failure from erasing unrelated exports.
        value = None
    globals()[name] = value
    return value


__all__ = [
    "SymbolicMath", "NumericalMath", "LinearAlgebra", "SpecialFunctions", "StatisticalMath",
    "CalculusService", "calculus_service", "ComputationFacade", "AnalysisFacade",
    "computation", "analysis", "mathematics_service_manager",
    *_LAZY_CLASSES, *_LAZY_INSTANCES,
]

class ComputationFacade:
    async def execute_computation(
        self,
        operation: str,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatcher simple para operaciones de cómputo matemático"""
        op = (operation or "").lower()
        try:
            if op == "solve_equation":
                eq = parameters.get("equation")
                var = parameters.get("variable", "x")
                solutions = SymbolicMath.solve_equation(eq or "0", var)
                return {"operation": op, "solutions": solutions}

            if op == "differentiate":
                expr = parameters.get("expression", "x")
                var = parameters.get("variable", "x")
                order = int(parameters.get("order", 1))
                deriv = SymbolicMath.differentiate(expr, var, order)
                return {"operation": op, "derivative": deriv}

            if op == "integrate_symbolic":
                expr = parameters.get("expression", "x")
                var = parameters.get("variable", "x")
                limits = parameters.get("limits")
                integ = SymbolicMath.integrate_symbolic(expr, var, limits)
                return {"operation": op, "integral": integ}

            if op == "series_expansion":
                expr = parameters.get("expression", "x")
                var = parameters.get("variable", "x")
                point = parameters.get("point", 0)
                order = int(parameters.get("order", 5))
                series = SymbolicMath.series_expansion(expr, var, point, order)
                return {"operation": op, "series": series}

            if op == "matrix_operation":
                A = parameters.get("A", [])
                B = parameters.get("B")
                mop = parameters.get("matrix_op", "eigenvalues")
                result = LinearAlgebra.matrix_operations(A, B, mop)
                return {"operation": op, "result": result}

            if op == "solve_linear_system":
                A = parameters.get("A", [])
                b = parameters.get("b", [])
                result = LinearAlgebra.solve_linear_system(A, b)
                return {"operation": op, "result": result}

            if op == "descriptive_statistics":
                data = parameters.get("data", [])
                stats = StatisticalMath.descriptive_statistics(data)
                return {"operation": op, "statistics": stats}

            # Fallback desconocido
            return {
                "operation": op,
                "parameters": parameters,
                "message": "Unknown operation",
            }
        except MathematicsError as e:
            return {"operation": op, "error": str(e)}


class AnalysisFacade:
    async def execute_analysis(
        self,
        data: Dict[str, Any],
        analysis_type: str,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analítica básica para el dominio de matemáticas"""
        atype = (analysis_type or "").lower()
        try:
            if atype == "descriptive_statistics":
                values = data.get("values", [])
                stats = StatisticalMath.descriptive_statistics(values)
                return {"analysis": atype, "statistics": stats}

            # Otras analíticas futuras
            return {
                "analysis": atype,
                "data": data,
                "parameters": parameters,
                "message": "Unknown analysis type",
            }
        except MathematicsError as e:
            return {"analysis": atype, "error": str(e)}


# Instancias esperadas por los routers
computation = ComputationFacade()
analysis = AnalysisFacade()
