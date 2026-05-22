# Physics Domain - AXIOM ATLAS

## Overview
El dominio de Physics en AXIOM ATLAS proporciona herramientas avanzadas para simulación y computación física, incluyendo física clásica, cuántica, de plasma y computacional. Cubre áreas como mecánica clásica, electrodinámica, mecánica cuántica, física de partículas y más, integrando algoritmos avanzados y modelos de IA para investigación científica responsable. Este dominio facilita simulaciones complejas, análisis de fenómenos físicos y generación de hipótesis, siempre con énfasis en precisión y validación física.

## API base paths (montados)
- `GET /physics` — raíz del dominio Physics.
- `GET /api/quantum-physics` — endpoints de Física Cuántica.
- `GET /api/quantum-computing` — endpoints de Computación Cuántica.
- `GET /api/quantum-algorithms` — endpoints de Algoritmos Cuánticos.

Para detalles de endpoints, métodos y ejemplos `curl`, ver la guía:
- [Physics API Guide](../../app/domains/physics/API_GUIDE.md)

## Services Available

### QuantumComputingService
- **Description:** Servicio de computación cuántica para simulaciones y algoritmos cuánticos.
- **Key Features:**
  - Simulación de circuitos cuánticos.
  - Algoritmos cuánticos (QAOA, VQE, Grover).
  - Análisis de entrelazamiento cuántico.
  - Optimización cuántica.
- **Endpoints:** Ver la [Physics API Guide](../../app/domains/physics/API_GUIDE.md). Rutas base: `/api/quantum-computing/*` y `/api/quantum-algorithms/*`.
- **Input Schema:** `QuantumComputingRequest` (ver `app/domains/physics/models/requests.py`).
- **Output Schema:** `QuantumComputingResponse` (ver `app/domains/physics/models/responses.py`).
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### QuantumChemistryService
- **Description:** Servicio de química cuántica para cálculos de estructura molecular.
- **Key Features:**
  - Cálculos de estructura electrónica.
  - Análisis de orbitales moleculares.
  - Predicción de propiedades moleculares.
  - Optimización de geometría molecular.
- **Endpoints:** Ver la [Physics API Guide](../../app/domains/physics/API_GUIDE.md).
- **Input Schema:** `QuantumChemistryRequest`.
- **Output Schema:** `QuantumChemistryResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### ParticlePhysicsService
- **Description:** Servicio de física de partículas para análisis de colisiones y resonancias.
- **Key Features:**
  - Análisis de colisiones de partículas.
  - Búsqueda de resonancias.
  - Simulación de decaimientos.
  - Análisis de secciones eficaces.
- **Endpoints:** Ver la [Physics API Guide](../../app/domains/physics/API_GUIDE.md).
- **Input Schema:** `ParticlePhysicsRequest`.
- **Output Schema:** `ParticlePhysicsResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### PlasmaPhysicsService
- **Description:** Servicio de física de plasma para simulaciones de plasmas.
- **Key Features:**
  - Simulaciones de plasmas magnetizados.
  - Análisis de inestabilidades de plasma.
  - Modelado de fusión nuclear.
  - Análisis de turbulencia de plasma.
- **Endpoints:** Ver la [Physics API Guide](../../app/domains/physics/API_GUIDE.md).
- **Input Schema:** `PlasmaPhysicsRequest`.
- **Output Schema:** `PlasmaPhysicsResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### ClassicalMechanicsService
- **Description:** Servicio de mecánica clásica para análisis de sistemas dinámicos.
- **Key Features:**
  - Análisis de sistemas dinámicos.
  - Simulaciones de mecánica celeste.
  - Análisis de estabilidad.
  - Optimización de trayectorias.
- **Endpoints:** Ver la [Physics API Guide](../../app/domains/physics/API_GUIDE.md).
- **Input Schema:** `ClassicalMechanicsRequest`.
- **Output Schema:** `ClassicalMechanicsResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### ElectrodynamicsService
- **Description:** Servicio de electrodinámica para análisis de campos electromagnéticos.
- **Key Features:**
  - Análisis de campos electromagnéticos.
  - Simulaciones de ondas electromagnéticas.
  - Análisis de antenas.
  - Modelado de dispositivos electromagnéticos.
- **Endpoints:** Ver la [Physics API Guide](../../app/domains/physics/API_GUIDE.md).
- **Input Schema:** `ElectrodynamicsRequest`.
- **Output Schema:** `ElectrodynamicsResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

## Installation Requirements

```bash
# Core dependencies
pip install -r requirements-core.txt

# Domain-specific dependencies
pip install -r requirements-physics.txt
```

## Quick Start

### Python SDK
```python
from app.domains.physics.services.quantum_computing import QuantumComputingService

# Initialize service
service = QuantumComputingService()

# Simulate quantum circuit
result = await service.simulate_circuit(circuit_params)

print(result)
```

### REST API
```bash
curl -X GET "http://localhost:8000/api/quantum-computing/info"
```

## Scientific Background
Este dominio se basa en herramientas estándar como Qiskit, OpenFermion, LAMMPS y métodos numéricos para física computacional. Referencias clave incluyen avances en computación cuántica y simulaciones físicas.

### Key Publications
1. Abraham et al. (2019). "Qiskit: An Open-source Framework for Quantum Computing". *arXiv preprint arXiv:1905.11946*.
2. McClean et al. (2020). "OpenFermion: The Electronic Structure Package for Quantum Computers". *Quantum Science and Technology*.

### Algorithms Implemented
- **Quantum Algorithms:** QAOA, VQE, Grover, O(2^n) complexity.
- **Molecular Dynamics:** Verlet integration, O(n²) complexity.
- **Monte Carlo:** Metropolis-Hastings, O(n) complexity.

## Performance Considerations
- **Computational Complexity:** Varía por simulación, e.g., O(2^n) para sistemas cuánticos.
- **Memory Requirements:** Hasta 4GB para simulaciones cuánticas grandes.
- **GPU Acceleration:** Soportado para cálculos paralelos.
- **Recommended Parameters:** Ajustar según precisión y recursos disponibles.

## Limitations
- No sustituye experimentos físicos reales.
- Limitado a sistemas computablemente tratables.
- Requiere validación física de resultados.

## Testing

### Run domain-specific tests:
```bash
# Unit tests
pytest tests/unit/physics/ -v

# Integration tests
pytest tests/integration/physics/ -v

# With coverage
pytest tests/physics/ --cov=app/domains/physics --cov-report=html
```

## Related Services
- [Mathematics](../MATHEMATICS_DOMAIN.md)
- [Chemistry](../CHEMISTRY_DOMAIN.md)
- [Biology](../BIOLOGY_DOMAIN.md)

## Contributing
See [CONTRIBUTING.md](../../CONTRIBUTING.md) in project root.

## License
See [LICENSE](../../LICENSE.md).

## Support
- **Documentation:** [Full docs](../../README.md)
- **Issues:** [GitHub Issues](https://github.com/org/axiom-atlas/issues)
- **Discussions:** [GitHub Discussions](https://github.com/org/axiom-atlas/discussions)
