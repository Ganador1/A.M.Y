> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="computational-physics---scientific-computing-services"></a>
# Computational Physics - Scientific Computing Services

<a id="overview"></a>
## Overview
The Computational Physics subdomain provides tools for solving partial differential equations with physics-informed neural networks (PINNs) and solid-state physics modules (DFT, electronic properties) integrating SciPy, NumPy, DeepXDE, and ASE.

<a id="services-available"></a>
## Services Available

<a id="physicsinformednnservice"></a>
### PhysicsInformedNNService
- **Description:** Solving PDEs and parameter inference using PINNs.
- **Key Features:**
  - Forward/inverse solution of PDEs
  - Multi-physics coupling
  - Parameter estimation
- **API Endpoints:**
  - `POST /api/physics/computational/pinn/solve` - Solve PDE
  - `POST /api/physics/computational/pinn/infer` - Parameter inference
- **Schemas:** `ComputationalPhysicsRequest` / `ComputationalPhysicsResponse`

<a id="solidstatephysicsservice"></a>
### SolidStatePhysicsService
- **Description:** Calculations of electronic structure and material properties.
- **Key Features:**
  - Band structure (DFT/ASE)
  - Thermal/electronic properties
  - Integration with workflows
- **API Endpoints:**
  - `POST /api/physics/computational/solid-state/band-structure`
  - `POST /api/physics/computational/solid-state/properties`
- **Schemas:** See `app/domains/physics/models/`

<a id="installation-requirements"></a>
## Installation Requirements
```bash
pip install numpy scipy deepxde ase
```

<a id="quick-start"></a>
## Quick Start
```python
from app.domains.physics.computational.physics_informed_nn_service import PhysicsInformedNNService

service = PhysicsInformedNNService()
solution = await service.solve_pde(params)
```

<a id="scientific-background"></a>
## Scientific Background
PINNs for solving PDEs; electronic structure methods for materials.

<a id="performance-considerations"></a>
## Performance Considerations
- Training PINNs can be expensive; use GPU.
- Mesh sizes and discretization affect memory/time.

<a id="testing"></a>
## Testing
```bash
pytest tests/physics/ -v
```

<a id="related-services"></a>
## Related Services
- [Mathematics](../../mathematics/README.md)
- [Astronomy](../../../../../../../atlas/app/domains/astronomy/README.md)
