# 🛠️ AXIOM META 4 - GUÍA DE INTEGRACIÓN PARA DESARROLLADORES

## 🎯 OBJETIVO

Esta guía proporciona instrucciones detalladas para integrar y utilizar las herramientas **AXIOM META 4** en el workflow de desarrollo del proyecto.

---

## 📋 QUICK START

### 1. **Instalación Rápida**
```bash
# Opción A: Script de automatización
./meta4_automation.sh install

# Opción B: Script directo
bash install_meta4_dependencies.sh

# Opción C: Manual
source .venv/bin/activate
pip install pymatgen cobra astropy networkx brian2 ase
```

### 2. **Verificación del Sistema**
```bash
# Verificar estado completo
./meta4_automation.sh status

# Diagnóstico detallado
./meta4_automation.sh diagnose
```

### 3. **Ejecución de Tests**
```bash
# Suite completa (recomendado)
./meta4_automation.sh full-suite

# Tests específicos
./meta4_automation.sh real-data
./meta4_automation.sh interdisciplinary
```

---

## 🏗️ INTEGRACIÓN EN VS CODE

### **Tasks Integradas**

Las siguientes tareas están disponibles en **Ctrl+Shift+P → Tasks: Run Task**:

1. **AXIOM META 4 - Install Dependencies**
2. **AXIOM META 4 - Validation Tests** 
3. **AXIOM META 4 - Functional Tests**
4. **AXIOM META 4 - Real Data Tests**
5. **AXIOM META 4 - Interdisciplinary Demo**
6. **AXIOM META 4 - Production Tests**
7. **AXIOM META 4 - System Diagnostics**
8. **AXIOM META 4 - Full Test Suite**

### **Configuración Launch.json**

Agregar configuraciones de debug para Meta 4:

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

## 🔌 INTEGRACIÓN API

### **Endpoints Disponibles**

```python
# app/routers/ (agregar si no existe)

from fastapi import APIRouter, HTTPException
from app.services.computational_chemistry import ComputationalChemistryService
from app.services.solid_state_physics import SolidStatePhysicsService
from app.services.computational_biology import ComputationalBiologyService

router = APIRouter(prefix="/meta4", tags=["AXIOM META 4"])

# Química Computacional
@router.post("/chemistry/analyze")
async def chemistry_analysis(request_data: dict):
    service = ComputationalChemistryService()
    return await service.process_request(request_data)

# Física Computacional  
@router.post("/physics/analyze")
async def physics_analysis(request_data: dict):
    service = SolidStatePhysicsService()
    return await service.process_request(request_data)

# Biología Computacional
@router.post("/biology/analyze") 
async def biology_analysis(request_data: dict):
    service = ComputationalBiologyService()
    return await service.process_request(request_data)
```

### **Uso con Cliente HTTP**

```bash
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

## 🧪 TESTING FRAMEWORK

### **Jerarquía de Tests**

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

### **Estrategia de Testing**

```bash
# Desarrollo diario
./meta4_automation.sh validate

# Pre-commit
./meta4_automation.sh functional

# Pre-release
./meta4_automation.sh real-data

# Demo/Presentación
./meta4_automation.sh interdisciplinary

# CI/CD Pipeline
./meta4_automation.sh full-suite
```

---

## 📊 MONITOREO Y MÉTRICAS

### **Archivos de Resultados**

```
meta4_validation_results.json      # Resultados validación
meta4_production_results.json      # Resultados producción
meta4_real_data_tests.json         # Tests datos reales
meta4_interdisciplinary_demo.json  # Demo interdisciplinaria
```

### **Métricas Clave**

```python
# Monitorear en logs/dashboard
metrics = {
    "success_rate": "Porcentaje de tests exitosos",
    "execution_time": "Tiempo promedio de ejecución", 
    "memory_usage": "Uso de memoria por análisis",
    "dependencies_status": "Estado de librerías científicas",
    "api_response_time": "Tiempo respuesta endpoints"
}
```

### **Scripts de Monitoreo**

```bash
# Monitoreo continuo
watch -n 300 './meta4_automation.sh status'

