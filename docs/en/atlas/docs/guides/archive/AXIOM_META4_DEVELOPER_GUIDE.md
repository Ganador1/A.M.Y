> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="-axiom-meta-4---guía-de-integración-para-desarrolladores"></a>
# 🛠️ AXIOM META 4 - INTEGRATION GUIDE FOR DEVELOPERS

<a id="-objetivo"></a>
## 🎯 OBJECTIVE

This guide provides detailed instructions for integrating and using the **AXIOM META 4** tools in the project's development workflow.

---

<a id="-quick-start"></a>
## 📋 QUICK START

<a id="1-instalación-rápida"></a>
### 1. **Quick Installation**
```bash
<a id="opción-a-script-de-automatización"></a>
# Opción A: Script de automatización
./meta4_automation.sh install

<a id="opción-b-script-directo"></a>
# Opción B: Script directo
bash install_meta4_dependencies.sh

<a id="opción-c-manual"></a>
# Opción C: Manual
source .venv/bin/activate
pip install pymatgen cobra astropy networkx brian2 ase
```

<a id="2-verificación-del-sistema"></a>
### 2. **System Verification**
```bash
<a id="verificar-estado-completo"></a>
# Verificar estado completo
./meta4_automation.sh status

<a id="diagnóstico-detallado"></a>
# Diagnóstico detallado
./meta4_automation.sh diagnose
```

<a id="3-ejecución-de-tests"></a>
### 3. **Running Tests**
```bash
<a id="suite-completa-recomendado"></a>
# Suite completa (recomendado)
./meta4_automation.sh full-suite

<a id="tests-específicos"></a>
# Tests específicos
./meta4_automation.sh real-data
./meta4_automation.sh interdisciplinary
```

---

<a id="-integración-en-vs-code"></a>
## 🏗️ INTEGRATION IN VS CODE

<a id="tasks-integradas"></a>
### **Integrated Tasks**

The following tasks are available in **Ctrl+Shift+P → Tasks: Run Task**:

1. **AXIOM META 4 - Install Dependencies**
2. **AXIOM META 4 - Validation Tests** 
3. **AXIOM META 4 - Functional Tests**
4. **AXIOM META 4 - Real Data Tests**
5. **AXIOM META 4 - Interdisciplinary Demo**
6. **AXIOM META 4 - Production Tests**
7. **AXIOM META 4 - System Diagnostics**
8. **AXIOM META 4 - Full Test Suite**

<a id="configuración-launchjson"></a>
### **Launch.json Configuration**

Add debug configurations for Meta 4:

```json
{
    "name": "Debug AXIOM META 4 - Chemistry Service",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/test_meta4_real_data.py",
    "console": "integratedTerminal",
    "env": {
        "PYTHONPATH": "${workspaceFolder}"
    },
    "args": []
},
{
    "name": "Debug AXIOM META 4 - Full Suite",
    "type": "python", 
    "request": "launch",
    "program": "${workspaceFolder}/test_meta4_interdisciplinary.py",
    "console": "integratedTerminal",
    "env": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}
```

---

<a id="-integración-api"></a>
## 🔌 API INTEGRATION

<a id="endpoints-disponibles"></a>
### **Available Endpoints**

```python
<a id="approuters-agregar-si-no-existe"></a>
# app/routers/ (agregar si no existe)

from fastapi import APIRouter, HTTPException
from app.services.computational_chemistry import ComputationalChemistryService
from app.services.solid_state_physics import SolidStatePhysicsService
from app.services.computational_biology import ComputationalBiologyService

router = APIRouter(prefix="/meta4", tags=["AXIOM META 4"])

<a id="química-computacional"></a>
# Química Computacional
@router.post("/chemistry/analyze")
async def chemistry_analysis(request_data: dict):
    service = ComputationalChemistryService()
    return await service.process_request(request_data)

<a id="física-computacional"></a>
# Física Computacional  
@router.post("/physics/analyze")
async def physics_analysis(request_data: dict):
    service = SolidStatePhysicsService()
    return await service.process_request(request_data)

<a id="biología-computacional"></a>
# Biología Computacional
@router.post("/biology/analyze") 
async def biology_analysis(request_data: dict):
    service = ComputationalBiologyService()
    return await service.process_request(request_data)
```

