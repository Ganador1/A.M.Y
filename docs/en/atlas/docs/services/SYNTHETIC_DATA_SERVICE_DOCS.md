> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="synthetic-data-generation-service"></a>
# Synthetic Data Generation Service

<a id="alcance"></a>
## Scope
- Service: `SyntheticDataService` (`app/services/ml/synthetic_data_service.py`).
- Purpose: Generation of high-fidelity synthetic data for scientific research, privacy preservation, and data augmentation.
- Implementation: Uses `SDV` (Synthetic Data Vault) and generative models such as `CTGAN` and `TVAE`.

<a id="capacidades"></a>
## Capabilities
- **Distribution Modeling**: Captures the correlations and statistical distributions of real data.
- **Privacy Preservation**: Generates data that does not contain identifiable information (PII) but maintains analytical utility.
- **Relational Data Handling**: Ability to synthesize databases with multiple tables and foreign keys.
- **Fidelity Evaluation**: Statistically compares synthetic data with the original.

<a id="modelos-soportados"></a>
## Supported Models
- **CTGAN**: Conditional Tabular GAN for categorical and continuous data.
- **TVAE**: Tabular Variational Autoencoder.
- **GaussianCopula**: Statistical model based on copulas for multivariate dependencies.

<a id="acciones-principales"></a>
## Main Actions

<a id="generate_synthetic_data"></a>
### `generate_synthetic_data`
Trains a model and generates a synthetic sample.
- **Input**:
  - `real_data` (pd.DataFrame): Training data.
  - `num_rows` (int): Number of rows to generate.
  - `model_type` (str): 'ctgan', 'tvae', or 'copula'.
- **Output**:
  - `synthetic_df` (pd.DataFrame): Generated data.
  - `report` (Dict): Quality and similarity report.

<a id="evaluate_synthetic_quality"></a>
### `evaluate_synthetic_quality`
Performs diagnostic tests on the generated data.
- **Input**:
  - `real_data`, `synthetic_data`.
- **Output**:
  - `score` (float): 0 to 1 score of overall fidelity.
  - `column_shapes` (Dict): Similarity per column.

<a id="ejemplo-de-uso"></a>
## Usage Example
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

<a id="pruebas"></a>
## Tests
- Run unit tests:
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_synthetic_data_service.py`
