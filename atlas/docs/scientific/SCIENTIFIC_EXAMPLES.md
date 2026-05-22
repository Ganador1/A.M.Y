# 🔬 Scientific Examples with AXIOM

## Practical Examples of AXIOM Usage in Scientific Research

This collection of examples demonstrates how AXIOM can be used in various scientific fields, from computational chemistry to quantum physics.

---

## 🧬 1. Computational Chemistry

### 1.1 Molecular Property Analysis

```bash
# Analysis of properties for a caffeine molecule
curl -X POST "http://localhost:8001/api/computational-chemistry/analyze-molecule" \
  -H "Content-Type: application/json" \
  -d '{
    "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    "properties": ["molecular_weight", "logp", "tpsa", "hbd", "hba"]
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    "formula": "C8H10N4O2",
    "descriptors": {
      "molecular_weight": 194.19,
      "logp": -0.07,
      "tpsa": 61.82,
      "hbd": 0,
      "hba": 6
    }
  }
}
```

### 1.2 Conformer Generation

```bash
# Generate conformers for ethanol
curl -X POST "http://localhost:8001/api/computational-chemistry/generate-conformers" \
  -H "Content-Type: application/json" \
  -d '{
    "smiles": "CCO",
    "num_conformers": 10,
    "optimization_method": "MMFF94"
  }'
```

### 1.3 DNA Sequence Analysis

```bash
# Analysis of a DNA sequence
curl -X POST "http://localhost:8001/api/computational-chemistry/analyze-sequence" \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": "ATCGATCGATCG",
    "sequence_type": "dna",
    "analysis_type": "composition"
  }'
```

---

## ⚛️ 2. Quantum Physics

### 2.1 Spin Evolution in a Magnetic Field

```bash
# Simulate spin evolution in a magnetic field
curl -X POST "http://localhost:8001/api/quantum-physics/spin-evolution" \
  -H "Content-Type: application/json" \
  -d '{
    "Bx": 1.0,
    "By": 0.5,
    "Bz": 2.0,
    "t_max": 5.0,
    "n_points": 100,
    "initial_state": [1, 0]
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "evolution_data": {
      "time": [0.0, 0.05, 0.1, ...],
      "x_magnetization": [1.0, 0.95, 0.89, ...],
      "y_magnetization": [0.0, 0.05, 0.11, ...],
      "z_magnetization": [0.0, -0.02, -0.04, ...]
    },
    "parameters": {
      "Bx": 1.0,
      "By": 0.5,
      "Bz": 2.0
    }
  }
}
```

### 2.2 Quantum Harmonic Oscillator

```bash
# Calculate energy levels of the quantum harmonic oscillator
curl -X POST "http://localhost:8001/api/quantum-physics/harmonic-oscillator" \
  -H "Content-Type: application/json" \
  -d '{
    "mass": 1.0,
    "omega": 1.0,
    "n_levels": 5,
    "calculate_wavefunctions": true
  }'
```

### 2.3 Entanglement Analysis

```bash
# Analyze two-qubit entangled state
curl -X POST "http://localhost:8001/api/quantum-physics/entanglement" \
  -H "Content-Type: application/json" \
  -d '{
    "state_vector": [0.707, 0, 0, 0.707],
    "analysis_type": "concurrence"
  }'
```

---

## 🧠 3. Quantum Computing

### 3.1 Bell State Generation

```bash
# Create |Φ+⟩ Bell state
curl -X POST "http://localhost:8001/api/quantum-computing/bell-state" \
  -H "Content-Type: application/json" \
  -d '{
    "bell_type": "phi_plus",
    "framework": "qiskit",
    "simulate": true,
    "shots": 1024
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "bell_state": "phi_plus",
    "circuit": {
      "gates": ["H", "CNOT"],
      "qubits": 2
    },
    "simulation_results": {
      "00": 512,
      "11": 512
    },
    "fidelity": 1.0
  }
}
```

