"""
Models for Mathematics AI Application
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any


# Base response model
class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


# Arithmetic models
class ArithmeticOperation(BaseModel):
    """Model for arithmetic operations"""
    operation: str = Field(..., description="Type of operation")
    operands: List[float] = Field(..., description="List of operands")


class ArithmeticResult(BaseModel):
    """Model for arithmetic results"""
    result: float = Field(..., description="Result of the operation")
    operation: str = Field(..., description="Operation performed")
    operands: List[float] = Field(..., description="Operands used")


# Equation models
class EquationSolver(BaseModel):
    """Model for equation solving"""
    equation: str = Field(..., description="Mathematical equation to solve")
    variable: str = Field(default="x", description="Variable to solve for")


class EquationResult(BaseModel):
    """Model for equation results"""
    solutions: List[Union[float, str]] = Field(..., description="Solutions to the equation")
    equation: str = Field(..., description="Original equation")
    variable: str = Field(..., description="Variable solved for")


# Calculus models
class CalculusRequest(BaseModel):
    """Unified model for calculus operations"""
    expression: str = Field(..., description="Mathematical expression")
    operation: str = Field(..., description="Type of calculus operation")
    variable: str = Field(default="x", description="Main variable")
    order: Optional[int] = Field(default=1, description="Order for derivatives")
    limits: Optional[List[float]] = Field(None, description="Limits for definite integrals")


class CalculusResponse(BaseModel):
    """Unified model for calculus operation results"""
    original_expression: str = Field(..., description="Original mathematical expression")
    result: str = Field(..., description="Result of the calculus operation")
    operation: str = Field(..., description="Operation performed")
    variable: str = Field(..., description="Variable used")
    steps: List[str] = Field(..., description="Detailed steps of the calculation")


# Statistics models
class StatisticsData(BaseModel):
    """Model for statistics data"""
    data: List[float] = Field(..., description="List of numerical data")


class StatisticsResult(BaseModel):
    """Model for statistics results"""
    mean: float = Field(..., description="Mean of the data")
    median: float = Field(..., description="Median of the data")
    mode: Optional[float] = Field(None, description="Mode of the data")
    std_dev: float = Field(..., description="Standard deviation")
    variance: float = Field(..., description="Variance")
    min: float = Field(..., description="Minimum value")
    max: float = Field(..., description="Maximum value")
    count: int = Field(..., description="Number of data points")


# Graphing models
class GraphingRequest(BaseModel):
    """Model for graphing requests"""
    expression: str = Field(..., description="Mathematical expression to graph")
    x_min: float = Field(default=-10, description="Minimum x value")
    x_max: float = Field(default=10, description="Maximum x value")
    points: int = Field(default=1000, description="Number of points to plot")


class GraphingResult(BaseModel):
    """Model for graphing results"""
    image_path: str = Field(..., description="Path to the generated graph image")
    expression: str = Field(..., description="Expression graphed")


# Advanced Algebra models
class MatrixRequest(BaseModel):
    """Model for matrix operations"""
    matrix: List[List[float]] = Field(..., description="Matrix data")
    operation: Optional[str] = Field(None, description="Operation to perform")


class MatrixResult(BaseModel):
    """Model for matrix results"""
    result: Union[float, List[List[float]], Dict[str, Any]] = Field(..., description="Result of matrix operation")
    operation: str = Field(..., description="Operation performed")


class PolynomialRequest(BaseModel):
    """Model for polynomial operations"""
    coefficients: List[float] = Field(..., description="Polynomial coefficients")
    operation: Optional[str] = Field(None, description="Operation to perform")


class PolynomialResult(BaseModel):
    """Model for polynomial results"""
    result: Union[List[float], str, Dict[str, Any]] = Field(..., description="Result of polynomial operation")
    operation: str = Field(..., description="Operation performed")


class ComplexNumberRequest(BaseModel):
    """Model for complex number operations"""
    real: float = Field(..., description="Real part")
    imag: float = Field(..., description="Imaginary part")
    operation: Optional[str] = Field(None, description="Operation to perform")
    # Additional fields for binary operations
    real1: Optional[float] = Field(None, description="Real part of first number")
    imag1: Optional[float] = Field(None, description="Imaginary part of first number")
    real2: Optional[float] = Field(None, description="Real part of second number")
    imag2: Optional[float] = Field(None, description="Imaginary part of second number")


class ComplexNumberResult(BaseModel):
    """Model for complex number results"""
    result: Union[Dict[str, float], float, str] = Field(..., description="Result of complex number operation")
    operation: str = Field(..., description="Operation performed")


# Differential Equations models
class DifferentialEquationRequest(BaseModel):
    """Model for differential equation solving"""
    equation: str = Field(..., description="Differential equation")
    function: str = Field(default="y", description="Function to solve for")
    variable: str = Field(default="x", description="Independent variable")
    initial_conditions: Optional[Dict[str, float]] = Field(None, description="Initial conditions")


class DifferentialEquationResult(BaseModel):
    """Model for differential equation results"""
    solution: str = Field(..., description="Solution to the differential equation")
    equation: str = Field(..., description="Original differential equation")
    method: str = Field(..., description="Method used to solve")


# Analytical Geometry models
class PointRequest(BaseModel):
    """Model for point operations"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: Optional[float] = Field(None, description="Z coordinate for 3D")


