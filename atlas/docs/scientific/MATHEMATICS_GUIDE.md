# 📚 AXIOM Mathematics Domain - Practical Usage Guide

## 🎯 **Introduction**

This guide provides practical examples and real-world use cases for utilizing all capabilities of the AXIOM Mathematics domain.

## 🚀 **Quick Start**

### **Prerequisites**
```bash
# Install dependencies
pip install requests numpy matplotlib plotly scipy pandas

# Run AXIOM server (if available)
# python main.py

# Run demo
python demo_axiom_mathematics.py
```

### **Verify System Status**
```python
import requests

# Verify general status
response = requests.get("http://localhost:8000/api/v1/mathematics/status")
print(response.json())

# Verify specific services
services = [
    "/visualization/status",
    "/ai/status", 
    "/number-theory/status",
    "/theorem-proving/status",
    "/distributed/status"
]

for service in services:
    response = requests.get(f"http://localhost:8000/api/v1/mathematics{service}")
    print(f"{service}: {response.json()['status']}")
```

## 📊 **1. Interactive Mathematical Visualization**

### **2D Function Plots**
```python
import requests

# Basic configuration
base_url = "http://localhost:8000/api/v1/mathematics"

# Simple function plot
function_data = {
    "function": "x**2 + 2*x - 3",
    "x_range": [-5, 3],
    "y_range": [-5, 10],
    "title": "Parabola: f(x) = x² + 2x - 3"
}

response = requests.post(
    f"{base_url}/visualization/2d-plots/function_plot",
    json={"data": function_data}
)

result = response.json()
print(f"Plot created: {result['success']}")
print(f"Interactive HTML: {result['data']['plot_html'][:100]}...")
```

### **Parametric Plots**
```python
# Mathematical Rose
parametric_data = {
    "x_function": "cos(t) * cos(4*t)",
    "y_function": "sin(t) * cos(4*t)", 
    "t_range": [0, 2*3.14159]
}

response = requests.post(
    f"{base_url}/visualization/2d-plots/parametric_plot",
    json={"data": parametric_data}
)

# Archimedean Spiral
spiral_data = {
    "x_function": "t * cos(t)",
    "y_function": "t * sin(t)",
    "t_range": [0, 6*3.14159]
}

response = requests.post(
    f"{base_url}/visualization/2d-plots/parametric_plot", 
    json={"data": spiral_data}
)
```

### **3D Plots**
```python
# Wavy Surface
surface_data = {
    "function": "sin(sqrt(X**2 + Y**2)) * exp(-0.1*sqrt(X**2 + Y**2))",
    "x_range": [-10, 10],
    "y_range": [-10, 10]
}

response = requests.post(
    f"{base_url}/visualization/3d-plots/surface_plot",
    json={"data": surface_data}
)

# Saddle Surface
saddle_data = {
    "function": "X**2 - Y**2", 
    "x_range": [-3, 3],
    "y_range": [-3, 3]
}

response = requests.post(
    f"{base_url}/visualization/3d-plots/surface_plot",
    json={"data": saddle_data}
)
```

### **Mathematical Animations**
```python
# Function animation with variable parameter
animation_data = {
    "function": "a * sin(x) + cos(a*x)",
    "parameter": "a",
    "parameter_range": [0.1, 3.0],
    "x_range": [-6.28, 6.28],
    "frames": 50
}

response = requests.post(
    f"{base_url}/visualization/animations/function_animation",
    json={"data": animation_data}
)
```

## 🧠 **2. Advanced Mathematical AI**

### **Problem Solving**
```python
# Algebra Problem
algebra_problem = {
    "problem": "Solve the system: 2x + 3y = 7, x - y = 1",
    "problem_type": "algebraic"
}

response = requests.post(
    f"{base_url}/ai/solve-problem/advanced_reasoning",
    json={"data": algebra_problem}
)

result = response.json()
print(f"Solution: {result['data']['solution_steps']}")

# Calculus Problem
calculus_problem = {
    "problem": "Find the integral of x^3 * e^x dx",
    "problem_type": "calculus"
}

response = requests.post(
    f"{base_url}/ai/solve-problem/advanced_reasoning", 
    json={"data": calculus_problem}
)
```

