# Prompt Registry Layer (Diseño y Estado)

## Objetivo
Centralizar la gestión versionada de plantillas de prompts para agentes científicos (hipótesis, revisión, refinamiento, búsqueda de literatura, peer review). Proporciona:
- Versionado explícito (name + version)
- Variables declaradas y validadas
- Render Jinja2 con `StrictUndefined`
- Auditoría de renders (JSONL) + hash
- Cache in-memory ligera para reducir IO
- Soporte para A/B testing por versión

## Estado Actual (Completado)
Componentes clave:
- Archivo: `app/services/prompting/prompt_registry_service.py`
- Dataclass `PromptRecord`
- Persistencia: `data/prompt_registry.json`
- Auditoría renders: `data/prompt_renders.jsonl`
- API pública:
  - `register(name, version, template, variables, metadata)`
  - `list()`
  - `get(name, version=None)` (devuelve todas las versiones si no se pasa `version`)
  - `render(name, version, context)`
- Cache:
  - `_cache_list` (lista completa)
  - `_cache_get` (búsqueda por name:version)
  - `_cache_render` (render de plantilla + keys de contexto)

## Ejemplo de Uso
```python
from app.services.prompting.prompt_registry_service import prompt_registry_service

prompt_registry_service.register(
    name="hypothesis_generation",
    version="v1",
    template="Domain: {{ domain }}\nQuestion: {{ research_question }}",
    variables=["domain", "research_question"],
    metadata={"purpose": "baseline generation"}
)

rendered = prompt_registry_service.render(
    name="hypothesis_generation",
    version="v1",
    context={"domain": "materials_science", "research_question": "How do defects affect conductivity?"}
)
```

## A/B Testing Integrado
Script: `examples/hypothesis_prompt_ab_test.py` compara:
- `static` (prompt embebido)
- `registry_v1`
- `registry_v2` (plantilla compacta con requerimiento 3–5 variables)

Métricas recogidas:
- Longitud título / descripción
- Nº variables
- Confianza (ajustada con penalización suave si v1 < 3 variables)
- Latencia
- Diversidad (1 - mean Jaccard sobre sets de variables)
- Consistencia de títulos normalizados
- Penalizaciones aplicadas

Salida JSON: `ab_hypothesis_report_<ts>.json`.

## Decisiones de Diseño
| Área | Decisión | Justificación |
|------|----------|---------------|
| Motor templates | Jinja2 StrictUndefined | Falla rápido ante variable faltante |
| Persistencia | JSON plano | Sencillez y trazabilidad en VCS |
| Auditoría | JSONL append-only | Bajo overhead, fácil parse streaming |
| Cache | In-memory por proceso | Evitar IO repetido en loops intensivos |
| Versionado | name + version string libre | Flexibilidad (v1, v2, exp1, etc.) |
| Registro implícito | Auto-registro de v1 por defecto | Reduce fricción inicial |
| A/B | Script separado | No contamina servicio core |

## Limitaciones Actuales
- Sin validación de esquema semántico (solo presencia de var)
- No hay expiración / TTL de cache
- No existe tagging semántico / embedding de prompts
- Sin UI de inspección
- No hay rollback automático

## Métricas Observadas (Ronda reciente)
- `registry_v1` más rápido (~-27% latencia vs static) pero menos variables
- `registry_v2` mayor confianza (+7% vs static) y +23% variables vs v1, con coste de +30% latencia v1

## Roadmap Próximo (Relacionado)
| Prioridad | Item | Tipo |
|----------|------|------|
| P0 | Integrar más plantillas (literature_search, refinement, peer_review) | E |
| P1 | Tagging + embeddings (semantic retrieval de prompts) | N |
| P1 | YAML export/import masivo (migraciones) | E |
| P2 | TTL & métricas de uso (LRU simple) | E |
| P2 | UI/CLI inspector (listar, diff templates) | E |
| P2 | Validación JSONSchema de variables | E |

## Integración con Otros Módulos
- `ScientificHypothesisAgent` usa `render()` cuando `use_prompt_registry=True` y soporta `prompt_version` para A/B.
- Extensible a PolicyEngine futuro para políticas textuales.

## Buenas Prácticas Recomendada
1. Prefijar nombres por dominio: `hypothesis_generation`, `peer_review`, `lit_search`.
2. Mantener variables pocas y semánticas (`domain`, `research_question`, `context_data`).
3. Usar metadatos: `{ "purpose": "baseline", "safety": "low", "owner": "research_core" }`.
4. Registrar cambios mayores como nuevas versiones (v3) en lugar de sobrescribir.

## Próximos Pasos Inmediatos
- Documentar en README global la capa completa.
- Añadir plantillas adicionales base.
- Conectar con futura capa de selección semántica de herramientas para prompts adaptativos.

---
Última actualización: auto-generado.
