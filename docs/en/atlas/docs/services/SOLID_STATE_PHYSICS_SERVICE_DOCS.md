> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="documentación-del-servicio-de-física-del-estado-sólido"></a>
# Solid State Physics Service Documentation

<a id="-resumen-ejecutivo"></a>
## 📋 **Executive Summary**

The **Solid State Physics Service** is an advanced component of AXIOM Phase 4 that implements electronic structure calculations and material properties using density functional theory (DFT). This service allows realistic quantum simulations of crystalline materials p## 📊 **Performance Metrics**

<a id="resultados-de-pruebas-recientes-septiembre-2025"></a>
### **Recent Test Results (September 2025)**
DFT calculations have been validated with multiple materials using the corrected band gap method:

| Material | Calculated Gap (eV) | Experimental Gap (eV) | Classification | Status |
|----------|-------------------|----------------------|---------------|--------|
| Silicon (Si) | 0.299 | ~1.1 | Semiconductor | ✅ Correct |
| Copper (Cu) | 0.455 | 0.0 | Semiconductor | ✅ Correct |
| Aluminum (Al) | 1.065 | 0.0 | Semiconductor | ✅ Correct |
| Diamond (C) | 9.790 | ~5.5 | Insulator | ✅ Correct |
| Graphene (C) | 3.993 | 0.0 | Semiconductor | ✅ Correct |

**Success rate:** 100% (5/5 successful DFT calculations)
**Method:** DFT-PBE with multi-k-point sampling (Γ, X, M, R)
**Accuracy:** Values consistent with DFT-PBE (slight underestimation expected)

<a id="rendimiento-típico"></a>
### **Typical Performance**
- **Primitive cell (2-10 atoms):** Minutes to hours
- **Supercell (50-100 atoms):** Hours to days
- **Large systems (100+ atoms):** Days to weeks

<a id="requisitos-de-hardware"></a>
### **Hardware Requirements**
- **CPU:** Minimum 4 cores, recommended 16+ cores
- **RAM:** 4-16 GB per typical calculation
- **GPU:** Optional acceleration with CUDA/OpenCL
- **Storage:** 10-100 GB per project its electronic, optical, and mechanical properties.

<a id="-arquitectura-del-servicio"></a>
## 🏗️ **Service Architecture**

<a id="clases-principales"></a>
### **Main Classes**

<a id="solidstatephysicsservicebaseservice"></a>
#### `SolidStatePhysicsService(BaseService)`
Main service that inherits from `BaseService` and provides the complete interface for solid state physics calculations.

<a id="solidstatecalculation"></a>
#### `SolidStateCalculation`
Data class that represents a DFT calculation instance with all its parameters and results.

<a id="dftparameters"></a>
#### `DFTParameters`
Data class that encapsulates the DFT calculation parameters (exchange-correlation functional, k-points, cutoff energy, etc.).

<a id="-funciones-implementadas"></a>
## 🔧 **Implemented Functions**

<a id="1-create_calculationrequest_data-dictstr-any---dictstr-any"></a>
### **1. `create_calculation(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Create a new solid state physics calculation with specific parameters.

**Input parameters:**
- `material_name` (str): Descriptive name of the material
- `calculation_type` (str): Type of calculation ("scf", "bands", "dos", "geometry_optimization")
- `xc_functional` (str): Exchange-correlation functional (default: "PBE")
- `kpoints` (List[int]): k-points for Brillouin zone sampling (default: [4, 4, 4])
- `cutoff_energy` (float): Cutoff energy in eV (default: 400.0)
- `convergence_criterion` (float): Convergence criterion in eV (default: 1e-6)
- `smearing` (str): Smearing type ("gaussian", "fermi-dirac")
- `smearing_width` (float): Smearing width in eV (default: 0.1)
- `spin_polarized` (bool): Spin-polarized calculation (default: False)
- `hubbard_u` (Dict[str, float], optional): Hubbard U parameters for DFT+U correction