### **Pattern Recognition**
```python
# Fibonacci Sequence
fibonacci_pattern = {
    "sequence": [1, 1, 2, 3, 5, 8, 13, 21],
    "pattern_type": "numerical"
}

response = requests.post(
    f"{base_url}/ai/solve-problem/pattern_recognition",
    json={"data": fibonacci_pattern}
)

# Prime Numbers
prime_pattern = {
    "sequence": [2, 3, 5, 7, 11, 13, 17, 19],
    "pattern_type": "numerical"
}

response = requests.post(
    f"{base_url}/ai/solve-problem/pattern_recognition",
    json={"data": prime_pattern}
)
```

### **Mathematical Tutor Mode**
```python
# Personalized Tutoring
tutor_data = {
    "problem": "Prove that the derivative of sin(x) is cos(x)",
    "student_level": "advanced",
    "explanation_style": "detailed"
}

response = requests.post(
    f"{base_url}/ai/mathematical-tutor",
    json={"data": tutor_data}
)

result = response.json()
for step in result['data']['step_by_step_solution']:
    print(f"Step {step['step']}: {step['explanation']}")
    print(f"Hint: {step['hint']}")
```

### **Similar Problem Generation**
```python
# Generate problem variations
problem_generation = {
    "base_problem": "Solve quadratic equation ax² + bx + c = 0",
    "difficulty": "medium",
    "count": 5
}

response = requests.post(
    f"{base_url}/ai/generate-problems",
    json={"data": problem_generation}
)

problems = response.json()['data']['similar_problems']
for i, problem in enumerate(problems, 1):
    print(f"{i}. {problem}")
```

## 🔢 **3. Computational Number Theory**

### **Algebraic Number Fields**
```python
# Field Q(√2)
field_sqrt2 = {
    "polynomial": [1, 0, -2],  # x² - 2
    "name": "Q(√2)"
}

response = requests.post(
    f"{base_url}/number-theory/algebraic-fields/create_number_field",
    json={"data": field_sqrt2}
)

# Field Q(∛2)
field_cbrt2 = {
    "polynomial": [1, 0, 0, -2],  # x³ - 2
    "name": "Q(∛2)"
}

response = requests.post(
    f"{base_url}/number-theory/algebraic-fields/create_number_field",
    json={"data": field_cbrt2}
)

# Field Operations
field_operations = {
    "field_data": {"polynomial": [1, 0, -2]},
    "operation_type": "norm",
    "element": [3, 2]  # 3 + 2√2
}

response = requests.post(
    f"{base_url}/number-theory/algebraic-fields/field_operations",
    json={"data": field_operations}
)
```

### **Elliptic Curves**
```python
# Standard Elliptic Curve
curve_standard = {
    "a": -1,
    "b": 1,
    "field": "rational"
}

response = requests.post(
    f"{base_url}/number-theory/elliptic-curves/create_curve",
    json={"data": curve_standard}
)

# Point Addition on Curve
point_addition = {
    "curve_data": {"a": -1, "b": 1},
    "point1": [0, 1],
    "point2": [1, 1]
}

response = requests.post(
    f"{base_url}/number-theory/elliptic-curves/group_law",
    json={"data": point_addition}
)

# Torsion Points
torsion_points = {
    "curve_data": {"a": -1, "b": 1},
    "order": 2
}

response = requests.post(
    f"{base_url}/number-theory/elliptic-curves/torsion_points",
    json={"data": torsion_points}
)
```

