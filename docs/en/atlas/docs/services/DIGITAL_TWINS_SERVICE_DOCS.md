> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="digital-twins-for-scientific-experiments-service"></a>
# Digital Twins for Scientific Experiments Service

<a id="alcance"></a>
## Scope
- Service: `DigitalTwinsService` (`app/services/advanced/digital_twins_service.py`).
- Purpose: Creation and management of digital replicas of experiments, equipment, and laboratory processes for real-time simulation and optimization.
- Implementation: Advanced physicochemical modeling system with sensor synchronization and predictive analytics.

<a id="capacidades"></a>
## Capabilities
- **Equipment Replicas**: Detailed modeling of instrumentation (e.g., spectrometers, sequencers) to predict failures and optimize usage.
- **Experiment Simulation**: Execution of "What-if" scenarios before performing the physical experiment.
- **Drift Detection**: Identification of discrepancies between the digital model and the physical process in real time.
- **Parameter Optimization**: Automatic suggestions to adjust experimental variables based on high-fidelity simulations.

<a id="tipos-de-gemelos-soportados"></a>
## Supported Twin Types
- **EQUIPMENT**: Replicas of laboratory hardware.
- **EXPERIMENT**: Models of complete experimental protocols.
- **PROCESS**: Workflows and reaction kinetics.
- **ENVIRONMENT**: Room conditions (temperature, humidity, vibration).

<a id="acciones-principales"></a>
## Main Actions

<a id="create_digital_twin"></a>
### `create_digital_twin`
Initializes a new digital twin from a specification.
- **Input**:
  - `name` (str): Unique identifier.
  - `twin_type` (TwinType): Category of the twin.
  - `parameters` (Dict): Initial state and constraints.
- **Output**:
  - `twin_id` (str): ID of the created twin.

<a id="run_simulation"></a>
### `run_simulation`
Runs a temporal simulation on the digital twin.
- **Input**:
  - `duration` (timedelta): Simulation time.
  - `interventions` (List): Planned changes during the simulation.
- **Output**:
  - `trajectory` (List[Dict]): Evolution of parameters over time.
  - `predictions` (List[PredictionResult]): Expected results.

<a id="synchronize_with_physical"></a>
### `synchronize_with_physical`
Updates the twin's state with real sensor data.
- **Input**:
  - `sensor_data` (List[SensorReading]): Current readings.
- **Output**:
  - `sync_status` (SyncStatus): Synchronization status.
  - `drift_metrics` (Dict): Magnitude of the detected deviation.

<a id="ejemplo-de-uso"></a>
## Usage Example
```python
from app.services.advanced.digital_twins_service import DigitalTwinsService, TwinType

service = DigitalTwinsService()
twin_id = service.create_digital_twin(
    name="Bioreactor_01_Twin",
    twin_type=TwinType.PROCESS,
    parameters={"temp": 37.0, "ph": 7.2, "agitation": 200}
)

<a id="simular-qué-pasa-si-subimos-la-agitación-a-300"></a>
# Simular qué pasa si subimos la agitación a 300
result = service.run_simulation(
    twin_id=twin_id,
    interventions=[{"time": "10m", "param": "agitation", "value": 300}]
)
```

<a id="pruebas"></a>
## Tests
- Run unit tests:
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_digital_twins_service.py`
