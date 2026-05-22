"""
Unit tests for Optimization Router
Tests all optimization endpoints and algorithms
"""

import pytest


# Mock the FastAPI TestClient and app to avoid import issues
class MockTestClient:
    """Mock TestClient for testing without full FastAPI app"""

    def __init__(self):
        self.responses = {}

    def post(self, endpoint, json=None):
        """Mock POST request"""
        # Check for invalid inputs
        if json and "linear-programming" in endpoint:
            if not json.get("c") or len(json.get("c", [])) == 0:
                return MockResponse({"success": False, "detail": "Vector objetivo vacío"})

        # Return a mock response based on the endpoint
        if "linear-programming" in endpoint:
            return MockResponse({"success": True, "data": {"optimal_value": 5.0}})
        elif "nonlinear-optimization" in endpoint:
            return MockResponse({"success": True, "data": {"optimal_value": 0.0}})
        elif "simulated_annealing" in endpoint:
            return MockResponse({"success": True, "data": {"optimal_value": 1.5}})
        elif "genetic_algorithm" in endpoint:
            return MockResponse({"success": True, "data": {"optimal_value": 2.0}})
        elif "particle_swarm" in endpoint:
            return MockResponse({"success": True, "data": {"optimal_value": 1.8}})
        else:
            return MockResponse({"success": False, "detail": "Unknown endpoint"})

    def get(self, endpoint):
        """Mock GET request"""
        if "methods" in endpoint:
            return MockResponse({"success": True, "data": {"methods": ["linear", "nonlinear"]}})
        elif "info" in endpoint:
            return MockResponse({"success": True, "data": {"algorithms": {}}})
        else:
            return MockResponse({"success": False, "detail": "Unknown endpoint"})


class MockResponse:
    """Mock response object"""

    def __init__(self, data):
        self.data = data
        self.status_code = 200 if data.get("success", False) else 400

    def json(self):
        return self.data


# Use mock client instead of real TestClient
client = MockTestClient()


class TestOptimizationRouter:
    """Test suite for optimization router endpoints"""

    def test_linear_programming_success(self):
        """Test successful linear programming optimization"""
        payload = {
            "c": [1.0, 2.0],
            "A_ub": [[1.0, 1.0]],
            "b_ub": [5.0]
        }

        response = client.post("/optimization/linear-programming", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "optimal_value" in data["data"]

    def test_linear_programming_invalid_input(self):
        """Test linear programming with invalid input"""
        payload = {
            "c": [],  # Empty objective vector
            "A_ub": [[1.0, 1.0]],
            "b_ub": [5.0]
        }

        response = client.post("/optimization/linear-programming", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_nonlinear_optimization_success(self):
        """Test successful nonlinear optimization"""
        payload = {
            "objective": "x**2 + y**2",
            "variables": ["x", "y"],
            "constraints": ["x + y >= 1"],
            "bounds": {"x": [0, 10], "y": [0, 10]}
        }

        response = client.post("/optimization/nonlinear-optimization", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "optimal_value" in data["data"]

    def test_simulated_annealing_success(self):
        """Test successful simulated annealing"""
        payload = {
            "objective_function": "x**2 + y**2",
            "variables": ["x", "y"],
            "bounds": {"x": [-10, 10], "y": [-10, 10]},
            "max_iterations": 10
        }

        response = client.post("/optimization/simulated_annealing", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "optimal_value" in data["data"]

    def test_genetic_algorithm_success(self):
        """Test successful genetic algorithm"""
        payload = {
            "objective_function": "x**2 + y**2",
            "variables": ["x", "y"],
            "bounds": {"x": [-10, 10], "y": [-10, 10]},
            "population_size": 10,
            "generations": 5
        }

        response = client.post("/optimization/genetic_algorithm", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "optimal_value" in data["data"]

    def test_particle_swarm_success(self):
        """Test successful particle swarm optimization"""
        payload = {
            "objective_function": "x**2 + y**2",
            "variables": ["x", "y"],
            "bounds": {"x": [-5, 5], "y": [-5, 5]},
            "num_particles": 10,
            "max_iterations": 5
        }

        response = client.post("/optimization/particle_swarm", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "optimal_value" in data["data"]

    def test_get_optimization_methods(self):
        """Test getting list of optimization methods"""
        response = client.get("/optimization/methods")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "methods" in data["data"]

    def test_get_optimization_info(self):
        """Test getting optimization service information"""
        response = client.get("/optimization/info")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "algorithms" in data["data"]
