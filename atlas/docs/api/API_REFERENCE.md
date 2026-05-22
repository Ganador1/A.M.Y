# 📖 AXIOM - Complete API Reference

## 🌐 API Reference - Scientific Computing Platform

This documentation provides a complete reference for all available endpoints in AXIOM, including the new integrated services: Causal Discovery, Federated Learning, Synthetic Data, Multimodal Reasoning, and Quantum Algorithms.

---

## 📊 General API Information

### Base URL
```
http://localhost:8000/api     # Integrated AXIOM Services
http://localhost:8001/api/v1  # Development (v1) - Legacy
https://api.axiom.ai/api/v1   # Production (v1) - Legacy
```

**Migration Note:** New AXIOM services are available on port 8000. Port 8001 remains operational for compatibility but is deprecated.

### Authentication (v1)
- Scheme: Bearer JWT (HS256), scopes per endpoint.
- Header: `Authorization: Bearer <token>`
- Example Scopes:
  - Scheduler: `scheduler`, `scheduler:admin`
  - Sandbox: `sandbox`
  - MLflow Registry: `mlflow:read`, `mlflow:write`, `mlflow:admin`
  - Scientific Evaluation: `sci-eval`

### Schemas per Endpoint (v1)
- The complete OpenAPI file is available at `docs/openapi_v1.json` (generate with `python scripts/generate_openapi.py`).
- JSON schemas per endpoint are exported to `docs/schemas/` (execute `python scripts/generate_schemas_from_openapi.py`).
- Examples:
  - `docs/schemas/experiment-scheduler/POST_api_scheduler_jobs.request.json`
  - `docs/schemas/experiment-scheduler/GET_api_scheduler_jobs.response.json`

### Response Format
All responses follow the standard JSON format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Specific results
  },
  "timestamp": "2025-01-01T12:00:00Z",
  "request_id": "req_123456"
}
```

### Error Codes
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    // Additional error information
  }
}
```

### Rate Limiting
- **Limit**: 60 requests per minute per IP
- **Response Headers**:
  - `X-RateLimit-Limit`: Total limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

---

## 🔢 1. Arithmetic - `/api/arithmetic/`

### 1.1 Basic Calculation
**Endpoint**: `POST /api/arithmetic/calculate`

Performs basic arithmetic operations with real numbers.

**Parameters**:
```json
{
  "operation": "add|subtract|multiply|divide|power|sqrt|sin|cos|tan|log|ln|exp",
  "operands": [1.5, 2.3, 4.7],
  "precision": 6
}
```

**Successful Response**:
```json
{
  "success": true,
  "message": "Arithmetic operation completed",
  "data": {
    "operation": "add",
    "operands": [1.5, 2.3, 4.7],
    "result": 8.5,
    "steps": [
      "1.5 + 2.3 = 3.8",
      "3.8 + 4.7 = 8.5"
    ],
    "precision": 6
  }
}
```

**Usage Examples**:

```bash
# Addition
curl -X POST "http://localhost:8001/api/arithmetic/calculate" \
  -H "Content-Type: application/json" \
  -d '{"operation": "add", "operands": [10, 20, 30]}'

# Power
curl -X POST "http://localhost:8001/api/arithmetic/calculate" \
  -H "Content-Type: application/json" \
  -d '{"operation": "power", "operands": [2, 8]}'

# Trigonometric function
curl -X POST "http://localhost:8001/api/arithmetic/calculate" \
  -H "Content-Type: application/json" \
  -d '{"operation": "sin", "operands": [1.5708]}'
```

### 1.2 Batch Calculation
**Endpoint**: `POST /api/arithmetic/batch`

Executes multiple arithmetic operations in parallel.

**Parameters**:
```json
{
  "operations": [
    {
      "operation": "add",
      "operands": [1, 2, 3]
    },
    {
      "operation": "multiply",
      "operands": [4, 5, 6]
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Batch operations completed",
  "data": {
    "results": [
      {
        "operation": "add",
        "result": 6,
        "steps": ["1 + 2 = 3", "3 + 3 = 6"]
      },
      {
        "operation": "multiply",
        "result": 120,
        "steps": ["4 × 5 = 20", "20 × 6 = 120"]
      }
    ],
    "total_operations": 2,
    "execution_time": 0.023
  }
}
```

### 1.3 List Available Operations
**Endpoint**: `GET /api/arithmetic/operations`

