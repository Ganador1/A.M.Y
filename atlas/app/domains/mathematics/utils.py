import sympy as sp


def safe_sympify(expr):
    """Safely sympify an expression, raising ValueError on parse errors.

    This helper centralizes SymPy parsing error handling so tests can expect
    ValueError instead of SympifyError during invalid input handling.
    """
    try:
        return sp.sympify(expr)
    except Exception:
        raise ValueError(f"Expresión matemática inválida: {expr}")