### 3.2 Grover's Search Algorithm

```bash
# Implement Grover's search for 4 elements
curl -X POST "http://localhost:8001/api/quantum-computing/grover-search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_space_size": 4,
    "target_index": 2,
    "framework": "qiskit",
    "simulate": true
  }'
```

### 3.3 Quantum Fourier Transform

```bash
# Apply QFT to a 3-qubit state
curl -X POST "http://localhost:8001/api/quantum-computing/quantum-fourier-transform" \
  -H "Content-Type: application/json" \
  -d '{
    "n_qubits": 3,
    "input_state": [1, 0, 0, 0, 0, 0, 0, 0],
    "inverse": false
  }'
```

---

## 🤖 4. Scientific AI with PINN

### 4.1 Solving Heat Equation with PINN

```bash
# Solve ∂u/∂t = α∇²u with boundary conditions
curl -X POST "http://localhost:8001/api/scientific-ai/solve-pde-pinn" \
  -H "Content-Type: application/json" \
  -d '{
    "pde_type": "heat_equation",
    "domain": {
      "x_range": [0, 1],
      "t_range": [0, 1]
    },
    "boundary_conditions": [
      {"type": "dirichlet", "value": 0, "boundary": "x=0"},
      {"type": "dirichlet", "value": 0, "boundary": "x=1"},
      {"type": "initial", "value": "sin(π*x)", "boundary": "t=0"}
    ],
    "parameters": {"alpha": 0.01},
    "training": {
      "epochs": 1000,
      "learning_rate": 0.001,
      "n_points": 1000
    }
  }'
```

### 4.2 Inverse Problem: Parameter Estimation

```bash
# Estimate thermal conductivity from observed data
curl -X POST "http://localhost:8001/api/scientific-ai/inverse-problem-pinn" \
  -H "Content-Type: application/json" \
  -d '{
    "pde_type": "heat_equation",
    "observed_data": {
      "positions": [[0.1, 0.5], [0.2, 0.5], [0.3, 0.5]],
      "temperatures": [0.8, 0.6, 0.4],
      "times": [0.1, 0.1, 0.1]
    },
    "parameter_to_estimate": "thermal_conductivity",
    "bounds": [0.001, 1.0]
  }'
```

### 4.3 Scientific Agent Creation

```bash
# Create an agent for scientific data analysis
curl -X POST "http://localhost:8001/api/scientific-ai/create-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "data_analyzer",
    "capabilities": ["statistical_analysis", "hypothesis_testing", "visualization"],
    "domain": "materials_science",
    "tools": ["regression", "clustering", "dimensionality_reduction"]
  }'
```

---

## 📊 5. Statistics and Data Analysis

### 5.1 Comprehensive Statistical Analysis

```bash
# Statistical analysis of a dataset
curl -X POST "http://localhost:8001/api/statistics/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "descriptive",
    "data": [12.5, 13.2, 11.8, 14.1, 12.9, 13.7, 12.3, 13.0, 12.8, 13.4],
    "include_distribution": true
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "count": 10,
    "mean": 12.97,
    "median": 13.0,
    "std_dev": 0.67,
    "variance": 0.45,
    "min": 11.8,
    "max": 14.1,
    "quartiles": [12.35, 13.0, 13.35],
    "distribution": {
      "normal_test": {"statistic": 0.23, "p_value": 0.89},
      "shapiro_test": {"statistic": 0.95, "p_value": 0.72}
    }
  }
}
```

### 5.2 Multiple Linear Regression

```bash
# Linear regression with multiple variables
curl -X POST "http://localhost:8001/api/statistics/linear-regression" \
  -H "Content-Type: application/json" \
  -d '{
    "x_data": [
      [1, 2, 3],
      [2, 3, 4],
      [3, 4, 5],
      [4, 5, 6],
      [5, 6, 7]
    ],
    "y_data": [5, 8, 11, 14, 17],
    "include_diagnostics": true
  }'
```

