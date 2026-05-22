# Configuración Central de AXIOM ATLAS

Esta guía consolida las variables de entorno y opciones principales que controlan el comportamiento de la plataforma. Todas las variables tienen valores por defecto seguros para entornos de desarrollo; en producción se recomienda fijarlas explícitamente.

## 1. Servidor y API

| Variable | Default | Descripción |
| --- | --- | --- |
| `HOST` (`APP_HOST`) | `0.0.0.0` | Dirección donde escuchar peticiones HTTP. Alias: `HOST`. |
| `PORT` (`APP_PORT`) | `8002` | Puerto TCP para exponer la API. |
| `DEBUG` | `False` | Activa trazas adicionales en FastAPI. |
| `RELOAD` | `False` | Reinicia automáticamente el servidor al detectar cambios (solo desarrollo). |
| `API_V1_PREFIX` | `/api` | Prefijo base para endpoints versionados. |
| `DOCS_URL` | `/docs` | Ruta de la interfaz OpenAPI. |
| `REDOC_URL` | `/redoc` | Ruta de la documentación ReDoc. |

> Estas variables se definen en `app/core/config.py` y se aplican tanto a `main.py` como a `main_refactored.py`.

## 2. CORS

| Variable | Default | Descripción |
| --- | --- | --- |
| `CORS_ALLOW_ORIGINS` | Lista de hosts locales | Lista separada por comas con orígenes autorizados para peticiones cross-origin. |

Si la variable no está definida, se usa el conjunto por defecto: `http://localhost`, `http://127.0.0.1` y variantes con puerto 8002.

## 3. Seguridad

| Variable | Default | Descripción |
| --- | --- | --- |
| `SECRET_KEY` | Generada al vuelo | Clave para firmar tokens (HS256). Persistir en producción. |
| `ENABLE_AUTH_ROUTES` | `false` | Activa rutas protegidas mediante Bearer token. |
| `API_BEARER_TOKEN` | `None` | Token esperado cuando `ENABLE_AUTH_ROUTES=true`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Duración de tokens de acceso. |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | `10080` | Duración de tokens de refresco (7 días). |

### Seguridad e integridad avanzada

Los módulos de integridad usan variables adicionales descritas en el README (sección "Sistema de Seguridad e Integridad"), entre ellas:

- `INTEGRITY_VALIDATION_ENABLED`
- `BLOCKCHAIN_VERIFICATION_ENABLED`
- `RISK_ASSESSMENT_INTERVAL`
- `ETHICS_GATE_ENABLED`
- `HMAC_SECRET_KEY`

Consulte esa sección para valores recomendados y descripción de flujos.

## 4. Base de datos

| Variable | Default | Descripción |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql://giovanniarangio@localhost:5432/axiom_meta4` | Cadena de conexión SQLAlchemy. |
| `ENABLE_DATABASE` | `true` | Permite desactivar completamente la capa de persistencia. |
| `DATABASE_POOL_SIZE` | `10` | Tamaño del pool de conexiones. |
| `DATABASE_MAX_OVERFLOW` | `20` | Conexiones extra permitidas. |
| `DATABASE_POOL_TIMEOUT` | `30` | Segundos antes de lanzar timeout al obtener conexión. |
| `DATABASE_POOL_RECYCLE` | `3600` | Reciclado del pool para evitar desconexiones prolongadas. |

## 5. Caché y Redis

| Variable | Default | Descripción |
| --- | --- | --- |
| `REDIS_URL` | `redis://localhost:6379` | Ubicación del servidor Redis. |
| `REDIS_DB` | `0` | Base de datos Redis a utilizar. |
| `REDIS_PASSWORD` | `None` | Password opcional. |
| `CACHE_TTL` | `300` | Tiempo de vida (segundos) de entradas cacheadas. |
| `ENABLE_REDIS_CACHE` | `True` | Permite desactivar Redis sin modificar código. |

## 6. Integraciones externas (LLM y APIs)

| Variable | Default | Descripción |
| --- | --- | --- |
| `ENABLE_LOCAL_LLM` | `true` | Activa el uso de modelos locales. |
| `LLM_BACKEND` | `ollama` | Backend por defecto (`ollama`, `mlx`, `transformers`). |
| `OLLAMA_API_URL` | `http://localhost:11434` | Endpoint de Ollama. |
| `OLLAMA_MODEL` | `falcon3:1b` | Modelo Ollama solicitado. |
| `HF_MODEL_ID` | `sshleifer/tiny-gpt2` | Modelo HuggingFace base. |
| `HF_MODEL_ID_SCIENCE` | `None` | Alternativa especializada para dominios científicos. |
| `MLX_MODEL_ID` | `mlx-community/SmolLM2-135M-Instruct-mlx` | Modelo MLX por defecto. |
| `LLM_MAX_NEW_TOKENS` | `384` | Longitud máxima de generación. |
| `LLM_TEMPERATURE` | `0.2` | Exploración vs determinismo. |
| `LLM_TRUST_REMOTE_CODE` | `true` | Permite usar repos que requieren `trust_remote_code`. |
| `HUGGINGFACE_API_KEY` | `None` | Token para endpoints que lo requieran. |
| `OPENAI_API_KEY` | `None` | Integración opcional con OpenAI. |
| `AGENT2_BASE_URL` | `http://localhost:8000` | URL del puente Agent 2. |

