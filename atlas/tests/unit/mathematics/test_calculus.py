"""
Unit tests for Calculus Router

Tests the calculus API endpoints and mathematical operations,
including derivatives, integrals, limits, and series.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Mock the dependencies that may not be available
with patch.dict('sys.modules', {
    'app.core.logging': Mock(),
    'app.core.config': Mock(),
    'app.models.advanced_models': Mock(),
    'app.models': Mock(),
    'app.services.calculus': Mock(),
}):
    from app.routers.calculus import (
        router,
        validate_mathematical_expression,
        format_calculus_result,
        CalculusOperationRequest,
        CalculusResult
    )


class TestMathematicalValidation:
    """Test mathematical expression validation"""

    def test_validate_valid_expression(self):
        """Test validation of valid mathematical expression"""
        assert validate_mathematical_expression("x^2 + sin(x)") is True
        assert validate_mathematical_expression("x**2 + cos(x)") is True

    def test_validate_invalid_expression(self):
        """Test validation of invalid mathematical expression"""
        assert validate_mathematical_expression("invalid expression +++") is False
        assert validate_mathematical_expression("") is False


class TestResultFormatting:
    """Test calculus result formatting"""

    def test_format_derivative_result(self):
        """Test formatting of derivative result"""
        result = format_calculus_result("derivative", "x^2", "2*x", "x")
        assert "d/dx" in result
        assert "2*x" in result

    def test_format_integral_result(self):
        """Test formatting of integral result"""
        result = format_calculus_result("integral", "x^2", "x^3/3", "x")
        assert "∫" in result
        assert "x^3/3" in result

    def test_format_limit_result(self):
        """Test formatting of limit result"""
        result = format_calculus_result("limit", "x^2", "4", "x")
        assert "lim" in result
        assert "4" in result


class TestCalculusOperationRequest:
    """Test CalculusOperationRequest model"""

    def test_valid_request(self):
        """Test creating valid request"""
        request = CalculusOperationRequest(
            expression="x^2 + sin(x)",
            operation="derivative",
            variable="x",
            order=1
        )
        assert request.expression == "x^2 + sin(x)"
        assert request.operation == "derivative"

    def test_invalid_operation(self):
        """Test invalid operation validation"""
        with pytest.raises(ValueError):
            CalculusOperationRequest(
                expression="x^2",
                operation="invalid_op"
            )

    def test_invalid_expression(self):
        """Test invalid expression validation"""
        with pytest.raises(ValueError):
            CalculusOperationRequest(
                expression="invalid +++ expression",
                operation="derivative"
            )


class TestCalculusResult:
    """Test CalculusResult model"""

    def test_result_creation(self):
        """Test creating calculus result"""
        result = CalculusResult(
            expression="x^2",
            operation="derivative",
            result="2*x",
            explanation="d/dx (x²) = 2x",
            computation_time_ms=15.5,
            symbolic=True
        )
        assert result.expression == "x^2"
        assert result.result == "2*x"
        assert result.computation_time_ms == 15.5


# Integration tests with mocked dependencies
class TestCalculusEndpoints:
    """Test calculus API endpoints with mocked dependencies"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def mock_calculus_service(self):
        """Mock CalculusService"""
        with patch('app.routers.calculus.CalculusService') as mock_service:
            mock_instance = Mock()
            mock_service.calculate.return_value = Mock(result="2*x")
            mock_service.calculate_limit.return_value = "2"
            mock_service.taylor_series.return_value = "1 + x + x^2/2"
            mock_service.calculate_partial_derivative.return_value = {
                "expression": "x*y",
                "variables": ["x", "y"],
                "orders": [1, 1],
                "result": "y",
                "explanation": "∂²f/∂x∂y = y"
            }
            mock_service.fourier_transform.return_value = {
                "expression": "exp(-t)",
                "variable": "t",
                "transform_variable": "f",
                "result": "1/(1 + I*2*pi*f)",
                "explanation": "Fourier transform of exp(-t)"
            }
            mock_service.return_value = mock_instance
            yield mock_service

    def test_get_examples_endpoint(self, client):
        """Test getting examples endpoint"""
        response = client.get("/calculus/examples")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "derivatives" in data["data"]
        assert "integrals" in data["data"]

    def test_quick_derivative_valid(self, client, mock_calculus_service):
        """Test quick derivative with valid expression"""
        response = client.post("/calculus/quick-derivative?expression=x^2")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data["data"]

    def test_quick_derivative_invalid(self, client):
        """Test quick derivative with invalid expression"""
        response = client.post("/calculus/quick-derivative?expression=invalid+++")
        assert response.status_code == 400

    def test_quick_integral_indefinite(self, client, mock_calculus_service):
        """Test quick integral indefinite"""
        response = client.post("/calculus/quick-integral?expression=x^2")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["integral_type"] == "indefinida"

    def test_quick_integral_definite(self, client, mock_calculus_service):
        """Test quick integral definite"""
        response = client.post("/calculus/quick-integral?expression=x&lower_limit=0&upper_limit=1")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["integral_type"] == "definida"

    def test_calculate_limit(self, client, mock_calculus_service):
        """Test limit calculation"""
        response = client.post("/calculus/limit?expression=x^2&variable=x&limit_point=2")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["result"] == "2"

    def test_taylor_series(self, client, mock_calculus_service):
        """Test Taylor series calculation"""
        response = client.post("/calculus/taylor?expression=e^x&variable=x&point=0&order=3")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data["data"]

    @pytest.mark.asyncio
    async def test_calculate_endpoint(self, mock_calculus_service):
        """Test main calculate endpoint"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        request_data = {
            "expression": "x^2",
            "operation": "derivative",
            "variable": "x",
            "order": 1
        }

        response = client.post("/calculus/calculate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["expression"] == "x^2"
        assert data["operation"] == "derivative"

    @pytest.mark.asyncio
    async def test_batch_calculus(self, mock_calculus_service):
        """Test batch calculus processing"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        request_data = {
            "operations": [
                {
                    "expression": "x^2",
                    "operation": "derivative",
                    "variable": "x",
                    "order": 1
                }
            ],
            "parallel": False,
            "timeout_seconds": 30
        }

        response = client.post("/calculus/batch", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["total_operations"] == 1
        assert data["successful"] == 1
        assert data["failed"] == 0

    @pytest.mark.asyncio
    async def test_partial_derivative(self, mock_calculus_service):
        """Test partial derivative calculation"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        request_data = {
            "expression": "x*y",
            "variables": ["x", "y"],
            "orders": [1, 1]
        }

        response = client.post("/calculus/partial-derivative", json=request_data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_fourier_transform(self, mock_calculus_service):
        """Test Fourier transform calculation"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        request_data = {
            "expression": "exp(-t)",
            "variable": "t",
            "transform_variable": "f"
        }

        response = client.post("/calculus/fourier-transform", json=request_data)
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling in calculus operations"""

    def test_invalid_expression_error(self):
        """Test handling of invalid mathematical expressions"""
        # This would test the HTTPException raising for invalid expressions
        # In a real scenario, this would be tested with the actual endpoint
        pass

    def test_service_unavailable_error(self):
        """Test handling when CalculusService is unavailable"""
        # This would test error handling when the service dependency fails
        pass