### 5.3 Hypothesis Testing

```bash
# Student's t-test for two samples
curl -X POST "http://localhost:8001/api/statistics/hypothesis" \
  -H "Content-Type: application/json" \
  -d '{
    "test_type": "t_test",
    "sample1": [12.1, 12.5, 12.3, 12.8, 12.2],
    "sample2": [13.1, 13.5, 13.3, 13.8, 13.2],
    "alternative": "two_sided",
    "alpha": 0.05
  }'
```

---

## 📈 6. Optimization

### 6.1 Linear Programming

```bash
# Maximize profit with constraints
curl -X POST "http://localhost:8001/api/optimization/linear-programming" \
  -H "Content-Type: application/json" \
  -d '{
    "objective": {
      "coefficients": [3, 2],
      "sense": "maximize"
    },
    "constraints": [
      {
        "coefficients": [1, 1],
        "sense": "<=",
        "rhs": 4
      },
      {
        "coefficients": [2, 1],
        "sense": "<=",
        "rhs": 5
      }
    ],
    "bounds": [[0, null], [0, null]]
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "optimal_value": 6.5,
    "optimal_solution": [1.5, 2.5],
    "status": "optimal",
    "slack_variables": [0.0, 0.0]
  }
}
```

### 6.2 Non-linear Optimization

```bash
# Minimize non-linear function
curl -X POST "http://localhost:8001/api/optimization/nonlinear-optimization" \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "x**2 + y**2",
    "constraints": [
      {"type": "inequality", "expression": "x + y - 1", "sense": "<="},
      {"type": "equality", "expression": "x - y"}
    ],
    "bounds": [[-2, 2], [-2, 2]],
    "method": "SLSQP"
  }'
```

---

## 🧮 7. Advanced Linear Algebra

### 7.1 Principal Component Analysis

```bash
# PCA on a multidimensional dataset
curl -X POST "http://localhost:8001/api/advanced-algebra/pca" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      [1, 2, 3, 4],
      [2, 3, 4, 5],
      [3, 4, 5, 6],
      [4, 5, 6, 7]
    ],
    "n_components": 2,
    "standardize": true
  }'
```

### 7.2 Singular Value Decomposition

```bash
# SVD of a matrix
curl -X POST "http://localhost:8001/api/advanced-algebra/svd" \
  -H "Content-Type: application/json" \
  -d '{
    "matrix": [
      [1, 2, 3],
      [4, 5, 6],
      [7, 8, 9]
    ],
    "full_matrices": false
  }'
```

### 7.3 Eigenvalues and Eigenvectors

```bash
# Calculate eigenvalues and eigenvectors
curl -X POST "http://localhost:8001/api/advanced-algebra/matrix/eigenvalues" \
  -H "Content-Type: application/json" \
  -d '{
    "matrix": [
      [4, -2],
      [1, 1]
    ],
    "eigenvectors": true
  }'
```

---

## 📐 8. Partial Differential Equations

### 8.1 2D Heat Equation

```bash
# Solve 2D heat equation
curl -X POST "http://localhost:8001/api/pde/heat-equation" \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": 2,
    "domain": {
      "x_range": [0, 1],
      "y_range": [0, 1],
      "t_range": [0, 0.1]
    },
    "initial_condition": "sin(π*x)*sin(π*y)",
    "boundary_conditions": {
      "left": 0,
      "right": 0,
      "bottom": 0,
      "top": 0
    },
    "thermal_diffusivity": 0.01,
    "method": "finite_difference",
    "grid_points": [50, 50, 100]
  }'
```

### 8.2 Wave Equation

```bash
# Simulate wave propagation
curl -X POST "http://localhost:8001/api/pde/wave-equation" \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": 1,
    "domain": {
      "x_range": [0, 1],
      "t_range": [0, 2]
    },
    "initial_displacement": "sin(π*x)",
    "initial_velocity": "0",
    "wave_speed": 1.0,
    "boundary_conditions": "fixed_ends"
  }'
```

