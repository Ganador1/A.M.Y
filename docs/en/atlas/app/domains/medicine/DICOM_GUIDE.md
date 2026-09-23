> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="guía-dicom-para-medical-imaging"></a>
# DICOM Guide for Medical Imaging

<a id="overview"></a>
## Overview
This document describes best practices for handling DICOM data in the Medicine domain: reading, anonymization, storage, and exposure via API.

<a id="lectura-y-metadatos"></a>
## Reading and Metadata
- Use `pydicom` to read files and access standard tags (PatientID, StudyInstanceUID, etc.).
- Validate consistency of series and studies.

```python
import pydicom
ds = pydicom.dcmread("/path/to/file.dcm")
print(ds.PatientID, ds.StudyInstanceUID)
```

<a id="anonimización"></a>
## Anonymization
- Remove/anonymize identifiers (PatientName, PatientID).
- Keep UIDs for internal traceability.

```python
from pydicom.uid import generate_uid
ds.PatientName = "ANON"
ds.PatientID = generate_uid()
ds.save_as("anon.dcm")
```

<a id="almacenamiento"></a>
## Storage
- Recommended structure: `/storage/{StudyInstanceUID}/{SeriesInstanceUID}/{SOPInstanceUID}.dcm`.
- Maintain indexes for fast search.

<a id="endpoints-api-referencia"></a>
## API Endpoints (reference)
- `POST /api/medicine/imaging/upload` - Upload study/series.
- `GET /api/medicine/imaging/series/{series_uid}` - Get series.
- `POST /api/medicine/imaging/segment` - Segment volumes.

<a id="integración-con-servicios"></a>
## Integration with Services
- `AdvancedMedicalImagingService` and `AdvancedSegmentationService` consume DICOM volumes.
- Ensure conversion to NIfTI/arrays according to pipeline.

<a id="troubleshooting"></a>
## Troubleshooting
- Invalid UIDs: regenerate and validate consistency.
- Missing tags: normalize with safe defaults.
- Corrupted files: retry reading and log incidents.
