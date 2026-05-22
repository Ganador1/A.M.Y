# Protocolos de Neuroimagen

## Overview
Guía de protocolos y parámetros recomendados para EEG, fMRI y otras modalidades en el dominio Neuroscience.

## EEG
- **Sampling Rate:** 250–1000 Hz según estudio.
- **Filtros:** Notch 50/60 Hz, band-pass 1–40 Hz.
- **Referencia:** Promedio o mastoides.
- **Artefactos:** ICA para remover parpadeos y EMG.

## fMRI
- **TR/TE:** TR 2s, TE 30ms (orientativo).
- **Preprocesamiento:** Motion correction, slice timing, spatial smoothing (6mm).
- **Normalización:** MNI152.
- **Análisis:** GLM, conectividad funcional.

## MEG
- **Sampling Rate:** 1000 Hz.
- **Filtros:** Band-pass 0.1–100 Hz.
- **Ruido ambiental:** Shielding y corrección de campo.

## Integración con Servicios
- `NeuroscienceLightService` para análisis EEG ligero.
- `AdvancedNeuroimagingAnalysis` para pipelines fMRI/MEG.

## Buenas Prácticas
- Documentar parámetros por sujeto/escaneo.
- Control de calidad (QC) por sesión.
- Versionar pipelines y plantillas.