# Digital Twins for Scientific Experiments Service

## Alcance
- Servicio: `DigitalTwinsService` (`app/services/advanced/digital_twins_service.py`).
- Propósito: Creación y gestión de réplicas digitales de experimentos, equipos y procesos de laboratorio para simulación y optimización en tiempo real.
- Implementación: Sistema avanzado de modelado físico-químico con sincronización de sensores y análisis predictivo.

## Capacidades
- **Réplicas de Equipos**: Modelado detallado de instrumentación (ej. espectrómetros, secuenciadores) para predecir fallos y optimizar uso.
- **Simulación de Experimentos**: Ejecución de "What-if" scenarios antes de realizar el experimento físico.
- **Detección de Deriva (Drift)**: Identificación de discrepancias entre el modelo digital y el proceso físico en tiempo real.
- **Optimización de Parámetros**: Sugerencias automáticas para ajustar variables experimentales basadas en simulaciones de alta fidelidad.

## Tipos de Gemelos Soportados
- **EQUIPMENT**: Réplicas de hardware de laboratorio.
- **EXPERIMENT**: Modelos de protocolos experimentales completos.
- **PROCESS**: Flujos de trabajo y cinéticas de reacción.
- **ENVIRONMENT**: Condiciones de sala (temperatura, humedad, vibración).

## Acciones Principales

### `create_digital_twin`
Inicializa un nuevo gemelo digital a partir de una especificación.
- **Entrada**:
  - `name` (str): Identificador único.
  - `twin_type` (TwinType): Categoría del gemelo.
  - `parameters` (Dict): Estado inicial y restricciones.
- **Salida**:
  - `twin_id` (str): ID del gemelo creado.

### `run_simulation`
Ejecuta una simulación temporal sobre el gemelo digital.
- **Entrada**:
  - `duration` (timedelta): Tiempo de simulación.
  - `interventions` (List): Cambios planeados durante la simulación.
- **Salida**:
  - `trajectory` (List[Dict]): Evolución de los parámetros en el tiempo.
  - `predictions` (List[PredictionResult]): Resultados esperados.

### `synchronize_with_physical`
Actualiza el estado del gemelo con datos reales de sensores.
- **Entrada**:
  - `sensor_data` (List[SensorReading]): Lecturas actuales.
- **Salida**:
  - `sync_status` (SyncStatus): Estado de la sincronización.
  - `drift_metrics` (Dict): Magnitud de la desviación detectada.

## Ejemplo de Uso
```python
from app.services.advanced.digital_twins_service import DigitalTwinsService, TwinType

service = DigitalTwinsService()
twin_id = service.create_digital_twin(
    name="Bioreactor_01_Twin",
    twin_type=TwinType.PROCESS,
    parameters={"temp": 37.0, "ph": 7.2, "agitation": 200}
)

# Simular qué pasa si subimos la agitación a 300
result = service.run_simulation(
    twin_id=twin_id,
    interventions=[{"time": "10m", "param": "agitation", "value": 300}]
)
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_digital_twins_service.py`