<a id="uso-con-cliente-http"></a>
### **Usage with HTTP Client**

```bash
<a id="análisis-cristalino"></a>
# Análisis cristalino
curl -X POST http://localhost:8000/meta4/chemistry/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "analyze_crystal_structure",
    "structure_data": {
      "lattice": {"a": 5.43, "b": 5.43, "c": 5.43, "alpha": 90, "beta": 90, "gamma": 90},
      "species": ["Si", "Si"], 
      "coords": [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
    }
  }'

<a id="red-metabólica"></a>
# Red metabólica
curl -X POST http://localhost:8000/meta4/chemistry/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "metabolic_network_analysis",
    "model": "test_model",
    "analysis_type": "fba"
  }'
```

---

<a id="-testing-framework"></a>
## 🧪 TESTING FRAMEWORK

<a id="jerarquía-de-tests"></a>
### **Test Hierarchy**

```
test_meta4_validation.py      # Nivel 1: Validación básica
    ├── Verificar dependencias
    ├── Tests de importación
    └── Configuración básica

test_meta4_functional.py      # Nivel 2: Funcionalidad
    ├── Tests unitarios por servicio
    ├── Validación de parámetros
    └── Manejo de errores

test_meta4_real_data.py       # Nivel 3: Datos reales
    ├── Datos científicos válidos
    ├── Casos de uso reales
    └── Precisión científica

test_meta4_interdisciplinary.py # Nivel 4: Integración
    ├── Análisis combinados
    ├── Workflows complejos
    └── Demostración completa
```

<a id="estrategia-de-testing"></a>
### **Testing Strategy**

```bash
<a id="desarrollo-diario"></a>
# Desarrollo diario
./meta4_automation.sh validate

<a id="pre-commit"></a>
# Pre-commit
./meta4_automation.sh functional

<a id="pre-release"></a>
# Pre-release
./meta4_automation.sh real-data

<a id="demopresentación"></a>
# Demo/Presentación
./meta4_automation.sh interdisciplinary

<a id="cicd-pipeline"></a>
# CI/CD Pipeline
./meta4_automation.sh full-suite
```

---

<a id="-monitoreo-y-métricas"></a>
## 📊 MONITORING AND METRICS

<a id="archivos-de-resultados"></a>
### **Results Files**

```
meta4_validation_results.json      # Resultados validación
meta4_production_results.json      # Resultados producción
meta4_real_data_tests.json         # Tests datos reales
meta4_interdisciplinary_demo.json  # Demo interdisciplinaria
```

<a id="métricas-clave"></a>
### **Key Metrics**

```python
<a id="monitorear-en-logsdashboard"></a>
# Monitorear en logs/dashboard
metrics = {
    "success_rate": "Porcentaje de tests exitosos",
    "execution_time": "Tiempo promedio de ejecución", 
    "memory_usage": "Uso de memoria por análisis",
    "dependencies_status": "Estado de librerías científicas",
    "api_response_time": "Tiempo respuesta endpoints"
}
```

<a id="scripts-de-monitoreo"></a>
### **Monitoring Scripts**

```bash
<a id="monitoreo-continuo"></a>
# Monitoreo continuo
watch -n 300 './meta4_automation.sh status'

<a id="alertas-automáticas"></a>
# Alertas automáticas
./meta4_automation.sh status || echo "ALERT: Meta 4 system failure" | mail admin@company.com
```

---

<a id="-debugging-y-troubleshooting"></a>
## 🔧 DEBUGGING AND TROUBLESHOOTING

<a id="problemas-comunes"></a>
### **Common Issues**

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: pymatgen` | Dependencies not installed | `./meta4_automation.sh install` |
| `COBRApy model not found` | Invalid metabolic model | Use `test_model` or verify data |
| `Brian2 compilation error` | Missing C++ compiler | Install Xcode Command Line Tools |
| `Memory error in simulation` | Datasets too large | Reduce simulation parameters |
| `Timeout in calculation` | Calculations too complex | Adjust timeouts in code |

<a id="herramientas-de-debug"></a>
### **Debug Tools**

```python
<a id="habilitar-logging-detallado"></a>
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

