> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="reproducibility-service"></a>
# Reproducibility Service

<a id="alcance"></a>
## Scope
- Service: `ReproducibilityService` (`app/services/infrastructure/reproducibility_service.py`).
- Purpose: Ensure the reproducibility of experiments and scientific analyses by capturing the environment state, software versions, and execution metadata.

<a id="capacidades"></a>
## Capabilities
- **Environment Capture**: Records detailed information about the operating system, Python version, installed packages, and environment variables.
- **Execution Snapshot**: Creates a complete record of a specific execution, including inputs, outputs, and the environment state.
- **Integrity Verification**: Generates hashes to ensure that artifacts and code have not changed.

<a id="componentes-clave"></a>
## Key Components

<a id="environmentsnapshot"></a>
### `EnvironmentSnapshot`
Captures the current state of the system:
- **Platform**: OS, version, architecture.
- **Python**: Version, executable, path.
- **Packages**: Complete list of packages installed via `pip list`.
- **Env Vars**: Critical variables such as `PATH`, `PYTHONPATH`, `CUDA_VISIBLE_DEVICES`.
- **System**: CPU count, total/available memory.

<a id="reproducibilityservice"></a>
### `ReproducibilityService`
Manages the storage and retrieval of reproducibility records.
- **Persistence**: Stores records in `reproducibility_records/` in JSON format.
- **Identification**: Each record has a unique `record_id` (UUID).

<a id="acciones-soportadas-process_request"></a>
## Supported Actions (`process_request`)

<a id="create_record"></a>
### `create_record`
Creates a new reproducibility record for an experiment.
- **Input**:
  - `experiment_id` (str): Experiment ID.
  - `inputs` (Dict): Input data.
  - `outputs` (Dict): Results obtained.
  - `metadata` (Dict, optional): Additional information.
- **Output**:
  - `record_id` (str): ID of the created record.
  - `snapshot` (Dict): The captured environment snapshot.

<a id="get_record"></a>
### `get_record`
Retrieves an existing record.
- **Input**:
  - `record_id` (str): Record ID.

<a id="list_records"></a>
### `list_records`
Lists all available records for an experiment.
- **Input**:
  - `experiment_id` (str).

<a id="ejemplo-de-uso"></a>
## Usage Example
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

<a id="pruebas"></a>
## Tests
- Run unit tests:
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_reproducibility_service.py`
