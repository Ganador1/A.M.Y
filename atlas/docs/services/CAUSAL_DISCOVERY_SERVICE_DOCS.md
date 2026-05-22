# Causal Discovery Engine Service

## Alcance
- Servicio: `CausalDiscoveryService` (`app/services/ml/causal_discovery_service.py`).
- Propósito: Descubrimiento de estructuras causales y análisis de relaciones de causa-efecto en conjuntos de datos científicos.
- Implementación: Utiliza librerías especializadas como `causal-learn` y `pgmpy` para inferencia causal avanzada.

## Capacidades
- **Descubrimiento de Estructura**: Identifica grafos acíclicos dirigidos (DAGs) que representan relaciones causales.
- **Estimación de Efectos**: Calcula el Efecto Causal Promedio (ATE) entre variables de tratamiento y resultado.
- **Inferencia Causal**: Realiza consultas probabilísticas sobre modelos causales establecidos.
- **Validación de Hipótesis**: Verifica si los datos observados son consistentes con una estructura causal propuesta.

## Algoritmos Soportados
- **PC (Constraint-based)**: Basado en pruebas de independencia condicional.
- **GES (Score-based)**: Búsqueda codiciosa en el espacio de grafos para maximizar una puntuación de ajuste.
- **LiNGAM**: Modelo lineal no gaussiano para identificar la dirección de la causalidad.
- **Backdoor Criterion**: Para el ajuste de variables confusoras (confounders).

## Acciones Principales

### `discover_causal_structure`
Descubre el grafo causal a partir de un DataFrame.
- **Entrada**:
  - `data` (pd.DataFrame): Datos observacionales.
  - `algorithm` (str): 'pc', 'ges', o 'lingam'.
- **Salida**:
  - `edges` (List[Tuple]): Lista de aristas dirigidas encontradas.
  - `graph_stats` (Dict): Métricas de densidad y conectividad.

### `estimate_causal_effect`
Estima el impacto de una variable sobre otra.
- **Entrada**:
  - `treatment` (str): Variable de intervención.
  - `outcome` (str): Variable de resultado.
  - `confounders` (List[str]): Variables a controlar.
- **Salida**:
  - `ate` (float): Average Causal Effect.
  - `confidence_interval` (Tuple): Intervalo de confianza del efecto.

## Ejemplo de Uso
```python
from app.services.causal_discovery_service import CausalDiscoveryService

service = CausalDiscoveryService()
result = service.estimate_causal_effect(
    data=my_dataframe,
    treatment="drug_dosage",
    outcome="recovery_rate",
    confounders=["age", "weight"]
)
print(f"Efecto estimado: {result['ate']}")
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_causal_discovery_service.py`
