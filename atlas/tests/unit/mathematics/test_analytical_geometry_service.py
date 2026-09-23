"""
Tests for Analytical Geometry Service
"""

import pytest
from app.services.analytical_geometry import AnalyticalGeometryService
from app.models.models import PointRequest, LineRequest, GeometryResult


class TestAnalyticalGeometryService:
    """Test cases for AnalyticalGeometryService"""

    @pytest.fixture
    def service(self):
        """Fixture to provide AnalyticalGeometryService instance"""
        return AnalyticalGeometryService()

    def test_distance_between_points_2d(self, service):
        """Test distance calculation between two 2D points"""
        point1 = PointRequest(x=0, y=0, z=None)
        point2 = PointRequest(x=3, y=4, z=None)

        result = service.distance_between_points(point1, point2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "distance"
        assert isinstance(result.result, (int, float))
        assert result.result == 5.0

    def test_distance_between_points_3d(self, service):
        """Test distance calculation between two 3D points"""
        point1 = PointRequest(x=0, y=0, z=0)
        point2 = PointRequest(x=1, y=1, z=1)

        result = service.distance_between_points(point1, point2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "distance"
        assert isinstance(result.result, (int, float))
        assert abs(result.result - 1.7320508075688772) < 1e-6

    def test_midpoint_calculation(self, service):
        """Test midpoint calculation between two points"""
        point1 = PointRequest(x=0, y=0, z=None)
        point2 = PointRequest(x=4, y=6, z=None)

        result = service.midpoint(point1, point2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "midpoint"
        assert isinstance(result.result, dict)
        assert "x" in result.result
        assert "y" in result.result
        assert result.result["x"] == 2.0
        assert result.result["y"] == 3.0

    def test_line_equation_from_points(self, service):
        """Test line equation calculation from two points"""
        point1 = PointRequest(x=1, y=2, z=None)
        point2 = PointRequest(x=3, y=4, z=None)

        result = service.line_equation_from_points(point1, point2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "line_equation"
        assert isinstance(result.result, dict)
        assert "slope" in result.result
        assert "intercept" in result.result
        assert result.result["slope"] == 1.0

    def test_line_equation_vertical(self, service):
        """Test line equation for vertical line"""
        point1 = PointRequest(x=2, y=1, z=None)
        point2 = PointRequest(x=2, y=5, z=None)

        result = service.line_equation_from_points(point1, point2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "line_equation"
        assert isinstance(result.result, dict)
        assert result.result["slope"] is None  # Vertical line
        assert result.result["equation"] == "x = 2"

    def test_parallel_lines(self, service):
        """Test checking if two lines are parallel"""
        line1 = LineRequest(point1=PointRequest(x=0, y=0, z=None), point2=PointRequest(x=1, y=1, z=None))
        line2 = LineRequest(point1=PointRequest(x=0, y=2, z=None), point2=PointRequest(x=1, y=3, z=None))

        result = service.are_parallel(line1, line2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "parallel_check"
        assert isinstance(result.result, bool)
        assert result.result is True

    def test_perpendicular_lines(self, service):
        """Test checking if two lines are perpendicular"""
        line1 = LineRequest(point1=PointRequest(x=0, y=0, z=None), point2=PointRequest(x=1, y=1, z=None))
        line2 = LineRequest(point1=PointRequest(x=0, y=0, z=None), point2=PointRequest(x=-1, y=1, z=None))

        result = service.are_perpendicular(line1, line2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "perpendicular_check"
        assert isinstance(result.result, bool)
        assert result.result is True

    def test_line_intersection(self, service):
        """Test intersection point of two lines"""
        line1 = LineRequest(point1=PointRequest(x=0, y=0, z=None), point2=PointRequest(x=2, y=2, z=None))
        line2 = LineRequest(point1=PointRequest(x=0, y=2, z=None), point2=PointRequest(x=2, y=0, z=None))

        result = service.line_intersection(line1, line2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "intersection"
        assert isinstance(result.result, dict)
        assert "x" in result.result
        assert "y" in result.result
        assert result.result["x"] == 1.0
        assert result.result["y"] == 1.0

    def test_parallel_lines_intersection(self, service):
        """Test intersection of parallel lines (should return None)"""
        line1 = LineRequest(point1=PointRequest(x=0, y=0, z=None), point2=PointRequest(x=1, y=1, z=None))
        line2 = LineRequest(point1=PointRequest(x=0, y=1, z=None), point2=PointRequest(x=1, y=2, z=None))

        result = service.line_intersection(line1, line2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "intersection"
        assert result.result is None

    def test_circle_equation(self, service):
        """Test circle equation from center and radius"""
        center = PointRequest(x=0, y=0, z=None)
        radius = 5.0

        result = service.circle_equation(center, radius)

        assert isinstance(result, GeometryResult)
        assert result.operation == "circle_equation"
        assert isinstance(result.result, dict)
        assert "equation" in result.result
        assert "x^2 + y^2 = 25" in result.result["equation"]

    def test_circle_from_three_points(self, service):
        """Test circle calculation from three points"""
        point1 = PointRequest(x=0, y=0, z=None)
        point2 = PointRequest(x=1, y=0, z=None)
        point3 = PointRequest(x=0, y=1, z=None)

        result = service.circle_from_three_points(point1, point2, point3)

        assert isinstance(result, GeometryResult)
        assert result.operation == "circle_from_points"
        assert isinstance(result.result, dict)
        assert "center" in result.result
        assert "radius" in result.result

    def test_point_on_circle(self, service):
        """Test checking if point lies on circle"""
        center = PointRequest(x=0, y=0, z=None)
        radius = 5.0
        point = PointRequest(x=3, y=4, z=None)

        result = service.point_on_circle(center, radius, point)

        assert isinstance(result, GeometryResult)
        assert result.operation == "point_on_circle"
        assert isinstance(result.result, bool)
        assert result.result is True

    def test_point_not_on_circle(self, service):
        """Test checking if point does not lie on circle"""
        center = PointRequest(x=0, y=0, z=None)
        radius = 5.0
        point = PointRequest(x=3, y=5, z=None)

        result = service.point_on_circle(center, radius, point)

        assert isinstance(result, GeometryResult)
        assert result.operation == "point_on_circle"
        assert isinstance(result.result, bool)
        assert result.result is False

    def test_tangent_lines_to_circle(self, service):
        """Test tangent lines from point to circle"""
        center = PointRequest(x=0, y=0, z=None)
        radius = 5.0
        point = PointRequest(x=5, y=5, z=None)

        result = service.tangent_lines_to_circle(center, radius, point)

        assert isinstance(result, GeometryResult)
        assert result.operation == "tangent_lines"
        assert isinstance(result.result, dict)
        assert "tangents" in result.result

    def test_circle_intersection(self, service):
        """Test intersection points of two circles"""
        center1 = PointRequest(x=0, y=0, z=None)
        radius1 = 5.0
        center2 = PointRequest(x=6, y=0, z=None)
        radius2 = 5.0

        result = service.circle_intersection(center1, radius1, center2, radius2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "circle_intersection"
        assert isinstance(result.result, dict)
        assert "intersection_points" in result.result

    def test_conic_sections_ellipse(self, service):
        """Test ellipse equation"""
        result = service.conic_section_equation("ellipse", a=5, b=3)

        assert isinstance(result, GeometryResult)
        assert result.operation == "conic_section"
        assert isinstance(result.result, dict)
        assert "equation" in result.result

    def test_conic_sections_parabola(self, service):
        """Test parabola equation"""
        result = service.conic_section_equation("parabola", p=4)

        assert isinstance(result, GeometryResult)
        assert result.operation == "conic_section"
        assert isinstance(result.result, dict)
        assert "equation" in result.result

    def test_conic_sections_hyperbola(self, service):
        """Test hyperbola equation"""
        result = service.conic_section_equation("hyperbola", a=3, b=2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "conic_section"
        assert isinstance(result.result, dict)
        assert "equation" in result.result

    def test_vector_operations_addition(self, service):
        """Test vector addition"""
        v1 = [1, 2, 3]
        v2 = [4, 5, 6]

        result = service.vector_addition(v1, v2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "vector_addition"
        assert result.result == [5, 7, 9]

    def test_vector_operations_dot_product(self, service):
        """Test vector dot product"""
        v1 = [1, 2, 3]
        v2 = [4, 5, 6]

        result = service.vector_dot_product(v1, v2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "vector_dot_product"
        assert isinstance(result.result, (int, float))
        assert result.result == 32

    def test_vector_operations_cross_product(self, service):
        """Test vector cross product"""
        v1 = [1, 2, 3]
        v2 = [4, 5, 6]

        result = service.vector_cross_product(v1, v2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "vector_cross_product"
        assert result.result == [-3, 6, -3]

    def test_vector_operations_magnitude(self, service):
        """Test vector magnitude"""
        v = [3, 4]

        result = service.vector_magnitude(v)

        assert isinstance(result, GeometryResult)
        assert result.operation == "vector_magnitude"
        assert isinstance(result.result, (int, float))
        assert result.result == 5.0

    def test_vector_operations_unit_vector(self, service):
        """Test unit vector calculation"""
        v = [3, 4]

        result = service.vector_unit(v)

        assert isinstance(result, GeometryResult)
        assert result.operation == "vector_unit"
        assert isinstance(result.result, list)
        assert abs(result.result[0] - 0.6) < 1e-6
        assert abs(result.result[1] - 0.8) < 1e-6

    def test_plane_equation_from_points(self, service):
        """Test plane equation from three points"""
        point1 = PointRequest(x=1, y=0, z=0)
        point2 = PointRequest(x=0, y=1, z=0)
        point3 = PointRequest(x=0, y=0, z=1)

        result = service.plane_equation_from_points(point1, point2, point3)

        assert isinstance(result, GeometryResult)
        assert result.operation == "plane_equation"
        assert isinstance(result.result, dict)
        assert "equation" in result.result

    def test_distance_point_to_plane(self, service):
        """Test distance from point to plane"""
        point = PointRequest(x=1, y=1, z=1)
        plane_coeffs = [1, 1, 1, -3]  # x + y + z - 3 = 0

        result = service.distance_point_to_plane(point, plane_coeffs)

        assert isinstance(result, GeometryResult)
        assert result.operation == "point_to_plane_distance"
        assert isinstance(result.result, (int, float))
        assert abs(result.result - 0.0) < 1e-9

    def test_line_plane_intersection(self, service):
        """Test intersection of line and plane"""
        line_point = PointRequest(x=0, y=0, z=0)
        line_direction = [1, 1, 1]
        plane_coeffs = [1, 1, 1, -3]

        result = service.line_plane_intersection(line_point, line_direction, plane_coeffs)

        assert isinstance(result, GeometryResult)
        assert result.operation == "line_plane_intersection"
        assert isinstance(result.result, dict)
        assert "intersection_point" in result.result

    def test_angle_between_vectors(self, service):
        """Test angle calculation between two vectors"""
        v1 = [1, 0, 0]
        v2 = [0, 1, 0]

        result = service.angle_between_vectors(v1, v2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "angle_between_vectors"
        assert isinstance(result.result, (int, float))
        assert abs(result.result - 90.0) < 1e-6

    def test_projection_of_vector(self, service):
        """Test vector projection"""
        v1 = [3, 4, 0]
        v2 = [1, 0, 0]

        result = service.vector_projection(v1, v2)

        assert isinstance(result, GeometryResult)
        assert result.operation == "vector_projection"
        assert result.result == [3, 0, 0]

    def test_area_triangle(self, service):
        """Test triangle area calculation"""
        point1 = PointRequest(x=0, y=0, z=None)
        point2 = PointRequest(x=4, y=0, z=None)
        point3 = PointRequest(x=0, y=3, z=None)

        result = service.triangle_area(point1, point2, point3)

        assert isinstance(result, GeometryResult)
        assert result.operation == "triangle_area"
        assert isinstance(result.result, (int, float))
        assert result.result == 6.0

    def test_centroid_triangle(self, service):
        """Test triangle centroid calculation"""
        point1 = PointRequest(x=0, y=0, z=None)
        point2 = PointRequest(x=4, y=0, z=None)
        point3 = PointRequest(x=0, y=3, z=None)

        result = service.triangle_centroid(point1, point2, point3)

        assert isinstance(result, GeometryResult)
        assert result.operation == "triangle_centroid"
        assert isinstance(result.result, dict)
        assert result.result["x"] == 4/3
        assert result.result["y"] == 1.0

    def test_polygon_area(self, service):
        """Test polygon area calculation"""
        points = [
            PointRequest(x=0, y=0, z=None),
            PointRequest(x=4, y=0, z=None),
            PointRequest(x=4, y=3, z=None),
            PointRequest(x=0, y=3, z=None)
        ]

        result = service.polygon_area(points)

        assert isinstance(result, GeometryResult)
        assert result.operation == "polygon_area"
        assert isinstance(result.result, (int, float))
        assert result.result == 12.0

    def test_invalid_input_distance(self, service):
        """Test distance calculation with invalid input"""
        point1 = PointRequest(x=0, y=0, z=None)
        point2 = PointRequest(x=float('inf'), y=0, z=None)

        with pytest.raises(ValueError):
            service.distance_between_points(point1, point2)

    def test_collinear_points_circle(self, service):
        """Test circle from three collinear points (should fail)"""
        point1 = PointRequest(x=0, y=0, z=None)
        point2 = PointRequest(x=1, y=1, z=None)
        point3 = PointRequest(x=2, y=2, z=None)

        with pytest.raises(ValueError):
            service.circle_from_three_points(point1, point2, point3)

    def test_zero_vector_magnitude(self, service):
        """Test magnitude of zero vector"""
        v = [0, 0, 0]

        with pytest.raises(ValueError):
            service.vector_unit(v)

    def test_coplanar_points_plane(self, service):
        """Test plane from three coplanar points (should work)"""
        point1 = PointRequest(x=0, y=0, z=0)
        point2 = PointRequest(x=1, y=0, z=0)
        point3 = PointRequest(x=0, y=1, z=0)

        result = service.plane_equation_from_points(point1, point2, point3)

        assert isinstance(result, GeometryResult)
        assert result.operation == "plane_equation"
