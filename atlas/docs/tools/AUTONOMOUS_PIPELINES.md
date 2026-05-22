# Sistema autónomo: pipelines y loops

## Qué es
AXIOM ATLAS incluye loops/pipelines autónomos para ejecutar ciclos de investigación por dominio (generar hipótesis → diseñar experimentos → ejecutar → evaluar → publicar).

## Ubicación en el código
- Pipelines por dominio: `app/autonomous/pipelines/`

Pipelines detectados:
- `astronomy_loop.py`
- `biology_loop.py`
- `chemistry_loop.py`
- `climate_loop.py`
- `engineering_loop.py`
- `materials_loop.py`
- `mathematics_loop.py`
- `medicine_loop.py`
- `neuroscience_loop.py`
- `quantum_loop.py`
- `enhanced_chemistry_loop.py`

## Cómo se usan
- Ejecución directa (scripts): muchos comandos viven en `scripts/run_*`.
- Ejecución vía routers: algunos routers llaman internamente a loops (ej. Chemistry enhanced).

## Recomendación de documentación por loop
Cada loop debería tener:
- Objetivo y criterio de parada
- Entradas (datasets/config)
- Salidas (artefactos y rutas)
- Dependencias opcionales (toolkits)
- Estrategia de evaluación y reproducibilidad

Si quieres, el siguiente paso es que genere un `README.md` corto por cada loop con ese formato.
