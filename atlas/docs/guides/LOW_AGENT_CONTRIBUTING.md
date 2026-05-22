# Guía de Contribución - Agente Low

Estado: experimental

## Alcance del Rol

El agente Low se enfoca en:

- CI/CD base y ampliaciones.
- Documentación estructural y gobernanza operacional.
- Validación de manifests y reproducibilidad operacional (scripts, checks).
- Integridad de publicaciones (firmas, hashes, Merkle) – fases posteriores.

## Flujo de Trabajo

1. Crear rama: `feature/low-<descripcion-corta>`.
2. Abrir PR temprana (draft) con checklist.
3. Asegurar CI verde (lint, tests, seguridad, build, validación manifests).
4. Actualizar sección de progreso en `raodmap gpt5midhigh.md`.
5. Solicitar 1 revisor técnico + 1 revisor de documentación si aplica.

## Checklist PR (copiar en descripción)

- [ ] Título con Conventional Commit.
- [ ] CI verde (adjuntar ejecución o badge).
- [ ] Sin findings críticos bandit / pip-audit.
- [ ] Documentación actualizada (`docs/INDEX.md` si cambia estado/archivo).
- [ ] Manifest(s) validados (si aplica) – adjuntar extracto de reporte.
- [ ] Changelog (si hay cambio visible para usuarios).

## Estándares de Código (Scripts)

- Python 3.11+.
- Tipado estricto donde sea razonable (`from __future__ import annotations`).
- Evitar dependencias innecesarias; preferir stdlib.
- Salidas CLI en JSON para integración fácil.

## Validación de Manifests

Ejecutar local:

```bash
python scripts/validate_manifests.py --models-dir models --schema models/manifest.schema.json --output reports/manifest_validation_report.json
```

Si no hay schema todavía: se aceptan warnings, no errores.

## Política de Documentación

- Cada nuevo documento: añadir a `docs/INDEX.md` con estado inicial `experimental`.
- Cambiar a `stable` tras dos iteraciones sin modificaciones estructurales.
- Marcar `deprecated` y mantener por 1 release antes de eliminar.

## Errores Comunes a Evitar

| Situación | Acción Correctiva |
|-----------|-------------------|
| PR grande (>400 loc) | Dividir en PRs lógicas más pequeñas |
| Falta de actualización del roadmap | Añadir progreso en sección Progreso Agente Low |
| Falla silenciosa en scripts | Devolver código !=0 y JSON con `errors` |
| Modificar lógica core sin coordinación | Abrir issue de propuesta antes |

## Métricas de Calidad Internas

- Tiempo medio de revisión objetivo: < 24h.
- % PRs con checklist completo: > 95%.
- Scripts sin tipado parcial crítico (errores mypy) en fases avanzadas.

## Próximos Incrementos del Rol

- Integración de validación de manifests como job dedicado en CI.
- Gate obligatorio para manifests una vez schema se estabilice.
- Scripts de firma (Ed25519) y verificación Merkle.

(Actualizar este documento cuando cambien responsabilidades o se agreguen nuevos gates.)
