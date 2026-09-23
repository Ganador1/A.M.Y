"""
Router Amigable - Interfaz de Usuario para Mathematics AI

Módulo FastAPI que proporciona acceso amigable a todas las funciones matemáticas disponibles.
Ofrece una interfaz intuitiva para explorar y utilizar las capacidades de computación
matemática de la plataforma AXIOM, con guías de ayuda y ejemplos prácticos.

Capacidades principales:
- Información general: descripción completa de todas las funciones disponibles
- Ayuda por categorías: documentación detallada para cada área matemática
- Ejemplos completos: casos de uso para todas las categorías disponibles
- Guía de inicio rápido: tutorial paso a paso para nuevos usuarios
- Navegación intuitiva: estructura clara de categorías y endpoints
- Documentación integrada: ejemplos de requests y responses

Catálogo de Endpoints:
- GET /: Información general de todas las funciones matemáticas disponibles
- GET /help/{category}: Ayuda detallada para una categoría específica
- GET /examples: Ejemplos para todas las categorías disponibles
- GET /quick-start: Guía de inicio rápido con ejemplos simples

Dependencias:
- BaseResponse: Modelo estandarizado de respuesta de la API
- FastAPI APIRouter: Framework para definición de rutas
- HTTPException: Manejo de errores HTTP
- typing: Anotaciones de tipos para Python

Uso del Servicio:
    Este router sirve como punto de entrada principal para usuarios nuevos
    y como referencia para usuarios experimentados. Proporciona navegación
    intuitiva hacia las funciones especializadas de cada dominio matemático,
    con ejemplos prácticos y guías de uso detalladas.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from app.models import BaseResponse

router = APIRouter()

@router.get("/", response_model=BaseResponse)
async def get_main_info():
    """
    Get information about all available mathematical functions
    """
    return BaseResponse(
        success=True,
        message="Welcome to Mathematics AI! Here are all available functions:",
        data={
            "categories": [
                {
                    "name": "Arithmetic",
                    "description": "Basic mathematical operations",
                    "endpoint": "/api/arithmetic",
                    "functions": [
                        "Addition, subtraction, multiplication, division",
                        "Powers and roots",
                        "Trigonometric functions",
                        "Logarithms and exponentials"
                    ]
                },
                {
                    "name": "Calculus",
                    "description": "Derivatives, integrals, and advanced calculus",
                    "endpoint": "/api/calculus",
                    "functions": [
                        "Derivatives and integrals",
                        "Limits and series",
                        "Partial derivatives",
                        "Fourier transforms"
                    ]
                },
                {
                    "name": "Equations",
                    "description": "Solve algebraic and transcendental equations",
                    "endpoint": "/api/equations",
                    "functions": [
                        "Linear and quadratic equations",
                        "Systems of equations",
                        "Polynomial equations",
                        "Transcendental equations"
                    ]
                },
                {
                    "name": "Statistics",
                    "description": "Statistical analysis and probability",
                    "endpoint": "/api/statistics",
                    "functions": [
                        "Descriptive statistics",
                        "Probability distributions",
                        "Hypothesis testing",
                        "Regression analysis"
                    ]
                },
                {
                    "name": "Graphing",
                    "description": "Function plotting and visualization",
                    "endpoint": "/api/graphing",
                    "functions": [
                        "2D and 3D plotting",
                        "Function visualization",
                        "Data visualization",
                        "Interactive graphs"
                    ]
                },
                {
                    "name": "Computational Chemistry",
                    "description": "Molecular analysis and quantum chemistry",
                    "endpoint": "/api/chemistry",
                    "functions": [
                        "Molecular property analysis",
                        "Conformer generation",
                        "Sequence analysis",
                        "Quantum chemistry calculations"
                    ]
                },
                {
                    "name": "Quantum Physics",
                    "description": "Quantum mechanical simulations",
                    "endpoint": "/api/quantum-physics",
                    "functions": [
                        "Spin evolution",
                        "Harmonic oscillator",
                        "Quantum state analysis",
                        "Time evolution"
                    ]
                },
                {
                    "name": "Quantum Computing",
                    "description": "Quantum algorithms and circuits",
                    "endpoint": "/api/quantum-computing",
                    "functions": [
                        "Bell states",
                        "Quantum Fourier Transform",
                        "Grover's algorithm",
                        "Circuit simulation"
                    ]
                },
                {
                    "name": "Scientific AI",
                    "description": "AI-powered scientific computing",
                    "endpoint": "/api/scientific-ai",
                    "functions": [
                        "Scientific reasoning",
                        "PDE solving with PINNs",
                        "AI-assisted problem solving",
                        "Advanced mathematical modeling"
                    ]
                },
                {
                    "name": "Advanced Algebra",
                    "description": "Advanced algebraic operations",
                    "endpoint": "/api/advanced-algebra",
                    "functions": [
                        "Matrix operations",
                        "Linear algebra",
                        "Vector calculus",
                        "Tensor operations"
                    ]
                },
                {
                    "name": "Number Theory",
                    "description": "Properties of integers and numbers",
                    "endpoint": "/api/number-theory",
                    "functions": [
                        "Prime numbers",
                        "Factorization",
                        "Number properties",
                        "Cryptographic functions"
                    ]
                },
                {
                    "name": "Optimization",
                    "description": "Mathematical optimization problems",
                    "endpoint": "/api/optimization",
                    "functions": [
                        "Linear programming",
                        "Nonlinear optimization",
                        "Constraint optimization",
                        "Multi-objective optimization"
                    ]
                }
            ],
            "quick_start": {
                "examples": [
                    {
                        "description": "Simple arithmetic",
                        "endpoint": "POST /api/arithmetic/calculate",
                        "body": {"operation": "add", "operands": [5, 3]}
                    },
                    {
                        "description": "Solve equation",
                        "endpoint": "POST /api/equations/solve",
                        "body": {"equation": "x^2 - 4 = 0"}
                    },
                    {
                        "description": "Calculate derivative",
                        "endpoint": "POST /api/calculus/calculate",
                        "body": {"expression": "x^2", "operation": "derivative"}
                    },
                    {
                        "description": "Analyze molecule",
                        "endpoint": "POST /api/chemistry/analyze-molecule",
                        "body": {"smiles": "CCO"}
                    }
                ]
            }
        }
    )

@router.get("/help/{category}", response_model=BaseResponse)
async def get_category_help(category: str):
    """
    Get detailed help for a specific category
    """
    help_data = {
        "arithmetic": {
            "description": "Basic mathematical operations made simple",
            "examples": [
                {
                    "name": "Simple Addition",
                    "endpoint": "POST /api/arithmetic/calculate",
                    "request": {"operation": "add", "operands": [10, 5, 3]},
                    "response": "Result: 18"
                },
                {
                    "name": "Trigonometric Function",
                    "endpoint": "POST /api/arithmetic/calculate",
                    "request": {"operation": "sin", "operands": [30]},
                    "response": "Result: 0.5 (sine of 30 degrees)"
                }
            ],
            "tips": [
                "Use 'add', 'subtract', 'multiply', 'divide' for basic operations",
                "Use 'sin', 'cos', 'tan' for trigonometric functions (input in degrees)",
                "Use 'power' for exponentiation: [base, exponent]",
                "Use 'sqrt' for square root, 'log' for logarithm"
            ]
        },
        "calculus": {
            "description": "Derivatives, integrals, and limits made easy",
            "examples": [
                {
                    "name": "Simple Derivative",
                    "endpoint": "POST /api/calculus/calculate",
                    "request": {"expression": "x^2", "operation": "derivative"},
                    "response": "Result: 2*x"
                },
                {
                    "name": "Definite Integral",
                    "endpoint": "POST /api/calculus/calculate",
                    "request": {"expression": "x", "operation": "integral", "lower_limit": 0, "upper_limit": 1},
                    "response": "Result: 1/2"
                }
            ],
            "tips": [
                "Use 'derivative' or 'integral' as operation type",
                "For definite integrals, specify lower_limit and upper_limit",
                "Use 'limit' endpoint for limit calculations",
                "Use 'taylor' endpoint for Taylor series expansion"
            ]
        },
        "equations": {
            "description": "Solve any equation with ease",
            "examples": [
                {
                    "name": "Quadratic Equation",
                    "endpoint": "POST /api/equations/solve",
                    "request": {"equation": "x^2 - 5*x + 6 = 0"},
                    "response": "Solutions: [2, 3]"
                },
                {
                    "name": "Transcendental Equation",
                    "endpoint": "POST /api/equations/solve",
                    "request": {"equation": "sin(x) = 0.5"},
                    "response": "Solutions: [30, 150, 390, ...]"
                }
            ],
            "tips": [
                "Write equations in natural form: 'x^2 + 2*x - 8 = 0'",
                "Use standard mathematical notation",
                "For systems, use multiple equations",
                "Variable defaults to 'x' if not specified"
            ]
        },
        "chemistry": {
            "description": "Molecular analysis and quantum chemistry",
            "examples": [
                {
                    "name": "Molecular Analysis",
                    "endpoint": "POST /api/chemistry/analyze-molecule",
                    "request": {"smiles": "CCO"},
                    "response": "Molecular weight, structure, properties"
                },
                {
                    "name": "DNA Analysis",
                    "endpoint": "POST /api/chemistry/analyze-sequence",
                    "request": {"sequence": "ATCGATCG", "sequence_type": "dna"},
                    "response": "GC content, molecular weight, properties"
                }
            ],
            "tips": [
                "Use SMILES notation for molecules (e.g., 'CCO' for ethanol)",
                "Supported sequence types: dna, rna, protein",
                "Get library info at /api/chemistry/info",
                "Quantum chemistry requires atomic coordinates"
            ]
        },
        "quantum": {
            "description": "Quantum physics and computing simulations",
            "examples": [
                {
                    "name": "Spin Evolution",
                    "endpoint": "POST /api/quantum-physics/spin-evolution",
                    "request": {"magnetic_field": {"Bx": 1.0, "By": 0, "Bz": 1.0}},
                    "response": "Time evolution of quantum spin"
                },
                {
                    "name": "Bell State",
                    "endpoint": "POST /api/quantum-computing/bell-state",
                    "request": {},
                    "response": "Quantum entangled state"
                }
            ],
            "tips": [
                "Quantum physics uses QuTiP library",
                "Quantum computing uses Qiskit/Cirq",
                "Check /info endpoints for library availability",
                "Parameters are in atomic units"
            ]
        }
    }

    if category not in help_data:
        raise HTTPException(status_code=404, detail=f"Help not found for category: {category}")

    return BaseResponse(
        success=True,
        message=f"Detailed help for {category}",
        data=help_data[category]
    )

@router.get("/examples", response_model=BaseResponse)
async def get_all_examples():
    """
    Get examples for all categories
    """
    return BaseResponse(
        success=True,
        message="Examples for all mathematical functions",
        data={
            "arithmetic": [
                {"operation": "add", "operands": [5, 3, 2], "description": "Sum three numbers"},
                {"operation": "power", "operands": [2, 8], "description": "2 to the power of 8"},
                {"operation": "sin", "operands": [45], "description": "Sine of 45 degrees"}
            ],
            "calculus": [
                {"expression": "x^3", "operation": "derivative", "description": "Derivative of x³"},
                {"expression": "x^2", "operation": "integral", "description": "Indefinite integral of x²"},
                {"expression": "1/x", "operation": "limit", "variable": "x", "limit_point": "0", "description": "Limit of 1/x as x approaches 0"}
            ],
            "equations": [
                {"equation": "x^2 - 4 = 0", "description": "Solve quadratic equation"},
                {"equation": "2*x + 3 = 7", "description": "Solve linear equation"},
                {"equation": "sin(x) = 0", "description": "Solve trigonometric equation"}
            ],
            "chemistry": [
                {"smiles": "CCO", "description": "Analyze ethanol molecule"},
                {"smiles": "c1ccccc1", "description": "Analyze benzene molecule"},
                {"sequence": "ATCGATCG", "sequence_type": "dna", "description": "Analyze DNA sequence"}
            ],
            "quantum": [
                {"type": "spin_evolution", "description": "Quantum spin time evolution"},
                {"type": "bell_state", "description": "Generate Bell entangled state"},
                {"type": "harmonic_oscillator", "description": "Quantum harmonic oscillator"}
            ]
        }
    )

@router.get("/quick-start", response_model=BaseResponse)
async def get_quick_start():
    """
    Get quick start guide with simple examples
    """
    return BaseResponse(
        success=True,
        message="Quick start guide for Mathematics AI",
        data={
            "welcome": "Welcome to Mathematics AI! Start with these simple examples:",
            "steps": [
                {
                    "step": 1,
                    "description": "Try basic arithmetic",
                    "endpoint": "POST /api/arithmetic/calculate",
                    "body": {"operation": "add", "operands": [5, 3]},
                    "expected": "Result: 8"
                },
                {
                    "step": 2,
                    "description": "Solve a simple equation",
                    "endpoint": "POST /api/equations/solve",
                    "body": {"equation": "x + 5 = 10"},
                    "expected": "Solution: x = 5"
                },
                {
                    "step": 3,
                    "description": "Calculate a derivative",
                    "endpoint": "POST /api/calculus/calculate",
                    "body": {"expression": "x^2", "operation": "derivative"},
                    "expected": "Result: 2*x"
                },
                {
                    "step": 4,
                    "description": "Explore advanced features",
                    "suggestion": "Visit /api/chemistry/info or /api/quantum-physics/info"
                }
            ],
            "tips": [
                "All endpoints return JSON responses with success/message/data fields",
                "Use GET /api/examples for more examples",
                "Check /api/{category}/examples for category-specific examples",
                "Visit /api/docs for interactive API documentation"
            ]
        }
    )
