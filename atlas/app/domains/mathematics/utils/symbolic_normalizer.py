"""Symbolic Expression Normalizer for Mathematical Analysis

Proporciona herramientas para normalización de expresiones simbólicas:
- AST interno simplificado (Variable, Constant, BinaryOp, UnaryOp, FunctionCall, Comparison, Quantifier)
- Conversión desde expresiones SymPy (si está disponible)
- Conversión a representación SMT-LIB fragmento básico
- Normalización y canonicalización determinista (para hashing y bridges)

Limitaciones iniciales:
- Soporta operaciones aritméticas básicas: + - * / **
- Relaciones: = != < <= > >=
- Booleanas: and or not -> =>
- Cuantificadores simples: forall, exists (como nodos estructurales; SMT output placeholder)

Uso principal:
- Puente para convertir conjeturas en texto o SymPy a AST normalizado
- Preparar entrada para Z3 con una traducción segura y controlada

Esta versión es deliberadamente ligera para iteración rápida.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Dict, Union
import math
from app.exceptions.domain.mathematics import MathematicsError

try:  # SymPy es opcional
    import sympy as sp  # type: ignore
    SYMPY_AVAILABLE = True
except MathematicsError:  # pragma: no cover
    sp = None  # type: ignore
    SYMPY_AVAILABLE = False

# ---- AST Node Definitions -------------------------------------------------------
@dataclass(frozen=True)
class ExprNode:
    def to_smt(self) -> str:  # pragma: no cover (override required)
        raise NotImplementedError

@dataclass(frozen=True)
class Variable(ExprNode):
    name: str
    sort: str = "Real"  # Real, Int, Bool
    def to_smt(self) -> str:
        return self.name

@dataclass(frozen=True)
class Constant(ExprNode):
    value: Union[int, float, bool]
    def to_smt(self) -> str:
        if isinstance(self.value, bool):
            return "true" if self.value else "false"
        if isinstance(self.value, (int, float)) and math.isfinite(float(self.value)):
            return str(self.value)
        raise ValueError("Unsupported constant value")

@dataclass(frozen=True)
class UnaryOp(ExprNode):
    op: str
    arg: ExprNode
    def to_smt(self) -> str:
        if self.op == "-":
            return f"(- {self.arg.to_smt()})"
        if self.op == "not":
            return f"(not {self.arg.to_smt()})"
        raise ValueError(f"Unsupported unary op {self.op}")

@dataclass(frozen=True)
class BinaryOp(ExprNode):
    op: str
    left: ExprNode
    right: ExprNode
    def to_smt(self) -> str:
        mapping = {"+": "+", "-": "-", "*": "*", "/": "/", "**": "pow", "and": "and", "or": "or", "->": "=>", "=>": "=>"}
        if self.op not in mapping:
            raise ValueError(f"Unsupported binary op {self.op}")
        smt_op = mapping[self.op]
        if smt_op == "pow":  # encode pow as (pow a b) placeholder
            return f"(pow {self.left.to_smt()} {self.right.to_smt()})"
        return f"({smt_op} {self.left.to_smt()} {self.right.to_smt()})"

@dataclass(frozen=True)
class Comparison(ExprNode):
    op: str
    left: ExprNode
    right: ExprNode
    def to_smt(self) -> str:
        mapping = {"=": "=", "==": "=", "!=": "distinct", "<": "<", "<=": "<=", ">": ">", ">=": ">="}
        if self.op not in mapping:
            raise ValueError(f"Unsupported comparison {self.op}")
        smt_op = mapping[self.op]
        if smt_op == "distinct":
            return f"(distinct {self.left.to_smt()} {self.right.to_smt()})"
        return f"({smt_op} {self.left.to_smt()} {self.right.to_smt()})"

@dataclass(frozen=True)
class FunctionCall(ExprNode):
    name: str
    args: List[ExprNode] = field(default_factory=list)
    def to_smt(self) -> str:
        if self.name == "abs" and len(self.args) == 1:
            # encode |x| as (ite (>= x 0) x (- x)) simplified form
            x = self.args[0].to_smt()
            return f"(ite (>= {x} 0) {x} (- {x}))"
        inner = " ".join(a.to_smt() for a in self.args)
        return f"({self.name} {inner})"

@dataclass(frozen=True)
class Quantifier(ExprNode):
    kind: str  # forall | exists
    variables: List[Variable]
    body: ExprNode
    def to_smt(self) -> str:
        vars_decl = " ".join(f"({v.name} {v.sort})" for v in self.variables)
        if self.kind not in ("forall", "exists"):
            raise ValueError("Unsupported quantifier kind")
        return f"({self.kind} ({vars_decl}) {self.body.to_smt()})"

# ---- Normalizer ---------------------------------------------------------------
class SymbolicExpressionNormalizer:
    def __init__(self) -> None:
        self._var_cache: Dict[str, Variable] = {}

    # Public API
    def from_sympy(self, expr: Any) -> ExprNode:
        if not SYMPY_AVAILABLE:
            raise RuntimeError("SymPy no disponible")
        return self._convert_sympy(expr)

    def from_python(self, statement: str, domain: Dict[str, str] | None = None) -> ExprNode:
        """
        Convierte una expresión en formato de cadena Python/SymPy a un AST normalizado.
        Utiliza SymPy para el parsing inicial.
        """
        if not SYMPY_AVAILABLE or sp is None:  # extra guard para linters
            raise RuntimeError("SymPy no disponible, no se puede procesar la cadena.")

        # Permitir que domain sea opcional para compatibilidad retroactiva con llamadas que
        # no proporcionan información explícita de tipos (p.ej. uso interno en servicios).
        if domain is None:
            domain = {}

        # Crear los símbolos de SymPy con la información de dominio (aunque no se use en `sympify`)
        # Esto es importante para que el conversor a SMT conozca los tipos.
        local_scope: Dict[str, Any] = {}
        for var_name, sort in domain.items():
            self.variable(var_name, sort=sort.capitalize())  # Asegura que el tipo se registre
            local_scope[var_name] = sp.Symbol(var_name)

        # Usar sympify para parsear la cadena de forma segura
        sympy_expr = sp.sympify(statement, locals=local_scope)  # type: ignore[arg-type]

        # Convertir la expresión de SymPy a nuestro AST interno
        return self._convert_sympy(sympy_expr)

    def variable(self, name: str, sort: str = "Real") -> Variable:
        if name not in self._var_cache:
            self._var_cache[name] = Variable(name=name, sort=sort)
        return self._var_cache[name]

    def get_variable_names(self) -> List[str]:
        """Devuelve lista de nombres de variables registradas."""
        return list(self._var_cache.keys())

    # SMT-LIB wrapper helper
    def to_smt_script(self, expr: ExprNode) -> str:
        decls = []
        for v in self._var_cache.values():
            decls.append(f"(declare-fun {v.name} () {v.sort})")
        # To prove a theorem, we assert its negation and check for unsatisfiability.
        return "\n".join(decls + [f"(assert (not {expr.to_smt()}))", "(check-sat)"])

    # --- Internal conversion helpers ---
    def _convert_sympy(self, expr: Any) -> ExprNode:  # pragma: no cover (depende SymPy)
        if not SYMPY_AVAILABLE or sp is None:  # pragma: no cover
            raise RuntimeError("SymPy no disponible para conversión interna")
        if isinstance(expr, sp.Symbol):
            return self.variable(str(expr))
        if expr.is_Number:
            return Constant(float(expr))
        if expr.is_Relational:
            op_map = {
                "==": "==", "!=": "!=", "<": "<", "<=": "<=", ">": ">", ">=": ">="
            }
            op = op_map.get(expr.rel_op)
            if op:
                return Comparison(op, self._convert_sympy(expr.lhs), self._convert_sympy(expr.rhs))
        if expr.is_Add:
            args = list(expr.args)
            node = self._convert_sympy(args[0])
            for a in args[1:]:
                node = BinaryOp("+", node, self._convert_sympy(a))
            return node
        if expr.is_Mul:
            args = list(expr.args)
            node = self._convert_sympy(args[0])
            for a in args[1:]:
                node = BinaryOp("*", node, self._convert_sympy(a))
            return node
        if expr.is_Pow:
            base, exp = expr.args
            return BinaryOp("**", self._convert_sympy(base), self._convert_sympy(exp))
        if expr.is_Function:
            return FunctionCall(expr.func.__name__.lower(), [self._convert_sympy(a) for a in expr.args])
        # Boolean and logical operators
        if isinstance(expr, sp.And):
            return BinaryOp("and", self._convert_sympy(expr.args[0]), self._convert_sympy(expr.args[1]))
        if isinstance(expr, sp.Or):
            return BinaryOp("or", self._convert_sympy(expr.args[0]), self._convert_sympy(expr.args[1]))
        if isinstance(expr, sp.Not):
            return UnaryOp("not", self._convert_sympy(expr.args[0]))
        if isinstance(expr, sp.Implies):
            return BinaryOp("=>", self._convert_sympy(expr.args[0]), self._convert_sympy(expr.args[1]))
        raise ValueError(f"Forma SymPy no soportada: {expr}")

# Convenience singleton
symbolic_normalizer_singleton = SymbolicExpressionNormalizer()

__all__ = [
    "ExprNode","Variable","Constant","UnaryOp","BinaryOp","Comparison","FunctionCall","Quantifier","SymbolicExpressionNormalizer","symbolic_normalizer_singleton"
]