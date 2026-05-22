# Dominio: Climate

## Qué es
Dominio para análisis y evidencia climática, centrado en series temporales (p.ej. anomalías de temperatura) y extracción de “evidence scores”.

## Ubicación en el código
- Paquete: `app/domains/climate/`
- Utilidades de datos: `app/domains/climate/data_utils.py`
- Servicios: `app/domains/climate/services/`

## Servicio principal
- `ClimateEvidenceService`: `app/domains/climate/services/climate_evidence_service.py`

## Datos (fuentes)
- Dataset GISTEMP: se referencia desde `real_data_tests/` (ruta exacta depende de config).

## API
En este dominio no veo un `routers/api.py` como en Astronomy; suele consumirse vía servicios o routers de plataforma. Si existe un router en `app/routers/` relacionado (p.ej. `advanced_earth_sciences.py` o `earth_sciences_light.py`), ese suele ser el punto de entrada HTTP.

## Referencias cercanas al código
- `app/domains/climate/README.md`
- `app/domains/climate/API_GUIDE.md`
- `app/domains/climate/SERVICES.md`
- `app/domains/climate/EXAMPLES.md`
