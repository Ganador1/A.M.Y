> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="-axiom-services-usage-guide"></a>
# 📚 AXIOM Services Usage Guide

<a id="guía-completa-de-uso-de-servicios-axiom"></a>
## Complete Guide to Using AXIOM Services

This guide provides practical examples and detailed documentation for using all integrated AXIOM services.

---

<a id="-inicio-rápido"></a>
## 🚀 Quick Start

<a id="1-iniciar-los-servicios"></a>
### 1. Start the Services
```bash
<a id="despliegue-completo"></a>
# Despliegue completo
./scripts/deploy.sh

<a id="o-manualmente"></a>
# O manualmente
docker-compose up -d
```

<a id="2-verificar-estado"></a>
### 2. Check Status
```bash
<a id="health-check-general"></a>
# Health check general
curl http://localhost:8000/health

<a id="documentación-interactiva"></a>
# Documentación interactiva
open http://localhost:8000/docs
```

<a id="3-acceder-a-monitoreo"></a>
### 3. Access Monitoring
- **API Docs:** http://localhost:8000/docs
- **Metrics:** http://localhost:8000/metrics
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000

---

<a id="-causal-discovery-service"></a>
## 🔍 Causal Discovery Service

<a id="descripción"></a>
### Description
Service for discovering causal relationships in data, estimating causal effects, and analyzing interventions.

<a id="endpoints-principales"></a>
### Main Endpoints

<a id="1-descubrir-estructura-causal"></a>
#### 1. Discover Causal Structure
```bash
POST /api/causal-discovery/discover-structure
```

**Usage example:**
```python
import requests
import pandas as pd

<a id="datos-de-ejemplo"></a>
# Datos de ejemplo
data = {
    "data": [
        {"x1": 1.0, "x2": 2.0, "y": 3.0},
        {"x1": 2.0, "x2": 3.0, "y": 5.0},
        {"x1": 3.0, "x2": 1.0, "y": 4.0}
    ],
    "algorithm": "pc",
    "significance_level": 0.05
}

response = requests.post(
    "http://localhost:8000/api/causal-discovery/discover-structure",
    json=data
)
print(response.json())
```

<a id="2-estimar-efecto-causal"></a>
#### 2. Estimate Causal Effect
```bash
POST /api/causal-discovery/estimate-effect
```

**Usage example:**
```python
effect_data = {
    "data": data["data"],
    "treatment": "x1",
    "outcome": "y",
    "confounders": ["x2"],
    "method": "linear_regression"
}

response = requests.post(
    "http://localhost:8000/api/causal-discovery/estimate-effect",
    json=effect_data
)
```

<a id="casos-de-uso"></a>
### Use Cases
- Analysis of observational data
- Identification of confounding variables
- Evaluation of interventions
- Public policy analysis

---

<a id="-federated-learning-service"></a>
## 🤝 Federated Learning Service

<a id="descripción-1"></a>
### Description
Service for coordinating federated learning trainings, managing sessions, and aggregating models from multiple clients.

<a id="endpoints-principales-1"></a>
### Main Endpoints

<a id="1-iniciar-sesión-federada"></a>
#### 1. Start Federated Session
```bash
POST /api/federated-learning/start
```

**Usage example:**
```python
session_config = {
    "session_name": "medical_research_fl",
    "model_type": "neural_network",
    "num_rounds": 10,
    "min_clients": 3,
    "strategy": "fedavg",
    "dataset_config": {
        "name": "medical_data",
        "features": 100,
        "classes": 2
    }
}

response = requests.post(
    "http://localhost:8000/api/federated-learning/start",
    json=session_config
)
session_id = response.json()["session_id"]
```

<a id="2-unirse-a-sesión"></a>
#### 2. Join Session
```bash
POST /api/federated-learning/join/{session_id}
```

