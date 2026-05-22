# GNOME Materials Discovery Service

## Alcance
- Servicio: `GNOMEMaterialsService` (`app/domains/chemistry/services/gnome_materials_service.py`).
- Propósito: Emular el descubrimiento de materiales y la predicción de propiedades utilizando una base de datos interna de materiales conocidos y heurísticas.
- Implementación: Placeholder ligero diseñado para simular las capacidades del modelo GNoME (Graph Networks for Materials Exploration).

## Capacidades
- **Sugerencia de Candidatos**: Recomienda materiales basados en una aplicación objetivo (baterías, celdas solares, semiconductores, etc.).
- **Predicción de Propiedades**: Estima propiedades físicas y químicas para fórmulas dadas.
- **Búsqueda de Materiales**: Permite filtrar la base de datos interna por aplicación y criterios específicos.

## Acciones Soportadas (`process_request`)

### `suggest_candidates`
Sugiere los mejores materiales para una aplicación específica.
- **Entrada**:
  - `target` (str): Aplicación objetivo (ej. "solar", "battery", "superconductor").
  - `top_n` (int, opcional): Número de candidatos a devolver (por defecto 3).
- **Salida**:
  - `candidates` (List[Dict]): Lista de materiales con su fórmula, puntuación y propiedades predichas.

### `predict_properties`
Predice propiedades para una fórmula química específica si existe en la base de datos.
- **Entrada**:
  - `formula` (str): Fórmula química (ej. "LiFePO4").
- **Salida**:
  - `properties` (Dict): Propiedades como conductividad, estabilidad, capacidad, etc.

### `search_materials`
Búsqueda directa en la base de datos de materiales.
- **Entrada**:
  - `application` (str): Tipo de aplicación.
  - `max_results` (int, opcional): Límite de resultados.
- **Salida**:
  - `candidates` (List[Dict]): Materiales que coinciden con la búsqueda.

## Base de Datos Interna (Ejemplos)
- **Baterías**: LiFePO4, LiCoO2, LiNiMnCoO2.
- **Solar**: MAPbI3, FAPbI3, GaAs, CdTe.
- **Semiconductores**: SiC, GaN.
- **Superconductores**: YBCO, MgB2.

## Ejemplo de Uso
```python
from app.domains.chemistry.services.gnome_materials_service import GNOMEMaterialsService

service = GNOMEMaterialsService()
result = await service.process_request({
    "action": "suggest_candidates",
    "target": "solar energy",
    "top_n": 2
})
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_gnome_materials_service.py`