class LineRequest(BaseModel):
    """Model for line operations"""
    point1: PointRequest = Field(..., description="First point")
    point2: PointRequest = Field(..., description="Second point")


class CircleRequest(BaseModel):
    """Model for circle operations"""
    center: PointRequest = Field(..., description="Center point")
    radius: float = Field(..., description="Radius")


class GeometryResult(BaseModel):
    """Model for geometry results"""
    result: Union[float, str, Dict[str, Any]] = Field(..., description="Result of geometry operation")
    operation: str = Field(..., description="Operation performed")


# Number Theory models
class NumberTheoryRequest(BaseModel):
    """Model for number theory operations"""
    number: int = Field(..., description="Number to analyze")
    operation: Optional[str] = Field(None, description="Operation to perform")


class NumberTheoryResult(BaseModel):
    """Model for number theory results"""
    result: Union[bool, int, List[int], Dict[str, Any]] = Field(..., description="Result of number theory operation")
    operation: str = Field(..., description="Operation performed")


# Optimization models
class OptimizationRequest(BaseModel):
    """Model for optimization problems"""
    objective: str = Field(..., description="Objective function")
    constraints: List[str] = Field(default=[], description="Constraint functions")
    variables: List[str] = Field(..., description="Variables to optimize")
    bounds: Optional[Dict[str, List[float]]] = Field(None, description="Variable bounds")


class OptimizationResult(BaseModel):
    """Model for optimization results"""
    optimal_value: float = Field(..., description="Optimal value of objective function")
    optimal_variables: Dict[str, float] = Field(..., description="Optimal variable values")
    status: str = Field(..., description="Optimization status")


# NLP Mathematical models
class MathNLPRequest(BaseModel):
    """Model for mathematical NLP processing"""
    text: str = Field(..., description="Mathematical text to process")
    operation: Optional[str] = Field(None, description="Specific operation to perform")


class MathNLPResult(BaseModel):
    """Model for mathematical NLP results"""
    parsed_expression: str = Field(..., description="Parsed mathematical expression")
    result: Optional[Union[float, str]] = Field(None, description="Computed result if applicable")
    confidence: float = Field(..., description="Confidence score of parsing")


# Quantum Computing models
class QuantumComputingRequest(BaseModel):
    """Model for quantum computing operations"""
    qubits: int = Field(..., description="Number of qubits for the quantum circuit")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Algorithm-specific parameters")
    shots: Optional[int] = Field(default=8192, description="Number of measurement shots")
    framework: Optional[str] = Field(default="qiskit", description="Quantum computing framework to use")


class QuantumComputingResult(BaseModel):
    """Model for quantum computing operation results"""
    circuit_info: Dict[str, Any] = Field(..., description="Information about the quantum circuit")
    measurement_results: Dict[str, float] = Field(..., description="Measurement probabilities")
    execution_time: float = Field(..., description="Execution time in seconds")
    framework: str = Field(..., description="Framework used for execution")
    algorithm_metrics: Optional[Dict[str, Any]] = Field(None, description="Algorithm-specific metrics")


# Response models for advanced_algebra_old.py compatibility
class MatrixResponse(BaseModel):
    """Response model for matrix operations"""
    success: bool = True
    message: Optional[str] = None
    result: Union[float, List[List[float]], Dict[str, Any]] = Field(..., description="Matrix operation result")
    operation: str = Field(..., description="Operation performed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")


class ComplexNumberResponse(BaseModel):
    """Response model for complex number operations"""
    success: bool = True
    message: Optional[str] = None
    result: Union[Dict[str, float], float, str] = Field(..., description="Complex number operation result")
    operation: str = Field(..., description="Operation performed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    representation: Optional[str] = Field(default=None, description="String representation")


class PolynomialResponse(BaseModel):
    """Response model for polynomial operations"""
    success: bool = True
    message: Optional[str] = None
    result: Union[List[float], str, Dict[str, Any]] = Field(..., description="Polynomial operation result")
    operation: str = Field(..., description="Operation performed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")


class LinearSystemRequest(BaseModel):
    """Request model for linear system operations"""
    matrix: List[List[float]] = Field(..., description="Coefficient matrix")
    constants: List[float] = Field(..., description="Constants vector")
    method: Optional[str] = Field("solve", description="Solution method")


class LinearSystemResponse(BaseModel):
    """Response model for linear system operations"""
    success: bool = True
    message: Optional[str] = None
    result: Union[List[float], Dict[str, Any]] = Field(..., description="Linear system solution")
    operation: str = Field(..., description="Operation performed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
