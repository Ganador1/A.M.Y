> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="astronomy-guía-de-api"></a>
# Astronomy: API guide

<a id="router-consolidado-del-dominio"></a>
## Consolidated domain router
- File: `app/domains/astronomy/routers/api.py`
- `APIRouter(prefix="/astronomy", tags=["Astronomy"])`

<a id="endpoints-típicos"></a>
## Typical endpoints
- `GET /astronomy/` → describes the domain
- `GET /astronomy/services` → list of capabilities
- `POST /astronomy/analyze-telescope-data` → telescopic data analysis
- `POST /astronomy/run-simulation` → simulations

<a id="auth"></a>
## Auth
Many endpoints use `Depends(get_current_user)` (see `app/security/auth.py`).

<a id="errores"></a>
## Errors
- 400 for validation/business failures
- 500 for unexpected failures

For the exact detail of request/response models:
- `app/domains/astronomy/models/requests.py`
- `app/domains/astronomy/models/responses.py`
