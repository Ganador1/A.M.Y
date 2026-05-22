# Guía Avanzada de Desarrollo y Contribución

Esta guía complementa `CONTRIBUTING.md` con detalles operativos y prácticas recomendadas.

## 1. Filosofía

- Fail-fast en imports (script unificado)
- Tests rápidos primero; diferir E2E pesados
- Observabilidad mínima viable (logs + métricas si aplica)

## 2. Flujo Sugerido Diario

1. Actualiza rama desde `main`.
2. Ejecuta: `python verify_imports.py --skip-optional`.
3. Corre tests unitarios relevantes al módulo modificado.
4. Implementa cambios.
5. Corre verificación completa (`python verify_imports.py`).
6. Ejecuta seguridad: Bandit + pip-audit.
7. Abre PR con resumen conciso (qué / por qué / riesgos).

## 3. Estructura de Tests y Selección Rápida

| Tipo | Carpeta | Uso principal |
|------|---------|---------------|
| Unit | tests/unit | Lógica pura, utilidades, edge cases |
| Integration | tests/integration | Interacción entre servicios/clases |
| E2E | tests/e2e | Flujo completo usuario/sistema |
| Performance | tests/performance | Cuellos de botella específicos |
| Fuzz | tests/fuzz | Robustez ante entradas no esperadas |
| Contract | tests/contract | Interfaces estables externas |

## 4. Estrategia para Nuevos Servicios

1. Crear módulo en `app/services/` con dependencia mínima.
2. Añadir registro en `service_registry` si aplica.
3. Proveer test unitario base + integración ligera.
4. Añadir doc breve en `docs/services/` (si no existe formato reutilizable).

## 5. Ingestión de Datos

- Extender `BaseFetcher`.
- Retornar `FetchBatch` con items normalizados.
- Mantener id canónica con `canonical_id`.
- Persistir estado incremental con `save_state`.

## 6. Patrones de Errores y Logging

| Situación | Acción |
|-----------|--------|
| Excepción recuperable externa (timeout) | Retry con `retry_call` |
| Error lógico interno | Lanzar excepción clara |
| Estado inconsistente | Log + fallback seguro |

## 7. Seguridad y Hardening

- No interpolar directamente entrada externa en logs sensibles.
- Observar dependencias nuevas: ejecutar `pip-audit` inmediatamente.
- Evitar datos PII en trazas.

## 8. Próxima Integración de Cobertura

Se añadirá `.coveragerc`. Recomendado etiquetar tests costosos con marca pytest para exclusión selectiva.

## 9. Estilo y Calidad

- Mantener funciones < ~50 líneas donde sea razonable.
- Extraer bloques reutilizables.
- Documentar funciones públicas con docstring breve.

## 10. Validación de Importación Masiva

`verify_imports.py` permite detección temprana de:

- Errores de sintaxis
- Dependencias faltantes
- Side-effects peligrosos

## 11. Checklists de PR (Extendido)

- [ ] Import check (completo)
- [ ] Nuevos servicios documentados
- [ ] Tests: unidad + (integración si aplica)
- [ ] Sin vulnerabilidades añadidas
- [ ] Logs revisados
- [ ] No secrets

## 12. Roadmap Técnico (Extracto)

- Cobertura automatizada
- Métricas homogéneas
- Refactor de módulos legacy a subpaquetes temáticos

---
Fin de la guía extendida.
