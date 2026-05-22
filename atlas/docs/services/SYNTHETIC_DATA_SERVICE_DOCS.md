# Synthetic Data Generation Service

## Alcance
- Servicio: `SyntheticDataService` (`app/services/ml/synthetic_data_service.py`).
- Propósito: Generación de datos sintéticos de alta fidelidad para investigación científica, preservación de privacidad y aumento de datos (Data Augmentation).
- Implementación: Utiliza `SDV` (Synthetic Data Vault) y modelos generativos como `CTGAN` y `TVAE`.

## Capacidades
- **Modelado de Distribuciones**: Captura las correlaciones y distribuciones estadísticas de datos reales.
- **Preservación de Privacidad**: Genera datos que no contienen información identificable (PII) pero mantienen la utilidad analítica.
- **Manejo de Datos Relacionales**: Capacidad para sintetizar bases de datos con múltiples tablas y claves foráneas.
- **Evaluación de Fidelidad**: Compara estadísticamente los datos sintéticos con los originales.

## Modelos Soportados
- **CTGAN**: Conditional Tabular GAN para datos categóricos y continuos.
- **TVAE**: Tabular Variational Autoencoder.
- **GaussianCopula**: Modelo estadístico basado en copulas para dependencias multivariadas.

## Acciones Principales

### `generate_synthetic_data`
Entrena un modelo y genera una muestra sintética.
- **Entrada**:
  - `real_data` (pd.DataFrame): Datos de entrenamiento.
  - `num_rows` (int): Cantidad de filas a generar.
  - `model_type` (str): 'ctgan', 'tvae', o 'copula'.
- **Salida**:
  - `synthetic_df` (pd.DataFrame): Datos generados.
  - `report` (Dict): Informe de calidad y similitud.

### `evaluate_synthetic_quality`
Realiza pruebas de diagnóstico sobre los datos generados.
- **Entrada**:
  - `real_data`, `synthetic_data`.
- **Salida**:
  - `score` (float): Puntuación de 0 a 1 de fidelidad general.
  - `column_shapes` (Dict): Similitud por columna.

## Ejemplo de Uso
```python
from app.services.synthetic_data_service import SyntheticDataService

service = SyntheticDataService()
synthetic_df, report = service.generate_synthetic_data(
    real_data=df_pacientes,
    num_rows=1000,
    model_type="ctgan"
)
print(f"Calidad de los datos: {report['overall_score']}")
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_synthetic_data_service.py`
