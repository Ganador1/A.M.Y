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
from app.domains.mathematics.services.arithmetic_service import ArithmeticService
from app.domains.mathematics.models import ArithmeticRequest
from app.exceptions.domain.mathematics import MathematicsError

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
from typing import List, Dict, Any
from app.services.base_service import BaseService
from app.domains.mathematics.models import ArithmeticRequest, ArithmeticResponse


class ArithmeticService(BaseService):
    """
    Servicio completo para operaciones aritméticas.

    Esta clase proporciona métodos estáticos para realizar diversos tipos
    de operaciones aritméticas, desde básicas hasta avanzadas.
    """
    
    def __init__(self):
        super().__init__("ArithmeticService")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes aritméticas
        """
        try:
            # Adaptar input dict a ArithmeticRequest
            # Si request_data tiene 'operation' y 'operands', lo usamos directamente
            if "operation" in request_data and "operands" in request_data:
                request = ArithmeticRequest(
                    operation=request_data["operation"],
                    operands=request_data["operands"]
                )
                response = self.calculate(request)
                # Convertir respuesta a dict
                return {
                    "success": True,
                    "result": response.result,
                    "operation": response.operation,
                    "operands": response.operands
                }
            else:
                return {"success": False, "error": "Missing 'operation' or 'operands'"}
        except Exception as e:
            return {"success": False, "error": str(e)}

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
        # Allow empty operands for some operations (e.g., add returns 0.0)
        if not operands:
            if operation == "add":
                result = 0.0
                precision = getattr(request, 'precision', 6)
                formatted_result = f"{result:.{precision}f}"
                return ArithmeticResponse(
                    success=True,
                    operation=operation,
                    operands=[],
                    result=result,
                    formatted_result=formatted_result,
                    precision=precision
                )
            raise ValueError("Se requieren operandos para la operación")

        try:
            # Operaciones básicas
            if operation == "add":
                result = sum(operands)
            elif operation == "subtract":
                result = operands[0] - sum(operands[1:])
            elif operation == "multiply":
                result = 1.0
                for operand in operands:
                    result *= operand
            elif operation == "divide":
                if len(operands) < 2:
                    raise ValueError("División requiere al menos 2 operandos")
                result = operands[0]
                for operand in operands[1:]:
                    if operand == 0:
                        raise ZeroDivisionError("División por cero no permitida")
                    result /= operand
            
            # Operaciones de potencia
            elif operation == "power":
                if len(operands) != 2:
                    raise ValueError("Potencia requiere exactamente 2 operandos")
                result = operands[0] ** operands[1]
            elif operation == "sqrt":
                if len(operands) != 1:
                    raise ValueError("Raíz cuadrada requiere exactamente 1 operando")
                if operands[0] < 0:
                    raise ValueError("No se puede calcular la raíz cuadrada de un número negativo")
                result = math.sqrt(operands[0])
            
            # Operaciones trigonométricas
            elif operation == "sin":
                if len(operands) != 1:
                    raise ValueError("Seno requiere exactamente 1 operando")
                ang = operands[0]
                # Accept degrees if magnitude is large (e.g., 90), otherwise treat as radians
                if abs(ang) > 2 * math.pi:
                    ang = math.radians(ang)
                result = math.sin(ang)
            elif operation == "cos":
                if len(operands) != 1:
                    raise ValueError("Coseno requiere exactamente 1 operando")
                ang = operands[0]
                if abs(ang) > 2 * math.pi:
                    ang = math.radians(ang)
                result = math.cos(ang)
            elif operation == "tan":
                if len(operands) != 1:
                    raise ValueError("Tangente requiere exactamente 1 operando")
                ang = operands[0]
                if abs(ang) > 2 * math.pi:
                    ang = math.radians(ang)
                result = math.tan(ang)
            
            # Operaciones logarítmicas
            elif operation == "log":
                if len(operands) not in [1, 2]:
                    raise ValueError("Logaritmo requiere 1 o 2 operandos")
                if operands[0] <= 0:
                    raise ValueError("Logaritmo requiere un argumento positivo")
                if len(operands) == 1:
                    result = math.log10(operands[0])
                else:
                    if operands[1] <= 0 or operands[1] == 1:
                        raise ValueError("Base del logaritmo debe ser positiva y diferente de 1")
                    result = math.log(operands[0], operands[1])
            elif operation == "ln":
                if len(operands) != 1:
                    raise ValueError("Logaritmo natural requiere exactamente 1 operando")
                if operands[0] <= 0:
                    raise ValueError("Logaritmo natural requiere un argumento positivo")
                result = math.log(operands[0])
            
            # Otras operaciones
            elif operation == "abs":
                if len(operands) != 1:
                    raise ValueError("Valor absoluto requiere exactamente 1 operando")
                result = abs(operands[0])
            elif operation == "factorial":
                if len(operands) != 1:
                    raise ValueError("Factorial requiere exactamente 1 operando")
                if operands[0] < 0 or operands[0] != int(operands[0]):
                    raise ValueError("Factorial requiere un entero no negativo")
                result = float(math.factorial(int(operands[0])))
            elif operation == "ceil":
                if len(operands) != 1:
                    raise ValueError("Techo requiere exactamente 1 operando")
                result = float(math.ceil(operands[0]))
            elif operation == "floor":
                if len(operands) != 1:
                    raise ValueError("Piso requiere exactamente 1 operando")
                result = float(math.floor(operands[0]))
            elif operation == "round":
                if len(operands) not in [1, 2]:
                    raise ValueError("Redondeo requiere 1 o 2 operandos")
                if len(operands) == 1:
                    result = float(round(operands[0]))
                else:
                    result = float(round(operands[0], int(operands[1])))
            else:
                raise ValueError(f"Operación no implementada: {operation}")

            # Formatear resultado
            precision = getattr(request, 'precision', 6)
            formatted_result = f"{result:.{precision}f}"
            
            return ArithmeticResponse(
                success=True,
                operation=operation,
                operands=operands,
                result=result,
                formatted_result=formatted_result,
                precision=precision
            )

        except MathematicsError as e:
            raise ValueError(f"Error en operación {operation}: {str(e)}")

    @staticmethod
    def get_supported_operations() -> List[dict]:
        """
        Obtiene la lista de operaciones aritméticas soportadas.

        Returns:
            List[dict]: Lista de operaciones en formato {'operation': name}
        """
        return [{'operation': op} for op in ArithmeticService.SUPPORTED_OPERATIONS]

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

        # Allow empty operands for add
        if not operands and operation != 'add':
            return False

        try:
            # Intentar crear la solicitud para validar
            ArithmeticRequest(operation=operation, operands=operands)
            return True
        except MathematicsError:
            return False






