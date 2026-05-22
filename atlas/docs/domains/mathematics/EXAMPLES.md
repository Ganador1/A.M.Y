# Examples for Mathematics Domain

## Arithmetic Calculation
```python
from axiom.domains.mathematics.services.arithmetic_service import ArithmeticService
from axiom.domains.mathematics.models import ArithmeticRequest

request = ArithmeticRequest(operation="power", operands=[2, 3])
service = ArithmeticService()
result = service.calculate(request)
print(result.result)  # Output: 8.0
```

## Solving Equations
```python
from axiom.domains.mathematics import EquationService

service = EquationService()
result = service.solve_equation("x**2 - 5*x + 6 = 0")
print(result)  # Output: Solutions for x
```

## API Example: Calculus Operation
```bash
curl -X POST "http://localhost:8000/api/mathematics/calculus/differentiate" \
     -H "Content-Type: application/json" \
     -d '{"expression": "x**2 + 3*x"}'
# Response: {"derivative": "2*x + 3"}
```

## Quantum Simulation
```bash
curl -X POST "http://localhost:8000/api/mathematics/quantum/simulate" \
     -H "Content-Type: application/json" \
     -d '{"circuit": "basic_qubit_circuit"}'
# Response: Simulation results
```