### **Finite Fields**
```python
# Finite Field F₇
finite_field_7 = {
    "prime": 7,
    "degree": 1
}

response = requests.post(
    f"{base_url}/number-theory/finite-fields/create_field",
    json={"data": finite_field_7}
)

# Finite Field F₂₈ (degree 8 extension)
finite_field_256 = {
    "prime": 2,
    "degree": 8
}

response = requests.post(
    f"{base_url}/number-theory/finite-fields/create_field", 
    json={"data": finite_field_256}
)

# Finite Field Arithmetic
field_arithmetic = {
    "field_data": {"prime": 7, "degree": 1},
    "element1": 5,
    "element2": 3,
    "operation_type": "multiply"
}

response = requests.post(
    f"{base_url}/number-theory/finite-fields/field_arithmetic",
    json={"data": field_arithmetic}
)
```

### **Lattices**
```python
# 2D Lattice
lattice_2d = {
    "basis": [[1, 0], [0.5, 0.866]]  # Hexagonal basis
}

response = requests.post(
    f"{base_url}/number-theory/lattices/create_lattice",
    json={"data": lattice_2d}
)

# Shortest Vector
shortest_vector = {
    "lattice_data": {"basis": [[3, 1], [1, 2]]}
}

response = requests.post(
    f"{base_url}/number-theory/lattices/shortest_vector",
    json={"data": shortest_vector}
)

# Basis Reduction (LLL)
basis_reduction = {
    "lattice_data": {"basis": [[1, 1, 1], [1, 0, 1], [1, 1, 0]]}
}

response = requests.post(
    f"{base_url}/number-theory/lattices/basis_reduction",
    json={"data": basis_reduction}
)
```

## 🔬 **4. Automated Theorem Proving**

### **Formal Verification**
```python
# Verify Identity Theorem
identity_theorem = {
    "theorem": "For all real numbers x, x + 0 = x",
    "proof_steps": [
        "Let x be an arbitrary real number",
        "By definition of addition, x + 0 = x",
        "Therefore, the theorem holds for all real x"
    ],
    "logical_system": "first_order_logic"
}

response = requests.post(
    f"{base_url}/theorem-proving/formal-verification/verify_theorem",
    json={"data": identity_theorem}
)

# Verify Algorithm
bubble_sort_verification = {
    "algorithm": "Bubble Sort",
    "preconditions": ["Array of comparable elements"],
    "postconditions": ["Array is sorted", "No elements lost or added"]
}

response = requests.post(
    f"{base_url}/theorem-proving/formal-verification/verify_algorithm",
    json={"data": bubble_sort_verification}
)
```

### **Automated Proof Generation**
```python
# Generate Proof by Induction
induction_proof = {
    "theorem": "For all n ≥ 1, 1 + 2 + ... + n = n(n+1)/2",
    "method": "proof_by_induction",
    "max_steps": 15
}

response = requests.post(
    f"{base_url}/theorem-proving/automated-proving/generate_proof",
    json={"data": induction_proof}
)

# Proof Search
proof_search = {
    "goal": "Prove that √2 is irrational",
    "available_lemmas": [
        "If p² is even, then p is even",
        "gcd(a, b) = 1 implies no common factors"
    ],
    "search_depth": 10
}

response = requests.post(
    f"{base_url}/theorem-proving/automated-proving/proof_search",
    json={"data": proof_search}
)
```

### **Consistency Analysis**
```python
# Verify Axiom Consistency
axiom_consistency = {
    "axioms": [
        "All men are mortal",
        "Socrates is a man",
        "Mortal beings die"
    ],
    "system": "first_order_logic"
}

response = requests.post(
    f"{base_url}/theorem-proving/consistency-analysis/check_consistency",
    json={"data": axiom_consistency}
)

# Find Contradictions
contradiction_check = {
    "statements": [
        "All swans are white",
        "Some swans are black",
        "Nothing can be both white and black"
    ]
}

response = requests.post(
    f"{base_url}/theorem-proving/consistency-analysis/find_contradictions",
    json={"data": contradiction_check}
)
```

