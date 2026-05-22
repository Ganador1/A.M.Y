# Puntos de Entrada de la API

Este documento describe los dos entrypoints disponibles en el repositorio y cómo utilizarlos según el escenario. La meta es facilitar la transición hacia la arquitectura modular refactorizada conservando compatibilidad con integraciones existentes.

## Resumen rápido

| Archivo | Estado | Uso recomendado |
| --- | --- | --- |
| `main_refactored.py` | ✅ Principal | Desarrollo activo, despliegues y nuevas integraciones |
| `main.py` | 🟡 Legado | Compatibilidad con scripts antiguos y pruebas específicas |

## `main_refactored.py` (entrypoint preferido)

- **Arquitectura**: Modular, con *router registry* y lazy loading.
- **Middleware**: Configurado desde `configure_middleware` con CORS, TrustedHosts y logging centralizado.
- **Ciclo de vida**: Utiliza `lifespan` asincrónico para inicializar orquestadores, base de datos y health checks periódicos.
- **Ventajas**:
  - Inicio 60-80% más rápido.
  - Memoria reducida (40-60%).
  - Registro automático de routers (más de 100) sin importaciones manuales.

### Cómo ejecutarlo

```bash
uvicorn main_refactored:app --host 0.0.0.0 --port 8002 --reload
```

> Ajusta host/puerto con las variables del archivo `.env` o parámetros CLI.

## `main.py` (modo legacy)

- **Arquitectura**: Registro manual de routers con importación exhaustiva.
- **Compatibilidad**: Mantiene nombres de ruta históricos y dependencias que todavía no migran al registry.
- **Cuándo usarlo**:
  - Validar integraciones que aún dependen de importaciones explícitas.
  - Comparar respuestas entre arquitecturas durante una migración progresiva.

### Ejecución

```bash
uvicorn main:app --host 0.0.0.0 --port 8002
```

No se recomienda habilitar `--reload` junto con la versión legacy en producción porque el tiempo de arranque es mayor.

## Roadmap sugerido

1. **Nuevas funcionalidades** → Desarrollar y registrar routers a través del *router registry* (ver `docs/router_registry.md`).
2. **Smoke tests y CI** → Actualizar scripts para apuntar a `main_refactored:app` por defecto.
3. **Desfase controlado** → Documentar claramente cualquier dependencia que requiera `main.py` y planificar su migración.
4. **Deprecación** → Cuando todos los routers estén registrados dinámicamente, se eliminará `main.py` o se convertirá en alias del entrypoint moderno.

Mantén este documento actualizado cada vez que cambie el proceso de arranque o el estado de los entrypoints.
