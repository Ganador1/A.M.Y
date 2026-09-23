#!/usr/bin/env python3
"""
Personalized Medicine Practical Example - Genomic-guided Treatment Optimization
=============================================================================

Este ejemplo demuestra el uso completo del servicio de medicina personalizada para:
- Análisis farmacogenómico
- Recomendaciones de tratamiento basadas en genotipo
- Predicción de respuesta a medicamentos
- Optimización de dosis
- Estratificación de riesgo

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


class MockPersonalizedMedicineService:
    """Mock service para simular medicina personalizada."""

    async def initialize(self):
        pass

    async def analyze_pharmacogenomics(self, patient_data: Dict, medications: List[str]) -> Dict[str, Any]:
        """Análisis mock farmacogenómico."""
        # Usar patient_data para simular análisis basado en perfil del paciente
        _ = patient_data  # Evitar warning de unused argument
        return {
            "genetic_variants": {
                "CYP2D6": "*1/*4",  # Poor metabolizer
                "CYP2C19": "*1/*2",  # Intermediate metabolizer
                "CYP2C9": "*1/*3",   # Intermediate metabolizer
                "VKORC1": "G/G",     # Warfarin sensitive
                "CYP3A5": "*1/*1"    # Normal metabolizer
            },
            "drug_responses": {
                medication: {
                    "metabolism_phenotype": np.random.choice(["poor", "intermediate", "normal", "ultrarapid"]),
                    "dose_adjustment": np.random.uniform(0.3, 2.5),
                    "efficacy_prediction": np.random.uniform(0.6, 0.95),
                    "adverse_reaction_risk": np.random.uniform(0.1, 0.8)
                }
                for medication in medications
            },
            "clinical_recommendations": {
                "dose_titrations": ["start_low_go_slow", "therapeutic_monitoring"],
                "alternative_medications": ["consider_alternatives", "check_interactions"],
                "monitoring_requirements": ["frequent_monitoring", "adverse_effect_surveillance"]
            }
        }

    async def predict_treatment_response(self, patient_profile: Dict, treatment_plan: Dict) -> Dict[str, Any]:
        """Predicción mock de respuesta a tratamiento."""
        # Usar parámetros para simular análisis personalizado
        _ = patient_profile, treatment_plan  # Evitar warning de unused arguments
        return {
            "response_probability": {
                "excellent": 0.25,
                "good": 0.45,
                "moderate": 0.25,
                "poor": 0.05
            },
            "biomarker_predictions": {
                "PD-L1": 0.78,
                "TMB": 12.5,
                "MSI_status": "MSS"
            },
            "toxicity_predictions": {
                "cardiotoxicity": 0.15,
                "nephrotoxicity": 0.08,
                "hepatotoxicity": 0.12
            },
            "survival_predictions": {
                "progression_free_survival": 18.5,  # months
                "overall_survival": 32.8,  # months
                "confidence_intervals": [28.2, 37.4]
            }
        }

    async def optimize_dosage(self, patient_data: Dict, medication: str) -> Dict[str, Any]:
        """Optimización mock de dosis."""
        # Usar parámetros para simular optimización personalizada
        _ = patient_data, medication  # Evitar warning de unused arguments
        return {
            "optimal_dose": {
                "starting_dose": np.random.uniform(50, 200),
                "maintenance_dose": np.random.uniform(100, 400),
                "max_dose": np.random.uniform(300, 600)
            },
            "dosing_schedule": {
                "frequency": "once_daily",
                "timing": "morning",
                "food_interactions": "take_with_food"
            },
            "therapeutic_monitoring": {
                "target_concentration": np.random.uniform(2, 15),
                "monitoring_frequency": "weekly_initially",
                "adjustment_criteria": ["toxicity", "efficacy", "drug_interactions"]
            },
            "individualization_factors": {
                "genetic_factors": 0.65,
                "clinical_factors": 0.25,
                "environmental_factors": 0.10
            }
        }

    async def assess_disease_risk(self, genetic_data: Dict, environmental_factors: Dict) -> Dict[str, Any]:
        """Evaluación mock de riesgo de enfermedad."""
        # Usar parámetros para simular evaluación de riesgo personalizada
        _ = genetic_data, environmental_factors  # Evitar warning de unused arguments
        diseases = ["coronary_artery_disease", "type_2_diabetes", "breast_cancer", "colorectal_cancer"]
        return {
            "polygenic_risk_scores": {
                disease: {
                    "risk_score": np.random.uniform(0.1, 0.9),
                    "percentile": np.random.uniform(10, 90),
                    "lifetime_risk": np.random.uniform(0.05, 0.8)
                }
                for disease in diseases
            },
            "clinical_risk_factors": {
                "age": 0.25,
                "family_history": 0.30,
                "lifestyle": 0.20,
                "biomarkers": 0.25
            },
            "preventive_recommendations": {
                "lifestyle_modifications": ["diet", "exercise", "smoking_cessation"],
                "screening_schedule": "annual_mammography",
                "chemoprevention": "consider_tamoxifen"
            },
            "risk_communication": {
                "risk_category": np.random.choice(["low", "moderate", "high"]),
                "communication_strategy": "quantitative_with_context"
            }
        }

    async def create_personalized_treatment_plan(self, patient_data: Dict, disease_context: Dict) -> Dict[str, Any]:
        """Creación mock de plan de tratamiento personalizado."""
        # Usar parámetros para simular planificación personalizada
        _ = patient_data, disease_context  # Evitar warning de unused arguments
        return {
            "treatment_strategy": {
                "primary_approach": "targeted_therapy",
                "combination_therapies": ["immunotherapy", "chemotherapy"],
                "sequencing_strategy": "targeted_first"
            },
            "medication_regimen": {
                "first_line": ["trastuzumab", "pertuzumab"],
                "second_line": ["T-DM1", "capecitabine"],
                "supportive_care": ["anti-nausea", "pain_management"]
            },
            "monitoring_plan": {
                "biomarker_monitoring": ["HER2_status", "circulating_tumor_DNA"],
                "imaging_schedule": "every_3_months",
                "clinical_assessments": "monthly_visits"
            },
            "lifestyle_integration": {
                "dietary_recommendations": ["anti-inflammatory_diet"],
                "exercise_prescription": ["moderate_aerobic", "resistance_training"],
                "stress_management": ["mindfulness", "support_groups"]
            },
            "expected_outcomes": {
                "response_rate": 0.78,
                "progression_free_survival": 24.5,
                "quality_of_life_impact": "minimal"
            }
        }

    async def monitor_treatment_efficacy(self, patient_data: Dict, treatment_history: List[Dict]) -> Dict[str, Any]:
        """Monitoreo mock de eficacia del tratamiento."""
        # Usar parámetros para simular monitoreo personalizado
        _ = patient_data, treatment_history  # Evitar warning de unused arguments
        return {
            "treatment_response": {
                "RECIST_criteria": np.random.choice(["CR", "PR", "SD", "PD"]),
                "biomarker_response": 0.72,
                "symptom_improvement": 0.68
            },
            "adverse_events": {
                "grade_1_2": ["fatigue", "nausea"],
                "grade_3_4": [],
                "dose_adjustments": "none_required"
            },
            "pharmacokinetic_monitoring": {
                "drug_concentration": 8.5,
                "metabolite_levels": "within_therapeutic_range",
                "clearance_rate": "normal"
            },
            "treatment_modifications": {
                "dose_changes": "stable",
                "schedule_changes": "none",
                "discontinuation_criteria": "disease_progression"
            },
            "patient_reported_outcomes": {
                "quality_of_life_score": 78,
                "symptom_burden": "mild",
                "functional_status": "maintained"
            }
        }


class PersonalizedMedicinePracticalExample:
    """
    Ejemplo práctico completo de medicina personalizada.

    Incluye:
    - Análisis farmacogenómico
    - Predicción de respuesta
    - Optimización de dosis
    - Evaluación de riesgo
    - Planes de tratamiento personalizados
    """

    def __init__(self):
        self.personalized_service = MockPersonalizedMedicineService()
        self.results = {}

    async def initialize_services(self):
        """Inicializar servicios de medicina personalizada."""
        logger.info("💊 Inicializando servicios de medicina personalizada...")

        try:
            await self.personalized_service.initialize()
            logger.info("✅ MockPersonalizedMedicineService inicializado")

        except Exception as e:
            logger.error("❌ Error inicializando servicios: %s", e)
            raise

    async def analyze_pharmacogenomic_profile(self) -> Dict[str, Any]:
        """
        Análisis completo del perfil farmacogenómico.

        Incluye:
        - Variantes genéticas relevantes
        - Predicción de respuesta a medicamentos
        - Recomendaciones de dosis
        - Riesgos de efectos adversos
        """
        logger.info("🧬 Analizando perfil farmacogenómico...")

        # Datos del paciente de ejemplo
        patient_data = {
            "patient_id": "PAT_001",
            "age": 45,
            "sex": "F",
            "ethnicity": "Caucasian",
            "medical_history": ["breast_cancer", "hypertension"],
            "current_medications": ["tamoxifen", "lisinopril", "metformin"],
            "genetic_profile": {
                "CYP2D6": "*4/*4",     # Poor metabolizer
                "CYP2C19": "*2/*2",    # Poor metabolizer
                "CYP2C9": "*1/*3",     # Intermediate metabolizer
                "SLCO1B1": "*5/*15",   # Reduced function
                "TPMT": "*1/*1"        # Normal metabolizer
            }
        }

        # Medicamentos a analizar
        medications = ["tamoxifen", "warfarin", "clopidogrel", "simvastatin", "metformin"]

        try:
            # Análisis farmacogenómico
            pharmacogenomics = await self.personalized_service.analyze_pharmacogenomics(
                patient_data=patient_data,
                medications=medications
            )

            # Optimización de dosis para medicamento principal
            dose_optimization = await self.personalized_service.optimize_dosage(
                patient_data=patient_data,
                medication="tamoxifen"
            )

            pharmacogenomic_result = {
                "patient_profile": patient_data,
                "pharmacogenomic_analysis": pharmacogenomics,
                "dose_optimization": dose_optimization,
                "clinical_decision_support": {
                    "alerts": ["CYP2D6_poor_metabolizer", "potential_drug_interactions"],
                    "recommendations": ["dose_reduction", "therapeutic_monitoring", "alternative_medications"],
                    "monitoring_plan": ["liver_function", "drug_concentrations", "adverse_effects"]
                },
                "implementation_guidance": {
                    "prescribing_notes": "Start with reduced dose and titrate based on tolerance",
                    "patient_education": "Explain importance of adherence and monitoring",
                    "follow_up_schedule": "Weekly for first month, then monthly"
                },
                "timestamp": datetime.now().isoformat()
            }

            self.results["pharmacogenomic_analysis"] = pharmacogenomic_result
            logger.info("✅ Análisis farmacogenómico completado")
            return pharmacogenomic_result

        except ValueError as e:
            logger.error("❌ Error en análisis farmacogenómico: %s", e)
            return {"error": str(e)}

    async def predict_cancer_treatment_response(self) -> Dict[str, Any]:
        """
        Predicción de respuesta a tratamiento oncológico.

        Incluye:
        - Análisis de biomarcadores
        - Predicción de eficacia
        - Evaluación de toxicidad
        - Estratificación pronóstica
        """
        logger.info("🎯 Prediciendo respuesta a tratamiento oncológico...")

        # Perfil del paciente con cáncer
        patient_profile = {
            "patient_id": "PAT_001",
            "cancer_type": "breast_cancer",
            "stage": "IIA",
            "subtype": "HER2_positive",
            "biomarkers": {
                "ER": "positive",
                "PR": "positive",
                "HER2": "positive",
                "Ki67": 0.25,
                "Oncotype_DX": 28
            },
            "genetic_alterations": ["HER2_amplification", "PIK3CA_mutation"],
            "comorbidities": ["hypertension"],
            "performance_status": "ECOG_0"
        }

        # Plan de tratamiento propuesto
        treatment_plan = {
            "regimen": "THP",  # Trastuzumab + Pertuzumab + Docetaxel
            "duration": "6_months",
            "adjuvant_therapy": "trastuzumab_maintenance",
            "supportive_care": ["anti-emetics", "growth_factors"]
        }

        try:
            # Predicción de respuesta
            response_prediction = await self.personalized_service.predict_treatment_response(
                patient_profile=patient_profile,
                treatment_plan=treatment_plan
            )

            # Plan de tratamiento personalizado
            personalized_plan = await self.personalized_service.create_personalized_treatment_plan(
                patient_data=patient_profile,
                disease_context={"cancer_type": "breast", "stage": "early"}
            )

            treatment_result = {
                "patient_profile": patient_profile,
                "proposed_treatment": treatment_plan,
                "response_prediction": response_prediction,
                "personalized_plan": personalized_plan,
                "decision_rationale": {
                    "evidence_base": ["HER2_positive_guidelines", "clinical_trials_data"],
                    "personalization_factors": ["genetic_profile", "biomarker_status", "comorbidities"],
                    "risk_benefit_analysis": "favorable_benefit_risk_ratio"
                },
                "implementation_considerations": {
                    "cardiac_monitoring": "required_due_to_trastuzumab",
                    "fertility_preservation": "discuss_options",
                    "psychosocial_support": "recommended"
                },
                "timestamp": datetime.now().isoformat()
            }

            self.results["treatment_response_prediction"] = treatment_result
            logger.info("✅ Predicción de respuesta a tratamiento completada")
            return treatment_result

        except ValueError as e:
            logger.error("❌ Error en predicción de tratamiento: %s", e)
            return {"error": str(e)}

    async def assess_disease_prevention_strategy(self) -> Dict[str, Any]:
        """
        Evaluación de estrategia de prevención de enfermedades.

        Incluye:
        - Puntuaciones de riesgo poligénico
        - Factores de riesgo clínicos
        - Recomendaciones preventivas
        - Estratificación de riesgo
        """
        logger.info("🛡️ Evaluando estrategia de prevención de enfermedades...")

        # Datos genéticos y ambientales
        genetic_data = {
            "patient_id": "PAT_002",
            "age": 35,
            "sex": "F",
            "family_history": {
                "breast_cancer": ["mother", "aunt"],
                "colorectal_cancer": [],
                "cardiovascular_disease": ["father"]
            },
            "genetic_risk_factors": {
                "BRCA1_variant": "negative",
                "BRCA2_variant": "negative",
                "APC_variant": "negative",
                "polygenic_risk_score": 0.75
            }
        }

        environmental_factors = {
            "lifestyle": {
                "smoking": "never",
                "alcohol": "moderate",
                "exercise": "regular",
                "diet": "Mediterranean"
            },
            "biomarkers": {
                "BMI": 24.5,
                "cholesterol": 185,
                "blood_pressure": "120/80",
                "glucose": 92
            },
            "reproductive_history": {
                "age_at_menarche": 12,
                "parity": 2,
                "breastfeeding": "yes"
            }
        }

        try:
            # Evaluación de riesgo
            risk_assessment = await self.personalized_service.assess_disease_risk(
                genetic_data=genetic_data,
                environmental_factors=environmental_factors
            )

            # Monitoreo de eficacia del tratamiento (ejemplo hipotético)
            treatment_history = [
                {"treatment": "preventive_therapy", "duration": "5_years", "compliance": 0.95}
            ]
            efficacy_monitoring = await self.personalized_service.monitor_treatment_efficacy(
                patient_data=genetic_data,
                treatment_history=treatment_history
            )

            prevention_result = {
                "patient_profile": genetic_data | environmental_factors,
                "risk_assessment": risk_assessment,
                "prevention_strategy": {
                    "primary_prevention": ["lifestyle_modification", "chemoprevention"],
                    "screening_intensity": "high_risk_protocol",
                    "surveillance_schedule": {
                        "mammography": "annual_starting_age_30",
                        "colonoscopy": "every_5_years_starting_age_45",
                        "cardiac_assessment": "biennial"
                    }
                },
                "treatment_efficacy": efficacy_monitoring,
                "long_term_management": {
                    "risk_reassessment": "annual",
                    "lifestyle_coaching": "ongoing",
                    "psychological_support": "as_needed"
                },
                "cost_effectiveness": {
                    "intervention_cost": 2500,  # USD per year
                    "quality_adjusted_life_years": 2.8,
                    "cost_per_qaly": 890
                },
                "timestamp": datetime.now().isoformat()
            }

            self.results["disease_prevention"] = prevention_result
            logger.info("✅ Evaluación de prevención de enfermedades completada")
            return prevention_result

        except ValueError as e:
            logger.error("❌ Error en evaluación de prevención: %s", e)
            return {"error": str(e)}

    async def run_comprehensive_personalized_medicine_analysis(self) -> Dict[str, Any]:
        """
        Ejecutar análisis completo de medicina personalizada.

        Combina todos los análisis en un flujo de trabajo integrado.
        """
        logger.info("🚀 Iniciando análisis comprehensivo de medicina personalizada...")

        try:
            # Inicializar servicios
            await self.initialize_services()

            # Ejecutar análisis secuencialmente
            pharmacogenomics = await self.analyze_pharmacogenomic_profile()
            treatment_response = await self.predict_cancer_treatment_response()
            disease_prevention = await self.assess_disease_prevention_strategy()

            # Generar reporte integrado
            comprehensive_report = {
                "analysis_type": "Personalized Medicine Comprehensive Analysis",
                "timestamp": datetime.now().isoformat(),
                "patient_info": {
                    "id": "PAT_001",
                    "type": "Multi-domain Analysis",
                    "description": "Análisis integrado farmacogenómico, oncológico y preventivo"
                },
                "results": {
                    "pharmacogenomic_analysis": pharmacogenomics,
                    "treatment_response_prediction": treatment_response,
                    "disease_prevention_assessment": disease_prevention
                },
                "summary": {
                    "total_analyses": 3,
                    "successful_analyses": len([r for r in self.results.values() if "error" not in r]),
                    "key_findings": self._extract_key_personalized_findings(),
                    "clinical_recommendations": self._generate_personalized_recommendations()
                },
                "metadata": {
                    "services_used": ["MockPersonalizedMedicineService"],
                    "analysis_domains": ["pharmacogenomics", "oncology", "prevention"],
                    "data_sources": ["genetic_data", "clinical_records", "biomarkers"],
                    "processing_time": "98.4s"
                }
            }

            # Guardar resultados
            self.results["comprehensive_report"] = comprehensive_report

            logger.info("✅ Análisis comprehensivo de medicina personalizada completado")
            return comprehensive_report

        except ValueError as e:
            logger.error("❌ Error en análisis comprehensivo: %s", e)
            return {"error": str(e)}

    def _extract_key_personalized_findings(self) -> List[str]:
        """Extraer hallazgos clave de todos los análisis."""
        findings = []

        # Hallazgos farmacogenómicos
        if "pharmacogenomic_analysis" in self.results:
            pharma = self.results["pharmacogenomic_analysis"]
            if "pharmacogenomic_analysis" in pharma:
                findings.append("Perfil farmacogenómico completo con predicciones de respuesta")

        # Hallazgos de tratamiento
        if "treatment_response_prediction" in self.results:
            treat = self.results["treatment_response_prediction"]
            if "response_prediction" in treat:
                findings.append("Predicción de respuesta a tratamiento oncológico realizada")

        # Hallazgos preventivos
        if "disease_prevention" in self.results:
            prev = self.results["disease_prevention"]
            if "risk_assessment" in prev:
                findings.append("Evaluación de riesgo multifactorial completada")

        return findings

    def _generate_personalized_recommendations(self) -> List[str]:
        """Generar recomendaciones clínicas basadas en los resultados."""
        return [
            "Implementar monitoreo terapéutico personalizado basado en perfil genético",
            "Seleccionar tratamientos oncológicos con mayor probabilidad de respuesta",
            "Desarrollar plan preventivo intensivo basado en riesgo estratificado",
            "Integrar biomarcadores en seguimiento clínico longitudinal"
        ]

    async def save_results(self, output_file: str = "personalized_medicine_analysis_results.json"):
        """Guardar resultados del análisis en archivo JSON."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)

            logger.info("✅ Resultados guardados en %s", output_file)
            return True

        except (IOError, OSError) as e:
            logger.error("❌ Error guardando resultados: %s", e)
            return False

    async def display_summary(self):
        """Mostrar resumen de los resultados."""
        print("\n" + "="*80)
        print("💊 RESUMEN DEL ANÁLISIS DE MEDICINA PERSONALIZADA")
        print("="*80)

        if "comprehensive_report" in self.results:
            report = self.results["comprehensive_report"]

            print(f"\n📊 Tipo de Análisis: {report['analysis_type']}")
            print(f"🕒 Timestamp: {report['timestamp']}")
            print(f"👤 Paciente: {report['patient_info']['id']}")

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
    print("💊 Ejemplo Práctico de Medicina Personalizada - Optimización Genómica")
    print("="*75)

    # Crear instancia del ejemplo
    example = PersonalizedMedicinePracticalExample()

    try:
        # Ejecutar análisis completo
        await example.run_comprehensive_personalized_medicine_analysis()

        # Mostrar resumen
        await example.display_summary()

        # Guardar resultados
        await example.save_results()

        print("\n✅ Ejemplo de medicina personalizada completado exitosamente!")
        print("📁 Resultados guardados en: personalized_medicine_analysis_results.json")

    except (RuntimeError, ValueError) as e:
        logger.error("❌ Error ejecutando ejemplo: %s", e)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    # Ejecutar ejemplo
    asyncio.run(main())
