#!/usr/bin/env python3
"""
Unit tests for arithmetic service
"""

import pytest
from app.domains.mathematics.services.arithmetic_service import ArithmeticService
from app.models import ArithmeticRequest


class TestArithmeticService:
    """Test cases for ArithmeticService"""

    def test_add_operation(self):
        """Test addition operation"""
        request = ArithmeticRequest(operation="add", operands=[1, 2, 3])
        result = ArithmeticService.calculate(request)

        assert result.operation == "add"
        assert result.result == 6.0
        assert result.operands == [1.0, 2.0, 3.0]

    def test_subtract_operation(self):
        """Test subtraction operation"""
        request = ArithmeticRequest(operation="subtract", operands=[10, 3, 2])
        result = ArithmeticService.calculate(request)

        assert result.operation == "subtract"
        assert result.result == 5.0  # 10 - 3 - 2 = 5

    def test_multiply_operation(self):
        """Test multiplication operation"""
        request = ArithmeticRequest(operation="multiply", operands=[2, 3, 4])
        result = ArithmeticService.calculate(request)

        assert result.operation == "multiply"
        assert result.result == 24.0  # 2 * 3 * 4 = 24

    def test_divide_operation(self):
        """Test division operation"""
        request = ArithmeticRequest(operation="divide", operands=[12, 3, 2])
        result = ArithmeticService.calculate(request)

        assert result.operation == "divide"
        assert result.result == 2.0  # 12 / 3 / 2 = 2

    def test_power_operation(self):
        """Test power operation"""
        request = ArithmeticRequest(operation="power", operands=[2, 3])
        result = ArithmeticService.calculate(request)

        assert result.operation == "power"
        assert result.result == 8.0  # 2^3 = 8

    def test_sqrt_operation(self):
        """Test square root operation"""
        request = ArithmeticRequest(operation="sqrt", operands=[16])
        result = ArithmeticService.calculate(request)

        assert result.operation == "sqrt"
        assert result.result == 4.0

    def test_sin_operation(self):
        """Test sine operation"""
        request = ArithmeticRequest(operation="sin", operands=[0])
        result = ArithmeticService.calculate(request)

        assert result.operation == "sin"
        assert abs(result.result - 0.0) < 1e-10  # sin(0) = 0

    def test_cos_operation(self):
        """Test cosine operation"""
        request = ArithmeticRequest(operation="cos", operands=[0])
        result = ArithmeticService.calculate(request)

        assert result.operation == "cos"
        assert abs(result.result - 1.0) < 1e-10  # cos(0) = 1

    def test_invalid_operation(self):
        """Test invalid operation raises exception"""
        request = ArithmeticRequest(operation="invalid_op", operands=[1, 2])

        with pytest.raises(ValueError, match="Operación no soportada"):
            ArithmeticService.calculate(request)

    def test_empty_operands(self):
        """Test empty operands list"""
        request = ArithmeticRequest(operation="add", operands=[])

        # Should not raise error, just return 0 for sum of empty list
        result = ArithmeticService.calculate(request)
        assert result.result == 0.0

    def test_single_operand_operations(self):
        """Test operations that work with single operand"""
        # Test sqrt with single operand
        request = ArithmeticRequest(operation="sqrt", operands=[9])
        result = ArithmeticService.calculate(request)
        assert result.result == 3.0

        # Test sin with single operand (90 degrees = π/2 radians)
        request = ArithmeticRequest(operation="sin", operands=[90])
        result = ArithmeticService.calculate(request)
        assert abs(result.result - 1.0) < 1e-10

    def test_supported_operations(self):
        """Test get_supported_operations returns expected operations"""
        operations = ArithmeticService.get_supported_operations()

        operation_names = [op["operation"] for op in operations]
        expected_ops = [
            "add", "subtract", "multiply", "divide",
            "power", "sqrt", "sin", "cos", "tan", "log"
        ]

        for op in expected_ops:
            assert op in operation_names

    @pytest.mark.parametrize("operation,operands,expected", [
        ("add", [1, 2, 3], 6.0),
        ("multiply", [2, 3, 4], 24.0),
        ("power", [2, 3], 8.0),
        ("sqrt", [16], 4.0),
        ("subtract", [10, 3], 7.0),
        ("divide", [12, 3], 4.0),
    ])
    def test_parametrized_operations(self, operation, operands, expected):
        """Test multiple operations with parametrize"""
        request = ArithmeticRequest(operation=operation, operands=operands)
        result = ArithmeticService.calculate(request)

        assert result.result == expected
        assert result.operation == operation