**Response**:
```json
{
  "success": true,
  "data": {
    "operations": [
      "add", "subtract", "multiply", "divide",
      "power", "sqrt", "sin", "cos", "tan",
      "log", "ln", "exp", "abs", "factorial"
    ],
    "categories": {
      "basic": ["add", "subtract", "multiply", "divide"],
      "advanced": ["power", "sqrt", "factorial"],
      "trigonometric": ["sin", "cos", "tan"],
      "exponential": ["log", "ln", "exp"]
    }
  }
}
```

---

## 📈 2. Calculus - `/api/calculus/`

### 2.1 Derivatives
**Endpoint**: `POST /api/calculus/calculate`

Calculates derivatives with step-by-step solution.

**Parameters**:
```json
{
  "operation": "derivative",
  "expression": "x^3 + 2*x^2 + x + 1",
  "variable": "x",
  "order": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "Derivative calculated successfully",
  "data": {
    "original_expression": "x^3 + 2*x^2 + x + 1",
    "result": "3*x^2 + 4*x + 1",
    "operation": "Derivative of order 1",
    "variable": "x",
    "order": 1,
    "steps": [
      "Original expression: x^3 + 2*x^2 + x + 1",
      "Applying power rule: d/dx(x^n) = n*x^(n-1)",
      "d/dx(x^3) = 3*x^2",
      "d/dx(2*x^2) = 4*x",
      "d/dx(x) = 1",
      "d/dx(1) = 0",
      "Final result: 3*x^2 + 4*x + 1"
    ]
  }
}
```

### 2.2 Integrals
**Endpoint**: `POST /api/calculus/calculate`

Calculates definite and indefinite integrals.

**Parameters**:
```json
{
  "operation": "integral",
  "expression": "x^2 + 3*x + 1",
  "variable": "x",
  "definite": true,
  "lower_limit": 0,
  "upper_limit": 1
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "original_expression": "x^2 + 3*x + 1",
    "result": "0.3333333333333333",
    "operation": "Definite integral",
    "variable": "x",
    "limits": [0, 1],
    "steps": [
      "∫(x^2 + 3*x + 1)dx from 0 to 1",
      "∫x^2 dx = (1/3)x^3",
      "∫3*x dx = (3/2)x^2",
      "∫1 dx = x",
      "Combined: (1/3)x^3 + (3/2)x^2 + x",
      "Evaluating from 0 to 1: 1/3 + 3/2 + 1 - 0 = 11/6 ≈ 1.8333",
      "Final result: 11/6"
    ]
  }
}
```

### 2.3 Limits
**Endpoint**: `POST /api/calculus/limit`

Calculates limits of functions.

**Parameters**:
```json
{
  "expression": "(x^2 - 1)/(x - 1)",
  "variable": "x",
  "point": 1,
  "direction": "both"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "expression": "(x^2 - 1)/(x - 1)",
    "result": 2,
    "variable": "x",
    "point": 1,
    "direction": "both",
    "steps": [
      "Limit of (x^2 - 1)/(x - 1) as x approaches 1",
      "Factor numerator: (x - 1)(x + 1)/(x - 1)",
      "Cancel common factor: x + 1",
      "Limit: 1 + 1 = 2"
    ]
  }
}
```

### 2.4 Partial Derivatives
**Endpoint**: `POST /api/calculus/partial-derivative`

**Parameters**:
```json
{
  "expression": "x^2*y + sin(z)",
  "variables": ["x", "y", "z"],
  "orders": [1, 1, 0]
}
```

---

## 🧮 3. Linear Algebra - `/api/advanced-algebra/`

### 3.1 Matrix Operations
**Endpoint**: `POST /api/advanced-algebra/matrix/add`

**Parameters**:
```json
{
  "matrix_a": [[1, 2], [3, 4]],
  "matrix_b": [[5, 6], [7, 8]]
}
```

### 3.2 Determinants
**Endpoint**: `POST /api/advanced-algebra/matrix/determinant`

**Parameters**:
```json
{
  "matrix": [[3, 2, 1], [1, 4, 2], [2, 1, 3]]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "matrix": [[3, 2, 1], [1, 4, 2], [2, 1, 3]],
    "determinant": 25,
    "steps": [
      "Matrix 3x3 determinant calculation",
      "det = 3*(4*3 - 2*2) - 2*(1*3 - 2*1) + 1*(1*2 - 4*1)",
      "det = 3*(12 - 4) - 2*(3 - 2) + 1*(2 - 4)",
      "det = 3*8 - 2*1 + 1*(-2)",
      "det = 24 - 2 - 2 = 20"
    ]
  }
}
```

