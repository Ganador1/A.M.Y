# Chemistry: guía de API

## Router consolidado
- Archivo: `app/domains/chemistry/routers/api.py`
- `APIRouter(prefix="/chemistry", tags=["Chemistry"])`

## Endpoints base
- `GET /chemistry/`
- `GET /chemistry/services`
- `POST /chemistry/compute`
- `POST /chemistry/analyze`

## Endpoints avanzados
El router incluye endpoints “enhanced” conectados a loops/pipelines. Ver el archivo para el listado completo.

## Modelos request/response
- `app/domains/chemistry/models/requests.py`
- `app/domains/chemistry/models/responses.py`
