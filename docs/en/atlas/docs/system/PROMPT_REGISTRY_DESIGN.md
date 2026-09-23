> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="prompt-registry-layer-diseño-y-estado"></a>
# Prompt Registry Layer (Design and Status)

<a id="objetivo"></a>
## Objective
Centralize versioned management of prompt templates for scientific agents (hypothesis, review, refinement, literature search, peer review). It provides:
- Explicit versioning (name + version)
- Declared and validated variables
- Jinja2 rendering with `StrictUndefined`
- Render auditing (JSONL) + hash
- Lightweight in-memory cache to reduce IO
- Support for A/B testing by version

<a id="estado-actual-completado"></a>
## Current Status (Completed)
Key components:
- File: `app/services/prompting/prompt_registry_service.py`
- Dataclass `PromptRecord`
- Persistence: `data/prompt_registry.json`
- Render auditing: `data/prompt_renders.jsonl`
- Public API:
  - `register(name, version, template, variables, metadata)`
  - `list()`
  - `get(name, version=None)` (returns all versions if `version` is not passed)
  - `render(name, version, context)`
- Cache:
  - `_cache_list` (full list)
  - `_cache_get` (lookup by name:version)
  - `_cache_render` (template render + context keys)

<a id="ejemplo-de-uso"></a>
## Usage Example
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

<a id="ab-testing-integrado"></a>
## Integrated A/B Testing
Script: `examples/hypothesis_prompt_ab_test.py` compares:
- `static` (embedded prompt)
- `registry_v1`
- `registry_v2` (compact template with 3–5 variable requirement)

Metrics collected:
- Title / description length
- No. of variables
- Confidence (adjusted with soft penalty if v1 < 3 variables)
- Latency
- Diversity (1 - mean Jaccard over variable sets)
- Consistency of normalized titles
- Penalties applied

JSON output: `ab_hypothesis_report_<ts>.json`.

<a id="decisiones-de-diseño"></a>
## Design Decisions
| Area | Decision | Justification |
|------|----------|---------------|
| Template engine | Jinja2 StrictUndefined | Fails fast on missing variable |
| Persistence | Plain JSON | Simplicity and traceability in VCS |
| Auditing | Append-only JSONL | Low overhead, easy streaming parse |
| Cache | In-memory per process | Avoid repeated IO in intensive loops |
| Versioning | name + free-form version string | Flexibility (v1, v2, exp1, etc.) |
| Implicit registration | Auto-registration of v1 by default | Reduces initial friction |
| A/B | Separate script | Does not pollute core service |

<a id="limitaciones-actuales"></a>
## Current Limitations
- No semantic schema validation (only variable presence)
- No cache expiration / TTL
- No semantic tagging / prompt embedding
- No inspection UI
- No automatic rollback

<a id="métricas-observadas-ronda-reciente"></a>
## Observed Metrics (Recent Round)
- `registry_v1` faster (~-27% latency vs static) but fewer variables
- `registry_v2` higher confidence (+7% vs static) and +23% variables vs v1, at the cost of +30% v1 latency

<a id="roadmap-próximo-relacionado"></a>
## Upcoming Roadmap (Related)
| Priority | Item | Type |
|----------|------|------|
| P0 | Integrate more templates (literature_search, refinement, peer_review) | E |
| P1 | Tagging + embeddings (semantic prompt retrieval) | N |
| P1 | Bulk YAML export/import (migrations) | E |
| P2 | TTL & usage metrics (simple LRU) | E |
| P2 | Inspector UI/CLI (list, diff templates) | E |
| P2 | JSONSchema validation of variables | E |

<a id="integración-con-otros-módulos"></a>
## Integration with Other Modules
- `ScientificHypothesisAgent` uses `render()` when `use_prompt_registry=True` and supports `prompt_version` for A/B.
- Extensible to a future PolicyEngine for textual policies.

<a id="buenas-prácticas-recomendada"></a>
## Recommended Best Practices
1. Prefix names by domain: `hypothesis_generation`, `peer_review`, `lit_search`.
2. Keep variables few and semantic (`domain`, `research_question`, `context_data`).
3. Use metadata: `{ "purpose": "baseline", "safety": "low", "owner": "research_core" }`.
4. Record major changes as new versions (v3) instead of overwriting.

<a id="próximos-pasos-inmediatos"></a>
## Immediate Next Steps
- Document the full layer in the global README.
- Add additional base templates.
- Connect with a future semantic tool selection layer for adaptive prompts.

---
Last updated: auto-generated.
