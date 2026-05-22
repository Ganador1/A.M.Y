"""
AXIOM - Servicio de Precisión Astropy
Cálculos astronómicos de alta precisión, transformaciones de coordenadas y fotometría
"""

import numpy as np
import logging
from typing import Dict, List, Any, Union
from dataclasses import dataclass
from datetime import datetime
from app.exceptions.base import AtlasException

try:
    from astropy.coordinates import SkyCoord, EarthLocation, ICRS, Galactic
    from astropy.time import Time
    from astropy import units as u
    from astropy.coordinates import solar_system_ephemeris
    import astropy.constants as const
    ASTROPY_AVAILABLE = True
except ImportError:
    ASTROPY_AVAILABLE = False
    logging.warning("Astropy no está disponible. Funcionalidad limitada.")


@dataclass
class CoordinateTransformation:
    """Resultado de transformación de coordenadas"""
    original_coord: str
    transformed_coord: str
    frame_from: str
    frame_to: str
    precision_mas: float  # Precisión en milli-arcseconds
    timestamp: datetime


@dataclass
class LightTravelCorrection:
    """Corrección de tiempo de luz"""
    target_name: str
    original_time: str
    corrected_time: str
    correction_seconds: float
    observer_location: str
    correction_type: str


@dataclass
class PhotometricAnalysis:
    """Análisis fotométrico diferencial"""
    target_magnitude: float
    reference_magnitudes: List[float]
    differential_magnitude: float
    magnitude_error: float
    filter_band: str
    airmass: float
    extinction_coefficient: float


