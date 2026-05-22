# Astronomy: guía de API

## Router consolidado del dominio
- Archivo: `app/domains/astronomy/routers/api.py`
- `APIRouter(prefix="/astronomy", tags=["Astronomy"])`

## Endpoints típicos
- `GET /astronomy/` → describe el dominio
- `GET /astronomy/services` → lista de capacidades
- `POST /astronomy/analyze-telescope-data` → análisis de datos telescópicos
- `POST /astronomy/run-simulation` → simulaciones

## Auth
Muchos endpoints usan `Depends(get_current_user)` (ver `app/security/auth.py`).

## Errores
- 400 para fallos de validación/negocio
- 500 para fallos inesperados

Para el detalle exacto de modelos request/response:
- `app/domains/astronomy/models/requests.py`
- `app/domains/astronomy/models/responses.py`
