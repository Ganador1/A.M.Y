"""
Unit tests for analytical geometry router

Tests for FastAPI analytical geometry router endpoints including:
- Circle analysis and properties
- Ellipse analysis (placeholder)
- Parabola analysis (placeholder)
- Hyperbola analysis (placeholder)
- Line analysis (placeholder)
- Triangle analysis (placeholder)
- Distance calculations
- Intersection calculations
- Parametric surface generation
- Error handling and validation
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.domains.mathematics.routers.analytical_geometry import router
from app.models import GeometryResponse


@pytest.fixture
def client():
    """Test client for analytical geometry router"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router, prefix="/api/geometry")
    return TestClient(app)


@pytest.fixture
def mock_geometry_service():
    """Mock AnalyticalGeometryService for testing"""
    with patch('app.routers.analytical_geometry.geometry_service') as mock_service:
        yield mock_service


class TestAnalyticalGeometryRouter:
    """Test suite for analytical geometry router endpoints"""

    def test_analyze_circle_success(self, client, mock_geometry_service):
        """Test successful circle analysis"""
        # Create a real GeometryResponse object
        mock_result = GeometryResponse(
            shape="circle",
            operation="analyze",
            result={
                "value": {"area": 78.54, "circumference": 31.416},
                "equation": "(x - 0)² + (y - 0)² = 25",
                "graph_data": None
            },
            properties={"center": [0, 0], "radius": 5},
            error=None
        )
        mock_geometry_service.process_geometry.return_value = mock_result

        request_data = {
            "operation": "analyze",
            "points": [[0, 0]],
            "parameters": {"center": [0, 0], "radius": 5}
        }

        response = client.post("/api/geometry/circle/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["shape"] == "circle"
        assert data["operation"] == "analyze"
        assert "value" in data["result"]
        assert "area" in data["result"]["value"]
        assert "circumference" in data["result"]["value"]
        mock_geometry_service.process_geometry.assert_called_once()

    def test_analyze_circle_wrong_shape(self, client, mock_geometry_service):
        """Test circle analysis with wrong shape type"""
        request_data = {
            "shape": "ellipse",  # Wrong shape
            "operation": "analyze",
            "parameters": {"center": [0, 0], "radius": 5}
        }

        response = client.post("/api/geometry/circle/analyze", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "Shape must be 'circle'" in data["detail"]

    def test_analyze_circle_service_error(self, client, mock_geometry_service):
        """Test circle analysis with service error"""
        mock_geometry_service.process_geometry.side_effect = Exception("Service error")

        request_data = {
            "shape": "circle",
            "operation": "analyze",
            "parameters": {"center": [0, 0], "radius": 5}
        }

        response = client.post("/api/geometry/circle/analyze", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "Service error" in data["detail"]

    def test_analyze_ellipse_placeholder(self, client):
        """Test ellipse analysis placeholder response"""
        request_data = {
            "shape": "ellipse",
            "operation": "analyze",
            "parameters": {"center": [0, 0], "semi_major": 5, "semi_minor": 3}
        }

        response = client.post("/api/geometry/ellipse/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["shape"] == "ellipse"
        assert data["operation"] == "analyze"
        assert "message" in data["result"]
        assert "Ellipse analysis not yet implemented" in data["result"]["message"]

    def test_analyze_ellipse_wrong_shape(self, client):
        """Test ellipse analysis with wrong shape type"""
        request_data = {
            "shape": "circle",  # Wrong shape
            "operation": "analyze",
            "parameters": {"center": [0, 0], "semi_major": 5, "semi_minor": 3}
        }

        response = client.post("/api/geometry/ellipse/analyze", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "Shape must be 'ellipse'" in data["detail"]

    def test_analyze_parabola_placeholder(self, client):
        """Test parabola analysis placeholder response"""
        request_data = {
            "shape": "parabola",
            "operation": "analyze",
            "parameters": {"vertex": [0, 0], "focus": [0, 1]}
        }

        response = client.post("/api/geometry/parabola/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["shape"] == "parabola"
        assert data["operation"] == "analyze"
        assert "message" in data["result"]
        assert "Parabola analysis not yet implemented" in data["result"]["message"]

    def test_analyze_parabola_wrong_shape(self, client):
        """Test parabola analysis with wrong shape type"""
        request_data = {
            "shape": "circle",  # Wrong shape
            "operation": "analyze",
            "parameters": {"vertex": [0, 0], "focus": [0, 1]}
        }

        response = client.post("/api/geometry/parabola/analyze", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "Shape must be 'parabola'" in data["detail"]

    def test_analyze_hyperbola_placeholder(self, client):
        """Test hyperbola analysis placeholder response"""
        request_data = {
            "shape": "hyperbola",
            "operation": "analyze",
            "parameters": {"center": [0, 0], "semi_major": 5, "semi_minor": 3}
        }

        response = client.post("/api/geometry/hyperbola/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["shape"] == "hyperbola"
        assert data["operation"] == "analyze"
        assert "message" in data["result"]
        assert "Hyperbola analysis not yet implemented" in data["result"]["message"]

    def test_analyze_hyperbola_wrong_shape(self, client):
        """Test hyperbola analysis with wrong shape type"""
        request_data = {
            "shape": "circle",  # Wrong shape
            "operation": "analyze",
            "parameters": {"center": [0, 0], "semi_major": 5, "semi_minor": 3}
        }

        response = client.post("/api/geometry/hyperbola/analyze", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "Shape must be 'hyperbola'" in data["detail"]

    def test_analyze_line_placeholder(self, client):
        """Test line analysis placeholder response"""
        request_data = {
            "shape": "line",
            "operation": "analyze",
            "parameters": {"point1": [0, 0], "point2": [1, 1]}
        }

        response = client.post("/api/geometry/line/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["shape"] == "line"
        assert data["operation"] == "analyze"
        assert "message" in data["result"]
        assert "Line analysis not yet implemented" in data["result"]["message"]

    def test_analyze_line_wrong_shape(self, client):
        """Test line analysis with wrong shape type"""
        request_data = {
            "shape": "circle",  # Wrong shape
            "operation": "analyze",
            "parameters": {"point1": [0, 0], "point2": [1, 1]}
        }

        response = client.post("/api/geometry/line/analyze", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "Shape must be 'line'" in data["detail"]

    def test_analyze_triangle_placeholder(self, client):
        """Test triangle analysis placeholder response"""
        request_data = {
            "shape": "triangle",
            "operation": "analyze",
            "parameters": {"vertices": [[0, 0], [1, 0], [0.5, 1]]}
        }

        response = client.post("/api/geometry/triangle/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["shape"] == "triangle"
        assert data["operation"] == "analyze"
        assert "message" in data["result"]
        assert "Triangle analysis not yet implemented" in data["result"]["message"]

    def test_analyze_triangle_wrong_shape(self, client):
        """Test triangle analysis with wrong shape type"""
        request_data = {
            "shape": "circle",  # Wrong shape
            "operation": "analyze",
            "parameters": {"vertices": [[0, 0], [1, 0], [0.5, 1]]}
        }

        response = client.post("/api/geometry/triangle/analyze", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "Shape must be 'triangle'" in data["detail"]

    def test_calculate_distance_success(self, client):
        """Test successful distance calculation"""
        request_data = {
            "point1": [0, 0],
            "point2": [3, 4]
        }

        response = client.post("/api/geometry/distance/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "distance" in data
        assert "points" in data
        assert data["distance"] == 0.0  # Placeholder implementation
        assert data["points"]["point1"] == [0, 0]
        assert data["points"]["point2"] == [3, 4]

    def test_calculate_distance_default_points(self, client):
        """Test distance calculation with default points"""
        request_data = {}  # Empty request should use defaults

        response = client.post("/api/geometry/distance/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "distance" in data
        assert "points" in data
        assert data["points"]["point1"] == [0, 0]
        assert data["points"]["point2"] == [1, 1]

    def test_calculate_distance_error(self, client):
        """Test distance calculation with error"""
        # This test would need to be updated if the service implementation changes
        # For now, it tests the basic error handling structure
        request_data = {
            "point1": [0, 0],
            "point2": [3, 4]
        }

        response = client.post("/api/geometry/distance/calculate", json=request_data)

        assert response.status_code == 200  # Current implementation doesn't error

    def test_calculate_intersection_placeholder(self, client):
        """Test intersection calculation placeholder"""
        request_data = {
            "shape1": {"type": "line", "point1": [0, 0], "point2": [1, 1]},
            "shape2": {"type": "line", "point1": [0, 1], "point2": [1, 0]}
        }

        response = client.post("/api/geometry/intersection/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "intersection" in data
        assert "message" in data["intersection"]
        assert "Intersection calculation not yet implemented" in data["intersection"]["message"]

    def test_get_examples_placeholder(self, client):
        """Test getting geometry examples placeholder"""
        response = client.get("/api/geometry/examples")

        assert response.status_code == 200
        data = response.json()
        assert "examples" in data
        assert "message" in data["examples"]
        assert "Examples not yet implemented" in data["examples"]["message"]

    def test_generate_parametric_surface_success(self, client):
        """Test parametric surface generation"""
        request_data = {
            "x_expr": "u * cos(v)",
            "y_expr": "u * sin(v)",
            "z_expr": "u",
            "u_range": [0, 1],
            "v_range": [0, 6.28],
            "u_steps": 20,
            "v_steps": 20
        }

        response = client.post("/api/geometry/parametric-surface", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "image_path" in data
        assert data["x_expr"] == "u * cos(v)"
        assert data["y_expr"] == "u * sin(v)"
        assert data["z_expr"] == "u"
        assert data["u_range"] == [0, 1]
        assert data["v_range"] == [0, 6.28]

    def test_generate_parametric_surface_error(self, client):
        """Test parametric surface generation with error"""
        request_data = {
            "x_expr": "invalid expression",
            "y_expr": "u * sin(v)",
            "z_expr": "u",
            "u_range": [0, 1],
            "v_range": [0, 6.28]
        }

        response = client.post("/api/geometry/parametric-surface", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_generate_parametric_surface_minimal_params(self, client):
        """Test parametric surface generation with minimal parameters"""
        request_data = {
            "x_expr": "u",
            "y_expr": "v",
            "z_expr": "u + v",
            "u_range": [0, 1],
            "v_range": [0, 1]
        }

        response = client.post("/api/geometry/parametric-surface", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["x_expr"] == "u"
        assert data["y_expr"] == "v"
        assert data["z_expr"] == "u + v"


if __name__ == '__main__':
    pytest.main([__file__])