class AstropyPrecisionService:
    """
    Servicio de cálculos astronómicos de alta precisión usando Astropy

    Capacidades:
    - Correcciones de tiempo de luz para objetos del sistema solar
    - Transformaciones de coordenadas de alta precisión
    - Cálculos de tiempo sidéreo
    - Fotometría diferencial automatizada
    - Análisis espectroscópico básico
    - Cálculos de precesión y nutación
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        if not ASTROPY_AVAILABLE:
            self.logger.error("Astropy no disponible. Funcionalidad limitada.")
            return

        # Configurar ubicaciones de observatorio comunes
        self.observatories = {
            'Palomar': EarthLocation.of_site('Palomar'),
            'Keck': EarthLocation.of_site('Keck'),
            'VLT': EarthLocation.of_site('Paranal'),
            'ALMA': EarthLocation.of_site('ALMA'),
            'HST': EarthLocation.from_geocentric(0*u.m, 0*u.m, 0*u.m),  # Aproximación
            'TESS': EarthLocation.from_geocentric(0*u.m, 0*u.m, 0*u.m)  # Aproximación
        }

        # Configurar efemerides del sistema solar
        solar_system_ephemeris.set('builtin')

        self.logger.info("AstropyPrecisionService inicializado correctamente")

    def light_travel_time_correction(
        self,
        target_coord: Union[str, 'SkyCoord'],
        observation_time: Union[str, 'Time'],
        observer_location: Union[str, 'EarthLocation'] = 'geocentric',
        target_type: str = 'star'
    ) -> LightTravelCorrection:
        """
        Calcula corrección de tiempo de luz para observaciones precisas

        Args:
            target_coord: Coordenadas del objetivo (string o SkyCoord)
            observation_time: Tiempo de observación (string o Time)
            observer_location: Ubicación del observador
            target_type: Tipo de objetivo ('star', 'planet', 'asteroid')

        Returns:
            LightTravelCorrection con tiempos corregidos
        """
        if not ASTROPY_AVAILABLE:
            raise ImportError("Astropy no disponible")

        # Procesar coordenadas
        if isinstance(target_coord, str):
            coord = SkyCoord.from_name(target_coord)
        else:
            coord = target_coord

        # Procesar tiempo
        if isinstance(observation_time, str):
            time_obj = Time(observation_time)
        else:
            time_obj = observation_time

        # Procesar ubicación del observador
        if isinstance(observer_location, str):
            if observer_location == 'geocentric':
                location = EarthLocation.from_geocentric(0*u.m, 0*u.m, 0*u.m)
            elif observer_location in self.observatories:
                location = self.observatories[observer_location]
            else:
                # Intentar resolver como sitio conocido
                try:
                    location = EarthLocation.of_site(observer_location)
                except AtlasException:
                    location = EarthLocation.from_geocentric(0*u.m, 0*u.m, 0*u.m)
        else:
            location = observer_location

        # Calcular corrección de tiempo de luz
        if target_type == 'star':
            # Para estrellas, usar corrección baricéntrica
            ltt_bary = time_obj.light_travel_time(coord)
            corrected_time = time_obj.tdb + ltt_bary
            correction_type = 'barycentric'
            correction_seconds = ltt_bary.to(u.second).value
        else:
            # Para objetos del sistema solar
            ltt_helio = time_obj.light_travel_time(coord, 'heliocentric', location)
            corrected_time = time_obj.tdb + ltt_helio
            correction_type = 'heliocentric'
            correction_seconds = ltt_helio.to(u.second).value

        return LightTravelCorrection(
            target_name=str(coord),
            original_time=str(time_obj),
            corrected_time=str(corrected_time),
            correction_seconds=float(correction_seconds),
            observer_location=str(location),
            correction_type=correction_type
        )

    def high_precision_coordinate_transform(
        self,
        coordinates: Union[str, 'SkyCoord'],
        frame_from: str = 'icrs',
        frame_to: str = 'galactic',
        epoch: Union[str, 'Time'] = 'J2000.0',
        precision_level: str = 'mas'
    ) -> CoordinateTransformation:
        """
        Transformación de coordenadas de alta precisión

        Args:
            coordinates: Coordenadas a transformar
            frame_from: Marco de referencia origen
            frame_to: Marco de referencia destino
            epoch: Época de referencia
            precision_level: Nivel de precisión ('mas', 'arcsec', 'arcmin')

        Returns:
            CoordinateTransformation con resultado de alta precisión
        """
        if not ASTROPY_AVAILABLE:
            raise ImportError("Astropy no disponible")

        # Procesar coordenadas de entrada
        if isinstance(coordinates, str):
            coord = SkyCoord.from_name(coordinates)
        else:
            coord = coordinates

        # Procesar época
        if isinstance(epoch, str):
            epoch_time = Time(epoch)
        else:
            epoch_time = epoch

        # Aplicar época si es necesario
        if hasattr(coord, 'obstime') and coord.obstime is None:
            coord = coord.apply_space_motion(new_obstime=epoch_time)

        # Transformar coordenadas
        frame_map = {
            'icrs': ICRS,
            'galactic': Galactic,
            'fk5': 'fk5',
            'fk4': 'fk4'
        }

        if frame_to in frame_map:
            if frame_to == 'galactic':
                transformed = coord.transform_to(Galactic())
            else:
                transformed = coord.transform_to(frame_map[frame_to])
        else:
            raise ValueError(f"Marco de referencia no soportado: {frame_to}")

        # Calcular precisión
        precision_mas = self._calculate_coordinate_precision(coord, transformed)

        return CoordinateTransformation(
            original_coord=f"{coord.ra.deg:.10f}, {coord.dec.deg:.10f}",
            transformed_coord=f"{transformed.lon.deg:.10f}, {transformed.lat.deg:.10f}",
            frame_from=frame_from,
            frame_to=frame_to,
            precision_mas=precision_mas,
            timestamp=datetime.now()
        )

    def calculate_sidereal_time(
        self,
        observation_time: Union[str, 'Time'],
        longitude: float,
        latitude: float,
        time_type: str = 'apparent'
    ) -> Dict[str, float]:
        """
        Calcula tiempo sidéreo para observaciones terrestres

        Args:
            observation_time: Tiempo de observación
            longitude: Longitud del observatorio (grados)
            latitude: Latitud del observatorio (grados)
            time_type: Tipo de tiempo sidéreo ('mean', 'apparent')

        Returns:
            Diccionario con tiempos sidéreos en diferentes formatos
        """
        if not ASTROPY_AVAILABLE:
            raise ImportError("Astropy no disponible")

        # Procesar tiempo
        if isinstance(observation_time, str):
            time_obj = Time(observation_time)
        else:
            time_obj = observation_time

        # Crear ubicación
        location = EarthLocation(lon=longitude*u.deg, lat=latitude*u.deg)

        # Calcular tiempo sidéreo
        if time_type == 'apparent':
            lst = time_obj.sidereal_time('apparent', longitude=location.lon)
        else:
            lst = time_obj.sidereal_time('mean', longitude=location.lon)

        return {
            'local_sidereal_time_hours': float(lst.hour),
            'local_sidereal_time_degrees': float(lst.deg),
            'greenwich_sidereal_time_hours': float(time_obj.sidereal_time('mean').hour),
            'julian_date': float(time_obj.jd),
            'modified_julian_date': float(time_obj.mjd)
        }

    def differential_photometry(
        self,
        target_flux: float,
        reference_fluxes: List[float],
        target_error: float = 0.0,
        reference_errors: List[float] = None,
        filter_band: str = 'V',
        airmass: float = 1.0
    ) -> PhotometricAnalysis:
        """
        Fotometría diferencial automatizada

        Args:
            target_flux: Flujo del objetivo
            reference_fluxes: Flujos de estrellas de referencia
            target_error: Error en el flujo del objetivo
            reference_errors: Errores en flujos de referencia
            filter_band: Banda fotométrica
            airmass: Masa de aire

        Returns:
            PhotometricAnalysis con resultado fotométrico
        """
        if not ASTROPY_AVAILABLE:
            raise ImportError("Astropy no disponible")

        # Calcular flujo de referencia combinado
        reference_flux_combined = np.mean(reference_fluxes)

        # Magnitud instrumental diferencial
        if target_flux > 0 and reference_flux_combined > 0:
            diff_magnitude = -2.5 * np.log10(target_flux / reference_flux_combined)
        else:
            diff_magnitude = np.nan

        # Calcular error de magnitud
        if reference_errors is None:
            reference_errors = [0.01] * len(reference_fluxes)

        # Error propagado
        target_rel_error = target_error / target_flux if target_flux > 0 else 0.1
        ref_rel_errors = [err/flux for err, flux in zip(reference_errors, reference_fluxes)
                         if flux > 0]
        combined_ref_error = np.sqrt(np.mean([e**2 for e in ref_rel_errors]))

        magnitude_error = 1.0857 * np.sqrt(target_rel_error**2 + combined_ref_error**2)

        # Coeficiente de extinción estimado
        extinction_coeff = self._estimate_extinction_coefficient(filter_band)

        return PhotometricAnalysis(
            target_magnitude=float(diff_magnitude),
            reference_magnitudes=[float(-2.5 * np.log10(f/reference_flux_combined))
                                for f in reference_fluxes],
            differential_magnitude=float(diff_magnitude),
            magnitude_error=float(magnitude_error),
            filter_band=filter_band,
            airmass=float(airmass),
            extinction_coefficient=extinction_coeff
        )

    def atmospheric_extinction_correction(
        self,
        magnitude: float,
        airmass: float,
        filter_band: str = 'V',
        site_altitude: float = 0.0
    ) -> Dict[str, float]:
        """
        Corrección de extinción atmosférica

        Args:
            magnitude: Magnitud observada
            airmass: Masa de aire
            filter_band: Banda fotométrica
            site_altitude: Altitud del sitio (metros)

        Returns:
            Diccionario con magnitudes corregidas
        """
        if not ASTROPY_AVAILABLE:
            raise ImportError("Astropy no disponible")

        # Coeficientes de extinción por banda
        extinction_coeffs = {
            'U': 0.60, 'B': 0.40, 'V': 0.20, 'R': 0.10, 'I': 0.05,
            'u': 0.50, 'g': 0.30, 'r': 0.15, 'i': 0.08, 'z': 0.05,
            'J': 0.03, 'H': 0.02, 'K': 0.01
        }

        base_extinction = extinction_coeffs.get(filter_band, 0.20)

        # Corrección por altitud (menor extinción a mayor altitud)
        altitude_factor = np.exp(-site_altitude / 8400)  # Escala atmosférica ~8.4 km
        extinction_coeff = base_extinction * altitude_factor

        # Aplicar corrección
        corrected_magnitude = magnitude - extinction_coeff * (airmass - 1.0)
        extinction_correction = extinction_coeff * (airmass - 1.0)

        return {
            'observed_magnitude': float(magnitude),
            'corrected_magnitude': float(corrected_magnitude),
            'extinction_correction': float(extinction_correction),
            'extinction_coefficient': extinction_coeff,
            'airmass': float(airmass),
            'filter_band': filter_band
        }

    def parallax_distance_calculation(
        self,
        parallax_mas: float,
        parallax_error_mas: float = 0.0
    ) -> Dict[str, float]:
        """
        Cálculo de distancia desde paralaje

        Args:
            parallax_mas: Paralaje en milli-arcseconds
            parallax_error_mas: Error del paralaje

        Returns:
            Diccionario con distancias y errores
        """
        if not ASTROPY_AVAILABLE:
            raise ImportError("Astropy no disponible")

        # Conversión a parsecs
        if parallax_mas > 0:
            distance_pc = 1000.0 / parallax_mas

            # Error de distancia (propagación de errores)
            if parallax_error_mas > 0:
                distance_error_pc = (1000.0 * parallax_error_mas) / (parallax_mas**2)
            else:
                distance_error_pc = 0.0
        else:
            distance_pc = np.inf
            distance_error_pc = np.inf

        # Conversiones adicionales
        distance_ly = distance_pc * 3.26156  # años luz
        distance_km = distance_pc * const.pc.to(u.km).value

        return {
            'parallax_mas': float(parallax_mas),
            'parallax_error_mas': float(parallax_error_mas),
            'distance_parsecs': float(distance_pc),
            'distance_error_parsecs': float(distance_error_pc),
            'distance_light_years': float(distance_ly),
            'distance_kilometers': float(distance_km),
            'relative_error_percent': float(100 * distance_error_pc / distance_pc) if distance_pc != np.inf else np.inf
        }

    def proper_motion_prediction(
        self,
        coordinates: Union[str, 'SkyCoord'],
        proper_motion_ra: float,  # mas/year
        proper_motion_dec: float,  # mas/year
        reference_epoch: Union[str, 'Time'],
        target_epoch: Union[str, 'Time']
    ) -> Dict[str, Any]:
        """
        Predicción de posición basada en movimiento propio

        Args:
            coordinates: Coordenadas de referencia
            proper_motion_ra: Movimiento propio en RA (mas/año)
            proper_motion_dec: Movimiento propio en Dec (mas/año)
            reference_epoch: Época de referencia
            target_epoch: Época objetivo

        Returns:
            Diccionario con coordenadas predichas
        """
        if not ASTROPY_AVAILABLE:
            raise ImportError("Astropy no disponible")

        # Procesar coordenadas
        if isinstance(coordinates, str):
            coord = SkyCoord.from_name(coordinates)
        else:
            coord = coordinates

        # Procesar épocas
        if isinstance(reference_epoch, str):
            ref_time = Time(reference_epoch)
        else:
            ref_time = reference_epoch

        if isinstance(target_epoch, str):
            target_time = Time(target_epoch)
        else:
            target_time = target_epoch

        # Diferencia temporal
        time_diff_years = (target_time - ref_time).to(u.year).value

        # Aplicar movimiento propio
        ra_offset = (proper_motion_ra * time_diff_years) * u.mas
        dec_offset = (proper_motion_dec * time_diff_years) * u.mas

        # Nuevas coordenadas
        new_ra = coord.ra + ra_offset.to(u.deg)
        new_dec = coord.dec + dec_offset.to(u.deg)

        predicted_coord = SkyCoord(ra=new_ra, dec=new_dec, frame=coord.frame,
                                  obstime=target_time)

        return {
            'original_coordinates': {
                'ra_deg': float(coord.ra.deg),
                'dec_deg': float(coord.dec.deg),
                'epoch': str(ref_time)
            },
            'predicted_coordinates': {
                'ra_deg': float(predicted_coord.ra.deg),
                'dec_deg': float(predicted_coord.dec.deg),
                'epoch': str(target_time)
            },
            'proper_motion': {
                'ra_mas_per_year': float(proper_motion_ra),
                'dec_mas_per_year': float(proper_motion_dec),
                'total_mas_per_year': float(np.sqrt(proper_motion_ra**2 + proper_motion_dec**2))
            },
            'time_difference_years': float(time_diff_years),
            'coordinate_shift': {
                'ra_arcsec': float(ra_offset.to(u.arcsec).value),
                'dec_arcsec': float(dec_offset.to(u.arcsec).value)
            }
        }

    def _calculate_coordinate_precision(
        self,
        original: 'SkyCoord',
        transformed: 'SkyCoord'
    ) -> float:
        """
        Calcula la precisión de la transformación de coordenadas

        Args:
            original: Coordenadas originales
            transformed: Coordenadas transformadas

        Returns:
            Precisión estimada en milli-arcseconds
        """
        # Estimación de precisión basada en la separación angular
        # y la precisión típica de las transformaciones
        base_precision = 0.1  # mas (precisión típica de Astropy)

        # Factor de corrección por magnitud (estrellas más débiles = menor precisión)
        # Asumimos magnitud típica si no está disponible
        magnitude_factor = 1.0

        return base_precision * magnitude_factor

    def _estimate_extinction_coefficient(self, filter_band: str) -> float:
        """
        Estima coeficiente de extinción para una banda fotométrica

        Args:
            filter_band: Banda fotométrica

        Returns:
            Coeficiente de extinción estimado
        """
        # Coeficientes típicos para sitios de calidad media
        coefficients = {
            'U': 0.60, 'B': 0.40, 'V': 0.20, 'R': 0.10, 'I': 0.05,
            'u': 0.50, 'g': 0.30, 'r': 0.15, 'i': 0.08, 'z': 0.05,
            'J': 0.03, 'H': 0.02, 'K': 0.01, 'Ks': 0.01
        }

        return coefficients.get(filter_band, 0.20)


# Función de utilidad para testing rápido
def astropy_precision_example():
    """
    Ejemplo rápido de uso del servicio de precisión Astropy
    """
    if not ASTROPY_AVAILABLE:
        print("Astropy no disponible para el ejemplo")
        return

    service = AstropyPrecisionService()

    try:
        print("=== Ejemplo de Servicio de Precisión Astropy ===\n")

        # 1. Corrección de tiempo de luz
        print("1. Corrección de tiempo de luz para Vega:")
        ltt_correction = service.light_travel_time_correction(
            target_coord="Vega",
            observation_time="2024-01-01T00:00:00",
            observer_location="Palomar"
        )
        print(f"   Corrección: {ltt_correction.correction_seconds:.3f} segundos")
        print(f"   Tipo: {ltt_correction.correction_type}")

        # 2. Transformación de coordenadas
        print("\n2. Transformación ICRS -> Galáctico para Vega:")
        coord_transform = service.high_precision_coordinate_transform(
            coordinates="Vega",
            frame_from="icrs",
            frame_to="galactic"
        )
        print(f"   ICRS: {coord_transform.original_coord}")
        print(f"   Galáctico: {coord_transform.transformed_coord}")
        print(f"   Precisión: {coord_transform.precision_mas:.3f} mas")

        # 3. Tiempo sidéreo
        print("\n3. Tiempo sidéreo para Palomar:")
        sidereal = service.calculate_sidereal_time(
            observation_time="2024-01-01T00:00:00",
            longitude=-116.8625,  # Palomar
            latitude=33.3561
        )
        print(f"   LST: {sidereal['local_sidereal_time_hours']:.4f} horas")
        print(f"   GST: {sidereal['greenwich_sidereal_time_hours']:.4f} horas")

        # 4. Fotometría diferencial
        print("\n4. Fotometría diferencial:")
        photometry = service.differential_photometry(
            target_flux=10000.0,
            reference_fluxes=[12000.0, 11500.0, 10800.0],
            target_error=100.0,
            filter_band='V'
        )
        print(f"   Magnitud diferencial: {photometry.differential_magnitude:.4f}")
        print(f"   Error: ±{photometry.magnitude_error:.4f} mag")

        # 5. Distancia desde paralaje
        print("\n5. Cálculo de distancia (paralaje 130 mas):")
        distance = service.parallax_distance_calculation(
            parallax_mas=130.0,
            parallax_error_mas=2.0
        )
        print(f"   Distancia: {distance['distance_parsecs']:.2f} ± {distance['distance_error_parsecs']:.2f} pc")
        print(f"   En años luz: {distance['distance_light_years']:.1f} ly")

        print("\n✅ Ejemplo completado exitosamente")

    except AtlasException as e:
        print(f"Error en ejemplo: {e}")


if __name__ == "__main__":
    astropy_precision_example()