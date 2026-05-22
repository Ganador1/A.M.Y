# Medicine: guía de API

## Router consolidado
- Archivo: `app/domains/medicine/routers/api.py`
- `APIRouter(prefix="/medicine", tags=["Medicine"])`

## Endpoints base
- `GET /medicine/`
- `GET /medicine/services`
- `POST /medicine/compute`
- `POST /medicine/analyze`

## Routers complementarios
- Router unificado: `app/domains/medicine/routers/unified_medical_router.py`
- WebSocket: `app/domains/medicine/routers/websocket_router.py`

## Modelos
- `app/domains/medicine/models/requests.py`
- `app/domains/medicine/models/responses.py`