### 3.3 Eigenvalues and Eigenvectors
**Endpoint**: `POST /api/advanced-algebra/matrix/eigenvalues`

**Parameters**:
```json
{
  "matrix": [[4, -2], [1, 1]]
}
```

### 3.4 Matrix Inverse
**Endpoint**: `POST /api/advanced-algebra/matrix/inverse`

---

## 📊 4. Statistics - `/api/statistics/`

### 4.1 Descriptive Statistics
**Endpoint**: `POST /api/statistics/calculate`

**Parameters**:
```json
{
  "operation": "descriptive",
  "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "count": 10,
    "mean": 5.5,
    "median": 5.5,
    "mode": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "std_dev": 3.0276503540974917,
    "variance": 9.166666666666666,
    "min": 1,
    "max": 10,
    "range": 9,
    "quartiles": [3.25, 5.5, 7.75],
    "iqr": 4.5,
    "skewness": 0.0,
    "kurtosis": -1.2242424242424244
  }
}
```

### 4.2 Linear Regression
**Endpoint**: `POST /api/statistics/linear-regression`

**Parameters**:
```json
{
  "x_data": [1, 2, 3, 4, 5],
  "y_data": [2, 4, 6, 8, 10]
}
```

### 4.3 Correlation
**Endpoint**: `POST /api/statistics/correlation`

**Parameters**:
```json
{
  "x_data": [1, 2, 3, 4, 5],
  "y_data": [2, 4, 6, 8, 10],
  "method": "pearson"
}
```

### 4.4 Hypothesis Testing
**Endpoint**: `POST /api/statistics/hypothesis`

---

## 🎨 5. Graphing - `/api/graphing/`

### 5.1 2D Plots
**Endpoint**: `POST /api/graphing/generate`

**Parameters**:
```json
{
  "expression": "sin(x)",
  "x_range": [-10, 10],
  "title": "Sine Function",
  "color": "blue",
  "line_style": "solid"
}
```

### 5.2 3D Plots
**Endpoint**: `POST /api/graphing/3d`

**Parameters**:
```json
{
  "expression": "x**2 + y**2",
  "x_range": [-5, 5],
  "y_range": [-5, 5],
  "colorscale": "Viridis",
  "opacity": 0.8
}
```

### 5.3 Parametric Plots
**Endpoint**: `POST /api/graphing/2d-parametric`

**Parameters**:
```json
{
  "x_expr": "cos(t)",
  "y_expr": "sin(t)",
  "t_range": [0, 6.28],
  "title": "Unit Circle"
}
```

### 5.4 Multi-Surface 3D
**Endpoint**: `POST /api/graphing/multi-surface-3d`

---

## 🎯 6. Equation Solving - `/api/equations/`

### 6.1 Simple Equation
**Endpoint**: `POST /api/equations/solve`

**Parameters**:
```json
{
  "equation": "x^2 - 4 = 0",
  "variable": "x"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "equation": "x^2 - 4 = 0",
    "variable": "x",
    "solutions": [-2, 2],
    "solution_type": "quadratic",
    "steps": [
      "x^2 - 4 = 0",
      "x^2 = 4",
      "x = ±√4",
      "x = ±2"
    ]
  }
}
```

### 6.2 System of Equations
**Endpoint**: `POST /api/equations/system`

**Parameters**:
```json
{
  "equations": [
    "2*x + 3*y = 7",
    "x - y = 1"
  ],
  "variables": ["x", "y"]
}
```

### 6.3 Batch Equations
**Endpoint**: `POST /api/equations/batch`

---

## 🔢 7. Number Theory - `/api/number-theory/`

### 7.1 Primality
**Endpoint**: `POST /api/number-theory/prime-check`

**Parameters**:
```json
{
  "number": 17
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "number": 17,
    "is_prime": true,
    "factors": [17],
    "prime_factors": [17],
    "test_method": "Miller-Rabin primality test"
  }
}
```

### 7.2 Factorization
**Endpoint**: `POST /api/number-theory/factorization`

**Parameters**:
```json
{
  "number": 12345
}
```