**Usage example:**
```python
client_config = {
    "client_id": "hospital_a",
    "data_size": 1000,
    "capabilities": ["gpu", "high_memory"]
}

response = requests.post(
    f"http://localhost:8000/api/federated-learning/join/{session_id}",
    json=client_config
)
```

<a id="casos-de-uso-1"></a>
### Use Cases
- Collaborative medical research
- Distributed financial analysis
- IoT and edge computing
- Data privacy preservation

---

<a id="-synthetic-data-service"></a>
## 🎲 Synthetic Data Service

<a id="descripción-2"></a>
### Description
Service for generating synthetic data that preserves the statistical properties of the original data while protecting privacy.

<a id="endpoints-principales-2"></a>
### Main Endpoints

<a id="1-generar-datos-tabulares"></a>
#### 1. Generate Tabular Data
```bash
POST /api/synthetic-data/generate/tabular
```

**Usage example:**
```python
tabular_request = {
    "original_data": [
        {"age": 25, "income": 50000, "education": "bachelor"},
        {"age": 35, "income": 75000, "education": "master"},
        {"age": 45, "income": 90000, "education": "phd"}
    ],
    "num_samples": 1000,
    "algorithm": "ctgan",
    "privacy_level": "high"
}

response = requests.post(
    "http://localhost:8000/api/synthetic-data/generate/tabular",
    json=tabular_request
)
synthetic_data = response.json()["synthetic_data"]
```

<a id="2-generar-series-temporales"></a>
#### 2. Generate Time Series
```bash
POST /api/synthetic-data/generate/time-series
```

**Usage example:**
```python
timeseries_request = {
    "original_data": {
        "timestamps": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "values": [100, 105, 98]
    },
    "num_samples": 365,
    "algorithm": "timegan",
    "seasonality": "daily"
}

response = requests.post(
    "http://localhost:8000/api/synthetic-data/generate/time-series",
    json=timeseries_request
)
```

<a id="3-validar-privacidad"></a>
#### 3. Validate Privacy
```bash
POST /api/synthetic-data/validate/privacy
```

<a id="casos-de-uso-2"></a>
### Use Cases
- Software testing with realistic data
- Sharing datasets without compromising privacy
- Augmenting small datasets
- Research and development

---

<a id="-multimodal-reasoning-service"></a>
## 🧠 Multimodal Reasoning Service

<a id="descripción-3"></a>
### Description
Service for analyzing multimodal documents, combining text, images, and other data types using advanced models such as Claude 3.5 and GPT-4V.

<a id="endpoints-principales-3"></a>
### Main Endpoints

<a id="1-analizar-documento"></a>
#### 1. Analyze Document
```bash
POST /api/multimodal-reasoning/analyze-document
```

**Usage example:**
```python
import base64

<a id="cargar-imagen"></a>
# Cargar imagen
with open("document.pdf", "rb") as f:
    document_data = base64.b64encode(f.read()).decode()

analysis_request = {
    "document_data": document_data,
    "document_type": "pdf",
    "analysis_type": "comprehensive",
    "extract_tables": True,
    "extract_figures": True,
    "language": "es"
}

response = requests.post(
    "http://localhost:8000/api/multimodal-reasoning/analyze-document",
    json=analysis_request
)
analysis = response.json()
```

<a id="2-comparar-enfoques"></a>
#### 2. Compare Approaches
```bash
POST /api/multimodal-reasoning/compare-approaches
```

**Usage example:**
```python
comparison_request = {
    "document_data": document_data,
    "approaches": ["claude", "gpt4v", "local_model"],
    "comparison_criteria": ["accuracy", "speed", "detail"]
}

response = requests.post(
    "http://localhost:8000/api/multimodal-reasoning/compare-approaches",
    json=comparison_request
)
```

<a id="casos-de-uso-3"></a>
### Use Cases
- Analysis of scientific documents
- Information extraction from reports
- Form processing
- Multimedia content analysis

---

<a id="-quantum-algorithms-service"></a>
## ⚛️ Quantum Algorithms Service

