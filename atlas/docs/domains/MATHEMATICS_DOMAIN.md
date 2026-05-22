# Mathematics Domain - AXIOM ATLAS

## Overview
El dominio de Mathematics en AXIOM ATLAS proporciona herramientas avanzadas para computación matemática, incluyendo álgebra, cálculo, estadísticas, ecuaciones diferenciales, topología y más. Cubre áreas como matemáticas puras, aplicadas, computacionales y topología, integrando algoritmos avanzados y modelos de IA para investigación científica responsable. Este dominio facilita cálculos complejos, análisis de datos y generación de hipótesis matemáticas, siempre con énfasis en precisión y validación.

## Services Available

### MathematicalDiscoveryEngine
- **Description:** Motor de descubrimiento matemático para generación de conjeturas y validación de teoremas.
- **Key Features:**
  - Generación automática de conjeturas matemáticas.
  - Validación de teoremas usando métodos formales.
  - Análisis de patrones en secuencias matemáticas.
  - Integración con sistemas de prueba automática.
- **API Endpoints:**
  - `POST /api/mathematics/discovery/generate-conjectures` - Generar conjeturas.
  - `POST /api/mathematics/discovery/validate-theorem` - Validar teorema.
  - `GET /api/mathematics/discovery/patterns` - Analizar patrones.
- **Input Schema:** `ConjectureRequest` (ver `app/domains/mathematics/models/requests.py`).
- **Output Schema:** `ConjectureResponse` (ver `app/domains/mathematics/models/responses.py`).
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### AutomatedTheoremProvingService
- **Description:** Servicio de demostración automática de teoremas usando métodos formales.
- **Key Features:**
  - Demostración automática de teoremas.
  - Verificación de pruebas matemáticas.
  - Generación de contraejemplos.
  - Análisis de completitud y consistencia.
- **API Endpoints:**
  - `POST /api/mathematics/theorem-proving/prove` - Demostrar teorema.
  - `POST /api/mathematics/theorem-proving/verify` - Verificar prueba.
  - `POST /api/mathematics/theorem-proving/counterexample` - Generar contraejemplo.
- **Input Schema:** `TheoremProvingRequest`.
- **Output Schema:** `TheoremProvingResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### MathPhysicsOrchestrator
- **Description:** Orquestador para problemas que combinan matemáticas y física.
- **Key Features:**
  - Resolución de ecuaciones diferenciales parciales.
  - Análisis de sistemas dinámicos.
  - Simulaciones de fenómenos físicos.
  - Optimización de modelos matemáticos.
- **API Endpoints:**
  - `POST /api/mathematics/physics/solve-pde` - Resolver EDP.
  - `POST /api/mathematics/physics/dynamical-systems` - Análisis de sistemas dinámicos.
  - `POST /api/mathematics/physics/optimize-model` - Optimizar modelo.
- **Input Schema:** `MathPhysicsRequest`.
- **Output Schema:** `MathPhysicsResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### AdvancedAlgebraService
- **Description:** Servicio avanzado de álgebra para operaciones complejas.
- **Key Features:**
  - Álgebra lineal avanzada.
  - Teoría de grupos y anillos.
  - Álgebra abstracta.
  - Cálculo simbólico.
- **API Endpoints:**
  - `POST /api/mathematics/algebra/linear-algebra` - Álgebra lineal.
  - `POST /api/mathematics/algebra/group-theory` - Teoría de grupos.
  - `POST /api/mathematics/algebra/symbolic-calc` - Cálculo simbólico.
- **Input Schema:** `AlgebraRequest`.
- **Output Schema:** `AlgebraResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### StatisticsService
- **Description:** Servicio de análisis estadístico y probabilístico.
- **Key Features:**
  - Análisis descriptivo y inferencial.
  - Distribuciones de probabilidad.
  - Pruebas de hipótesis.
  - Análisis de regresión.
- **API Endpoints:**
  - `POST /api/mathematics/statistics/descriptive` - Análisis descriptivo.
  - `POST /api/mathematics/statistics/inferential` - Análisis inferencial.
  - `POST /api/mathematics/statistics/regression` - Análisis de regresión.
- **Input Schema:** `StatisticsRequest`.
- **Output Schema:** `StatisticsResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### TopologyService
- **Description:** Servicio de topología para análisis de espacios y estructuras.
- **Key Features:**
  - Topología algebraica.
  - Análisis de variedades.
  - Teoría de homotopía.
  - Geometría diferencial.
- **API Endpoints:**
  - `POST /api/mathematics/topology/algebraic` - Topología algebraica.
  - `POST /api/mathematics/topology/manifolds` - Análisis de variedades.
  - `POST /api/mathematics/topology/homotopy` - Teoría de homotopía.
- **Input Schema:** `TopologyRequest`.
- **Output Schema:** `TopologyResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

## Installation Requirements

```bash
# Core dependencies
pip install -r requirements-core.txt

# Domain-specific dependencies
pip install -r requirements-mathematics.txt
```

## Quick Start

### Python SDK
```python
from app.domains.mathematics.services.mathematical_discovery_engine import MathematicalDiscoveryEngine

# Initialize service
engine = MathematicalDiscoveryEngine()

# Generate conjectures
conjectures = await engine.generate_seed_conjectures(domain="number_theory", limit=5)

print(conjectures)
```

### REST API
```bash
curl -X POST "http://localhost:8000/api/mathematics/discovery/generate-conjectures" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "number_theory",
    "limit": 5,
    "complexity": "medium"
  }'
```

## Scientific Background
Este dominio se basa en herramientas estándar como SymPy, SciPy, NumPy y sistemas de prueba automática para matemáticas computacionales. Referencias clave incluyen avances en demostración automática de teoremas y análisis matemático.

### Key Publications
1. Meurer et al. (2017). "SymPy: symbolic computing in Python". *PeerJ Computer Science*. DOI: 10.7717/peerj-cs.103
2. Harrison, J. (2009). "Handbook of Practical Logic and Automated Reasoning". *Cambridge University Press*.

### Algorithms Implemented
- **Theorem Proving:** Resolution, tableaux, O(n²) complexity.
- **Symbolic Computation:** Gröbner bases, O(n³) complexity.
- **Statistical Analysis:** Maximum likelihood, O(n log n) complexity.

## Performance Considerations
- **Computational Complexity:** Varía por algoritmo, e.g., O(n³) para álgebra lineal.
- **Memory Requirements:** Hasta 2GB para cálculos simbólicos complejos.
- **GPU Acceleration:** Soportado para operaciones matriciales.
- **Recommended Parameters:** Ajustar según precisión requerida.

## Limitations
- No sustituye la intuición matemática humana.
- Limitado a problemas computablemente tratables.
- Requiere validación de resultados.

## Testing

### Run domain-specific tests:
```bash
# Unit tests
pytest tests/unit/mathematics/ -v

# Integration tests
pytest tests/integration/mathematics/ -v

# With coverage
pytest tests/mathematics/ --cov=app/domains/mathematics --cov-report=html
```

## Related Services
- [Physics](../PHYSICS_DOMAIN.md)
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
