#!/usr/bin/env python3
"""
Biomechanics Practical Example - Advanced Movement Analysis and Simulation
===========================================================================

Este ejemplo demuestra el uso completo del servicio de biomecánica para:
- Análisis de marcha y movimiento humano
- Modelado biomecánico 3D
- Análisis de fuerzas musculares
- Simulación de movimiento
- Evaluación de rendimiento deportivo

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


class MockBiomechanicsService:
    """Mock service para simular análisis biomecánico avanzado."""

    async def initialize(self):
        pass

    async def analyze_gait(self, motion_data: Dict, analysis_type: str) -> Dict[str, Any]:
        """Análisis mock de marcha."""
        return {
            "gait_parameters": {
                "cadence": 110.5,  # pasos/minuto
                "stride_length": 1.45,  # metros
                "walking_speed": 1.68,  # m/s
                "step_width": 0.12  # metros
            },
            "joint_kinematics": {
                "hip_flexion": {"range": 45.2, "peak": 28.5},
                "knee_flexion": {"range": 62.1, "peak": 38.9},
                "ankle_dorsiflexion": {"range": 25.8, "peak": 12.3}
            },
            "temporal_parameters": {
                "stance_phase": 62.5,  # % del ciclo de marcha
                "swing_phase": 37.5,   # % del ciclo de marcha
                "double_support": 21.3 # % del ciclo de marcha
            },
            "symmetry_index": 0.92  # 1.0 = perfectamente simétrico
        }

    async def analyze_muscle_forces(self, motion_data: Dict, muscle_groups: List[str]) -> Dict[str, Any]:
        """Análisis mock de fuerzas musculares."""
        return {
            "muscle_forces": {
                muscle: {
                    "peak_force": np.random.uniform(500, 2500),  # Newtons
                    "force_profile": "unimodal",
                    "activation_pattern": "phasic"
                }
                for muscle in muscle_groups
            },
            "joint_moments": {
                "hip": {"flexor_moment": 85.3, "abductor_moment": 45.2},
                "knee": {"extensor_moment": 120.8, "varus_moment": 15.6},
                "ankle": {"plantarflexor_moment": 95.4}
            },
            "power_analysis": {
                "hip_power": 1.25,  # W/kg
                "knee_power": 2.15,  # W/kg
                "ankle_power": 3.85   # W/kg
            }
        }

    async def create_3d_model(self, anatomical_data: Dict, model_type: str) -> Dict[str, Any]:
        """Creación mock de modelo 3D."""
        return {
            "model_info": {
                "type": model_type,
                "segments": 15,
                "degrees_of_freedom": 23,
                "markers": 45
            },
            "anthropometric_parameters": {
                "height": 1.75,  # metros
                "mass": 70.5,    # kg
                "body_segments": {
                    "head": {"mass": 4.8, "length": 0.25},
                    "trunk": {"mass": 28.2, "length": 0.65},
                    "upper_arm": {"mass": 2.1, "length": 0.32},
                    "forearm": {"mass": 1.4, "length": 0.27},
                    "hand": {"mass": 0.6, "length": 0.18},
                    "thigh": {"mass": 8.9, "length": 0.42},
                    "shank": {"mass": 4.2, "length": 0.41},
                    "foot": {"mass": 1.1, "length": 0.23}
                }
            },
            "joint_centers": {
                "hip": [0.0, 0.0, 0.92],
                "knee": [0.0, 0.0, 0.48],
                "ankle": [0.0, 0.0, 0.08]
            },
            "validation_metrics": {
                "marker_residuals": 0.012,  # metros
                "joint_center_accuracy": 0.008  # metros
            }
        }

    async def simulate_movement(self, initial_conditions: Dict, simulation_params: Dict) -> Dict[str, Any]:
        """Simulación mock de movimiento."""
        duration = simulation_params.get("duration", 2.0)
        time_steps = int(duration * 100)  # 100 Hz

        return {
            "simulation_info": {
                "duration": duration,
                "time_steps": time_steps,
                "sampling_rate": 100,  # Hz
                "solver": "Runge-Kutta 4th order"
            },
            "kinematic_trajectories": {
                "joint_angles": np.random.rand(time_steps, 6).tolist(),  # 6 DOF
                "segment_positions": np.random.rand(time_steps, 9).tolist(),  # 3 segmentos x 3D
                "center_of_mass": np.random.rand(time_steps, 3).tolist()
            },
            "kinetic_trajectories": {
                "joint_forces": np.random.rand(time_steps, 6).tolist(),
                "joint_moments": np.random.rand(time_steps, 6).tolist(),
                "ground_reaction_forces": np.random.rand(time_steps, 3).tolist()
            },
            "energy_analysis": {
                "mechanical_energy": np.random.rand(time_steps).tolist(),
                "metabolic_cost": 3.25,  # J/kg
                "efficiency": 0.78
            },
            "stability_metrics": {
                "margin_of_stability": 0.085,  # metros
                "dynamic_balance_index": 0.92
            }
        }

    async def analyze_sports_performance(self, athlete_data: Dict, sport_type: str) -> Dict[str, Any]:
        """Análisis mock de rendimiento deportivo."""
        return {
            "performance_metrics": {
                "power_output": 285.5,  # watts
                "force_velocity_profile": {
                    "max_force": 3200,  # N
                    "max_velocity": 3.2,  # m/s
                    "power_peak": 285.5   # W
                },
                "technique_efficiency": 0.87,
                "coordination_index": 0.91
            },
            "biomechanical_analysis": {
                "joint_loading": {
                    "peak_impact_force": 2.8,  # x body weight
                    "joint_stress_distribution": "optimal"
                },
                "movement_economy": {
                    "oxygen_cost": 0.18,  # ml/kg/min
                    "mechanical_efficiency": 0.82
                }
            },
            "injury_risk_assessment": {
                "overall_risk": "low",
                "critical_factors": ["asymmetric_loading", "high_impact_forces"],
                "preventive_recommendations": [
                    "Strengthen lower extremity muscles",
                    "Improve landing technique",
                    "Increase flexibility training"
                ]
            },
            "training_recommendations": {
                "periodization": "strength_endurance_phase",
                "focus_areas": ["power_development", "technique_refinement"],
                "recovery_needs": "moderate"
            }
        }

    async def assess_rehabilitation_progress(self, patient_data: Dict, baseline_data: Dict) -> Dict[str, Any]:
        """Evaluación mock de progreso de rehabilitación."""
        return {
            "progress_metrics": {
                "functional_recovery": 0.78,  # 0-1 scale
                "strength_gains": {
                    "quadriceps": 0.65,
                    "hamstrings": 0.58,
                    "calf_muscles": 0.72
                },
                "range_of_motion": {
                    "knee_flexion": 0.85,
                    "ankle_dorsiflexion": 0.91
                }
            },
            "comparison_to_baseline": {
                "gait_symmetry_improvement": 0.23,
                "weight_bearing_distribution": "improved",
                "pain_reduction": 0.34
            },
            "rehabilitation_effectiveness": {
                "treatment_response": "excellent",
                "recovery_trajectory": "accelerated",
                "functional_goals_achievement": 0.82
            },
            "clinical_recommendations": {
                "continue_current_protocol": True,
                "adjustments_needed": ["increase_resistance", "add_balance_training"],
                "follow_up_schedule": "weekly_assessments"
            }
        }


class BiomechanicsPracticalExample:
    """
    Ejemplo práctico completo de análisis biomecánico.

    Incluye:
    - Análisis de marcha
    - Modelado 3D
    - Análisis de fuerzas
    - Simulación de movimiento
    - Evaluación deportiva
    """

    def __init__(self):
        self.biomechanics_service = MockBiomechanicsService()
        self.results = {}

    async def initialize_services(self):
        """Inicializar servicios de biomecánica."""
        logger.info("🏃 Inicializando servicios de biomecánica...")

        try:
            await self.biomechanics_service.initialize()
            logger.info("✅ MockBiomechanicsService inicializado")

        except Exception as e:
            logger.error("❌ Error inicializando servicios: %s", e)
            raise

    async def analyze_human_gait(self) -> Dict[str, Any]:
        """
        Análisis completo de marcha humana.

        Incluye:
        - Parámetros espaciotemporales
        - Cinemática articular
        - Simetría y coordinación
        - Análisis de fases
        """
        logger.info("🚶 Analizando marcha humana...")

        # Datos de movimiento de ejemplo (captura de movimiento)
        motion_data = {
            "subject_id": "SUBJ_001",
            "trial_type": "normal_walking",
            "sampling_rate": 100,  # Hz
            "duration": 10.0,      # segundos
            "markers": {
                "LASI": [0.1, 0.9, 0.0],   # Left anterior superior iliac spine
                "RASI": [-0.1, 0.9, 0.0],  # Right anterior superior iliac spine
                "LKNE": [0.08, 0.48, 0.0], # Left knee
                "RKNE": [-0.08, 0.48, 0.0],# Right knee
                "LANK": [0.05, 0.08, 0.0], # Left ankle
                "RANK": [-0.05, 0.08, 0.0] # Right ankle
            },
            "force_plates": {
                "left": {"force": [0, 0, 700], "cop": [0.02, 0.05]},   # Newtons, meters
                "right": {"force": [0, 0, 650], "cop": [-0.02, 0.05]}
            }
        }

        try:
            # Análisis de marcha
            gait_analysis = await self.biomechanics_service.analyze_gait(
                motion_data=motion_data,
                analysis_type="comprehensive"
            )

            # Análisis de fuerzas musculares
            muscle_groups = ["quadriceps", "hamstrings", "gastrocnemius", "tibialis_anterior"]
            muscle_analysis = await self.biomechanics_service.analyze_muscle_forces(
                motion_data=motion_data,
                muscle_groups=muscle_groups
            )

            gait_result = {
                "motion_capture_data": motion_data,
                "gait_analysis": gait_analysis,
                "muscle_force_analysis": muscle_analysis,
                "biomechanical_assessment": {
                    "gait_quality_score": 0.88,
                    "risk_factors": ["mild_asymmetry", "reduced_ankle_range"],
                    "clinical_insights": "Normal gait pattern with minor asymmetries"
                },
                "processing_metadata": {
                    "analysis_time": "45.2s",
                    "algorithms_used": ["inverse_kinematics", "muscle_force_estimation"],
                    "validation_score": 0.94
                },
                "timestamp": datetime.now().isoformat()
            }

            self.results["gait_analysis"] = gait_result
            logger.info("✅ Análisis de marcha humana completado")
            return gait_result

        except ValueError as e:
            logger.error("❌ Error en análisis de marcha: %s", e)
            return {"error": str(e)}

    async def create_musculoskeletal_model(self) -> Dict[str, Any]:
        """
        Creación de modelo musculoesquelético 3D.

        Incluye:
        - Modelado antropométrico
        - Definición de centros articulares
        - Validación del modelo
        - Análisis de grados de libertad
        """
        logger.info("🦴 Creando modelo musculoesquelético 3D...")

        # Datos anatómicos de ejemplo
        anatomical_data = {
            "subject_id": "SUBJ_001",
            "height": 1.75,      # metros
            "mass": 70.5,        # kg
            "sex": "male",
            "age": 28,
            "body_segments": {
                "head_neck": {"length": 0.25, "mass_fraction": 0.081},
                "trunk": {"length": 0.65, "mass_fraction": 0.497},
                "upper_arm": {"length": 0.32, "mass_fraction": 0.028},
                "forearm": {"length": 0.27, "mass_fraction": 0.016},
                "hand": {"length": 0.18, "mass_fraction": 0.006},
                "thigh": {"length": 0.42, "mass_fraction": 0.100},
                "shank": {"length": 0.41, "mass_fraction": 0.046},
                "foot": {"length": 0.23, "mass_fraction": 0.014}
            },
            "joint_constraints": {
                "hip": {"type": "ball_socket", "dof": 3},
                "knee": {"type": "hinge", "dof": 1},
                "ankle": {"type": "hinge", "dof": 1}
            }
        }

        try:
            # Creación del modelo 3D
            model_3d = await self.biomechanics_service.create_3d_model(
                anatomical_data=anatomical_data,
                model_type="musculoskeletal"
            )

            # Simulación de movimiento
            simulation_result = await self.biomechanics_service.simulate_movement(
                initial_conditions={
                    "joint_angles": [0, 0, 0, 30, 0, 0],  # grados
                    "angular_velocities": [0, 0, 0, 0, 0, 0]  # rad/s
                },
                simulation_params={
                    "duration": 2.0,  # segundos
                    "time_step": 0.01,  # segundos
                    "gravity": [0, 0, -9.81],  # m/s²
                    "ground_contact": True
                }
            )

            model_result = {
                "anatomical_data": anatomical_data,
                "3d_model": model_3d,
                "simulation_results": simulation_result,
                "model_validation": {
                    "anthropometric_accuracy": 0.96,
                    "kinematic_consistency": 0.98,
                    "dynamic_equilibrium": 0.95
                },
                "clinical_applications": {
                    "gait_analysis": "validated",
                    "rehabilitation_planning": "suitable",
                    "sports_performance": "optimized"
                },
                "timestamp": datetime.now().isoformat()
            }

            self.results["musculoskeletal_model"] = model_result
            logger.info("✅ Modelo musculoesquelético 3D creado")
            return model_result

        except ValueError as e:
            logger.error("❌ Error en creación del modelo: %s", e)
            return {"error": str(e)}

    async def analyze_sports_performance(self) -> Dict[str, Any]:
        """
        Análisis de rendimiento deportivo.

        Incluye:
        - Perfil fuerza-velocidad
        - Eficiencia técnica
        - Análisis de coordinación
        - Evaluación de riesgo de lesión
        """
        logger.info("⚽ Analizando rendimiento deportivo...")

        # Datos de atleta de ejemplo
        athlete_data = {
            "athlete_id": "ATH_001",
            "sport": "basketball",
            "position": "forward",
            "age": 24,
            "height": 2.01,  # metros
            "mass": 98.5,     # kg
            "performance_data": {
                "vertical_jump": 0.85,  # metros
                "sprint_10m": 1.85,     # segundos
                "agility_test": 8.92,   # segundos
                "max_strength": {
                    "squat": 180,       # kg
                    "bench_press": 120, # kg
                    "deadlift": 200     # kg
                }
            },
            "injury_history": ["ankle_sprain_2023", "knee_strain_2022"],
            "training_load": "high"
        }

        try:
            # Análisis de rendimiento deportivo
            performance_analysis = await self.biomechanics_service.analyze_sports_performance(
                athlete_data=athlete_data,
                sport_type="basketball"
            )

            # Evaluación de progreso de rehabilitación (si aplica)
            if athlete_data["injury_history"]:
                rehab_assessment = await self.biomechanics_service.assess_rehabilitation_progress(
                    patient_data=athlete_data,
                    baseline_data={
                        "pre_injury_performance": {
                            "vertical_jump": 0.92,
                            "sprint_10m": 1.78
                        }
                    }
                )
            else:
                rehab_assessment = None

            sports_result = {
                "athlete_profile": athlete_data,
                "performance_analysis": performance_analysis,
                "rehabilitation_assessment": rehab_assessment,
                "training_prescription": {
                    "periodization_phase": "competition_preparation",
                    "focus_exercises": ["plyometrics", "strength_training", "agility_drills"],
                    "recovery_strategies": ["active_recovery", "nutrition_optimization"],
                    "monitoring_metrics": ["power_output", "technique_efficiency"]
                },
                "injury_prevention": {
                    "risk_level": "moderate",
                    "preventive_measures": ["proper_warmup", "technique_drills", "load_management"],
                    "monitoring_schedule": "biweekly_assessments"
                },
                "timestamp": datetime.now().isoformat()
            }

            self.results["sports_performance"] = sports_result
            logger.info("✅ Análisis de rendimiento deportivo completado")
            return sports_result

        except ValueError as e:
            logger.error("❌ Error en análisis deportivo: %s", e)
            return {"error": str(e)}

    async def run_comprehensive_biomechanics_analysis(self) -> Dict[str, Any]:
        """
        Ejecutar análisis biomecánico completo.

        Combina todos los análisis en un flujo de trabajo integrado.
        """
        logger.info("🚀 Iniciando análisis biomecánico comprehensivo...")

        try:
            # Inicializar servicios
            await self.initialize_services()

            # Ejecutar análisis secuencialmente
            gait_analysis = await self.analyze_human_gait()
            musculoskeletal_model = await self.create_musculoskeletal_model()
            sports_performance = await self.analyze_sports_performance()

            # Generar reporte integrado
            comprehensive_report = {
                "analysis_type": "Biomechanics Comprehensive Analysis",
                "timestamp": datetime.now().isoformat(),
                "subject_info": {
                    "id": "SUBJ_001",
                    "type": "Multi-purpose Analysis",
                    "description": "Análisis integrado de marcha, modelado 3D y rendimiento deportivo"
                },
                "results": {
                    "gait_analysis": gait_analysis,
                    "musculoskeletal_model": musculoskeletal_model,
                    "sports_performance": sports_performance
                },
                "summary": {
                    "total_analyses": 3,
                    "successful_analyses": len([r for r in self.results.values() if "error" not in r]),
                    "key_findings": self._extract_key_biomechanics_findings(),
                    "clinical_recommendations": self._generate_biomechanics_recommendations()
                },
                "metadata": {
                    "services_used": ["MockBiomechanicsService"],
                    "analysis_types": ["gait_analysis", "3d_modeling", "sports_performance"],
                    "data_sources": ["motion_capture", "force_plates", "anthropometric_data"],
                    "processing_time": "142.8s"
                }
            }

            # Guardar resultados
            self.results["comprehensive_report"] = comprehensive_report

            logger.info("✅ Análisis biomecánico comprehensivo completado")
            return comprehensive_report

        except ValueError as e:
            logger.error("❌ Error en análisis comprehensivo: %s", e)
            return {"error": str(e)}

    def _extract_key_biomechanics_findings(self) -> List[str]:
        """Extraer hallazgos clave de todos los análisis."""
        findings = []

        # Hallazgos de marcha
        if "gait_analysis" in self.results:
            gait = self.results["gait_analysis"]
            if "gait_analysis" in gait:
                findings.append("Análisis de marcha completado con parámetros espaciotemporales")

        # Hallazgos de modelado
        if "musculoskeletal_model" in self.results:
            model = self.results["musculoskeletal_model"]
            if "3d_model" in model:
                findings.append("Modelo musculoesquelético 3D creado y validado")

        # Hallazgos deportivos
        if "sports_performance" in self.results:
            sports = self.results["sports_performance"]
            if "performance_analysis" in sports:
                findings.append("Análisis de rendimiento deportivo realizado")

        return findings

    def _generate_biomechanics_recommendations(self) -> List[str]:
        """Generar recomendaciones clínicas basadas en los resultados."""
        return [
            "Implementar programa de fortalecimiento muscular para mejorar simetría de marcha",
            "Optimizar técnica deportiva mediante análisis biomecánico detallado",
            "Monitoreo continuo del rendimiento para prevenir lesiones",
            "Integrar datos biomecánicos en planes de rehabilitación personalizados"
        ]

    async def save_results(self, output_file: str = "biomechanics_analysis_results.json"):
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
        print("🏃 RESUMEN DEL ANÁLISIS BIOMECÁNICO")
        print("="*80)

        if "comprehensive_report" in self.results:
            report = self.results["comprehensive_report"]

            print(f"\n📊 Tipo de Análisis: {report['analysis_type']}")
            print(f"🕒 Timestamp: {report['timestamp']}")
            print(f"👤 Sujeto: {report['subject_info']['id']}")

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
    print("🏃 Ejemplo Práctico de Biomecánica - Análisis Avanzado")
    print("="*60)

    # Crear instancia del ejemplo
    example = BiomechanicsPracticalExample()

    try:
        # Ejecutar análisis completo
        await example.run_comprehensive_biomechanics_analysis()

        # Mostrar resumen
        await example.display_summary()

        # Guardar resultados
        await example.save_results()

        print("\n✅ Ejemplo de biomecánica completado exitosamente!")
        print("📁 Resultados guardados en: biomechanics_analysis_results.json")

    except (RuntimeError, ValueError) as e:
        logger.error("❌ Error ejecutando ejemplo: %s", e)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    # Ejecutar ejemplo
    asyncio.run(main())
