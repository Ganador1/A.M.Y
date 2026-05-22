# Lightweight package initialization for the mathematics domain.
# Avoid importing heavy optional dependencies at package import time to prevent
# import-time failures in environments where SciPy, scikit-learn, etc., are
# not available or incompatible (tests mock many modules).
from .services.calculus_service import CalculusService

# Expose the core/lightweight services and provide placeholders for the rest.
calculus_service = CalculusService()

# Lazy placeholders for optional/advanced services
arithmetic_service = None
statistics_service = None
advanced_algebra_service = None
number_theory_service = None
optimization_service = None
differential_equations_service = None
topology_service = None
mathematical_discovery_engine = None
quantum_math_service = None
gpu_math_service = None
symbolic_ai_service = None
advanced_visualization_service = None