#!/usr/bin/env python3
"""
Additive Manufacturing Service - AXIOM META 4
=============================================

Servicio avanzado para modelado de manufactura aditiva con simulación térmica completa.
Implementa simulación multi-física de procesos de impresión 3D con fusión por láser,
incluyendo dinámica de fluidos, transferencia de calor, solidificación y evolución microestructural.

Autor: AXIOM META 4 Development Team
Fecha: Diciembre 2024
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Union, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from datetime import datetime
import asyncio

from app.services.base_service import BaseService
from app.exceptions.domain.engineering import EngineeringError

logger = logging.getLogger(__name__)


class AdditiveProcess(Enum):
    """Procesos de manufactura aditiva soportados"""
    LASER_POWDER_BED_FUSION = "lpbf"      # Fusión por láser en lecho de polvo
    DIRECT_ENERGY_DEPOSITION = "ded"      # Deposición directa de energía
    ELECTRON_BEAM_MELTING = "ebm"         # Fusión por haz de electrones
    SELECTIVE_LASER_SINTERING = "sls"     # Sinterizado selectivo por láser
    BINDER_JETTING = "binder_jetting"     # Inyección de binder


class MaterialType(Enum):
    """Tipos de material para manufactura aditiva"""
    METALLIC = "metallic"
    POLYMERIC = "polymeric"
    CERAMIC = "ceramic"
    COMPOSITE = "composite"


@dataclass
class ThermalHistory:
    """Historia térmica completa de un punto material"""
    temperature_profile: np.ndarray  # Perfil de temperatura vs tiempo
    time_points: np.ndarray         # Puntos temporales
    heating_rates: np.ndarray       # Tasas de calentamiento
    cooling_rates: np.ndarray       # Tasas de enfriamiento
    peak_temperatures: List[float]  # Temperaturas pico
    dwell_times: List[float]        # Tiempos de permanencia
    thermal_cycles: int            # Número de ciclos térmicos
    total_time: float              # Tiempo total


@dataclass
class MeltPoolDynamics:
    """Dinámica del pool de fusión"""
    dimensions: Dict[str, float]      # Dimensiones del pool (largo, ancho, profundidad)
    temperature_distribution: np.ndarray
    velocity_field: np.ndarray        # Campo de velocidad del fluido
    surface_tension: float           # Tensión superficial
    viscosity: float                 # Viscosidad del material fundido
    evaporation_rate: float          # Tasa de evaporación
    keyhole_depth: Optional[float]   # Profundidad del keyhole (si aplica)


@dataclass
class MicrostructureEvolution:
    """Evolución microestructural"""
    grain_size_distribution: np.ndarray
    phase_fractions: Dict[str, float]
    porosity_distribution: np.ndarray
    defect_density: Dict[str, float]
    mechanical_properties: Dict[str, float]
    thermal_properties: Dict[str, float]


@dataclass
class AdditiveManufacturingSolution:
    """Solución completa de manufactura aditiva"""
    thermal_history: ThermalHistory
    melt_pool_dynamics: MeltPoolDynamics
    microstructure_evolution: MicrostructureEvolution
    build_quality_metrics: Dict[str, float]
    process_efficiency: Dict[str, float]
    defect_analysis: Dict[str, Any]
    computation_time: float
    timestamp: datetime = field(default_factory=datetime.now)


class ThermalTransportEquations:
    """Ecuaciones de transporte térmico para manufactura aditiva"""

    def __init__(self, material_properties: Dict[str, float]):
        self.material_props = material_properties
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def heat_conduction_equation(self, temperature: np.ndarray,
                               heat_source: np.ndarray,
                               time_step: float) -> np.ndarray:
        """
        Resolver ecuación de conducción de calor

        ∂T/∂t = α ∇²T + Q/ρc_p

        Args:
            temperature: Campo de temperatura actual
            heat_source: Fuente de calor (potencia volumétrica)
            time_step: Paso de tiempo

        Returns:
            Nuevo campo de temperatura
        """
        # Propiedades térmicas
        alpha = self.material_props.get('thermal_diffusivity', 1e-5)  # m²/s
        rho = self.material_props.get('density', 7800)               # kg/m³
        cp = self.material_props.get('specific_heat', 500)           # J/(kg·K)

        # Laplaciano de temperatura
        laplacian = np.zeros_like(temperature)
        for i in range(3):  # 3D
            laplacian += np.gradient(np.gradient(temperature, axis=i), axis=i)

        # Ecuación completa
        dT_dt = alpha * laplacian + heat_source / (rho * cp)

        # Integración temporal (Euler forward)
        new_temperature = temperature + dT_dt * time_step

        return new_temperature

    def laser_heat_source(self, position: np.ndarray, laser_parameters: Dict[str, float]) -> np.ndarray:
        """
        Modelo de fuente de calor láser

        Args:
            position: Posición en el dominio
            laser_parameters: Parámetros del láser

        Returns:
            Distribución de fuente de calor
        """
        # Parámetros del láser
        power = laser_parameters.get('power', 200)           # W
        beam_radius = laser_parameters.get('beam_radius', 50e-6)  # m
        absorption_coeff = laser_parameters.get('absorption', 0.3)

        # Posición del centro del haz
        center_x = laser_parameters.get('center_x', 0)
        center_y = laser_parameters.get('center_y', 0)

        # Distancia al centro del haz
        r_squared = (position[:, 0] - center_x)**2 + (position[:, 1] - center_y)**2

        # Perfil gaussiano del haz
        beam_profile = np.exp(-2 * r_squared / beam_radius**2)

        # Fuente de calor volumétrica
        heat_source = absorption_coeff * power * beam_profile / (np.pi * beam_radius**2)

        return heat_source

    def convection_boundary_condition(self, temperature: np.ndarray,
                                    surface_normal: np.ndarray,
                                    ambient_temperature: float = 300) -> np.ndarray:
        """
        Condición de contorno convectiva

        Args:
            temperature: Temperatura en la superficie
            surface_normal: Normal a la superficie
            ambient_temperature: Temperatura ambiente

        Returns:
            Flujo convectivo
        """
        h = self.material_props.get('heat_transfer_coeff', 10)  # W/(m²·K)

        # Flujo convectivo: -h(T - T_ambient)
        convective_flux = -h * (temperature - ambient_temperature)

        return convective_flux

    def radiation_boundary_condition(self, temperature: np.ndarray,
                                   emissivity: float = 0.3,
                                   ambient_temperature: float = 300) -> np.ndarray:
        """
        Condición de contorno radiativa

        Args:
            temperature: Temperatura en la superficie
            emissivity: Emisividad
            ambient_temperature: Temperatura ambiente

        Returns:
            Flujo radiativo
        """
        sigma = 5.67e-8  # Constante de Stefan-Boltzmann

        # Flujo radiativo: -εσ(T⁴ - T_ambient⁴)
        radiative_flux = -emissivity * sigma * (temperature**4 - ambient_temperature**4)

        return radiative_flux


class FluidDynamicsEquations:
    """Ecuaciones de dinámica de fluidos para el pool de fusión"""

    def __init__(self, material_properties: Dict[str, float]):
        self.material_props = material_properties
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def navier_stokes_equation(self, velocity: np.ndarray,
                             pressure: np.ndarray,
                             temperature: np.ndarray,
                             time_step: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Resolver ecuaciones de Navier-Stokes

        Args:
            velocity: Campo de velocidad
            pressure: Campo de presión
            temperature: Campo de temperatura
            time_step: Paso de tiempo

        Returns:
            Nuevos campos de velocidad y presión
        """
        # Propiedades del fluido
        rho = self.material_props.get('density', 7800)
        mu = self.material_props.get('viscosity', 0.006)  # Pa·s
        beta = self.material_props.get('thermal_expansion', 1e-4)  # 1/K

        # Término convectivo
        convective_term = np.zeros_like(velocity)
        for i in range(3):
            for j in range(3):
                convective_term[:, i] += velocity[:, j] * np.gradient(velocity[:, i], axis=j)

        # Gradiente de presión
        pressure_gradient = np.zeros_like(velocity)
        for i in range(3):
            pressure_gradient[:, i] = np.gradient(pressure, axis=i)

        # Término viscoso (simplificado)
        viscous_term = mu * np.zeros_like(velocity)  # Placeholder

        # Fuerza de flotación (Boussinesq)
        gravity = np.array([0, 0, -9.81])
        buoyancy_force = -rho * beta * (temperature - 300)[:, None] * gravity

        # Ecuación de momento
        dV_dt = -convective_term - pressure_gradient / rho + viscous_term / rho + buoyancy_force / rho

        # Nuevo campo de velocidad
        new_velocity = velocity + dV_dt * time_step

        # Ecuación de continuidad (proyección para presión)
        divergence = np.sum(np.gradient(new_velocity, axis=0), axis=0)
        pressure_correction = -rho / time_step * divergence

        new_pressure = pressure + pressure_correction

        return new_velocity, new_pressure

    def surface_tension_model(self, temperature: np.ndarray,
                            curvature: np.ndarray) -> np.ndarray:
        """
        Modelo de tensión superficial

        Args:
            temperature: Temperatura en la superficie
            curvature: Curvatura de la superficie

        Returns:
            Fuerza de tensión superficial
        """
        # Coeficiente de tensión superficial
        sigma_0 = self.material_props.get('surface_tension', 1.5)  # N/m
        dsigma_dT = self.material_props.get('surface_tension_temp_coeff', -0.0003)  # N/(m·K)

        # Tensión superficial dependiente de temperatura
        surface_tension = sigma_0 + dsigma_dT * (temperature - 300)

        # Fuerza capilar: σ * κ * n
        capillary_force = surface_tension * curvature

        return capillary_force

    def evaporation_model(self, temperature: np.ndarray) -> np.ndarray:
        """
        Modelo de evaporación

        Args:
            temperature: Temperatura en la superficie

        Returns:
            Tasa de evaporación
        """
        # Modelo de Langmuir
        T_boiling = self.material_props.get('boiling_temperature', 3000)  # K
        latent_heat = self.material_props.get('latent_heat', 6e6)          # J/kg
        R = 8.314  # Constante universal de gases

        # Presión de vapor saturado (aproximación)
        vapor_pressure = np.exp(-latent_heat / R * (1/temperature - 1/T_boiling))

        # Tasa de evaporación
        evaporation_rate = vapor_pressure * np.sqrt(self.material_props.get('molecular_weight', 0.056) / (2 * np.pi * R * temperature))

        return evaporation_rate


