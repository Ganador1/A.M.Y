> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="configuración-central-de-axiom-atlas"></a>
# AXIOM ATLAS Central Configuration

This guide consolidates the environment variables and main options that control the platform's behavior. All variables have safe default values for development environments; in production it is recommended to set them explicitly.

<a id="1-servidor-y-api"></a>
## 1. Server and API

| Variable | Default | Description |
| --- | --- | --- |
| `HOST` (`APP_HOST`) | `0.0.0.0` | Address where to listen for HTTP requests. Alias: `HOST`. |
| `PORT` (`APP_PORT`) | `8002` | TCP port to expose the API. |
| `DEBUG` | `False` | Enables additional traces in FastAPI. |
| `RELOAD` | `False` | Automatically restarts the server upon detecting changes (development only). |
| `API_V1_PREFIX` | `/api` | Base prefix for versioned endpoints. |
| `DOCS_URL` | `/docs` | Path of the OpenAPI interface. |
| `REDOC_URL` | `/redoc` | Path of the ReDoc documentation. |

> These variables are defined in `app/core/config.py` and apply to both `main.py` and `main_refactored.py`.

<a id="2-cors"></a>
## 2. CORS

| Variable | Default | Description |
| --- | --- | --- |
| `CORS_ALLOW_ORIGINS` | List of local hosts | Comma-separated list of origins authorized for cross-origin requests. |

If the variable is not defined, the default set is used: `http://localhost`, `http://127.0.0.1`, and variants with port 8002.

<a id="3-seguridad"></a>
## 3. Security

| Variable | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | Generated on the fly | Key to sign tokens (HS256). Persist in production. |
| `ENABLE_AUTH_ROUTES` | `false` | Enables routes protected via Bearer token. |
| `API_BEARER_TOKEN` | `None` | Expected token when `ENABLE_AUTH_ROUTES=true`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token duration. |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | `10080` | Refresh token duration (7 days). |

<a id="seguridad-e-integridad-avanzada"></a>
### Advanced security and integrity

The integrity modules use additional variables described in the README (section "Security and Integrity System"), including:

- `INTEGRITY_VALIDATION_ENABLED`
- `BLOCKCHAIN_VERIFICATION_ENABLED`
- `RISK_ASSESSMENT_INTERVAL`
- `ETHICS_GATE_ENABLED`
- `HMAC_SECRET_KEY`

Consult that section for recommended values and flow descriptions.

<a id="4-base-de-datos"></a>
## 4. Database

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql://Ganador1@localhost:5432/axiom_meta4` | SQLAlchemy connection string. |
| `ENABLE_DATABASE` | `true` | Allows completely disabling the persistence layer. |
| `DATABASE_POOL_SIZE` | `10` | Connection pool size. |
| `DATABASE_MAX_OVERFLOW` | `20` | Extra connections allowed. |
| `DATABASE_POOL_TIMEOUT` | `30` | Seconds before throwing a timeout when obtaining a connection. |
| `DATABASE_POOL_RECYCLE` | `3600` | Pool recycling to avoid prolonged disconnections. |

<a id="5-caché-y-redis"></a>
## 5. Cache and Redis

| Variable | Default | Description |
| --- | --- | --- |
| `REDIS_URL` | `redis://localhost:6379` | Location of the Redis server. |
| `REDIS_DB` | `0` | Redis database to use. |
| `REDIS_PASSWORD` | `None` | Optional password. |
| `CACHE_TTL` | `300` | Time to live (seconds) of cached entries. |
| `ENABLE_REDIS_CACHE` | `True` | Allows disabling Redis without modifying code. |

<a id="6-integraciones-externas-llm-y-apis"></a>
## 6. External integrations (LLM and APIs)

| Variable | Default | Description |
| --- | --- | --- |
| `ENABLE_LOCAL_LLM` | `true` | Enables the use of local models. |
| `LLM_BACKEND` | `ollama` | Default backend (`ollama`, `mlx`, `transformers`). |
| `OLLAMA_API_URL` | `http://localhost:11434` | Ollama endpoint. |
| `OLLAMA_MODEL` | `falcon3:1b` | Requested Ollama model. |
| `HF_MODEL_ID` | `sshleifer/tiny-gpt2` | Base HuggingFace model. |
| `HF_MODEL_ID_SCIENCE` | `None` | Specialized alternative for scientific domains. |
| `MLX_MODEL_ID` | `mlx-community/SmolLM2-135M-Instruct-mlx` | Default MLX model. |
| `LLM_MAX_NEW_TOKENS` | `384` | Maximum generation length. |
| `LLM_TEMPERATURE` | `0.2` | Exploration vs determinism. |
| `LLM_TRUST_REMOTE_CODE` | `true` | Allows using repos that require `trust_remote_code`. |
| `HUGGINGFACE_API_KEY` | `None` | Token for endpoints that require it. |
| `OPENAI_API_KEY` | `None` | Optional integration with OpenAI. |
| `AGENT2_BASE_URL` | `http://localhost:8000` | URL of the Agent 2 bridge. |

