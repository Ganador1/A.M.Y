# Examples for Climate Domain

## Climate Evidence Analysis
```python
from app.domains.climate.services import ClimateEvidenceService

service = ClimateEvidenceService()
result = await service.process_request({"action": "climate_evidence"})
print(result)
```