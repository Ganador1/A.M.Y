# Climate: ejemplos

## Ejemplo (SDK Python)
```python
from app.domains.climate.services.climate_evidence_service import ClimateEvidenceService

service = ClimateEvidenceService()
result = await service.process_request({"action": "climate_evidence"})
print(result)
```
