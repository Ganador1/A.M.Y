> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="federated-learning-coordination-service"></a>
# Federated Learning Coordination Service

<a id="alcance"></a>
## Scope
- Service: `FederatedLearningService` (`app/services/ml/federated_learning_service.py`).
- Purpose: Coordination of distributed training while preserving data privacy (Privacy-Preserving ML).
- Implementation: Based on the `Flower` framework (`flwr`) for orchestration of federated clients.

<a id="capacidades"></a>
## Capabilities
- **Decentralized Training**: Allows training global models without data leaving local nodes.
- **Weight Aggregation**: Implements algorithms to combine updates from multiple clients.
- **Security**: Supports Differential Privacy and Secure Aggregation (optional).
- **Federated Evaluation**: Evaluates the performance of the global model on distributed local data.

<a id="estrategias-de-agregación"></a>
## Aggregation Strategies
- **FedAvg (Federated Averaging)**: Weighted average of model parameters.
- **FedProx**: Variant of FedAvg that handles heterogeneity of systems and data.
- **FedOpt**: Adaptive federated optimizers.

<a id="acciones-principales"></a>
## Main Actions

<a id="start_federated_server"></a>
### `start_federated_server`
Starts the orchestration server for a training round.
- **Input**:
  - `num_rounds` (int): Number of training iterations.
  - `min_clients` (int): Minimum number of clients required to start.
  - `strategy` (str): Aggregation strategy (default: 'fedavg').
- **Output**:
  - `history` (Dict): History of loss and accuracy metrics per round.

<a id="evaluate_global_model"></a>
### `evaluate_global_model`
Evaluates the resulting model on a centralized validation set (if available).
- **Input**:
  - `model_weights` (List): Weights of the global model.
- **Output**:
  - `metrics` (Dict): Accuracy, Precision, Recall.

<a id="ejemplo-de-configuración"></a>
## Configuration Example
```python
<a id="configuración-del-servidor-federado"></a>
# Configuración del servidor federado
config = {
    "num_rounds": 5,
    "min_available_clients": 3,
    "fraction_fit": 1.0,
    "strategy": "FedProx"
}
service.start_federated_server(config)
```

<a id="pruebas"></a>
## Tests
- Run unit tests:
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_federated_learning_service.py`
