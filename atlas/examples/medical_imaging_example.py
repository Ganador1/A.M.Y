#!/usr/bin/env python3
"""
Medical Imaging Service - Ejemplo Práctico Completo
Demuestra el uso del servicio médico mejorado con segmentación avanzada

Uso:
    python medical_imaging_example.py

Requiere:
    - Python 3.8+
    - Dependencias instaladas (ver requirements.txt)
    - Acceso al directorio del proyecto
"""

import sys
import numpy as np
from pathlib import Path
from scipy.ndimage import zoom

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.domains.medicine.imaging.medical_imaging_service import MedicalImagingService

def main():
    """Ejemplo completo del Medical Imaging Service"""

    print("🏥 Medical Imaging Service - Ejemplo Práctico")
    print("=" * 60)

    try:
        # 1. Inicializar el servicio
        print("\\n1️⃣ Inicializando Medical Imaging Service...")
        medical_service = MedicalImagingService()
        print("✅ Servicio inicializado exitosamente")

        # 2. Verificar métodos disponibles
        print("\\n2️⃣ Verificando métodos de segmentación disponibles...")
        methods = medical_service.get_available_segmentation_methods()

        print(f"📋 Métodos básicos: {methods['basic_methods']}")
        print(f"🚀 Métodos avanzados: {methods['advanced_methods']}")
        print(f"🔧 Total de métodos: {len(methods['all_methods'])}")

        # 3. Crear datos de prueba realistas
        print("\\n3️⃣ Creando datos de imagen cardíaca sintéticos...")
        cardiac_data = create_synthetic_cardiac_data()
        print(f"✅ Datos creados: {cardiac_data['pixel_data'].shape}")

        # 4. Comparar métodos de segmentación
        print("\\n4️⃣ Comparando métodos de segmentación...")
        segmentation_results = compare_segmentation_methods(medical_service, cardiac_data)

        # 5. Mostrar resultados detallados
        print("\\n5️⃣ Resultados de segmentación:")
        display_segmentation_results(segmentation_results)

        # 6. Análisis de strain
        print("\\n6️⃣ Realizando análisis de strain miocárdico...")
        strain_result = perform_strain_analysis(medical_service, cardiac_data)

        # 7. Calibración paciente-específica
        print("\\n7️⃣ Calibrando modelo paciente-específico...")
        patient_model = calibrate_patient_model(medical_service, cardiac_data, segmentation_results, strain_result)

        # 8. Guardar resultados
        print("\\n8️⃣ Guardando resultados...")
        save_results(cardiac_data, segmentation_results, strain_result, patient_model)

        print("\\n🎉 ¡Ejemplo completado exitosamente!")
        print("\\n📊 Resumen:")
        print(f"   • {len(methods['all_methods'])} métodos de segmentación probados")
        print("   • Strain miocárdico analizado")
        print("   • Modelo paciente-específico calibrado")
        print(f"   • Resultados guardados en: {project_root}/results/")

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

