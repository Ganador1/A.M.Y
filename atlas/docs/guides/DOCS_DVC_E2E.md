# Ejemplo DVC End-to-End (sin DVC obligatorio)

Este ejemplo muestra cómo versionar un dataset pequeño con `DataVersioningService` y generar un reporte de procedencia sin requerir que `dvc` esté instalado (si está presente, lo usará; si no, continúa sin bloquear).

## Qué hace
- Crea un CSV pequeño en `data/`.
- Llama a `version_data` para registrar checksum, tamaño, metadatos y tags en `data/versions.json`.
- Genera un reporte de procedencia para ese `data_path` y lo guarda en `data/provenance_report.json`.

## Ejecutar
1) Activar entorno virtual y ejecutar el script:

```
source .venv/bin/activate
python examples/dvc_versioning_e2e.py
```

Salida esperada (resumen):
- Mensaje `OK DVC E2E`.
- JSON con información de versioning y `provenance_report`.
- Archivo `data/provenance_report.json` creado.

## Variables útiles
- `STRICT_DATA_PATHS=1` para forzar que los datos estén bajo `ALLOWED_DATA_ROOT` (por defecto `./data`).
- `ALLOWED_DATA_ROOT=./data` para definir raíz permitida.
- `MAX_VERSION_FILE_BYTES=524288000` (500MB) límite de tamaño por archivo.

## Notas
- Si `dvc` no está en el PATH, verás advertencias y se omitirá el tracking DVC, pero el versionado interno seguirá funcionando.
- Los historiales se almacenan en `data/versions.json`.