### 7.3 Greatest Common Divisor
**Endpoint**: `POST /api/number-theory/gcd`

**Parameters**:
```json
{
  "numbers": [48, 18]
}
```

### 7.4 Euler's Totient Function
**Endpoint**: `POST /api/number-theory/euler-totient`

### 7.5 Modular Inverse
**Endpoint**: `POST /api/number-theory/modular-inverse`

### 7.6 Modular Exponentiation
**Endpoint**: `POST /api/number-theory/modular-exponentiation`

### 7.7 Legendre and Jacobi Symbols
**Endpoint**: `POST /api/number-theory/legendre-symbol`

### 7.8 Discrete Logarithm
**Endpoint**: `POST /api/number-theory/discrete-logarithm`

### 7.9 Chinese Remainder Theorem
**Endpoint**: `POST /api/number-theory/chinese-remainder`

---

## 🎯 8. Optimization - `/api/optimization/`

### 8.1 Linear Programming
**Endpoint**: `POST /api/optimization/linear-programming`

**Parameters**:
```json
{
  "c": [-1, -2],  // Objective function coefficients
  "A_ub": [[1, 1], [2, 1]],  // Inequality constraint matrix
  "b_ub": [4, 6],  // Inequality right-hand side
  "bounds": [[0, null], [0, null]]  // Variable bounds
}
```

### 8.2 Nonlinear Optimization
**Endpoint**: `POST /api/optimization/nonlinear-optimization`

### 8.3 Convex Optimization
**Endpoint**: `POST /api/optimization/convex-optimization`

### 8.4 Quadratic Programming
**Endpoint**: `POST /api/optimization/quadratic-programming`

---

## 🧬 9. Computational Chemistry - `/api/computational-chemistry/`

### 9.1 Molecular Analysis
**Endpoint**: `POST /api/computational-chemistry/analyze-molecule`

**Parameters**:
```json
{
  "smiles": "CCO",
  "properties": ["molecular_weight", "logp", "tpsa"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "smiles": "CCO",
    "formula": "C2H6O",
    "descriptors": {
      "molecular_weight": 46.068,
      "logp": -0.0014,
      "tpsa": 20.23,
      "hbd": 1,
      "hba": 1,
      "rotatable_bonds": 1,
      "heavy_atoms": 3
    }
  }
}
```

### 9.2 Conformer Generation
**Endpoint**: `POST /api/computational-chemistry/generate-conformers`

### 9.3 Sequence Analysis
**Endpoint**: `POST /api/computational-chemistry/analyze-sequence`

### 9.4 Quantum Chemistry Calculations
**Endpoint**: `POST /api/computational-chemistry/quantum-chemistry`

---

## ⚛️ 10. Quantum Physics - `/api/quantum-physics/`

### 10.1 Spin Evolution
**Endpoint**: `POST /api/quantum-physics/spin-evolution`

**Parameters**:
```json
{
  "Bx": 1.0,
  "By": 0.0,
  "Bz": 1.0,
  "t_max": 10.0,
  "n_points": 100
}
```

### 10.2 Quantum Harmonic Oscillator
**Endpoint**: `POST /api/quantum-physics/harmonic-oscillator`

### 10.3 Entanglement Analysis
**Endpoint**: `POST /api/quantum-physics/entanglement`

---

## 🧠 11. Quantum Computing - `/api/quantum-computing/`

### 11.1 Bell States
**Endpoint**: `POST /api/quantum-computing/bell-state`

**Parameters**:
```json
{
  "framework": "qiskit"
}
```

### 11.2 Grover's Search
**Endpoint**: `POST /api/quantum-computing/grover-search`

### 11.3 Quantum Fourier Transform
**Endpoint**: `POST /api/quantum-computing/quantum-fourier-transform`

### 11.4 VQE (Variational Quantum Eigensolver)
**Endpoint**: `POST /api/quantum-computing/variational-quantum-eigensolver`

---

## 🤖 12. Scientific AI - `/api/scientific-ai/`

### 12.1 PINN for PDE
**Endpoint**: `POST /api/scientific-ai/solve-pde-pinn`

### 12.2 Inverse Problems
**Endpoint**: `POST /api/scientific-ai/inverse-problem-pinn`

### 12.3 Agent Creation
**Endpoint**: `POST /api/scientific-ai/create-agent`

---

