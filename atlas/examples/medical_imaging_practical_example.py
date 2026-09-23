#!/usr/bin/env python3
"""
Medical Imaging Practical Example - Advanced Image Analysis and Processing
==========================================================================

Este ejemplo demuestra el uso completo del servicio de imágenes médicas para:
- Procesamiento avanzado de imágenes médicas
- Análisis de tejidos y órganos
- Detección automática de anomalías
- Segmentación y cuantificación
- Análisis temporal y comparación

Incluye datos reales de ejemplo y casos de uso prácticos.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockAdvancedMedicalImagingService:
    """Mock service para simular análisis avanzado de imágenes médicas."""

    async def initialize(self):
        pass

    async def analyze_image(self, image_data: Dict, analysis_type: str) -> Dict[str, Any]:
        """Análisis mock de imagen médica."""
        # Usar los parámetros para simular procesamiento
        modality = image_data.get("modality", "MRI")
        body_part = image_data.get("body_part", "brain")

        return {
            "image_info": {
                "dimensions": image_data.get("dimensions", [512, 512, 100]),
                "modality": modality,
                "body_part": body_part
            },
            "segmentation": {
                "regions": ["gray_matter", "white_matter", "csf"],
                "volumes": {"gray_matter": 450.2, "white_matter": 380.1, "csf": 120.5}
            },
            "anomalies": [
                {"type": "lesion", "location": [120, 150, 45], "severity": "moderate", "confidence": 0.89}
            ],
            "quality_metrics": {"snr": 25.4, "contrast": 0.78}
        }

    async def segment_tissue(self, image_data: Dict, tissue_types: List[str]) -> Dict[str, Any]:
        """Segmentación mock de tejidos."""
        # Usar tissue_types para generar resultados apropiados
        return {
            "segmented_regions": {
                tissue: {"volume": np.random.uniform(100, 500), "confidence": 0.92}
                for tissue in tissue_types
            }
        }

    async def detect_anomalies(self, image_data: Dict, anomaly_types: List[str]) -> Dict[str, Any]:
        """Detección mock de anomalías."""
        # Generar anomalías basadas en los tipos solicitados
        anomalies = [
            {
                "type": anomaly_type,
                "location": [np.random.randint(100, 400) for _ in range(3)],
                "size": [np.random.uniform(5, 25) for _ in range(3)],
                "confidence": np.random.uniform(0.8, 0.95),
                "severity": np.random.choice(["low", "moderate", "high"])
            }
            for anomaly_type in anomaly_types[:2]  # Limitar a 2 para el ejemplo
        ]

        return {
            "detected_anomalies": anomalies,
            "false_positives": 2,
            "sensitivity": 0.91
        }

    async def quantify_features(self, image_data: Dict, features: List[str]) -> Dict[str, Any]:
        """Cuantificación mock de características."""
        # Generar cuantificaciones basadas en las características solicitadas
        return {
            "quantified_features": {
                feature: {
                    "value": np.random.uniform(0.1, 10.0),
                    "unit": "mm³" if "volume" in feature else "HU",
                    "confidence": 0.87
                }
                for feature in features
            }
        }

    async def analyze_temporal_changes(self, image_series: List[Dict]) -> Dict[str, Any]:
        """Análisis mock de cambios temporales."""
        # Analizar la serie temporal proporcionada
        num_points = len(image_series)
        return {
            "temporal_analysis": {
                "change_rate": np.random.uniform(0.01, 0.05),
                "trend": "increasing" if num_points > 3 else "stable",
                "significant_changes": [
                    {"time_point": i, "change_magnitude": np.random.uniform(0.1, 0.3), "p_value": 0.02}
                    for i in range(1, min(num_points, 3))
                ]
            }
        }

    async def compare_images(self, image1: Dict, image2: Dict) -> Dict[str, Any]:
        """Comparación mock de imágenes."""
        # Comparar las dos imágenes proporcionadas
        return {
            "comparison_metrics": {
                "similarity_score": np.random.uniform(0.7, 0.9),
                "differences": [
                    {"region": "temporal_lobe", "difference_magnitude": np.random.uniform(0.1, 0.2)}
                ]
            }
        }

    async def generate_report(self, analysis_results: Dict) -> Dict[str, Any]:
        """Generación mock de reporte."""
        # Generar reporte basado en los resultados
        num_analyses = len(analysis_results)
        return {
            "report": {
                "summary": f"Análisis completado exitosamente con {num_analyses} componentes",
                "findings": ["Lesión detectada", "Cambios en materia blanca"],
                "recommendations": ["Seguimiento en 3 meses", "Biopsia recomendada"]
            }
        }


class MedicalImagingPracticalExample:
    """
    Ejemplo práctico completo de análisis de imágenes médicas.

    Incluye:
    - Procesamiento de imágenes médicas
    - Segmentación de tejidos
    - Detección de anomalías
    - Análisis cuantitativo
    - Comparación temporal
    """

    def __init__(self):
        self.imaging_service = MockAdvancedMedicalImagingService()
        self.results = {}

    async def initialize_services(self):
        """Inicializar servicios de imágenes médicas."""
        logger.info("🏥 Inicializando servicios de imágenes médicas...")

        try:
            await self.imaging_service.initialize()
            logger.info("✅ AdvancedMedicalImagingService inicializado")

        except Exception as e:
            logger.error("❌ Error inicializando servicios: %s", e)
            raise

    async def analyze_medical_image(self) -> Dict[str, Any]:
        """
        Análisis completo de imagen médica.

        Incluye:
        - Caracterización de imagen
        - Segmentación automática
        - Detección de anomalías
        - Métricas de calidad
        """
        logger.info("🖼️ Analizando imagen médica...")

        # Datos de imagen de ejemplo (RM cerebral)
        image_data = {
            "image_id": "MRI_001",
            "modality": "MRI_T1",
            "body_part": "brain",
            "dimensions": [256, 256, 160],
            "voxel_size": [1.0, 1.0, 1.0],
            "data": np.random.rand(256, 256, 160).astype(np.float32),  # Mock data
            "metadata": {
                "patient_id": "PAT_001",
                "study_date": "2024-01-15",
                "manufacturer": "Siemens",
                "protocol": "T1_MPRAGE"
            }
        }

        try:
            # Análisis completo de imagen
            analysis_result = await self.imaging_service.analyze_image(
                image_data=image_data,
                analysis_type="comprehensive"
            )

            # Resultados detallados
            image_analysis = {
                "image_characteristics": image_data["metadata"],
                "segmentation_results": analysis_result.get("segmentation", {}),
                "anomaly_detection": analysis_result.get("anomalies", []),
                "quality_assessment": analysis_result.get("quality_metrics", {}),
                "processing_timestamp": datetime.now().isoformat(),
                "analysis_duration": "45.2s"  # Mock duration
            }

            self.results["image_analysis"] = image_analysis
            logger.info("✅ Análisis de imagen médica completado")
            return image_analysis

        except ValueError as e:
            logger.error("❌ Error en análisis de imagen: %s", e)
            return {"error": str(e)}

    async def segment_brain_tissues(self) -> Dict[str, Any]:
        """
        Segmentación avanzada de tejidos cerebrales.

        Incluye:
        - Segmentación de materia gris/blanca
        - LCR y otras estructuras
        - Volumetría automática
        - Validación de calidad
        """
        logger.info("🧠 Segmentando tejidos cerebrales...")

        # Datos de segmentación
        segmentation_data = {
            "image_id": "BRAIN_SEG_001",
            "tissue_types": ["gray_matter", "white_matter", "csf", "hippocampus", "thalamus"],
            "atlas": "MNI152",
            "processing_parameters": {
                "smoothing": 0.5,
                "threshold": 0.3,
                "iterations": 100
            }
        }

        try:
            # Segmentación de tejidos
            segmentation_result = await self.imaging_service.segment_tissue(
                image_data=segmentation_data,
                tissue_types=segmentation_data["tissue_types"]
            )

            # Análisis volumétrico
            volumetric_analysis = await self.imaging_service.quantify_features(
                image_data=segmentation_data,
                features=["volume", "surface_area", "cortical_thickness"]
            )

            tissue_segmentation = {
                "segmentation_parameters": segmentation_data,
                "tissue_volumes": segmentation_result.get("segmented_regions", {}),
                "volumetric_measures": volumetric_analysis.get("quantified_features", {}),
                "quality_metrics": {
                    "dice_coefficient": 0.87,
                    "hausdorff_distance": 1.2,
                    "processing_time": "120.5s"
                },
                "validation": {
                    "cross_validation_score": 0.91,
                    "manual_validation_agreement": 0.89
                },
                "timestamp": datetime.now().isoformat()
            }

            self.results["tissue_segmentation"] = tissue_segmentation
            logger.info("✅ Segmentación de tejidos cerebrales completada")
            return tissue_segmentation

        except ValueError as e:
            logger.error("❌ Error en segmentación de tejidos: %s", e)
            return {"error": str(e)}

    async def detect_medical_anomalies(self) -> Dict[str, Any]:
        """
        Detección automática de anomalías médicas.

        Incluye:
        - Tumores y lesiones
        - Anomalías vasculares
        - Cambios patológicos
        - Clasificación por severidad
        """
        logger.info("🔍 Detectando anomalías médicas...")

        # Configuración de detección
        anomaly_config = {
            "scan_type": "brain_mri",
            "anomaly_types": ["tumor", "stroke", "lesion", "hemorrhage", "atrophy"],
            "sensitivity": 0.85,
            "specificity": 0.92,
            "model_version": "v2.1"
        }

        try:
            # Detección de anomalías
            detection_result = await self.imaging_service.detect_anomalies(
                image_data=anomaly_config,
                anomaly_types=anomaly_config["anomaly_types"]
            )

            # Análisis de severidad
            severity_analysis = {
                "severity_classification": {
                    "high": len([a for a in detection_result.get("detected_anomalies", [])
                               if a.get("severity") == "high"]),
                    "moderate": len([a for a in detection_result.get("detected_anomalies", [])
                                   if a.get("severity") == "moderate"]),
                    "low": len([a for a in detection_result.get("detected_anomalies", [])
                              if a.get("severity") == "low"])
                },
                "risk_assessment": {
                    "immediate_risk": "moderate",
                    "progression_risk": "high",
                    "treatment_urgency": "medium"
                }
            }

            anomaly_detection = {
                "detection_config": anomaly_config,
                "detected_anomalies": detection_result.get("detected_anomalies", []),
                "performance_metrics": {
                    "sensitivity": detection_result.get("sensitivity", 0),
                    "specificity": anomaly_config["specificity"],
                    "precision": 0.88,
                    "f1_score": 0.87
                },
                "severity_analysis": severity_analysis,
                "false_positive_analysis": {
                    "count": detection_result.get("false_positives", 0),
                    "rate": 0.03
                },
                "timestamp": datetime.now().isoformat()
            }

            self.results["anomaly_detection"] = anomaly_detection
            logger.info("✅ Detección de anomalías médicas completada")
            return anomaly_detection

        except ValueError as e:
            logger.error("❌ Error en detección de anomalías: %s", e)
            return {"error": str(e)}

    async def analyze_temporal_progression(self) -> Dict[str, Any]:
        """
        Análisis de progresión temporal de enfermedades.

        Incluye:
        - Seguimiento longitudinal
        - Tasas de cambio
        - Predicción de evolución
        - Comparación con baselines
        """
        logger.info("📈 Analizando progresión temporal...")

        # Serie temporal de imágenes
        temporal_series = [
            {
                "image_id": f"BRAIN_T{i}",
                "timestamp": f"2024-{i+1:02d}-01",
                "lesion_volume": 10.5 + i * 0.8,  # Crecimiento simulado
                "edema_extent": 25.3 + i * 1.2
            }
            for i in range(6)  # 6 meses de seguimiento
        ]

        try:
            # Análisis temporal
            temporal_analysis = await self.imaging_service.analyze_temporal_changes(
                image_series=temporal_series
            )

            # Comparaciones pareadas
            comparisons = []
            for i in range(len(temporal_series) - 1):
                comparison = await self.imaging_service.compare_images(
                    temporal_series[i],
                    temporal_series[i + 1]
                )
                comparisons.append({
                    "time_points": [temporal_series[i]["timestamp"], temporal_series[i + 1]["timestamp"]],
                    "comparison": comparison
                })

            temporal_progression = {
                "temporal_series": temporal_series,
                "change_analysis": temporal_analysis.get("temporal_analysis", {}),
                "pairwise_comparisons": comparisons,
                "progression_metrics": {
                    "growth_rate": 0.15,  # mm³/mes
                    "doubling_time": 4.6,  # meses
                    "volumetric_trend": "exponential"
                },
                "prediction": {
                    "next_6_months_volume": 18.7,
                    "confidence_interval": [15.2, 22.1],
                    "risk_progression": "high"
                },
                "clinical_correlation": {
                    "symptom_progression": "moderate",
                    "treatment_response": "partial",
                    "prognostic_indicators": ["size_increase", "edema_expansion"]
                },
                "timestamp": datetime.now().isoformat()
            }

            self.results["temporal_analysis"] = temporal_progression
            logger.info("✅ Análisis de progresión temporal completado")
            return temporal_progression

        except ValueError as e:
            logger.error("❌ Error en análisis temporal: %s", e)
            return {"error": str(e)}

    async def run_comprehensive_imaging_analysis(self) -> Dict[str, Any]:
        """
        Ejecutar análisis completo de imágenes médicas.

        Combina todos los análisis en un flujo de trabajo integrado.
        """
        logger.info("🚀 Iniciando análisis comprehensivo de imágenes médicas...")

        try:
            # Inicializar servicios
            await self.initialize_services()

            # Ejecutar análisis secuencialmente
            image_analysis = await self.analyze_medical_image()
            tissue_segmentation = await self.segment_brain_tissues()
            anomaly_detection = await self.detect_medical_anomalies()
            temporal_analysis = await self.analyze_temporal_progression()

            # Generar reporte integrado
            comprehensive_report = {
                "analysis_type": "Medical Imaging Comprehensive Analysis",
                "timestamp": datetime.now().isoformat(),
                "patient_info": {
                    "id": "PAT_001",
                    "age": 45,
                    "sex": "F",
                    "diagnosis": "Glioblastoma multiforme"
                },
                "results": {
                    "image_analysis": image_analysis,
                    "tissue_segmentation": tissue_segmentation,
                    "anomaly_detection": anomaly_detection,
                    "temporal_analysis": temporal_analysis
                },
                "summary": {
                    "total_analyses": 4,
                    "successful_analyses": len([r for r in self.results.values() if "error" not in r]),
                    "key_findings": self._extract_key_imaging_findings(),
                    "clinical_recommendations": self._generate_imaging_recommendations()
                },
                "metadata": {
                    "services_used": ["AdvancedMedicalImagingService"],
                    "modalities_processed": ["MRI_T1", "MRI_FLAIR", "CT"],
                    "ai_models_used": ["DeepLesion", "nnU-Net", "TemporalCNN"],
                    "processing_time": "285.7s"
                }
            }

            # Guardar resultados
            self.results["comprehensive_report"] = comprehensive_report

            logger.info("✅ Análisis comprehensivo de imágenes médicas completado")
            return comprehensive_report

        except ValueError as e:
            logger.error("❌ Error en análisis comprehensivo: %s", e)
            return {"error": str(e)}

    def _extract_key_imaging_findings(self) -> List[str]:
        """Extraer hallazgos clave de todos los análisis."""
        findings = []

        # Hallazgos de análisis de imagen
        if "image_analysis" in self.results:
            img = self.results["image_analysis"]
            if "anomaly_detection" in img and img["anomaly_detection"]:
                findings.append(f"{len(img['anomaly_detection'])} anomalías detectadas en imagen")

        # Hallazgos de segmentación
        if "tissue_segmentation" in self.results:
            seg = self.results["tissue_segmentation"]
            if "tissue_volumes" in seg:
                findings.append("Segmentación volumétrica de tejidos completada")

        # Hallazgos de anomalías
        if "anomaly_detection" in self.results:
            ano = self.results["anomaly_detection"]
            if "detected_anomalies" in ano:
                findings.append(f"{len(ano['detected_anomalies'])} anomalías clasificadas por severidad")

        # Hallazgos temporales
        if "temporal_analysis" in self.results:
            temp = self.results["temporal_analysis"]
            if "progression_metrics" in temp:
                findings.append("Análisis de progresión temporal realizado")

        return findings

    def _generate_imaging_recommendations(self) -> List[str]:
        """Generar recomendaciones clínicas basadas en los resultados."""
        return [
            "Seguimiento por imágenes en 3 meses para evaluar progresión",
            "Considerar biopsia guiada por imagen para confirmación histológica",
            "Evaluación multidisciplinaria con neurocirugía y oncología",
            "Monitoreo clínico estrecho de síntomas neurológicos",
            "Inicio de tratamiento adyuvante según protocolo institucional"
        ]

    async def save_results(self, output_file: str = "medical_imaging_analysis_results.json"):
        """Guardar resultados del análisis en archivo JSON."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Convertir arrays numpy a listas para serialización JSON
                json_results = self._convert_numpy_arrays(self.results)
                json.dump(json_results, f, indent=2, ensure_ascii=False)

            logger.info("✅ Resultados guardados en %s", output_file)
            return True

        except (IOError, OSError) as e:
            logger.error("❌ Error guardando resultados: %s", e)
            return False

    def _convert_numpy_arrays(self, obj):
        """Convertir arrays numpy a tipos serializables."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_arrays(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_arrays(item) for item in obj]
        else:
            return obj

    async def display_summary(self):
        """Mostrar resumen de los resultados."""
        print("\n" + "="*80)
        print("🏥 RESUMEN DEL ANÁLISIS DE IMÁGENES MÉDICAS")
        print("="*80)

        if "comprehensive_report" in self.results:
            report = self.results["comprehensive_report"]

            print(f"\n📊 Tipo de Análisis: {report['analysis_type']}")
            print(f"🕒 Timestamp: {report['timestamp']}")
            print(f"👤 Paciente: {report['patient_info']['id']} ({report['patient_info']['age']} años)")

            print("\n🔬 Análisis Realizados:")
            results = report['results']
            for analysis_type, result in results.items():
                status = "✅" if "error" not in result else "❌"
                print(f"  {status} {analysis_type.replace('_', ' ').title()}")

            print("\n🎯 Hallazgos Clave:")
            for finding in report['summary']['key_findings']:
                print(f"  • {finding}")

            print("\n💊 Recomendaciones Clínicas:")
            for rec in report['summary']['clinical_recommendations']:
                print(f"  • {rec}")

        print("\n" + "="*80)


async def main():
    """Función principal del ejemplo."""
    print("🏥 Ejemplo Práctico de Imágenes Médicas - Análisis Avanzado")
    print("="*65)

    # Crear instancia del ejemplo
    example = MedicalImagingPracticalExample()

    try:
        # Ejecutar análisis completo
        await example.run_comprehensive_imaging_analysis()

        # Mostrar resumen
        await example.display_summary()

        # Guardar resultados
        await example.save_results()

        print("\n✅ Ejemplo de imágenes médicas completado exitosamente!")
        print("📁 Resultados guardados en: medical_imaging_analysis_results.json")

    except (RuntimeError, ValueError) as e:
        logger.error("❌ Error ejecutando ejemplo: %s", e)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    # Ejecutar ejemplo
    asyncio.run(main())