# Alertas automáticas
./meta4_automation.sh status || echo "ALERT: Meta 4 system failure" | mail admin@company.com
```

---

## 🔧 DEBUGGING Y TROUBLESHOOTING

### **Problemas Comunes**

| Error | Causa | Solución |
|-------|-------|----------|
| `ModuleNotFoundError: pymatgen` | Dependencias no instaladas | `./meta4_automation.sh install` |
| `COBRApy model not found` | Modelo metabólico inválido | Usar `test_model` o verificar datos |
| `Brian2 compilation error` | Compilador C++ faltante | Instalar Xcode Command Line Tools |
| `Memory error in simulation` | Datasets muy grandes | Reducir parámetros de simulación |
| `Timeout in calculation` | Cálculos muy complejos | Ajustar timeouts en código |

### **Herramientas de Debug**

```python
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug específico por servicio
from app.services.computational_chemistry import ComputationalChemistryService
service = ComputationalChemistryService()
service.debug = True

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

### **Performance Profiling**

```python
# Profiling de funciones Meta 4
import cProfile
import pstats

def profile_meta4_analysis():
    cProfile.run('run_interdisciplinary_demo()', 'meta4_profile.prof')
    stats = pstats.Stats('meta4_profile.prof')
    stats.sort_stats('cumulative').print_stats(20)
```

---

## 📦 DEPLOYMENT

### **Contenedor Docker**

```dockerfile
# Dockerfile.meta4
FROM python:3.11-slim

# Dependencias del sistema para librerías científicas
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Instalar Meta 4
COPY install_meta4_dependencies.sh .
RUN bash install_meta4_dependencies.sh

# Copiar aplicación
COPY . /app
WORKDIR /app

# Tests de verificación
RUN python test_meta4_validation.py

EXPOSE 8000
CMD ["python", "main.py"]
```

### **Docker Compose**

```yaml
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

### **CI/CD Pipeline**

```yaml
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

## 🚀 CASOS DE USO AVANZADOS

### **1. Pipeline de Investigación**

```python
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

### **2. Análisis Multi-escala**

```python
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

### **3. Optimización de Materiales**

```python
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

## 📚 RECURSOS ADICIONALES

### **Documentación de Referencias**

- [Pymatgen Documentation](https://pymatgen.org/index.html)
- [COBRApy Documentation](https://cobrapy.readthedocs.io/)
- [Astropy Documentation](https://docs.astropy.org/)
- [NetworkX Documentation](https://networkx.org/documentation/)
- [Brian2 Documentation](https://brian2.readthedocs.io/)

### **Ejemplos de Código**

Ver carpeta `examples/` para casos de uso específicos:
- `chemistry_examples.py` - Análisis químicos avanzados
- `physics_examples.py` - Simulaciones físicas
- `biology_examples.py` - Análisis biológicos
- `interdisciplinary_examples.py` - Casos combinados

### **Comunidad y Soporte**

- **Issues**: Reportar bugs en GitHub
- **Discussions**: Preguntas y mejoras
- **Wiki**: Documentación extendida
- **Slack/Discord**: Canal de desarrolladores

---

## ✅ CHECKLIST DE INTEGRACIÓN

### **Pre-integración**
- [ ] Entorno virtual configurado
- [ ] Dependencias Meta 4 instaladas  
- [ ] Tests de validación pasando
- [ ] Documentación revisada

### **Durante integración**
- [ ] Tasks de VS Code configuradas
- [ ] Endpoints API implementados
- [ ] Tests específicos creados
- [ ] Monitoreo configurado

### **Post-integración**
- [ ] Tests de regresión pasando
- [ ] Performance verificado
- [ ] Documentación actualizada
- [ ] Team training completado

---

## 🎯 PRÓXIMOS PASOS

1. **Implementar endpoints API** específicos para tu caso de uso
2. **Crear tests personalizados** para tus workflows
3. **Configurar monitoreo** de métricas importantes
4. **Documentar casos de uso** específicos de tu dominio
5. **Entrenar al equipo** en las nuevas herramientas

---

**AXIOM META 4** está diseñado para ser modular y extensible. ¡Experimenta con las capacidades y adapta las herramientas a tus necesidades específicas!

---

*Última actualización: 3 de Septiembre, 2025*  
*Versión: Meta 4.0 - Developer Integration Guide*
