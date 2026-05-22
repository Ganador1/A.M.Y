"""Compatibility shim: expose the public API expected by tests.
This module delegates to `differential_equations_fixed` implementation.
"""
from .differential_equations_fixed import DifferentialEquationService, PDESolver

__all__ = ["DifferentialEquationService", "PDESolver"]
