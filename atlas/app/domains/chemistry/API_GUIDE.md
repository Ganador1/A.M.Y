# API Guide for Chemistry Domain

## Key Endpoints
- `/chemistry/computational/analyze`: Molecular analysis (POST).
- `/chemistry/chemml/predict`: Property prediction (POST).
- `/chemistry/nmr/analyze`: NMR analysis (POST).
- `/chemistry/materials/discover`: Materials discovery (POST).

## Authentication
Required for sensitive operations.

## Example Request
```bash
curl -X POST \"http://localhost:8000/api/chemistry/computational/analyze\" -d '{\"smiles\": \"CCO\"}'
```