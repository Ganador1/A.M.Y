# Ejemplos Ejecutables en Biology

## Ejemplo 1: Simulación Neuronal
```python
from app.domains.biology.services.computational_biology import ComputationalBiologyService

service = ComputationalBiologyService()
params = {'neurons': 100, 'duration': 1000}
result = service.simulate_neural_network(params)
print(result)
```

## Ejemplo 2: Extracción de Entidades NLP
```bash
curl -X POST "http://localhost:8000/api/biology/biomedical-nlp/extract-entities" \
  -H "Content-Type: application/json" \
  -d '{"text": "The p53 gene is mutated in cancer."}'
```

## Ejemplo 3: Generación con BioGPT
```python
from app.domains.biology.services.biogpt_service import BioGPTService

service = BioGPTService()
result = service.generate_text("Generate a hypothesis about p53")
print(result)
```

Más ejemplos en notebooks/02_biology_domain_tour.ipynb.