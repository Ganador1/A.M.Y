"""
Models for Mathematics AI Application
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any, Tuple
from datetime import datetime


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


class EquationRequest(BaseModel):
    """Model for equation requests"""
    equation: str = Field(..., description="Mathematical equation to solve")
    variable: str = Field(default="x", description="Variable to solve for")


class EquationResponse(BaseModel):
    """Model for equation responses"""
    solutions: List[Union[float, str]] = Field(..., description="Solutions to the equation")
    equation: str = Field(..., description="Original equation")
    variable: str = Field(..., description="Variable solved for")


# Calculus models
class DerivativeRequest(BaseModel):
    """Model for derivative calculation"""
    expression: str = Field(..., description="Mathematical expression")
    variable: str = Field(default="x", description="Variable to differentiate with respect to")
    order: int = Field(default=1, description="Order of derivative")


class IntegralRequest(BaseModel):
    """Model for integral calculation"""
    expression: str = Field(..., description="Mathematical expression")
    variable: str = Field(default="x", description="Variable to integrate with respect to")
    lower_limit: Optional[float] = Field(None, description="Lower limit for definite integral")
    upper_limit: Optional[float] = Field(None, description="Upper limit for definite integral")


class CalculusResult(BaseModel):
    """Model for calculus results"""
    result: str = Field(..., description="Result of the calculus operation")
    expression: str = Field(..., description="Original expression")
    operation: str = Field(..., description="Operation performed")


class CalculusRequest(BaseModel):
    """Model for calculus requests"""
    expression: str = Field(..., description="Mathematical expression")
    variable: str = Field(default="x", description="Variable")
    operation: str = Field(..., description="Operation type (derivative, integral)")
    order: Optional[int] = Field(1, description="Order for derivatives")
    lower_limit: Optional[float] = Field(None, description="Lower limit for integrals")
    upper_limit: Optional[float] = Field(None, description="Upper limit for integrals")


class CalculusResponse(BaseModel):
    """Model for calculus responses"""
    result: str = Field(..., description="Result of the calculus operation")
    expression: str = Field(..., description="Original expression")
    operation: str = Field(..., description="Operation performed")


# Partial Derivative models
class PartialDerivativeRequest(BaseModel):
    """Model for partial derivative calculation"""
    expression: str = Field(..., description="Mathematical expression")
    variables: List[str] = Field(..., description="Variables to differentiate with respect to")
    orders: List[int] = Field(default=[1], description="Orders of derivatives for each variable")


class PartialDerivativeResponse(BaseModel):
    """Model for partial derivative results"""
    result: str = Field(..., description="Result of the partial derivative")
    expression: str = Field(..., description="Original expression")
    variables: List[str] = Field(..., description="Variables differentiated")
    orders: List[int] = Field(..., description="Orders of derivatives")


# Fourier Transform models
class FourierTransformRequest(BaseModel):
    """Model for Fourier Transform requests"""
    expression: str = Field(..., description="Mathematical expression to transform")
    variable: str = Field(..., description="Original variable")
    transform_variable: str = Field(..., description="Variable for the transformed function")


class FourierTransformResponse(BaseModel):
    """Model for Fourier Transform results"""
    original_expression: str = Field(..., description="Original mathematical expression")
    transformed_expression: str = Field(..., description="Result of the Fourier Transform")
    variable: str = Field(..., description="Original variable")
    transform_variable: str = Field(..., description="Variable for the transformed function")
    steps: List[str] = Field(..., description="Steps taken to perform the transform")


# Differential Equations models
class DifferentialEquationRequest(BaseModel):
    """Model for differential equation solving"""
    equation: str = Field(..., description="Differential equation")
    function: str = Field(default="y", description="Function to solve for")
    variable: str = Field(default="x", description="Independent variable")
    initial_conditions: Optional[Dict[str, float]] = Field(None, description="Initial conditions")


class DifferentialEquationResponse(BaseModel):
    """Model for differential equation results"""
    solution: str = Field(..., description="Solution to the differential equation")
    equation: str = Field(..., description="Original differential equation")
    method: str = Field(..., description="Method used to solve")


# Partial Differential Equations models
class PartialDifferentialEquationRequest(BaseModel):
    """Model for Partial Differential Equation solving"""
    equation: str = Field(..., description="Partial differential equation")
    function: str = Field(..., description="Function to solve for (e.g., 'u(x,y)')")
    variables: List[str] = Field(..., description="Independent variables (e.g., ['x', 'y'])")
    boundary_conditions: Optional[Dict[str, str]] = Field(None, description="Boundary conditions")


class PartialDifferentialEquationResponse(BaseModel):
    """Model for Partial Differential Equation results"""
    original_equation: str = Field(..., description="Original partial differential equation")
    solution: str = Field(..., description="Solution to the partial differential equation")
    solution_type: str = Field(..., description="Type of solution (e.g., 'symbolic', 'numerical')")
    steps: List[str] = Field(..., description="Steps taken to solve the PDE")


# Geometry models
class GeometryRequest(BaseModel):
    """Request for geometry operations"""
    shape: str = Field(..., description="Type of geometric shape")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the shape")
    operation: str = Field(..., description="Operation to perform")


class GeometryResponse(BaseModel):
    """Response for geometry operations"""
    shape: str = Field(..., description="Type of geometric shape")
    operation: str = Field(..., description="Operation performed")
    result: Dict[str, Any] = Field(..., description="Result of the operation")
    properties: Optional[Dict[str, Any]] = Field(None, description="Additional properties")
    error: Optional[str] = Field(None, description="Error message if any")


# Analytical Geometry models
class PointRequest(BaseModel):
    """Model for 2D/3D point representation"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: Optional[float] = Field(None, description="Z coordinate (for 3D points)")


