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

# Cargar el resto de servicios de forma segura (pueden requerir libs pesadas como SciPy/sklearn)
try:
    from .arithmetic_service import ArithmeticService  # Servicio principal más completo
    from .equation_service import EquationService
    from .statistics_service import StatisticsService
    from .graphing_service import GraphingService
    from .topology_service import TopologyService
    from .advanced_sympy_service import AdvancedSymPyService
    from .sagemath_service import SageMathService
    from .julia_service import JuliaService
    from .symengine_service import SymEngineService
    from .discovery_engine import MathematicalDiscoveryEngine
    from .advanced_topology_service import AdvancedTopologyService
    from .quantum_math_service import QuantumMathematicsService
    from .math_ml_service import MathematicalMLService
    from .math_visualization_service import MathVisualizationService
    from .advanced_math_ai_service import AdvancedMathAIService
    from .advanced_number_theory_service import AdvancedNumberTheoryService
    from .automated_theorem_proving_service import AutomatedTheoremProvingService
    from .distributed_computing_service import DistributedComputingService
    from .differential_equations_service import DifferentialEquationService
    from .number_theory_service import NumberTheoryService
    from .combinatorics_service import CombinatoricsService
    from .service_manager import mathematics_service_manager
    from .advanced_algebra_service import AdvancedAlgebraService
    from .gpu_math_service import GPUMathService
    from .symbolic_ai_service import SymbolicAIService
    from .advanced_visualization_service import AdvancedVisualizationService
    from .bioinformatics_service import BioinformaticsService
    from .advanced_quantum_service import AdvancedQuantumService
    from .financial_mathematics_service import FinancialMathematicsService
    from .vr_ar_visualization_service import VRARVisualizationService
except Exception:
    # Fall back to minimal placeholders to avoid breaking imports during tests
    ArithmeticService = None
    EquationService = None
    StatisticsService = None
    GraphingService = None
    TopologyService = None
    AdvancedSymPyService = None
    SageMathService = None
    JuliaService = None
    SymEngineService = None
    MathematicalDiscoveryEngine = None
    AdvancedTopologyService = None
    QuantumMathematicsService = None
    MathematicalMLService = None
    MathVisualizationService = None
    AdvancedMathAIService = None
    AdvancedNumberTheoryService = None
    AutomatedTheoremProvingService = None
    DistributedComputingService = None
    DifferentialEquationService = None
    NumberTheoryService = None
    CombinatoricsService = None
    mathematics_service_manager = None
    AdvancedAlgebraService = None
    GPUMathService = None
    SymbolicAIService = None
    AdvancedVisualizationService = None
    BioinformaticsService = None
    AdvancedQuantumService = None
    FinancialMathematicsService = None
    VRARVisualizationService = None

# Instancias de servicios especializados (cargar solo los que existen)
arithmetic_service = ArithmeticService() if ArithmeticService is not None else None
equation_service = EquationService() if EquationService is not None else None
calculus_service = CalculusService()
statistics_service = StatisticsService() if StatisticsService is not None else None
graphing_service = GraphingService() if GraphingService is not None else None
topology_service = TopologyService() if TopologyService is not None else None
advanced_sympy_service = AdvancedSymPyService() if AdvancedSymPyService is not None else None
sagemath_service = SageMathService() if SageMathService is not None else None
julia_service = JuliaService() if JuliaService is not None else None
symengine_service = SymEngineService() if SymEngineService is not None else None
discovery_engine = MathematicalDiscoveryEngine() if MathematicalDiscoveryEngine is not None else None
advanced_topology_service = AdvancedTopologyService() if AdvancedTopologyService is not None else None
quantum_math_service = QuantumMathematicsService() if QuantumMathematicsService is not None else None
math_ml_service = MathematicalMLService() if MathematicalMLService is not None else None
math_visualization_service = MathVisualizationService() if MathVisualizationService is not None else None
advanced_math_ai_service = AdvancedMathAIService() if AdvancedMathAIService is not None else None
advanced_number_theory_service = AdvancedNumberTheoryService() if AdvancedNumberTheoryService is not None else None
automated_theorem_proving_service = AutomatedTheoremProvingService() if AutomatedTheoremProvingService is not None else None
distributed_computing_service = DistributedComputingService() if DistributedComputingService is not None else None
differential_equations_service = DifferentialEquationService() if DifferentialEquationService is not None else None
number_theory_service = NumberTheoryService() if NumberTheoryService is not None else None
combinatorics_service = CombinatoricsService() if CombinatoricsService is not None else None
advanced_algebra_service = AdvancedAlgebraService() if AdvancedAlgebraService is not None else None
gpu_math_service = GPUMathService() if GPUMathService is not None else None
symbolic_ai_service = SymbolicAIService() if SymbolicAIService is not None else None
advanced_visualization_service = AdvancedVisualizationService() if AdvancedVisualizationService is not None else None
bioinformatics_service = BioinformaticsService() if BioinformaticsService is not None else None
advanced_quantum_service = AdvancedQuantumService() if AdvancedQuantumService is not None else None
financial_mathematics_service = FinancialMathematicsService() if FinancialMathematicsService is not None else None
vr_ar_visualization_service = VRARVisualizationService() if VRARVisualizationService is not None else None


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