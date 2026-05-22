# Services in Biology Domain

## ComputationalBiologyService
**Description**: Service for computational biology operations covering neuroscience, genomics, and ecology.

**Key Features**:
- Neural simulations using Brian2 and NEURON
- Genetic network analysis with NetworkX
- Ecological modeling with SciPy

**Usage**:
```python
from axiom.domains.biology import ComputationalBiologyService
service = ComputationalBiologyService()
simulation = service.run_neural_simulation(parameters)
```

## BiomedicalNLPService
**Description**: Biomedical natural language processing using BioBERT for entity extraction and semantic analysis.

**Key Features**:
- Entity extraction (genes, proteins, diseases)
- Semantic similarity analysis
- Literature search enhancement

**Usage**:
```python
from axiom.domains.biology import BiomedicalNLPService
service = BiomedicalNLPService()
entities = service.extract_entities("The p53 protein plays a crucial role in cancer development.")
```

## BioGPTService
**Description**: Biomedical text generation with BioGPT.

**Key Features**:
- Hypothesis generation
- Literature summaries
- Concept explanations

**Usage**:
```python
from axiom.domains.biology import BioGPTService
service = BioGPTService()
text = service.generate("Explain the process of DNA replication")
```

## AdvancedGenomicsService
**Description**: Advanced genomic analyses such as variant calling and pharmacogenomics.

**Key Features**:
- Cancer analysis
- Pharmacogenomics
- Structural variants

**Usage**:
```python
from axiom.domains.biology import AdvancedGenomicsService
service = AdvancedGenomicsService()
variants = service.call_variants(sample_data)
```

## GenomicsService
**Description**: Basic genomics services with secure validations.

**Key Features**:
- Sequence analysis
- Dry-run validations
- Secure processing

**Usage**:
```python
from axiom.domains.biology import GenomicsService
service = GenomicsService()
result = service.analyze_sequence(dna_sequence)
```

## DNABERT2Service
**Description**: DNA analysis using DNABERT2.

**Key Features**:
- Functional predictions
- DNA sequence analysis
- Genomic feature extraction

**Usage**:
```python
from axiom.domains.biology import DNABERT2Service
service = DNABERT2Service()
predictions = service.predict_function(dna_sequence)
```

## ProtGPT2Service
**Description**: Protein sequence generation with ProtGPT2.

**Key Features**:
- Sequence design
- Protein engineering
- Structure prediction

**Usage**:
```python
from axiom.domains.biology import ProtGPT2Service
service = ProtGPT2Service()
sequence = service.generate_protein(constraints)
```