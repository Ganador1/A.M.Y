# Neuroscience: ejemplos

## Ejemplo (SDK Python)
```python
from app.domains.neuroscience.services.neuroscience_light_service import NeuroscienceLightService

service = NeuroscienceLightService()
result = await service.process_request({"action": "eeg_basic_analysis", "data": [0.1, 0.2, 0.15]})
print(result)
```
