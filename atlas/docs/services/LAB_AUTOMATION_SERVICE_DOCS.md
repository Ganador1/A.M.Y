# Lab Automation Service

## Alcance
- Servicio: `LabAutomationService` (`app/domains/engineering/services/lab_automation_service.py`).
- Propósito: Orquestación de protocolos de laboratorio automatizados y gestión de instrumentación robótica.
- Implementación: Puente de abstracción sobre `LabEquipmentBridge` para ejecutar tareas complejas de forma asíncrona.

## Capacidades
- **Ejecución de Protocolos**: Automatización de flujos de trabajo estándar como PCR, ELISA y purificación de ácidos nucleicos.
- **Gestión de Muestras**: Seguimiento de la ubicación y estado de muestras en placas de 96/384 pocillos.
- **Control de Instrumentación**: Interfaz unificada para termocicladores, lectores de placas, centrífugas y brazos robóticos.
- **Simulación de Tiempos**: Estimación y simulación de la duración de protocolos para planificación de recursos.

## Protocolos Implementados

### `run_pcr_protocol`
Simula la preparación y ejecución de un programa de PCR.
- **Entrada**:
  - `samples` (List[Dict]): Lista de muestras con volumen y posición.
  - `program` (Dict): Ciclos, temperaturas y tiempos.
- **Salida**:
  - `status`: 'completed' o 'failed'.
  - `steps`: Detalle de cada paso ejecutado.

### `run_elisa_assay`
Ejecuta un ensayo ELISA completo incluyendo incubaciones y lectura final.
- **Entrada**:
  - `samples` (List[str]): IDs de las muestras.
  - `antibodies` (Dict): Especificación de anticuerpos primarios/secundarios.
  - `read_wavelength_nm` (int): Longitud de onda para la lectura de absorbancia.
- **Salida**:
  - `absorbance_data` (Dict): Resultados de la lectura del plate reader.

## Ejemplo de Uso
```python
from app.domains.engineering.services.lab_automation_service import LabAutomationService

service = LabAutomationService()
await service.initialize()

# Ejecutar un protocolo PCR
result = await service.run_pcr_protocol(
    samples=[{"id": "S1", "well": "A1", "volume": 25}],
    program={"cycles": 35, "annealing": {"temp": 58, "time": 30}}
)
print(f"Protocolo completado: {result['completed_at']}")
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_lab_automation_service.py`
