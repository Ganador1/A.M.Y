> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="lab-automation-service"></a>
# Lab Automation Service

<a id="alcance"></a>
## Scope
- Service: `LabAutomationService` (`app/domains/engineering/services/lab_automation_service.py`).
- Purpose: Orchestration of automated laboratory protocols and management of robotic instrumentation.
- Implementation: Abstraction bridge over `LabEquipmentBridge` to execute complex tasks asynchronously.

<a id="capacidades"></a>
## Capabilities
- **Protocol Execution**: Automation of standard workflows such as PCR, ELISA, and nucleic acid purification.
- **Sample Management**: Tracking of sample location and status in 96/384-well plates.
- **Instrumentation Control**: Unified interface for thermocyclers, plate readers, centrifuges, and robotic arms.
- **Time Simulation**: Estimation and simulation of protocol duration for resource planning.

<a id="protocolos-implementados"></a>
## Implemented Protocols

<a id="run_pcr_protocol"></a>
### `run_pcr_protocol`
Simulates the preparation and execution of a PCR program.
- **Input**:
  - `samples` (List[Dict]): List of samples with volume and position.
  - `program` (Dict): Cycles, temperatures, and times.
- **Output**:
  - `status`: 'completed' or 'failed'.
  - `steps`: Detail of each executed step.

<a id="run_elisa_assay"></a>
### `run_elisa_assay`
Executes a complete ELISA assay including incubations and final reading.
- **Input**:
  - `samples` (List[str]): Sample IDs.
  - `antibodies` (Dict): Specification of primary/secondary antibodies.
  - `read_wavelength_nm` (int): Wavelength for absorbance reading.
- **Output**:
  - `absorbance_data` (Dict): Results of the plate reader reading.

<a id="ejemplo-de-uso"></a>
## Usage Example
```python
from app.domains.engineering.services.lab_automation_service import LabAutomationService

service = LabAutomationService()
await service.initialize()

<a id="ejecutar-un-protocolo-pcr"></a>
# Ejecutar un protocolo PCR
result = await service.run_pcr_protocol(
    samples=[{"id": "S1", "well": "A1", "volume": 25}],
    program={"cycles": 35, "annealing": {"temp": 58, "time": 30}}
)
print(f"Protocolo completado: {result['completed_at']}")
```

<a id="pruebas"></a>
## Tests
- Run unit tests:
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_lab_automation_service.py`
