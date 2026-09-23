#!/bin/bash
"""
Automated test script for Mathematics AI endpoints
"""

echo "🚀 Starting Mathematics AI Automated Test"
echo "=========================================="

# Start server in background
echo "📡 Starting server..."
cd .
source .venv/bin/activate
python main.py &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to be ready..."
sleep 5

# Test health endpoint
echo -e "\n🏥 Testing Health Endpoint:"
curl -s "http://localhost:8002/health" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Status: {data.get(\"status\")}'); print(f'Version: {data.get(\"version\")}'); print(f'Uptime: {data.get(\"uptime_seconds\")}s')"

# Test Simulated Annealing
echo -e "\n🧪 Testing Simulated Annealing:"
RESPONSE=$(curl -s -X POST "http://localhost:8002/api/optimization/simulated_annealing" \
  -H "Content-Type: application/json" \
  -d '{
    "objective_function": "x**2 + y**2",
    "variables": ["x", "y"],
    "bounds": {"x": [-5, 5], "y": [-5, 5]}
  }')

if [ $? -eq 0 ] && [ ! -z "$RESPONSE" ]; then
    echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('✅ Simulated Annealing Results:')
print(f'  Status: {data.get(\"status\")}')
print(f'  Optimal value: {data.get(\"optimal_value\", \"N/A\"):.4f}')
print(f'  Variables: {data.get(\"optimal_variables\")}')
print(f'  Iterations: {data.get(\"iterations\")}')
print(f'  Convergence: {data.get(\"convergence\")}')
"
else
    echo "❌ Failed to get response from Simulated Annealing endpoint"
fi

# Test Genetic Algorithm
echo -e "\n🧬 Testing Genetic Algorithm:"
RESPONSE=$(curl -s -X POST "http://localhost:8002/api/optimization/genetic_algorithm" \
  -H "Content-Type: application/json" \
  -d '{
    "objective_function": "x**2 + y**2",
    "variables": ["x", "y"],
    "bounds": {"x": [-3, 3], "y": [-3, 3]}
  }')

if [ $? -eq 0 ] && [ ! -z "$RESPONSE" ]; then
    echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('✅ Genetic Algorithm Results:')
print(f'  Status: {data.get(\"status\")}')
print(f'  Optimal value: {data.get(\"optimal_value\", \"N/A\"):.4f}')
print(f'  Variables: {data.get(\"optimal_variables\")}')
print(f'  Generations: {data.get(\"generations\")}')
"
else
    echo "❌ Failed to get response from Genetic Algorithm endpoint"
fi

# Test PDE Heat Equation
echo -e "\n🔥 Testing PDE Heat Equation:"
RESPONSE=$(curl -s -X POST "http://localhost:8002/api/pde/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "equation_type": "heat",
    "parameters": {
      "length": 1.0,
      "time": 0.1,
      "thermal_diffusivity": 0.1,
      "nx": 20,
      "nt": 50
    }
  }')

if [ $? -eq 0 ] && [ ! -z "$RESPONSE" ]; then
    echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('✅ PDE Heat Equation Results:')
print(f'  Status: {data.get(\"status\")}')
print(f'  Solution type: {data.get(\"solution_type\")}')
print(f'  Has solution: {\"solution\" in data}')
"
else
    echo "❌ Failed to get response from PDE endpoint"
fi

# Cleanup
echo -e "\n🧹 Cleaning up..."
kill $SERVER_PID 2>/dev/null || true

echo -e "\n✨ Test completed!"
