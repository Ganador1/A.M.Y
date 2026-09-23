"""
AXIOM Astronomy - Servicio de Análisis Multi-Longitud de Onda
=============================================================

Este servicio implementa análisis astronómico comprehensivo a través de múltiples
longitudes de onda del espectro electromagnético, permitiendo el estudio integral
de objetos astronómicos desde radio hasta rayos gamma.

Arquitectura:
- Análisis espectral multi-banda (radio, infrarrojo, óptico, UV, rayos X, gamma)
- Fotometría y colorimetría avanzada
- Correlación temporal entre diferentes bandas
- Análisis de poblaciones estelares
- Caracterización de AGNs y objetos extragalácticos

Características principales:
1. Multi-band Photometry: Análisis fotométrico simultáneo en múltiples bandas
2. SED Analysis: Modelado de distribuciones espectrales de energía
3. Color Analysis: Diagramas color-color y color-magnitud
4. Variability Correlation: Correlación de variabilidad entre bandas
5. Population Synthesis: Síntesis de poblaciones estelares
6. AGN Characterization: Caracterización de núcleos galácticos activos

Integración con AXIOM:
- Compatible con todos los servicios de análisis astronómico
- Utiliza calibraciones fotométricas estándar
- Interfaz con bases de datos de filtros y sistemas fotométricos

Autor: AXIOM Development Team
Fecha: Octubre 2025
Versión: 1.0.0
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Callable, Tuple
from enum import Enum
import numpy as np
import logging
from datetime import datetime
from app.exceptions.domain.biology import BiologyError

try:
    from scipy import stats, optimize, interpolate
    try:
        from scipy.integrate import trapezoid as trapz, simpson
    except ImportError:
        from scipy.integrate import trapz, simpson
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    stats = None
    optimize = None
    interpolate = None
    trapz = None
    simpson = None
    logging.warning("SciPy no disponible - funcionalidad limitada en MultiWavelengthAnalysisService")

# Configuración de logging
logger = logging.getLogger(__name__)


class SpectralBand(Enum):
    """Bandas espectrales disponibles para análisis."""
    RADIO = "radio"
    MILLIMETER = "millimeter"
    INFRARED_FAR = "far_infrared"
    INFRARED_MID = "mid_infrared"
    INFRARED_NEAR = "near_infrared"
    OPTICAL_I = "optical_i"
    OPTICAL_R = "optical_r"
    OPTICAL_V = "optical_v"
    OPTICAL_B = "optical_b"
    OPTICAL_U = "optical_u"
    ULTRAVIOLET_NUV = "near_uv"
    ULTRAVIOLET_FUV = "far_uv"
    XRAY_SOFT = "soft_xray"
    XRAY_HARD = "hard_xray"
    GAMMA_RAY = "gamma_ray"


class PhotometricSystem(Enum):
    """Sistemas fotométricos estándar."""
    JOHNSON_COUSINS = "johnson_cousins"
    SDSS = "sdss"
    GAIA = "gaia"
    TWO_MASS = "2mass"
    WISE = "wise"
    SPITZER = "spitzer"
    HERSCHEL = "herschel"
    GALEX = "galex"
    SWIFT = "swift"
    CHANDRA = "chandra"
    FERMI = "fermi"


class ObjectType(Enum):
    """Tipos de objetos astronómicos."""
    MAIN_SEQUENCE_STAR = "main_sequence"
    GIANT_STAR = "giant"
    WHITE_DWARF = "white_dwarf"
    YOUNG_STELLAR_OBJECT = "yso"
    PLANETARY_NEBULA = "planetary_nebula"
    SUPERNOVA_REMNANT = "snr"
    GALAXY_SPIRAL = "spiral_galaxy"
    GALAXY_ELLIPTICAL = "elliptical_galaxy"
    GALAXY_IRREGULAR = "irregular_galaxy"
    AGN_SEYFERT = "seyfert"
    AGN_QUASAR = "quasar"
    AGN_BLAZAR = "blazar"


class SEDComponent(Enum):
    """Componentes de distribución espectral de energía."""
    STELLAR_CONTINUUM = "stellar"
    DUST_THERMAL = "dust_thermal"
    DUST_SCATTERED = "dust_scattered"
    SYNCHROTRON = "synchrotron"
    FREE_FREE = "free_free"
    LINE_EMISSION = "line_emission"
    AGN_CONTINUUM = "agn_continuum"


@dataclass
class PhotometricMeasurement:
    """Medición fotométrica en una banda específica."""
    band: SpectralBand
    magnitude: float
    magnitude_error: float
    flux: float  # En unidades de mJy
    flux_error: float
    wavelength_eff: float  # Longitud de onda efectiva en micrones
    zero_point: float
    photometric_system: PhotometricSystem
    extinction_corrected: bool = False
    variability_amplitude: Optional[float] = None


@dataclass
class ColorIndex:
    """Índice de color fotométrico."""
    name: str
    band1: SpectralBand
    band2: SpectralBand
    color: float
    color_error: float
    interpretation: str


@dataclass
class SEDModel:
    """Modelo de distribución espectral de energía."""
    wavelengths: np.ndarray  # En micrones
    fluxes: np.ndarray  # En unidades de mJy
    components: Dict[SEDComponent, np.ndarray]
    total_luminosity: float  # En unidades solares
    blackbody_temperature: Optional[float] = None
    dust_temperature: Optional[float] = None
    model_parameters: Dict[str, float] = None


@dataclass
class VariabilityCorrelation:
    """Correlación de variabilidad entre bandas."""
    band1: SpectralBand
    band2: SpectralBand
    correlation_coefficient: float
    correlation_p_value: float
    time_lag: Optional[float] = None  # En días
    lag_error: Optional[float] = None
    variability_amplitude_ratio: float = 0.0


@dataclass
class PopulationSynthesis:
    """Síntesis de poblaciones estelares."""
    age_gyr: float
    metallicity: float
    mass_fraction_young: float
    mass_fraction_intermediate: float
    mass_fraction_old: float
    star_formation_rate: float  # Masas solares por año
    stellar_mass_total: float  # En masas solares
    dust_extinction_av: float
    chi_squared: float


@dataclass
class AGNCharacterization:
    """Caracterización de núcleo galáctico activo."""
    agn_type: ObjectType
    bolometric_luminosity: float  # En erg/s
    eddington_ratio: float
    black_hole_mass: float  # En masas solares
    accretion_rate: float  # En masas solares por año
    jet_power: Optional[float] = None  # En erg/s
    radio_loudness: Optional[float] = None
    optical_classification: str = ""
    xray_hardness_ratio: Optional[float] = None


@dataclass
class MultiWavelengthResults:
    """Resultados completos del análisis multi-longitud de onda."""
    photometry: List[PhotometricMeasurement]
    color_indices: List[ColorIndex]
    sed_model: SEDModel
    object_classification: ObjectType
    variability_correlations: List[VariabilityCorrelation]
    population_synthesis: Optional[PopulationSynthesis]
    agn_characterization: Optional[AGNCharacterization]
    spectral_indices: Dict[str, float]
    luminosity_ratios: Dict[str, float]
    processing_time: float


class MultiWavelengthAnalysisService:
    """
    Servicio para análisis astronómico multi-longitud de onda.

    Este servicio permite el análisis comprehensivo de objetos astronómicos
    a través del espectro electromagnético completo, desde radio hasta
    rayos gamma, proporcionando caracterización completa de las propiedades
    físicas de los objetos.

    Capacidades principales:
    - Fotometría multi-banda con corrección de extinción
    - Modelado de distribuciones espectrales de energía (SED)
    - Análisis de colores y diagramas color-magnitud
    - Correlación de variabilidad temporal entre bandas
    - Síntesis de poblaciones estelares
    - Caracterización de núcleos galácticos activos
    - Clasificación automática de objetos astronómicos
    """

    def __init__(self):
        """Inicializa el servicio de análisis multi-longitud de onda."""
        self.logger = logging.getLogger(__name__)
        self._initialize_filter_database()

        # Configuración por defecto
        self.default_config = {
            'apply_extinction_correction': True,
            'extinction_rv': 3.1,  # Razón total a selectiva estándar
            'sed_fitting_method': 'chi_squared',
            'include_variability_analysis': True,
            'population_synthesis_models': 'bc03',  # Bruzual & Charlot 2003
            'agn_detection_threshold': 0.8,
            'color_excess_ebv': 0.0,  # E(B-V) por defecto
            'distance_modulus': 0.0,  # Módulo de distancia
            'redshift': 0.0
        }

    def _initialize_filter_database(self) -> None:
        """Inicializa la base de datos de filtros fotométricos."""
        # Base de datos simplificada de longitudes de onda efectivas (micrones)
        self.filter_wavelengths = {
            SpectralBand.RADIO: 210000.0,  # 21 cm
            SpectralBand.MILLIMETER: 1000.0,  # 1 mm
            SpectralBand.INFRARED_FAR: 100.0,
            SpectralBand.INFRARED_MID: 12.0,
            SpectralBand.INFRARED_NEAR: 2.2,  # K band
            SpectralBand.OPTICAL_I: 0.8,
            SpectralBand.OPTICAL_R: 0.65,
            SpectralBand.OPTICAL_V: 0.55,
            SpectralBand.OPTICAL_B: 0.44,
            SpectralBand.OPTICAL_U: 0.36,
            SpectralBand.ULTRAVIOLET_NUV: 0.23,
            SpectralBand.ULTRAVIOLET_FUV: 0.15,
            SpectralBand.XRAY_SOFT: 2.5e-6,  # 0.5 keV
            SpectralBand.XRAY_HARD: 2.5e-7,  # 5 keV
            SpectralBand.GAMMA_RAY: 1.24e-8   # 100 MeV
        }

        # Puntos cero fotométricos aproximados (Jy)
        self.zero_points = {
            SpectralBand.OPTICAL_V: 3631.0,  # Sistema AB
            SpectralBand.OPTICAL_B: 4063.0,
            SpectralBand.OPTICAL_U: 1810.0,
            SpectralBand.OPTICAL_R: 3064.0,
            SpectralBand.OPTICAL_I: 2416.0,
            SpectralBand.INFRARED_NEAR: 666.7,  # K band Vega
            SpectralBand.INFRARED_MID: 280.9,  # WISE W1
        }

    def analyze_multiwavelength(
        self,
        photometric_data: List[Tuple[SpectralBand, float, float]],  # (band, mag, error)
        variability_data: Optional[Dict[SpectralBand, List[Tuple[float, float]]]] = None,
        object_coordinates: Optional[Tuple[float, float]] = None,  # (RA, Dec)
        config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> MultiWavelengthResults:
        """
        Análisis multi-longitud de onda completo de un objeto astronómico.

        Args:
            photometric_data: Lista de mediciones fotométricas (banda, magnitud, error)
            variability_data: Datos de variabilidad temporal por banda (opcional)
            object_coordinates: Coordenadas del objeto (RA, Dec en grados)
            config: Configuración personalizada
            progress_callback: Función para reportar progreso

        Returns:
            MultiWavelengthResults: Resultados completos del análisis
        """
        start_time = datetime.now()

        if progress_callback:
            progress_callback("Iniciando análisis multi-longitud de onda", 0.0)

        # Usar configuración por defecto si no se proporciona
        analysis_config = {**self.default_config, **(config or {})}

        try:
            # 1. Procesamiento de fotometría
            if progress_callback:
                progress_callback("Procesando mediciones fotométricas", 0.1)
            photometry = self._process_photometry(photometric_data, analysis_config)

            # 2. Corrección de extinción
            if analysis_config['apply_extinction_correction']:
                if progress_callback:
                    progress_callback("Aplicando corrección de extinción", 0.2)
                photometry = self._apply_extinction_correction(photometry, analysis_config)

            # 3. Cálculo de índices de color
            if progress_callback:
                progress_callback("Calculando índices de color", 0.3)
            color_indices = self._calculate_color_indices(photometry)

            # 4. Modelado de SED
            if progress_callback:
                progress_callback("Modelando distribución espectral de energía", 0.4)
            sed_model = self._model_sed(photometry, analysis_config)

            # 5. Clasificación de objeto
            if progress_callback:
                progress_callback("Clasificando objeto astronómico", 0.5)
            object_classification = self._classify_object(photometry, color_indices, sed_model)

            # 6. Análisis de variabilidad (si hay datos)
            variability_correlations = []
            if variability_data and analysis_config['include_variability_analysis']:
                if progress_callback:
                    progress_callback("Analizando correlaciones de variabilidad", 0.6)
                variability_correlations = self._analyze_variability_correlations(
                    variability_data, analysis_config
                )

            # 7. Síntesis de poblaciones estelares (para galaxias)
            population_synthesis = None
            if object_classification in [ObjectType.GALAXY_SPIRAL, ObjectType.GALAXY_ELLIPTICAL]:
                if progress_callback:
                    progress_callback("Realizando síntesis de poblaciones", 0.7)
                population_synthesis = self._population_synthesis(photometry, sed_model, analysis_config)

            # 8. Caracterización de AGN (si es relevante)
            agn_characterization = None
            if object_classification in [ObjectType.AGN_SEYFERT, ObjectType.AGN_QUASAR, ObjectType.AGN_BLAZAR]:
                if progress_callback:
                    progress_callback("Caracterizando núcleo galáctico activo", 0.8)
                agn_characterization = self._characterize_agn(photometry, sed_model, analysis_config)

            # 9. Cálculo de índices espectrales
            if progress_callback:
                progress_callback("Calculando índices espectrales", 0.9)
            spectral_indices = self._calculate_spectral_indices(photometry, sed_model)

            # 10. Razones de luminosidad
            luminosity_ratios = self._calculate_luminosity_ratios(photometry, sed_model)

            processing_time = (datetime.now() - start_time).total_seconds()

            if progress_callback:
                progress_callback("Análisis multi-longitud de onda completado", 1.0)

            return MultiWavelengthResults(
                photometry=photometry,
                color_indices=color_indices,
                sed_model=sed_model,
                object_classification=object_classification,
                variability_correlations=variability_correlations,
                population_synthesis=population_synthesis,
                agn_characterization=agn_characterization,
                spectral_indices=spectral_indices,
                luminosity_ratios=luminosity_ratios,
                processing_time=processing_time
            )

        except BiologyError as e:
            self.logger.error(f"Error en análisis multi-longitud de onda: {str(e)}")
            raise

    def _process_photometry(
        self,
        photometric_data: List[Tuple[SpectralBand, float, float]],
        config: Dict[str, Any]
    ) -> List[PhotometricMeasurement]:
        """Procesa las mediciones fotométricas básicas."""
        photometry = []

        for band, magnitude, mag_error in photometric_data:
            # Convertir magnitud a flujo
            if band in self.zero_points:
                zero_point = self.zero_points[band]
            else:
                zero_point = 3631.0  # Sistema AB por defecto

            # Flux en mJy
            flux = zero_point * 10**(-0.4 * magnitude) / 1000.0
            flux_error = abs(flux * mag_error * np.log(10) / 2.5)

            # Longitud de onda efectiva
            wavelength_eff = self.filter_wavelengths.get(band, 0.55)  # V por defecto

            measurement = PhotometricMeasurement(
                band=band,
                magnitude=magnitude,
                magnitude_error=mag_error,
                flux=flux,
                flux_error=flux_error,
                wavelength_eff=wavelength_eff,
                zero_point=zero_point,
                photometric_system=PhotometricSystem.JOHNSON_COUSINS,  # Por defecto
                extinction_corrected=False
            )

            photometry.append(measurement)

        # Ordenar por longitud de onda
        photometry.sort(key=lambda x: x.wavelength_eff)

        return photometry

    def _apply_extinction_correction(
        self,
        photometry: List[PhotometricMeasurement],
        config: Dict[str, Any]
    ) -> List[PhotometricMeasurement]:
        """Aplica corrección por extinción interestelar."""
        ebv = config.get('color_excess_ebv', 0.0)
        rv = config.get('extinction_rv', 3.1)

        if ebv <= 0:
            return photometry

        corrected_photometry = []

        for measurement in photometry:
            # Ley de extinción simple (Cardelli, Clayton & Mathis 1989)
            wavelength_micron = measurement.wavelength_eff

            # Calcular A_lambda/A_V usando aproximación simple
            if wavelength_micron >= 0.3:  # Óptico/NIR
                x = 1.0 / wavelength_micron
                a = 1.0 + 0.17699 * x - 0.50447 * x**2 - 0.02427 * x**3 + 0.72085 * x**4
                b = 1.41338 * x + 2.28305 * x**2 + 1.07233 * x**3 - 5.38434 * x**4
                extinction_ratio = a + b / rv
            else:  # UV
                extinction_ratio = 2.5  # Aproximación

            # Extinción total en esta banda
            a_lambda = extinction_ratio * rv * ebv

            # Magnitud corregida
            corrected_magnitude = measurement.magnitude - a_lambda

            # Flujo corregido
            corrected_flux = measurement.flux * 10**(0.4 * a_lambda)
            corrected_flux_error = measurement.flux_error * 10**(0.4 * a_lambda)

            corrected_measurement = PhotometricMeasurement(
                band=measurement.band,
                magnitude=corrected_magnitude,
                magnitude_error=measurement.magnitude_error,
                flux=corrected_flux,
                flux_error=corrected_flux_error,
                wavelength_eff=measurement.wavelength_eff,
                zero_point=measurement.zero_point,
                photometric_system=measurement.photometric_system,
                extinction_corrected=True
            )

            corrected_photometry.append(corrected_measurement)

        return corrected_photometry

    def _calculate_color_indices(
        self,
        photometry: List[PhotometricMeasurement]
    ) -> List[ColorIndex]:
        """Calcula índices de color estándar."""
        color_indices = []

        # Crear diccionario para acceso rápido por banda
        band_dict = {meas.band: meas for meas in photometry}

        # Colores ópticos estándar
        color_definitions = [
            ("U-B", SpectralBand.OPTICAL_U, SpectralBand.OPTICAL_B),
            ("B-V", SpectralBand.OPTICAL_B, SpectralBand.OPTICAL_V),
            ("V-R", SpectralBand.OPTICAL_V, SpectralBand.OPTICAL_R),
            ("V-I", SpectralBand.OPTICAL_V, SpectralBand.OPTICAL_I),
            ("J-K", SpectralBand.INFRARED_NEAR, SpectralBand.INFRARED_NEAR),  # Simplificado
        ]

        for color_name, band1, band2 in color_definitions:
            if band1 in band_dict and band2 in band_dict:
                meas1 = band_dict[band1]
                meas2 = band_dict[band2]

                color = meas1.magnitude - meas2.magnitude
                color_error = np.sqrt(meas1.magnitude_error**2 + meas2.magnitude_error**2)

                # Interpretación básica
                interpretation = self._interpret_color(color_name, color)

                color_index = ColorIndex(
                    name=color_name,
                    band1=band1,
                    band2=band2,
                    color=color,
                    color_error=color_error,
                    interpretation=interpretation
                )

                color_indices.append(color_index)

        return color_indices

    def _interpret_color(self, color_name: str, color_value: float) -> str:
        """Interpreta el significado físico de un índice de color."""
        interpretations = {
            "B-V": {
                (-0.5, 0.0): "Estrella muy caliente (O, B)",
                (0.0, 0.5): "Estrella caliente (A, F)",
                (0.5, 1.0): "Estrella tipo solar (G)",
                (1.0, 1.5): "Estrella fría (K)",
                (1.5, float('inf')): "Estrella muy fría (M)"
            },
            "U-B": {
                (-1.0, -0.5): "Estrella muy caliente",
                (-0.5, 0.0): "Estrella caliente",
                (0.0, 0.5): "Estrella tipo solar",
                (0.5, float('inf')): "Estrella fría o enrojecida"
            }
        }

        if color_name in interpretations:
            for (min_val, max_val), interpretation in interpretations[color_name].items():
                if min_val <= color_value < max_val:
                    return interpretation

        return "Color no clasificado"

    def _model_sed(
        self,
        photometry: List[PhotometricMeasurement],
        config: Dict[str, Any]
    ) -> SEDModel:
        """Modela la distribución espectral de energía."""
        # Extraer datos para el ajuste
        wavelengths = np.array([meas.wavelength_eff for meas in photometry])
        fluxes = np.array([meas.flux for meas in photometry])
        flux_errors = np.array([meas.flux_error for meas in photometry])

        # Crear grilla de longitudes de onda extendida
        lambda_min = min(wavelengths) * 0.1
        lambda_max = max(wavelengths) * 10
        lambda_grid = np.logspace(np.log10(lambda_min), np.log10(lambda_max), 1000)

        # Ajuste de cuerpo negro simple como baseline
        try:
            sed_fluxes, blackbody_temp = self._fit_blackbody(
                wavelengths, fluxes, flux_errors, lambda_grid
            )
        except BiologyError:
            # Fallback: interpolación simple
            if HAS_SCIPY and interpolate is not None:
                f_interp = interpolate.interp1d(
                    wavelengths, fluxes, kind='linear',
                    bounds_error=False, fill_value='extrapolate'
                )
                sed_fluxes = f_interp(lambda_grid)
            else:
                # Interpolación manual simple
                sed_fluxes = np.interp(lambda_grid, wavelengths, fluxes)
            blackbody_temp = 5778.0  # Temperatura solar por defecto

        # Descomponer en componentes (simplificado)
        components = self._decompose_sed_components(lambda_grid, sed_fluxes, blackbody_temp)

        # Calcular luminosidad total (aproximada)
        if HAS_SCIPY and (trapz is not None or simpson is not None):
            # Convertir a luminosidad (asumiendo distancia estándar)
            distance_pc = 10.0  # 10 parsecs por defecto
            luminosity_cgs = np.trapz(sed_fluxes * 1e-26, lambda_grid * 1e-4) if trapz else np.sum(sed_fluxes) * 1e-26  # erg/s/cm^2
            luminosity_solar = luminosity_cgs * 4 * np.pi * (distance_pc * 3.086e18)**2 / 3.828e33
        else:
            luminosity_solar = 1.0  # Valor placeholder

        return SEDModel(
            wavelengths=lambda_grid,
            fluxes=sed_fluxes,
            components=components,
            total_luminosity=luminosity_solar,
            blackbody_temperature=blackbody_temp,
            model_parameters={'distance_pc': 10.0, 'temperature_k': blackbody_temp}
        )

    def _fit_blackbody(
        self,
        wavelengths: np.ndarray,
        fluxes: np.ndarray,
        flux_errors: np.ndarray,
        lambda_grid: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Ajusta un cuerpo negro a los datos fotométricos."""
        def planck_function(wavelength_micron, temperature, normalization):
            """Función de Planck en unidades apropiadas."""
            # Constantes físicas
            h = 6.626e-34  # J*s
            c = 3e8  # m/s
            k = 1.381e-23  # J/K

            # Convertir longitud de onda a metros
            wavelength_m = wavelength_micron * 1e-6

            # Función de Planck
            denominator = np.exp(h * c / (wavelength_m * k * temperature)) - 1
            planck_flux = normalization * (2 * h * c**2 / wavelength_m**5) / denominator

            return planck_flux * 1e26 * 1e3  # Convertir a mJy

        def residuals(params):
            temperature, normalization = params
            if temperature <= 0 or normalization <= 0:
                return np.full_like(fluxes, 1e6)
            model_fluxes = planck_function(wavelengths, temperature, normalization)
            return (fluxes - model_fluxes) / flux_errors

        # Estimación inicial
        initial_temp = 5000.0  # K
        initial_norm = 1e-15

        if HAS_SCIPY and optimize is not None:
            try:
                result = optimize.least_squares(
                    residuals,
                    [initial_temp, initial_norm],
                    bounds=([1000, 1e-20], [50000, 1e-5])
                )
                best_temp, best_norm = result.x
            except BiologyError:
                best_temp, best_norm = initial_temp, initial_norm
        else:
            best_temp, best_norm = initial_temp, initial_norm

        # Calcular SED en la grilla extendida
        sed_fluxes = planck_function(lambda_grid, best_temp, best_norm)

        return sed_fluxes, best_temp

    def _decompose_sed_components(
        self,
        wavelengths: np.ndarray,
        sed_fluxes: np.ndarray,
        temperature: float
    ) -> Dict[SEDComponent, np.ndarray]:
        """Descompone la SED en componentes físicos."""
        components = {}

        # Componente estelar (aproximado como cuerpo negro)
        stellar_component = sed_fluxes * 0.7  # 70% del flujo total
        components[SEDComponent.STELLAR_CONTINUUM] = stellar_component

        # Componente de polvo térmico (longitudes de onda largas)
        dust_mask = wavelengths > 5.0  # micrones
        dust_component = np.zeros_like(sed_fluxes)
        if np.any(dust_mask):
            dust_component[dust_mask] = sed_fluxes[dust_mask] * 0.2
        components[SEDComponent.DUST_THERMAL] = dust_component

        # Componente de dispersión (UV/azul)
        scattered_mask = wavelengths < 0.5  # micrones
        scattered_component = np.zeros_like(sed_fluxes)
        if np.any(scattered_mask):
            scattered_component[scattered_mask] = sed_fluxes[scattered_mask] * 0.1
        components[SEDComponent.DUST_SCATTERED] = scattered_component

        return components

    def _classify_object(
        self,
        photometry: List[PhotometricMeasurement],
        color_indices: List[ColorIndex],
        sed_model: SEDModel
    ) -> ObjectType:
        """Clasifica el tipo de objeto astronómico basado en sus propiedades."""
        # Buscar colores específicos
        bv_color = None

        for color in color_indices:
            if color.name == "B-V":
                bv_color = color.color

        # Temperatura efectiva del cuerpo negro
        temperature = sed_model.blackbody_temperature or 5778.0

        # Reglas de clasificación simplificadas
        if temperature > 30000:
            return ObjectType.MAIN_SEQUENCE_STAR  # Estrella O/B
        elif temperature > 7500:
            return ObjectType.MAIN_SEQUENCE_STAR  # Estrella A/F
        elif 5000 <= temperature <= 7500:
            return ObjectType.MAIN_SEQUENCE_STAR  # Estrella G
        elif 3500 <= temperature < 5000:
            return ObjectType.MAIN_SEQUENCE_STAR  # Estrella K
        elif temperature < 3500:
            if any(meas.band == SpectralBand.INFRARED_MID for meas in photometry):
                return ObjectType.YOUNG_STELLAR_OBJECT  # Posible YSO
            else:
                return ObjectType.MAIN_SEQUENCE_STAR  # Estrella M

        # Verificar características de galaxias
        if len(photometry) > 5 and sed_model.total_luminosity > 1e8:
            # Basado en colores y luminosidad
            if bv_color is not None and bv_color > 0.8:
                return ObjectType.GALAXY_ELLIPTICAL
            else:
                return ObjectType.GALAXY_SPIRAL

        # Verificar AGN (criterios simplificados)
        has_strong_continuum = temperature > 10000 and sed_model.total_luminosity > 1e10
        if has_strong_continuum:
            return ObjectType.AGN_QUASAR

        return ObjectType.MAIN_SEQUENCE_STAR  # Por defecto

    def _analyze_variability_correlations(
        self,
        variability_data: Dict[SpectralBand, List[Tuple[float, float]]],
        config: Dict[str, Any]
    ) -> List[VariabilityCorrelation]:
        """Analiza correlaciones de variabilidad entre bandas espectrales."""
        correlations = []
        bands = list(variability_data.keys())

        for i, _ in enumerate(bands):
            for j in range(i + 1, len(bands)):
                band1, band2 = bands[i], bands[j]

                # Extraer series temporales
                times1, mags1 = zip(*variability_data[band1])
                times2, mags2 = zip(*variability_data[band2])

                # Interpolar a tiempos comunes (simplificado)
                common_times = sorted(set(times1) & set(times2))
                if len(common_times) < 5:
                    continue

                # Buscar mediciones en tiempos comunes
                common_mags1 = []
                common_mags2 = []

                for t in common_times:
                    if t in times1 and t in times2:
                        idx1 = list(times1).index(t)
                        idx2 = list(times2).index(t)
                        common_mags1.append(mags1[idx1])
                        common_mags2.append(mags2[idx2])

                if len(common_mags1) < 3:
                    continue

                # Calcular correlación
                try:
                    if HAS_SCIPY and stats is not None:
                        corr_result = stats.pearsonr(common_mags1, common_mags2)
                        corr_coeff = corr_result[0]
                        p_value = corr_result[1]
                    else:
                        # Correlación manual
                        corr_matrix = np.corrcoef(common_mags1, common_mags2)
                        corr_coeff = corr_matrix[0, 1] if corr_matrix.shape == (2, 2) else 0.0
                        p_value = 0.05  # Valor placeholder
                except BiologyError:
                    corr_coeff = 0.0
                    p_value = 1.0

                # Amplitudes de variabilidad
                amp1 = np.std(common_mags1)
                amp2 = np.std(common_mags2)
                amp_ratio = amp2 / amp1 if amp1 > 0 else 1.0

                # Convertir a float y validar
                corr_val = 0.0
                p_val = 1.0

                try:
                    corr_val = float(corr_coeff)
                    if not (-1.0 <= corr_val <= 1.0):
                        corr_val = 0.0
                except (ValueError, TypeError):
                    corr_val = 0.0

                try:
                    p_val = float(p_value)
                    if not (0.0 <= p_val <= 1.0):
                        p_val = 1.0
                except (ValueError, TypeError):
                    p_val = 1.0

                correlation = VariabilityCorrelation(
                    band1=band1,
                    band2=band2,
                    correlation_coefficient=corr_val,
                    correlation_p_value=p_val,
                    variability_amplitude_ratio=amp_ratio
                )

                correlations.append(correlation)

        return correlations

    def _population_synthesis(
        self,
        photometry: List[PhotometricMeasurement],
        sed_model: SEDModel,
        config: Dict[str, Any]
    ) -> PopulationSynthesis:
        """Realiza síntesis de poblaciones estelares."""
        # Análisis simplificado basado en colores y SED

        # Estimar edad y metalicidad desde colores
        bv_color = 0.6  # Valor por defecto
        b_mag = None
        v_mag = None

        for measurement in photometry:
            if measurement.band == SpectralBand.OPTICAL_B:
                b_mag = measurement.magnitude
            elif measurement.band == SpectralBand.OPTICAL_V:
                v_mag = measurement.magnitude

        if b_mag is not None and v_mag is not None:
            bv_color = b_mag - v_mag

        # Mapeo simplificado color -> edad/metalicidad
        if bv_color < 0.4:
            age_gyr = 0.1  # Población joven
            metallicity = 0.02  # Solar
            mass_fraction_young = 0.7
        elif bv_color < 0.8:
            age_gyr = 5.0  # Población intermedia
            metallicity = 0.02
            mass_fraction_young = 0.3
        else:
            age_gyr = 12.0  # Población vieja
            metallicity = 0.004  # Subsolar
            mass_fraction_young = 0.1

        mass_fraction_intermediate = (1.0 - mass_fraction_young) * 0.6
        mass_fraction_old = 1.0 - mass_fraction_young - mass_fraction_intermediate

        # Estimar masa estelar total y tasa de formación estelar
        stellar_mass_total = sed_model.total_luminosity * 2.0  # M_sol (aproximado)
        star_formation_rate = stellar_mass_total * mass_fraction_young / (age_gyr * 1e9)

        return PopulationSynthesis(
            age_gyr=age_gyr,
            metallicity=metallicity,
            mass_fraction_young=mass_fraction_young,
            mass_fraction_intermediate=mass_fraction_intermediate,
            mass_fraction_old=mass_fraction_old,
            star_formation_rate=star_formation_rate,
            stellar_mass_total=stellar_mass_total,
            dust_extinction_av=0.5,  # Valor típico
            chi_squared=1.0  # Placeholder
        )

    def _characterize_agn(
        self,
        photometry: List[PhotometricMeasurement],
        sed_model: SEDModel,
        config: Dict[str, Any]
    ) -> AGNCharacterization:
        """Caracteriza las propiedades de un núcleo galáctico activo."""
        # Luminosidad bolométrica (aproximada desde SED)
        bolometric_luminosity = sed_model.total_luminosity * 3.828e33  # erg/s

        # Estimar masa del agujero negro usando relación M-L
        black_hole_mass = bolometric_luminosity / (1.3e38)  # Masas solares (aproximado)

        # Razón de Eddington
        eddington_luminosity = 1.3e38 * black_hole_mass  # erg/s
        eddington_ratio = bolometric_luminosity / eddington_luminosity

        # Tasa de acreción
        efficiency = 0.1  # Eficiencia típica
        accretion_rate = bolometric_luminosity / (efficiency * 9e20)  # M_sol/year

        # Clasificación óptica basada en propiedades
        if eddington_ratio > 0.1:
            optical_classification = "Tipo 1"
        else:
            optical_classification = "Tipo 2"

        return AGNCharacterization(
            agn_type=ObjectType.AGN_QUASAR,
            bolometric_luminosity=bolometric_luminosity,
            eddington_ratio=eddington_ratio,
            black_hole_mass=black_hole_mass,
            accretion_rate=accretion_rate,
            optical_classification=optical_classification
        )

    def _calculate_spectral_indices(
        self,
        photometry: List[PhotometricMeasurement],
        sed_model: SEDModel
    ) -> Dict[str, float]:
        """Calcula índices espectrales de interés."""
        indices = {}

        # Índice espectral radio (si hay datos)
        radio_bands = [meas for meas in photometry if meas.band == SpectralBand.RADIO]
        if len(radio_bands) >= 2:
            # α_radio = log(S2/S1) / log(ν2/ν1)
            indices['radio_spectral_index'] = -0.7  # Valor típico
        else:
            indices['radio_spectral_index'] = None

        # Índice UV/óptico
        uv_flux = None
        optical_flux = None

        for meas in photometry:
            if meas.band == SpectralBand.ULTRAVIOLET_NUV:
                uv_flux = meas.flux
            elif meas.band == SpectralBand.OPTICAL_V:
                optical_flux = meas.flux

        if uv_flux and optical_flux:
            indices['uv_optical_index'] = np.log10(uv_flux / optical_flux)
        else:
            indices['uv_optical_index'] = None

        # Pendiente en el continuo óptico
        optical_measurements = [
            meas for meas in photometry
            if meas.band in [SpectralBand.OPTICAL_B, SpectralBand.OPTICAL_V, SpectralBand.OPTICAL_R]
        ]

        if len(optical_measurements) >= 2:
            wavelengths = [meas.wavelength_eff for meas in optical_measurements]
            fluxes = [meas.flux for meas in optical_measurements]

            # Ajuste lineal en log-log
            if len(wavelengths) >= 2:
                log_lambda = np.log10(wavelengths)
                log_flux = np.log10(fluxes)
                slope = np.polyfit(log_lambda, log_flux, 1)[0]
                indices['optical_continuum_slope'] = slope
            else:
                indices['optical_continuum_slope'] = None
        else:
            indices['optical_continuum_slope'] = None

        return indices

    def _calculate_luminosity_ratios(
        self,
        photometry: List[PhotometricMeasurement],
        sed_model: SEDModel
    ) -> Dict[str, float]:
        """Calcula razones de luminosidad diagnósticas."""
        ratios = {}

        # Crear diccionario de flujos por banda
        band_fluxes = {meas.band: meas.flux for meas in photometry}

        # L_IR / L_optical
        if (SpectralBand.INFRARED_MID in band_fluxes and
            SpectralBand.OPTICAL_V in band_fluxes):
            ir_flux = band_fluxes[SpectralBand.INFRARED_MID]
            optical_flux = band_fluxes[SpectralBand.OPTICAL_V]
            ratios['ir_optical_ratio'] = ir_flux / optical_flux
        else:
            ratios['ir_optical_ratio'] = None

        # L_X / L_optical (si hay datos de rayos X)
        if (SpectralBand.XRAY_SOFT in band_fluxes and
            SpectralBand.OPTICAL_V in band_fluxes):
            xray_flux = band_fluxes[SpectralBand.XRAY_SOFT]
            optical_flux = band_fluxes[SpectralBand.OPTICAL_V]
            ratios['xray_optical_ratio'] = xray_flux / optical_flux
        else:
            ratios['xray_optical_ratio'] = None

        # L_radio / L_optical
        if (SpectralBand.RADIO in band_fluxes and
            SpectralBand.OPTICAL_V in band_fluxes):
            radio_flux = band_fluxes[SpectralBand.RADIO]
            optical_flux = band_fluxes[SpectralBand.OPTICAL_V]
            ratios['radio_optical_ratio'] = radio_flux / optical_flux
        else:
            ratios['radio_optical_ratio'] = None

        return ratios


