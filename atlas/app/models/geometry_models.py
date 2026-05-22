"""
Geometry Models for Analytical Geometry Router

Models for geometric shapes, operations, and responses used in analytical geometry calculations.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class ShapeType(str, Enum):
    """Enumeration of supported geometric shapes"""
    CIRCLE = "circle"
    ELLIPSE = "ellipse"
    PARABOLA = "parabola"
    HYPERBOLA = "hyperbola"
    LINE = "line"
    TRIANGLE = "triangle"
    POINT = "point"
    PLANE = "plane"


class GeometryOperation(str, Enum):
    """Enumeration of supported geometry operations"""
    ANALYZE = "analyze"
    CALCULATE = "calculate"
    INTERSECT = "intersect"
    TRANSFORM = "transform"
    PLOT = "plot"


class GeometryRequest(BaseModel):
    """Request model for geometry operations"""
    shape: ShapeType = Field(..., description="Type of geometric shape")
    operation: GeometryOperation = Field(..., description="Operation to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Shape-specific parameters")
    coordinate_system: str = Field(default="cartesian", description="Coordinate system to use")


class GeometryResponse(BaseModel):
    """Response model for geometry operations"""
    shape: ShapeType = Field(..., description="Type of geometric shape")
    operation: GeometryOperation = Field(..., description="Operation performed")
    result: Dict[str, Any] = Field(..., description="Operation results")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Shape properties")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class DistanceRequest(BaseModel):
    """Request model for distance calculations"""
    point1: List[float] = Field(..., description="First point coordinates [x, y] or [x, y, z]")
    point2: List[float] = Field(..., description="Second point coordinates [x, y] or [x, y, z]")
    object_type: str = Field(default="point_to_point", description="Type of distance calculation")


class DistanceResponse(BaseModel):
    """Response model for distance calculations"""
    distance: float = Field(..., description="Calculated distance")
    points: Dict[str, List[float]] = Field(..., description="Points used in calculation")
    formula: str = Field(..., description="Formula used for calculation")


class IntersectionRequest(BaseModel):
    """Request model for intersection calculations"""
    shape1: Dict[str, Any] = Field(..., description="First geometric shape")
    shape2: Dict[str, Any] = Field(..., description="Second geometric shape")
    shape1_type: ShapeType = Field(..., description="Type of first shape")
    shape2_type: ShapeType = Field(..., description="Type of second shape")


class IntersectionResponse(BaseModel):
    """Response model for intersection calculations"""
    intersection_points: List[List[float]] = Field(default_factory=list, description="Intersection points")
    intersection_type: str = Field(..., description="Type of intersection")
    shapes: Dict[str, Any] = Field(..., description="Original shapes")


class ParametricSurfaceRequest(BaseModel):
    """Request model for parametric surface generation"""
    x_expr: str = Field(..., description="Expression for x coordinate")
    y_expr: str = Field(..., description="Expression for y coordinate")
    z_expr: str = Field(..., description="Expression for z coordinate")
    u_range: Tuple[float, float] = Field(..., description="Range for u parameter (min, max)")
    v_range: Tuple[float, float] = Field(..., description="Range for v parameter (min, max)")
    u_steps: int = Field(default=50, description="Number of steps in u direction")
    v_steps: int = Field(default=50, description="Number of steps in v direction")


class ParametricSurfaceResponse(BaseModel):
    """Response model for parametric surface generation"""
    image_path: str = Field(..., description="Path to generated surface image")
    x_expr: str = Field(..., description="X expression used")
    y_expr: str = Field(..., description="Y expression used")
    z_expr: str = Field(..., description="Z expression used")
    u_range: Tuple[float, float] = Field(..., description="U range used")
    v_range: Tuple[float, float] = Field(..., description="V range used")
    surface_data: Optional[Dict[str, Any]] = Field(None, description="Surface data points")


class CircleProperties(BaseModel):
    """Properties of a circle"""
    center: List[float] = Field(..., description="Center point [x, y]")
    radius: float = Field(..., description="Radius of the circle")
    area: float = Field(..., description="Area of the circle")
    circumference: float = Field(..., description="Circumference of the circle")
    equation: str = Field(..., description="Standard equation of the circle")


class EllipseProperties(BaseModel):
    """Properties of an ellipse"""
    center: List[float] = Field(..., description="Center point [x, y]")
    semi_major_axis: float = Field(..., description="Length of semi-major axis")
    semi_minor_axis: float = Field(..., description="Length of semi-minor axis")
    foci: List[List[float]] = Field(..., description="Foci points")
    eccentricity: float = Field(..., description="Eccentricity of the ellipse")
    area: float = Field(..., description="Area of the ellipse")
    equation: str = Field(..., description="Standard equation of the ellipse")


class LineProperties(BaseModel):
    """Properties of a line"""
    slope: Optional[float] = Field(None, description="Slope of the line")
    intercept: Optional[float] = Field(None, description="Y-intercept")
    equation: str = Field(..., description="Equation of the line")
    normal_vector: Optional[List[float]] = Field(None, description="Normal vector for 3D lines")
    direction_vector: Optional[List[float]] = Field(None, description="Direction vector")


class TriangleProperties(BaseModel):
    """Properties of a triangle"""
    vertices: List[List[float]] = Field(..., description="Triangle vertices [[x1,y1], [x2,y2], [x3,y3]]")
    sides: List[float] = Field(..., description="Lengths of the three sides")
    angles: List[float] = Field(..., description="Angles at each vertex in degrees")
    area: float = Field(..., description="Area of the triangle")
    perimeter: float = Field(..., description="Perimeter of the triangle")
    centroid: List[float] = Field(..., description="Centroid coordinates")
    triangle_type: str = Field(..., description="Type of triangle (equilateral, isosceles, scalene)")
