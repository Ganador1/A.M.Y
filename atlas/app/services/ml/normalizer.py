"""
Expression Normalizer Service
Normaliza y parsea expresiones matemáticas para análisis y manipulación
"""

import re
from typing import Dict, Any, List, Union
from abc import ABC, abstractmethod
from app.exceptions.base import AtlasException


class ExprNode(ABC):
    """Nodo base del AST de expresiones"""

    @abstractmethod
    def to_string(self) -> str:
        """Convertir a string"""
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, variables: Dict[str, Any]) -> Any:
        """Evaluar con valores de variables"""
        raise NotImplementedError


class Variable(ExprNode):
    """Nodo de variable"""

    def __init__(self, name: str, sort: str = "Real"):
        self.name = name
        self.sort = sort  # "Real", "Int", "Bool"

    def to_string(self) -> str:
        return self.name

    def evaluate(self, variables: Dict[str, Any]) -> Any:
        return variables.get(self.name, 0)

    def __repr__(self):
        return f"Variable({self.name}, {self.sort})"


class Constant(ExprNode):
    """Nodo de constante"""

    def __init__(self, value: Union[int, float, bool]):
        self.value = value

    def to_string(self) -> str:
        return str(self.value)

    def evaluate(self, variables: Dict[str, Any]) -> Any:
        return self.value

    def __repr__(self):
        return f"Constant({self.value})"


class BinaryOp(ExprNode):
    """Operación binaria"""

    def __init__(self, left: ExprNode, op: str, right: ExprNode):
        self.left = left
        self.op = op
        self.right = right

    def to_string(self) -> str:
        return f"({self.left.to_string()} {self.op} {self.right.to_string()})"

    def evaluate(self, variables: Dict[str, Any]) -> Any:
        left_val = self.left.evaluate(variables)
        right_val = self.right.evaluate(variables)

        if self.op == "+":
            return left_val + right_val
        elif self.op == "-":
            return left_val - right_val
        elif self.op == "*":
            return left_val * right_val
        elif self.op == "/":
            return left_val / right_val if right_val != 0 else float('inf')
        elif self.op == "**":
            return left_val ** right_val
        elif self.op == "and":
            return left_val and right_val
        elif self.op == "or":
            return left_val or right_val
        else:
            raise ValueError(f"Unknown operator: {self.op}")

    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op}, {self.right})"


class Comparison(ExprNode):
    """Operación de comparación"""

    def __init__(self, left: ExprNode, op: str, right: ExprNode):
        self.left = left
        self.op = op
        self.right = right

    def to_string(self) -> str:
        return f"({self.left.to_string()} {self.op} {self.right.to_string()})"

    def evaluate(self, variables: Dict[str, Any]) -> Any:
        left_val = self.left.evaluate(variables)
        right_val = self.right.evaluate(variables)

        if self.op == "==":
            return left_val == right_val
        elif self.op == "!=":
            return left_val != right_val
        elif self.op == "<":
            return left_val < right_val
        elif self.op == "<=":
            return left_val <= right_val
        elif self.op == ">":
            return left_val > right_val
        elif self.op == ">=":
            return left_val >= right_val
        else:
            raise ValueError(f"Unknown comparison operator: {self.op}")

    def __repr__(self):
        return f"Comparison({self.left}, {self.op}, {self.right})"


