# Model Management Service

## Alcance
- Servicio: `ModelManagementService` (`app/services/ml/model_management_service.py`).
- Propósito: Gestionar el ciclo de vida de los modelos de IA, incluyendo registro, listado, consulta y actualización de metadatos.
- Persistencia: Los datos se almacenan en un archivo JSON local en `data/models_registry.json`.

## Capacidades
- **Registro de Modelos**: Almacena información sobre nuevos modelos (nombre, versión, tarea, URI, metadatos).
- **Listado**: Recupera todos los modelos registrados.
- **Consulta**: Busca modelos específicos por nombre y versión.
- **Actualización**: Permite modificar los metadatos de un modelo existente.

## Acciones Soportadas (`process_request`)

### `register`
Registra un nuevo modelo en el sistema.
- **Entrada**:
  - `name` (str): Nombre del modelo.
  - `version` (str): Versión (ej. "1.0.0").
  - `task` (str): Tarea (ej. "text-generation", "classification").
  - `uri` (str, opcional): Ubicación del modelo (local o remota).
  - `metadata` (Dict, opcional): Información adicional.
- **Salida**:
  - `model` (Dict): El registro del modelo creado.

### `list`
Lista todos los modelos registrados.
- **Salida**:
  - `count` (int): Número total de modelos.
  - `models` (List[Dict]): Lista de registros de modelos.

### `get`
Obtiene los detalles de un modelo específico.
- **Entrada**:
  - `name` (str): Nombre del modelo.
  - `version` (str, opcional): Versión específica.
- **Salida**:
  - `models` (List[Dict]): Lista de modelos que coinciden con los criterios.

### `update`
Actualiza los metadatos de un modelo.
- **Entrada**:
  - `name` (str): Nombre del modelo.
  - `version` (str): Versión del modelo.
  - `metadata` (Dict): Nuevos metadatos a fusionar.

## Estructura de Datos (`ModelRecord`)
- `name`: Nombre único.
- `version`: Identificador de versión.
- `task`: Tipo de tarea de ML.
- `uri`: Ruta o URL del artefacto.
- `created_at`: Marca de tiempo de creación (ISO 8601).
- `metadata`: Diccionario flexible de metadatos.

## Ejemplo de Uso
```python
from app.services.ml.model_management_service import ModelManagementService

service = ModelManagementService()
await service.process_request({
    "action": "register",
    "name": "llama3-8b-science",
    "version": "1.0.0",
    "task": "scientific-reasoning"
})
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_model_management_service.py`