### **Counterexample Generation**
```python
# Refute False Conjecture
false_conjecture = {
    "conjecture": "All prime numbers are odd",
    "domain": "natural_numbers"
}

response = requests.post(
    f"{base_url}/theorem-proving/counterexample-generation/generate_counterexample",
    json={"data": false_conjecture}
)

# Attempt to Refute True Conjecture
goldbach_conjecture = {
    "conjecture": "Every even integer greater than 2 can be expressed as the sum of two primes",
    "method": "exhaustive_search"
}

response = requests.post(
    f"{base_url}/theorem-proving/counterexample-generation/refute_conjecture",
    json={"data": goldbach_conjecture}
)
```

## ☁️ **5. Distributed Computing**

### **Parallel Processing**
```python
# Large Matrix Multiplication
large_matrices = {
    "matrices": [
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        [[9, 8, 7], [6, 5, 4], [3, 2, 1]]
    ],
    "operation_type": "multiplication",
    "strategy": "block_wise"
}

response = requests.post(
    f"{base_url}/distributed/parallel-processing/matrix_operations",
    json={"data": large_matrices}
)

# Parallel Numerical Integration
parallel_integration = {
    "function": "sin(x) * cos(x) * exp(-x**2)",
    "range": [0, 10],
    "method": "simpson",
    "chunks": 8
}

response = requests.post(
    f"{base_url}/distributed/parallel-processing/numerical_integration",
    json={"data": parallel_integration}
)

# Parallel Optimization
parallel_optimization = {
    "objective": "x**2 + y**2 - 2*x*y + sin(x) + cos(y)",
    "constraints": ["x >= -5", "x <= 5", "y >= -5", "y <= 5"],
    "algorithm": "genetic",
    "populations": 4
}

response = requests.post(
    f"{base_url}/distributed/parallel-processing/optimization",
    json={"data": parallel_optimization}
)
```

### **Load Balancing**
```python
# Distribute Computational Tasks
computational_tasks = {
    "tasks": [f"compute_prime_{i}" for i in range(1, 25)],
    "strategy": "weighted_round_robin",
    "priority": "high"
}

response = requests.post(
    f"{base_url}/distributed/load-balancing/distribute_tasks",
    json={"data": computational_tasks}
)

# Optimize System Resources
resource_optimization = {
    "constraints": {
        "max_cpu": 0.8,
        "max_memory": 0.9,
        "max_network": 1000
    },
    "goal": "maximize_throughput"
}

response = requests.post(
    f"{base_url}/distributed/load-balancing/optimize_resources",
    json={"data": resource_optimization}
)
```

### **Horizontal Scaling**
```python
# Scale Up under High Load
scale_up = {
    "load": 0.9,
    "target": 0.95,
    "strategy": "predictive"
}

response = requests.post(
    f"{base_url}/distributed/horizontal-scaling/scale_up",
    json={"data": scale_up}
)

# Scale Down to Optimize Costs
scale_down = {
    "load": 0.3,
    "cost_optimization": True
}

response = requests.post(
    f"{base_url}/distributed/horizontal-scaling/scale_down",
    json={"data": scale_down}
)
```

### **Fault Tolerance**
```python
# Detect System Failures
failure_detection = {
    "interval": 5,
    "threshold": 0.95
}

response = requests.post(
    f"{base_url}/distributed/fault-tolerance/detect_failures",
    json={"data": failure_detection}
)

# Recover from Node Failure
failure_recovery = {
    "failure_type": "node_failure",
    "strategy": "automatic_failover"
}

response = requests.post(
    f"{base_url}/distributed/fault-tolerance/recover_from_failure",
    json={"data": failure_recovery}
)
```

## 📊 **6. Integrated Use Cases**