class LineRequest(BaseModel):
    """Model for line representation using two points"""
    point1: PointRequest = Field(..., description="First point on the line")
    point2: PointRequest = Field(..., description="Second point on the line")


class GeometryResult(BaseModel):
    """Model for geometry operation results"""
    operation: str = Field(..., description="Type of geometry operation performed")
    result: Any = Field(..., description="Result of the operation")
    success: bool = Field(default=True, description="Whether the operation was successful")
    error: Optional[str] = Field(None, description="Error message if operation failed")


# Parametric Surface models
class ParametricSurfaceRequest(BaseModel):
    """Model for generating 3D parametric surfaces"""
    x_expr: str = Field(..., description="Expression for x(u,v)")
    y_expr: str = Field(..., description="Expression for y(u,v)")
    z_expr: str = Field(..., description="Expression for z(u,v)")
    u_range: List[float] = Field(..., min_length=2, max_length=2, description="[u_min, u_max]")
    v_range: List[float] = Field(..., min_length=2, max_length=2, description="[v_min, v_max]")
    u_points: int = Field(default=50, description="Number of points for u")
    v_points: int = Field(default=50, description="Number of points for v")
    title: Optional[str] = Field(None, description="Title of the plot")


class ParametricSurfaceResponse(BaseModel):
    """Model for Parametric Surface generation results"""
    image_path: str = Field(..., description="Path to the generated 3D surface image")
    x_expr: str = Field(..., description="Expression for x(u,v)")
    y_expr: str = Field(..., description="Expression for y(u,v)")
    z_expr: str = Field(..., description="Expression for z(u,v)")
    u_range: List[float] = Field(..., description="[u_min, u_max]")
    v_range: List[float] = Field(..., description="[v_min, v_max]")


# Number Theory models
class NumberTheoryRequest(BaseModel):
    """Model for number theory operations"""
    number: int = Field(..., description="Number to analyze")
    operation: Optional[str] = Field(None, description="Operation to perform")
    numbers: Optional[List[int]] = Field(None, description="List of numbers for operations like GCD/LCM")
    modulus: Optional[int] = Field(None, description="Modulus for modular operations")
    exponent: Optional[int] = Field(None, description="Exponent for modular exponentiation")
    remainders: Optional[List[int]] = Field(None, description="Remainders for Chinese Remainder Theorem")
    moduli: Optional[List[int]] = Field(None, description="Moduli for Chinese Remainder Theorem")
    base: Optional[int] = Field(None, description="Base for discrete logarithm")


class NumberTheoryResult(BaseModel):
    """Model for number theory results"""
    result: Union[bool, int, List[int], Dict[str, Any]] = Field(..., description="Result of number theory operation")
    operation: str = Field(..., description="Operation performed")


