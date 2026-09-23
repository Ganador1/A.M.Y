> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="guía-de-api---mathematics"></a>
# API Guide - Mathematics

<a id="overview"></a>
## Overview
The Mathematics domain API is exposed under the prefix `/mathematics` and integrates a consolidated router and specialized sub-routers. POST requests use the `BaseRequest` model with the `data` field for parameters.

<a id="autenticación"></a>
## Authentication
- Use standard AXIOM authentication (Bearer token) for protected endpoints.

<a id="endpoints-consolidados"></a>
## Consolidated Endpoints
- `GET /mathematics/` — Domain overview.
- `GET /mathematics/status` — Service status.
- `GET /mathematics/capabilities` — Capabilities by service.
- `GET /mathematics/capabilities/{service_name}` — Capabilities of a service.
- `GET /mathematics/services` — List of available services.
- `POST /mathematics/execute/{service_name}/{operation}` — Executes operation.
- `POST /mathematics/batch-execute` — Executes multiple operations in parallel.
- `POST /mathematics/optimize` — System optimization (background).
- `GET /mathematics/health` — Health check.
 - `GET /mathematics/statistics` — Domain metrics and statistics.
 - `POST /mathematics/cache/clear` — Clears the domain cache.
 - `GET /mathematics/cache/info` — Cache status information.
 - `POST /mathematics/services/{service_name}/restart` — Restarts a specific service.
 - `GET /mathematics/help` — Help and quick endpoint guide.

<a id="sub-routers-y-prefijos"></a>
## Sub-routers and Prefixes
- Calculus: `GET/POST /mathematics/...` (included without additional prefix)
- Advanced SymPy: `/mathematics/advanced/...`
- SageMath: `/mathematics/sagemath/...`
- Julia: `/mathematics/julia/...`
- SymEngine: `/mathematics/symengine/...`
- Discovery Engine: `/mathematics/discovery/...`
- Topology: `/mathematics/topology/...`
- Quantum Math: `/mathematics/quantum/...`
- ML: `/mathematics/ml/...`
- Visualization: `/mathematics/visualization/...`
- Mathematical AI: `/mathematics/ai/...`
- Number Theory: `/mathematics/number-theory/...`
- Theorem Proving: `/mathematics/theorem-proving/...`
- Distributed: `/mathematics/distributed/...`

<a id="ejemplo-de-request"></a>
## Request Example
`POST /mathematics/execute/optimization/linear_programming`
```json
{
  "data": {
    "objective": "minimize",
    "c": [1, 2, 3],
    "A": [[1, 0, 2], [0, 1, 1]],
    "b": [4, 3],
    "bounds": [[0, null], [0, null], [0, null]]
  }
}
```

<a id="response-estándar"></a>
## Standard Response
```json
{
  "success": true,
  "message": "Operation linear_programming executed on optimization",
  "data": {
    "result": { "x": [0, 3, 1], "value": 5.0 },
    "metadata": { "domain": "mathematics" }
  }
}
```

<a id="errores"></a>
## Errors
- 400 Bad Request: invalid data.
- 404 Not Found: service/operation does not exist.
- 500 Internal Server Error: internal error (`MathematicsError`).

<a id="notas"></a>
## Notes
- For batch operations, send `data.operations` as a list of `{service_name, operation, parameters}`.
- Query specific capabilities with `GET /mathematics/capabilities/{service_name}`.
 - Maintenance and support endpoints: see the consolidated endpoints section.
