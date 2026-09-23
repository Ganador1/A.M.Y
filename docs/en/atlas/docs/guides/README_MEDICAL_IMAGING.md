> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="medical-imaging-service---ejemplos-prácticos"></a>
# Medical Imaging Service - Practical Examples

This directory contains practical examples for using the enhanced **Medical Imaging Service** with advanced cardiac segmentation capabilities.

<a id="-archivos-disponibles"></a>
## 📋 Available Files

<a id="1-medical_imaging_examplepy"></a>
### 1. `medical_imaging_example.py`
**Complete and detailed example** demonstrating all the service's functionalities:

- ✅ Medical service initialization
- ✅ Comparison of segmentation methods
- ✅ Myocardial strain analysis
- ✅ Patient-specific model calibration
- ✅ Clinical report generation
- ✅ Saving results

**Usage:**
```bash
python medical_imaging_example.py
```

**Approximate duration:** 2-3 minutes
**Requirements:** All dependencies installed

<a id="2-medical_imaging_quick_testpy"></a>
### 2. `medical_imaging_quick_test.py`
**Quick test** to verify that the service works correctly:

- ✅ Basic initialization
- ✅ Verification of available methods
- ✅ Simple segmentation with synthetic data
- ✅ Validation of results

**Usage:**
```bash
python medical_imaging_quick_test.py
```

**Approximate duration:** 30 seconds
**Requirements:** Basic dependencies installed

<a id="-inicio-rápido"></a>
## 🚀 Quick Start

<a id="paso-1-instalar-dependencias"></a>
### Step 1: Install Dependencies
```bash
<a id="desde-el-directorio-raíz-del-proyecto"></a>
# Desde el directorio raíz del proyecto
pip install -r requirements.txt
```

<a id="paso-2-ejecutar-prueba-rápida"></a>
### Step 2: Run Quick Test
```bash
cd examples
python medical_imaging_quick_test.py
```

<a id="paso-3-ejecutar-ejemplo-completo"></a>
### Step 3: Run Complete Example
```bash
python medical_imaging_example.py
```

<a id="-qué-incluyen-los-ejemplos"></a>
## 📊 What the Examples Include

<a id="datos-sintéticos-realistas"></a>
### Realistic Synthetic Data
- 3D cardiac images with anatomical structures
- Realistic noise similar to DICOM data
- Metadata compatible with medical standards

<a id="funcionalidades-demostradas"></a>
### Demonstrated Functionalities
- **Basic segmentation:** Threshold, adaptive, morphological
- **Advanced segmentation:** Deep learning with MONAI, U-Net
- **Strain analysis:** Optical flow for myocardial evaluation
- **Patient-specific models:** Automatic calibration
- **Clinical reports:** Automatic report generation

<a id="resultados-generados"></a>
### Generated Results
The examples automatically save the results in `../results/`:
- `cardiac_data.npy` - Original image data
- `segmentation_results.json` - Segmentation results
- `strain_analysis.json` - Strain analysis
- `patient_model.json` - Calibrated model
- `clinical_report.md` - Complete clinical report

<a id="-solución-de-problemas"></a>
## 🔧 Troubleshooting

<a id="error-de-importación"></a>
### Import Error
If you get import errors:
```bash
<a id="asegurarse-de-estar-en-el-directorio-correcto"></a>
# Asegurarse de estar en el directorio correcto
cd /ruta/al/proyecto/atlas

<a id="instalar-dependencias-faltantes"></a>
# Instalar dependencias faltantes
pip install pydicom SimpleITK nibabel monai torchio opencv-python scikit-image
```

<a id="error-de-memoria"></a>
### Memory Error
If there are memory issues with large data:
```python
<a id="reducir-el-tamaño-de-los-datos-sintéticos"></a>
# Reducir el tamaño de los datos sintéticos
height, width, slices = 64, 64, 6  # En lugar de 128, 128, 12
```

<a id="métodos-avanzados-no-disponibles"></a>
### Advanced Methods Not Available
If advanced methods are not available:
- Verify that MONAI is installed: `pip install monai`
- Verify that PyTorch is installed: `pip install torch torchvision`
- Basic methods will always be available

<a id="-próximos-pasos"></a>
## 📈 Next Steps

After successfully running the examples:

1. **Use real data:** Replace synthetic data with real DICOM/NIfTI files
2. **Customize algorithms:** Adjust segmentation parameters according to clinical needs
3. **Integrate into application:** Use the service in your existing FastAPI application
4. **Clinical validation:** Test with real medical datasets for validation

<a id="-soporte"></a>
## 📞 Support

For questions or issues:
- Review the complete documentation at `../docs/MEDICAL_IMAGING_SERVICE_COMPLETE_GUIDE.md`
- Check logs at `../logs/`
- Consult issues in the project repository

<a id="-actualizaciones"></a>
## 🔄 Updates

The examples are automatically updated with the service's new functionalities. For the most recent version, run:
```bash
git pull origin main
```

---

**Version:** 1.0.0
**Last update:** September 2025
**Service:** Medical Imaging Service with advanced capabilities
