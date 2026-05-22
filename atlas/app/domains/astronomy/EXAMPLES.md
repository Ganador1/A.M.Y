# Examples for Astronomy Domain

## Light Curve Analysis
```python
from app.domains.astronomy.services import LightkurveAdvancedService

service = LightkurveAdvancedService()
result = service.analyze_light_curve(time=[...], flux=[...])
print(result)
```

## Exoplanet Detection
```python
from app.domains.astronomy.services import ExoplanetTransitAnalysisService

service = ExoplanetTransitAnalysisService()
result = service.detect_transits(light_curve={...})
print(result)
```

## Multi-Wavelength Analysis
```bash
curl -X POST "http://localhost:8000/api/astronomy/multiwavelength" \
     -H "Content-Type: application/json" \
     -d '{"data": {...}}'
```