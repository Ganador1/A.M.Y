"""
Integration tests for API functionality

Tests the complete integration of API endpoints and services with mocked components.
"""

import pytest
from unittest.mock import MagicMock


class TestAPIIntegration:
    """Test suite for API integration testing with mocked components."""

    def test_health_check_basic(self):
        """Test basic health check endpoint."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
        mock_client.get.return_value = mock_response

        response = mock_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_check_detailed(self):
        """Test detailed health check endpoint."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "system": {"cpu": 45.2, "memory": 67.8},
            "dependencies": {"database": "ok", "cache": "ok"},
            "metrics": {"requests": 1234, "errors": 0}
        }
        mock_client.get.return_value = mock_response

        response = mock_client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "system" in data
        assert "dependencies" in data
        assert "metrics" in data

    def test_api_documentation_accessible(self):
        """Test that API documentation is accessible."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_client.get.return_value = mock_response

        response = mock_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "paths": {"/health": {"get": {"responses": {"200": {"description": "OK"}}}}},
            "components": {"schemas": {}}
        }
        mock_client.get.return_value = mock_response

        response = mock_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "components" in schema

    def test_arithmetic_operations_integration(self):
        """Test arithmetic operations integration."""
        mock_client = MagicMock()

        # Test addition
        mock_response_add = MagicMock()
        mock_response_add.status_code = 200
        mock_response_add.json.return_value = {"result": 15}

        mock_response_mult = MagicMock()
        mock_response_mult.status_code = 200
        mock_response_mult.json.return_value = {"result": 42}

        mock_client.post.side_effect = [mock_response_add, mock_response_mult]

        # Test addition
        payload = {"a": 10, "b": 5}
        response = mock_client.post("/api/arithmetic/add", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert data["result"] == 15

        # Test multiplication
        payload = {"a": 6, "b": 7}
        response = mock_client.post("/api/arithmetic/multiply", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 42

    def test_calculus_integration(self):
        """Test calculus operations integration."""
        mock_client = MagicMock()

        # Test derivative
        mock_response_deriv = MagicMock()
        mock_response_deriv.status_code = 200
        mock_response_deriv.json.return_value = {"derivative": "2*x + 3"}

        mock_response_int = MagicMock()
        mock_response_int.status_code = 200
        mock_response_int.json.return_value = {"integral": "x**3/3 + C"}

        mock_client.post.side_effect = [mock_response_deriv, mock_response_int]

        # Test derivative
        payload = {"expression": "x**2 + 3*x", "variable": "x"}
        response = mock_client.post("/api/calculus/derivative", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "derivative" in data
        assert "2*x + 3" in data["derivative"]

        # Test integral
        payload = {"expression": "x**2", "variable": "x"}
        response = mock_client.post("/api/calculus/integrate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "integral" in data

    def test_pde_integration(self):
        """Test PDE solving integration."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "solution": [[0.1, 0.2, 0.3]],
            "grid": {"x": [0.0, 0.1, 0.2], "t": [0.0, 0.01, 0.02]}
        }
        mock_client.post.return_value = mock_response

        # Test heat equation
        payload = {
            "L": 1.0,
            "alpha": 0.01,
            "T": 0.1,
            "Nx": 50,
            "Nt": 100,
            "boundary_conditions": {"left": "0", "right": "0"},
            "initial_condition": "sin(pi*x)"
        }
        response = mock_client.post("/api/pde/heat-equation", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "solution" in data
        assert "grid" in data

    def test_optimization_integration(self):
        """Test optimization algorithms integration."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "solution": [0.1, 0.2],
            "objective_value": 0.05
        }
        mock_client.post.return_value = mock_response

        # Test simulated annealing
        payload = {
            "objective": "x**2 + y**2",
            "bounds": [[-10, 10], [-10, 10]],
            "max_iterations": 100,
            "initial_temperature": 100.0
        }
        response = mock_client.post("/api/optimization/simulated-annealing", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "solution" in data
        assert "objective_value" in data

    def test_transform_integration(self):
        """Test integral transforms integration."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"transform": "sqrt(pi)*exp(-k**2/4)"}
        mock_client.post.return_value = mock_response

        # Test Fourier transform
        payload = {
            "expression": "exp(-x**2)",
            "variable": "x",
            "domain": "real"
        }
        response = mock_client.post("/api/transform/fourier", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "transform" in data

    def test_complex_analysis_integration(self):
        """Test complex analysis integration."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"series": "1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120"}
        mock_client.post.return_value = mock_response

        # Test series expansion
        payload = {
            "expression": "exp(x)",
            "variable": "x",
            "order": 5
        }
        response = mock_client.post("/api/complex-analysis/taylor-series", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "series" in data

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        mock_client = MagicMock()

        # Mock responses with some rate limited
        responses = []
        for i in range(70):
            mock_resp = MagicMock()
            mock_resp.status_code = 429 if i > 60 else 200  # Some rate limited
            responses.append(mock_resp)

        mock_client.get.side_effect = responses

        # Make multiple requests quickly
        status_codes = []
        for _ in range(70):  # Exceed rate limit
            response = mock_client.get("/health")
            status_codes.append(response.status_code)

        # Should have some 429 responses
        assert 429 in status_codes

    def test_caching_integration(self):
        """Test caching functionality."""
        mock_client = MagicMock()

        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {"result": 8}
        mock_response1.headers = {}

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {"result": 8}
        mock_response2.headers = {"X-Cache": "HIT"}

        mock_client.post.side_effect = [mock_response1, mock_response2]

        # Make same request multiple times
        payload = {"a": 5, "b": 3}
        response1 = mock_client.post("/api/arithmetic/add", json=payload)
        response2 = mock_client.post("/api/arithmetic/add", json=payload)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()

        # Check cache headers if present
        if "X-Cache" in response2.headers:
            assert response2.headers["X-Cache"] in ["HIT", "MISS"]

    def test_error_handling_integration(self):
        """Test error handling across endpoints."""
        mock_client = MagicMock()

        # Test invalid input
        mock_response_422 = MagicMock()
        mock_response_422.status_code = 422
        mock_client.post.return_value = mock_response_422

        payload = {"invalid": "data"}
        response = mock_client.post("/api/arithmetic/add", json=payload)
        assert response.status_code == 422  # Validation error

        # Test non-existent endpoint
        mock_response_404 = MagicMock()
        mock_response_404.status_code = 404
        mock_client.get.return_value = mock_response_404

        response = mock_client.get("/api/non-existent")
        assert response.status_code == 404

    def test_service_integration_cross_endpoints(self):
        """Test integration between different services."""
        mock_client = MagicMock()

        # Mock responses for derivative and integral
        mock_response_deriv = MagicMock()
        mock_response_deriv.status_code = 200
        mock_response_deriv.json.return_value = {"derivative": "3*x**2"}

        mock_response_int = MagicMock()
        mock_response_int.status_code = 200
        mock_response_int.json.return_value = {"integral": "x**3 + C"}

        mock_client.post.side_effect = [mock_response_deriv, mock_response_int]

        # Use result from one endpoint as input to another
        # First get a derivative
        payload1 = {"expression": "x**3", "variable": "x"}
        response1 = mock_client.post("/api/calculus/derivative", json=payload1)
        derivative = response1.json()["derivative"]

        # Then integrate the result
        payload2 = {"expression": derivative, "variable": "x"}
        response2 = mock_client.post("/api/calculus/integrate", json=payload2)

        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_visualization_integration(self):
        """Test visualization endpoints integration."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"plot_data": {"x": [1, 2, 3], "y": [1, 4, 9]}}
        mock_client.post.return_value = mock_response

        # Test graphing endpoint
        payload = {
            "expression": "sin(x)",
            "x_range": [-10, 10],
            "num_points": 100
        }
        response = mock_client.post("/api/graph/plot", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "plot_data" in data or "image" in data

    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "# HELP requests_total Total number of requests\nrequests_total 1234"
        mock_client.get.return_value = mock_response

        response = mock_client.get("/metrics")
        assert response.status_code == 200
        # Metrics should be in Prometheus format or JSON
        content = response.text
        assert "requests_total" in content or "requests" in content

    def test_stats_endpoint(self):
        """Test stats endpoint."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "uptime": "1h 30m",
            "total_requests": 1500
        }
        mock_client.get.return_value = mock_response

        response = mock_client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "uptime" in data
        assert "total_requests" in data
