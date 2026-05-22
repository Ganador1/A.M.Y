# Guía de API - Mathematics

## Overview
La API del dominio Mathematics se expone bajo el prefijo `/mathematics` e integra un router consolidado y sub-routers especializados. Las peticiones POST usan el modelo `BaseRequest` con el campo `data` para parámetros.

## Autenticación
- Usar autenticación estándar de AXIOM (token Bearer) para endpoints protegidos.

## Endpoints Consolidados
- `GET /mathematics/` — Overview del dominio.
- `GET /mathematics/status` — Estado de servicios.
- `GET /mathematics/capabilities` — Capacidades por servicio.
- `GET /mathematics/capabilities/{service_name}` — Capacidades de un servicio.
- `GET /mathematics/services` — Lista de servicios disponibles.
- `POST /mathematics/execute/{service_name}/{operation}` — Ejecuta operación.
- `POST /mathematics/batch-execute` — Ejecuta múltiples operaciones en paralelo.
- `POST /mathematics/optimize` — Optimización del sistema (background).
- `GET /mathematics/health` — Health check.
 - `GET /mathematics/statistics` — Métricas y estadísticas del dominio.
 - `POST /mathematics/cache/clear` — Limpia la cache del dominio.
 - `GET /mathematics/cache/info` — Información del estado de la cache.
 - `POST /mathematics/services/{service_name}/restart` — Reinicia un servicio específico.
 - `GET /mathematics/help` — Ayuda y guía rápida de endpoints.

## Sub-routers y Prefijos
- Calculus: `GET/POST /mathematics/...` (incluido sin prefijo adicional)
- SymPy avanzado: `/mathematics/advanced/...`
- SageMath: `/mathematics/sagemath/...`
- Julia: `/mathematics/julia/...`
- SymEngine: `/mathematics/symengine/...`
- Discovery Engine: `/mathematics/discovery/...`
- Topology: `/mathematics/topology/...`
- Quantum Math: `/mathematics/quantum/...`
- ML: `/mathematics/ml/...`
- Visualization: `/mathematics/visualization/...`
- AI matemático: `/mathematics/ai/...`
- Number Theory: `/mathematics/number-theory/...`
- Theorem Proving: `/mathematics/theorem-proving/...`
- Distributed: `/mathematics/distributed/...`

## Ejemplo de Request
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

## Response Estándar
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

## Errores
- 400 Bad Request: datos inválidos.
- 404 Not Found: servicio/operación no existe.
- 500 Internal Server Error: error interno (`MathematicsError`).

## Notas
- Para operaciones por lote, enviar `data.operations` como lista de `{service_name, operation, parameters}`.
- Consultar capacidades específicas con `GET /mathematics/capabilities/{service_name}`.
 - Endpoints de mantenimiento y soporte: ver sección de endpoints consolidados.