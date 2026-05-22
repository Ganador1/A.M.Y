# Examples for Engineering Domain

## Execute Lab Protocol
```python
from app.domains.engineering.services import AdvancedLabAutomationService

service = AdvancedLabAutomationService()
result = service.execute_protocol("pcr", parameters={"cycles": 30})
print(result)
```

## List Equipment
```bash
curl "http://localhost:8000/api/v1/lab-equipment/equipment"
```

## Submit Synthesis Task
```bash
curl -X POST "http://localhost:8000/api/v1/synthesis-equipment/submit" \
     -H "Content-Type: application/json" \
     -d '{"equipment_type": "reactor", "parameters": {...}}'
```