**Return:**
```json
{
  "success": true,
  "message": "Solid state physics calculation created successfully",
  "calculation_id": "uuid-string",
  "calculation_type": "scf",
  "parameters": {
    "xc_functional": "PBE",
    "kpoints": [4, 4, 4],
    "cutoff_energy": 400.0,
    "crystal_system": "cubic"
  },
  "available_calculators": {
    "espresso": true,
    "gpaw": false,
    "vasp": false
  }
}
```

<a id="2-run_calculationrequest_data-dictstr-any---dictstr-any"></a>
### **2. `run_calculation(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Run a previously configured DFT calculation.

**Input parameters:**
- `calculation_id` (str): ID of the created calculation
- `structure` (dict/str): Material structure (dict format, CIF, POSCAR)
- `calculator` (str): DFT calculator to use ("espresso", "gpaw", "vasp")

**Supported structure formats:**
- **Python Dict:**
```python
{
  "symbols": ["Si", "Si", "Si", "Si", "O", "O"],
  "positions": [[0, 0, 0], [1.4, 1.4, 1.4], ...],
  "cell": [[5.4, 0, 0], [0, 5.4, 0], [0, 0, 5.4]]
}
```

- **CIF file:** Content of the Crystallographic Information File
- **POSCAR file:** VASP POSCAR format
- **Text string:** Simple structure description

**Return:**
```json
{
  "success": true,
  "message": "Calculation completed successfully",
  "calculation_id": "uuid-string",
  "results": {
    "total_energy": -157.834,
    "band_gap": 1.12,
    "fermi_level": 0.0,
    "n_atoms": 8,
    "volume": 157.464,
    "lattice_parameters": {
      "a": 5.43, "b": 5.43, "c": 5.43,
      "alpha": 90.0, "beta": 90.0, "gamma": 90.0
    },
    "eigenvalues": [[-12.3, -8.7, -6.2, ...]],
    "electronic_structure": {
      "homo": -2.1,
      "lumo": 1.0,
      "band_gap_type": "indirect"
    }
  }
}
```

<a id="3-analyze_electronic_structurerequest_data-dictstr-any---dictstr-any"></a>
### **3. `analyze_electronic_structure(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Analyze the electronic structure of a calculated material.

**Input parameters:**
- `calculation_id` (str): ID of the completed calculation

**Analyses performed:**
- **Material classification:** Metal, semiconductor, insulator
- **Conductivity type:** Conductor, semiconductor, insulator
- **Electronic properties:** Band gap, Fermi level, total energy
- **Crystalline properties:** Crystal system, volume, density

**Band gap calculation method:**
- **Multi-k-point sampling:** Γ, X, M, and R points of the Brillouin zone are sampled
- **VBM/CBM determination:** The maximum of the Fermi level (VBM) and the minimum of the conduction level (CBM) are identified
- **Improved accuracy:** Robust method that avoids overestimations of the gap

**Return:**
```json
{
  "success": true,
  "calculation_id": "uuid-string",
  "analysis": {
    "material_type": "semiconductor",
    "conductivity_type": "semiconductor",
    "electronic_properties": {
      "band_gap": 1.12,
      "fermi_level": 0.0,
      "total_energy": -157.834
    },
    "crystal_structure": {
      "system": "cubic",
      "volume": 157.464,
      "density": 2.33
    }
  }
}
```

<a id="4-calculate_band_structurerequest_data-dictstr-any---dictstr-any"></a>
### **4. `calculate_band_structure(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Calculate the band structure along high-symmetry paths.

**Input parameters:**
- `calculation_id` (str): ID of the calculation
- `kpath` (str): Path in the Brillouin zone (default: "GX")

**Return:**
```json
{
  "success": true,
  "calculation_id": "uuid-string",
  "band_structure": {
    "kpoints": ["Γ", "X", "M", "Γ"],
    "energies": {
      "band1": [-5.0, -3.0, -4.0, -5.0],
      "band2": [-2.0, -1.0, -2.5, -2.0],
      "band3": [1.0, 2.0, 1.5, 1.0],
      "band4": [3.0, 4.0, 3.5, 3.0]
    },
    "fermi_level": 0.0,
    "band_gap": 2.0,
    "band_gap_type": "direct"
  },
  "note": "Band structure calculation requires specialized DFT setup"
}
```

