# API Guide for Physics Domain

## Authentication
Most endpoints require API key authentication. Include `Authorization: Bearer YOUR_API_KEY` in headers.

## Base Paths
- Physics domain root: `GET /physics/`, `GET /physics/services`
- Quantum Physics: `GET/POST /api/quantum-physics/*`
- Quantum Computing: `GET/POST /api/quantum-computing/*`
- Quantum Algorithms: `GET/POST /api/quantum-algorithms/*`

## Key Endpoints

### Physics Domain Root
- **GET /physics/**: Domain info.
- **GET /physics/services**: List available services.

### Quantum Physics (`/api/quantum-physics`)
- **POST /spin-evolution**: Simulate spin evolution in magnetic field.
  - Parameters: `Bx`, `By`, `Bz`, `t_max`, `n_points`
  - Example:
    ```bash
    curl -X POST "http://localhost:8000/api/quantum-physics/spin-evolution" \
         -H "Content-Type: application/json" \
         -d '{"Bx": 0, "By": 0, "Bz": 1.0, "t_max": 10, "n_points": 100}'
    ```
- **POST /harmonic-oscillator**: Quantum harmonic oscillator simulation.
- **POST /two-level-system**: Two-level system with dissipation.
- **POST /entanglement-analysis**: Entanglement metrics for selected states.
- **POST /quantum-optics**: Jaynes–Cummings model simulation.
- **GET /quick-spin/{Bx}/{By}/{Bz}**: Quick spin simulation.

### Quantum Computing (`/api/quantum-computing`)
- **POST /bell-state**: Create Bell states (framework: `qiskit` or `cirq`).
  - Example:
    ```bash
    curl -X POST "http://localhost:8000/api/quantum-computing/bell-state" \
         -H "Content-Type: application/json" \
         -d '{"framework": "qiskit"}'
    ```
- **POST /grover-search**: Grover search on target state.
- **POST /quantum-fourier-transform**: Quantum Fourier Transform.
- **POST /vqe**: Variational Quantum Eigensolver.
- **POST /quantum-classical-comparison**: Compare quantum vs classical.
- Más endpoints avanzados disponibles en `/docs`.

### Quantum Algorithms (`/api/quantum-algorithms`)
- **POST /qaoa/optimize**: QAOA optimization.
  - Example:
    ```bash
    curl -X POST "http://localhost:8000/api/quantum-algorithms/qaoa/optimize" \
         -H "Content-Type: application/json" \
         -d '{"graph": [[0,1],[1,2],[2,0]], "p": 2}'
    ```
- **POST /vqe/ground-state**: Ground state via VQE.
- **POST /quantum-advantage**: Analyze quantum advantage.
- **GET /circuits**: List available circuits.
- **GET /backends**: List available backends.
- **GET /health**: Service health.

For full API documentation, refer to the OpenAPI spec at `/docs`.