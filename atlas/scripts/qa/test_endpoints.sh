#!/bin/bash
# ⚠️ Advertencia de seguridad
# Este script realiza llamadas HTTP contra un servidor local.
# No lo uses contra entornos públicos sin autenticación/TLS.
# Evita imprimir tokens o PII. Revisa ETHICS_AND_SAFETY.md.

# Test script for Mathematics AI optimization endpoints

echo "Testing Mathematics AI Optimization Endpoints"
echo "=============================================="

# Wait for server to start
sleep 5

# Test Simulated Annealing
echo -e "\n1. Testing Simulated Annealing:"
curl -s -X POST "http://localhost:8001/optimization/simulated_annealing" \
  -H "Content-Type: application/json" \
  -d '{
    "objective_function": "x**2 + y**2",
    "variables": ["x", "y"],
    "bounds": {"x": [-10, 10], "y": [-10, 10]}
  }' | python3 -m json.tool | head -20

echo -e "\n2. Testing Genetic Algorithm:"
curl -s -X POST "http://localhost:8001/optimization/genetic_algorithm" \
  -H "Content-Type: application/json" \
  -d '{
    "objective_function": "x**2 + y**2",
    "variables": ["x", "y"],
    "bounds": {"x": [-5, 5], "y": [-5, 5]}
  }' | python3 -m json.tool | head -20

echo -e "\n3. Testing Particle Swarm Optimization:"
curl -s -X POST "http://localhost:8001/optimization/particle_swarm" \
  -H "Content-Type: application/json" \
  -d '{
    "objective_function": "x**2 + y**2",
    "variables": ["x", "y"],
    "bounds": {"x": [-5, 5], "y": [-5, 5]}
  }' | python3 -m json.tool | head -20

echo -e "\n4. Testing PDE Heat Equation:"
curl -s -X POST "http://localhost:8001/pde/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "equation_type": "heat",
    "parameters": {
      "length": 1.0,
      "time": 0.1,
      "thermal_diffusivity": 0.1,
      "nx": 50,
      "nt": 100
    }
  }' | python3 -m json.tool | head -20

echo -e "\nTest completed!"
