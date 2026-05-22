# Tool Adapter Interface Specification

## Objetivo
Unificar invocación heterogénea de servicios científicos (modelos, simulaciones, optimizadores) bajo interfaz consistente, extensible y observable.

## Motivación
Actualmente cada servicio expone métodos ad-hoc. La ausencia de contrato dificulta:
- Orquestación dinámica
- Reintentos estandarizados
- Medición comparativa
- Registro uniforme

## Contrato Propuesto
```python
class ToolAdapter(Protocol):
    name: str
    version: str
    capabilities: list[str]

    async def prepare(self, **kwargs) -> None: ...
    async def invoke(self, payload: dict) -> dict: ...
    async def validate(self, output: dict) -> None: ...
    async def teardown(self) -> None: ...
```

## Ciclo de Vida
1. Registro en AdapterRegistry
2. prepare(): carga modelos / contexto
3. invoke(): ejecución atómica con timeout
4. validate(): checks dominio (shape, ranges, integridad)
5. teardown(): liberación recursos

## AdapterRegistry
| Función | Descripción |
|---------|-------------|
| register(adapter) | Alta dinámica |
| get(name) | Resolución |
| list() | Inspección |
| invoke(name, payload) | Atajo orquestado |

## Metadatos Ejecución
```
{
  "adapter": "segmentation_v1",
  "start_ts": "...",
  "duration_ms": 142,
  "status": "SUCCESS",
  "retries": 0,
  "hash_config": "..."
}
```

## Estrategia de Errores
| Tipo | Manejo |
|------|--------|
| Transitorio | Reintento exponencial |
| Validación | Falla inmediata |
| Timeout | Cancel + registro |
| Sistema | Escalado alerta |

## Observabilidad Integrada
- Métricas: adapter_latency_ms, adapter_failures_total, adapter_concurrency
- Logs: nivel INFO (inicio / fin), WARNING (retry), ERROR (fallo final)

## Seguridad
- Hash de payload antes y después (integridad)
- Lista blanca de adapters habilitados

## Extensibilidad
- Decoradores para políticas (cache, rate limit, tracing)
- Capabilities: ["GPU", "BAYES_OPT", "UQ", "SEGMENTATION"]

## Roadmap
| Fase | Entrega |
|------|---------|
| 1 | Interfaces + Registry básico |
| 2 | Decoradores (retry, timeout, tracing) |
| 3 | Métricas export + integración integrity pipeline |
| 4 | Generación automática docs adapters |
| 5 | Auto-benchmark comparativo |

## Ejemplo Simplificado
```python
class SegmentationAdapter:
    name = "segmentation_v1"
    version = "0.1.0"
    capabilities = ["SEGMENTATION", "GPU"]

    async def prepare(self):
        self.model = load_model()

    async def invoke(self, payload):
        img = payload["image"]
        mask = self.model.predict(img)
        return {"mask": mask}

    async def validate(self, output):
        assert "mask" in output

    async def teardown(self):
        del self.model
```

---
Especificación inicial completada.
