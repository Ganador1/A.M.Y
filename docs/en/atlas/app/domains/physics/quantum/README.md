> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="quantum-physics-and-computing---scientific-computing-services"></a>
# Quantum Physics and Computing - Scientific Computing Services

<a id="overview"></a>
## Overview
The Quantum Physics subdomain in AXIOM ATLAS brings together services for simulating quantum systems, building and executing quantum circuits, hybrid algorithms (VQE, QAOA), designing superconducting circuits, and analyzing particle physics data. It integrates libraries such as QuTiP, Qiskit, Cirq, and scientific analysis tools to offer reproducible and scalable capabilities.

These services support research in quantum technologies, advanced materials, quantum optics, and high-energy physics, with consistent API routes and well-defined schemas.

<a id="api-base-paths"></a>
## API base paths
- `GET /api/quantum-physics` — Quantum Physics (QuTiP)
- `GET /api/quantum-computing` — Quantum Computing (Qiskit/Cirq)
- `GET /api/quantum-algorithms` — Quantum Algorithms (VQE, QAOA, Grover, QFT, Shor)

For `curl` examples and the complete list of endpoints, see:
- [Physics API Guide](../../../../../../../atlas/app/domains/physics/API_GUIDE.md)

<a id="services-available"></a>
## Services Available

<a id="quantumphysicsservice"></a>
### QuantumPhysicsService
- **Description:** Simulation of quantum systems (spin, oscillators, quantum optics) with QuTiP.
- **Key Features:**
  - Evolution of states and densities
  - Open systems and dissipation
  - Jaynes-Cummings models
- **API Endpoints:**
  - `POST /api/quantum-physics/spin-evolution` - Spin evolution
  - `POST /api/quantum-physics/harmonic-oscillator` - Harmonic oscillator
  - `POST /api/quantum-physics/quantum-optics` - Quantum optics
- **Input Schema:** `PhysicsQuantumRequest` (see `app/domains/physics/models/requests.py`)
- **Output Schema:** `PhysicsQuantumResponse` (see `app/domains/physics/models/responses.py`)
- **Examples:** See [EXAMPLES.md](../../../../../../../atlas/app/domains/physics/EXAMPLES.md)

<a id="quantumcomputingservice"></a>
### QuantumComputingService
- **Description:** Circuit construction and simulation with Qiskit/Cirq; supports variational algorithms.
- **Key Features:**
  - Circuit construction and transpilation
  - Simulation with noise and local backends
  - Fidelity metrics
- **API Endpoints:**
  - `POST /api/quantum-computing/vqe` - VQE
  - `POST /api/quantum-computing/qaoa/maxcut` - QAOA (MaxCut)
  - `POST /api/quantum-computing/grover-search` - Grover's search
  - `POST /api/quantum-computing/quantum-fourier-transform` - QFT
- **Input Schema:** `QuantumCircuitRequest`
- **Output Schema:** `QuantumCircuitResponse`
- **Examples:** See [EXAMPLES.md](../../../../../../../atlas/app/domains/physics/EXAMPLES.md)

<a id="quantumalgorithmsservice"></a>
### QuantumAlgorithmsService
- **Description:** Catalog and executions of key quantum algorithms.
- **Key Features:**
  - VQE, QAOA, Grover, Shor, QFT
  - Hybrid classical-quantum integration
- **API Endpoints:**
  - `POST /api/quantum-algorithms/qft` - Quantum Fourier Transform
  - `POST /api/quantum-algorithms/grover` - Grover's search
- **Schemas:** See `models/requests.py` and `models/responses.py`
- **More detail:** See [ALGORITHMS.md](ALGORITHMS.md)

<a id="superconductingdesignservice"></a>
### SuperconductingDesignService
- **Description:** Design and optimization of superconducting circuits (qubits, resonators).
- **Status:** Endpoint not currently mounted; consult roadmap.
- **Examples:** See [EXAMPLES.md](../../../../../../../atlas/app/domains/physics/EXAMPLES.md)

<a id="particlephysicsservice"></a>
### ParticlePhysicsService
- **Description:** Collider data analysis; jet reconstruction, new physics searches.
- **API Endpoints:** `POST /api/physics/particle/analyze-events`
- **Examples:** See [EXAMPLES.md](../../../../../../../atlas/app/domains/physics/EXAMPLES.md)

<a id="installation-requirements"></a>
## Installation Requirements

```bash
pip install qutip qiskit cirq numpy scipy matplotlib
```

<a id="quick-start"></a>
## Quick Start

<a id="python-sdk"></a>
### Python SDK
```python
from app.domains.physics.quantum.quantum_physics_service import QuantumPhysicsService

service = QuantumPhysicsService()
result = await service.simulate_spin_evolution(Bx=0, By=0, Bz=1.0, t_max=10, n_points=100)
print(result)
```

<a id="rest-api"></a>
### REST API
```bash
curl -X POST "http://localhost:8000/api/quantum-physics/spin-evolution" \
  -H "Content-Type: application/json" \
  -d '{"Bx": 0, "By": 0, "Bz": 1.0, "t_max": 10, "n_points": 100}'
```

<a id="scientific-background"></a>
## Scientific Background
Based on quantum mechanics, quantum circuit theory, and quantum optics. Classical simulators are used to study behaviors and validate hypotheses before accessing hardware.

<a id="key-publications"></a>
### Key Publications
1. Nielsen & Chuang (2010). "Quantum Computation and Quantum Information".
2. Peruzzo et al. (2014). "A variational eigenvalue solver on a photonic quantum processor".

<a id="algorithms-implemented"></a>
### Algorithms Implemented
- See [ALGORITHMS.md](ALGORITHMS.md) for details and complexities.

<a id="performance-considerations"></a>
## Performance Considerations
- Simulations grow exponentially with the number of qubits.
- Control parameters `n_max`, `n_points`, circuit depth.
- Consider noise and decoherence in realistic simulations.

<a id="limitations"></a>
## Limitations
- Classical simulation of quantum systems; limited scalability.
- Ideal results require validation on hardware.

<a id="testing"></a>
## Testing

```bash
pytest tests/physics/ -v
```

<a id="related-services"></a>
## Related Services
- [Mathematics](../../mathematics/README.md)
- [Chemistry](../../../../../../../atlas/app/domains/chemistry/README.md)

<a id="contributing"></a>
## Contributing
See CONTRIBUTING.md (`../../../CONTRIBUTING.md`; resource not included) at the root.

<a id="license"></a>
## License
See LICENSE (`../../../LICENSE.md`; resource not included).

<a id="support"></a>
## Support
- **Documentation:** Full docs (`../../../docs/README.md`; resource not included)
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
