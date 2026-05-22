# Chemistry: ejemplos

## Ejemplo (SDK Python)
```python
from app.domains.chemistry.services.computational_chemistry import ComputationalChemistryService

service = ComputationalChemistryService()
result = service.analyze_molecule({"smiles": "CCO"})
print(result)
```

## Ejemplo (REST)
```bash
curl -X POST "http://localhost:8000/chemistry/compute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"operation": "analyze_molecule", "parameters": {"smiles": "CCO"}}'
```
