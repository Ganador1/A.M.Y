# Router Registry de AXIOM ATLAS

El *router registry* automatiza la carga de más de 100 routers FastAPI agrupados por dominio. Esta guía explica cómo analizar, regenerar y validar `app/routers/router_registry.py` sin romper compatibilidad con la arquitectura legacy.

## 1. Componentes principales

| Elemento | Ubicación | Descripción |
| --- | --- | --- |
| Archivo generado | `app/routers/router_registry.py` | Tabla central de routers con prefijos y tags. |
| Script de utilidad | `scripts/utils/router_registry.py` | Herramientas para analizar y regenerar el archivo. |
| Config opcional | `config/router_registry.json` | Persistencia de configuraciones personalizadas. |

## 2. Comandos disponibles

Situarse en la raíz del repo y ejecutar:

```bash
cd .
python scripts/utils/router_registry.py --analyze   # Detecta routers actuales en main.py
python scripts/utils/router_registry.py --create    # Genera router_registry.py desde templates
python scripts/utils/router_registry.py --migrate   # Migra routers legacy al sistema modular
```

> El encabezado de `router_registry.py` mantiene un recordatorio abreviado (`python router_registry.py --create`). Esta guía añade la ruta completa del script.

## 3. Flujo recomendado para agregar un router

1. **Crear el router** en `app/routers/nombre.py` exportando `router = APIRouter(...)`.
2. **Actualizar plantillas o JSON** (opcional): agrega metadatos en `config/router_registry.json` si quieres documentar dependencias.
3. **Regenerar el registro**:

   ```bash
   python scripts/utils/router_registry.py --create
   ```

4. **Revisar diffs**: confirma que el bloque correspondiente aparece en `router_registry.py` con el prefijo correcto.
5. **Ejecutar pruebas**: corre smoke tests o import checks para asegurar que el router se carga (`pytest tests/smoke/test_advanced_modules.py -q`, por ejemplo).

## 4. Validación y compatibilidad

- `main_refactored.py` intenta registrar routers mediante `register_routers(app, router_config)`.
- Si el registro automático falla (ImportError, módulo ausente), se ejecuta `register_legacy_routers` como fallback.
- Mantén el archivo generado bajo control de versiones: cualquier edición manual será sobrescrita al volver a ejecutar el script.

## 5. Buenas prácticas

- **Atomicidad**: tras ejecutar `--create`, comitea los cambios del archivo generado junto con los nuevos routers.
- **Revisión de dependencias**: el script puede marcar dependencias faltantes; instálalas o documenta los requisitos.
- **Documentación**: enlaza nuevos routers en `docs/ROUTERS_INDEX.md` para mantener la documentación centralizada.
- **CI/CD**: considera añadir un trabajo que ejecute `python scripts/utils/router_registry.py --analyze` para detectar routers sin registrar.

Mantén este documento actualizado cuando se modifiquen rutas, scripts o convenciones del registro.
