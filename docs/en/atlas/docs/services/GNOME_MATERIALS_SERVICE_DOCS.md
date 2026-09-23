> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="gnome-materials-discovery-service"></a>
# GNOME Materials Discovery Service

<a id="alcance"></a>
## Scope
- Service: `GNOMEMaterialsService` (`app/domains/chemistry/services/gnome_materials_service.py`).
- Purpose: Emulate materials discovery and property prediction using an internal database of known materials and heuristics.
- Implementation: Lightweight placeholder designed to simulate the capabilities of the GNoME model (Graph Networks for Materials Exploration).

<a id="capacidades"></a>
## Capabilities
- **Candidate Suggestion**: Recommends materials based on a target application (batteries, solar cells, semiconductors, etc.).
- **Property Prediction**: Estimates physical and chemical properties for given formulas.
- **Materials Search**: Allows filtering the internal database by application and specific criteria.

<a id="acciones-soportadas-process_request"></a>
## Supported Actions (`process_request`)

<a id="suggest_candidates"></a>
### `suggest_candidates`
Suggests the best materials for a specific application.
- **Input**:
  - `target` (str): Target application (e.g., "solar", "battery", "superconductor").
  - `top_n` (int, optional): Number of candidates to return (default 3).
- **Output**:
  - `candidates` (List[Dict]): List of materials with their formula, score, and predicted properties.

<a id="predict_properties"></a>
### `predict_properties`
Predicts properties for a specific chemical formula if it exists in the database.
- **Input**:
  - `formula` (str): Chemical formula (e.g., "LiFePO4").
- **Output**:
  - `properties` (Dict): Properties such as conductivity, stability, capacity, etc.

<a id="search_materials"></a>
### `search_materials`
Direct search in the materials database.
- **Input**:
  - `application` (str): Application type.
  - `max_results` (int, optional): Results limit.
- **Output**:
  - `candidates` (List[Dict]): Materials matching the search.

<a id="base-de-datos-interna-ejemplos"></a>
## Internal Database (Examples)
- **Batteries**: LiFePO4, LiCoO2, LiNiMnCoO2.
- **Solar**: MAPbI3, FAPbI3, GaAs, CdTe.
- **Semiconductors**: SiC, GaN.
- **Superconductors**: YBCO, MgB2.

<a id="ejemplo-de-uso"></a>
## Usage Example
```python
from app.domains.chemistry.services.gnome_materials_service import GNOMEMaterialsService

service = GNOMEMaterialsService()
result = await service.process_request({
    "action": "suggest_candidates",
    "target": "solar energy",
    "top_n": 2
})
```

<a id="pruebas"></a>
## Tests
- Run unit tests:
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_gnome_materials_service.py`
