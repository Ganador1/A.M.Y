"""
Arithmetic Operations Service
============================

Servicio completo para operaciones aritméticas básicas y avanzadas.

Este servicio proporciona funcionalidades para realizar cálculos aritméticos
con soporte para operaciones básicas, avanzadas y funciones matemáticas.

Funciones Soportadas:
-------------------
- Operaciones básicas: suma, resta, multiplicación, división
- Potencias y raíces: potencia, raíz cuadrada, raíz n-ésima
- Funciones trigonométricas: sin, cos, tan, etc.
- Funciones hiperbólicas: sinh, cosh, tanh, etc.
- Logaritmos: natural, base 10, logaritmo arbitrario
- Funciones exponenciales: exp, pow
- Operaciones por lotes para múltiples cálculos

Ejemplos de Uso:
---------------
```python
from app.services.arithmetic import ArithmeticService
from app.models import ArithmeticRequest
from app.exceptions.infrastructure.api import APIError

# Suma básica
request = ArithmeticRequest(operation="add", operands=[1, 2, 3])
result = ArithmeticService.calculate(request)
print(result.result)  # 6.0

# Potencia
request = ArithmeticRequest(operation="power", operands=[2, 3])
result = ArithmeticService.calculate(request)
print(result.result)  # 8.0

# Función trigonométrica
request = ArithmeticRequest(operation="sin", operands=[3.14159/2])
result = ArithmeticService.calculate(request)
print(result.result)  # 1.0 (aproximadamente)
```

Limitaciones:
------------
- Máximo 1000 operandos por operación
- Precisión limitada por números de punto flotante
- No soporta números complejos (excepto en funciones específicas)

Notas de Implementación:
----------------------
- Todas las operaciones usan aritmética de punto flotante de doble precisión
- Las funciones trigonométricas esperan ángulos en radianes
- Las operaciones de división verifican división por cero
- Los resultados se redondean a 10 decimales para evitar errores de punto flotante
"""

import math
from typing import List
from app.models import ArithmeticRequest, ArithmeticResponse


