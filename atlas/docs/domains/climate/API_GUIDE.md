# Climate: guía de API

Este dominio es mayormente “service-first”. Los endpoints HTTP suelen estar en routers de plataforma:
- `app/routers/advanced_earth_sciences.py`
- `app/routers/earth_sciences_light.py`

Si tu intención es exponer `/climate/...` como router consolidado, el patrón recomendado es el mismo que Astronomy:
- Crear `app/domains/climate/routers/api.py` con `APIRouter(prefix="/climate")`
- Registrar el router (router registry) o incluirlo en la app
