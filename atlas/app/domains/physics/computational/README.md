# Computational Physics - Scientific Computing Services

## Overview
El subdominio de Física Computacional provee herramientas para resolver ecuaciones diferenciales parciales con redes informadas por física (PINNs) y módulos de física del estado sólido (DFT, propiedades electrónicas) integrando SciPy, NumPy, DeepXDE y ASE.

## Services Available

### PhysicsInformedNNService
- **Description:** Resolución de PDEs e inferencia de parámetros usando PINNs.
- **Key Features:**
  - Solución forward/inverse de PDEs
  - Acoplamiento multi-física
  - Estimación de parámetros
- **API Endpoints:**
  - `POST /api/physics/computational/pinn/solve` - Resolver PDE
  - `POST /api/physics/computational/pinn/infer` - Inferencia de parámetros
- **Schemas:** `ComputationalPhysicsRequest` / `ComputationalPhysicsResponse`

### SolidStatePhysicsService
- **Description:** Cálculos de estructura electrónica y propiedades de materiales.
- **Key Features:**
  - Band structure (DFT/ASE)
  - Propiedades térmicas/electrónicas
  - Integración con workflows
- **API Endpoints:**
  - `POST /api/physics/computational/solid-state/band-structure`
  - `POST /api/physics/computational/solid-state/properties`
- **Schemas:** Ver `app/domains/physics/models/`

## Installation Requirements
```bash
pip install numpy scipy deepxde ase
```

## Quick Start
```python
from app.domains.physics.computational.physics_informed_nn_service import PhysicsInformedNNService

service = PhysicsInformedNNService()
solution = await service.solve_pde(params)
```

## Scientific Background
PINNs para resolver PDEs; métodos de estructura electrónica para materiales.

## Performance Considerations
- Entrenamiento de PINNs puede ser costoso; usar GPU.
- Tamaños de malla y discretización afectan memoria/tiempo.

## Testing
```bash
pytest tests/physics/ -v
```

## Related Services
- [Mathematics](../../mathematics/README.md)
- [Astronomy](../../astronomy/README.md)