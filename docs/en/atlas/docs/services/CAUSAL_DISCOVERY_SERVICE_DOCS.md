> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="causal-discovery-engine-service"></a>
# Causal Discovery Engine Service

<a id="alcance"></a>
## Scope
- Service: `CausalDiscoveryService` (`app/services/ml/causal_discovery_service.py`).
- Purpose: Discovery of causal structures and analysis of cause-effect relationships in scientific datasets.
- Implementation: Uses specialized libraries such as `causal-learn` and `pgmpy` for advanced causal inference.

<a id="capacidades"></a>
## Capabilities
- **Structure Discovery**: Identifies directed acyclic graphs (DAGs) that represent causal relationships.
- **Effect Estimation**: Calculates the Average Causal Effect (ATE) between treatment and outcome variables.
- **Causal Inference**: Performs probabilistic queries on established causal models.
- **Hypothesis Validation**: Verifies whether the observed data are consistent with a proposed causal structure.

<a id="algoritmos-soportados"></a>
## Supported Algorithms
- **PC (Constraint-based)**: Based on conditional independence tests.
- **GES (Score-based)**: Greedy search in the graph space to maximize a fit score.
- **LiNGAM**: Non-Gaussian linear model to identify the direction of causality.
- **Backdoor Criterion**: For adjusting confounding variables (confounders).

<a id="acciones-principales"></a>
## Main Actions

<a id="discover_causal_structure"></a>
### `discover_causal_structure`
Discovers the causal graph from a DataFrame.
- **Input**:
  - `data` (pd.DataFrame): Observational data.
  - `algorithm` (str): 'pc', 'ges', or 'lingam'.
- **Output**:
  - `edges` (List[Tuple]): List of directed edges found.
  - `graph_stats` (Dict): Density and connectivity metrics.

<a id="estimate_causal_effect"></a>
### `estimate_causal_effect`
Estimates the impact of one variable on another.
- **Input**:
  - `treatment` (str): Intervention variable.
  - `outcome` (str): Outcome variable.
  - `confounders` (List[str]): Variables to control for.
- **Output**:
  - `ate` (float): Average Causal Effect.
  - `confidence_interval` (Tuple): Confidence interval of the effect.

<a id="ejemplo-de-uso"></a>
## Usage Example
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

<a id="pruebas"></a>
## Tests
- Run unit tests:
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_causal_discovery_service.py`
