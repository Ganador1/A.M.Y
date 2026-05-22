# Advanced Earth Sciences Service

## Alcance
- Servicio: `AdvancedEarthSciencesService` (`app/services/advanced/advanced_earth_sciences_service.py`).
- Propósito: Modelado avanzado de sistemas terrestres, incluyendo climatología, oceanografía y sismología.
- Implementación: Integración de modelos climáticos (CESM/CMIP6), análisis de datos históricos (NASA GISTEMP) y simulaciones geofísicas.

## Capacidades
- **Modelado Climático**: Simulación de escenarios de calentamiento global y evaluación de puntos de inflexión (Tipping Points).
- **Oceanografía Física**: Análisis de corrientes oceánicas, transporte vertical de nutrientes y acidificación de los océanos.
- **Sismología Avanzada**: Análisis de enjambres sísmicos, cálculo de peligrosidad sísmica y optimización de redes de monitoreo.
- **Análisis de Impacto**: Evaluación de efectos sectoriales (agricultura, recursos hídricos) y regionales del cambio climático.

## Módulos Principales

### Climatología
- `assess_tipping_points`: Evalúa la probabilidad de cruzar umbrales críticos (ej. colapso de la AMOC, deshielo del Ártico).
- `simulate_regional_analysis`: Proyecciones climáticas detalladas para coordenadas geográficas específicas.

### Oceanografía
- `analyze_ocean_currents`: Modelado de la circulación termohalina y transporte de calor.
- `estimate_primary_productivity`: Estimación de la producción biológica basada en niveles de clorofila y nutrientes.

### Sismología
- `analyze_seismic_swarms`: Identificación de patrones en secuencias de sismos de baja magnitud.
- `calculate_seismic_hazard`: Estimación de la aceleración máxima del suelo (PGA) para una región.

## Ejemplo de Uso
```python
from app.services.advanced.advanced_earth_sciences_service import AdvancedEarthSciencesService

service = AdvancedEarthSciencesService()

# Evaluar puntos de inflexión para un escenario de +2.5°C
result = await service.assess_tipping_points(
    scenario="SSP3-7.0",
    target_temp_increase=2.5
)
print(f"Riesgo de colapso AMOC: {result['amoc_collapse_probability']}%")
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_advanced_earth_sciences_service.py`
