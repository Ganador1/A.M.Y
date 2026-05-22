# 📚 AXIOM Services Usage Guide

## Guía Completa de Uso de Servicios AXIOM

Esta guía proporciona ejemplos prácticos y documentación detallada para utilizar todos los servicios AXIOM integrados.

---

## 🚀 Inicio Rápido

### 1. Iniciar los Servicios
```bash
# Despliegue completo
./scripts/deploy.sh

# O manualmente
docker-compose up -d
```

### 2. Verificar Estado
```bash
# Health check general
curl http://localhost:8000/health

# Documentación interactiva
open http://localhost:8000/docs
```

### 3. Acceder a Monitoreo
- **API Docs:** http://localhost:8000/docs
- **Métricas:** http://localhost:8000/metrics
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000

---

## 🔍 Causal Discovery Service

### Descripción
Servicio para descubrimiento de relaciones causales en datos, estimación de efectos causales y análisis de intervenciones.

### Endpoints Principales

#### 1. Descubrir Estructura Causal
```bash
POST /api/causal-discovery/discover-structure
```

**Ejemplo de uso:**
```python
import requests
import pandas as pd

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

#### 2. Estimar Efecto Causal
```bash
POST /api/causal-discovery/estimate-effect
```

**Ejemplo de uso:**
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

### Casos de Uso
- Análisis de datos observacionales
- Identificación de variables confusoras
- Evaluación de intervenciones
- Análisis de políticas públicas

---

## 🤝 Federated Learning Service

### Descripción
Servicio para coordinar entrenamientos de aprendizaje federado, gestionar sesiones y agregar modelos de múltiples clientes.

### Endpoints Principales

#### 1. Iniciar Sesión Federada
```bash
POST /api/federated-learning/start
```

**Ejemplo de uso:**
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

#### 2. Unirse a Sesión
```bash
POST /api/federated-learning/join/{session_id}
```

**Ejemplo de uso:**
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

### Casos de Uso
- Investigación médica colaborativa
- Análisis financiero distribuido
- IoT y edge computing
- Preservación de privacidad de datos

---

## 🎲 Synthetic Data Service

### Descripción
Servicio para generar datos sintéticos que preservan las propiedades estadísticas de los datos originales mientras protegen la privacidad.

### Endpoints Principales

#### 1. Generar Datos Tabulares
```bash
POST /api/synthetic-data/generate/tabular
```

**Ejemplo de uso:**
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

#### 2. Generar Series Temporales
```bash
POST /api/synthetic-data/generate/time-series
```

**Ejemplo de uso:**
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

#### 3. Validar Privacidad
```bash
POST /api/synthetic-data/validate/privacy
```

### Casos de Uso
- Pruebas de software con datos realistas
- Compartir datasets sin comprometer privacidad
- Aumentar datasets pequeños
- Investigación y desarrollo

---

## 🧠 Multimodal Reasoning Service

### Descripción
Servicio para análisis de documentos multimodales, combinando texto, imágenes y otros tipos de datos usando modelos avanzados como Claude 3.5 y GPT-4V.

### Endpoints Principales

#### 1. Analizar Documento
```bash
POST /api/multimodal-reasoning/analyze-document
```

**Ejemplo de uso:**
```python
import base64

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

#### 2. Comparar Enfoques
```bash
POST /api/multimodal-reasoning/compare-approaches
```

**Ejemplo de uso:**
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

### Casos de Uso
- Análisis de documentos científicos
- Extracción de información de reportes
- Procesamiento de formularios
- Análisis de contenido multimedia

---

## ⚛️ Quantum Algorithms Service

### Descripción
Servicio para ejecutar algoritmos cuánticos híbridos, incluyendo QAOA y VQE, con soporte para múltiples backends cuánticos.

### Endpoints Principales

#### 1. Optimización QAOA
```bash
POST /api/quantum-algorithms/qaoa/optimize
```

**Ejemplo de uso:**
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

#### 2. VQE para Estado Fundamental
```bash
POST /api/quantum-algorithms/vqe/ground-state
```

**Ejemplo de uso:**
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

#### 3. Análisis de Ventaja Cuántica
```bash
POST /api/quantum-algorithms/quantum-advantage
```

### Casos de Uso
- Optimización combinatoria
- Química cuántica
- Problemas de satisfacibilidad
- Investigación en computación cuántica

---

## 📊 Monitoring Service

### Descripción
Servicio para monitoreo, métricas y observabilidad de toda la plataforma AXIOM.

### Endpoints Principales

#### 1. Health Check Completo
```bash
GET /api/monitoring/health
```

#### 2. Métricas del Sistema
```bash
GET /api/monitoring/metrics
```

#### 3. Estado de Servicios
```bash
GET /api/monitoring/services/status
```

**Ejemplo de uso:**
```python
# Verificar estado general
response = requests.get("http://localhost:8000/api/monitoring/health")
health_status = response.json()

# Obtener métricas específicas
response = requests.get("http://localhost:8000/api/monitoring/metrics?service=all")
metrics = response.json()

# Verificar servicio específico
response = requests.get("http://localhost:8000/api/monitoring/services/causal_discovery/status")
service_status = response.json()
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Configuración de la aplicación
ENVIRONMENT=production
LOG_LEVEL=INFO
WORKERS=4

# Base de datos
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017/axiom

# Servicios externos
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Monitoreo
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000
```

### Configuración de Logging
```python
import logging

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

## 🚨 Manejo de Errores

### Códigos de Error Comunes
- **400:** Bad Request - Datos de entrada inválidos
- **404:** Not Found - Recurso no encontrado
- **422:** Validation Error - Error de validación de datos
- **500:** Internal Server Error - Error interno del servidor
- **503:** Service Unavailable - Servicio temporalmente no disponible

### Ejemplo de Manejo de Errores
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

## 📈 Optimización de Rendimiento

### Mejores Prácticas
1. **Usar Cache:** Los servicios implementan cache automático para operaciones repetidas
2. **Batch Processing:** Enviar múltiples requests en lotes cuando sea posible
3. **Async Operations:** Usar endpoints asíncronos para operaciones largas
4. **Monitoreo:** Revisar métricas regularmente para identificar cuellos de botella

### Ejemplo de Uso Asíncrono
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

## 🔒 Seguridad

### Autenticación
```python
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

### Validación de Datos
Todos los servicios implementan validación automática usando Pydantic. Asegúrate de enviar datos en el formato correcto según la documentación de la API.

---

## 📞 Soporte y Troubleshooting

### Logs y Debugging
```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f axiom-api

# Ver logs en tiempo real
tail -f logs/axiom.log
```

### Comandos Útiles
```bash
# Reiniciar servicios
docker-compose restart

# Verificar estado de contenedores
docker-compose ps

# Acceder a contenedor para debugging
docker-compose exec axiom-api bash

# Verificar conectividad
curl -f http://localhost:8000/health
```

### Contacto
Para soporte técnico o reportar issues:
- Revisar logs en `logs/axiom.log`
- Verificar métricas en Grafana
- Consultar documentación de API en `/docs`

---

**Guía actualizada el 20 de septiembre, 2025**  
**AXIOM META 4 - Scientific Computing Platform**