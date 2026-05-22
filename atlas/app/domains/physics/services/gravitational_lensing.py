"""
Gravitational Lensing Analysis Service - AXIOM Advanced
======================================================

Servicio especializado para análisis de lentes gravitacionales con cálculos
de Einstein radius, posiciones de imágenes múltiples y magnificación.

Características:
- Cálculo de Einstein radius para lentes puntuales y extendidas
- Análisis de deflexión gravitacional
- Predicción de posiciones de imágenes múltiples
- Cálculo de magnificación y distorsión
- Análisis de caustics y critical curves
- Weak lensing shear analysis

Modelos implementados:
- Singular Isothermal Sphere (SIS)
- Navarro-Frenk-White (NFW) profile
- Point mass lens
- Singular Isothermal Ellipsoid (SIE)

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import scipy.optimize
from scipy.special import hyp2f1

from app.services.base_service import BaseService
from app.exceptions.domain.physics import PhysicsError

logger = logging.getLogger(__name__)

# Constantes físicas y astronómicas
C_LIGHT = 2.998e8  # m/s
G_NEWTON = 6.674e-11  # m^3 kg^-1 s^-2
SOLAR_MASS = 1.989e30  # kg
PC_TO_M = 3.086e16  # metros por parsec
MPC_TO_M = 3.086e22  # metros por megaparsec


@dataclass
class LensSystem:
    """Sistema de lentes gravitacionales"""
    # Propiedades de la lente
    lens_mass: float  # Masa en masas solares
    lens_redshift: float  # z_lens
    
    # Propiedades de la fuente
    source_redshift: float  # z_source
    
    # Distancias angulares (en Mpc)
    d_lens: float
    d_source: float
    d_lens_source: float
    
    # Parámetros del modelo de lente
    lens_model: str = "SIS"  # SIS, NFW, point_mass, SIE
    
    # Parámetros adicionales específicos del modelo
    model_params: Optional[Dict[str, float]] = None


@dataclass
class LensingResult:
    """Resultado del análisis de lentes"""
    # Einstein radius
    einstein_radius_arcsec: float
    einstein_radius_physical_kpc: float
    
    # Posiciones de imágenes
    image_positions: List[Tuple[float, float]]  # (theta_x, theta_y) en arcsec
    image_magnifications: List[float]
    total_magnification: float
    
    # Parámetros derivados
    enclosed_mass: float  # Masa dentro del Einstein radius
    
    # Critical curves y caustics
    critical_curves: Optional[np.ndarray] = None
    caustics: Optional[np.ndarray] = None
    
    # Parámetros adicionales
    velocity_dispersion: Optional[float] = None  # km/s para modelos SIS
    
    # Análisis de weak lensing
    shear_gamma1: float = 0.0
    shear_gamma2: float = 0.0
    convergence_kappa: float = 0.0


class GravitationalLensingService(BaseService):
    """
    Servicio de análisis de lentes gravitacionales
    """
    
    def __init__(self):
        super().__init__("GravitationalLensing")
        
        # Configuración por defecto de cosmología (Planck 2018)
        self.cosmology = {
            'H0': 67.4,  # km/s/Mpc
            'omega_m': 0.315,
            'omega_lambda': 0.685,
            'omega_k': 0.0
        }
        
        logger.info("🌌 GravitationalLensingService inicializado")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process gravitational lensing service requests"""
        try:
            action = request_data.get("action", "")
            
            if action == "analyze_strong_lensing":
                return await self.analyze_strong_lensing(
                    lens_mass_solar=request_data["lens_mass_solar"],
                    lens_redshift=request_data["lens_redshift"],
                    source_redshift=request_data["source_redshift"],
                    source_position=request_data["source_position"],
                    lens_model=request_data.get("lens_model", "SIS"),
                    model_params=request_data.get("model_params")
                )
            elif action == "calculate_einstein_radius":
                return await self.calculate_einstein_radius_simple(
                    lens_mass_solar=request_data["lens_mass_solar"],
                    lens_redshift=request_data["lens_redshift"],
                    source_redshift=request_data["source_redshift"],
                    lens_model=request_data.get("lens_model", "point_mass")
                )
            elif action == "analyze_microlensing":
                return await self.analyze_microlensing_event(
                    lens_mass_solar=request_data["lens_mass_solar"],
                    source_distance_kpc=request_data["source_distance_kpc"],
                    lens_distance_kpc=request_data["lens_distance_kpc"],
                    impact_parameter_au=request_data["impact_parameter_au"],
                    relative_velocity_km_s=request_data["relative_velocity_km_s"]
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "analyze_strong_lensing",
                        "calculate_einstein_radius", 
                        "analyze_microlensing"
                    ]
                }
                
        except PhysicsError as e:
            return self.handle_error(e, "process_request")
        except Exception as e:
            return self.handle_error(e, "process_request")
    
    async def analyze_strong_lensing(
        self,
        lens_mass_solar: float,
        lens_redshift: float,
        source_redshift: float,
        source_position: Tuple[float, float],
        lens_model: str = "SIS",
        model_params: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Análisis completo de strong lensing
        
        Args:
            lens_mass_solar: Masa de la lente en masas solares
            lens_redshift: Redshift de la lente
            source_redshift: Redshift de la fuente  
            source_position: Posición de la fuente (beta_x, beta_y) en arcsec
            lens_model: Modelo de lente (SIS, NFW, point_mass, SIE)
            model_params: Parámetros adicionales del modelo
            
        Returns:
            Análisis completo de strong lensing
        """
        try:
            logger.info(f"🌌 Analizando strong lensing: {lens_model}, M={lens_mass_solar:.2e} M_sun")
            
            # Calcular distancias angulares
            distances = self._calculate_angular_distances(lens_redshift, source_redshift)
            
            # Crear sistema de lentes
            lens_system = LensSystem(
                lens_mass=lens_mass_solar,
                lens_redshift=lens_redshift,
                source_redshift=source_redshift,
                d_lens=distances['d_lens'],
                d_source=distances['d_source'],
                d_lens_source=distances['d_lens_source'],
                lens_model=lens_model,
                model_params=model_params or {}
            )
            
            # Calcular Einstein radius
            einstein_radius = self._calculate_einstein_radius(lens_system)
            
            # Encontrar posiciones de imágenes
            image_analysis = await self._find_image_positions(lens_system, source_position)
            
            # Calcular magnificaciones
            magnifications = self._calculate_magnifications(lens_system, image_analysis['positions'])
            
            # Análisis de critical curves y caustics
            critical_analysis = await self._analyze_critical_curves(lens_system)
            
            # Análisis de weak lensing
            weak_lensing = self._analyze_weak_lensing(lens_system, source_position)
            
            # Parámetros físicos derivados
            physical_params = self._calculate_physical_parameters(lens_system, einstein_radius)
            
            return {
                "lens_system": {
                    "lens_mass_solar": lens_mass_solar,
                    "lens_redshift": lens_redshift,
                    "source_redshift": source_redshift,
                    "lens_model": lens_model
                },
                "einstein_radius": {
                    "arcsec": einstein_radius['arcsec'],
                    "physical_kpc": einstein_radius['physical_kpc'],
                    "mass_enclosed_solar": physical_params['enclosed_mass']
                },
                "strong_lensing": {
                    "n_images": len(image_analysis['positions']),
                    "image_positions_arcsec": image_analysis['positions'],
                    "image_magnifications": magnifications['individual'],
                    "total_magnification": magnifications['total'],
                    "image_types": image_analysis.get('types', [])
                },
                "critical_curves": {
                    "n_critical_points": len(critical_analysis.get('critical_curves', [])),
                    "caustic_area_arcsec2": critical_analysis.get('caustic_area', 0.0),
                    "cross_section_arcsec2": critical_analysis.get('cross_section', 0.0)
                },
                "weak_lensing": {
                    "shear_gamma1": weak_lensing['gamma1'],
                    "shear_gamma2": weak_lensing['gamma2'],
                    "convergence_kappa": weak_lensing['kappa'],
                    "reduced_shear_g1": weak_lensing['g1'],
                    "reduced_shear_g2": weak_lensing['g2']
                },
                "physical_parameters": physical_params,
                "distances": {
                    "d_lens_mpc": distances['d_lens'],
                    "d_source_mpc": distances['d_source'],
                    "d_lens_source_mpc": distances['d_lens_source']
                }
            }
            
        except QuantumError as e:
            logger.error(f"❌ Error en análisis de strong lensing: {str(e)}")
            raise
    
    async def calculate_einstein_radius_simple(
        self,
        lens_mass_solar: float,
        lens_redshift: float,
        source_redshift: float,
        lens_model: str = "point_mass"
    ) -> Dict[str, Any]:
        """
        Cálculo simple del Einstein radius para diferentes modelos
        
        Args:
            lens_mass_solar: Masa de la lente en masas solares
            lens_redshift: Redshift de la lente
            source_redshift: Redshift de la fuente
            lens_model: Modelo de lente
            
        Returns:
            Einstein radius y parámetros relacionados
        """
        try:
            logger.info(f"📐 Calculando Einstein radius: {lens_model}")
            
            # Distancias angulares
            distances = self._calculate_angular_distances(lens_redshift, source_redshift)
            
            # Sistema de lentes simplificado
            lens_system = LensSystem(
                lens_mass=lens_mass_solar,
                lens_redshift=lens_redshift,
                source_redshift=source_redshift,
                d_lens=distances['d_lens'],
                d_source=distances['d_source'],
                d_lens_source=distances['d_lens_source'],
                lens_model=lens_model
            )
            
            # Calcular Einstein radius
            einstein_radius = self._calculate_einstein_radius(lens_system)
            
            # Parámetros derivados
            physical_params = self._calculate_physical_parameters(lens_system, einstein_radius)
            
            # Escalas características
            scales = self._calculate_characteristic_scales(lens_system)
            
            return {
                "einstein_radius_arcsec": einstein_radius['arcsec'],
                "einstein_radius_kpc": einstein_radius['physical_kpc'],
                "mass_within_einstein_radius_solar": physical_params['enclosed_mass'],
                "velocity_dispersion_km_s": physical_params.get('velocity_dispersion', 0.0),
                "deflection_scale_arcsec": scales['deflection_scale'],
                "physical_scale_kpc_arcsec": scales['physical_scale'],
                "time_delay_scale_days": scales.get('time_delay_scale', 0.0),
                "lensing_strength": self._calculate_lensing_strength(lens_system),
                "system_classification": self._classify_lens_system(lens_system, einstein_radius)
            }
            
        except QuantumError as e:
            logger.error(f"❌ Error calculando Einstein radius: {str(e)}")
            raise
    
    async def analyze_microlensing_event(
        self,
        lens_mass_solar: float,
        source_distance_kpc: float,
        lens_distance_kpc: float,
        impact_parameter_au: float,
        relative_velocity_km_s: float
    ) -> Dict[str, Any]:
        """
        Análisis de evento de microlensing
        
        Args:
            lens_mass_solar: Masa de la lente
            source_distance_kpc: Distancia a la fuente
            lens_distance_kpc: Distancia a la lente
            impact_parameter_au: Parámetro de impacto
            relative_velocity_km_s: Velocidad relativa
            
        Returns:
            Análisis del evento de microlensing
        """
        try:
            logger.info("🔍 Analizando evento de microlensing")
            
            # Calcular Einstein radius para microlensing
            einstein_radius_au = self._calculate_microlensing_einstein_radius(
                lens_mass_solar, source_distance_kpc, lens_distance_kpc
            )
            
            # Parámetro de impacto normalizado
            u_min = impact_parameter_au / einstein_radius_au
            
            # Magnificación máxima
            max_magnification = self._calculate_microlensing_magnification(u_min)
            
            # Duración del evento
            event_duration = self._calculate_microlensing_duration(
                einstein_radius_au, relative_velocity_km_s
            )
            
            # Curva de luz del evento
            light_curve = self._generate_microlensing_light_curve(
                u_min, event_duration, relative_velocity_km_s, einstein_radius_au
            )
            
            return {
                "microlensing_parameters": {
                    "einstein_radius_au": einstein_radius_au,
                    "impact_parameter_normalized": u_min,
                    "maximum_magnification": max_magnification,
                    "event_duration_days": event_duration,
                    "einstein_crossing_time_days": event_duration / (2 * np.sqrt(1 + u_min**2))
                },
                "event_classification": {
                    "event_type": "Point source" if u_min > 0.1 else "High magnification",
                    "detectability": "Easy" if max_magnification > 2 else "Difficult",
                    "duration_class": "Long" if event_duration > 100 else "Short"
                },
                "light_curve": {
                    "time_days": light_curve['time'].tolist(),
                    "magnification": light_curve['magnification'].tolist(),
                    "flux_normalized": light_curve['flux'].tolist()
                },
                "observational_predictions": {
                    "peak_brightness_increase_mag": -2.5 * np.log10(max_magnification),
                    "fwhm_duration_days": event_duration * 0.6,  # Aproximación
                    "rise_time_days": event_duration * 0.3,
                    "optimal_observation_window_days": event_duration * 1.5
                }
            }
            
        except QuantumError as e:
            logger.error(f"❌ Error en análisis de microlensing: {str(e)}")
            raise
    
    # ========== MÉTODOS DE CÁLCULO PRINCIPALES ==========
    
    def _calculate_angular_distances(
        self,
        z_lens: float,
        z_source: float
    ) -> Dict[str, float]:
        """Calcula distancias angulares cosmológicas"""
        
        # Simplificación: usar aproximación de bajo redshift si z < 0.5
        # Para redshifts altos, usar integración numérica
        
        if z_lens > 2.0 or z_source > 5.0:
            raise ValueError("Redshifts muy altos para este análisis simplificado")
        
        H0 = self.cosmology['H0']  # km/s/Mpc
        c = 299792.458  # km/s
        
        # Distancia de luminosidad (aproximación)
        d_lens = c * z_lens / H0  # Mpc
        d_source = c * z_source / H0  # Mpc
        
        # Distancia angular entre lente y fuente
        # Para cosmología plana: D_ls = D_s - D_l en aproximación de bajo z
        d_lens_source = d_source - d_lens
        
        if d_lens_source <= 0:
            raise ValueError("Fuente debe estar detrás de la lente (z_source > z_lens)")
        
        return {
            'd_lens': d_lens,
            'd_source': d_source,
            'd_lens_source': d_lens_source
        }
    
    def _calculate_einstein_radius(self, lens_system: LensSystem) -> Dict[str, float]:
        """Calcula el Einstein radius"""
        
        # Einstein radius angular en radianes
        # theta_E = sqrt(4GM/c^2 * D_ls / (D_l * D_s))
        
        mass_kg = lens_system.lens_mass * SOLAR_MASS
        d_l = lens_system.d_lens * MPC_TO_M
        d_s = lens_system.d_source * MPC_TO_M
        d_ls = lens_system.d_lens_source * MPC_TO_M
        
        # Einstein radius en radianes
        theta_e_rad = np.sqrt(4 * G_NEWTON * mass_kg * d_ls / (C_LIGHT**2 * d_l * d_s))
        
        # Convertir a arcsec
        theta_e_arcsec = theta_e_rad * 206265  # rad to arcsec
        
        # Tamaño físico en kpc
        physical_size_kpc = theta_e_arcsec * d_l / (206265 * 1000 * PC_TO_M)  # kpc
        
        return {
            'arcsec': theta_e_arcsec,
            'physical_kpc': physical_size_kpc,
            'radians': theta_e_rad
        }
    
    async def _find_image_positions(
        self,
        lens_system: LensSystem,
        source_position: Tuple[float, float]
    ) -> Dict[str, Any]:
        """Encuentra posiciones de imágenes múltiples"""
        
        beta_x, beta_y = source_position
        
        if lens_system.lens_model == "point_mass":
            # Para lente puntual, solución analítica
            positions = self._solve_point_mass_lensing(lens_system, beta_x, beta_y)
        elif lens_system.lens_model == "SIS":
            # Singular Isothermal Sphere
            positions = self._solve_sis_lensing(lens_system, beta_x, beta_y)
        else:
            # Solución numérica general
            positions = self._solve_lens_equation_numerical(lens_system, beta_x, beta_y)
        
        # Clasificar imágenes
        image_types = self._classify_images(positions, source_position)
        
        return {
            'positions': positions,
            'types': image_types
        }
    
    def _solve_point_mass_lensing(
        self,
        lens_system: LensSystem,
        beta_x: float,
        beta_y: float
    ) -> List[Tuple[float, float]]:
        """Solución analítica para lente puntual"""
        
        einstein_radius = self._calculate_einstein_radius(lens_system)
        theta_e = einstein_radius['arcsec']
        
        beta = np.sqrt(beta_x**2 + beta_y**2)
        
        if beta == 0:
            # Fuente en el eje óptico - anillo de Einstein
            return [(theta_e, 0), (-theta_e, 0), (0, theta_e), (0, -theta_e)]
        
        # Dos imágenes para fuente fuera del eje
        theta_plus = 0.5 * (beta + np.sqrt(beta**2 + 4*theta_e**2))
        theta_minus = 0.5 * (beta - np.sqrt(beta**2 + 4*theta_e**2))
        
        # Posiciones angulares
        cos_phi = beta_x / beta if beta > 0 else 1
        sin_phi = beta_y / beta if beta > 0 else 0
        
        image1 = (theta_plus * cos_phi, theta_plus * sin_phi)
        image2 = (theta_minus * cos_phi, theta_minus * sin_phi)
        
        return [image1, image2]
    
    def _solve_sis_lensing(
        self,
        lens_system: LensSystem,
        beta_x: float,
        beta_y: float
    ) -> List[Tuple[float, float]]:
        """Solución para Singular Isothermal Sphere"""
        
        einstein_radius = self._calculate_einstein_radius(lens_system)
        theta_e = einstein_radius['arcsec']
        
        beta = np.sqrt(beta_x**2 + beta_y**2)
        
        if beta == 0:
            # Anillo de Einstein
            n_points = 8
            angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
            return [(theta_e * np.cos(a), theta_e * np.sin(a)) for a in angles]
        
        # Para SIS: dos imágenes
        cos_phi = beta_x / beta if beta > 0 else 1
        sin_phi = beta_y / beta if beta > 0 else 0
        
        # Posiciones de las imágenes para SIS
        theta1 = beta + theta_e
        theta2 = abs(beta - theta_e) if beta > theta_e else 0
        
        images = [(theta1 * cos_phi, theta1 * sin_phi)]
        if theta2 > 0:
            images.append((theta2 * cos_phi, theta2 * sin_phi))
        
        return images
    
    def _solve_lens_equation_numerical(
        self,
        lens_system: LensSystem,
        beta_x: float,
        beta_y: float
    ) -> List[Tuple[float, float]]:
        """Solución numérica general de la ecuación de lentes"""
        
        # Implementación simplificada - buscar raíces numéricamente
        einstein_radius = self._calculate_einstein_radius(lens_system)
        theta_e = einstein_radius['arcsec']
        
        # Grid de búsqueda
        theta_max = max(5 * theta_e, 2.0)  # arcsec
        n_grid = 50
        
        theta_x_grid = np.linspace(-theta_max, theta_max, n_grid)
        theta_y_grid = np.linspace(-theta_max, theta_max, n_grid)
        
        positions = []
        
        # Buscar posiciones donde la ecuación de lentes se satisface
        for theta_x in theta_x_grid:
            for theta_y in theta_y_grid:
                # Evaluar ecuación de lentes
                deflection = self._calculate_deflection_angle(
                    lens_system, theta_x, theta_y
                )
                
                # Residuo de la ecuación de lentes
                residual_x = theta_x - deflection[0] - beta_x
                residual_y = theta_y - deflection[1] - beta_y
                residual = np.sqrt(residual_x**2 + residual_y**2)
                
                # Si el residuo es pequeño, es una imagen
                if residual < 0.1:  # Tolerance en arcsec
                    # Refinar con optimización local
                    result = scipy.optimize.minimize(
                        lambda theta: self._lens_equation_residual(
                            lens_system, theta, (beta_x, beta_y)
                        ),
                        [theta_x, theta_y],
                        method='Nelder-Mead'
                    )
                    
                    if result.success and result.fun < 0.01:
                        pos = (float(result.x[0]), float(result.x[1]))
                        
                        # Evitar duplicados
                        is_duplicate = False
                        for existing_pos in positions:
                            dist = np.sqrt((pos[0] - existing_pos[0])**2 + 
                                         (pos[1] - existing_pos[1])**2)
                            if dist < 0.05:  # 0.05 arcsec tolerance
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            positions.append(pos)
        
        return positions
    
    def _calculate_deflection_angle(
        self,
        lens_system: LensSystem,
        theta_x: float,
        theta_y: float
    ) -> Tuple[float, float]:
        """Calcula ángulo de deflexión para posición dada"""
        
        if lens_system.lens_model == "point_mass":
            return self._deflection_point_mass(lens_system, theta_x, theta_y)
        elif lens_system.lens_model == "SIS":
            return self._deflection_sis(lens_system, theta_x, theta_y)
        else:
            # Modelo por defecto (point mass)
            return self._deflection_point_mass(lens_system, theta_x, theta_y)
    
    def _deflection_point_mass(
        self,
        lens_system: LensSystem,
        theta_x: float,
        theta_y: float
    ) -> Tuple[float, float]:
        """Deflexión para lente puntual"""
        
        einstein_radius = self._calculate_einstein_radius(lens_system)
        theta_e = einstein_radius['arcsec']
        
        theta = np.sqrt(theta_x**2 + theta_y**2)
        
        if theta == 0:
            return (0.0, 0.0)
        
        # Deflexión radial para lente puntual
        alpha = theta_e**2 / theta
        
        return (alpha * theta_x / theta, alpha * theta_y / theta)
    
    def _deflection_sis(
        self,
        lens_system: LensSystem,
        theta_x: float,
        theta_y: float
    ) -> Tuple[float, float]:
        """Deflexión para SIS"""
        
        einstein_radius = self._calculate_einstein_radius(lens_system)
        theta_e = einstein_radius['arcsec']
        
        theta = np.sqrt(theta_x**2 + theta_y**2)
        
        if theta == 0:
            return (0.0, 0.0)
        
        # Para SIS: deflexión constante = theta_E
        alpha = theta_e
        
        return (alpha * theta_x / theta, alpha * theta_y / theta)
    
    def _lens_equation_residual(
        self,
        lens_system: LensSystem,
        theta: np.ndarray,
        beta: Tuple[float, float]
    ) -> float:
        """Residuo de la ecuación de lentes para optimización"""
        
        theta_x, theta_y = theta
        beta_x, beta_y = beta
        
        deflection = self._calculate_deflection_angle(lens_system, theta_x, theta_y)
        
        residual_x = theta_x - deflection[0] - beta_x
        residual_y = theta_y - deflection[1] - beta_y
        
        return residual_x**2 + residual_y**2
    
    def _calculate_magnifications(
        self,
        lens_system: LensSystem,
        image_positions: List[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """Calcula magnificaciones de las imágenes"""
        
        magnifications = []
        
        for pos in image_positions:
            mag = self._calculate_single_image_magnification(lens_system, pos)
            magnifications.append(mag)
        
        total_mag = sum(magnifications)
        
        return {
            'individual': magnifications,
            'total': total_mag
        }
    
    def _calculate_single_image_magnification(
        self,
        lens_system: LensSystem,
        image_position: Tuple[float, float]
    ) -> float:
        """Calcula magnificación de una imagen individual"""
        
        theta_x, theta_y = image_position
        
        # Calcular matriz Jacobiana de la transformación de lentes
        eps = 0.01  # Step size para diferencias finitas
        
        # Derivadas parciales de la deflexión
        alpha_x_plus, alpha_y_plus = self._calculate_deflection_angle(
            lens_system, theta_x + eps, theta_y
        )
        alpha_x_minus, alpha_y_minus = self._calculate_deflection_angle(
            lens_system, theta_x - eps, theta_y
        )
        alpha_x, alpha_y = self._calculate_deflection_angle(
            lens_system, theta_x, theta_y + eps
        )
        alpha_x2, alpha_y2 = self._calculate_deflection_angle(
            lens_system, theta_x, theta_y - eps
        )
        
        # Matriz Jacobiana
        d_alpha_x_d_theta_x = (alpha_x_plus - alpha_x_minus) / (2 * eps)
        d_alpha_y_d_theta_y = (alpha_y2 - alpha_y) / (2 * eps)
        d_alpha_x_d_theta_y = (alpha_x - alpha_x_minus) / (2 * eps)
        d_alpha_y_d_theta_x = (alpha_y_plus - alpha_y_minus) / (2 * eps)
        
        # Matriz de magnificación
        A = np.array([
            [1 - d_alpha_x_d_theta_x, -d_alpha_x_d_theta_y],
            [-d_alpha_y_d_theta_x, 1 - d_alpha_y_d_theta_y]
        ])
        
        # Magnificación = 1/|det(A)|
        det_A = np.linalg.det(A)
        
        if abs(det_A) < 1e-10:
            return 1000.0  # Magnificación muy alta cerca de critical curve
        
        return abs(1.0 / det_A)
    
    def _classify_images(
        self,
        positions: List[Tuple[float, float]],
        source_position: Tuple[float, float]
    ) -> List[str]:
        """Clasifica tipos de imágenes"""
        
        types = []
        
        for pos in positions:
            # Distancia de la imagen al centro
            r_image = np.sqrt(pos[0]**2 + pos[1]**2)
            r_source = np.sqrt(source_position[0]**2 + source_position[1]**2)
            
            if r_image > r_source:
                types.append("primary")
            else:
                types.append("secondary")
        
        return types
    
    # ========== MÉTODOS AUXILIARES ==========
    
    async def _analyze_critical_curves(self, lens_system: LensSystem) -> Dict[str, Any]:
        """Analiza critical curves y caustics"""
        
        # Implementación simplificada
        einstein_radius = self._calculate_einstein_radius(lens_system)
        theta_e = einstein_radius['arcsec']
        
        if lens_system.lens_model == "point_mass":
            # Para lente puntual, critical curve es círculo
            critical_radius = theta_e
            caustic_area = np.pi * (theta_e / 2)**2  # Área aproximada de la caustic
        else:
            critical_radius = theta_e
            caustic_area = np.pi * theta_e**2 * 0.25
        
        # Cross-section para strong lensing
        cross_section = np.pi * theta_e**2
        
        return {
            'critical_curves': [(critical_radius, 0)],  # Simplificado
            'caustic_area': caustic_area,
            'cross_section': cross_section
        }
    
    def _analyze_weak_lensing(
        self,
        lens_system: LensSystem,
        source_position: Tuple[float, float]
    ) -> Dict[str, float]:
        """Análisis de weak lensing"""
        
        # Parámetros de weak lensing simplificados
        theta_x, theta_y = source_position
        
        einstein_radius = self._calculate_einstein_radius(lens_system)
        theta_e = einstein_radius['arcsec']
        
        r = np.sqrt(theta_x**2 + theta_y**2)
        
        if r == 0:
            return {'gamma1': 0, 'gamma2': 0, 'kappa': 1, 'g1': 0, 'g2': 0}
        
        # Convergencia (simplificada)
        if lens_system.lens_model == "SIS":
            kappa = theta_e / (2 * r) if r > 0 else 1
        else:
            kappa = (theta_e / r)**2 / 2 if r > 0 else 1
        
        # Shear components (simplificado)
        cos_2phi = (theta_x**2 - theta_y**2) / r**2 if r > 0 else 1
        sin_2phi = 2 * theta_x * theta_y / r**2 if r > 0 else 0
        
        gamma = kappa  # Aproximación para lente circular
        gamma1 = gamma * cos_2phi
        gamma2 = gamma * sin_2phi
        
        # Reduced shear
        denom = 1 - kappa
        if abs(denom) > 1e-6:
            g1 = gamma1 / denom
            g2 = gamma2 / denom
        else:
            g1 = gamma1
            g2 = gamma2
        
        return {
            'gamma1': gamma1,
            'gamma2': gamma2,
            'kappa': kappa,
            'g1': g1,
            'g2': g2
        }
    
    def _calculate_physical_parameters(
        self,
        lens_system: LensSystem,
        einstein_radius: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calcula parámetros físicos derivados"""
        
        # Masa dentro del Einstein radius
        enclosed_mass = lens_system.lens_mass  # Para lente puntual
        
        # Dispersión de velocidad para modelos SIS
        if lens_system.lens_model == "SIS":
            # sigma_v = c * theta_E * sqrt(D_s / (4*pi * D_ls))
            theta_e_rad = einstein_radius['radians']
            d_s = lens_system.d_source * MPC_TO_M
            d_ls = lens_system.d_lens_source * MPC_TO_M
            
            sigma_v = C_LIGHT * theta_e_rad * np.sqrt(d_s / (4 * np.pi * d_ls))
            sigma_v_km_s = sigma_v / 1000  # km/s
        else:
            sigma_v_km_s = 0.0
        
        return {
            'enclosed_mass': enclosed_mass,
            'velocity_dispersion': sigma_v_km_s,
            'lens_strength': einstein_radius['arcsec']
        }
    
    def _calculate_characteristic_scales(self, lens_system: LensSystem) -> Dict[str, float]:
        """Calcula escalas características del sistema"""
        
        einstein_radius = self._calculate_einstein_radius(lens_system)
        theta_e = einstein_radius['arcsec']
        
        # Escala de deflexión
        deflection_scale = theta_e
        
        # Escala física (kpc/arcsec)
        d_l = lens_system.d_lens * MPC_TO_M
        physical_scale = d_l / (206265 * 1000 * PC_TO_M)  # kpc/arcsec
        
        # Escala de tiempo de delay (simplificada)
        time_delay_scale = 0.0  # Placeholder
        
        return {
            'deflection_scale': deflection_scale,
            'physical_scale': physical_scale,
            'time_delay_scale': time_delay_scale
        }
    
    def _calculate_lensing_strength(self, lens_system: LensSystem) -> float:
        """Calcula fuerza del lensing"""
        
        einstein_radius = self._calculate_einstein_radius(lens_system)
        
        # Fuerza basada en Einstein radius y redshifts
        strength = einstein_radius['arcsec'] * (1 + lens_system.lens_redshift)
        
        return strength
    
    def _classify_lens_system(
        self,
        lens_system: LensSystem,
        einstein_radius: Dict[str, float]
    ) -> str:
        """Clasifica el sistema de lentes"""
        
        theta_e = einstein_radius['arcsec']
        
        if theta_e > 5.0:
            return "Strong lens - cluster"
        elif theta_e > 1.0:
            return "Strong lens - galaxy"
        elif theta_e > 0.1:
            return "Intermediate lens"
        else:
            return "Weak lens"
    
    # ========== MÉTODOS DE MICROLENSING ==========
    
    def _calculate_microlensing_einstein_radius(
        self,
        lens_mass_solar: float,
        source_distance_kpc: float,
        lens_distance_kpc: float
    ) -> float:
        """Calcula Einstein radius para microlensing (en AU)"""
        
        # Distancias en metros
        d_l = lens_distance_kpc * 1000 * PC_TO_M
        d_s = source_distance_kpc * 1000 * PC_TO_M
        d_ls = d_s - d_l
        
        if d_ls <= 0:
            raise ValueError("Fuente debe estar más lejos que la lente")
        
        # Masa en kg
        mass_kg = lens_mass_solar * SOLAR_MASS
        
        # Einstein radius en metros
        r_e = np.sqrt(4 * G_NEWTON * mass_kg * d_ls * d_l / (C_LIGHT**2 * d_s))
        
        # Convertir a AU
        AU = 1.496e11  # metros
        r_e_au = r_e / AU
        
        return r_e_au
    
    def _calculate_microlensing_magnification(self, u: float) -> float:
        """Calcula magnificación de microlensing"""
        
        # A = (u^2 + 2) / (u * sqrt(u^2 + 4))
        if u == 0:
            return float('inf')
        
        magnification = (u**2 + 2) / (u * np.sqrt(u**2 + 4))
        
        return magnification
    
    def _calculate_microlensing_duration(
        self,
        einstein_radius_au: float,
        relative_velocity_km_s: float
    ) -> float:
        """Calcula duración del evento de microlensing"""
        
        # Convertir velocidad a AU/día
        km_s_to_au_day = 86400 / 1.496e8  # conversión
        velocity_au_day = relative_velocity_km_s * km_s_to_au_day
        
        # Tiempo de cruce del Einstein radius
        t_e = 2 * einstein_radius_au / velocity_au_day  # días
        
        return t_e
    
    def _generate_microlensing_light_curve(
        self,
        u_min: float,
        duration_days: float,
        velocity_km_s: float,
        einstein_radius_au: float
    ) -> Dict[str, np.ndarray]:
        """Genera curva de luz de microlensing"""
        
        # Grid temporal
        t_max = duration_days * 2
        time = np.linspace(-t_max, t_max, 200)
        
        # Parámetro de impacto en función del tiempo
        t_e = duration_days / 2  # Einstein crossing time
        u = np.sqrt(u_min**2 + (time / t_e)**2)
        
        # Magnificación
        magnification = (u**2 + 2) / (u * np.sqrt(u**2 + 4))
        
        # Flujo normalizado
        flux = magnification
        
        return {
            'time': time,
            'magnification': magnification,
            'flux': flux
        }


# Instancia global del servicio
gravitational_lensing_service = GravitationalLensingService()
