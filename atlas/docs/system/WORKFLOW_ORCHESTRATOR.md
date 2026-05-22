# Workflow Orchestrator

Motor de ejecución de workflows científicos (v1.1).

## Conceptos

- Workflow: DAG lógico de tareas científicas
- Task: Unidad atómica (análisis, simulación, validación)
- Execution Context: Variables compartidas

## Capacidades

- Creación / listado / ejecución de workflows
- Persistencia de estados y resultados
- Validaciones de parámetros básicas
- (TODO) Detección de ciclos en `scientific_ui`
- (TODO) Planificación adaptativa según métricas

## Ejecución Básica

POST /api/workflows/execute -> devuelve `workflow_id` y estados

## Estados

- pending
- running
- completed
- failed

## Limitaciones Actuales

- Sin sistema de colas distribuido
- Sin backpressure inteligente
- Sin persistencia de grafo versionado

Ver `IMPLEMENTATION_STATUS.md` para progreso detallado.