### **Mathematical Analysis Pipeline**
```python
def mathematical_analysis_pipeline(problem_text):
    """Complete mathematical analysis pipeline"""
    
    # Step 1: Generate problem variations
    generation_data = {
        "base_problem": problem_text,
        "difficulty": "medium",
        "count": 3
    }
    
    problems_response = requests.post(
        f"{base_url}/ai/generate-problems",
        json={"data": generation_data}
    )
    
    # Step 2: Solve with AI
    solve_data = {
        "problem": problem_text,
        "problem_type": "general"
    }
    
    solution_response = requests.post(
        f"{base_url}/ai/solve-problem/advanced_reasoning",
        json={"data": solve_data}
    )
    
    # Step 3: Verify solution
    verification_data = {
        "problem": problem_text,
        "solution": "Extracted from AI response",
        "verification_methods": ["substitution", "logic"]
    }
    
    verification_response = requests.post(
        f"{base_url}/ai/verify-solution",
        json={"data": verification_data}
    )
    
    # Step 4: Create visualization if appropriate
    if "x" in problem_text.lower():
        viz_data = {
            "function": "extracted_function",
            "x_range": [-10, 10],
            "title": f"Visualization: {problem_text}"
        }
        
        viz_response = requests.post(
            f"{base_url}/visualization/2d-plots/function_plot",
            json={"data": viz_data}
        )
    
    return {
        "problems": problems_response.json(),
        "solution": solution_response.json(),
        "verification": verification_response.json(),
        "visualization": viz_response.json() if 'viz_response' in locals() else None
    }

# Execute pipeline
result = mathematical_analysis_pipeline("Find the roots of x² - 4x + 3 = 0")
```

### **Cryptographic Analysis**
```python
def cryptographic_analysis():
    """Cryptographic analysis using number theory"""
    
    # Create elliptic curve for cryptography
    crypto_curve = {
        "a": -3,
        "b": 1,
        "field": "finite"
    }
    
    curve_response = requests.post(
        f"{base_url}/number-theory/elliptic-curves/create_curve",
        json={"data": crypto_curve}
    )
    
    # Cryptographic analysis
    crypto_analysis = {
        "crypto_type": "elliptic_curve",
        "parameters": {
            "curve": crypto_curve,
            "key_size": 256
        }
    }
    
    analysis_response = requests.post(
        f"{base_url}/number-theory/cryptographic-analysis",
        json={"data": crypto_analysis}
    )
    
    return analysis_response.json()

# Execute analysis
crypto_result = cryptographic_analysis()
```

### **Distributed Scientific Optimization**
```python
def scientific_optimization():
    """Scientific optimization with distributed computing"""
    
    # Define complex optimization problem
    optimization_problem = {
        "objective": "minimize energy function with multiple variables",
        "constraints": ["physical constraints", "boundary conditions"],
        "algorithm": "multi_objective_genetic",
        "parallel_populations": 8
    }
    
    # Execute distributed optimization
    optimization_response = requests.post(
        f"{base_url}/distributed/parallel-processing/optimization",
        json={"data": optimization_problem}
    )
    
    # Analyze performance
    performance_data = {
        "types": ["cpu", "memory", "convergence"],
        "time_range": "optimization_duration"
    }
    
    performance_response = requests.post(
        f"{base_url}/distributed/performance-monitoring/get_metrics",
        json={"data": performance_data}
    )
    
    return {
        "optimization": optimization_response.json(),
        "performance": performance_response.json()
    }

# Execute scientific optimization
scientific_result = scientific_optimization()
```

## 🔧 **Advanced Configuration**

### **Environment Variables**
```bash
# Server Configuration
export AXIOM_HOST=localhost
export AXIOM_PORT=8000
export AXIOM_DEBUG=true

# Distributed Computing Configuration
export AXIOM_NODES=4
export AXIOM_MAX_MEMORY=8GB
export AXIOM_CACHE_SIZE=1GB

# Visualization Configuration
export AXIOM_PLOT_DPI=300
export AXIOM_PLOT_FORMAT=png
export AXIOM_INTERACTIVE=true
```

