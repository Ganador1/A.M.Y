# Guía DICOM para Medical Imaging

## Overview
Este documento describe buenas prácticas para manejar datos DICOM en el dominio Medicine: lectura, anonimización, almacenamiento, y exposición vía API.

## Lectura y Metadatos
- Usar `pydicom` para leer archivos y acceder a tags estándar (PatientID, StudyInstanceUID, etc.).
- Validar consistencia de series y estudios.

```python
import pydicom
ds = pydicom.dcmread("/path/to/file.dcm")
print(ds.PatientID, ds.StudyInstanceUID)
```

## Anonimización
- Remover/anonimizar identificadores (PatientName, PatientID).
- Mantener UIDs para trazabilidad interna.

```python
from pydicom.uid import generate_uid
ds.PatientName = "ANON"
ds.PatientID = generate_uid()
ds.save_as("anon.dcm")
```

## Almacenamiento
- Estructura recomendada: `/storage/{StudyInstanceUID}/{SeriesInstanceUID}/{SOPInstanceUID}.dcm`.
- Mantener índices para búsqueda rápida.

## Endpoints API (referencia)
- `POST /api/medicine/imaging/upload` - Subir estudio/serie.
- `GET /api/medicine/imaging/series/{series_uid}` - Obtener serie.
- `POST /api/medicine/imaging/segment` - Segmentar volúmenes.

## Integración con Servicios
- `AdvancedMedicalImagingService` y `AdvancedSegmentationService` consumen volúmenes DICOM.
- Asegurar conversión a NIfTI/arrays según pipeline.

## Troubleshooting
- UIDs inválidos: regenerar y validar consistencia.
- Tags faltantes: normalizar con defaults seguros.
- Archivos corruptos: reintentar lectura y registrar incidentes.