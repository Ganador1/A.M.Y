> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="documentación-del-servicio-de-dinámica-molecular"></a>
# Molecular Dynamics Service Documentation

<a id="-resumen-ejecutivo"></a>
## 📋 **Executive Summary**

The **Molecular Dynamics Service** is a critical component of AXIOM Phase 4 that implements realistic molecular dynamics simulations using OpenMM. This service allows detailed atomistic simulations to study the dynamic behavior of complex molecular systems.

<a id="-arquitectura-del-servicio"></a>
## 🏗️ **Service Architecture**

<a id="clases-principales"></a>
### **Main Classes**

<a id="moleculardynamicsservicebaseservice"></a>
#### `MolecularDynamicsService(BaseService)`
Main service that inherits from `BaseService` and provides the complete interface for molecular dynamics simulations.

<a id="mdsimulation"></a>
#### `MDSimulation`
Data class that represents a simulation instance with all its parameters and results.

<a id="mdparameters"></a>
#### `MDParameters`
Data class that encapsulates the physical parameters of the simulation.

<a id="-funciones-implementadas"></a>
## 🔧 **Implemented Functions**

<a id="1-create_simulationrequest_data-dictstr-any---dictstr-any"></a>
### **1. `create_simulation(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Create a new molecular dynamics simulation with specific parameters.

**Input parameters:**
- `system_name` (str): Descriptive name of the system
- `temperature` (float): Temperature in Kelvin (default: 300.0)
- `pressure` (float, optional): Pressure in atm for NPT ensembles
- `timestep` (float): Time step in femtoseconds (default: 2.0)
- `total_time` (float): Total simulation time in picoseconds (default: 100.0)
- `equilibration_time` (float): Equilibration time in ps (default: 10.0)
- `thermostat` (str): Thermostat type (default: "Langevin")
- `barostat` (str, optional): Barostat type for NPT
- `nonbonded_cutoff` (float): Cutoff radius for non-bonded interactions in nm (default: 1.0)
- `constraints` (str, optional): Bond constraints ("HBonds", "AllBonds", None)
- `save_frequency` (int, optional): Data saving frequency

**Return:**
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

<a id="2-run_simulationrequest_data-dictstr-any---dictstr-any"></a>
### **2. `run_simulation(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Run a previously created molecular dynamics simulation.

**Input parameters:**
- `simulation_id` (str): ID of the created simulation
- `input_structure` (str): Content of the PDB file or path to the file
- `forcefield` (str): Force field to use (default: "amber14-all.xml")

**Supported force fields:**
- `amber14-all.xml`: Complete AMBER force field
- `amber14-all.xml`: AMBER force field for proteins
- `tip3p.xml`: TIP3P water model
- `charmm36.xml`: CHARMM force field

**Return:**
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

<a id="3-analyze_trajectoryrequest_data-dictstr-any---dictstr-any"></a>
### **3. `analyze_trajectory(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Analyze the trajectory of a completed simulation.

**Available analysis types:**
- `rmsd`: RMSD (Root Mean Square Deviation) calculation
- `energy_analysis`: Detailed analysis of energy components
- `stability_analysis`: System stability analysis

**Input parameters:**
- `simulation_id` (str): Simulation ID
- `analysis_type` (str): Type of analysis to perform

**Example return for `energy_analysis`:**
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

<a id="-métodos-de-alto-nivel"></a>
## 🎯 **High-Level Methods**

<a id="4-protein_foldingrequest_data-dictstr-any---dictstr-any"></a>
### **4. `protein_folding(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Configure protein folding simulation.

**Input parameters:**
- `protein_sequence` (str): Amino acid sequence
- `temperature` (float): Simulation temperature (default: 300.0)
- `simulation_time` (float): Simulation time in nanoseconds (default: 50.0)

**Applications:**
- Study of folding mechanisms
- Protein design
- Analysis of conformational stability

<a id="5-ligand_bindingrequest_data-dictstr-any---dictstr-any"></a>
### **5. `ligand_binding(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Configure ligand-protein binding simulation.

**Input parameters:**
- `protein_pdb` (str): Protein structure in PDB format
- `ligand_smiles` (str): SMILES representation of the ligand
- `binding_site` (dict, optional): Specific binding site

**Applications:**
- Drug discovery
- Ligand optimization
- Binding affinity studies

<a id="6-material_propertiesrequest_data-dictstr-any---dictstr-any"></a>
### **6. `material_properties(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Configure material property simulation.

**Input parameters:**
- `material_structure` (str): Material structure (CIF, POSCAR)
- `property_type` (str): Property type ("thermal", "mechanical", "electrical")
- `temperature_range` (list): Temperature range [min, max]

**Applications:**
- Thermal properties of materials
- Mechanical behavior
- Electrical properties

<a id="-características-técnicas"></a>
## 🔬 **Technical Features**

<a id="integración-con-openmm"></a>
### **OpenMM Integration**
- **Version:** OpenMM 8.3.1
- **Backend:** Support for CUDA, OpenCL, CPU
- **Units:** Consistent handling of physicochemical units
- **Optimization:** Automatic GPU acceleration when available

<a id="campos-de-fuerzas-soportados"></a>
### **Supported Force Fields**
- **AMBER:** amber14-all.xml, amber14-protein.xml
- **CHARMM:** charmm36.xml
- **Water Models:** tip3p.xml, spce.xml
- **Materials:** clayff.xml (in development)