# Cyclic Group Generator models
class CyclicGroupGeneratorRequest(BaseModel):
    """Model for checking if a number is a generator of a cyclic group Z_n"""
    n: int = Field(..., description="The modulus n for the cyclic group Z_n")
    a: int = Field(..., description="The number 'a' to check if it's a generator")


class CyclicGroupGeneratorResponse(BaseModel):
    """Model for Cyclic Group Generator check results"""
    n: int = Field(..., description="The modulus n")
    a: int = Field(..., description="The number 'a' checked")
    is_generator: bool = Field(..., description="True if 'a' is a generator of Z_n, False otherwise")
    order_of_a: Optional[int] = Field(None, description="The order of 'a' modulo n")
    phi_n: Optional[int] = Field(None, description="Euler's totient function phi(n)")
    steps: List[str] = Field(..., description="Steps taken to determine if 'a' is a generator")


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


# Quadratic Programming models
class QuadraticProgrammingRequest(BaseModel):
    """Model for quadratic programming problems"""
    objective_matrix: List[List[float]] = Field(..., description="Quadratic objective matrix Q")
    objective_vector: List[float] = Field(..., description="Linear objective vector c")
    constraint_matrix: Optional[List[List[float]]] = Field(None, description="Constraint matrix A")
    constraint_vector: Optional[List[float]] = Field(None, description="Constraint vector b")
    bounds: Optional[Dict[str, List[float]]] = Field(None, description="Variable bounds")


class QuadraticProgrammingResponse(BaseModel):
    """Model for quadratic programming results"""
    optimal_value: float = Field(..., description="Optimal value of objective function")
    optimal_variables: List[float] = Field(..., description="Optimal variable values")
    status: str = Field(..., description="Optimization status")
    message: str = Field(..., description="Solver message")


# Math NLP models
class MathNLPRequest(BaseModel):
    """Model for mathematical NLP processing"""
    text: str = Field(..., description="Mathematical text to process")
    operation: Optional[str] = Field(None, description="Specific operation to perform")


class MathNLPResult(BaseModel):
    """Model for mathematical NLP results"""
    parsed_expression: str = Field(..., description="Parsed mathematical expression")
    result: Optional[Union[float, str]] = Field(None, description="Computed result if applicable")
    confidence: float = Field(..., description="Confidence score of parsing")


# Combinatorics models
class CombinatoricsRequest(BaseModel):
    """Model for combinatorics operations"""
    operation: str = Field(..., description="Type of combinatorics operation")
    n: int = Field(..., description="Total number of items")
    k: Optional[int] = Field(None, description="Number of items to choose/select")
    with_replacement: bool = Field(default=False, description="Whether to allow replacement")
    ordered: bool = Field(default=False, description="Whether order matters")


class CombinatoricsResult(BaseModel):
    """Model for combinatorics results"""
    result: Union[int, List[List[int]]] = Field(..., description="Result of combinatorics operation")
    operation: str = Field(..., description="Operation performed")
    explanation: str = Field(..., description="Explanation of the result")


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


class StatisticsRequest(BaseModel):
    """Model for statistics requests"""
    data: List[float] = Field(..., description="List of numerical data")
    operations: Optional[List[str]] = Field(None, description="Specific operations to perform")


class StatisticsResponse(BaseModel):
    """Model for statistics responses"""
    mean: float = Field(..., description="Mean of the data")
    median: float = Field(..., description="Median of the data")
    mode: Optional[float] = Field(None, description="Mode of the data")
    std_dev: float = Field(..., description="Standard deviation")
    variance: float = Field(..., description="Variance")
    min: float = Field(..., description="Minimum value")
    max: float = Field(..., description="Maximum value")
    count: int = Field(..., description="Number of data points")


# Linear Regression models
class LinearRegressionRequest(BaseModel):
    """Model for linear regression requests"""
    x_data: List[float] = Field(..., description="X values for regression")
    y_data: List[float] = Field(..., description="Y values for regression")
    degree: int = Field(default=1, description="Degree of polynomial regression")


class LinearRegressionResponse(BaseModel):
    """Model for linear regression responses"""
    coefficients: List[float] = Field(..., description="Regression coefficients")
    r_squared: float = Field(..., description="R-squared value")
    equation: str = Field(..., description="Regression equation")
    predictions: List[float] = Field(..., description="Predicted values")