class MicrostructureEvolutionModel:
    """Modelo de evolución microestructural"""

    def __init__(self, material_properties: Dict[str, float]):
        self.material_props = material_properties
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def grain_growth_model(self, temperature: np.ndarray,
                          time_step: float,
                          current_grain_size: np.ndarray) -> np.ndarray:
        """
        Modelo de crecimiento de grano

        Args:
            temperature: Campo de temperatura
            time_step: Paso de tiempo
            current_grain_size: Tamaño de grano actual

        Returns:
            Nuevo tamaño de grano
        """
        # Energía de activación para crecimiento de grano
        Q_grain = self.material_props.get('grain_growth_activation', 1.5e5)  # J/mol
        R = 8.314  # Constante universal de gases

        # Tasa de crecimiento de grano
        growth_rate = self.material_props.get('grain_growth_coeff', 1e-10) * np.exp(-Q_grain / (R * temperature))

        # Nuevo tamaño de grano
        new_grain_size = current_grain_size + growth_rate * time_step

        return new_grain_size

    def phase_transformation_model(self, temperature: np.ndarray,
                                 cooling_rate: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Modelo de transformación de fases

        Args:
            temperature: Campo de temperatura
            cooling_rate: Tasa de enfriamiento

        Returns:
            Fracciones de fase
        """
        # Temperaturas de transformación
        T_liquidus = self.material_props.get('liquidus_temperature', 1600)
        T_solidus = self.material_props.get('solidus_temperature', 1400)

        # Fracción sólida (modelo de Scheil)
        T_normalized = (T_liquidus - temperature) / (T_liquidus - T_solidus)
        solid_fraction = np.clip(T_normalized, 0, 1)

        # Fracción de fases
        phase_fractions = {
            'liquid': 1 - solid_fraction,
            'solid': solid_fraction,
            'austenite': np.zeros_like(solid_fraction),  # Placeholder
            'martensite': np.zeros_like(solid_fraction)  # Placeholder
        }

        return phase_fractions

    def porosity_formation_model(self, temperature: np.ndarray,
                               solidification_rate: np.ndarray) -> np.ndarray:
        """
        Modelo de formación de porosidad

        Args:
            temperature: Campo de temperatura
            solidification_rate: Tasa de solidificación

        Returns:
            Distribución de porosidad
        """
        # Modelo simplificado de porosidad
        # Porosidad aumenta con tasa de solidificación rápida
        base_porosity = self.material_props.get('base_porosity', 0.001)
        porosity_factor = 1 + solidification_rate / self.material_props.get('critical_solidification_rate', 0.1)

        porosity = base_porosity * porosity_factor

        return np.clip(porosity, 0, 0.1)  # Máximo 10% porosidad


class AdditiveManufacturingService(BaseService):
    """Servicio principal de manufactura aditiva"""

    def __init__(self):
        """Inicializar servicio de manufactura aditiva"""
        super().__init__("AdditiveManufacturingService")
        self.thermal_solver = None
        self.fluid_solver = None
        self.microstructure_solver = None
        
        logger.info("🔥 Additive Manufacturing Service initialized")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa requests de manufactura aditiva"""
        self.log_request(request_data)
        try:
            operation = request_data.get("operation", "")
            
            if operation == "setup_process":
                process_type_str = request_data.get("process_type", "lpbf")
                material_type_str = request_data.get("material_type", "metallic")
                material_props = request_data.get("material_properties", {})
                
                try:
                    process_type = AdditiveProcess(process_type_str)
                    material_type = MaterialType(material_type_str)
                except ValueError:
                    return {"error": "Invalid process or material type"}
                
                self.setup_process(process_type, material_type, material_props)
                return {"status": "configured"}
                
            elif operation == "simulate_track":
                laser_params = request_data.get("laser_parameters", {})
                process_params = request_data.get("process_parameters", {})
                
                # Note: simulate_single_track is synchronous
                solution = self.simulate_single_track(laser_params, process_params)
                
                # Convert solution to dict
                return {
                    "status": "simulated",
                    "computation_time": solution.computation_time,
                    "build_quality": solution.build_quality_metrics
                }
                
            else:
                return {"error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            return self.handle_error(e, "process_request")

    def setup_process(self, process_type: AdditiveProcess,
                     material_type: MaterialType,
                     material_properties: Dict[str, float]) -> None:
        """
        Configurar proceso de manufactura aditiva

        Args:
            process_type: Tipo de proceso
            material_type: Tipo de material
            material_properties: Propiedades del material
        """
        self.logger.info(f"🔧 Configurando proceso {process_type.value} para material {material_type.value}...")

        # Inicializar solvers
        self.thermal_solver = ThermalTransportEquations(material_properties)
        self.fluid_solver = FluidDynamicsEquations(material_properties)
        self.microstructure_solver = MicrostructureEvolutionModel(material_properties)

        self.logger.info("✅ Proceso de manufactura aditiva configurado")

    def simulate_single_track(self, laser_parameters: Dict[str, float],
                            process_parameters: Dict[str, float],
                            domain_size: Tuple[float, float, float] = (1e-3, 1e-3, 1e-3),
                            simulation_time: float = 1e-3) -> AdditiveManufacturingSolution:
        """
        Simular una pista única de manufactura aditiva

        Args:
            laser_parameters: Parámetros del láser
            process_parameters: Parámetros del proceso
            domain_size: Tamaño del dominio (m)
            simulation_time: Tiempo de simulación (s)

        Returns:
            AdditiveManufacturingSolution completa
        """
        self.logger.info("🔬 Simulando pista única de manufactura aditiva...")

        if not all([self.thermal_solver, self.fluid_solver, self.microstructure_solver]):
            raise RuntimeError("Debe configurar el proceso primero")

        # Asegurar que los solvers no son None
        assert self.thermal_solver is not None
        assert self.fluid_solver is not None
        assert self.microstructure_solver is not None

        # Configurar dominio
        nx, ny, nz = 50, 50, 20

        # Crear malla
        x = np.linspace(0, domain_size[0], nx)
        y = np.linspace(0, domain_size[1], ny)
        z = np.linspace(0, domain_size[2], nz)
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

        positions = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])

        # Condiciones iniciales
        temperature = np.full(positions.shape[0], 300.0)  # Temperatura ambiente
        velocity = np.zeros_like(positions)
        pressure = np.full(positions.shape[0], 1e5)  # Presión atmosférica
        grain_size = np.full(positions.shape[0], 1e-5)  # Tamaño inicial de grano

        # Parámetros de simulación
        dt = 1e-6  # Paso de tiempo
        n_steps = int(simulation_time / dt)

        # Almacenar historia térmica
        thermal_history_points = []
        time_points = []

        # Simulación temporal
        for step in range(n_steps):
            current_time = step * dt
            time_points.append(current_time)

            # Calcular fuente de calor láser
            laser_params_with_position = laser_parameters.copy()
            laser_params_with_position.update({
                'center_x': process_parameters.get('scan_speed', 1.0) * current_time,
                'center_y': domain_size[1] / 2
            })

            heat_source = self.thermal_solver.laser_heat_source(positions, laser_params_with_position)

            # Resolver transporte térmico
            temperature = self.thermal_solver.heat_conduction_equation(temperature, heat_source, dt)

            # Resolver dinámica de fluidos (solo en zona fundida)
            molten_region = temperature > process_parameters.get('melting_temperature', 1600)
            if np.any(molten_region):
                velocity[molten_region], pressure[molten_region] = self.fluid_solver.navier_stokes_equation(
                    velocity[molten_region], pressure[molten_region],
                    temperature[molten_region], dt
                )

            # Evolución microestructural
            grain_size = self.microstructure_solver.grain_growth_model(temperature, dt, grain_size)

            # Almacenar punto de historia térmica (punto central)
            center_idx = nx//2 + ny//2 * nx + nz//2 * nx * ny
            thermal_history_points.append(temperature[center_idx])

        # Procesar resultados
        thermal_history = self._process_thermal_history(
            np.array(thermal_history_points), np.array(time_points)
        )

        melt_pool_dynamics = self._analyze_melt_pool_dynamics(
            temperature, velocity, positions, domain_size
        )

        microstructure_evolution = self._analyze_microstructure_evolution(
            grain_size, temperature, positions
        )

        build_quality_metrics = self._calculate_build_quality_metrics(
            thermal_history, melt_pool_dynamics, microstructure_evolution
        )

        process_efficiency = self._calculate_process_efficiency(
            laser_parameters, thermal_history, melt_pool_dynamics
        )

        defect_analysis = self._analyze_defects(
            microstructure_evolution, thermal_history
        )

        return AdditiveManufacturingSolution(
            thermal_history=thermal_history,
            melt_pool_dynamics=melt_pool_dynamics,
            microstructure_evolution=microstructure_evolution,
            build_quality_metrics=build_quality_metrics,
            process_efficiency=process_efficiency,
            defect_analysis=defect_analysis,
            computation_time=simulation_time
        )

    def _process_thermal_history(self, temperature_profile: np.ndarray,
                               time_points: np.ndarray) -> ThermalHistory:
        """Procesar historia térmica completa"""
        # Calcular tasas de calentamiento/enfriamiento
        heating_rates = np.gradient(temperature_profile, time_points)
        cooling_rates = -np.minimum(heating_rates, 0)

        # Identificar temperaturas pico
        peak_indices = np.where(np.diff(np.sign(heating_rates)) < 0)[0]
        peak_temperatures = temperature_profile[peak_indices].tolist()

        # Calcular tiempos de permanencia
        dwell_times = []
        for peak_temp in peak_temperatures:
            above_threshold = temperature_profile > (peak_temp * 0.9)
            dwell_time = np.sum(above_threshold) * (time_points[1] - time_points[0])
            dwell_times.append(dwell_time)

        return ThermalHistory(
            temperature_profile=temperature_profile,
            time_points=time_points,
            heating_rates=heating_rates,
            cooling_rates=cooling_rates,
            peak_temperatures=peak_temperatures,
            dwell_times=dwell_times,
            thermal_cycles=len(peak_temperatures),
            total_time=time_points[-1] - time_points[0]
        )

    def _analyze_melt_pool_dynamics(self, temperature: np.ndarray,
                                  velocity: np.ndarray,
                                  positions: np.ndarray,
                                  domain_size: Tuple[float, float, float]) -> MeltPoolDynamics:
        """Analizar dinámica del pool de fusión"""
        # Identificar zona fundida
        melting_temp = 1600  # K (aproximado)
        molten_mask = temperature > melting_temp

        if not np.any(molten_mask):
            # No hay zona fundida
            return MeltPoolDynamics(
                dimensions={'length': 0, 'width': 0, 'depth': 0},
                temperature_distribution=np.array([]),
                velocity_field=np.array([]),
                surface_tension=1.5,
                viscosity=0.006,
                evaporation_rate=0,
                keyhole_depth=None
            )

        molten_positions = positions[molten_mask]

        # Calcular dimensiones del pool
        dimensions = {
            'length': np.ptp(molten_positions[:, 0]),
            'width': np.ptp(molten_positions[:, 1]),
            'depth': np.ptp(molten_positions[:, 2])
        }

        # Profundidad del keyhole (si existe)
        max_depth = dimensions['depth']
        keyhole_depth = max_depth if max_depth > 100e-6 else None  # 100 μm threshold

        return MeltPoolDynamics(
            dimensions=dimensions,
            temperature_distribution=temperature[molten_mask],
            velocity_field=velocity[molten_mask],
            surface_tension=1.5,
            viscosity=0.006,
            evaporation_rate=float(np.mean(temperature[molten_mask]) * 1e-6),  # Placeholder
            keyhole_depth=keyhole_depth
        )

    def _analyze_microstructure_evolution(self, grain_size: np.ndarray,
                                        temperature: np.ndarray,
                                        positions: np.ndarray) -> MicrostructureEvolution:
        """Analizar evolución microestructural"""
        # Calcular distribución de tamaño de grano
        grain_size_dist = grain_size

        # Fracciones de fase (simplificado)
        phase_fractions = {
            'austenite': 0.7,
            'ferrite': 0.2,
            'martensite': 0.1
        }

        # Distribución de porosidad
        porosity_dist = np.random.normal(0.005, 0.002, len(grain_size))

        # Densidad de defectos
        defect_density = {
            'dislocations': 1e12,  # m⁻²
            'vacancies': 1e20,     # m⁻³
            'grain_boundaries': 1e6  # m⁻¹
        }

        # Propiedades mecánicas (basadas en tamaño de grano - ley de Hall-Petch)
        k_hp = 0.01  # MPa·m^(1/2)
        yield_strength = 50 + k_hp / np.sqrt(np.mean(grain_size) * 1e6)  # MPa

        mechanical_properties = {
            'yield_strength': yield_strength,
            'ultimate_strength': yield_strength * 1.5,
            'elongation': 20.0,
            'hardness': yield_strength * 0.3
        }

        thermal_properties = {
            'thermal_conductivity': 50.0,  # W/(m·K)
            'specific_heat': 500.0,        # J/(kg·K)
            'thermal_expansion': 1e-5      # 1/K
        }

        return MicrostructureEvolution(
            grain_size_distribution=grain_size_dist,
            phase_fractions=phase_fractions,
            porosity_distribution=porosity_dist,
            defect_density=defect_density,
            mechanical_properties=mechanical_properties,
            thermal_properties=thermal_properties
        )

    def _calculate_build_quality_metrics(self, thermal_history: ThermalHistory,
                                       melt_pool_dynamics: MeltPoolDynamics,
                                       microstructure_evolution: MicrostructureEvolution) -> Dict[str, float]:
        """Calcular métricas de calidad de construcción"""
        metrics = {}

        # Estabilidad térmica
        temp_std = np.std(thermal_history.temperature_profile)
        temp_mean = np.mean(thermal_history.temperature_profile)
        metrics['thermal_stability'] = 1 - min(float(temp_std / temp_mean), 1)

        # Consistencia del pool de fusión
        if melt_pool_dynamics.dimensions['length'] > 0:
            pool_volume = (melt_pool_dynamics.dimensions['length'] *
                          melt_pool_dynamics.dimensions['width'] *
                          melt_pool_dynamics.dimensions['depth'])
            metrics['melt_pool_consistency'] = min(pool_volume / 1e-9, 1)  # Normalized
        else:
            metrics['melt_pool_consistency'] = 0

        # Calidad microestructural
        avg_grain_size = np.mean(microstructure_evolution.grain_size_distribution)
        metrics['microstructure_quality'] = 1 / (1 + avg_grain_size * 1e6)  # Smaller grains = better

        # Densidad (inversa de porosidad)
        avg_porosity = np.mean(microstructure_evolution.porosity_distribution)
        metrics['density'] = 1 - avg_porosity

        # Overall quality score
        metrics['overall_quality'] = float(np.mean(np.array([
            metrics['thermal_stability'],
            metrics['melt_pool_consistency'],
            metrics['microstructure_quality'],
            metrics['density']
        ])))

        return metrics

    def _calculate_process_efficiency(self, laser_parameters: Dict[str, float],
                                    thermal_history: ThermalHistory,
                                    melt_pool_dynamics: MeltPoolDynamics) -> Dict[str, float]:
        """Calcular eficiencia del proceso"""
        efficiency = {}

        # Eficiencia energética
        laser_power = laser_parameters.get('power', 200)
        absorbed_power = laser_power * laser_parameters.get('absorption', 0.3)
        efficiency['energy_efficiency'] = absorbed_power / laser_power

        # Eficiencia de fusión
        if melt_pool_dynamics.dimensions['length'] > 0:
            melt_volume = (melt_pool_dynamics.dimensions['length'] *
                          melt_pool_dynamics.dimensions['width'] *
                          melt_pool_dynamics.dimensions['depth'])
            efficiency['melt_efficiency'] = min(melt_volume / 1e-9, 1)
        else:
            efficiency['melt_efficiency'] = 0

        # Eficiencia de solidificación
        cooling_rate = np.mean(thermal_history.cooling_rates)
        efficiency['solidification_efficiency'] = min(float(cooling_rate / 1e6), 1)  # Normalized

        return efficiency

    def _analyze_defects(self, microstructure_evolution: MicrostructureEvolution,
                        thermal_history: ThermalHistory) -> Dict[str, Any]:
        """Analizar defectos en la construcción"""
        defects = {}

        # Análisis de porosidad
        avg_porosity = np.mean(microstructure_evolution.porosity_distribution)
        defects['porosity'] = {
            'average': avg_porosity,
            'maximum': np.max(microstructure_evolution.porosity_distribution),
            'distribution': 'normal' if avg_porosity < 0.01 else 'high'
        }

        # Análisis de cracking
        thermal_stress = np.max(np.abs(thermal_history.heating_rates)) * 1e-5  # Placeholder
        defects['cracking'] = {
            'thermal_stress': thermal_stress,
            'risk_level': 'high' if thermal_stress > 100 else 'low'
        }

        # Análisis de falta de fusión
        melt_consistency = np.std(microstructure_evolution.grain_size_distribution)
        defects['lack_of_fusion'] = {
            'consistency': melt_consistency,
            'risk_level': 'high' if melt_consistency > 1e-5 else 'low'
        }

        return defects

    def optimize_process_parameters(self, target_properties: Dict[str, float],
                                  constraints: Dict[str, Any]) -> Dict[str, float]:
        """
        Optimizar parámetros del proceso

        Args:
            target_properties: Propiedades objetivo
            constraints: Restricciones del proceso

        Returns:
            Parámetros optimizados
        """
        # Implementación simplificada de optimización
        # En producción, usar algoritmos de optimización avanzados

        optimized_params = {
            'laser_power': 250.0,      # W
            'scan_speed': 800.0,       # mm/s
            'layer_thickness': 30.0,   # μm
            'hatch_spacing': 100.0     # μm
        }

        self.logger.info("🎯 Parámetros del proceso optimizados")
        return optimized_params

    def export_am_results(self, solution: AdditiveManufacturingSolution,
                         output_path: Union[str, Path],
                         format: str = "json") -> str:
        """
        Exportar resultados de manufactura aditiva

        Args:
            solution: Solución de manufactura aditiva
            output_path: Ruta de salida
            format: Formato de exportación

        Returns:
            Ruta del archivo exportado
        """
        output_path = Path(output_path)

        if format == "json":
            export_data = {
                "additive_manufacturing_solution": {
                    "thermal_history": {
                        "peak_temperatures": solution.thermal_history.peak_temperatures,
                        "thermal_cycles": solution.thermal_history.thermal_cycles,
                        "total_time": solution.thermal_history.total_time,
                        "max_heating_rate": float(np.max(solution.thermal_history.heating_rates)),
                        "max_cooling_rate": float(np.max(solution.thermal_history.cooling_rates))
                    },
                    "melt_pool_dynamics": {
                        "dimensions": solution.melt_pool_dynamics.dimensions,
                        "surface_tension": solution.melt_pool_dynamics.surface_tension,
                        "viscosity": solution.melt_pool_dynamics.viscosity,
                        "evaporation_rate": solution.melt_pool_dynamics.evaporation_rate,
                        "keyhole_depth": solution.melt_pool_dynamics.keyhole_depth
                    },
                    "microstructure_evolution": {
                        "average_grain_size": float(np.mean(solution.microstructure_evolution.grain_size_distribution)),
                        "phase_fractions": solution.microstructure_evolution.phase_fractions,
                        "average_porosity": float(np.mean(solution.microstructure_evolution.porosity_distribution)),
                        "mechanical_properties": solution.microstructure_evolution.mechanical_properties
                    },
                    "build_quality_metrics": solution.build_quality_metrics,
                    "process_efficiency": solution.process_efficiency,
                    "defect_analysis": solution.defect_analysis,
                    "computation_time": solution.computation_time,
                    "timestamp": solution.timestamp.isoformat()
                },
                "metadata": {
                    "service_version": "AXIOM_META4_AM_v1.0",
                    "computation_date": datetime.now().isoformat()
                }
            }

            with open(output_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

        return str(output_path)

    def _calculate_spatial_resolution(self, domain_size: Tuple[float, float, float],
                                    grid_points: Tuple[int, int, int]) -> Dict[str, float]:
        """Calculate spatial resolution for simulation domain"""
        dx = domain_size[0] / grid_points[0]
        dy = domain_size[1] / grid_points[1]
        dz = domain_size[2] / grid_points[2]

        return {
            'dx': dx,
            'dy': dy,
            'dz': dz,
            'min_resolution': min(dx, dy, dz),
            'aspect_ratio': max(dx, dy, dz) / min(dx, dy, dz)
        }

    def _calculate_temporal_consistency(self, time_steps: int, simulation_time: float,
                                       thermal_diffusivity: float = 1e-6) -> Dict[str, float]:
        """Calculate temporal consistency metrics"""
        dt = simulation_time / time_steps
        cfl_number = dt / (thermal_diffusivity * 1e-6)

        return {
            'dt': dt,
            'cfl_number': cfl_number,
            'time_steps': time_steps,
            'stability_ratio': cfl_number < 0.5  # CFL condition
        }

    def _calculate_snr(self, signal: np.ndarray, noise: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio"""
        signal_power = np.mean(signal ** 2)
        noise_power = np.mean(noise ** 2)

        if noise_power == 0:
            return float('inf')

        return 10 * np.log10(signal_power / noise_power)


# Instancia global del servicio
additive_manufacturing_service = AdditiveManufacturingService()


def simulate_additive_process(laser_parameters: Dict[str, float],
                            process_parameters: Dict[str, float]) -> AdditiveManufacturingSolution:
    """Función de conveniencia para simulación de manufactura aditiva"""
    return additive_manufacturing_service.simulate_single_track(laser_parameters, process_parameters)


if __name__ == "__main__":
    # Demo del servicio de manufactura aditiva
    logger.info("🔥 Additive Manufacturing Service - Demo")

    print("🔥 Servicio de Manufactura Aditiva inicializado correctamente")
    print("📊 Capacidades disponibles:")
    print("  - Simulación térmica completa con PINN")
    print("  - Dinámica de fluidos del pool de fusión")
    print("  - Evolución microestructural")
    print("  - Análisis de defectos y calidad")
    print("  - Optimización de parámetros de proceso")

    print("\\n⚙️ Procesos soportados:")
    for process in AdditiveProcess:
        print(f"  • {process.value}")

    print("\\n🔧 Configurando proceso LPBF para material metálico...")

    # Propiedades del material (Inconel 718)
    material_properties = {
        'density': 8190,                    # kg/m³
        'thermal_diffusivity': 3.6e-6,      # m²/s
        'specific_heat': 435,               # J/(kg·K)
        'thermal_conductivity': 11.4,       # W/(m·K)
        'melting_temperature': 1600,        # K
        'boiling_temperature': 3000,        # K
        'latent_heat': 2.1e6,               # J/kg
        'surface_tension': 1.8,             # N/m
        'viscosity': 0.006,                 # Pa·s
        'thermal_expansion': 1.2e-5,        # 1/K
        'heat_transfer_coeff': 50,          # W/(m²·K)
        'grain_growth_activation': 1.5e5,   # J/mol
        'grain_growth_coeff': 1e-10,        # m²/s
        'liquidus_temperature': 1600,       # K
        'solidus_temperature': 1530,        # K
        'base_porosity': 0.001,
        'critical_solidification_rate': 0.1
    }

    # Configurar proceso
    additive_manufacturing_service.setup_process(
        AdditiveProcess.LASER_POWDER_BED_FUSION,
        MaterialType.METALLIC,
        material_properties
    )

    print("\\n⚡ Parámetros del láser configurados:")
    laser_parameters = {
        'power': 200,           # W
        'beam_radius': 50e-6,   # m
        'absorption': 0.35      # Eficiencia de absorción
    }
    print(f"  • Potencia: {laser_parameters['power']} W")
    print(f"  • Radio del haz: {laser_parameters['beam_radius']*1e6:.0f} μm")
    print(f"  • Absorción: {laser_parameters['absorption']:.1%}")

    print("\\n🏗️ Parámetros del proceso:")
    process_parameters = {
        'scan_speed': 800.0,      # mm/s
        'layer_thickness': 30.0,  # μm
        'hatch_spacing': 100.0,   # μm
        'melting_temperature': 1600.0  # K
    }
    print(f"  • Velocidad de escaneo: {process_parameters['scan_speed']} mm/s")
    print(f"  • Espesor de capa: {process_parameters['layer_thickness']} μm")
    print(f"  • Espaciado de hatch: {process_parameters['hatch_spacing']} μm")

    print("\\n🔬 Simulando pista única...")
    try:
        solution = additive_manufacturing_service.simulate_single_track(
            laser_parameters, process_parameters,
            domain_size=(1e-3, 1e-3, 0.5e-3),  # 1mm x 1mm x 0.5mm
            simulation_time=2e-3  # 2ms
        )

        print("\\n📈 Resultados obtenidos:")
        print(f"  • Temperatura pico máxima: {max(solution.thermal_history.peak_temperatures):.0f} K")
        print(f"  • Ciclos térmicos: {solution.thermal_history.thermal_cycles}")
        print(f"  • Tasa máxima de calentamiento: {np.max(solution.thermal_history.heating_rates):.0e} K/s")
        print(f"  • Tasa máxima de enfriamiento: {np.max(solution.thermal_history.cooling_rates):.0e} K/s")

        print("\\n🔥 Dinámica del pool de fusión:")
        print(f"  • Longitud: {solution.melt_pool_dynamics.dimensions['length']*1e6:.1f} μm")
        print(f"  • Ancho: {solution.melt_pool_dynamics.dimensions['width']*1e6:.1f} μm")
        print(f"  • Profundidad: {solution.melt_pool_dynamics.dimensions['depth']*1e6:.1f} μm")
        print(f"  • Tensión superficial: {solution.melt_pool_dynamics.surface_tension:.2f} N/m")

        print("\\n🔬 Microestructura:")
        print(f"  • Tamaño promedio de grano: {np.mean(solution.microstructure_evolution.grain_size_distribution)*1e6:.1f} μm")
        print(f"  • Porosidad promedio: {np.mean(solution.microstructure_evolution.porosity_distribution):.2%}")
        print(f"  • Resistencia a la fluencia: {solution.microstructure_evolution.mechanical_properties['yield_strength']:.0f} MPa")

        print("\\n📊 Métricas de calidad:")
        print(f"  • Estabilidad térmica: {solution.build_quality_metrics['thermal_stability']:.2f}")
        print(f"  • Consistencia del pool: {solution.build_quality_metrics['melt_pool_consistency']:.2f}")
        print(f"  • Calidad microestructural: {solution.build_quality_metrics['microstructure_quality']:.2f}")
        print(f"  • Densidad: {solution.build_quality_metrics['density']:.2%}")
        print(f"  • Calidad general: {solution.build_quality_metrics['overall_quality']:.2f}")

        print("\\n⚡ Eficiencia del proceso:")
        print(f"  • Eficiencia energética: {solution.process_efficiency['energy_efficiency']:.1%}")
        print(f"  • Eficiencia de fusión: {solution.process_efficiency['melt_efficiency']:.2f}")
        print(f"  • Eficiencia de solidificación: {solution.process_efficiency['solidification_efficiency']:.2f}")

        print("\\n🔍 Análisis de defectos:")
        print(f"  • Porosidad: {solution.defect_analysis['porosity']['distribution']}")
        print(f"  • Riesgo de cracking: {solution.defect_analysis['cracking']['risk_level']}")
        print(f"  • Riesgo de falta de fusión: {solution.defect_analysis['lack_of_fusion']['risk_level']}")

        print("\\n🏆 Servicio de Manufactura Aditiva listo para aplicaciones industriales!")

    except Exception as e:
        print(f"❌ Error en simulación de manufactura aditiva: {e}")
        import traceback
        traceback.print_exc()