def create_synthetic_cardiac_data():
    """Crea datos de imagen cardíaca sintéticos realistas"""

    # Dimensiones típicas de una imagen cardíaca
    height, width, slices = 128, 128, 12

    # Crear imagen base con ruido
    image_data = np.random.normal(0, 0.1, (height, width, slices))

    # Añadir estructuras cardíacas simuladas
    # Ventrículo izquierdo (región central)
    lv_center = (height//2, width//2)
    lv_radius = 25
    lv_mask = create_circular_mask(height, width, lv_center, lv_radius)
    image_data[lv_mask, :] += 0.8  # Más brillante

    # Ventrículo derecho (región lateral)
    rv_center = (height//2, width//3)
    rv_radius = 18
    rv_mask = create_circular_mask(height, width, rv_center, rv_radius)
    image_data[rv_mask, :] += 0.6

    # Aurículas
    la_center = (height//3, width//2)
    la_radius = 15
    la_mask = create_circular_mask(height, width, la_center, la_radius)
    image_data[la_mask, :] += 0.4

    ra_center = (height//3, width//3)
    ra_radius = 12
    ra_mask = create_circular_mask(height, width, ra_center, ra_radius)
    image_data[ra_mask, :] += 0.3

    # Miocardio (anillo alrededor del VI)
    myocardium_mask = create_ring_mask(height, width, lv_center, lv_radius, lv_radius + 8)
    image_data[myocardium_mask, :] += 1.0  # Más brillante que las cavidades

    # Añadir ruido realista
    noise = np.random.normal(0, 0.05, image_data.shape)
    image_data += noise

    # Normalizar a rango típico de DICOM
    image_data = (image_data - image_data.min()) / (image_data.max() - image_data.min())
    image_data = (image_data * 2000).astype(np.float32)  # Rango típico

    return {
        'pixel_data': image_data,
        'spacing': [1.5, 1.5, 8.0],  # mm: pixel_size_x, pixel_size_y, slice_thickness
        'origin': [0.0, 0.0, 0.0],
        'direction': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
        'metadata': {
            'patient_id': 'EXAMPLE_001',
            'study_date': '20250908',
            'modality': 'CT',
            'series_description': 'Cardiac CT - Synthetic Data'
        }
    }

def create_circular_mask(height, width, center, radius):
    """Crea una máscara circular"""
    y, x = np.ogrid[:height, :width]
    dist_from_center = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    mask = dist_from_center <= radius
    return mask

def create_ring_mask(height, width, center, inner_radius, outer_radius):
    """Crea una máscara en forma de anillo"""
    y, x = np.ogrid[:height, :width]
    dist_from_center = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    mask = (dist_from_center >= inner_radius) & (dist_from_center <= outer_radius)
    return mask

def compare_segmentation_methods(service, image_data):
    """Compara diferentes métodos de segmentación"""

    methods = service.get_available_segmentation_methods()
    results = {}

    print("   Probando métodos de segmentación...")

    for method in methods['all_methods']:
        try:
            print(f"     🔄 Probando {method}...")
            result = service.segment_cardiac_chambers(image_data, method)

            # Calcular métricas adicionales
            total_volume = sum(result.volume_estimates.values())
            avg_confidence = np.mean(list(result.segmentation_confidence.values()))

            results[method] = {
                'result': result,
                'total_volume': total_volume,
                'avg_confidence': avg_confidence,
                'success': True
            }

            print(f"       ✅ {method}: Vol={total_volume:.1f}mL, Conf={avg_confidence:.1%}")

        except Exception as e:
            print(f"       ❌ {method}: Error - {e}")
            results[method] = {
                'result': None,
                'error': str(e),
                'success': False
            }

    return results

def display_segmentation_results(results):
    """Muestra resultados detallados de segmentación"""

    print("\\n" + "="*60)
    print("📊 RESULTADOS DE SEGMENTACIÓN")
    print("="*60)

    successful_methods = [m for m, r in results.items() if r['success']]

    if not successful_methods:
        print("❌ Ningún método de segmentación funcionó correctamente")
        return

    # Encontrar el mejor método
    best_method = max(successful_methods,
                     key=lambda m: results[m]['avg_confidence'])

    print(f"🏆 Mejor método: {best_method}")
    print(f"   Confianza promedio: {results[best_method]['avg_confidence']:.1%}")
    print(f"   Volumen total: {results[best_method]['total_volume']:.1f} mL")

    print("\\n📋 Detalles por método:")
    for method in successful_methods:
        result = results[method]
        seg_result = result['result']

        print(f"\\n🔹 {method.upper()}:")
        print(f"   Confianza promedio: {result['avg_confidence']:.1%}")
        print(f"   Volumen total: {result['total_volume']:.1f} mL")

        # Mostrar volúmenes por región
        volumes = seg_result.volume_estimates
        for region, volume in volumes.items():
            confidence = seg_result.segmentation_confidence[region]
            print(f"     • {region}: {volume:.1f} mL ({confidence:.1%})")

def perform_strain_analysis(service, image_data):
    """Realiza análisis de strain miocárdico"""

    print("   Creando secuencia temporal sintética...")

    # Crear secuencia temporal (15 frames)
    time_points = np.linspace(0, 1.0, 15)  # 1 segundo de ciclo cardíaco

    # Simular movimiento cardíaco (contracción/relajación)
    base_image = image_data['pixel_data'][:, :, 6]  # Slice central
    sequence = []

    for t in time_points:
        # Simular contracción cardíaca (sístole)
        if t < 0.4:  # Fase de contracción
            scale_factor = 1.0 - 0.3 * (t / 0.4)  # Reducir tamaño
        else:  # Fase de relajación
            scale_factor = 0.7 + 0.3 * ((t - 0.4) / 0.6)  # Aumentar tamaño

        # Aplicar transformación simple
        scaled_image = zoom(base_image, scale_factor, order=1)

        # Ajustar al tamaño original
        if scaled_image.shape[0] > base_image.shape[0]:
            # Recortar
            start = (scaled_image.shape[0] - base_image.shape[0]) // 2
            scaled_image = scaled_image[start:start+base_image.shape[0],
                                      start:start+base_image.shape[1]]
        else:
            # Pad
            pad_width = (base_image.shape[0] - scaled_image.shape[0]) // 2
            scaled_image = np.pad(scaled_image,
                                pad_width,
                                mode='constant',
                                constant_values=base_image.min())

        sequence.append(scaled_image)

    # Crear array 4D (tiempo, altura, ancho, slices)
    image_sequence = np.stack(sequence, axis=0)
    image_sequence = np.expand_dims(image_sequence, axis=-1)  # Añadir dimensión de slices

    print(f"   Secuencia creada: {image_sequence.shape}")

    # Realizar análisis de strain
    strain_result = service.analyze_myocardial_strain(image_sequence, time_points)

    print("   ✅ Análisis de strain completado")
    print(f"   Strain longitudinal: {strain_result.global_longitudinal_strain:.3f}")
    print(f"   Strain circunferencial: {strain_result.global_circumferential_strain:.3f}")
    print(f"   Strain radial: {strain_result.global_radial_strain:.3f}")

    return strain_result

def calibrate_patient_model(service, image_data, segmentation_results, strain_result):
    """Calibra modelo paciente-específico"""

    # Usar el mejor resultado de segmentación
    successful_methods = [m for m, r in segmentation_results.items() if r['success']]
    best_method = max(successful_methods,
                     key=lambda m: segmentation_results[m]['avg_confidence'])

    segmentation = segmentation_results[best_method]['result']

    print(f"   Usando segmentación: {best_method}")
    print(f"   Confianza: {segmentation_results[best_method]['avg_confidence']:.1%}")

    # Calibrar modelo
    patient_model = service.calibrate_patient_specific_model(
        image_data,
        segmentation,
        strain_result
    )

    print("   ✅ Modelo paciente-específico calibrado")
    print(f"   Paciente ID: {patient_model['patient_id']}")
    print(f"   Geometrías calibradas: {len(patient_model['geometries'])} regiones")
    print(f"   Propiedades materiales: {len(patient_model['material_properties'])} regiones")

    return patient_model

def save_results(cardiac_data, segmentation_results, strain_result, patient_model):
    """Guarda los resultados del análisis"""

    # Crear directorio de resultados
    results_dir = project_root / "results"
    results_dir.mkdir(exist_ok=True)

    print(f"   Guardando en: {results_dir}")

    # Guardar datos de imagen
    np.save(results_dir / "cardiac_data.npy", cardiac_data['pixel_data'])

    # Guardar resultados de segmentación
    import json
    segmentation_summary = {}

    for method, result in segmentation_results.items():
        if result['success']:
            segmentation_summary[method] = {
                'total_volume': result['total_volume'],
                'avg_confidence': result['avg_confidence'],
                'volumes': result['result'].volume_estimates,
                'confidence': result['result'].segmentation_confidence
            }
        else:
            segmentation_summary[method] = {
                'error': result['error'],
                'success': False
            }

    with open(results_dir / "segmentation_results.json", 'w') as f:
        json.dump(segmentation_summary, f, indent=2, default=str)

    # Guardar análisis de strain
    strain_summary = {
        'global_longitudinal_strain': strain_result.global_longitudinal_strain,
        'global_circumferential_strain': strain_result.global_circumferential_strain,
        'global_radial_strain': strain_result.global_radial_strain,
        'strain_rate': strain_result.strain_rate,
        'torsion': strain_result.torsion
    }

    with open(results_dir / "strain_analysis.json", 'w') as f:
        json.dump(strain_summary, f, indent=2, default=str)

    # Guardar modelo paciente
    with open(results_dir / "patient_model.json", 'w') as f:
        json.dump(patient_model, f, indent=2, default=str)

    print("   ✅ Todos los resultados guardados")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
