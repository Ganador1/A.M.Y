# Nuevos Servicios Fase 5

Este documento describe los nuevos servicios integrados: DNABERT-2 Genomics, GNOME Materials y Model Management.

## DNABERT-2 Genomics (ligero)
- Router: `app/routers/dnabert2.py`
- Servicio: `app/services/dnabert2_service.py`
- Endpoints:
  - POST `/api/dnabert2/encode-sequence` { sequence, k? }
  - POST `/api/dnabert2/predict-motifs` { sequence }
  - POST `/api/dnabert2/classify-promoter` { sequence }

Ejemplo (HTTP):
```
POST /api/dnabert2/predict-motifs
{
  "sequence": "ACGTACGTATATAACGCGCGTTT"
}
```
Respuesta:
```
{
  "success": true,
  "motifs": [
    {"motif": "TATA", "positions": [8, 9] },
    {"motif": "CG", "positions": [2, 4, 14] }
  ]
}
```

Uso en Python:
```
from app.services.dnabert2_service import DNABERT2GenomicsService
svc = DNABERT2GenomicsService()
print(svc.predict_motifs({"sequence": "ACGTATATAACGCG"}))
```

## GNOME Materials (placeholder)
- Router: `app/routers/gnome_materials.py`
- Servicio: `app/services/gnome_materials_service.py`
- Endpoints:
  - POST `/api/gnome/suggest-candidates` { target, top_n? }
  - POST `/api/gnome/predict-properties` { formula }

Ejemplo (HTTP):
```
POST /api/gnome/suggest-candidates
{
  "target": "high thermal conductivity",
  "top_n": 3
}
```

Uso en Python:
```
from app.services.gnome_materials_service import GNOMEMaterialsService
svc = GNOMEMaterialsService()
print(svc.suggest_candidates({"target": "battery cathode", "top_n": 2}))
```

## Model Management
- Servicio: `app/services/model_management_service.py`
- Funciones: registrar, listar, obtener y actualizar metadatos de modelos en `data/models_registry.json`.

Ejemplo (Python):
```
from app.services.model_management_service import ModelManagementService
svc = ModelManagementService(registry_path="data/models_registry.json")
svc.register_model({"name": "my-model", "version": "1.0.0"})
print(svc.list_models())
```

## Notas de seguridad
- pip-audit: sin vulnerabilidades conocidas
- Bandit: ejecutado sobre `app/` y `tests/` (reporte `bandit_report.json`)

## Trazabilidad y MLflow
- Los workflows registran `workflow_steps` en parámetros de experimento para mejor trazabilidad en MLflow (`file:./mlruns`).