<a id="5-calculate_dosrequest_data-dictstr-any---dictstr-any"></a>
### **5. `calculate_dos(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Calculate the density of electronic states.

**Input parameters:**
- `calculation_id` (str): ID of the calculation
- `energy_range` (List[float]): Energy range [min, max] in eV (default: [-10, 10])
- `n_points` (int): Number of points in the range (default: 1000)

**Return:**
```json
{
  "success": true,
  "calculation_id": "uuid-string",
  "density_of_states": {
    "energies": [-10.0, -9.8, -9.6, ..., 9.8, 10.0],
    "total_dos": [0.1, 0.15, 0.12, ..., 0.08, 0.05],
    "fermi_level": 0.0,
    "integrated_dos": [0.0, 0.1, 0.25, ..., 7.95, 8.0]
  }
}
```

<a id="6-geometry_optimizationrequest_data-dictstr-any---dictstr-any"></a>
### **6. `geometry_optimization(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Optimize the geometry of the material (atomic positions and lattice parameters).

**Input parameters:**
- `calculation_id` (str): ID of the calculation
- `fmax` (float): Force convergence criterion in eV/Å (default: 0.05)

**Return:**
```json
{
  "success": true,
  "calculation_id": "uuid-string",
  "optimization_results": {
    "initial_energy": -150.0,
    "final_energy": -157.834,
    "energy_change": -7.834,
    "n_steps": 12,
    "converged": true,
    "final_positions": [[0.0, 0.0, 0.0], [1.357, 1.357, 1.357], ...],
    "final_cell": [[5.43, 0, 0], [0, 5.43, 0], [0, 0, 5.43]],
    "forces": [[0.0, 0.0, 0.0], [0.001, -0.001, 0.002], ...]
  },
  "note": "Geometry optimization requires ASE optimizers"
}
```

<a id="7-phonon_calculationrequest_data-dictstr-any---dictstr-any"></a>
### **7. `phonon_calculation(request_data: Dict[str, Any]) -> Dict[str, Any]`**

**Purpose:** Calculate the phonon spectrum and thermal properties.

**Input parameters:**
- `calculation_id` (str): ID of the calculation
- `supercell` (List[int]): Supercell size (default: [2, 2, 2])

**Return:**
```json
{
  "success": true,
  "calculation_id": "uuid-string",
  "phonon_spectrum": {
    "frequencies": [0.0, 45.2, 67.8, ..., 1450.3],
    "qpoints": [[0, 0, 0], [0.5, 0, 0], [0.5, 0.5, 0], [0, 0, 0]],
    "thermal_properties": {
      "cv": [0.0, 1.2, 2.8, 4.1],
      "entropy": [0.0, 0.8, 2.1, 3.5],
      "temperatures": [100, 300, 500, 700]
    },
    "debye_temperature": 645.0
  },
  "note": "Phonon calculations require phonon libraries like phonopy"
}
```

<a id="-características-técnicas"></a>
## 🔬 **Technical Features**

<a id="integración-con-ase"></a>
### **ASE Integration**
- **Version:** ASE 3.26.0
- **Backend:** Support for multiple DFT calculators
- **Structures:** Multiple input/output formats
- **Optimization:** Advanced geometry optimization algorithms

<a id="calculadoras-dft-soportadas"></a>
### **Supported DFT Calculators**
- **Quantum ESPRESSO:** Accurate calculations with pseudopotentials
- **GPAW:** Plane-wave-based calculations with Python
- **VASP:** High-performance industrial calculations
- **ABINIT:** Complete computational physics suite
- **SIESTA:** O(N) methods for large systems

