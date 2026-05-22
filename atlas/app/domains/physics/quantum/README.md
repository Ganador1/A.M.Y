# Quantum Physics and Computing - Scientific Computing Services

## Overview
El subdominio de Física Cuántica en AXIOM ATLAS reúne servicios para simulación de sistemas cuánticos, construcción y ejecución de circuitos cuánticos, algoritmos híbridos (VQE, QAOA), diseño de circuitos superconductores y análisis de datos de física de partículas. Integra bibliotecas como QuTiP, Qiskit, Cirq y herramientas de análisis científico para ofrecer capacidades reproducibles y escalables.

Estos servicios soportan investigación en tecnologías cuánticas, materiales avanzados, óptica cuántica y física de altas energías, con rutas API consistentes y esquemas bien definidos.

## API base paths
- `GET /api/quantum-physics` — Física Cuántica (QuTiP)
- `GET /api/quantum-computing` — Computación Cuántica (Qiskit/Cirq)
- `GET /api/quantum-algorithms` — Algoritmos Cuánticos (VQE, QAOA, Grover, QFT, Shor)

Para ejemplos `curl` y lista completa de endpoints, ver:
- [Physics API Guide](../../physics/API_GUIDE.md)

## Services Available

### QuantumPhysicsService
- **Description:** Simulación de sistemas cuánticos (espín, osciladores, óptica cuántica) con QuTiP.
- **Key Features:**
  - Evolución de estados y densidades
  - Sistemas abiertos y disipación
  - Modelos Jaynes-Cummings
- **API Endpoints:**
  - `POST /api/quantum-physics/spin-evolution` - Evolución de espín
  - `POST /api/quantum-physics/harmonic-oscillator` - Oscilador armónico
  - `POST /api/quantum-physics/quantum-optics` - Óptica cuántica
- **Input Schema:** `PhysicsQuantumRequest` (ver `app/domains/physics/models/requests.py`)
- **Output Schema:** `PhysicsQuantumResponse` (ver `app/domains/physics/models/responses.py`)
- **Examples:** Ver [EXAMPLES.md](../EXAMPLES.md)

### QuantumComputingService
- **Description:** Construcción y simulación de circuitos con Qiskit/Cirq; soporta algoritmos variacionales.
- **Key Features:**
  - Construcción de circuitos y transpilation
  - Simulación con ruido y backends locales
  - Métricas de fidelidad
- **API Endpoints:**
  - `POST /api/quantum-computing/vqe` - VQE
  - `POST /api/quantum-computing/qaoa/maxcut` - QAOA (MaxCut)
  - `POST /api/quantum-computing/grover-search` - Búsqueda de Grover
  - `POST /api/quantum-computing/quantum-fourier-transform` - QFT
- **Input Schema:** `QuantumCircuitRequest`
- **Output Schema:** `QuantumCircuitResponse`
- **Examples:** Ver [EXAMPLES.md](../EXAMPLES.md)

### QuantumAlgorithmsService
- **Description:** Catálogo y ejecuciones de algoritmos cuánticos clave.
- **Key Features:**
  - VQE, QAOA, Grover, Shor, QFT
  - Integración híbrida clásico-cuántico
- **API Endpoints:**
  - `POST /api/quantum-algorithms/qft` - Quantum Fourier Transform
  - `POST /api/quantum-algorithms/grover` - Búsqueda de Grover
- **Schemas:** Ver `models/requests.py` y `models/responses.py`
- **Más detalle:** Ver [ALGORITHMS.md](./ALGORITHMS.md)

### SuperconductingDesignService
- **Description:** Diseño y optimización de circuitos superconductores (qubits, resonadores).
- **Estado:** Endpoint no montado actualmente; consultar roadmap.
- **Examples:** Ver [EXAMPLES.md](../EXAMPLES.md)

### ParticlePhysicsService
- **Description:** Análisis de datos de colisionadores; reconstrucción de jets, búsqueda de nueva física.
- **API Endpoints:** `POST /api/physics/particle/analyze-events`
- **Examples:** Ver [EXAMPLES.md](../EXAMPLES.md)

## Installation Requirements

```bash
pip install qutip qiskit cirq numpy scipy matplotlib
```

## Quick Start

### Python SDK
```python
from app.domains.physics.quantum.quantum_physics_service import QuantumPhysicsService

service = QuantumPhysicsService()
result = await service.simulate_spin_evolution(Bx=0, By=0, Bz=1.0, t_max=10, n_points=100)
print(result)
```

### REST API
```bash
curl -X POST "http://localhost:8000/api/quantum-physics/spin-evolution" \
  -H "Content-Type: application/json" \
  -d '{"Bx": 0, "By": 0, "Bz": 1.0, "t_max": 10, "n_points": 100}'
```

## Scientific Background
Basado en mecánica cuántica, teoría de circuitos cuánticos y óptica cuántica. Se emplean simuladores clásicos para estudiar comportamientos y validar hipótesis antes de acceso a hardware.

### Key Publications
1. Nielsen & Chuang (2010). "Quantum Computation and Quantum Information".
2. Peruzzo et al. (2014). "A variational eigenvalue solver on a photonic quantum processor".

### Algorithms Implemented
- Ver [ALGORITHMS.md](./ALGORITHMS.md) para detalles y complejidades.

## Performance Considerations
- Simulaciones crecen exponencialmente con el número de qubits.
- Controlar parámetros `n_max`, `n_points`, profundidad de circuitos.
- Considerar ruido y decoherencia en simulaciones realistas.

## Limitations
- Simulación clásica de sistemas cuánticos; escalabilidad limitada.
- Resultados ideales requieren validación en hardware.

## Testing

```bash
pytest tests/physics/ -v
```

## Related Services
- [Mathematics](../../mathematics/README.md)
- [Chemistry](../../chemistry/README.md)

## Contributing
Ver [CONTRIBUTING.md](../../../CONTRIBUTING.md) en la raíz.

## License
Ver [LICENSE](../../../LICENSE.md).

## Support
- **Documentation:** [Full docs](../../../docs/README.md)
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions