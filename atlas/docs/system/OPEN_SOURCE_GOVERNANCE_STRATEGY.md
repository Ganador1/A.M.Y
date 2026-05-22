# Open Source Governance Strategy (Draft)

Estado: experimental

## Objetivos

Establecer un modelo de gobernanza transparente y sostenible para AXIOM META 4 que asegure calidad, seguridad, reproducibilidad científica y participación comunitaria responsable.

## Roles y Responsabilidades

| Rol | Responsabilidades Clave | Decisiones Permitidas |
|-----|-------------------------|------------------------|
| Maintainer Core | Revisión final de PRs críticas, releases, seguridad | Merge, release tags |
| Security Champion | Auditorías, respuesta a vulnerabilidades, políticas CSP | Parche rápido seguridad |
| Research Lead | Aceptación de pipelines científicos, criterios metodológicos | Aprobación de experimentos |
| Community Contributor | PRs no críticas, documentación, ejemplos | Sugerencias / issues |

## Flujos de Decisión

1. Propuesta (issue con etiqueta `proposal`).
2. Discusión (comentarios + label `rfc`).
3. Aprobación (consenso Maintainers + etiqueta `approved`).
4. Implementación (branch feature + PR con checklist).
5. Revisión final (al menos 2 revisores + passing CI).

## Reglas de Calidad

- 0 findings críticos (bandit / pip-audit) antes de merge.
- 100% nuevos endpoints con pruebas (unit o contract) + validación Pydantic.
- Cambios incompatibles requieren: (a) versión API nueva, (b) migración documentada.

## Ciclo de Release

| Fase | Duración | Criterio |
|------|----------|----------|
| Snapshot | continuo | Merge en main con CI verde |
| Release Candidate | 1 semana | Congelación de features + hardening |
| Stable | n/a | Tag firmado + changelog + hashes |

## Seguridad y Respuesta

- Ventana de divulgación responsable: 30 días.
- Canal privado para reportes (correo: security [at] ejemplo.org).
- Parche crítico < 72h y post-mortem documentado.

## Reproducibilidad y Ciencia

- Cada release estable incluye: manifests verificados, hashes, métricas clave y paquete reproducible.
- PROV graph exportable (JSON) + referencia MLflow.

## Transparencia Operativa

- Publicación de métricas agregadas (latencia p95, tasa de error, reproducibilidad) por release.
- Changelog estructurado (Added/Changed/Deprecated/Removed/Security).

## Resolución de Conflictos

- Escalamiento: contribuidor → maintainer → comité reducido (3 miembros) → arbitraje externo (opcional).

## Métricas de Gobernanza (Iniciales)

| Métrica | Objetivo |
|---------|----------|
| Tiempo medio de revisión PR | < 48h |
| % PRs con checklist completo | > 95% |
| Issues sin respuesta (>7d) | 0 |
| Reverts post-merge | < 2% |

## Próximos Pasos

1. Formalizar comité inicial de gobernanza.
2. Publicar plantillas de: issue, PR, propuesta de mejora (RFC ligera).
3. Añadir script de verificación de checklist en CI.

(Actualizar este documento cuando cambie la estructura de roles o métricas operativas.)