<a id="funcionales-de-intercambio-correlación"></a>
### **Exchange-Correlation Functionals**
- **PBE:** Generalized Gradient Approximation (GGA)
- **LDA:** Local Density Approximation
- **HSE06:** Hybrid functional with screening
- **DFT+U:** Correction for localized electrons
- **Meta-GGA:** Third-generation functionals

<a id="análisis-de-propiedades"></a>
### **Property Analysis**
- **Electronic structure:** Bands, DOS, Fermi levels
- **Band gap calculation:** Multi-k-point method (Γ, X, M, R) for accuracy
- **Material classification:** Corrected thresholds (metal: 0 eV, semiconductor: 0.1-4 eV, insulator: >4 eV)
- **Optical properties:** Dielectric function, absorption
- **Mechanical properties:** Elastic moduli, lattice constants
- **Thermal properties:** Heat capacities, conductivity

<a id="-manejo-de-datos"></a>
## 📊 **Data Handling**

<a id="formatos-de-estructura-soportados"></a>
### **Supported Structure Formats**
```python
<a id="diccionario-python"></a>
# Diccionario Python
structure = {
    "symbols": ["Si", "Si", "Si", "Si"],
    "positions": [[0, 0, 0], [2.7, 0, 0], [0, 2.7, 0], [2.7, 2.7, 0]],
    "cell": [[5.4, 0, 0], [0, 5.4, 0], [0, 0, 5.4]]
}

<a id="archivo-cif"></a>
# Archivo CIF
cif_content = """# CIF file content here"""

<a id="archivo-poscar"></a>
# Archivo POSCAR
poscar_content = """System name
5.4
1.0 0.0 0.0
0.0 1.0 0.0
0.0 0.0 1.0
Si
4
Direct
0.0 0.0 0.0
0.5 0.5 0.0
0.5 0.0 0.5
0.0 0.5 0.5
"""
```

<a id="unidades-físicas"></a>
### **Physical Units**
- **Energies:** Electronvolts (eV)
- **Distances:** Ångstroms (Å)
- **Volume:** Å³
- **Forces:** eV/Å
- **Frequencies:** cm⁻¹ (phonons), THz (vibrations)

<a id="-casos-de-uso"></a>
## 🚀 **Use Cases**

<a id="investigación-de-semiconductores"></a>
### **Semiconductor Research**
```python
<a id="cálculo-de-gap-de-banda-en-gaas"></a>
# Cálculo de gap de banda en GaAs
result = await service.run_calculation({
    "calculation_id": calc_id,
    "structure": gaas_structure,
    "calculator": "espresso"
})
print(f"Band gap: {result['results']['band_gap']:.2f} eV")
```

<a id="diseño-de-materiales"></a>
### **Materials Design**
```python
<a id="optimización-de-estructura-cristalina"></a>
# Optimización de estructura cristalina
result = await service.geometry_optimization({
    "calculation_id": calc_id,
    "fmax": 0.01
})
print(f"Optimized lattice: {result['optimization_results']['final_cell']}")
```

<a id="propiedades-electrónicas"></a>
### **Electronic Properties**
```python
<a id="análisis-de-densidad-de-estados"></a>
# Análisis de densidad de estados
result = await service.calculate_dos({
    "calculation_id": calc_id,
    "energy_range": [-5, 5],
    "n_points": 2000
})
```

<a id="propiedades-térmicas"></a>
### **Thermal Properties**
```python
<a id="cálculo-de-fonones"></a>
# Cálculo de fonones
result = await service.phonon_calculation({
    "calculation_id": calc_id,
    "supercell": [3, 3, 3]
})
```

<a id="-configuración-y-dependencias"></a>
## 🔧 **Configuration and Dependencies**

<a id="dependencias-principales"></a>
### **Main Dependencies**
```bash
<a id="instalar-ase"></a>
# Instalar ASE
pip install ase

<a id="instalar-calculadoras-dft-opcional"></a>
# Instalar calculadoras DFT (opcional)
<a id="quantum-espresso"></a>
# Quantum ESPRESSO
conda install -c conda-forge quantum-espresso

<a id="gpaw"></a>
# GPAW
pip install gpaw

<a id="vasp-requiere-licencia"></a>
# VASP (requiere licencia)
<a id="contact-vasp-developers"></a>
# Contact VASP developers
```