class ArithmeticService:
    """
    Servicio completo para operaciones aritméticas.

    Esta clase proporciona métodos estáticos para realizar diversos tipos
    de operaciones aritméticas, desde básicas hasta avanzadas.
    """

    # Operaciones soportadas
    SUPPORTED_OPERATIONS = [
        # Básicas
        "add", "subtract", "multiply", "divide",

        # Potencias y raíces
        "power", "sqrt", "cbrt", "nth_root",

        # Trigonométricas
        "sin", "cos", "tan", "cot", "sec", "csc",
        "asin", "acos", "atan", "acot", "asec", "acsc",

        # Hiperbólicas
        "sinh", "cosh", "tanh", "coth", "sech", "csch",
        "asinh", "acosh", "atanh", "acoth", "asech", "acsch",

        # Logaritmos
        "log", "log10", "log2", "ln",

        # Exponenciales
        "exp", "pow",

        # Otras
        "abs", "factorial", "ceil", "floor", "round"
    ]

    @staticmethod
    def calculate(request: ArithmeticRequest) -> ArithmeticResponse:
        """
        Ejecuta operaciones aritméticas con validación completa.

        Args:
            request: Solicitud que contiene la operación y operandos.
                    Debe incluir:
                    - operation: Tipo de operación (string)
                    - operands: Lista de números para operar

        Returns:
            ArithmeticResponse: Resultado de la operación con:
                               - result: Resultado numérico
                               - operation: Operación realizada
                               - operands: Operandos utilizados

        Raises:
            ValueError: Si la operación no es soportada o hay errores en los operandos
            ZeroDivisionError: Si se intenta dividir por cero

        Ejemplos:
            >>> req = ArithmeticRequest(operation="add", operands=[1, 2, 3])
            >>> result = ArithmeticService.calculate(req)
            >>> result.result
            6.0
        """
        operation = request.operation
        operands = request.operands

        # Validar operación
        if operation not in ArithmeticService.SUPPORTED_OPERATIONS:
            raise ValueError(f"Operación no soportada: {operation}")

        # Validar operandos
        if not operands:
            raise ValueError("Se requieren operandos para la operación")

        try:
            # Operaciones básicas
            if operation == "add":
                result = sum(operands)
            elif operation == "subtract":
                result = operands[0] - sum(operands[1:])
            elif operation == "multiply":
                result = 1.0
                for num in operands:
                    result *= num
            elif operation == "divide":
                if len(operands) < 2:
                    raise ValueError("División requiere al menos 2 operandos")
                result = operands[0]
                for num in operands[1:]:
                    if num == 0:
                        raise ZeroDivisionError("División por cero")
                    result /= num

            # Potencias y raíces
            elif operation == "power":
                if len(operands) != 2:
                    raise ValueError("Potencia requiere exactamente 2 operandos")
                result = operands[0] ** operands[1]
            elif operation == "sqrt":
                if len(operands) != 1:
                    raise ValueError("Raíz cuadrada requiere exactamente 1 operando")
                if operands[0] < 0:
                    raise ValueError("Raíz cuadrada de número negativo")
                result = math.sqrt(operands[0])
            elif operation == "cbrt":
                if len(operands) != 1:
                    raise ValueError("Raíz cúbica requiere exactamente 1 operando")
                result = operands[0] ** (1/3)
            elif operation == "nth_root":
                if len(operands) != 2:
                    raise ValueError("Raíz n-ésima requiere exactamente 2 operandos")
                if operands[1] == 0:
                    raise ValueError("Raíz de índice cero")
                result = operands[0] ** (1/operands[1])

            # Funciones trigonométricas
            elif operation == "sin":
                result = math.sin(operands[0])
            elif operation == "cos":
                result = math.cos(operands[0])
            elif operation == "tan":
                result = math.tan(operands[0])
            elif operation == "cot":
                result = 1 / math.tan(operands[0])
            elif operation == "sec":
                result = 1 / math.cos(operands[0])
            elif operation == "csc":
                result = 1 / math.sin(operands[0])

            # Funciones trigonométricas inversas
            elif operation == "asin":
                if not -1 <= operands[0] <= 1:
                    raise ValueError("Dominio de arcsin: [-1, 1]")
                result = math.asin(operands[0])
            elif operation == "acos":
                if not -1 <= operands[0] <= 1:
                    raise ValueError("Dominio de arccos: [-1, 1]")
                result = math.acos(operands[0])
            elif operation == "atan":
                result = math.atan(operands[0])
            elif operation == "acot":
                result = math.pi/2 - math.atan(operands[0])
            elif operation == "asec":
                if abs(operands[0]) < 1:
                    raise ValueError("Dominio de arcsec: (-∞, -1] ∪ [1, ∞)")
                result = math.acos(1/operands[0])
            elif operation == "acsc":
                if abs(operands[0]) < 1:
                    raise ValueError("Dominio de arccsc: (-∞, -1] ∪ [1, ∞)")
                result = math.asin(1/operands[0])

            # Funciones hiperbólicas
            elif operation == "sinh":
                result = math.sinh(operands[0])
            elif operation == "cosh":
                result = math.cosh(operands[0])
            elif operation == "tanh":
                result = math.tanh(operands[0])
            elif operation == "coth":
                result = 1 / math.tanh(operands[0])
            elif operation == "sech":
                result = 1 / math.cosh(operands[0])
            elif operation == "csch":
                result = 1 / math.sinh(operands[0])

            # Funciones hiperbólicas inversas
            elif operation == "asinh":
                result = math.asinh(operands[0])
            elif operation == "acosh":
                if operands[0] < 1:
                    raise ValueError("Dominio de arcosh: [1, ∞)")
                result = math.acosh(operands[0])
            elif operation == "atanh":
                if not -1 < operands[0] < 1:
                    raise ValueError("Dominio de artanh: (-1, 1)")
                result = math.atanh(operands[0])
            elif operation == "acoth":
                if abs(operands[0]) <= 1:
                    raise ValueError("Dominio de arcoth: (-∞, -1) ∪ (1, ∞)")
                result = math.atanh(1/operands[0])
            elif operation == "asech":
                if not 0 < operands[0] <= 1:
                    raise ValueError("Dominio de arsech: (0, 1]")
                result = math.acosh(1/operands[0])
            elif operation == "acsch":
                result = math.asinh(1/operands[0])

            # Logaritmos
            elif operation == "log":
                if len(operands) == 1:
                    # Logaritmo natural
                    if operands[0] <= 0:
                        raise ValueError("Logaritmo de número no positivo")
                    result = math.log(operands[0])
                elif len(operands) == 2:
                    # Logaritmo en base arbitraria
                    if operands[0] <= 0 or operands[1] <= 0 or operands[1] == 1:
                        raise ValueError("Base y argumento deben ser positivos y base ≠ 1")
                    result = math.log(operands[0], operands[1])
                else:
                    raise ValueError("Logaritmo requiere 1 o 2 operandos")
            elif operation == "log10":
                if operands[0] <= 0:
                    raise ValueError("Logaritmo de número no positivo")
                result = math.log10(operands[0])
            elif operation == "log2":
                if operands[0] <= 0:
                    raise ValueError("Logaritmo de número no positivo")
                result = math.log2(operands[0])
            elif operation == "ln":
                if operands[0] <= 0:
                    raise ValueError("Logaritmo natural de número no positivo")
                result = math.log(operands[0])

            # Exponenciales
            elif operation == "exp":
                result = math.exp(operands[0])
            elif operation == "pow":
                if len(operands) != 2:
                    raise ValueError("Pow requiere exactamente 2 operandos")
                result = math.pow(operands[0], operands[1])

            # Otras funciones
            elif operation == "abs":
                result = abs(operands[0])
            elif operation == "factorial":
                if not isinstance(operands[0], int) or operands[0] < 0:
                    raise ValueError("Factorial requiere entero no negativo")
                result = math.factorial(int(operands[0]))
            elif operation == "ceil":
                result = math.ceil(operands[0])
            elif operation == "floor":
                result = math.floor(operands[0])
            elif operation == "round":
                if len(operands) == 1:
                    result = round(operands[0])
                elif len(operands) == 2:
                    result = round(operands[0], int(operands[1]))
                else:
                    raise ValueError("Round requiere 1 o 2 operandos")

            else:
                raise ValueError(f"Operación no implementada: {operation}")

            # Redondear resultado para evitar errores de punto flotante
            if isinstance(result, float):
                result = round(result, 10)

            return ArithmeticResponse(
                result=result,
                operation=operation,
                operands=operands
            )

        except Exception as e:
            raise ValueError(f"Error en operación {operation}: {str(e)}")

    @staticmethod
    def get_supported_operations() -> List[str]:
        """
        Obtiene la lista de operaciones aritméticas soportadas.

        Returns:
            List[str]: Lista de todas las operaciones disponibles
        """
        return ArithmeticService.SUPPORTED_OPERATIONS.copy()

    @staticmethod
    def validate_operation(operation: str, operands: List[float]) -> bool:
        """
        Valida si una operación puede ejecutarse con los operandos dados.

        Args:
            operation: Nombre de la operación
            operands: Lista de operandos

        Returns:
            bool: True si la operación es válida, False en caso contrario
        """
        if operation not in ArithmeticService.SUPPORTED_OPERATIONS:
            return False

        if not operands:
            return False

        try:
            # Intentar crear la solicitud para validar
            ArithmeticRequest(operation=operation, operands=operands)
            return True
        except Exception:
            return False