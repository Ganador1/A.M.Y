"""
Tests comprehensivos para BiomechanicsService
===========================================

Suite de testing para el servicio de biomecánica y análisis de movimiento.
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, List, Any

from app.domains.medicine.biomechanics_service import (
    BiomechanicsService, MotionCaptureData, GaitAnalysisResult,
    MusculoskeletalModel, ForceAnalysis, MovementPattern
)


class TestBiomechanicsService:
    """Test suite para BiomechanicsService"""

    @pytest.fixture
    def biomechanics_service(self):
        """Fixture para BiomechanicsService"""
        service = BiomechanicsService()
        service.initialize()
        return service

    @pytest.fixture
    def sample_motion_data(self):
        """Fixture para datos de captura de movimiento"""
        return MotionCaptureData(
            timestamp=datetime.now(),
            markers={
                "head": np.random.rand(1000, 3),
                "left_shoulder": np.random.rand(1000, 3),
                "right_shoulder": np.random.rand(1000, 3),
                "left_hip": np.random.rand(1000, 3),
                "right_hip": np.random.rand(1000, 3),
                "left_knee": np.random.rand(1000, 3),
                "right_knee": np.random.rand(1000, 3),
                "left_ankle": np.random.rand(1000, 3),
                "right_ankle": np.random.rand(1000, 3)
            },
            sampling_rate=120,
            subject_id="BIOMECH_TEST_001",
            activity="walking"
        )

    @pytest.fixture
    def sample_force_plate_data(self):
        """Fixture para datos de placa de fuerza"""
        return {
            "force_vectors": {
                "Fx": np.random.rand(2000) * 100,  # Fuerza lateral
                "Fy": np.random.rand(2000) * 100,  # Fuerza anteroposterior  
                "Fz": np.random.rand(2000) * 800 + 200,  # Fuerza vertical (peso corporal)
            },
            "moments": {
                "Mx": np.random.rand(2000) * 50,
                "My": np.random.rand(2000) * 50,
                "Mz": np.random.rand(2000) * 30
            },
            "center_of_pressure": {
                "CoPx": np.random.rand(2000) * 0.4 - 0.2,
                "CoPy": np.random.rand(2000) * 0.6 - 0.3
            },
            "sampling_rate": 240,
            "subject_mass_kg": 70
        }

    def test_service_initialization(self, biomechanics_service):
        """Test inicialización del servicio de biomecánica"""
        assert biomechanics_service.is_initialized
        assert len(biomechanics_service.supported_activities) > 0
        assert "walking" in biomechanics_service.supported_activities
        assert "running" in biomechanics_service.supported_activities
        assert "jumping" in biomechanics_service.supported_activities

    @pytest.mark.asyncio
    async def test_gait_analysis(self, biomechanics_service, sample_motion_data):
        """Test análisis de marcha"""
        with patch.object(biomechanics_service, '_analyze_gait_parameters') as mock_gait:
            mock_gait.return_value = GaitAnalysisResult(
                subject_id="BIOMECH_TEST_001",
                temporal_parameters={
                    "stride_length_m": 1.42,
                    "step_length_m": 0.71,
                    "cadence_steps_per_min": 108,
                    "walking_speed_ms": 1.28,
                    "stance_phase_percent": 62,
                    "swing_phase_percent": 38,
                    "double_support_percent": 12
                },
                spatial_parameters={
                    "step_width_m": 0.14,
                    "foot_angle_degrees": 8.5,
                    "pelvic_rotation_degrees": 4.2
                },
                joint_angles={
                    "hip_flexion_max": 35,
                    "knee_flexion_max": 68,
                    "ankle_dorsiflexion_max": 12,
                    "ankle_plantarflexion_max": 20
                },
                asymmetry_indices={
                    "stance_time_asymmetry": 2.1,
                    "swing_time_asymmetry": 1.8,
                    "step_length_asymmetry": 3.2
                }
            )
            
            result = await biomechanics_service.analyze_gait(
                motion_data=sample_motion_data,
                force_data=None,
                analysis_type="comprehensive"
            )
            
            assert result.temporal_parameters["stride_length_m"] > 1.0
            assert 100 <= result.temporal_parameters["cadence_steps_per_min"] <= 120
            assert result.temporal_parameters["stance_phase_percent"] > 50
            assert result.asymmetry_indices["step_length_asymmetry"] < 5.0  # Normal asymmetry
            mock_gait.assert_called_once()

    @pytest.mark.asyncio
    async def test_joint_kinematic_analysis(self, biomechanics_service, sample_motion_data):
        """Test análisis cinemático articular"""
        with patch.object(biomechanics_service, '_calculate_joint_kinematics') as mock_kinematics:
            mock_kinematics.return_value = {
                "hip_joint": {
                    "flexion_extension": {
                        "range_of_motion_degrees": 45,
                        "peak_flexion": 35,
                        "peak_extension": -10,
                        "angular_velocity_max": 180
                    },
                    "abduction_adduction": {
                        "range_of_motion_degrees": 15,
                        "peak_abduction": 8,
                        "peak_adduction": -7
                    }
                },
                "knee_joint": {
                    "flexion_extension": {
                        "range_of_motion_degrees": 70,
                        "peak_flexion": 68,
                        "peak_extension": -2,
                        "angular_velocity_max": 300
                    }
                },
                "ankle_joint": {
                    "dorsiflexion_plantarflexion": {
                        "range_of_motion_degrees": 32,
                        "peak_dorsiflexion": 12,
                        "peak_plantarflexion": -20,
                        "angular_velocity_max": 250
                    }
                }
            }
            
            result = await biomechanics_service.analyze_joint_kinematics(
                motion_data=sample_motion_data,
                joints=["hip", "knee", "ankle"],
                smoothing_filter=True
            )
            
            assert result["knee_joint"]["flexion_extension"]["range_of_motion_degrees"] > 60
            assert result["hip_joint"]["flexion_extension"]["peak_flexion"] > 0
            assert result["ankle_joint"]["dorsiflexion_plantarflexion"]["peak_plantarflexion"] < 0
            mock_kinematics.assert_called_once()

    @pytest.mark.asyncio
    async def test_force_analysis(self, biomechanics_service, sample_force_plate_data):
        """Test análisis de fuerzas"""
        with patch.object(biomechanics_service, '_analyze_ground_reaction_forces') as mock_forces:
            mock_forces.return_value = ForceAnalysis(
                subject_id="FORCE_TEST_001",
                peak_forces={
                    "vertical_force_N": 852.3,
                    "vertical_force_bw": 1.22,  # Body weight multiplier
                    "braking_force_N": 145.7,
                    "propulsive_force_N": 168.2,
                    "mediolateral_force_N": 89.4
                },
                loading_rates={
                    "vertical_loading_rate_N_per_s": 4250,
                    "time_to_peak_force_ms": 125
                },
                impulse_parameters={
                    "vertical_impulse_Ns": 89.7,
                    "braking_impulse_Ns": 12.3,
                    "propulsive_impulse_Ns": 14.8
                },
                center_of_pressure_metrics={
                    "cop_path_length_mm": 245,
                    "cop_velocity_mean_mm_s": 85.2,
                    "cop_area_mm2": 892
                }
            )
            
            result = await biomechanics_service.analyze_forces(
                force_data=sample_force_plate_data,
                analysis_type="ground_reaction_forces"
            )
            
            assert result.peak_forces["vertical_force_bw"] > 1.0  # Should exceed body weight
            assert result.loading_rates["vertical_loading_rate_N_per_s"] > 1000
            assert result.impulse_parameters["vertical_impulse_Ns"] > 0
            assert result.center_of_pressure_metrics["cop_path_length_mm"] > 0
            mock_forces.assert_called_once()

    @pytest.mark.asyncio
    async def test_musculoskeletal_modeling(self, biomechanics_service, sample_motion_data):
        """Test modelado musculoesquelético"""
        with patch.object(biomechanics_service, '_create_musculoskeletal_model') as mock_model:
            mock_model.return_value = MusculoskeletalModel(
                subject_id="MODEL_TEST_001",
                anthropometrics={
                    "height_m": 1.75,
                    "mass_kg": 70,
                    "leg_length_m": 0.92,
                    "thigh_length_m": 0.45,
                    "shank_length_m": 0.43
                },
                muscle_forces={
                    "gluteus_maximus": {"peak_force_N": 1250, "activation_timing": "heel_strike"},
                    "vastus_lateralis": {"peak_force_N": 980, "activation_timing": "loading_response"},
                    "gastrocnemius": {"peak_force_N": 1450, "activation_timing": "push_off"},
                    "tibialis_anterior": {"peak_force_N": 280, "activation_timing": "heel_strike"}
                },
                joint_moments={
                    "hip_extensor_moment_Nm": 125,
                    "knee_extensor_moment_Nm": 95,
                    "ankle_plantarflexor_moment_Nm": 145
                },
                joint_powers={
                    "hip_power_W": 180,
                    "knee_power_W": -85,  # Energy absorption
                    "ankle_power_W": 220   # Energy generation
                }
            )
            
            result = await biomechanics_service.create_musculoskeletal_model(
                motion_data=sample_motion_data,
                anthropometric_data={"height": 1.75, "mass": 70},
                muscle_activation_data=None
            )
            
            assert result.anthropometrics["height_m"] == 1.75
            assert result.muscle_forces["gastrocnemius"]["peak_force_N"] > 1000
            assert result.joint_moments["ankle_plantarflexor_moment_Nm"] > 100
            assert result.joint_powers["ankle_power_W"] > 0  # Power generation
            mock_model.assert_called_once()

    @pytest.mark.asyncio
    async def test_movement_pattern_recognition(self, biomechanics_service, sample_motion_data):
        """Test reconocimiento de patrones de movimiento"""
        with patch.object(biomechanics_service, '_recognize_movement_patterns') as mock_pattern:
            mock_pattern.return_value = [
                MovementPattern(
                    pattern_name="heel_strike",
                    start_frame=0,
                    end_frame=25,
                    confidence=0.95,
                    characteristics={
                        "ankle_angle_degrees": -5,
                        "knee_angle_degrees": 5,
                        "vertical_force_N": 750
                    }
                ),
                MovementPattern(
                    pattern_name="toe_off",
                    start_frame=350,
                    end_frame=375,
                    confidence=0.92,
                    characteristics={
                        "ankle_angle_degrees": -25,
                        "knee_angle_degrees": 45,
                        "vertical_force_N": 200
                    }
                )
            ]
            
            patterns = await biomechanics_service.recognize_movement_patterns(
                motion_data=sample_motion_data,
                activity="walking"
            )
            
            assert len(patterns) == 2
            assert patterns[0].pattern_name == "heel_strike"
            assert patterns[0].confidence > 0.9
            assert patterns[1].pattern_name == "toe_off"
            mock_pattern.assert_called_once()

    @pytest.mark.asyncio
    async def test_injury_risk_assessment(self, biomechanics_service, sample_motion_data, sample_force_plate_data):
        """Test evaluación de riesgo de lesiones"""
        with patch.object(biomechanics_service, '_assess_injury_risk') as mock_risk:
            mock_risk.return_value = {
                "overall_risk_score": 0.35,
                "risk_factors": {
                    "high_loading_rate": {
                        "risk_level": "moderate",
                        "value": 4250,
                        "threshold": 4000,
                        "associated_injuries": ["stress_fracture", "shin_splints"]
                    },
                    "asymmetry_index": {
                        "risk_level": "low", 
                        "value": 3.2,
                        "threshold": 10.0,
                        "associated_injuries": ["compensatory_injuries"]
                    },
                    "joint_stiffness": {
                        "risk_level": "low",
                        "ankle_stiffness": 0.12,
                        "knee_stiffness": 0.08,
                        "associated_injuries": ["overuse_injuries"]
                    }
                },
                "recommendations": [
                    "Gradual loading progression",
                    "Strengthening exercises for weak muscle groups", 
                    "Gait retraining to reduce loading rate"
                ]
            }
            
            risk_assessment = await biomechanics_service.assess_injury_risk(
                motion_data=sample_motion_data,
                force_data=sample_force_plate_data,
                athlete_profile={"sport": "running", "experience_years": 3}
            )
            
            assert 0.0 <= risk_assessment["overall_risk_score"] <= 1.0
            assert "high_loading_rate" in risk_assessment["risk_factors"]
            assert len(risk_assessment["recommendations"]) > 0
            mock_risk.assert_called_once()

    @pytest.mark.asyncio
    async def test_performance_optimization(self, biomechanics_service, sample_motion_data):
        """Test optimización del rendimiento"""
        with patch.object(biomechanics_service, '_analyze_performance_metrics') as mock_performance:
            mock_performance.return_value = {
                "efficiency_metrics": {
                    "metabolic_cost_index": 0.85,
                    "mechanical_efficiency": 0.78,
                    "energy_return_ratio": 0.65
                },
                "technique_analysis": {
                    "stride_optimization": "increase_cadence_by_5_percent",
                    "ground_contact_time": "reduce_by_10ms",
                    "vertical_oscillation": "reduce_by_2cm"
                },
                "strength_requirements": {
                    "hip_extensors": "adequate",
                    "calf_muscles": "needs_improvement",
                    "core_stability": "adequate"
                },
                "training_recommendations": [
                    "Plyometric exercises for calf muscle power",
                    "Cadence drills at 180 steps/min",
                    "Forward lean technique practice"
                ]
            }
            
            optimization = await biomechanics_service.optimize_performance(
                motion_data=sample_motion_data,
                performance_goals=["speed", "efficiency", "injury_prevention"]
            )
            
            assert optimization["efficiency_metrics"]["mechanical_efficiency"] > 0.5
            assert "stride_optimization" in optimization["technique_analysis"]
            assert len(optimization["training_recommendations"]) > 0
            mock_performance.assert_called_once()

    @pytest.mark.asyncio
    async def test_comparative_analysis(self, biomechanics_service):
        """Test análisis comparativo"""
        # Datos de referencia (normales)
        reference_data = {
            "stride_length": 1.45,
            "cadence": 110,
            "stance_phase": 60,
            "peak_vertical_force": 1.2
        }
        
        # Datos del paciente
        patient_data = {
            "stride_length": 1.28,
            "cadence": 95,
            "stance_phase": 68,
            "peak_vertical_force": 1.1
        }
        
        with patch.object(biomechanics_service, '_compare_with_reference') as mock_compare:
            mock_compare.return_value = {
                "deviations": {
                    "stride_length": {"difference": -0.17, "percent_difference": -11.7, "significance": "moderate"},
                    "cadence": {"difference": -15, "percent_difference": -13.6, "significance": "high"},
                    "stance_phase": {"difference": 8, "percent_difference": 13.3, "significance": "moderate"},
                    "peak_vertical_force": {"difference": -0.1, "percent_difference": -8.3, "significance": "low"}
                },
                "overall_similarity_score": 0.72,
                "clinical_interpretation": [
                    "Reduced cadence suggests potential mobility limitations",
                    "Increased stance phase indicates cautious gait pattern",
                    "Overall gait pattern shows compensatory strategies"
                ]
            }
            
            comparison = await biomechanics_service.compare_with_reference(
                patient_data=patient_data,
                reference_data=reference_data,
                comparison_type="healthy_adult_population"
            )
            
            assert comparison["overall_similarity_score"] < 1.0
            assert "cadence" in comparison["deviations"]
            assert comparison["deviations"]["cadence"]["significance"] == "high"
            assert len(comparison["clinical_interpretation"]) > 0
            mock_compare.assert_called_once()

    def test_data_filtering_and_preprocessing(self, biomechanics_service, sample_motion_data):
        """Test filtrado y preprocesamiento de datos"""
        # Test filtro pasa-bajas
        filtered_data = biomechanics_service.apply_lowpass_filter(
            data=sample_motion_data.markers["left_ankle"],
            cutoff_frequency=6,
            sampling_rate=120
        )
        
        assert filtered_data.shape == sample_motion_data.markers["left_ankle"].shape
        
        # Test detección de gaps
        gaps = biomechanics_service.detect_data_gaps(
            data=sample_motion_data.markers,
            threshold=0.1
        )
        
        assert isinstance(gaps, dict)
        
        # Test interpolación
        interpolated_data = biomechanics_service.interpolate_missing_data(
            data=sample_motion_data.markers["right_knee"],
            method="cubic_spline"
        )
        
        assert interpolated_data.shape == sample_motion_data.markers["right_knee"].shape

    @pytest.mark.asyncio
    async def test_real_time_analysis_capability(self, biomechanics_service):
        """Test capacidad de análisis en tiempo real"""
        # Simular stream de datos en tiempo real
        real_time_frames = [
            {"markers": {"ankle": np.random.rand(3)}, "timestamp": i}
            for i in range(10)
        ]
        
        with patch.object(biomechanics_service, '_process_real_time_frame') as mock_rt:
            mock_rt.return_value = {
                "frame_id": 0,
                "ankle_angle": 15.5,
                "ground_contact": True,
                "gait_phase": "stance"
            }
            
            results = []
            for frame in real_time_frames:
                result = await biomechanics_service.process_real_time_frame(
                    frame_data=frame,
                    analysis_mode="gait_phase_detection"
                )
                results.append(result)
            
            assert len(results) == 10
            for result in results:
                assert "ankle_angle" in result
                assert "gait_phase" in result


if __name__ == "__main__":
    # Ejecutar tests específicos
    pytest.main([__file__, "-v", "--tb=short"])
