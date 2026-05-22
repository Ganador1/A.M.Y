#!/usr/bin/env python3
"""
Medical Imaging Service - Prueba Rápida
Script simple para verificar que el servicio funciona correctamente

Uso:
    python medical_imaging_quick_test.py

Requiere:
    - Python 3.8+
    - Dependencias instaladas
"""

import sys
import numpy as np
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.domains.medicine.imaging.medical_imaging_service import MedicalImagingService

def quick_test():
    """Prueba rápida del Medical Imaging Service"""

    print("🏥 Medical Imaging Service - Prueba Rápida")
    print("=" * 50)

    try:
        # 1. Inicializar servicio
        print("\\n1️⃣ Inicializando servicio...")
        service = MedicalImagingService()
        print("✅ Servicio inicializado")

        # 2. Verificar métodos disponibles
        print("\\n2️⃣ Verificando métodos de segmentación...")
        methods = service.get_available_segmentation_methods()
        print(f"📋 Métodos disponibles: {len(methods['all_methods'])}")
        print(f"   Básicos: {methods['basic_methods']}")
        print(f"   Avanzados: {methods['advanced_methods']}")

        # 3. Crear datos de prueba simples
        print("\\n3️⃣ Creando datos de prueba...")
        test_data = create_simple_test_data()
        print(f"✅ Datos creados: {test_data['pixel_data'].shape}")

        # 4. Probar segmentación básica
        print("\\n4️⃣ Probando segmentación básica...")
        result = service.segment_cardiac_chambers(test_data, 'threshold')

        print("✅ Segmentación completada")
        print(f"   Volúmenes estimados: {len(result.volume_estimates)} regiones")
        print(f"   Confianza promedio: {np.mean(list(result.segmentation_confidence.values())):.1%}")

        # 5. Mostrar resultados
        print("\\n5️⃣ Resultados:")
        for region, volume in result.volume_estimates.items():
            confidence = result.segmentation_confidence[region]
            print(f"   • {region}: {volume:.1f} mL ({confidence:.1%})")

        print("\\n🎉 ¡Prueba rápida completada exitosamente!")
        return True

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_test_data():
    """Crea datos de prueba simples"""

    # Imagen 2D simple con estructuras cardíacas básicas
    height, width = 64, 64

    # Crear imagen base
    image = np.zeros((height, width), dtype=np.float32)

    # Añadir ventrículo izquierdo (círculo central)
    center = (height//2, width//2)
    radius = 15

    y, x = np.ogrid[:height, :width]
    mask = (x - center[1])**2 + (y - center[0])**2 <= radius**2
    image[mask] = 1500  # Intensidad típica

    # Añadir ruido
    noise = np.random.normal(0, 50, image.shape)
    image += noise

    # Añadir dimensión de slices para compatibilidad
    image_3d = np.expand_dims(image, axis=-1)

    return {
        'pixel_data': image_3d,
        'spacing': [2.0, 2.0, 8.0],
        'origin': [0.0, 0.0, 0.0],
        'direction': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
        'metadata': {
            'patient_id': 'TEST_001',
            'study_date': '20250908',
            'modality': 'CT',
            'series_description': 'Quick Test Data'
        }
    }

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
