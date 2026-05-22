# Advanced Services

Resumen de servicios científicos avanzados separados del README principal.

## Plausibility Service

- Evaluación multi-métrica (coherencia, evidencia, precedente, viabilidad, novedad)
- Ajuste incremental con nueva evidencia
- Entrenamiento ML condicional

## Experiment Scheduler

- Job states: pending, running, completed, failed
- Prioridad derivada de plausibility score
- Reintentos con backoff exponencial

## Reproducibility & Integrity

- Generación de paquetes FAIR autocontenidos
- Huellas SHA-256 y manifiestos
- Integridad de artefactos (router integrity)

## MLflow Registry

- Registro y versionado de modelos científicos
- Métricas y artefactos asociados

## Sandbox Executor

- Ejecución segura de código experimental (aislamiento lógico)
- Limitación de recursos futura (TODO: cgroups / namespaces)

## Data Versioning

- DVC scripts y ejemplos integrados (ver `examples/dvc_versioning_e2e.py`)

## Observability

- Métricas unificadas (contadores, gauges, eventos)
- Health endpoints compuestos

---

Para detalles sobre orquestación y multi-agente ver `WORKFLOW_ORCHESTRATOR.md` y `MULTI_AGENT.md`.
