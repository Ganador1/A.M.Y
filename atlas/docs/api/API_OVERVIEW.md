# API Overview (Executive)

Esta página centraliza los endpoints principales. Para detalles exhaustivos usar la documentación autogenerada FastAPI (`/docs`) o los routers individuales.

## Categorías Clave

- Matemáticas Fundamentales (cálculo, álgebra, teoría de números, transformadas)
- Física y Simulación (PDE, cristalografía, química computacional, quantum básico)
- Ciencia de Datos y ML (series temporales, plausibility, experiment scheduler)
- Laboratorio Autónomo (workflow orchestration, reproducibilidad, integrity, sandbox)

## Índice Completo de Routers

Para una lista categorizada más amplia ver `ROUTERS_INDEX.md`.

## Ejemplos Representativos

| Dominio | Endpoint | Descripción |
|---------|----------|-------------|
| Topología | POST /api/topology/report | Reporte integrado (diagramas, invariantes) |
| Cálculo | POST /calculus/partial-derivative | Derivadas parciales multivariable |
| PDE | POST /pde/heat-1d | Simulación ecuación del calor |
| Plausibility | POST /api/plausibility/evaluate | Evaluar hipótesis científica |
| Scheduler | POST /api/scheduler/jobs | Crear trabajo científico |
| Reproducibilidad | POST /api/reproducibility/package | Paquete FAIR reproducible |
| Workflows | POST /api/workflows/execute | Ejecutar workflow científico |
| Conjeturas | POST /api/number-theory/conjectures/generate | Generar conjeturas |

## Autenticación

Todos los endpoints críticos requieren JWT (Authorization: Bearer `TOKEN`). Ver `auth.py`.

## Versionado

- Prefijos `/api` para servicios laboratorio y científicos
- Prefijos de routers matemáticos legados sin `/api` serán alineados en futuras versiones.

## Estados Especiales

Algunos endpoints devuelven mensajes de optimización no implementada en `llm_routing` y streaming pendiente en `agent2_bridge_service`.

---

Más detalles avanzados: ver `ADVANCED_SERVICES.md` y `MULTI_AGENT.md`.
