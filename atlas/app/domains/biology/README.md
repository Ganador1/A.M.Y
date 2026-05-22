# Biology - Scientific Computing Services

## Overview
El dominio de Biology en AXIOM ATLAS proporciona herramientas avanzadas para computación biológica, incluyendo análisis genómico, procesamiento de lenguaje natural biomédico, simulaciones neuronales y más. Cubre áreas como genómica, biología computacional, neurociencia y ecología, integrando modelos de IA como BioGPT, DNABERT2 y ProtGPT2 para investigación científica responsable. Este dominio facilita simulaciones, análisis de datos y generación de hipótesis en biología, siempre con énfasis en ética y seguridad.

## Services Available

### ComputationalBiologyService
- **Description:** Servicio para operaciones de biología computacional, cubriendo neurociencia, genómica avanzada y ecología.
- **Key Features:**
  - Simulaciones neuronales con Brian2 y NEURON.
  - Análisis de redes genéticas con NetworkX.
  - Modelado ecológico con SciPy.
- **API Endpoints:**
  - `POST /api/biology/computational/simulate` - Ejecutar simulación.
  - `GET /api/biology/computational/results/{id}` - Obtener resultados.
- **Input Schema:** `BiologyComputationalRequest` (ver `app/domains/biology/models/requests.py`).
- **Output Schema:** `BiologyComputationalResponse` (ver `app/domains/biology/models/responses.py`).
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### BiomedicalNLPService
- **Description:** Procesamiento de lenguaje natural biomédico utilizando BioBERT para extracción de entidades y análisis semántico.
- **Key Features:**
  - Extracción de entidades (genes, proteínas, enfermedades).
  - Análisis de similitud semántica.
  - Mejora de búsquedas en literatura.
- **API Endpoints:**
  - `POST /api/biology/biomedical-nlp/extract-entities` - Extracción de entidades.
  - `POST /api/biology/biomedical-nlp/semantic-similarity` - Análisis de similitud.
- **Input Schema:** `EntityExtractionRequest`.
- **Output Schema:** `EntityExtractionResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### BioGPTService
- **Description:** Generación de texto biomédico con BioGPT.
- **Key Features:**
  - Generación de hipótesis.
  - Resúmenes de literatura.
  - Explicación de conceptos.
- **API Endpoints:**
  - `POST /api/biology/biogpt/generate` - Generar texto.
- **Input Schema:** `BioGPTGenerationRequest`.
- **Output Schema:** `BioGPTResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### AdvancedGenomicsService
- **Description:** Análisis genómicos avanzados como llamada de variantes y farmacogenómica.
- **Key Features:**
  - Análisis de cáncer.
  - Farmacogenómica.
  - Variantes estructurales.
- **API Endpoints:**
  - `POST /api/biology/advanced-genomics/variant-calling` - Llamada de variantes.
- **Input Schema:** `VariantCallingRequest`.
- **Output Schema:** `VariantCallingResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### GenomicsService
- **Description:** Servicios básicos de genómica con validaciones seguras.
- **Key Features:**
  - Análisis de secuencias.
  - Dry-run para herramientas como DeepVariant.
- **API Endpoints:**
  - `POST /api/biology/genomics/analyze` - Análisis genómico.
- **Input Schema:** `GenomicsRequest`.
- **Output Schema:** `GenomicsResponse`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### DNABERT2Service
- **Description:** Análisis de secuencias de ADN con DNABERT2.
- **Key Features:**
  - Predicción de funciones genéticas.
- **API Endpoints:**
  - `POST /api/biology/dnabert2/predict` - Predicción.
- **Input Schema:** `DNABERT2Request`.
- **Output Schema:** `DNABERT2Response`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

### ProtGPT2Service
- **Description:** Generación de secuencias de proteínas con ProtGPT2.
- **Key Features:**
  - Diseño de proteínas.
- **API Endpoints:**
  - `POST /api/biology/protgpt2/generate` - Generar secuencia.
- **Input Schema:** `ProtGPT2Request`.
- **Output Schema:** `ProtGPT2Response`.
- **Examples:** Ver [EXAMPLES.md](./EXAMPLES.md).

## Installation Requirements

```bash
# Core dependencies
pip install -r requirements-core.txt

# Domain-specific dependencies
pip install -r requirements-biology.txt
```

## Quick Start

### Python SDK
```python
from app.domains.biology.services.computational_biology import ComputationalBiologyService

# Initialize service
service = ComputationalBiologyService()

# Execute method
result = await service.simulate_neural_network(params)

print(result)
```

### REST API
```bash
curl -X POST "http://localhost:8000/api/biology/computational/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "param1": "value1",
    "param2": "value2"
  }'
```

## Scientific Background
Este dominio se basa en herramientas estándar como BioPython, NetworkX y modelos de IA para biología computacional. Referencias clave incluyen avances en genómica y neurociencia.

### Key Publications
1. Cock et al. (2009). "Biopython: freely available Python tools for computational molecular biology and bioinformatics". *Bioinformatics*. DOI: 10.1093/bioinformatics/btp163
2. Hines et al. (2009). "NEURON and Python". *Frontiers in Neuroinformatics*. DOI: 10.3389/neuro.11.001.2009

### Algorithms Implemented
- **Neural Simulation:** Hodgkin-Huxley models, O(n) complexity.
- **Network Analysis:** Graph algorithms, O(v+e) complexity.

## Performance Considerations
- **Computational Complexity:** Varía por simulación, e.g., O(n) para redes pequeñas.
- **Memory Requirements:** Hasta 1GB para simulaciones grandes.
- **GPU Acceleration:** Soportado para modelos de IA.
- **Recommended Parameters:** Ajustar según recursos disponibles.

## Limitations
- No sustituye experimentos reales.
- Limitado a datos no sensibles.
- Requiere validación ética.

## Testing

### Run domain-specific tests:
```bash
# Unit tests
pytest tests/unit/biology/ -v

# Integration tests
pytest tests/integration/biology/ -v

# With coverage
pytest tests/biology/ --cov=app/domains/biology --cov-report=html
```

## Related Services
- [Chemistry](../chemistry/README.md)
- [Neuroscience](../neuroscience/README.md)

## Contributing
See [CONTRIBUTING.md](../../CONTRIBUTING.md) in project root.

## License
See [LICENSE](../../LICENSE.md).

## Support
- **Documentation:** [Full docs](../../docs/README.md)
- **Issues:** [GitHub Issues](https://github.com/org/axiom-atlas/issues)
- **Discussions:** [GitHub Discussions](https://github.com/org/axiom-atlas/discussions)