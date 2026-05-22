# Astronomy: ejemplos

## Ejemplo (SDK Python)
```python
from app.domains.astronomy.services import astronomy_service

result = await astronomy_service.analyze_telescope_data(
    telescope_name="DemoScope",
    data_type="light_curve",
    coordinates={"ra": 12.34, "dec": -56.78},
    observation_parameters={"exposure_s": 30}
)
print(result)
```

## Ejemplo (REST)
```bash
curl -X POST "http://localhost:8000/astronomy/analyze-telescope-data" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "telescope_name": "DemoScope",
    "data_type": "light_curve",
    "coordinates": {"ra": 12.34, "dec": -56.78},
    "observation_parameters": {"exposure_s": 30}
  }'
```

Nota: la URL exacta depende de cómo se incluya el router en la app.