<a id="7-límites-computacionales"></a>
## 7. Computational limits

| Variable | Default | Description |
| --- | --- | --- |
| `MAX_COMPUTATION_TIME` | `30` | Maximum time (seconds) for intensive operations. |
| `MAX_PLOT_POINTS` | `10000` | Limit of points in graphs. |
| `MAX_MATRIX_SIZE` | `1000` | Maximum dimension of processed matrices. |
| `MAX_POLYNOMIAL_DEGREE` | `20` | Overly complex polynomials are restricted. |
| `MAX_REQUEST_BYTES` | `5 MB` | Limits request payloads (multipart/form-data). |

<a id="8-observabilidad"></a>
## 8. Observability

| Variable | Default | Description |
| --- | --- | --- |
| `ENABLE_OTEL` | `false` | Enables OpenTelemetry. |
| `OTEL_SERVICE_NAME` | `axiom-meta4` | Name of the reported service. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `None` | OTLP endpoint (e.g. `http://localhost:4317`). |
| `OTEL_TRACES_SAMPLER_ARG` | `1.0` | Sampling ratio. |
| `OTEL_INSTRUMENT_HTTPX` | `true` | Instruments HTTPX requests. |
| `ENABLE_PROM_SERVICE_METRICS` | `false` | Exposes additional metrics per service. |

<a id="9-gpu-y-cómputo-distribuido"></a>
## 9. GPU and distributed computing

| Variable | Default | Description |
| --- | --- | --- |
| `ENABLE_GPU` | `True` | Enables GPU detection and usage. |
| `GPU_MEMORY_FRACTION` | `0.8` | Maximum percentage of usable GPU memory. |
| `GPU_DEVICE` | `None` | Explicit device identifier; autodetection if not defined. |
| `ENABLE_MPS` | `True` | Enables Apple Metal Performance Shaders support. |
| `ENABLE_CUDA` | `True` | Enables CUDA support. |
| `ENABLE_DISTRIBUTED` | `False` | Enables distributed execution. |
| `DISTRIBUTED_BACKEND` | `gloo` | Backend for torch.distributed (`gloo`, `nccl`, `mpi`). |
| `WORLD_SIZE` | `1` | Total number of nodes. |
| `RANK` | `0` | Identifier of the local process. |
| `MASTER_ADDR` | `localhost` | Address of the master node. |
| `MASTER_PORT` | `12355` | Port of the master node. |

<a id="10-async-tool-adapter-y-validaciones"></a>
## 10. Async Tool Adapter and validations

The asynchronous and integrity services use additional variables collected in the README and in `app/async_tool_adapter.py`. The most relevant are:

| Variable | Module | Description |
| --- | --- | --- |
| `ASYNC_TOOL_MAX_CONCURRENT` | AsyncToolAdapter | Maximum simultaneous tasks. |
| `ASYNC_TOOL_TIMEOUT` | AsyncToolAdapter | Global execution timeout (seconds). |
| `ASYNC_TOOL_RETRY_ATTEMPTS` | AsyncToolAdapter | Retries per task. |
| `ASYNC_TOOL_FAIL_FAST` | AsyncToolAdapter | Cuts cascading executions upon failures. |
| `TOOL_CACHE_ENABLED` | Tool Adapter Cache | Enables the LRU/TTL cache. |
| `TOOL_CACHE_MAX_SIZE` | Tool Adapter Cache | Limit of cached entries. |
| `TOOL_CACHE_TTL` | Tool Adapter Cache | Cache expiration (seconds). |

<a id="11-buenas-prácticas-operativas"></a>
## 11. Operational best practices

1. **Version `.env` example**: keep a `config/.env.example` file with critical variables.
2. **Separate environments**: production should use different secrets for `SECRET_KEY`, `HMAC_SECRET_KEY`, API keys, and database credentials.
3. **Review limits**: adjust `MAX_REQUEST_BYTES`, `MAX_COMPUTATION_TIME`, and the concurrency of the asynchronous adapter according to the actual load.
4. **Observability**: enable OpenTelemetry and `/metrics` in environments that need continuous monitoring.

---

> Is any variable or custom service missing? Strengthen this document by creating additional subsections and linking it from the README to keep it up to date.