<a id="descripción-4"></a>
### Description
Service for running hybrid quantum algorithms, including QAOA and VQE, with support for multiple quantum backends.

<a id="endpoints-principales-4"></a>
### Main Endpoints

<a id="1-optimización-qaoa"></a>
#### 1. QAOA Optimization
```bash
POST /api/quantum-algorithms/qaoa/optimize
```

**Usage example:**
```python
qaoa_request = {
    "problem_hamiltonian": {
        "ZZ": [[0, 1], [1, 2]],  # Conexiones del grafo
        "Z": [0, 1, 2]           # Términos individuales
    },
    "num_qubits": 3,
    "num_layers": 2,
    "optimizer": "COBYLA",
    "max_iterations": 100,
    "backend": "qiskit_simulator"
}

response = requests.post(
    "http://localhost:8000/api/quantum-algorithms/qaoa/optimize",
    json=qaoa_request
)
result = response.json()
print(f"Optimal parameters: {result['optimal_parameters']}")
print(f"Optimal value: {result['optimal_value']}")
```

<a id="2-vqe-para-estado-fundamental"></a>
#### 2. VQE for Ground State
```bash
POST /api/quantum-algorithms/vqe/ground-state
```

**Usage example:**
```python
vqe_request = {
    "molecular_hamiltonian": {
        "H2": {  # Molécula de hidrógeno
            "geometry": [["H", [0.0, 0.0, 0.0]], ["H", [0.0, 0.0, 0.74]]],
            "basis": "sto-3g"
        }
    },
    "num_qubits": 4,
    "ansatz_type": "hardware_efficient",
    "optimizer": "SPSA",
    "backend": "pennylane"
}

response = requests.post(
    "http://localhost:8000/api/quantum-algorithms/vqe/ground-state",
    json=vqe_request
)
```

<a id="3-análisis-de-ventaja-cuántica"></a>
#### 3. Quantum Advantage Analysis
```bash
POST /api/quantum-algorithms/quantum-advantage
```

<a id="casos-de-uso-4"></a>
### Use Cases
- Combinatorial optimization
- Quantum chemistry
- Satisfiability problems
- Research in quantum computing

---

<a id="-monitoring-service"></a>
## 📊 Monitoring Service

<a id="descripción-5"></a>
### Description
Service for monitoring, metrics, and observability of the entire AXIOM platform.

<a id="endpoints-principales-5"></a>
### Main Endpoints

<a id="1-health-check-completo"></a>
#### 1. Full Health Check
```bash
GET /api/monitoring/health
```

<a id="2-métricas-del-sistema"></a>
#### 2. System Metrics
```bash
GET /api/monitoring/metrics
```

<a id="3-estado-de-servicios"></a>
#### 3. Service Status
```bash
GET /api/monitoring/services/status
```

**Usage example:**
```python
<a id="verificar-estado-general"></a>
# Verificar estado general
response = requests.get("http://localhost:8000/api/monitoring/health")
health_status = response.json()

<a id="obtener-métricas-específicas"></a>
# Obtener métricas específicas
response = requests.get("http://localhost:8000/api/monitoring/metrics?service=all")
metrics = response.json()

<a id="verificar-servicio-específico"></a>
# Verificar servicio específico
response = requests.get("http://localhost:8000/api/monitoring/services/causal_discovery/status")
service_status = response.json()
```

---

<a id="-configuración-avanzada"></a>
## 🔧 Advanced Configuration

<a id="variables-de-entorno"></a>
### Environment Variables
```bash
<a id="configuración-de-la-aplicación"></a>
# Configuración de la aplicación
ENVIRONMENT=production
LOG_LEVEL=INFO
WORKERS=4

<a id="base-de-datos"></a>
# Base de datos
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017/axiom

<a id="servicios-externos"></a>
# Servicios externos
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

<a id="monitoreo"></a>
# Monitoreo
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000
```