## 🧪 13. Partial Differential Equations - `/api/pde/`

### 13.1 Heat Equation
**Endpoint**: `POST /api/pde/heat-equation`

### 13.2 Wave Equation
**Endpoint**: `POST /api/pde/wave-equation`

### 13.3 Laplace Equation
**Endpoint**: `POST /api/pde/laplace-equation`

### 13.4 Poisson Equation
**Endpoint**: `POST /api/pde/poisson-equation`

---

## 🔄 14. Transforms - `/api/transform/`

### 14.1 Fourier Transform
**Endpoint**: `POST /api/transform/fourier`

### 14.2 Laplace Transform
**Endpoint**: `POST /api/transform/laplace`

### 14.3 Z-Transform
**Endpoint**: `POST /api/transform/z-transform`

---

## 📐 15. Variational Calculus - `/api/variational-calculus/`

### 15.1 Euler-Lagrange Equation
**Endpoint**: `POST /api/variational-calculus/euler-lagrange`

### 15.2 Brachistochrone Problem
**Endpoint**: `POST /api/variational-calculus/brachistochrone`

---

## 🔬 16. Complex Analysis - `/api/complex-analysis/`

### 16.1 Power Series
**Endpoint**: `POST /api/complex-analysis/power-series`

### 16.2 Residues and Poles
**Endpoint**: `POST /api/complex-analysis/residues`

### 16.3 Complex Integration
**Endpoint**: `POST /api/complex-analysis/contour-integral`

---

## 📊 17. Monitoring Endpoints - `/`

### 17.1 Health Checks
**Endpoint**: `GET /health`

