# Physics: guía de API

## Router consolidado
- Archivo: `app/domains/physics/routers/api.py`
- `APIRouter(prefix="/physics", tags=["Physics"])`

## Endpoints base
- `GET /physics/`
- `GET /physics/services`
- `POST /physics/compute`
- `POST /physics/analyze`

## Endpoints especializados
- Ver `app/domains/physics/routers/` y `app/routers/quantum_*.py`.

## Errores
- El dominio usa excepciones como `QuantumError` (ver `app/exceptions/domain/physics.py`).
