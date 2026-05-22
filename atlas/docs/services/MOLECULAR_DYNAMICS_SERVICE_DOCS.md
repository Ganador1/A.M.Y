# Documentación del Servicio de Dinámica Molecular

## 📋 **Resumen Ejecutivo**

El **Servicio de Dinámica Molecular** es un componente crítico de AXIOM Phase 4 que implementa simulaciones de dinámica molecular realistas usando OpenMM. Este servicio permite realizar simulaciones atomísticas detalladas para estudiar el comportamiento dinámico de sistemas moleculares complejos.

## 🏗️ **Arquitectura del Servicio**

### **Clases Principales**

#### `MolecularDynamicsService(BaseService)`
Servicio principal que hereda de `BaseService` y proporciona la interfaz completa para simulaciones de dinámica molecular.

#### `MDSimulation`
Clase de datos que representa una instancia de simulación con todos sus parámetros y resultados.

#### `MDParameters`
Clase de datos que encapsula los parámetros físicos de la simulación.

## 🔧 **Funciones Implementadas**

### **1. `create_simulation(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Propósito:** Crear una nueva simulación de dinámica molecular con parámetros específicos.

**Parámetros de entrada:**
- `system_name` (str): Nombre descriptivo del sistema
- `temperature` (float): Temperatura en Kelvin (default: 300.0)
- `pressure` (float, opcional): Presión en atm para ensambles NPT
- `timestep` (float): Paso de tiempo en femtosegundos (default: 2.0)
- `total_time` (float): Tiempo total de simulación en picosegundos (default: 100.0)
- `equilibration_time` (float): Tiempo de equilibración en ps (default: 10.0)
- `thermostat` (str): Tipo de termostato (default: "Langevin")
- `barostat` (str, opcional): Tipo de barostato para NPT
- `nonbonded_cutoff` (float): Radio de corte para interacciones no enlazadas en nm (default: 1.0)
- `constraints` (str, opcional): Restricciones de enlaces ("HBonds", "AllBonds", None)
- `save_frequency` (int, opcional): Frecuencia de guardado de datos

**Retorno:**
```json
{
  "success": true,
  "message": "Molecular dynamics simulation created successfully",
  "simulation_id": "uuid-string",
  "simulation_type": "NVT|NPT",
  "parameters": {
    "temperature": 300.0,
    "pressure": null,
    "timestep": 2.0,
    "total_time": 100.0,
    "total_steps": 50000,
    "save_frequency": 500
  }
}
```

### **2. `run_simulation(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Propósito:** Ejecutar una simulación de dinámica molecular previamente creada.

**Parámetros de entrada:**
- `simulation_id` (str): ID de la simulación creada
- `input_structure` (str): Contenido del archivo PDB o ruta al archivo
- `forcefield` (str): Campo de fuerzas a usar (default: "amber14-all.xml")

**Campos de fuerzas soportados:**
- `amber14-all.xml`: Campo de fuerzas AMBER completo
- `amber14-all.xml`: Campo de fuerzas AMBER para proteínas
- `tip3p.xml`: Modelo de agua TIP3P
- `charmm36.xml`: Campo de fuerzas CHARMM

**Retorno:**
```json
{
  "success": true,
  "message": "Simulation completed successfully",
  "simulation_id": "uuid-string",
  "results": {
    "thermodynamic_data": {
      "energies": [...],
      "average_temperature": 299.8,
      "average_potential_energy": -1250.5,
      "average_kinetic_energy": 1875.3,
      "average_total_energy": 624.8
    },
    "final_structure": {
      "positions": [[x1,y1,z1], [x2,y2,z2], ...],
      "n_atoms": 1500
    },
    "simulation_info": {
      "total_steps": 50000,
      "timestep": 2.0,
      "temperature": 300.0,
      "forcefield": "amber14-all.xml"
    }
  }
}
```

### **3. `analyze_trajectory(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Propósito:** Analizar la trayectoria de una simulación completada.

**Tipos de análisis disponibles:**
- `rmsd`: Cálculo de RMSD (Root Mean Square Deviation)
- `energy_analysis`: Análisis detallado de componentes energéticas
- `stability_analysis`: Análisis de estabilidad del sistema

**Parámetros de entrada:**
- `simulation_id` (str): ID de la simulación
- `analysis_type` (str): Tipo de análisis a realizar

**Ejemplo de retorno para `energy_analysis`:**
```json
{
  "success": true,
  "simulation_id": "uuid-string",
  "analysis_type": "energy_analysis",
  "analysis": {
    "potential_energy_stats": {
      "mean": -1250.5,
      "std": 45.2,
      "min": -1320.1,
      "max": -1180.3
    },
    "kinetic_energy_stats": {
      "mean": 1875.3,
      "std": 32.1,
      "min": 1820.5,
      "max": 1920.7
    },
    "total_energy_stats": {
      "mean": 624.8,
      "std": 15.3,
      "min": 590.2,
      "max": 650.1
    },
    "energy_conservation": 0.0245
  }
}
```

## 🎯 **Métodos de Alto Nivel**

### **4. `protein_folding(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Propósito:** Configurar simulación de plegamiento de proteínas.

**Parámetros de entrada:**
- `protein_sequence` (str): Secuencia de aminoácidos
- `temperature` (float): Temperatura de simulación (default: 300.0)
- `simulation_time` (float): Tiempo de simulación en nanosegundos (default: 50.0)

**Aplicaciones:**
- Estudio de mecanismos de plegamiento
- Diseño de proteínas
- Análisis de estabilidad de conformaciones

### **5. `ligand_binding(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Propósito:** Configurar simulación de unión ligando-proteína.

