# Dominio: Chemistry

## Qué es
Dominio para química computacional, análisis molecular, espectroscopía (NMR), cristalografía y descubrimiento de materiales.

## Ubicación en el código
- Paquete: `app/domains/chemistry/`
- Router consolidado: `app/domains/chemistry/routers/api.py` (declara `prefix="/chemistry"`)
- Servicios: `app/domains/chemistry/services/`

## Servicios principales (clases/archivos)
- `ComputationalChemistryService`: `app/domains/chemistry/services/computational_chemistry.py`
- `ChemMLService`: `app/domains/chemistry/services/chemml_service.py`
- `AdvancedNMRService`: `app/domains/chemistry/services/advanced_nmr_service.py`
- `MaterialsDiscoveryService`: `app/domains/chemistry/services/materials_discovery_service.py`
- Otros: `molecular_dynamics.py`, `advanced_spectrometers.py`

## API (router consolidado)
- `GET /chemistry/` → info del dominio
- `POST /chemistry/compute`
- `POST /chemistry/analyze`
- Endpoints “enhanced” (p.ej. electrocatalysis loop): ver `app/domains/chemistry/routers/api.py`

## Integración con pipelines autónomos
- `EnhancedChemistryLoop`: `app/autonomous/pipelines/enhanced_chemistry_loop.py` (referenciado desde el router del dominio)

## Referencias cercanas al código
- `app/domains/chemistry/README.md`
- `app/domains/chemistry/API_GUIDE.md`
- `app/domains/chemistry/SERVICES.md`
- `app/domains/chemistry/EXAMPLES.md`