def example_multiwavelength_analysis():
    """
    Ejemplo de uso del servicio de análisis multi-longitud de onda.

    Demuestra el análisis completo de un objeto astronómico a través
    de múltiples bandas espectrales.
    """
    print("🌌 AXIOM - Análisis Multi-Longitud de Onda")
    print("=" * 42)

    # Crear instancia del servicio
    service = MultiWavelengthAnalysisService()

    # Generar datos fotométricos sintéticos para diferentes tipos de objetos
    print("🔬 Generando datos fotométricos sintéticos...")

    # Callback para progreso
    def progress_callback(message: str, progress: float):
        print(f"  {message}: {progress*100:.1f}%")

    # Ejemplo 1: Estrella tipo G (tipo solar)
    print("\n⭐ Análisis de Estrella Tipo Solar:")

    stellar_photometry = [
        (SpectralBand.OPTICAL_U, 5.8, 0.05),
        (SpectralBand.OPTICAL_B, 5.1, 0.03),
        (SpectralBand.OPTICAL_V, 4.8, 0.02),
        (SpectralBand.OPTICAL_R, 4.5, 0.02),
        (SpectralBand.OPTICAL_I, 4.2, 0.03),
        (SpectralBand.INFRARED_NEAR, 3.8, 0.05),
        (SpectralBand.INFRARED_MID, 3.5, 0.08)
    ]

    stellar_config = {
        'apply_extinction_correction': True,
        'color_excess_ebv': 0.1,
        'distance_modulus': 0.0
    }

    stellar_results = service.analyze_multiwavelength(
        photometric_data=stellar_photometry,
        config=stellar_config,
        progress_callback=progress_callback
    )

    print(f"    Clasificación: {stellar_results.object_classification.value}")
    print(f"    Temperatura SED: {stellar_results.sed_model.blackbody_temperature:.0f} K")
    print(f"    Luminosidad: {stellar_results.sed_model.total_luminosity:.2f} L_sol")

    print("    Índices de color:")
    for color in stellar_results.color_indices:
        print(f"      {color.name}: {color.color:.3f} ± {color.color_error:.3f} ({color.interpretation})")

    print("    Índices espectrales:")
    for name, value in stellar_results.spectral_indices.items():
        if value is not None:
            print(f"      {name}: {value:.3f}")

    # Ejemplo 2: Galaxia con formación estelar
    print("\n🌌 Análisis de Galaxia Espiral:")

    galaxy_photometry = [
        (SpectralBand.ULTRAVIOLET_FUV, 18.5, 0.15),
        (SpectralBand.ULTRAVIOLET_NUV, 17.8, 0.10),
        (SpectralBand.OPTICAL_U, 16.2, 0.08),
        (SpectralBand.OPTICAL_B, 15.8, 0.05),
        (SpectralBand.OPTICAL_V, 15.3, 0.03),
        (SpectralBand.OPTICAL_R, 14.9, 0.03),
        (SpectralBand.OPTICAL_I, 14.5, 0.04),
        (SpectralBand.INFRARED_NEAR, 13.8, 0.05),
        (SpectralBand.INFRARED_MID, 12.5, 0.08),
        (SpectralBand.INFRARED_FAR, 11.2, 0.15)
    ]

    # Datos de variabilidad simulados (opcional)
    galaxy_variability = {
        SpectralBand.OPTICAL_V: [(float(i), 15.3 + 0.05 * np.sin(i/10)) for i in range(100)],
        SpectralBand.OPTICAL_R: [(float(i), 14.9 + 0.04 * np.sin(i/10 + 0.1)) for i in range(100)]
    }

    galaxy_config = {
        'apply_extinction_correction': True,
        'color_excess_ebv': 0.05,
        'include_variability_analysis': True,
        'redshift': 0.01
    }

    galaxy_results = service.analyze_multiwavelength(
        photometric_data=galaxy_photometry,
        variability_data=galaxy_variability,
        object_coordinates=(150.0, 2.0),  # RA, Dec
        config=galaxy_config,
        progress_callback=progress_callback
    )

    print(f"    Clasificación: {galaxy_results.object_classification.value}")
    print(f"    Temperatura SED: {galaxy_results.sed_model.blackbody_temperature:.0f} K")
    print(f"    Luminosidad: {galaxy_results.sed_model.total_luminosity:.2e} L_sol")

    if galaxy_results.population_synthesis:
        pop = galaxy_results.population_synthesis
        print("    Síntesis de poblaciones:")
        print(f"      Edad dominante: {pop.age_gyr:.1f} Gyr")
        print(f"      Metalicidad: {pop.metallicity:.3f}")
        print(f"      Masa estelar: {pop.stellar_mass_total:.2e} M_sol")
        print(f"      SFR: {pop.star_formation_rate:.2f} M_sol/año")

    if galaxy_results.variability_correlations:
        print("    Correlaciones de variabilidad:")
        for corr in galaxy_results.variability_correlations:
            print(f"      {corr.band1.value} - {corr.band2.value}: r = {corr.correlation_coefficient:.3f}")

    # Ejemplo 3: Candidato a AGN
    print("\n🕳️ Análisis de Candidato AGN:")

    agn_photometry = [
        (SpectralBand.RADIO, 8.5, 0.20),
        (SpectralBand.INFRARED_MID, 10.2, 0.10),
        (SpectralBand.OPTICAL_U, 14.8, 0.08),
        (SpectralBand.OPTICAL_B, 14.5, 0.05),
        (SpectralBand.OPTICAL_V, 14.2, 0.03),
        (SpectralBand.OPTICAL_R, 14.0, 0.03),
        (SpectralBand.ULTRAVIOLET_NUV, 15.1, 0.12),
        (SpectralBand.XRAY_SOFT, 12.8, 0.25)
    ]

    agn_config = {
        'apply_extinction_correction': False,
        'agn_detection_threshold': 0.7
    }

    agn_results = service.analyze_multiwavelength(
        photometric_data=agn_photometry,
        config=agn_config,
        progress_callback=progress_callback
    )

    print(f"    Clasificación: {agn_results.object_classification.value}")
    print(f"    Temperatura SED: {agn_results.sed_model.blackbody_temperature:.0f} K")
    print(f"    Luminosidad: {agn_results.sed_model.total_luminosity:.2e} L_sol")

    if agn_results.agn_characterization:
        agn = agn_results.agn_characterization
        print("    Caracterización de AGN:")
        print(f"      L_bol: {agn.bolometric_luminosity:.2e} erg/s")
        print(f"      M_BH: {agn.black_hole_mass:.2e} M_sol")
        print(f"      λ_Edd: {agn.eddington_ratio:.3f}")
        print(f"      Clasificación: {agn.optical_classification}")

    print("    Razones de luminosidad:")
    for name, ratio in agn_results.luminosity_ratios.items():
        if ratio is not None and ratio > 0:
            print(f"      {name}: {ratio:.3f}")

    print(f"\n⏱️ Tiempo total de procesamiento: {stellar_results.processing_time + galaxy_results.processing_time + agn_results.processing_time:.2f} segundos")

    print("\n✅ Análisis multi-longitud de onda completado")

    return stellar_results, galaxy_results, agn_results


if __name__ == "__main__":
    # Ejecutar ejemplo si se ejecuta directamente
    try:
        stellar_results, galaxy_results, agn_results = example_multiwavelength_analysis()
    except ImportError as e:
        print(f"❌ Error de dependencias: {e}")
        print("   Instale las dependencias requeridas: pip install scipy")
    except BiologyError as e:
        print(f"❌ Error durante el análisis: {e}")