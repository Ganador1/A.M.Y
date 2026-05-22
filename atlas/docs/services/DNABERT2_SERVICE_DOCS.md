# DNABERT-2 Genomics Service

## Alcance
- Servicio: `DNABERT2GenomicsService` (`app/domains/biology/services/dnabert2_service.py`).
- Propósito: Proporcionar utilidades básicas de análisis de secuencias genómicas inspiradas en el modelo DNABERT-2.
- Implementación: Versión ligera (lightweight) basada en heurísticas y procesamiento de k-mers, diseñada para ser reemplazada por un backend de HuggingFace si es necesario.

## Capacidades
- **Tokenización de Secuencias (k-mers)**: Divide secuencias de ADN en tokens de longitud *k*.
- **Predicción de Motivos**: Identifica motivos conocidos como TATA-box e islas CpG.
- **Clasificación de Promotores**: Clasifica secuencias como promotores o no promotores basándose en la presencia de motivos y densidad de CpG.

## Acciones Soportadas (`process_request`)

### `encode_sequence`
Tokeniza una secuencia de ADN en k-mers.
- **Entrada**:
  - `sequence` (str): Secuencia de ADN (A, C, G, T, N).
  - `k` (int, opcional): Tamaño del k-mer (por defecto usa la configuración del servicio, usualmente 6).
- **Salida**:
  - `tokens` (List[str]): Lista de k-mers generados.
  - `length` (int): Longitud de la secuencia original.

### `predict_motifs`
Busca motivos biológicos específicos en la secuencia.
- **Entrada**:
  - `sequence` (str): Secuencia de ADN.
- **Salida**:
  - `motifs` (Dict): Diccionario con posiciones de `TATA_box` y `CpG_islands`.

### `classify_promoter`
Realiza una clasificación binaria de la secuencia.
- **Entrada**:
  - `sequence` (str): Secuencia de ADN.
- **Salida**:
  - `label` (str): "promoter" o "non_promoter".
  - `confidence` (float): Puntuación de confianza (0.0 a 1.0).
  - `has_tata` (bool): Indica si se encontró un TATA-box.

## Configuración
- `k` (int): Tamaño predeterminado de k-mer para tokenización.

## Ejemplo de Uso
```python
from app.domains.biology.services.dnabert2_service import DNABERT2GenomicsService

service = DNABERT2GenomicsService()
result = await service.process_request({
    "action": "classify_promoter",
    "sequence": "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
})
print(result["label"])
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_dnabert2_service.py`