<a id="debug-específico-por-servicio"></a>
# Debug específico por servicio
from app.services.computational_chemistry import ComputationalChemistryService
service = ComputationalChemistryService()
service.debug = True

<a id="verificar-dependencias-específicas"></a>
# Verificar dependencias específicas
python -c "
import sys
libs = ['pymatgen', 'cobra', 'astropy', 'networkx', 'brian2', 'ase']
for lib in libs:
    try:
        mod = __import__(lib)
        print(f'✅ {lib} v{getattr(mod, \"__version__\", \"unknown\")}')
    except ImportError as e:
        print(f'❌ {lib}: {e}')
"
```

<a id="performance-profiling"></a>
### **Performance Profiling**

```python
<a id="profiling-de-funciones-meta-4"></a>
# Profiling de funciones Meta 4
import cProfile
import pstats

def profile_meta4_analysis():
    cProfile.run('run_interdisciplinary_demo()', 'meta4_profile.prof')
    stats = pstats.Stats('meta4_profile.prof')
    stats.sort_stats('cumulative').print_stats(20)
```

---

<a id="-deployment"></a>
## 📦 DEPLOYMENT

<a id="contenedor-docker"></a>
### **Docker Container**

```dockerfile
<a id="dockerfilemeta4"></a>
# Dockerfile.meta4
FROM python:3.11-slim

<a id="dependencias-del-sistema-para-librerías-científicas"></a>
# Dependencias del sistema para librerías científicas
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

<a id="instalar-dependencias-python"></a>
# Instalar dependencias Python
COPY requirements.txt .
RUN pip install -r requirements.txt

<a id="instalar-meta-4"></a>
# Instalar Meta 4
COPY install_meta4_dependencies.sh .
RUN bash install_meta4_dependencies.sh

<a id="copiar-aplicación"></a>
# Copiar aplicación
COPY . /app
WORKDIR /app

<a id="tests-de-verificación"></a>
# Tests de verificación
RUN python test_meta4_validation.py

