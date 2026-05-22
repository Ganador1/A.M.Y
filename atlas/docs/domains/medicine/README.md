# Dominio: Medicine

## Qué es
Dominio para cómputo médico: NLP clínico, medicina personalizada, biomecánica, imagen médica y genómica clínica.

## Ubicación en el código
- Paquete: `app/domains/medicine/`
- Router consolidado: `app/domains/medicine/routers/api.py` (declara `prefix="/medicine"`)
- Servicios: `app/domains/medicine/services/`

## Servicios principales
- `ClinicalBERTService`: `app/domains/medicine/services/clinicalbert_service.py` (nota: existen variantes/broken/fixed en el repo)
- `PersonalizedMedicineService`: `app/domains/medicine/personalized_medicine_service.py` y/o `app/domains/medicine/services/personalized_medicine_service.py`
- `AdvancedMedicalImagingService`: `app/domains/medicine/services/advanced_medical_imaging_service.py`
- `AdvancedClinicalValidationService`: `app/domains/medicine/services/advanced_clinical_validation_service.py`

## API (router consolidado)
- `GET /medicine/` → info del dominio
- `POST /medicine/compute`
- `POST /medicine/analyze`

## Routers adicionales
- `app/domains/medicine/routers/unified_medical_router.py`
- `app/domains/medicine/routers/websocket_router.py`

## Referencias cercanas al código
- `app/domains/medicine/README.md`
- `app/domains/medicine/API_GUIDE.md`
- `app/domains/medicine/SERVICES.md`
- `app/domains/medicine/EXAMPLES.md`
- `app/domains/medicine/DICOM_GUIDE.md`
