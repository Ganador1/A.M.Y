# Engineering: ejemplos

## Ejemplo (SDK Python) - PCR simulado
```python
from app.domains.engineering.services.lab_automation_service import LabAutomationService

service = LabAutomationService()
await service.initialize()
result = await service.run_pcr_protocol(samples=[{"id": "S1", "well": "A1", "volume": 25}])
print(result)
```

## Ejemplo (REST)
Revisar `app/routers/lab_automation.py` para la ruta exacta; depende de prefijos de inclusión.