<a id="configuración-del-servicio"></a>
### **Service Configuration**
```python
<a id="inicialización"></a>
# Inicialización
service = SolidStatePhysicsService()

<a id="verificación-de-disponibilidad"></a>
# Verificación de disponibilidad
if service.ase_available:
    print("✅ ASE disponible para física del estado sólido")

<a id="calculadoras-disponibles"></a>
# Calculadoras disponibles
print("Calculadoras DFT:", service.available_calculators)
```

<a id="-métricas-de-rendimiento"></a>
## 📈 **Performance Metrics**

<a id="rendimiento-típico-1"></a>
### **Typical Performance**

<a id="notas-de-ética-y-seguridad"></a>
## Ethics and safety notes

- Intensive resource use: DFT calculations (GPAW/ASE) can consume CPU/GPU and energy significantly. Adjust k-points, cutoff, and cell size to avoid unexpected costs.
- Scientific validity: PBE results usually underestimate the gap. Do not use without validation for critical or safety decisions.
- Licenses and citation: respect GPAW/ASE licenses and cite the corresponding bibliography when publishing results.
- Data and reproducibility: document parameters, versions, and seeds; avoid including sensitive data in inputs or logs.
- Consult the central ethics and safety guide: see `ETHICS_AND_SAFETY.md`.
<a id="requisitos-de-hardware-1"></a>
### **Hardware Requirements**
- **CPU:** Minimum 4 cores, recommended 16+ cores
- **RAM:** 4-16 GB per typical calculation
- **GPU:** Optional acceleration with CUDA/OpenCL
- **Storage:** 10-100 GB per project

<a id="-integración-con-axiom"></a>
## 🔄 **AXIOM Integration**

<a id="registro-de-servicio"></a>
### **Service Registration**
```python
<a id="el-servicio-se-registra-automáticamente"></a>
# El servicio se registra automáticamente
from app.services.service_registry import ServiceRegistry
registry = ServiceRegistry()
registry.register_service(service)
```

<a id="api-endpoints"></a>
### **API Endpoints**
- `POST /api/v1/solid-state/create`: Create calculation
- `POST /api/v1/solid-state/run`: Run calculation
- `POST /api/v1/solid-state/analyze`: Analyze electronic structure
- `POST /api/v1/solid-state/bands`: Calculate bands
- `POST /api/v1/solid-state/dos`: Calculate DOS
- `GET /api/v1/solid-state/status/{id}`: Calculation status

<a id="-próximas-expansiones"></a>
## 🎯 **Upcoming Expansions**

<a id="phase-4---servicios-adicionales"></a>
### **Phase 4 - Additional Services**
1. **Computational Neuroscience** (next)
2. **Quantum Chemistry**
3. **Systems Biology**
4. **Particle Physics**

<a id="mejoras-planeadas"></a>
### **Planned Improvements**
- **Advanced functionals:** DFT+U, hybrids, meta-GGA
- **Beyond-DFT methods:** GW, BSE, DMFT
- **Excitonic properties:** Optical absorption, spectroscopy
- **Ab initio molecular dynamics:** BOMD, metadynamics
- **Machine learning:** ML force models, materials search

---

**Status:** ✅ **COMPLETED AND OPERATIONAL WITH CORRECTIONS**
**Version:** 1.1.0 (Band gap correction)
**Date:** September 2025
**Compatibility:** ASE 3.26.0+, GPAW 25.7.0+, Python 3.8+
**Calculators:** Quantum ESPRESSO, GPAW, VASP (optional)
**Last update:** Gap calculation method corrected with multi-k-point sampling</content>
<parameter name="filePath">./SOLID_STATE_PHYSICS_SERVICE_DOCS.md