**Parámetros de entrada:**
- `protein_pdb` (str): Estructura de la proteína en formato PDB
- `ligand_smiles` (str): Representación SMILES del ligando
- `binding_site` (dict, opcional): Sitio de unión específico

**Aplicaciones:**
- Descubrimiento de fármacos
- Optimización de ligandos
- Estudios de afinidad de unión

### **6. `material_properties(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Propósito:** Configurar simulación de propiedades de materiales.

**Parámetros de entrada:**
- `material_structure` (str): Estructura del material (CIF, POSCAR)
- `property_type` (str): Tipo de propiedad ("thermal", "mechanical", "electrical")
- `temperature_range` (list): Rango de temperaturas [min, max]

**Aplicaciones:**
- Propiedades térmicas de materiales
- Comportamiento mecánico
- Propiedades eléctricas

## 🔬 **Características Técnicas**

### **Integración con OpenMM**
- **Versión:** OpenMM 8.3.1
- **Backend:** Soporte para CUDA, OpenCL, CPU
- **Unidades:** Manejo consistente de unidades físico-químicas
- **Optimización:** Aceleración GPU automática cuando disponible

### **Campos de Fuerzas Soportados**
- **AMBER:** amber14-all.xml, amber14-protein.xml
- **CHARMM:** charmm36.xml
- **Modelos de Agua:** tip3p.xml, spce.xml
- **Materiales:** clayff.xml (en desarrollo)

### **Ensamblajes Soportados**
- **NVT:** Volumen constante, temperatura constante
- **NPT:** Presión constante, temperatura constante
- **NVE:** Energía constante, volumen constante

### **Análisis Disponibles**
- **RMSD:** Desviación cuadrática media de la raíz
- **Análisis Energético:** Componentes potencial, cinética, total
- **Estabilidad:** Conservación de energía, estabilidad térmica

## 📊 **Manejo de Datos**

### **Formato de Resultados**
- **Energías:** En kilojoules/mol (kJ/mol)
- **Temperaturas:** En Kelvin (K)
- **Posiciones:** En nanómetros (nm)
- **Tiempos:** En picosegundos (ps) o femtosegundos (fs)

### **Serialización JSON**
- Conversión automática de objetos OpenMM Quantity
- Manejo robusto de unidades físico-químicas
- Compatibilidad con APIs REST

## 🚀 **Casos de Uso**

### **Investigación Biomolecular**
```python
# Simulación de plegamiento proteico
result = await service.protein_folding({
    "protein_sequence": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR",
    "temperature": 310.0,
    "simulation_time": 100.0
})
```

### **Descubrimiento de Fármacos**
```python
# Simulación de unión ligando-proteína
result = await service.ligand_binding({
    "protein_pdb": protein_structure,
    "ligand_smiles": "CC1=CC=C(C=C1)C2=CC(=NN2C3=CC=C(C=C3)S(=O)(=O)N)C",
    "binding_site": {"residues": [25, 45, 67]}
})
```

### **Ciencia de Materiales**
```python
# Simulación de propiedades térmicas
result = await service.material_properties({
    "material_structure": cif_content,
    "property_type": "thermal",
    "temperature_range": [100, 1000]
})
```

## 🔧 **Configuración y Dependencias**

### **Dependencias Requeridas**
```bash
# Instalar OpenMM
conda install -c conda-forge openmm

# O usando pip
pip install openmm
```

### **Configuración del Servicio**
```python
# Inicialización
service = MolecularDynamicsService()

# Verificación de disponibilidad
if service.openmm_available:
    print("✅ OpenMM disponible para simulaciones")
```

## 📈 **Métricas de Rendimiento**

### **Rendimiento Típico**
- **Proteína pequeña (100 residuos):** ~10-50 ns/día en GPU
- **Sistema grande (10,000 átomos):** ~1-5 ns/día en GPU
- **Memoria:** 1-4 GB por cada 10,000 átomos

### **Optimizaciones Implementadas**
- **Minimización de energía** antes de producción
- **Equilibración térmica** automática
- **Frecuencia de guardado** configurable
- **Manejo de memoria** eficiente

## 🔄 **Integración con AXIOM**

### **Registro de Servicio**
```python
# El servicio se registra automáticamente en el service registry
from app.services.service_registry import ServiceRegistry
registry = ServiceRegistry()
registry.register_service(service)
```

### **API Endpoints**
- `POST /api/v1/molecular-dynamics/create`: Crear simulación
- `POST /api/v1/molecular-dynamics/run`: Ejecutar simulación
- `POST /api/v1/molecular-dynamics/analyze`: Analizar trayectoria
- `GET /api/v1/molecular-dynamics/status/{id}`: Estado de simulación

## 🎯 **Próximas Expansiones**

### **Phase 4 - Próximos Servicios**
1. **Física del Estado Sólido** (próximo)
2. **Neurociencia Computacional**
3. **Química Cuántica**
4. **Biología de Sistemas**

### **Mejoras Planeadas**
- **Campos de fuerzas adicionales** (OPLS, GROMOS)
- **Métodos avanzados** (Replica Exchange, Metadynamics)
- **Análisis especializados** (PCA, clustering, free energy)
- **Interfaz gráfica** para configuración de simulaciones

---

**Estado:** ✅ **COMPLETADO Y OPERATIVO**
**Versión:** 1.0.0
**Fecha:** Septiembre 2025
**Compatibilidad:** OpenMM 8.3.1+, Python 3.8+</content>
<parameter name="filePath">./MOLECULAR_DYNAMICS_SERVICE_DOCS.md
