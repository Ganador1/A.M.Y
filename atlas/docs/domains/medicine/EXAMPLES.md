# Medicine: ejemplos

## Ejemplo (REST) - compute genérico
```bash
curl -X POST "http://localhost:8000/medicine/compute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"operation": "summarize", "parameters": {"text": "Clinical note..."}}'
```

Nota: la operación exacta depende de la implementación en `app/domains/medicine/services/computation.py`.
