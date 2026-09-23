"""
Arithmetic Service for Mathematics Domain

Servicio para operaciones aritméticas básicas y avanzadas.
"""

import math
import numpy as np
from typing import List, Dict, Any, Optional
from decimal import Decimal, getcontext
from app.exceptions.domain.mathematics import MathematicsError


from app.services.base_service import BaseService

class ArithmeticService(BaseService):
    """
    Servicio para operaciones aritméticas y funciones matemáticas.
    Proporciona cálculos precisos con soporte para diferentes formatos numéricos.
    """

    def __init__(self):
        super().__init__("ArithmeticService")
        self.supported_operations = [
            'add', 'subtract', 'multiply', 'divide',
            'power', 'sqrt', 'log', 'ln', 'exp',
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
            'factorial', 'abs', 'round', 'floor', 'ceil'
        ]

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a service request.
        """
        operation = request_data.get("operation")
        operands = request_data.get("operands", [])
        precision = request_data.get("precision", 6)
        
        if not operation:
            return {"success": False, "error": "Operation required"}
            
        return self.calculate(operation, operands, precision)

    def calculate(self, operation: str, operands: List[float], precision: int = 6) -> Dict[str, Any]:
        """
        Realiza una operación aritmética
        """
        if operation not in self.supported_operations:
            return {
                "success": False,
                "error": f"Unsupported operation: {operation}",
                "available_operations": self.supported_operations
            }

        if not operands:
            return {"success": False, "error": "No operands provided"}

        try:
            # Use local decimal context when needed (do not mutate global context)

            if operation in ['add', 'subtract', 'multiply', 'divide']:
                result = self._basic_arithmetic(operation, operands)
            elif operation in ['power', 'sqrt']:
                result = self._power_operations(operation, operands)
            elif operation in ['log', 'ln', 'exp']:
                result = self._exponential_operations(operation, operands)
            elif operation in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']:
                result = self._trigonometric_operations(operation, operands)
            elif operation == 'factorial':
                result = self._factorial_operation(operands)
            else:
                result = self._other_operations(operation, operands)

            # Formatear resultado
            formatted_result = self._format_result(result, precision)

            return {
                "success": True,
                "operation": operation,
                "operands": operands,
                "result": float(result),
                "formatted_result": formatted_result,
                "precision": precision
            }

        except MathematicsError as e:
            return {
                "success": False,
                "error": f"Calculation error: {str(e)}",
                "operation": operation,
                "operands": operands
            }

    def batch_calculate(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Realiza múltiples operaciones aritméticas
        """
        results = []
        successful = 0
        failed = 0

        for op in operations:
            result = self.calculate(
                op.get('operation', ''),
                op.get('operands', []),
                op.get('precision', 6)
            )
            results.append(result)

            if result['success']:
                successful += 1
            else:
                failed += 1

        return {
            "total_operations": len(operations),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    def get_operations_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre operaciones disponibles
        """
        categories = {
            "basic": ['add', 'subtract', 'multiply', 'divide'],
            "power": ['power', 'sqrt'],
            "exponential": ['log', 'ln', 'exp'],
            "trigonometric": ['sin', 'cos', 'tan', 'asin', 'acos', 'atan'],
            "special": ['factorial', 'abs', 'round', 'floor', 'ceil']
        }

        return {
            "total_operations": len(self.supported_operations),
            "categories": categories,
            "operations": self.supported_operations
        }

    def _basic_arithmetic(self, operation: str, operands: List[float]) -> float:
        """Operaciones aritméticas básicas"""
        if operation == 'add':
            return sum(operands)
        elif operation == 'subtract':
            if len(operands) < 2:
                raise ValueError("Subtraction requires at least 2 operands")
            result = operands[0]
            for op in operands[1:]:
                result -= op
            return result
        elif operation == 'multiply':
            result = 1.0
            for op in operands:
                result *= op
            return result
        elif operation == 'divide':
            if len(operands) < 2:
                raise ValueError("Division requires at least 2 operands")
            result = operands[0]
            for op in operands[1:]:
                if op == 0:
                    raise ZeroDivisionError("Division by zero")
                result /= op
            return result

    def _power_operations(self, operation: str, operands: List[float]) -> float:
        """Operaciones de potencia"""
        if operation == 'power':
            if len(operands) != 2:
                raise ValueError("Power operation requires exactly 2 operands")
            return operands[0] ** operands[1]
        elif operation == 'sqrt':
            if len(operands) != 1:
                raise ValueError("Square root requires exactly 1 operand")
            if operands[0] < 0:
                raise ValueError("Square root of negative number")
            return math.sqrt(operands[0])

    def _exponential_operations(self, operation: str, operands: List[float]) -> float:
        """Operaciones exponenciales y logarítmicas"""
        if len(operands) != 1:
            raise ValueError("Exponential operations require exactly 1 operand")

        if operation == 'exp':
            return math.exp(operands[0])
        elif operation == 'log':
            if operands[0] <= 0:
                raise ValueError("Logarithm requires positive number")
            return math.log10(operands[0])
        elif operation == 'ln':
            if operands[0] <= 0:
                raise ValueError("Natural logarithm requires positive number")
            return math.log(operands[0])

    def _trigonometric_operations(self, operation: str, operands: List[float]) -> float:
        """Operaciones trigonométricas (ángulos en grados)"""
        if len(operands) != 1:
            raise ValueError("Trigonometric operations require exactly 1 operand")

        angle_rad = math.radians(operands[0])  # Convertir a radianes

        if operation == 'sin':
            return math.sin(angle_rad)
        elif operation == 'cos':
            return math.cos(angle_rad)
        elif operation == 'tan':
            return math.tan(angle_rad)
        elif operation == 'asin':
            if not -1 <= operands[0] <= 1:
                raise ValueError("Arcsin requires input between -1 and 1")
            result = math.asin(operands[0])
            return math.degrees(result)  # Convertir de vuelta a grados
        elif operation == 'acos':
            if not -1 <= operands[0] <= 1:
                raise ValueError("Arccos requires input between -1 and 1")
            result = math.acos(operands[0])
            return math.degrees(result)
        elif operation == 'atan':
            result = math.atan(operands[0])
            return math.degrees(result)

    def _factorial_operation(self, operands: List[float]) -> float:
        """Operación factorial"""
        if len(operands) != 1:
            raise ValueError("Factorial requires exactly 1 operand")

        n = operands[0]
        if not n.is_integer() or n < 0:
            raise ValueError("Factorial requires non-negative integer")

        return math.factorial(int(n))

    def _other_operations(self, operation: str, operands: List[float]) -> float:
        """Otras operaciones matemáticas"""
        if len(operands) != 1:
            raise ValueError("Operation requires exactly 1 operand")

        value = operands[0]

        if operation == 'abs':
            return abs(value)
        elif operation == 'round':
            return round(value)
        elif operation == 'floor':
            return math.floor(value)
        elif operation == 'ceil':
            return math.ceil(value)

    def _format_result(self, result: float, precision: int) -> str:
        """Formatea el resultado numérico"""
        if abs(result) < 1e-10:
            return "0.0"
        elif abs(result) > 1e10:
            return ".2e"
        else:
            return f"{result:.{precision}f}"