### 8.3 Laplace Equation

```bash
# Solve electrostatic potential problem
curl -X POST "http://localhost:8001/api/pde/laplace-equation" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": {
      "x_range": [0, 1],
      "y_range": [0, 1]
    },
    "boundary_conditions": {
      "left": "sin(π*y)",
      "right": 0,
      "bottom": 0,
      "top": 0
    },
    "method": "finite_difference",
    "tolerance": 1e-6
  }'
```

---

## 🔬 9. Complex Analysis

### 9.1 Contour Integrals

```bash
# Calculate contour integral
curl -X POST "http://localhost:8001/api/complex-analysis/contour-integral" \
  -H "Content-Type: application/json" \
  -d '{
    "integrand": "1/(z^2 + 1)",
    "contour": "unit_circle",
    "method": "residue_theorem"
  }'
```

### 9.2 Power Series

```bash
# Expand function in power series
curl -X POST "http://localhost:8001/api/complex-analysis/power-series" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "exp(z)",
    "center": 0,
    "order": 10
  }'
```

### 9.3 Residues and Poles

```bash
# Calculate residues of a rational function
curl -X POST "http://localhost:8001/api/complex-analysis/residues" \
  -H "Content-Type: application/json" \
  -d '{
    "numerator": "1",
    "denominator": "(z-1)*(z-2)*(z+1)",
    "poles": [1, 2, -1]
  }'
```

---

## 🔢 10. Number Theory

### 10.1 Large Number Factorization

```bash
# Factorize a large composite number
curl -X POST "http://localhost:8001/api/number-theory/factorization" \
  -H "Content-Type: application/json" \
  -d '{
    "number": 123456789,
    "method": "pollard_rho"
  }'
```

### 10.2 Primality Testing

```bash
# Check if a number is prime
curl -X POST "http://localhost:8001/api/number-theory/prime-check" \
  -H "Content-Type: application/json" \
  -d '{
    "number": 982451653,
    "method": "miller_rabin",
    "confidence": 0.999999
  }'
```

### 10.3 RSA Cryptography

```bash
# Generate RSA keys
curl -X POST "http://localhost:8001/api/cryptography/generate-rsa-keys" \
  -H "Content-Type: application/json" \
  -d '{
    "key_size": 2048
  }'

# Encrypt message
curl -X POST "http://localhost:8001/api/cryptography/rsa-encrypt" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, World!",
    "public_key": "..."
  }'

# Decrypt message
curl -X POST "http://localhost:8001/api/cryptography/rsa-decrypt" \
  -H "Content-Type: application/json" \
  -d '{
    "encrypted_message": "...",
    "private_key": "..."
  }'
```

---

## 🎨 11. Scientific Visualization

### 11.1 3D Function Plot

```bash
# Generate 3D plot of a mathematical function
curl -X POST "http://localhost:8001/api/graphing/3d" \
  -H "Content-Type: application/json" \
  -d '{
    "expression": "sin(sqrt(x**2 + y**2))",
    "x_range": [-5, 5],
    "y_range": [-5, 5],
    "grid_density": 50,
    "colorscale": "Viridis",
    "title": "Circular Wave"
  }'
```

### 11.2 Contour Plot

```bash
# Create contour plot
curl -X POST "http://localhost:8001/api/graphing/contour" \
  -H "Content-Type: application/json" \
  -d '{
    "expression": "x**2 - y**2",
    "x_range": [-2, 2],
    "y_range": [-2, 2],
    "levels": 20,
    "colorscale": "RdBu"
  }'
```

### 11.3 Statistical Data Visualization

```bash
# Create histogram with normal distribution fit
curl -X POST "http://localhost:8001/api/graphing/histogram" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [1.2, 1.8, 2.1, 2.3, 2.5, 2.7, 2.9, 3.1, 3.3, 3.8],
    "bins": 10,
    "title": "Data Distribution",
    "show_normal_fit": true
  }'
```

