"""
Ejemplo de uso del BiomechanicsService
====================================

Demostración de las capacidades de análisis biomecánico.
"""

import asyncio
import numpy as np
from datetime import datetime

from app.domains.medicine.biomechanics import (
    BiomechanicsService, ActivityType, AnalysisType,
    MotionCaptureData, ForceData, AnthropometricData,
    BiomechanicsAnalysisRequest
)


async def biomechanics_demo():
    """Demostración completa del servicio de biomecánica"""
    print("🏃 DEMO: BiomechanicsService - Análisis de Movimiento Avanzado")
    print("=" * 60)
    
    # 1. Inicializar servicio
    print("1. Inicializando BiomechanicsService...")
    service = BiomechanicsService()
    await service.initialize()
    print(f"   ✅ Servicio inicializado. Actividades soportadas: {len(service.supported_activities)}")
    
    # 2. Crear datos de ejemplo
    print("\n2. Generando datos de captura de movimiento simulados...")
    
    # Simular datos de marcadores corporales durante la marcha
    n_frames = 1000  # 8.33 segundos a 120 Hz
    time_vector = np.linspace(0, n_frames/120, n_frames)
    
    # Generar movimiento periódico simulando marcha
    markers = {}
    for marker in ["head", "left_shoulder", "right_shoulder", "pelvis", 
                   "left_hip", "right_hip", "left_knee", "right_knee",
                   "left_ankle", "right_ankle"]:
        # Movimiento base + componente cíclico de marcha
        base_x = np.ones(n_frames) * np.random.uniform(-0.1, 0.1)
        base_y = time_vector * 1.3  # Velocidad de marcha ~1.3 m/s
        base_z = np.ones(n_frames) * np.random.uniform(0.8, 1.8)  # Altura del marcador
        
        # Agregar componente cíclico (pasos)
        step_frequency = 1.8  # Hz (cadencia ~108 pasos/min)
        if "ankle" in marker:
            # Los tobillos tienen mayor oscilación vertical
            base_z += 0.1 * np.sin(2 * np.pi * step_frequency * time_vector)
        
        markers[marker] = np.column_stack([base_x, base_y, base_z])
    
    motion_data = MotionCaptureData(
        timestamp=datetime.now(),
        markers=markers,
        sampling_rate=120,
        subject_id="DEMO_SUBJECT_001",
        activity=ActivityType.WALKING
    )
    
    print(f"   ✅ Datos de movimiento creados: {len(markers)} marcadores, {n_frames} frames")
    
    # 3. Crear datos de placa de fuerza
    print("\n3. Generando datos de placa de fuerza simulados...")
    
    n_force_frames = 2000  # 8.33 segundos a 240 Hz
    
    # Simular fuerzas de reacción del suelo durante la marcha
    body_weight = 70 * 9.81  # 70 kg sujeto
    
    # Fuerza vertical (Fz) - patrón típico de marcha
    fz_pattern = np.zeros(n_force_frames)
    for i in range(4):  # 4 pasos en 8.33 segundos
        start_idx = i * n_force_frames // 4
        end_idx = (i + 1) * n_force_frames // 4
        
        # Patrón de doble pico típico de la marcha
        step_time = np.linspace(0, 1, end_idx - start_idx)
        fz_step = body_weight * (1.2 * np.exp(-((step_time - 0.2) / 0.1)**2) +
                               0.8 * np.exp(-((step_time - 0.8) / 0.15)**2))
        fz_pattern[start_idx:end_idx] = fz_step
    
    force_data = ForceData(
        force_vectors={
            "Fx": np.random.normal(0, 50, n_force_frames),  # Fuerza lateral
            "Fy": np.random.normal(0, 80, n_force_frames),  # Fuerza anteroposterior
            "Fz": fz_pattern  # Fuerza vertical
        },
        moments={
            "Mx": np.random.normal(0, 20, n_force_frames),
            "My": np.random.normal(0, 25, n_force_frames),
            "Mz": np.random.normal(0, 15, n_force_frames)
        },
        center_of_pressure={
            "CoPx": np.random.normal(0, 0.05, n_force_frames),
            "CoPy": np.random.normal(0, 0.08, n_force_frames)
        },
        sampling_rate=240,
        subject_mass_kg=70
    )
    
    print(f"   ✅ Datos de fuerza creados: {n_force_frames} frames a 240 Hz")
    
    # 4. Datos antropométricos
    print("\n4. Definiendo perfil antropométrico...")
    
    anthropometric_data = AnthropometricData(
        subject_id="DEMO_SUBJECT_001",
        height_m=1.75,
        mass_kg=70,
        gender="male",
        age_years=28,
        leg_length_m=0.92,
        thigh_length_m=0.45,
        shank_length_m=0.43
    )
    
    print(f"   ✅ Sujeto: {anthropometric_data.gender}, {anthropometric_data.age_years} años, "
          f"{anthropometric_data.height_m}m, {anthropometric_data.mass_kg}kg")
    
    # 5. Análisis de marcha
    print("\n5. 🚶 Realizando análisis de marcha...")
    
    gait_request = BiomechanicsAnalysisRequest(
        subject_id="DEMO_SUBJECT_001",
        analysis_type=AnalysisType.GAIT_ANALYSIS,
        motion_data=motion_data,
        force_data=force_data,
        anthropometric_data=anthropometric_data,
        filtering_enabled=True,
        cutoff_frequency=6.0
    )
    
    gait_result = await service.analyze_comprehensive(gait_request)
    
    if gait_result.gait_analysis:
        print("   📊 Resultados del análisis:")
        print(f"      • Análisis ID: {gait_result.analysis_id}")
        print(f"      • Timestamp: {gait_result.timestamp}")
        print(f"      • Tipo: {gait_result.analysis_type}")
        
        if gait_result.gait_analysis:
            ga = gait_result.gait_analysis
            print(f"      • Número de pasos: {ga.step_count}")
            print(f"      • Duración del ciclo: {ga.cycle_duration:.2f}s")
            if ga.temporal_parameters:
                print("      • Parámetros temporales disponibles")
            if ga.spatial_parameters:
                print("      • Parámetros espaciales disponibles")
        
        if gait_result.quality_score:
            print(f"   🎯 Puntuación de calidad: {gait_result.quality_score:.1f}/100")
        
        if gait_result.recommendations:
            print("   💡 Principales recomendaciones:")
    
    print(f"   ⏱️  Tiempo de procesamiento: {gait_result.processing_time_seconds:.3f} segundos")
    
    # 6. Análisis de cinemática articular
    print("\n6. 🦴 Realizando análisis de cinemática articular...")
    
    kinematics_request = BiomechanicsAnalysisRequest(
        subject_id="DEMO_SUBJECT_001",
        analysis_type=AnalysisType.JOINT_KINEMATICS,
        motion_data=motion_data,
        anthropometric_data=anthropometric_data
    )
    
    kinematics_result = await service.analyze_comprehensive(kinematics_request)
    
    if kinematics_result.joint_kinematics:
        print(f"   📊 Cinemática articular analizada para {len(kinematics_result.joint_kinematics)} articulaciones:")
        for joint_name, kinematics in kinematics_result.joint_kinematics.items():
            rom = kinematics.range_of_motion
            print(f"      • {joint_name.capitalize()}: RDM = {rom.get('flexion_extension', 0):.1f}°")
    
    # 7. Análisis de fuerzas
    print("\n7. ⚡ Realizando análisis de fuerzas...")
    
    force_request = BiomechanicsAnalysisRequest(
        subject_id="DEMO_SUBJECT_001",
        analysis_type=AnalysisType.FORCE_ANALYSIS,
        force_data=force_data,
        anthropometric_data=anthropometric_data,
        normalize_to_body_weight=True
    )
    
    force_result = await service.analyze_comprehensive(force_request)
    
    if force_result.force_analysis:
        fa = force_result.force_analysis
        print(f"   📊 Análisis de fuerzas:")
        print(f"      • Fuerza vertical máxima: {fa.peak_forces.get('vertical_force_bw', 0):.2f} BW")
        print(f"      • Tasa de carga: {fa.loading_rates.get('vertical_loading_rate_N_per_s', 0):.0f} N/s")
        print(f"      • Impulso vertical: {fa.impulse_parameters.get('vertical_impulse_Ns', 0):.1f} N⋅s")
    
    # 8. Evaluación de riesgo de lesiones
    print("\n8. ⚠️ Realizando evaluación de riesgo de lesiones...")
    
    risk_request = BiomechanicsAnalysisRequest(
        subject_id="DEMO_SUBJECT_001",
        analysis_type=AnalysisType.INJURY_RISK,
        motion_data=motion_data,
        force_data=force_data,
        anthropometric_data=anthropometric_data
    )
    
    risk_result = await service.analyze_comprehensive(risk_request)
    
    if risk_result.injury_risk:
        ir = risk_result.injury_risk
        risk_level = "BAJO" if ir.overall_risk_score < 0.3 else "MODERADO" if ir.overall_risk_score < 0.7 else "ALTO"
        print(f"   📊 Evaluación de riesgo:")
        print(f"      • Puntuación general: {ir.overall_risk_score:.2f} ({risk_level})")
        print(f"      • Factores de riesgo identificados: {len(ir.risk_factors)}")
        print(f"      • Recomendaciones: {len(ir.recommendations)}")
        
        if ir.recommendations:
            print("   💡 Principales recomendaciones:")
            for i, rec in enumerate(ir.recommendations[:3], 1):
                print(f"      {i}. {rec}")
    
    # 9. Análisis en tiempo real
    print("\n9. ⏱️ Demostrando capacidades de tiempo real...")
    
    # Simular procesamiento frame por frame
    frames_to_process = 5
    print(f"   Procesando {frames_to_process} frames en tiempo real...")
    
    for i in range(frames_to_process):
        frame_data = {
            "timestamp": i,
            "markers": {
                "ankle": np.random.rand(3)
            }
        }
        
        rt_result = await service.process_real_time_frame(
            frame_data, 
            analysis_mode="gait_phase_detection"
        )
        
        print(f"      Frame {i}: Fase = {rt_result.get('gait_phase', 'unknown')}, "
              f"Contacto = {rt_result.get('ground_contact', False)}")
    
    # 10. Resumen final
    print("\n" + "="*60)
    print("🎉 DEMO COMPLETADO - BiomechanicsService")
    print("✅ Análisis de marcha realizado")
    print("✅ Cinemática articular calculada") 
    print("✅ Fuerzas analizadas")
    print("✅ Riesgo de lesiones evaluado")
    print("✅ Procesamiento en tiempo real demostrado")
    print("\n🔬 El BiomechanicsService está listo para análisis biomecánico profesional!")


if __name__ == "__main__":
    asyncio.run(biomechanics_demo())
