# Guía de Contribución a AXIOM ATLAS

Esta guía resume el flujo de trabajo recomendado para aportar cambios de forma segura, reproducible y alineada con los principios del proyecto.

## 1. Entorno

1. Clona el repositorio.
2. Crea entorno virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. (Opcional) Instala dependencias adicionales para herramientas locales.

## 2. Verificaciones Rápidas Antes de Commits

| Verificación | Comando | Objetivo |
|--------------|---------|----------|
| Imports limpios | `python verify_imports.py --skip-optional` (rápido) luego sin flag | Asegura que no se rompan módulos |
| Tests unitarios clave | `pytest -q tests/unit` | Validar lógica base |
| Seguridad (Bandit) | `bandit -q -r app tests` | Detectar patrones inseguros |
| Dependencias (pip-audit) | `pip-audit -r requirements.audit.txt` | Vulnerabilidades conocidas |

## 3. Estrategia de Imports

El script `verify_imports.py` ahora incluye:

- Módulos core (`app/`)
- Módulos de ingestión (`ingestion/`)
- Scripts raíz críticos (`main`, `comprehensive_analysis`, `generate_final_report`)

Ejemplos:

```bash
python verify_imports.py --skip-optional  # rápido (solo core)
python verify_imports.py                  # completo
```

## 4. Tests

Clasificación existente:

- `tests/unit/` (rápidos, deterministas)
- `tests/integration/` (interacción cruzada de componentes)
- `tests/e2e/` (flujo extremo a extremo)
- `tests/performance/`, `tests/fuzz/`, `tests/contract/`

Reglas:

- Prioriza pruebas unitarias para nueva lógica.
- Aísla red/IO mediante mocks.
- Añade casos de regresión cuando corrijas un bug.

## 5. Estándares de Código

- Tipado progresivo (usa anotaciones en nuevo código).
- Evita dependencias innecesarias.
- Manejo robusto de errores: no silencies excepciones críticas.
- Logging: informativo, sin datos sensibles.

## 6. Seguridad y Calidad

- Bandit y pip-audit deben estar limpios antes de PR.
- No introducir claves/secrets en commits.
- Validar entradas externas (peticiones, archivos).

## 7. Flujo de Pull Request

1. Crear rama descriptiva: `feature/descripcion-corta` o `fix/area-breve`.
2. Ejecutar verificaciones (imports, tests, seguridad).
3. Acompañar cambios con documentación si altera comportamiento público.
4. Referenciar issues relacionados.

## 8. Cobertura (Futuro Cercano)

Se añadirá configuración `coverage.py`. Recomendado preparar tests con nombres claros y evitar lógica crítica sin pruebas.

## 9. Documentación

- Añade o actualiza guías bajo `docs/guides/`.
- Para arquitectura transversal usar `docs/system/`.
- Reportes extensos: mantener en secciones existentes.

## 10. Observabilidad y Depuración

- Activar modo debug via variable en settings si disponible.
- Registrar eventos clave y tiempos en nuevas integraciones.

## 11. Ingestión de Datos

- Nuevos fetchers deben extender `BaseFetcher` y devolver `FetchBatch`.
- Usar utilidades de `ingestion.utils` para hashing, cache y estado.

## 12. Checklist Pre-PR

- [ ] Imports core + opcionales OK
- [ ] Tests unitarios y relevantes pasan
- [ ] Sin vulnerabilidades críticas
- [ ] Documentación actualizada
- [ ] No secrets / credenciales
- [ ] Logs razonables

---
¡Gracias por contribuir a AXIOM ATLAS! 💡