## 7. Límites computacionales

| Variable | Default | Descripción |
| --- | --- | --- |
| `MAX_COMPUTATION_TIME` | `30` | Tiempo máximo (segundos) para operaciones intensivas. |
| `MAX_PLOT_POINTS` | `10000` | Límite de puntos en gráficas. |
| `MAX_MATRIX_SIZE` | `1000` | Dimensión máxima de matrices procesadas. |
| `MAX_POLYNOMIAL_DEGREE` | `20` | Se restringen polinomios demasiado complejos. |
| `MAX_REQUEST_BYTES` | `5 MB` | Limita payloads de peticiones (multipart/form-data). |

## 8. Observabilidad

| Variable | Default | Descripción |
| --- | --- | --- |
| `ENABLE_OTEL` | `false` | Activa OpenTelemetry. |
| `OTEL_SERVICE_NAME` | `axiom-meta4` | Nombre del servicio reportado. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `None` | Endpoint OTLP (p.ej. `http://localhost:4317`). |
| `OTEL_TRACES_SAMPLER_ARG` | `1.0` | Ratio de muestreo. |
| `OTEL_INSTRUMENT_HTTPX` | `true` | Instrumenta peticiones HTTPX. |
| `ENABLE_PROM_SERVICE_METRICS` | `false` | Expone métricas adicionales por servicio. |

## 9. GPU y cómputo distribuido

| Variable | Default | Descripción |
| --- | --- | --- |
| `ENABLE_GPU` | `True` | Activa detección y uso de GPU. |
| `GPU_MEMORY_FRACTION` | `0.8` | Porcentaje máximo de memoria GPU utilizable. |
| `GPU_DEVICE` | `None` | Identificador explícito del dispositivo; autodetección si no se define. |
| `ENABLE_MPS` | `True` | Activa soporte Apple Metal Performance Shaders. |
| `ENABLE_CUDA` | `True` | Activa soporte CUDA. |
| `ENABLE_DISTRIBUTED` | `False` | Habilita ejecución distribuida. |
| `DISTRIBUTED_BACKEND` | `gloo` | Backend para torch.distributed (`gloo`, `nccl`, `mpi`). |
| `WORLD_SIZE` | `1` | Número total de nodos. |
| `RANK` | `0` | Identificador del proceso local. |
| `MASTER_ADDR` | `localhost` | Dirección del nodo maestro. |
| `MASTER_PORT` | `12355` | Puerto del nodo maestro. |

## 10. Async Tool Adapter y validaciones

Los servicios asincrónicos y de integridad utilizan variables adicionales recogidas en el README y en `app/async_tool_adapter.py`. Las más relevantes son:

| Variable | Módulo | Descripción |
| --- | --- | --- |
| `ASYNC_TOOL_MAX_CONCURRENT` | AsyncToolAdapter | Máximo de tareas simultáneas. |
| `ASYNC_TOOL_TIMEOUT` | AsyncToolAdapter | Timeout global de ejecución (segundos). |
| `ASYNC_TOOL_RETRY_ATTEMPTS` | AsyncToolAdapter | Reintentos por tarea. |
| `ASYNC_TOOL_FAIL_FAST` | AsyncToolAdapter | Corta ejecuciones en cascada ante fallos. |
| `TOOL_CACHE_ENABLED` | Tool Adapter Cache | Activa la caché LRU/TTL. |
| `TOOL_CACHE_MAX_SIZE` | Tool Adapter Cache | Límite de entradas cacheadas. |
| `TOOL_CACHE_TTL` | Tool Adapter Cache | Expiración de caché (segundos). |

## 11. Buenas prácticas operativas

1. **Versionar `.env` ejemplo**: mantén un archivo `config/.env.example` con variables críticas.
2. **Separar entornos**: producción debe usar secretos distintos para `SECRET_KEY`, `HMAC_SECRET_KEY`, claves API y credenciales de base de datos.
3. **Revisar límites**: ajusta `MAX_REQUEST_BYTES`, `MAX_COMPUTATION_TIME` y la concurrencia del adaptador asíncrono según la carga real.
4. **Observabilidad**: activa OpenTelemetry y `/metrics` en entornos que necesiten monitoreo continuo.

---

> ¿Falta alguna variable o servicio personalizado? Refuerza este documento creando subsecciones adicionales y enlazándolo desde el README para mantenerlo actualizado.
