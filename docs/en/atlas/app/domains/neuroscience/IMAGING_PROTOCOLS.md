> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="protocolos-de-neuroimagen"></a>
# Neuroimaging Protocols

<a id="overview"></a>
## Overview
Guide to recommended protocols and parameters for EEG, fMRI, and other modalities in the Neuroscience domain.

<a id="eeg"></a>
## EEG
- **Sampling Rate:** 250–1000 Hz depending on the study.
- **Filters:** Notch 50/60 Hz, band-pass 1–40 Hz.
- **Reference:** Average or mastoids.
- **Artifacts:** ICA to remove blinks and EMG.

<a id="fmri"></a>
## fMRI
- **TR/TE:** TR 2s, TE 30ms (approximate).
- **Preprocessing:** Motion correction, slice timing, spatial smoothing (6mm).
- **Normalization:** MNI152.
- **Analysis:** GLM, functional connectivity.

<a id="meg"></a>
## MEG
- **Sampling Rate:** 1000 Hz.
- **Filters:** Band-pass 0.1–100 Hz.
- **Environmental noise:** Shielding and field correction.

<a id="integración-con-servicios"></a>
## Integration with Services
- `NeuroscienceLightService` for lightweight EEG analysis.
- `AdvancedNeuroimagingAnalysis` for fMRI/MEG pipelines.

<a id="buenas-prácticas"></a>
## Best Practices
- Document parameters per subject/scan.
- Quality control (QC) per session.
- Version pipelines and templates.
