> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="dnabert-2-genomics-service"></a>
# DNABERT-2 Genomics Service

<a id="alcance"></a>
## Scope
- Service: `DNABERT2GenomicsService` (`app/domains/biology/services/dnabert2_service.py`).
- Purpose: Provide basic genomic sequence analysis utilities inspired by the DNABERT-2 model.
- Implementation: Lightweight version based on heuristics and k-mer processing, designed to be replaced by a HuggingFace backend if necessary.

<a id="capacidades"></a>
## Capabilities
- **Sequence Tokenization (k-mers)**: Splits DNA sequences into tokens of length *k*.
- **Motif Prediction**: Identifies known motifs such as TATA-box and CpG islands.
- **Promoter Classification**: Classifies sequences as promoters or non-promoters based on the presence of motifs and CpG density.

<a id="acciones-soportadas-process_request"></a>
## Supported Actions (`process_request`)

<a id="encode_sequence"></a>
### `encode_sequence`
Tokenizes a DNA sequence into k-mers.
- **Input**:
  - `sequence` (str): DNA sequence (A, C, G, T, N).
  - `k` (int, optional): K-mer size (by default uses the service configuration, usually 6).
- **Output**:
  - `tokens` (List[str]): List of generated k-mers.
  - `length` (int): Length of the original sequence.

<a id="predict_motifs"></a>
### `predict_motifs`
Searches for specific biological motifs in the sequence.
- **Input**:
  - `sequence` (str): DNA sequence.
- **Output**:
  - `motifs` (Dict): Dictionary with positions of `TATA_box` and `CpG_islands`.

<a id="classify_promoter"></a>
### `classify_promoter`
Performs a binary classification of the sequence.
- **Input**:
  - `sequence` (str): DNA sequence.
- **Output**:
  - `label` (str): "promoter" or "non_promoter".
  - `confidence` (float): Confidence score (0.0 to 1.0).
  - `has_tata` (bool): Indicates whether a TATA-box was found.

<a id="configuración"></a>
## Configuration
- `k` (int): Default k-mer size for tokenization.

<a id="ejemplo-de-uso"></a>
## Usage Example
```python
from app.domains.biology.services.dnabert2_service import DNABERT2GenomicsService

service = DNABERT2GenomicsService()
result = await service.process_request({
    "action": "classify_promoter",
    "sequence": "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
})
print(result["label"])
```

<a id="pruebas"></a>
## Tests
- Run unit tests:
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_dnabert2_service.py`