# Graphing models
class GraphingRequest(BaseModel):
    """Model for graphing requests"""
    expression: str = Field(..., description="Mathematical expression to graph")
    x_min: float = Field(default=-10, description="Minimum x value")
    x_max: float = Field(default=10, description="Maximum x value")
    points: int = Field(default=1000, description="Number of points to plot")
    variable: str = Field(default="x", description="Variable name")
    title: Optional[str] = Field(None, description="Graph title")


class GraphingResult(BaseModel):
    """Model for graphing results"""
    image_path: str = Field(..., description="Path to the generated graph image")
    expression: str = Field(..., description="Expression graphed")


class GraphResponse(BaseModel):
    """Model for graph responses"""
    image_path: str = Field(..., description="Path to the generated graph image")
    expression: str = Field(..., description="Expression graphed")
    x_range: Optional[List[float]] = Field(None, description="X axis range")
    y_range: Optional[List[float]] = Field(None, description="Y axis range")
    points_count: Optional[int] = Field(None, description="Number of points used")


# Graph Theory models
class GraphTheoryRequest(BaseModel):
    """Model for graph theory operations"""
    nodes: List[str] = Field(..., description="List of nodes in the graph")
    edges: List[Tuple[str, str]] = Field(..., description="List of edges in the graph")
    operation: str = Field(..., description="Operation to perform")
    source: Optional[str] = Field(None, description="Source node for the operation")
    target: Optional[str] = Field(None, description="Target node for the operation")


class GraphResult(BaseModel):
    """Model for graph theory operation results"""
    operation: str = Field(..., description="Operation performed")
    result: Dict[str, Any] = Field(..., description="Result of the operation")
    visualization_path: Optional[str] = Field(None, description="Path to graph visualization")
    error: Optional[str] = Field(None, description="Error message if any")


# Cryptography models
class RSAKeyRequest(BaseModel):
    """Model for RSA key generation requests"""
    bits: int = Field(default=2048, description="Key size in bits")


class RSAKeyResponse(BaseModel):
    """Model for RSA key generation responses"""
    public_key: str = Field(..., description="RSA public key")
    private_key: str = Field(..., description="RSA private key")


class RSAEncryptRequest(BaseModel):
    """Model for RSA encryption requests"""
    public_key: str = Field(..., description="RSA public key")
    message: str = Field(..., description="Message to encrypt")


class RSAEncryptResponse(BaseModel):
    """Model for RSA encryption responses"""
    encrypted_message: str = Field(..., description="Encrypted message")


class RSADecryptRequest(BaseModel):
    """Model for RSA decryption requests"""
    private_key: str = Field(..., description="RSA private key")
    encrypted_message: str = Field(..., description="Encrypted message to decrypt")


class RSADecryptResponse(BaseModel):
    """Model for RSA decryption responses"""
    decrypted_message: str = Field(..., description="Decrypted message")


# Scientific AI models
class PINNConfig(BaseModel):
    """Configuration for Physics-Informed Neural Networks"""
    pde_type: str = Field(default="poisson1d", description="Type of PDE to solve")
    domain: List[float] = Field(default=[0, 1], description="Domain boundaries [start, end]")
    num_points: int = Field(default=100, description="Number of training points")
    num_test_points: int = Field(default=1000, description="Number of test points")
    epochs: int = Field(default=100, description="Number of training epochs")
    learning_rate: float = Field(default=0.001, description="Learning rate")
    hidden_layers: List[int] = Field(default=[50, 50], description="Hidden layer sizes")
    activation: str = Field(default="tanh", description="Activation function")


class PINNRequest(BaseModel):
    """Request for PINN-based PDE solving"""
    config: PINNConfig = Field(default_factory=PINNConfig, description="PINN configuration")
    boundary_conditions: Optional[Dict[str, Any]] = Field(None, description="Boundary conditions")
    initial_conditions: Optional[Dict[str, Any]] = Field(None, description="Initial conditions")


class PINNResponse(BaseModel):
    """Response for PINN-based PDE solving"""
    solution: Dict[str, Any] = Field(..., description="PINN solution data")
    loss_history: List[float] = Field(..., description="Training loss history")
    final_loss: float = Field(..., description="Final training loss")
    config: PINNConfig = Field(..., description="Configuration used")