class ExpressionNormalizer:
    """Normalizador de expresiones matemáticas"""

    def __init__(self):
        self.variables: Dict[str, Variable] = {}

    def from_python(self, expression: str) -> ExprNode:
        """
        Parsear expresión Python a AST
        Implementación simplificada para expresiones matemáticas básicas
        """
        # Limpiar la expresión
        expr = expression.strip()

        # Extraer variables usando regex
        var_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        potential_vars = re.findall(var_pattern, expr)

        # Filtrar palabras clave y funciones
        keywords = {'and', 'or', 'not', 'if', 'else', 'for', 'while', 'def', 'class', 'import', 'from', 'True', 'False', 'None'}
        variables_found = [v for v in potential_vars if v not in keywords and not v.isdigit()]

        # Crear variables
        for var_name in variables_found:
            if var_name not in self.variables:
                self.variables[var_name] = Variable(var_name)

        # Parseo simplificado - convertir a evaluación segura
        # NOTA: Esta es una implementación básica. En producción usar un parser real.
        try:
            # Intentar evaluar como expresión simple
            if "==" in expr:
                left, right = expr.split("==", 1)
                return Comparison(
                    self._parse_simple_expr(left.strip()),
                    "==",
                    self._parse_simple_expr(right.strip())
                )
            elif "!=" in expr:
                left, right = expr.split("!=", 1)
                return Comparison(
                    self._parse_simple_expr(left.strip()),
                    "!=",
                    self._parse_simple_expr(right.strip())
                )
            elif "<=" in expr:
                left, right = expr.split("<=", 1)
                return Comparison(
                    self._parse_simple_expr(left.strip()),
                    "<=",
                    self._parse_simple_expr(right.strip())
                )
            elif ">=" in expr:
                left, right = expr.split(">=", 1)
                return Comparison(
                    self._parse_simple_expr(left.strip()),
                    ">=",
                    self._parse_simple_expr(right.strip())
                )
            elif "<" in expr:
                left, right = expr.split("<", 1)
                return Comparison(
                    self._parse_simple_expr(left.strip()),
                    "<",
                    self._parse_simple_expr(right.strip())
                )
            elif ">" in expr:
                left, right = expr.split(">", 1)
                return Comparison(
                    self._parse_simple_expr(left.strip()),
                    ">",
                    self._parse_simple_expr(right.strip())
                )
            else:
                # Expresión sin comparación
                return self._parse_simple_expr(expr)

        except AtlasException:
            # Fallback: devolver una variable dummy
            return Variable("x", "Real")

    def _parse_simple_expr(self, expr: str) -> ExprNode:
        """Parsear expresión simple (sin comparación)"""
        expr = expr.strip()

        # Intentar parsear como número
        try:
            if "." in expr or "e" in expr.lower():
                return Constant(float(expr))
            else:
                return Constant(int(expr))
        except ValueError:
            pass

        # Verificar si es una variable
        if expr in self.variables:
            return self.variables[expr]

        # Verificar si es True/False
        if expr == "True":
            return Constant(True)
        elif expr == "False":
            return Constant(False)

        # Parseo básico de operaciones binarias
        ops = ["+", "-", "*", "/", "**", "and", "or"]
        for op in ops:
            if op in expr:
                parts = expr.split(op, 1)
                if len(parts) == 2:
                    left = self._parse_simple_expr(parts[0].strip())
                    right = self._parse_simple_expr(parts[1].strip())
                    return BinaryOp(left, op, right)

        # Si no se puede parsear, asumir que es una variable
        if expr and expr[0].isalpha():
            if expr not in self.variables:
                self.variables[expr] = Variable(expr)
            return self.variables[expr]

        # Fallback
        return Constant(0)

    def normalize(self, expression: str) -> str:
        """Normalizar expresión a forma canónica"""
        ast = self.from_python(expression)
        return ast.to_string()

    def extract_variables(self, expression: str) -> List[str]:
        """Extraer nombres de variables de la expresión"""
        ast = self.from_python(expression)
        variables = []

        def traverse(node):
            if isinstance(node, Variable):
                if node.name not in variables:
                    variables.append(node.name)
            elif hasattr(node, '__dict__'):
                for attr_value in node.__dict__.values():
                    if isinstance(attr_value, ExprNode):
                        traverse(attr_value)
                    elif isinstance(attr_value, list):
                        for item in attr_value:
                            if isinstance(item, ExprNode):
                                traverse(item)

        traverse(ast)
        return variables