---

## 🔄 12. Transforms

### 12.1 Fourier Transform

```bash
# Calculate signal FFT
curl -X POST "http://localhost:8001/api/transform/fourier" \
  -H "Content-Type: application/json" \
  -d '{
    "signal": [1, 0.5, 0, -0.5, -1, -0.5, 0, 0.5],
    "sampling_rate": 1000,
    "transform_type": "fft"
  }'
```

### 12.2 Laplace Transform

```bash
# Calculate Laplace transform
curl -X POST "http://localhost:8001/api/transform/laplace" \
  -H "Content-Type: application/json" \
  -d '{
    "expression": "t*exp(-a*t)",
    "variable": "t",
    "transform_variable": "s",
    "region_of_convergence": "Re(s) > a"
  }'
```

---

## 📝 Python Example Scripts

### Example 1: Full Molecular Analysis

```python
import requests
import json

def analyze_molecule(smiles):
    """Complete molecular property analysis"""
    url = "http://localhost:8001/api/computational-chemistry/analyze-molecule"
    
    payload = {
        "smiles": smiles,
        "properties": [
            "molecular_weight", "logp", "tpsa", 
            "hbd", "hba", "rotatable_bonds"
        ]
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Example with aspirin
result = analyze_molecule("CC(=O)OC1=CC=CC=C1C(=O)O")
print(json.dumps(result, indent=2))
```

### Example 2: Quantum Simulation

```python
import requests
import matplotlib.pyplot as plt

def simulate_spin_evolution(Bx, By, Bz, t_max):
    """Simulate spin evolution in a magnetic field"""
    url = "http://localhost:8001/api/quantum-physics/spin-evolution"
    
    payload = {
        "Bx": Bx,
        "By": By, 
        "Bz": Bz,
        "t_max": t_max,
        "n_points": 200
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    if data["success"]:
        evolution = data["data"]["evolution_data"]
        
        # Plot results
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 3, 1)
        plt.plot(evolution["time"], evolution["x_magnetization"])
        plt.title("X Magnetization")
        plt.xlabel("Time")
        plt.ylabel("M_x")
        
        plt.subplot(1, 3, 2)
        plt.plot(evolution["time"], evolution["y_magnetization"])
        plt.title("Y Magnetization")
        plt.xlabel("Time")
        plt.ylabel("M_y")
        
        plt.subplot(1, 3, 3)
        plt.plot(evolution["time"], evolution["z_magnetization"])
        plt.title("Z Magnetization")
        plt.xlabel("Time")
        plt.ylabel("M_z")
        
        plt.tight_layout()
        plt.show()
    
    return data

# Simulate spin in magnetic field
result = simulate_spin_evolution(1.0, 0.5, 2.0, 10.0)
```

### Example 3: Constrained Optimization

```python
import requests
import numpy as np

def optimize_production():
    """Optimize production with resource constraints"""
    url = "http://localhost:8001/api/optimization/linear-programming"
    
    # Maximize: 3*x + 2*y (profit)
    # Constraints:
    # x + y <= 4 (labor)
    # 2*x + y <= 5 (raw material)
    # x, y >= 0
    
    payload = {
        "objective": {
            "coefficients": [3, 2],
            "sense": "maximize"
        },
        "constraints": [
            {"coefficients": [1, 1], "sense": "<=", "rhs": 4},
            {"coefficients": [2, 1], "sense": "<=", "rhs": 5}
        ],
        "bounds": [[0, None], [0, None]]
    }
    
    response = requests.post(url, json=payload)
    return response.json()

result = optimize_production()
print(f"Optimal Solution: {result['data']['optimal_solution']}")
print(f"Max Profit: {result['data']['optimal_value']}")
```

---

*AXIOM Scientific Examples v2.0.0*
