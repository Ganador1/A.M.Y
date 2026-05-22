# Reproducibility Service

## Alcance
- Servicio: `ReproducibilityService` (`app/services/infrastructure/reproducibility_service.py`).
- Propósito: Garantizar la reproducibilidad de experimentos y análisis científicos capturando el estado del entorno, versiones de software y metadatos de ejecución.

## Capacidades
- **Captura de Entorno**: Registra información detallada sobre el sistema operativo, versión de Python, paquetes instalados y variables de entorno.
- **Snapshot de Ejecución**: Crea un registro completo de una ejecución específica, incluyendo entradas, salidas y el estado del entorno.
- **Verificación de Integridad**: Genera hashes para asegurar que los artefactos y el código no han cambiado.

## Componentes Clave

### `EnvironmentSnapshot`
Captura el estado actual del sistema:
- **Platform**: OS, versión, arquitectura.
- **Python**: Versión, ejecutable, path.
- **Packages**: Lista completa de paquetes instalados vía `pip list`.
- **Env Vars**: Variables críticas como `PATH`, `PYTHONPATH`, `CUDA_VISIBLE_DEVICES`.
- **System**: Conteo de CPUs, memoria total/disponible.

### `ReproducibilityService`
Gestiona el almacenamiento y recuperación de registros de reproducibilidad.
- **Persistencia**: Almacena registros en `reproducibility_records/` en formato JSON.
- **Identificación**: Cada registro tiene un `record_id` único (UUID).

## Acciones Soportadas (`process_request`)

### `create_record`
Crea un nuevo registro de reproducibilidad para un experimento.
- **Entrada**:
  - `experiment_id` (str): ID del experimento.
  - `inputs` (Dict): Datos de entrada.
  - `outputs` (Dict): Resultados obtenidos.
  - `metadata` (Dict, opcional): Información adicional.
- **Salida**:
  - `record_id` (str): ID del registro creado.
  - `snapshot` (Dict): El snapshot del entorno capturado.

### `get_record`
Recupera un registro existente.
- **Entrada**:
  - `record_id` (str): ID del registro.

### `list_records`
Lista todos los registros disponibles para un experimento.
- **Entrada**:
  - `experiment_id` (str).

## Ejemplo de Uso
```python
from app.services.infrastructure.reproducibility_service import ReproducibilityService

service = ReproducibilityService()
record = await service.process_request({
    "action": "create_record",
    "experiment_id": "EXP-2025-001",
    "inputs": {"param1": 10},
    "outputs": {"result": 0.95}
})
print(f"Record created: {record['record_id']}")
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_reproducibility_service.py`
