# Dominio: Physics

## Qué es
Dominio para simulación y análisis en física: computación cuántica, algoritmos híbridos (QAOA/VQE), física de partículas, plasma y PINNs.

## Ubicación en el código
- Paquete: `app/domains/physics/`
- Router consolidado: `app/domains/physics/routers/api.py` (declara `prefix="/physics"`)
- Routers específicos: `app/domains/physics/routers/quantum_algorithms.py`, `quantum_computing.py`, `quantum_physics.py`, etc.
- Servicios: `app/domains/physics/services/`

## Servicios principales
- `QuantumAlgorithmsService`: `app/domains/physics/services/quantum_algorithms_service.py`
- `AsyncQuantumComputingService`: `app/domains/physics/services/async_quantum_computing_service.py`
- `PhysicsInformedNNService`: `app/domains/physics/services/physics_informed_nn_service.py`
- `ParticlePhysicsService`: `app/domains/physics/services/particle_physics_service.py`
- Otros: `quantum_chemistry_service.py`, `solid_state_physics.py`, `gravitational_lensing.py`

## API (router consolidado)
- `GET /physics/` → info del dominio
- `POST /physics/compute`
- `POST /physics/analyze`

## Entrada HTTP (routers de plataforma)
Además del router del dominio, el repo tiene routers en `app/routers/`:
- `app/routers/quantum_algorithms.py` (prefix canónico documentado en API_REFERENCE)
- `app/routers/quantum_physics.py`, `app/routers/quantum_computing.py`

## Referencias cercanas al código
- `app/domains/physics/README.md`
- `app/domains/physics/API_GUIDE.md`
- `app/domains/physics/SERVICES.md`
- `app/domains/physics/EXAMPLES.md`
