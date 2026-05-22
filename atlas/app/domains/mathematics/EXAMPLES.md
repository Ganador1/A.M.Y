# Ejemplos - Mathematics

## Ejecutar Optimización (LP)
```bash
curl -X POST "http://localhost:8000/mathematics/execute/optimization/linear_programming" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "objective": "minimize",
      "c": [1, 2, 3],
      "A": [[1, 0, 2], [0, 1, 1]],
      "b": [4, 3],
      "bounds": [[0, null], [0, null], [0, null]]
    }
  }'
```

## Primalidad (Number Theory)
```bash
curl -X POST "http://localhost:8000/mathematics/execute/number_theory/is_prime" \
  -H "Content-Type: application/json" \
  -d '{ "data": { "n": 104729 } }'
```

## Símbolos y Simplificación (SymPy)
```bash
curl -X POST "http://localhost:8000/mathematics/execute/sympy/simplify" \
  -H "Content-Type: application/json" \
  -d '{ "data": { "expression": "sin(x)**2 + cos(x)**2" } }'
```

## Topología de Datos
```bash
curl -X POST "http://localhost:8000/mathematics/execute/topology/persistent_homology" \
  -H "Content-Type: application/json" \
  -d '{ "data": { "points": [[0,0],[1,0],[0,1],[1,1]], "metric": "euclidean" } }'
```

## Batch de Operaciones
```bash
curl -X POST "http://localhost:8000/mathematics/batch-execute" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "operations": [
        { "service_name": "optimization", "operation": "linear_programming", "parameters": { "c": [1,2], "A": [[1,1]], "b": [3] } },
        { "service_name": "number_theory", "operation": "is_prime", "parameters": { "n": 97 } }
      ]
    }
  }'
```