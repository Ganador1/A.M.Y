# API Guide for Mathematics Domain

## Overview
This guide covers the key API endpoints for the Mathematics domain in AXIOM. All endpoints require authentication via API key.

## Key Endpoints

### Arithmetic Operations
- **Endpoint**: `/api/mathematics/arithmetic/calculate`
- **Method**: POST
- **Description**: Perform arithmetic calculations.
- **Example Request**:
  ```bash
  curl -X POST "http://localhost:8000/api/mathematics/arithmetic/calculate" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer YOUR_API_KEY" \
       -d '{"operation": "add", "operands": [1, 2, 3]}'
  ```

### Calculus Differentiation
- **Endpoint**: `/api/mathematics/calculus/differentiate`
- **Method**: POST
- **Description**: Compute derivatives of expressions.
- **Example Request**:
  ```bash
  curl -X POST "http://localhost:8000/api/mathematics/calculus/differentiate" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer YOUR_API_KEY" \
       -d '{"expression": "x**3 + 2*x"}'
  ```

### Quantum Simulation
- **Endpoint**: `/api/mathematics/quantum/simulate`
- **Method**: POST
- **Description**: Simulate quantum circuits.
- **Example Request**:
  ```bash
  curl -X POST "http://localhost:8000/api/mathematics/quantum/simulate" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer YOUR_API_KEY" \
       -d '{"circuit": "H 0; CNOT 0 1"}'
  ```

### ML Model Training
- **Endpoint**: `/api/mathematics/ml/train`
- **Method**: POST
- **Description**: Train ML models for mathematical tasks.
- **Example Request**:
  ```bash
  curl -X POST "http://localhost:8000/api/mathematics/ml/train" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer YOUR_API_KEY" \
       -d '{"data": [[1,2],[3,4]], "labels": [0,1]}'
  ```

## Authentication
All endpoints require an API key in the Authorization header.

## Error Handling
Standard HTTP status codes are used, with detailed error messages in the response body.