**Response**:
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "version": "1.1.0",
  "uptime": "2h 30m"
}
```

### 17.2 Detailed Health
**Endpoint**: `GET /health/detailed`

### 17.3 Metrics
**Endpoint**: `GET /metrics`

### 17.4 Cache Statistics
**Endpoint**: `GET /cache/stats`

### 17.5 Redis Status
**Endpoint**: `GET /redis/status`

---

## 🧬 18. DNABERT-2 Genomics - `/api/scientific/dnabert2/`

### 18.1 Sequence Encoding
**Endpoint**: `POST /api/scientific/dnabert2/encode-sequence`
Tokenizes a DNA sequence into k-mers.

### 18.2 Motif Prediction
**Endpoint**: `POST /api/scientific/dnabert2/predict-motifs`
Identifies functional motifs (TATA-box, CpG islands).

### 18.3 Promoter Classification
**Endpoint**: `POST /api/scientific/dnabert2/classify-promoter`
Classifies if a sequence is a promoter.

---

## 🧪 19. GNOME Materials Discovery - `/api/scientific/gnome-materials/`

### 19.1 Candidate Suggestion
**Endpoint**: `POST /api/scientific/gnome-materials/suggest-candidates`
Recommends materials for a specific application.

### 19.2 Property Prediction
**Endpoint**: `POST /api/scientific/gnome-materials/predict-properties`
Estimates properties for a chemical formula.

---

## 🤖 20. MLflow Model Registry - `/api/infrastructure/mlflow-registry/`

### 20.1 Model Registration
**Endpoint**: `POST /api/infrastructure/mlflow-registry/register`
Registers a new model in the registry.

### 20.2 List Models
**Endpoint**: `GET /api/infrastructure/mlflow-registry/models`
Lists all registered models.

### 20.3 Stage Transition
**Endpoint**: `POST /api/infrastructure/mlflow-registry/models/transition-stage`
Promotes a model between stages (Staging, Production, etc.).

---

## 🔄 21. Scientific Reproducibility - `/api/infrastructure/reproducibility/`

### 21.1 Export Package
**Endpoint**: `POST /api/infrastructure/reproducibility/export-package`
Generates a reproducible ZIP package with code, data, and environment.

### 21.2 Package Cleanup
**Endpoint**: `POST /api/infrastructure/reproducibility/cleanup`
Removes old packages to free up space.

---

## 🧠 22. Causal Discovery - `/api/scientific/causal-discovery/`

### 22.1 Structure Discovery
**Endpoint**: `POST /api/scientific/causal-discovery/discover`
Identifies the causal graph from observational data.

### 22.2 Effect Estimation
**Endpoint**: `POST /api/scientific/causal-discovery/estimate-effect`
Calculates the causal impact of one variable on another.

---

## 🌐 23. Federated Learning - `/api/scientific/federated-learning/`

### 23.1 Start Server
**Endpoint**: `POST /api/scientific/federated-learning/start-server`
Starts a federated training round.

### 23.2 Training Status
**Endpoint**: `GET /api/scientific/federated-learning/status`
Gets the progress of training rounds.

---

## 📊 24. Synthetic Data - `/api/scientific/synthetic-data/`

### 24.1 Generate Data
**Endpoint**: `POST /api/scientific/synthetic-data/generate`
Creates a synthetic dataset based on a real sample.

### 24.2 Evaluate Quality
**Endpoint**: `POST /api/scientific/synthetic-data/evaluate`
Compares statistical fidelity between real and synthetic data.

---

## 👁️ 25. Multimodal Reasoning - `/api/scientific/multimodal-reasoning/`

### 25.1 Image Analysis
**Endpoint**: `POST /api/scientific/multimodal-reasoning/analyze-image`
Analyzes scientific images using advanced vision models.

### 25.2 Complex Reasoning
**Endpoint**: `POST /api/scientific/multimodal-reasoning/reason`
Combines multiple sources (images, text) for scientific synthesis.

---

## ⚛️ 26. Quantum Algorithms - `/api/scientific/quantum-algorithms/`

### 26.1 QAOA Optimization
**Endpoint**: `POST /api/scientific/quantum-algorithms/qaoa`
Solves combinatorial optimization problems.

### 26.2 VQE Chemistry
**Endpoint**: `POST /api/scientific/quantum-algorithms/vqe`
Calculates ground state energies for molecules.

---

## 👯 27. Digital Twins - `/api/scientific/digital-twins/`

### 27.1 Create Twin
**Endpoint**: `POST /api/scientific/digital-twins/create`
Initializes a digital replica of an experiment or equipment.

### 27.2 Simulate Scenario
**Endpoint**: `POST /api/scientific/digital-twins/{twin_id}/simulate`
Runs a predictive simulation on the digital twin.

---

## 🧪 28. Lab Automation - `/api/scientific/lab-automation/`

### 28.1 PCR Protocol
**Endpoint**: `POST /api/scientific/lab-automation/pcr`
Executes an automated thermal cycling protocol.

### 28.2 ELISA Assay
**Endpoint**: `POST /api/scientific/lab-automation/elisa`
Orchestrates a complete ELISA assay with absorbance reading.

---

## 🚨 Common Error Codes

### Validation Errors (400)
```json
{
  "success": false,
  "error": "Invalid mathematical expression",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "expression",
    "value": "invalid_expr",
    "reason": "Expression contains invalid characters"
  }
}
```

### Calculation Errors (422)
```json
{
  "success": false,
  "error": "Mathematical calculation failed",
  "error_code": "CALCULATION_ERROR",
  "details": {
    "operation": "derivative",
    "expression": "x^2",
    "reason": "Division by zero encountered"
  }
}
```

### Server Errors (500)
```json
{
  "success": false,
  "error": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "details": {
    "traceback": "...",
    "request_id": "req_123456"
  }
}
```

### Rate Limiting Errors (429)
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "limit": 60,
    "remaining": 0,
    "reset_time": "2025-01-01T12:01:00Z"
  }
}
```

---

## 📝 Usage Notes

### 1. Input Limits
- **Mathematical expressions**: Maximum 1000 characters
- **Matrices**: Maximum 100×100 elements
- **Statistical data**: Maximum 10,000 points
- **Plots**: Maximum 10,000 render points

### 2. Supported Formats
- **Expressions**: SymPy syntax (x^2, sin(x), exp(x), etc.)
- **Matrices**: Arrays of arrays of numbers
- **Data**: Arrays of numbers or arrays of points [x, y]
- **SMILES**: Standard chemical notation for molecules

### 3. Numerical Precision
- **Decimals**: 6 digits by default
- **Tolerance**: 1e-10 for comparisons
- **Iterations**: Maximum 1000 for iterative methods

### 4. Caching
- Results are cached automatically
- Configurable TTL per endpoint
- Manual invalidation available

### 5. Concurrency
- Multiple requests processed in parallel
- Resource limits per user
- Queue system for heavy operations

---

*This documentation is kept up to date with the latest AXIOM functionalities. For specific examples or advanced use cases, consult the interactive documentation at `/docs`.*