<a id="configuración-de-logging"></a>
### Logging Configuration
```python
import logging

<a id="configurar-logging-para-servicios-axiom"></a>
# Configurar logging para servicios AXIOM
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/axiom.log'),
        logging.StreamHandler()
    ]
)
```

---

<a id="-manejo-de-errores"></a>
## 🚨 Error Handling

<a id="códigos-de-error-comunes"></a>
### Common Error Codes
- **400:** Bad Request - Invalid input data
- **404:** Not Found - Resource not found
- **422:** Validation Error - Data validation error
- **500:** Internal Server Error - Internal server error
- **503:** Service Unavailable - Service temporarily unavailable

<a id="ejemplo-de-manejo-de-errores"></a>
### Error Handling Example
```python
import requests
from requests.exceptions import RequestException

def call_axiom_service(endpoint, data):
    try:
        response = requests.post(f"http://localhost:8000{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        if response.status_code == 422:
            print(f"Validation error: {response.json()}")
        elif response.status_code == 503:
            print("Service temporarily unavailable, please retry later")
        else:
            print(f"HTTP error: {e}")
    
    except RequestException as e:
        print(f"Request failed: {e}")
    
    return None
```

---

<a id="-optimización-de-rendimiento"></a>
## 📈 Performance Optimization

<a id="mejores-prácticas"></a>
### Best Practices
1. **Use Cache:** Services implement automatic caching for repeated operations
2. **Batch Processing:** Send multiple requests in batches when possible
3. **Async Operations:** Use asynchronous endpoints for long operations
4. **Monitoring:** Review metrics regularly to identify bottlenecks

<a id="ejemplo-de-uso-asíncrono"></a>
### Asynchronous Usage Example
```python
import asyncio
import aiohttp

async def async_axiom_call(session, endpoint, data):
    async with session.post(f"http://localhost:8000{endpoint}", json=data) as response:
        return await response.json()

async def batch_processing():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(10):
            data = {"batch_id": i, "data": f"sample_{i}"}
            task = async_axiom_call(session, "/api/synthetic-data/generate/tabular", data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
```

---

<a id="-seguridad"></a>
## 🔒 Security

<a id="autenticación"></a>
### Authentication
```python
<a id="ejemplo-con-token-de-autenticación"></a>
# Ejemplo con token de autenticación
headers = {
    "Authorization": "Bearer your_jwt_token_here",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8000/api/causal-discovery/discover-structure",
    json=data,
    headers=headers
)
```

<a id="validación-de-datos"></a>
### Data Validation
All services implement automatic validation using Pydantic. Make sure to send data in the correct format according to the API documentation.

---

<a id="-soporte-y-troubleshooting"></a>
## 📞 Support and Troubleshooting

<a id="logs-y-debugging"></a>
### Logs and Debugging
```bash
<a id="ver-logs-de-todos-los-servicios"></a>
# Ver logs de todos los servicios
docker-compose logs -f

<a id="ver-logs-de-un-servicio-específico"></a>
# Ver logs de un servicio específico
docker-compose logs -f axiom-api

<a id="ver-logs-en-tiempo-real"></a>
# Ver logs en tiempo real
tail -f logs/axiom.log
```

<a id="comandos-útiles"></a>
### Useful Commands
```bash
<a id="reiniciar-servicios"></a>
# Reiniciar servicios
docker-compose restart

<a id="verificar-estado-de-contenedores"></a>
# Verificar estado de contenedores
docker-compose ps

<a id="acceder-a-contenedor-para-debugging"></a>
# Acceder a contenedor para debugging
docker-compose exec axiom-api bash

<a id="verificar-conectividad"></a>
# Verificar conectividad
curl -f http://localhost:8000/health
```

<a id="contacto"></a>
### Contact
For technical support or to report issues:
- Review logs at `logs/axiom.log`
- Check metrics in Grafana
- Consult the API documentation at `/docs`

---

**Guide updated on 20 September, 2025**  
**AXIOM META 4 - Scientific Computing Platform**
