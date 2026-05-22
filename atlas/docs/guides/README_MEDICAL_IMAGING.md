# Medical Imaging Service - Ejemplos Prácticos

Este directorio contiene ejemplos prácticos para usar el **Medical Imaging Service** mejorado con capacidades avanzadas de segmentación cardíaca.

## 📋 Archivos Disponibles

### 1. `medical_imaging_example.py`
**Ejemplo completo y detallado** que demuestra todas las funcionalidades del servicio:

- ✅ Inicialización del servicio médico
- ✅ Comparación de métodos de segmentación
- ✅ Análisis de strain miocárdico
- ✅ Calibración de modelo paciente-específico
- ✅ Generación de reportes clínicos
- ✅ Guardado de resultados

**Uso:**
```bash
python medical_imaging_example.py
```

**Duración aproximada:** 2-3 minutos
**Requisitos:** Todas las dependencias instaladas

### 2. `medical_imaging_quick_test.py`
**Prueba rápida** para verificar que el servicio funciona correctamente:

- ✅ Inicialización básica
- ✅ Verificación de métodos disponibles
- ✅ Segmentación simple con datos sintéticos
- ✅ Validación de resultados

**Uso:**
```bash
python medical_imaging_quick_test.py
```

**Duración aproximada:** 30 segundos
**Requisitos:** Dependencias básicas instaladas

## 🚀 Inicio Rápido

### Paso 1: Instalar Dependencias
```bash
# Desde el directorio raíz del proyecto
pip install -r requirements.txt
```

### Paso 2: Ejecutar Prueba Rápida
```bash
cd examples
python medical_imaging_quick_test.py
```

### Paso 3: Ejecutar Ejemplo Completo
```bash
python medical_imaging_example.py
```

## 📊 Qué Incluyen los Ejemplos

### Datos Sintéticos Realistas
- Imágenes cardíacas 3D con estructuras anatómicas
- Ruido realista similar a datos DICOM
- Metadatos compatibles con estándares médicos

### Funcionalidades Demostradas
- **Segmentación básica:** Threshold, adaptive, morphological
- **Segmentación avanzada:** Deep learning con MONAI, U-Net
- **Análisis de strain:** Optical flow para evaluación miocárdica
- **Modelos paciente-específicos:** Calibración automática
- **Reportes clínicos:** Generación automática de informes

### Resultados Generados
Los ejemplos guardan automáticamente los resultados en `../results/`:
- `cardiac_data.npy` - Datos de imagen originales
- `segmentation_results.json` - Resultados de segmentación
- `strain_analysis.json` - Análisis de strain
- `patient_model.json` - Modelo calibrado
- `clinical_report.md` - Reporte clínico completo

## 🔧 Solución de Problemas

### Error de Importación
Si obtienes errores de importación:
```bash
# Asegurarse de estar en el directorio correcto
cd /ruta/al/proyecto/atlas

# Instalar dependencias faltantes
pip install pydicom SimpleITK nibabel monai torchio opencv-python scikit-image
```

### Error de Memoria
Si hay problemas de memoria con datos grandes:
```python
# Reducir el tamaño de los datos sintéticos
height, width, slices = 64, 64, 6  # En lugar de 128, 128, 12
```

### Métodos Avanzados No Disponibles
Si los métodos avanzados no están disponibles:
- Verificar que MONAI esté instalado: `pip install monai`
- Verificar que PyTorch esté instalado: `pip install torch torchvision`
- Los métodos básicos siempre estarán disponibles

## 📈 Próximos Pasos

Después de ejecutar los ejemplos exitosamente:

1. **Usar datos reales:** Reemplazar los datos sintéticos con archivos DICOM/NIfTI reales
2. **Personalizar algoritmos:** Ajustar parámetros de segmentación según necesidades clínicas
3. **Integrar en aplicación:** Usar el servicio en tu aplicación FastAPI existente
4. **Validación clínica:** Probar con datasets médicos reales para validación

## 📞 Soporte

Para preguntas o problemas:
- Revisar la documentación completa en `../docs/MEDICAL_IMAGING_SERVICE_COMPLETE_GUIDE.md`
- Verificar logs en `../logs/`
- Consultar issues en el repositorio del proyecto

## 🔄 Actualizaciones

Los ejemplos se actualizan automáticamente con las nuevas funcionalidades del servicio. Para la versión más reciente, ejecutar:
```bash
git pull origin main
```

---

**Versión:** 1.0.0
**Última actualización:** Septiembre 2025
**Servicio:** Medical Imaging Service con capacidades avanzadas