<a id="ensamblajes-soportados"></a>
### **Supported Ensembles**
- **NVT:** Constant volume, constant temperature
- **NPT:** Constant pressure, constant temperature
- **NVE:** Constant energy, constant volume

<a id="análisis-disponibles"></a>
### **Available Analyses**
- **RMSD:** Root mean square deviation
- **Energy Analysis:** Potential, kinetic, total components
- **Stability:** Energy conservation, thermal stability

<a id="-manejo-de-datos"></a>
## 📊 **Data Handling**

<a id="formato-de-resultados"></a>
### **Results Format**
- **Energies:** In kilojoules/mol (kJ/mol)
- **Temperatures:** In Kelvin (K)
- **Positions:** In nanometers (nm)
- **Times:** In picoseconds (ps) or femtoseconds (fs)

<a id="serialización-json"></a>
### **JSON Serialization**
- Automatic conversion of OpenMM Quantity objects
- Robust handling of physicochemical units
- Compatibility with REST APIs

<a id="-casos-de-uso"></a>
## 🚀 **Use Cases**

<a id="investigación-biomolecular"></a>
### **Biomolecular Research**
```python
<a id="simulación-de-plegamiento-proteico"></a>
# Simulación de plegamiento proteico
result = await service.protein_folding({
    "protein_sequence": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR",
    "temperature": 310.0,
    "simulation_time": 100.0
})
```

<a id="descubrimiento-de-fármacos"></a>
### **Drug Discovery**
```python
<a id="simulación-de-unión-ligando-proteína"></a>
# Simulación de unión ligando-proteína
result = await service.ligand_binding({
    "protein_pdb": protein_structure,
    "ligand_smiles": "CC1=CC=C(C=C1)C2=CC(=NN2C3=CC=C(C=C3)S(=O)(=O)N)C",
    "binding_site": {"residues": [25, 45, 67]}
})
```

<a id="ciencia-de-materiales"></a>
### **Materials Science**
```python
<a id="simulación-de-propiedades-térmicas"></a>
# Simulación de propiedades térmicas
result = await service.material_properties({
    "material_structure": cif_content,
    "property_type": "thermal",
    "temperature_range": [100, 1000]
})
```

<a id="-configuración-y-dependencias"></a>
## 🔧 **Configuration and Dependencies**

<a id="dependencias-requeridas"></a>
### **Required Dependencies**
```bash
<a id="instalar-openmm"></a>
# Instalar OpenMM
conda install -c conda-forge openmm

<a id="o-usando-pip"></a>
# O usando pip
pip install openmm
```

<a id="configuración-del-servicio"></a>
### **Service Configuration**
```python
<a id="inicialización"></a>
# Inicialización
service = MolecularDynamicsService()

<a id="verificación-de-disponibilidad"></a>
# Verificación de disponibilidad
if service.openmm_available:
    print("✅ OpenMM disponible para simulaciones")
```

<a id="-métricas-de-rendimiento"></a>
## 📈 **Performance Metrics**

<a id="rendimiento-típico"></a>
### **Typical Performance**
- **Small protein (100 residues):** ~10-50 ns/day on GPU
- **Large system (10,000 atoms):** ~1-5 ns/day on GPU
- **Memory:** 1-4 GB per 10,000 atoms

<a id="optimizaciones-implementadas"></a>
### **Implemented Optimizations**
- **Energy minimization** before production
- **Automatic thermal equilibration**
- **Configurable saving frequency**
- **Efficient memory handling**

<a id="-integración-con-axiom"></a>
## 🔄 **Integration with AXIOM**

<a id="registro-de-servicio"></a>
### **Service Registration**
```python
<a id="el-servicio-se-registra-automáticamente-en-el-service-registry"></a>
# El servicio se registra automáticamente en el service registry
from app.services.service_registry import ServiceRegistry
registry = ServiceRegistry()
registry.register_service(service)
```

<a id="api-endpoints"></a>
### **API Endpoints**
- `POST /api/v1/molecular-dynamics/create`: Create simulation
- `POST /api/v1/molecular-dynamics/run`: Run simulation
- `POST /api/v1/molecular-dynamics/analyze`: Analyze trajectory
- `GET /api/v1/molecular-dynamics/status/{id}`: Simulation status

<a id="-próximas-expansiones"></a>
## 🎯 **Upcoming Expansions**

<a id="phase-4---próximos-servicios"></a>
### **Phase 4 - Upcoming Services**
1. **Solid State Physics** (next)
2. **Computational Neuroscience**
3. **Quantum Chemistry**
4. **Systems Biology**

<a id="mejoras-planeadas"></a>
### **Planned Improvements**
- **Additional force fields** (OPLS, GROMOS)
- **Advanced methods** (Replica Exchange, Metadynamics)
- **Specialized analyses** (PCA, clustering, free energy)
- **Graphical interface** for simulation configuration

---

**Status:** ✅ **COMPLETED AND OPERATIONAL**
**Version:** 1.0.0
**Date:** September 2025
**Compatibility:** OpenMM 8.3.1+, Python 3.8+</content>
<parameter name="filePath">./MOLECULAR_DYNAMICS_SERVICE_DOCS.md