### **Client Configuration**
```python
class AxiomMathClient:
    def __init__(self, base_url="http://localhost:8000", timeout=30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "AxiomMathClient/1.0"
        })
    
    def make_request(self, endpoint, data=None, method="GET"):
        url = f"{self.base_url}/api/v1/mathematics{endpoint}"
        
        if method == "POST":
            response = self.session.post(url, json={"data": data}, timeout=self.timeout)
        else:
            response = self.session.get(url, timeout=self.timeout)
        
        return response.json()
    
    def visualize(self, plot_type, data):
        return self.make_request(f"/visualization/{plot_type}", data, "POST")
    
    def solve_with_ai(self, problem, problem_type="general"):
        data = {"problem": problem, "problem_type": problem_type}
        return self.make_request("/ai/solve-problem/advanced_reasoning", data, "POST")
    
    def verify_theorem(self, theorem, proof_steps):
        data = {"theorem": theorem, "proof_steps": proof_steps}
        return self.make_request("/theorem-proving/formal-verification/verify_theorem", data, "POST")

# Client Usage
client = AxiomMathClient()
result = client.solve_with_ai("Integrate x^2 dx", "calculus")
```

## 🐛 **Troubleshooting**

### **Common Errors**

**Connection Error:**
```python
# Verify Connectivity
try:
    response = requests.get(f"{base_url}/status", timeout=5)
    print(f"Server status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to AXIOM server")
    print("💡 Solution: Verify the server is running")
```

**Data Format Error:**
```python
# Correct Data Format
correct_format = {
    "data": {  # Important! Data must be wrapped in "data"
        "function": "x**2",
        "x_range": [-5, 5]
    }
}

# Incorrect Format
incorrect_format = {
    "function": "x**2",
    "x_range": [-5, 5]
}
```

**Timeout on Long Operations:**
```python
# Increase Timeout for Complex Operations
response = requests.post(
    url, 
    json=data, 
    timeout=120  # 2 minutes for complex operations
)
```

### **Logs and Debugging**
```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Enable detailed logs
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
```

## 📈 **Monitoring and Metrics**

### **Performance Metrics**
```python
def get_system_metrics():
    """Get complete system metrics"""
    
    metrics_data = {
        "types": ["cpu", "memory", "network", "throughput"],
        "time_range": "last_hour"
    }
    
    response = requests.post(
        f"{base_url}/distributed/performance-monitoring/get_metrics",
        json={"data": metrics_data}
    )
    
    return response.json()

# Continuous Monitoring
import time

def monitor_system(duration_minutes=60, interval_seconds=30):
    """Monitor system for specified duration"""
    
    end_time = time.time() + (duration_minutes * 60)
    
    while time.time() < end_time:
        metrics = get_system_metrics()
        
        if metrics['success']:
            data = metrics['data']['metrics']
            print(f"CPU: {data['cpu_utilization']*100:.1f}% | "
                  f"Memory: {data['memory_utilization']*100:.1f}% | "
                  f"Throughput: {data['throughput']} req/s")
        
        time.sleep(interval_seconds)

# Execute Monitoring
monitor_system(duration_minutes=30, interval_seconds=60)
```

## 🎯 **Best Practices**

### **Performance Optimization**
1. **Use parallel processing** for intensive operations
2. **Implement caching** for frequent results
3. **Monitor metrics** regularly
4. **Scale horizontally** under high load

### **Security**
1. **Validate input** before sending to server
2. **Use HTTPS** in production
3. **Implement rate limiting** to prevent abuse
4. **Audit logs** for sensitive operations

### **Development**
1. **Use demo mode** for serverless development
2. **Implement automated tests** for all functionalities
3. **Document specific use cases**
4. **Maintain backward compatibility** in APIs

---

## 🎉 **Conclusion**

This guide covers all practical aspects of using the AXIOM Mathematics domain. With these examples and patterns, you can:

- 📊 Create impressive mathematical visualizations
- 🧠 Solve complex problems with AI
- 🔢 Perform advanced number theory calculations
- 🔬 Formally verify theorems
- ☁️ Leverage distributed computing
- 🔧 Integrate all capabilities into workflows

The AXIOM Mathematics Domain is ready to power your mathematical research and development! 🚀

---

*Developed with ❤️ for the mathematical community*  
*AXIOM Mathematics Domain v2.2.0*