EXPOSE 8000
CMD ["python", "main.py"]
```

<a id="docker-compose"></a>
### **Docker Compose**

```yaml
<a id="docker-composemeta4yml"></a>
# docker-compose.meta4.yml
version: '3.8'
services:
  axiom-meta4:
    build:
      context: .
      dockerfile: Dockerfile.meta4
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./results:/app/results
    environment:
      - PYTHONPATH=/app
      - META4_DEBUG=false
    healthcheck:
      test: ["CMD", "python", "-c", "from app.services.computational_chemistry import ComputationalChemistryService; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

<a id="cicd-pipeline-1"></a>
### **CI/CD Pipeline**

```yaml
<a id="githubworkflowsmeta4yml"></a>
# .github/workflows/meta4.yml
name: AXIOM META 4 Tests

on: [push, pull_request]

jobs:
  test-meta4:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m venv .venv
        source .venv/bin/activate
        bash install_meta4_dependencies.sh
        
    - name: Run Meta 4 validation
      run: |
        source .venv/bin/activate
        python test_meta4_validation.py
        
    - name: Run Meta 4 functional tests
      run: |
        source .venv/bin/activate
        python test_meta4_functional.py
        
    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: meta4-results
        path: meta4_*_results.json
```

---

<a id="-casos-de-uso-avanzados"></a>
## 🚀 ADVANCED USE CASES

<a id="1-pipeline-de-investigación"></a>
### **1. Research Pipeline**

```python
<a id="research_pipelinepy"></a>
# research_pipeline.py
import asyncio
from app.services import *

async def research_pipeline(compound_smiles: str):
    """Pipeline completo de investigación"""
    
    # 1. Análisis químico
    chem_service = ComputationalChemistryService()
    molecular_props = await chem_service.analyze_molecule({"smiles": compound_smiles})
    
    # 2. Simulación física  
    phys_service = SolidStatePhysicsService()
    interaction_data = await phys_service.molecular_interactions(molecular_props)
    
    # 3. Impacto biológico
    bio_service = ComputationalBiologyService()
    pathway_analysis = await bio_service.drug_target_analysis({
        "compound": compound_smiles,
        "pathways": ["apoptosis", "cell_cycle"]
    })
    
    return {
        "chemistry": molecular_props,
        "physics": interaction_data,
        "biology": pathway_analysis
    }
```

<a id="2-análisis-multi-escala"></a>
### **2. Multi-scale Analysis**

```python
<a id="multi_scale_analysispy"></a>
# multi_scale_analysis.py
async def multi_scale_ecosystem_analysis(region_data):
    """Análisis desde moléculas hasta ecosistemas"""
    
    # Nivel molecular
    metabolic_networks = await analyze_species_metabolism(region_data["species"])
    
    # Nivel poblacional  
    population_dynamics = await simulate_population_interactions(region_data["populations"])
    
    # Nivel ecosistémico
    biodiversity_metrics = await calculate_ecosystem_health(region_data["environment"])
    
    return integrate_multi_scale_results(metabolic_networks, population_dynamics, biodiversity_metrics)
```

<a id="3-optimización-de-materiales"></a>
### **3. Materials Optimization**

```python
<a id="materials_optimizationpy"></a>
# materials_optimization.py
async def optimize_material_properties(target_properties):
    """Optimización inversa de propiedades de materiales"""
    
    # Generar candidatos
    candidate_structures = generate_crystal_candidates(target_properties)
    
    # Analizar propiedades
    results = []
    for structure in candidate_structures:
        props = await analyze_crystal_structure(structure)
        score = calculate_property_score(props, target_properties)
        results.append((structure, props, score))
    
    # Retornar mejores candidatos
    return sorted(results, key=lambda x: x[2], reverse=True)[:10]
```

---

<a id="-recursos-adicionales"></a>
## 📚 ADDITIONAL RESOURCES

<a id="documentación-de-referencias"></a>
### **Reference Documentation**

- [Pymatgen Documentation](https://pymatgen.org/index.html)
- [COBRApy Documentation](https://cobrapy.readthedocs.io/)
- [Astropy Documentation](https://docs.astropy.org/)
- [NetworkX Documentation](https://networkx.org/documentation/)
- [Brian2 Documentation](https://brian2.readthedocs.io/)

<a id="ejemplos-de-código"></a>
### **Code Examples**

See folder `examples/` for specific use cases:
- `chemistry_examples.py` - Advanced chemical analysis
- `physics_examples.py` - Physical simulations
- `biology_examples.py` - Biological analysis
- `interdisciplinary_examples.py` - Combined cases

<a id="comunidad-y-soporte"></a>
### **Community and Support**

- **Issues**: Report bugs on GitHub
- **Discussions**: Questions and improvements
- **Wiki**: Extended documentation
- **Slack/Discord**: Developer channel

---

<a id="-checklist-de-integración"></a>
## ✅ INTEGRATION CHECKLIST

<a id="pre-integración"></a>
### **Pre-integration**
- [ ] Virtual environment configured
- [ ] Meta 4 dependencies installed  
- [ ] Validation tests passing
- [ ] Documentation reviewed

<a id="durante-integración"></a>
### **During integration**
- [ ] VS Code tasks configured
- [ ] API endpoints implemented
- [ ] Specific tests created
- [ ] Monitoring configured

<a id="post-integración"></a>
### **Post-integration**
- [ ] Regression tests passing
- [ ] Performance verified
- [ ] Documentation updated
- [ ] Team training completed

---

<a id="-próximos-pasos"></a>
## 🎯 NEXT STEPS

1. **Implement API endpoints** specific to your use case
2. **Create custom tests** for your workflows
3. **Configure monitoring** of important metrics
4. **Document use cases** specific to your domain
5. **Train the team** on the new tools

---

**AXIOM META 4** is designed to be modular and extensible. Experiment with the capabilities and adapt the tools to your specific needs!

---

*Last updated: 3 of September, 2025*  
*Version: Meta 4.0 - Developer Integration Guide*