class InverseProblemRequest(BaseModel):
    """Request for inverse problem solving with PINN"""
    observed_data: List[float] = Field(..., description="Observed data points")
    domain: List[float] = Field(default=[0, 1], description="Domain boundaries")
    epochs: int = Field(default=100, description="Number of training epochs")


class InverseProblemResponse(BaseModel):
    """Response for inverse problem solving"""
    estimated_parameters: Dict[str, float] = Field(..., description="Estimated parameters")
    loss_history: List[float] = Field(..., description="Training loss history")
    final_loss: float = Field(..., description="Final training loss")


class AIAgentRequest(BaseModel):
    """Request for creating AI agents"""
    agent_type: str = Field(..., description="Type of AI agent")
    task: str = Field(..., description="Task for the agent")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")


class AIAgentResponse(BaseModel):
    """Response for AI agent creation"""
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Type of agent created")
    capabilities: List[str] = Field(..., description="Agent capabilities")
    status: str = Field(..., description="Agent status")


class ScientificReasoningRequest(BaseModel):
    """Request for scientific reasoning"""
    query: str = Field(..., description="Scientific query to reason about")
    domain: Optional[str] = Field(None, description="Scientific domain")
    context: Optional[str] = Field(None, description="Additional context")


class ScientificReasoningResponse(BaseModel):
    """Response for scientific reasoning"""
    reasoning: str = Field(..., description="Reasoning process")
    conclusion: str = Field(..., description="Final conclusion")
    confidence: float = Field(..., description="Confidence score")
    sources: Optional[List[str]] = Field(None, description="Sources used")


class PINNOptimizationRequest(BaseModel):
    """Request for PINN architecture optimization"""
    pde_type: str = Field(default="poisson1d", description="Type of PDE")
    search_space: Dict[str, List[Any]] = Field(..., description="Search space for optimization")
    max_trials: int = Field(default=10, description="Maximum number of trials")


class PINNOptimizationResponse(BaseModel):
    """Response for PINN optimization"""
    best_config: Dict[str, Any] = Field(..., description="Best configuration found")
    best_loss: float = Field(..., description="Best loss achieved")
    trials: List[Dict[str, Any]] = Field(..., description="All trial results")


# Scientific Discovery and Verification Contracts
class ConjectureResult(BaseModel):
    """Unified data contract for mathematical conjecture results
    
    Used for communication between Agent1 (Symbolic) and Agent2 (Scientific)
    """
    conjecture_id: str = Field(..., description="Unique identifier for the conjecture")
    expression: str = Field(..., description="Mathematical expression in normalized form")
    domain: str = Field(..., description="Mathematical domain (e.g., algebra, calculus, number_theory)")
    complexity: str = Field(..., description="Complexity level (simple, medium, complex)")
    confidence_score: float = Field(default=0.0, description="Initial confidence score from symbolic analysis")
    variables: List[str] = Field(default_factory=list, description="List of variables in the expression")
    normalized_ast: Optional[Dict[str, Any]] = Field(None, description="Normalized AST representation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Creation timestamp")


class VerifiedStatement(BaseModel):
    """Unified data contract for verified mathematical statements
    
    Used for communication between Agent2 (Scientific) and Agent1 (Symbolic)
    """
    statement_id: str = Field(..., description="Unique identifier for the verified statement")
    original_conjecture_id: str = Field(..., description="ID of the original conjecture")
    expression: str = Field(..., description="Mathematical expression that was verified")
    verification_status: str = Field(..., description="Verification status (proved, disproved, undecided)")
    verification_method: str = Field(..., description="Method used for verification (theorem_prover, numerical, heuristic)")
    confidence_score: float = Field(..., description="Final confidence score after verification")
    proof_evidence: Optional[str] = Field(None, description="Evidence or proof sketch")
    counterexample: Optional[str] = Field(None, description="Counterexample if disproved")
    computation_time: float = Field(..., description="Time taken for verification in seconds")
    resources_used: Dict[str, Any] = Field(default_factory=dict, description="Computational resources used")
    timestamp: datetime = Field(default_factory=datetime.now, description="Verification timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
