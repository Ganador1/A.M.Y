"""
Unit tests for arithmetic router

Tests for FastAPI arithmetic router endpoints including:
- Basic arithmetic operations (add, subtract, multiply, divide)
- Advanced operations (power, sqrt, log, exp)
- Trigonometric functions (sin, cos, tan, asin, acos, atan)
- Batch processing
- Quick calculations via URL parameters
- Error handling and validation
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.routers.arithmetic import router
from app.models import ArithmeticResponse


@pytest.fixture
def client():
    """Test client for arithmetic router"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router, prefix="/api/arithmetic")
    return TestClient(app)


@pytest.fixture
def mock_arithmetic_service():
    """Mock ArithmeticService for testing"""
    with patch('app.routers.arithmetic.ArithmeticService') as mock_service:
        yield mock_service


class TestArithmeticRouter:
    """Test suite for arithmetic router endpoints"""

    def test_calculate_arithmetic_success(self, client, mock_arithmetic_service):
        """Test successful arithmetic calculation"""
        # Mock the service response
        mock_result = ArithmeticResponse(
            operation="add",
            operands=[5, 3],
            result=8
        )
        mock_arithmetic_service.calculate.return_value = mock_result

        request_data = {
            "operation": "add",
            "operands": [5, 3]
        }

        response = client.post("/api/arithmetic/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "add"
        assert data["operands"] == [5, 3]
        assert data["result"] == 8
        mock_arithmetic_service.calculate.assert_called_once()

    def test_calculate_arithmetic_value_error(self, client, mock_arithmetic_service):
        """Test arithmetic calculation with ValueError"""
        mock_arithmetic_service.calculate.side_effect = ValueError("Invalid operands")

        request_data = {
            "operation": "add",
            "operands": ["invalid"]
        }

        response = client.post("/api/arithmetic/calculate", json=request_data)
                            
        assert response.status_code == 422
        data = response.json()
        # Pydantic validation error, not our custom error message
        assert "detail" in data

    def test_calculate_arithmetic_generic_error(self, client, mock_arithmetic_service):
        """Test arithmetic calculation with generic exception"""
        mock_arithmetic_service.calculate.side_effect = Exception("Calculation failed")

        request_data = {
            "operation": "add",
            "operands": [5, 3]
        }

        response = client.post("/api/arithmetic/calculate", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "Error al calcular" in data["detail"]

    def test_get_operations(self, client, mock_arithmetic_service):
        """Test getting available operations"""
        mock_arithmetic_service.get_supported_operations.return_value = [
            "add", "subtract", "multiply", "divide", "power", "sqrt"
        ]

        response = client.get("/api/arithmetic/operations")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "available_operations" in data["data"]
        assert "categorized_operations" in data["data"]
        assert "usage_examples" in data["data"]
        assert "add" in data["data"]["available_operations"]

    def test_calculate_batch_all_success(self, client, mock_arithmetic_service):
        """Test batch calculation with all operations successful"""
        mock_results = [
            ArithmeticResponse(operation="add", operands=[1, 2], result=3),
            ArithmeticResponse(operation="multiply", operands=[3, 4], result=12)
        ]

        def mock_calculate(request):
            if request.operation == "add":
                return mock_results[0]
            elif request.operation == "multiply":
                return mock_results[1]
            else:
                raise ValueError("Unknown operation")

        mock_arithmetic_service.calculate.side_effect = mock_calculate

        batch_request = [
            {"operation": "add", "operands": [1, 2]},
            {"operation": "multiply", "operands": [3, 4]}
        ]

        response = client.post("/api/arithmetic/batch", json=batch_request)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_requests"] == 2
        assert data["data"]["successful"] == 2
        assert data["data"]["failed"] == 0
        assert len(data["data"]["results"]) == 2

    def test_calculate_batch_with_errors(self, client, mock_arithmetic_service):
        """Test batch calculation with some operations failing"""
        def mock_calculate(request):
            if request.operation == "add":
                return ArithmeticResponse(operation="add", operands=[1, 2], result=3)
            elif request.operation == "invalid":
                raise ValueError("Invalid operation")
            else:
                raise Exception("Unknown error")

        mock_arithmetic_service.calculate.side_effect = mock_calculate

        batch_request = [
            {"operation": "add", "operands": [1, 2]},
            {"operation": "invalid", "operands": [1]},
            {"operation": "error", "operands": [1]}
        ]

        response = client.post("/api/arithmetic/batch", json=batch_request)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True  # At least one operation succeeded
        assert data["data"]["total_requests"] == 3
        assert data["data"]["successful"] == 1
        assert data["data"]["failed"] == 2
        assert len(data["data"]["results"]) == 1
        assert len(data["data"]["errors"]) == 2

    def test_get_examples(self, client):
        """Test getting arithmetic examples"""
        response = client.get("/api/arithmetic/examples")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "basic_operations" in data["data"]
        assert "advanced_operations" in data["data"]
        assert "trigonometric_operations" in data["data"]
        assert "tips" in data["data"]

        # Check that examples have expected structure
        basic_ops = data["data"]["basic_operations"]
        assert len(basic_ops) > 0
        assert "name" in basic_ops[0]
        assert "operation" in basic_ops[0]
        assert "operands" in basic_ops[0]
        assert "expected_result" in basic_ops[0]

    def test_quick_calc_binary_operation_success(self, client, mock_arithmetic_service):
        """Test quick calculation with binary operation"""
        mock_result = ArithmeticResponse(
            operation="add",
            operands=[5, 3],
            result=8
        )
        mock_arithmetic_service.calculate.return_value = mock_result

        response = client.post("/api/arithmetic/quick-calc/add?a=5&b=3")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["operation"] == "add"
        assert data["data"]["operands"] == [5, 3]
        assert data["data"]["result"] == 8

    def test_quick_calc_unary_operation_success(self, client, mock_arithmetic_service):
        """Test quick calculation with unary operation"""
        mock_result = ArithmeticResponse(
            operation="sqrt",
            operands=[16],
            result=4
        )
        mock_arithmetic_service.calculate.return_value = mock_result

        response = client.post("/api/arithmetic/quick-calc/sqrt?a=16")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["operation"] == "sqrt"
        assert data["data"]["operands"] == [16]
        assert data["data"]["result"] == 4

    def test_quick_calc_binary_missing_second_operand(self, client):
        """Test quick calculation with binary operation missing second operand"""
        response = client.post("/api/arithmetic/quick-calc/add?a=5")

        assert response.status_code == 400
        data = response.json()
        assert "requiere dos operandos" in data["detail"]

    def test_quick_calc_unary_with_second_operand(self, client):
        """Test quick calculation with unary operation having unnecessary second operand"""
        response = client.post("/api/arithmetic/quick-calc/sqrt?a=16&b=2")

        assert response.status_code == 400
        data = response.json()
        assert "solo requiere un operando" in data["detail"]

    def test_quick_calc_invalid_parameters(self, client, mock_arithmetic_service):
        """Test quick calculation with invalid parameters"""
        mock_arithmetic_service.calculate.side_effect = ValueError("Invalid input")

        response = client.post("/api/arithmetic/quick-calc/add?a=invalid&b=3")

        assert response.status_code == 422
        data = response.json()
        # Pydantic validation error for invalid parameter
        assert "detail" in data

    def test_quick_calc_calculation_error(self, client, mock_arithmetic_service):
        """Test quick calculation with calculation error"""
        mock_arithmetic_service.calculate.side_effect = Exception("Division by zero")

        response = client.post("/api/arithmetic/quick-calc/divide?a=5&b=0")

        assert response.status_code == 400
        data = response.json()
        assert "Error en el cálculo" in data["detail"]


if __name__ == '__main__':
    pytest.main([__file__])
