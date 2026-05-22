# Federated Learning Coordination Service

## Alcance
- Servicio: `FederatedLearningService` (`app/services/ml/federated_learning_service.py`).
- Propósito: Coordinación de entrenamiento distribuido preservando la privacidad de los datos (Privacy-Preserving ML).
- Implementación: Basado en el framework `Flower` (`flwr`) para orquestación de clientes federados.

## Capacidades
- **Entrenamiento Descentralizado**: Permite entrenar modelos globales sin que los datos salgan de los nodos locales.
- **Agregación de Pesos**: Implementa algoritmos para combinar actualizaciones de múltiples clientes.
- **Seguridad**: Soporta Differential Privacy y Secure Aggregation (opcional).
- **Evaluación Federada**: Evalúa el rendimiento del modelo global en datos locales distribuidos.

## Estrategias de Agregación
- **FedAvg (Federated Averaging)**: Promedio ponderado de los parámetros del modelo.
- **FedProx**: Variante de FedAvg que maneja la heterogeneidad de los sistemas y datos.
- **FedOpt**: Optimizadores federados adaptativos.

## Acciones Principales

### `start_federated_server`
Inicia el servidor de orquestación para una ronda de entrenamiento.
- **Entrada**:
  - `num_rounds` (int): Número de iteraciones de entrenamiento.
  - `min_clients` (int): Mínimo de clientes requeridos para iniciar.
  - `strategy` (str): Estrategia de agregación (default: 'fedavg').
- **Salida**:
  - `history` (Dict): Historial de métricas de pérdida y precisión por ronda.

### `evaluate_global_model`
Evalúa el modelo resultante en un conjunto de validación centralizado (si está disponible).
- **Entrada**:
  - `model_weights` (List): Pesos del modelo global.
- **Salida**:
  - `metrics` (Dict): Accuracy, Precision, Recall.

## Ejemplo de Configuración
```python
# Configuración del servidor federado
config = {
    "num_rounds": 5,
    "min_available_clients": 3,
    "fraction_fit": 1.0,
    "strategy": "FedProx"
}
service.start_federated_server(config)
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_federated_learning_service.py`
