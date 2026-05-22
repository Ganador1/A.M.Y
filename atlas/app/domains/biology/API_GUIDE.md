# Guía de API para Biology

## Endpoints Principales
- **/biogpt/generate**: Genera texto biomédico. Método: POST. Input: {"prompt": "texto"}.
- **/biomedical-nlp/extract-entities**: Extrae entidades. Método: POST. Input: {"text": "texto"}.
- **/advanced-genomics/variant-calling**: Llamada de variantes. Método: POST.

## Autenticación
Usa API keys en headers.

## Ejemplos de Requests
```bash
curl -X POST "http://localhost:8000/api/biology/biogpt/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain DNA replication"}'
```

Consulta API_REFERENCE_GENERATED.md para detalles completos.