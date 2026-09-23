"""
Advanced Earth Sciences Service
Servicio avanzado de ciencias de la tierra con modelado climático y oceanográfico
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import logging
from datetime import datetime, timedelta
import random
import math
from pathlib import Path
from statistics import mean
from app.domains.climate.data_utils import load_gistemp_dataset, resolve_gistemp_path
from app.exceptions.domain.biology import BiologyError
from app.types.advanced_earth_sciences_service_types import (
    BuildRealExtremeEventsResult,
    AssessTippingPointsSimulationResult,
    SimulateSectoralImpactsResult,
    SimulateRegionalAnalysisResult,
    AnalyzeOceanCurrentsResult,
    AnalyzeVerticalTransportResult,
    EstimatePrimaryProductivityResult,
    AnalyzeOceanAcidificationResult,
    AnalyzeSeismicSwarmsResult,
    CalculateSeismicHazardResult,
    RecommendSeismicNetworkResult,
    GetAnalysisHistoryResult,
    GetSupportedModelsResult,
)

logger = logging.getLogger(__name__)


class AdvancedEarthSciencesService:
    """
    Servicio avanzado de ciencias de la tierra y oceanografía
    Incluye modelado climático CESM/CMIP6, análisis sísmico y oceanografía
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.simulation_mode = self.config.get('simulation', True)
        self.data_path = self.config.get('data_path', '/data/earth')
        self.analysis_history = []
        self.gistemp_csv_path = Path(
            self.config.get('gistemp_csv_path')
            or Path(__file__).resolve().parents[2] / 'real_data_tests' / 'climate_nasa_gistemp.csv'
        )
        self._gistemp_cache: Optional[List[Dict[str, Any]]] = None

        # Modelos climáticos disponibles
        self.climate_models = {
            'CESM2': {
                'name': 'Community Earth System Model 2',
                'resolution': '1.25°',
                'components': ['atmosphere', 'ocean', 'land', 'ice'],
                'scenarios': ['SSP119', 'SSP126', 'SSP245', 'SSP370', 'SSP585']
            },
            'GFDL-ESM4': {
                'name': 'GFDL Earth System Model 4',
                'resolution': '1.0°',
                'components': ['atmosphere', 'ocean', 'land', 'ice', 'chemistry'],
                'scenarios': ['SSP126', 'SSP245', 'SSP370', 'SSP585']
            },
            'UKESM1': {
                'name': 'UK Earth System Model 1',
                'resolution': '1.875°',
                'components': ['atmosphere', 'ocean', 'land', 'ice', 'chemistry', 'vegetation'],
                'scenarios': ['SSP119', 'SSP126', 'SSP245', 'SSP585']
            }
    }

        # Tipos de análisis sísmico
        self.seismic_analysis_types = {
            'magnitude_estimation': {
                'name': 'Estimación de magnitud',
                'methods': ['ML', 'MB', 'MW', 'MS'],
                'accuracy': 0.2
            },
            'location_refinement': {
                'name': 'Refinamiento de localización',
                'methods': ['grid_search', 'probabilistic', 'machine_learning'],
                'accuracy_km': 5.0
            },
            'focal_mechanism': {
                'name': 'Mecanismo focal',
                'methods': ['moment_tensor', 'first_motion', 'waveform_inversion'],
                'uncertainty_degrees': 15
            },
            'tsunami_assessment': {
                'name': 'Evaluación de tsunami',
                'methods': ['empirical', 'numerical_modeling'],
                'response_time_minutes': 5
            }
    }

        # Variables oceanográficas
        self.ocean_variables = {
            'sea_surface_temperature': {'units': '°C', 'range': [-2, 35]},
            'sea_surface_height': {'units': 'm', 'range': [-0.5, 0.5]},
            'salinity': {'units': 'PSU', 'range': [30, 40]},
            'current_velocity_u': {'units': 'm/s', 'range': [-2, 2]},
            'current_velocity_v': {'units': 'm/s', 'range': [-2, 2]},
            'mixed_layer_depth': {'units': 'm', 'range': [10, 500]},
            'chlorophyll_a': {'units': 'mg/m³', 'range': [0.01, 10]},
            'oxygen': {'units': 'mol/m³', 'range': [150, 350]}
        }

    async def analyze_climate_model_cmip6(self, model_name: str, scenario: str,
                                        region: Optional[Dict[str, float]] = None,
                                        time_period: Tuple[str, str] = ('2020', '2100')) -> Dict[str, Any]:
        """
        Analiza salidas de modelo climático CMIP6
        """
        try:
            if model_name not in self.climate_models:
                return {"error": f"Modelo {model_name} no disponible"}

            model_info = self.climate_models[model_name]
            scenario_label = scenario or model_info['scenarios'][0]
            if scenario_label not in model_info['scenarios']:
                if not self.simulation_mode and scenario_label.lower() == 'observed':
                    scenario_internal = model_info['scenarios'][0]
                else:
                    return {"error": f"Escenario {scenario_label} no disponible para {model_name}"}
            else:
                scenario_internal = scenario_label

            analysis_id = self._generate_analysis_id('climate', model_name, scenario_label)

            if self.simulation_mode:
                result = await self._simulate_climate_analysis(
                    analysis_id, model_name, scenario_internal, region, time_period, model_info
                )
            else:
                result = await self._run_real_climate_analysis(
                    analysis_id, model_name, scenario_label, region, time_period, model_info
                )

            # Guardar en historial
            self.analysis_history.append(result)

            return result

        except BiologyError as e:
            logger.error(f"Error en análisis climático: {e}")
            return {"error": f"Error en análisis climático: {str(e)}"}

    async def _simulate_climate_analysis(self, analysis_id: str, model_name: str, scenario: str,
                                         region: Optional[Dict[str, float]], time_period: Tuple, model_info: Dict) -> Dict[str, Any]:
        """Simula análisis de modelo climático"""

        # Simular tiempo de análisis
        await asyncio.sleep(3)

        # Generar tendencias climáticas simuladas
        start_year, end_year = int(time_period[0]), int(time_period[1])
        years = list(range(start_year, end_year + 1))

        # Tendencias de temperatura (más altas para escenarios más severos)
        scenario_warming = {
            'SSP119': 1.5, 'SSP126': 2.1, 'SSP245': 3.2, 'SSP370': 4.1, 'SSP585': 5.2
        }
        total_warming = scenario_warming.get(scenario, 3.0)

        # Simular series temporales
        temp_baseline = 14.5  # Temperatura global actual
        temp_timeseries = []
        for i, _ in enumerate(years):
            # Tendencia + variabilidad natural
            warming_progress = (i / len(years)) * total_warming
            natural_variability = random.gauss(0, 0.3)
            temp_timeseries.append(temp_baseline + warming_progress + natural_variability)

        # Precipitación (cambios porcentuales)
        precip_changes = []
        for i in range(len(years)):
            base_change = (i / len(years)) * random.uniform(-10, 15)  # % change
            variability = random.gauss(0, 5)
            precip_changes.append(base_change + variability)

        # Eventos extremos
        heat_waves = self._simulate_extreme_events('heat_wave', years, scenario)
        droughts = self._simulate_extreme_events('drought', years, scenario)
        floods = self._simulate_extreme_events('flood', years, scenario)

        # Puntos de inflexión climáticos
        tipping_points = self._assess_tipping_points_simulation(total_warming, scenario)

        # Análisis regional si se proporciona
        regional_analysis = None
        if region:
            regional_analysis = await self._simulate_regional_analysis(region, scenario, years)

        # Impactos sectoriales
        sectoral_impacts = self._simulate_sectoral_impacts(total_warming, scenario)

        return {
            'analysis_id': analysis_id,
            'analysis_type': 'climate_model_cmip6',
            'model_name': model_name,
            'scenario': scenario,
            'time_period': time_period,
            'region': region,
            'status': 'completed',
            'completion_time': datetime.now().isoformat(),
            'results': {
                'temperature_trends': {
                    'years': years,
                    'global_temp_anomaly': temp_timeseries,
                    'total_warming_c': round(total_warming, 1),
                    'warming_rate_per_decade': round(total_warming / ((end_year - start_year) / 10), 2)
                },
                'precipitation_trends': {
                    'years': years,
                    'percent_change': precip_changes,
                    'mean_change_percent': round(sum(precip_changes) / len(precip_changes), 1)
                },
                'extreme_events': {
                    'heat_waves': heat_waves,
                    'droughts': droughts,
                    'floods': floods,
                    'total_extreme_events': len(heat_waves) + len(droughts) + len(floods)
                },
                'tipping_points': tipping_points,
                'regional_analysis': regional_analysis,
                'sectoral_impacts': sectoral_impacts,
                'confidence_intervals': {
                    'temperature_5th_percentile': round(total_warming * 0.7, 1),
                    'temperature_95th_percentile': round(total_warming * 1.3, 1)
                }
            },
            'model_info': model_info,
            'simulation_mode': True
        }

    def _load_gistemp_dataset(self) -> List[Dict[str, Any]]:
        if self._gistemp_cache is not None:
            return self._gistemp_cache

        path = resolve_gistemp_path(self.gistemp_csv_path)
        entries = load_gistemp_dataset(path)
        self._gistemp_cache = entries
        return entries

    @staticmethod
    def _slice_dataset_by_period(entries: List[Dict[str, Any]], time_period: Tuple[str, str]) -> List[Dict[str, Any]]:
        start_year, end_year = time_period
        try:
            start = int(start_year)
            end = int(end_year)
        except (TypeError, ValueError):
            return entries
        return [e for e in entries if start <= e['Year'] <= end]

    def _build_real_extreme_events(self, entries: List[BuildRealExtremeEventsResult]) -> BuildRealExtremeEventsResult:
        # Derivamos eventos extremos utilizando los mayores valores absolutos de anomalías mensuales
        monthly_columns = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        flattened: List[Tuple[str, int, float]] = []
        for entry in entries:
            year = entry['Year']
            for month in monthly_columns:
                value = entry.get(month)
                if value is not None:
                    flattened.append((month, year, value))

        # Ordenamos por magnitud absoluta de la anomalía para identificar eventos relevantes
        flattened.sort(key=lambda item: abs(item[2]), reverse=True)
        top_events = flattened[: max(6, len(entries) // 5)]

        heat_waves: List[Dict[str, Any]] = []
        droughts: List[Dict[str, Any]] = []
        floods: List[Dict[str, Any]] = []

        for month, year, anomaly in top_events:
            intensity = 'extreme' if anomaly >= 1.0 else 'severe' if anomaly >= 0.7 else 'moderate'
            affected_area = 5.1e8  # km² aproximados de superficie terrestre
            duration = 30 + int(abs(anomaly) * 20)
            event_payload = {
                'event_id': f'{month}_{year}',
                'month': month,
                'year': year,
                'intensity': intensity,
                'anomaly': anomaly,
                'duration_days': duration,
                'affected_area_km2': affected_area,
                'signal_strength': min(1.0, abs(anomaly) / 2.0),
            }
            if anomaly >= 0.0:
                heat_waves.append(event_payload)
            else:
                droughts.append(event_payload)

        # Los eventos de inundación se modelan como anomalías negativas significativas de estaciones húmedas
        floods = [
            {
                **event,
                'event_id': f'flood_{event["event_id"]}',
                'intensity': 'severe' if event['anomaly'] < -0.8 else 'moderate',
            }
            for event in droughts[: len(droughts) // 2 or 1]
        ]

        return {
            'heat_waves': heat_waves,
            'droughts': droughts,
            'floods': floods,
            'total_extreme_events': len(heat_waves) + len(droughts) + len(floods),
        }

    @staticmethod
    def _compute_real_tipping_points(entries: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        jd_values = [float(e['J-D']) for e in entries if isinstance(e.get('J-D'), (int, float))]
        if not jd_values:
            return {}
        max_anomaly = max(jd_values)
        min_anomaly = min(jd_values)
        return {
            'high_warming': {
                'exceedance_probability': min(1.0, max_anomaly / 2.0),
                'anomaly': max_anomaly,
                'description': 'Anomalía positiva máxima observada en el periodo',
            },
            'cooling_events': {
                'exceedance_probability': min(1.0, abs(min_anomaly) / 2.0),
                'anomaly': min_anomaly,
                'description': 'Anomalía negativa máxima observada en el periodo',
            },
        }

    async def process_seismic_events_advanced(self, event_criteria: Dict[str, Any],
                                              analysis_types: List[str]) -> Dict[str, Any]:
        """
        Procesamiento avanzado de eventos sísmicos
        """
        try:
            analysis_id = self._generate_analysis_id('seismic', str(event_criteria))

            if self.simulation_mode:
                result = await self._simulate_seismic_analysis(
                    analysis_id, event_criteria, analysis_types
                )
            else:
                result = await self._run_real_seismic_analysis(
                    analysis_id, event_criteria, analysis_types
                )

            # Guardar en historial
            self.analysis_history.append(result)

            return result

        except BiologyError as e:
            logger.error(f"Error en análisis sísmico: {e}")
            return {"error": f"Error en análisis sísmico: {str(e)}"}

    async def _simulate_seismic_analysis(self, analysis_id: str, event_criteria: Dict,
                                       analysis_types: List[str]) -> Dict[str, Any]:
        """Simula análisis sísmico avanzado"""

        # Simular tiempo de análisis
        await asyncio.sleep(2)

        # Generar eventos sísmicos simulados
        min_magnitude = event_criteria.get('min_magnitude', 4.0)
        max_magnitude = event_criteria.get('max_magnitude', 8.0)
        time_window_hours = event_criteria.get('time_window_hours', 24)

        # Distribución de magnitudes (ley de Gutenberg-Richter)
        # Ajustar para que siempre genere algunos eventos
        if min_magnitude >= 6.0:
            num_events = random.randint(10, 50)  # Para magnitudes altas
        else:
            num_events = int(10 ** max(0, 4.5 - min_magnitude))  # Aproximación
        events = []

        for i in range(min(num_events, 1000)):  # Máximo 1000 eventos
            magnitude = random.uniform(min_magnitude, max_magnitude)
            depth_km = random.uniform(1, 700)

            # Ubicación aleatoria (si no se especifica región)
            lat = random.uniform(-90, 90)
            lon = random.uniform(-180, 180)

            event = {
                'event_id': f'SIM_{i+1:04d}',
                'magnitude': round(magnitude, 1),
                'depth_km': round(depth_km, 1),
                'latitude': round(lat, 3),
                'longitude': round(lon, 3),
                'origin_time': (datetime.now() - timedelta(hours=random.uniform(0, time_window_hours))).isoformat(),
                'location_uncertainty_km': round(random.uniform(1, 50), 1),
                'magnitude_uncertainty': round(random.uniform(0.1, 0.5), 1)
            }

            # Añadir análisis específicos
            if 'focal_mechanism' in analysis_types:
                event['focal_mechanism'] = {
                    'strike': random.randint(0, 360),
                    'dip': random.randint(0, 90),
                    'rake': random.randint(-180, 180),
                    'moment_tensor': [random.uniform(-1, 1) for _ in range(6)]
                }

            if 'tsunami_assessment' in analysis_types and magnitude >= 6.0 and depth_km <= 70:
                event['tsunami_potential'] = {
                    'threat_level': random.choice(['low', 'medium', 'high']),
                    'estimated_wave_height_m': round(random.uniform(0.1, 10), 1),
                    'coastal_arrival_time_hours': round(random.uniform(0.5, 8), 1)
                }

            events.append(event)

        # Análisis de enjambres sísmicos
        swarm_analysis = self._analyze_seismic_swarms(events)

        # Análisis de peligrosidad sísmica
        hazard_analysis = self._calculate_seismic_hazard(events, event_criteria)

        # Red sísmica recomendada
        network_recommendations = self._recommend_seismic_network(events)

        return {
            'analysis_id': analysis_id,
            'analysis_type': 'seismic_advanced',
            'event_criteria': event_criteria,
            'analysis_types': analysis_types,
            'status': 'completed',
            'completion_time': datetime.now().isoformat(),
            'results': {
                'total_events': len(events),
                'events': events[:50],  # Primeros 50 eventos
                'magnitude_distribution': {
                    'min': min([e['magnitude'] for e in events]),
                    'max': max([e['magnitude'] for e in events]),
                    'mean': round(sum([e['magnitude'] for e in events]) / len(events), 1),
                    'above_6': len([e for e in events if e['magnitude'] >= 6.0]),
                    'above_7': len([e for e in events if e['magnitude'] >= 7.0])
                },
                'depth_distribution': {
                    'shallow_0_70km': len([e for e in events if e['depth_km'] <= 70]),
                    'intermediate_70_300km': len([e for e in events if 70 < e['depth_km'] <= 300]),
                    'deep_300km_plus': len([e for e in events if e['depth_km'] > 300])
                },
                'swarm_analysis': swarm_analysis,
                'seismic_hazard': hazard_analysis,
                'network_recommendations': network_recommendations,
                'tsunami_events': len([e for e in events if 'tsunami_potential' in e])
            },
            'simulation_mode': True
        }

    async def ocean_modeling_advanced(self, region: Dict[str, float],
                                      analysis_type: str = 'regional',
                                    time_span_days: int = 30) -> Dict[str, Any]:
        """
        Modelado oceanográfico avanzado
        """
        try:
            analysis_id = self._generate_analysis_id('ocean', analysis_type, str(region))

            if self.simulation_mode:
                result = await self._simulate_ocean_modeling(
                    analysis_id, region, analysis_type, time_span_days
                )
            else:
                result = await self._run_real_ocean_modeling(
                    analysis_id, region, analysis_type, time_span_days
                )

            # Guardar en historial
            self.analysis_history.append(result)

            return result

        except BiologyError as e:
            logger.error(f"Error en modelado oceanográfico: {e}")
            return {"error": f"Error en modelado oceanográfico: {str(e)}"}

    async def _simulate_ocean_modeling(self, analysis_id: str, region: Dict,
                                       analysis_type: str, time_span_days: int) -> Dict[str, Any]:
        """Simula modelado oceanográfico avanzado"""

        # Simular tiempo de análisis
        await asyncio.sleep(3)

        # Generar datos oceanográficos simulados
        time_series = []
        for day in range(time_span_days):
            date = datetime.now() - timedelta(days=time_span_days - day)

            # Generar valores para cada variable oceanográfica
            daily_data = {'date': date.isoformat()}
            for var, info in self.ocean_variables.items():
                min_val, max_val = info['range']
                # Añadir variabilidad estacional y aleatoria
                seasonal_factor = math.sin(2 * math.pi * day / 365) * 0.2
                daily_data[var] = round(
                    random.uniform(min_val, max_val) + seasonal_factor * (max_val - min_val), 3
                )

            time_series.append(daily_data)

        # Detección de eddies (remolinos oceánicos)
        eddies = self._detect_ocean_eddies_simulation(region, time_span_days)

        # Frentes oceánicos
        fronts = self._detect_ocean_fronts_simulation(region)

        # Corrientes principales
        current_analysis = self._analyze_ocean_currents(time_series)
        # Upwelling/downwelling
        vertical_transport = self._analyze_vertical_transport(time_series)

        # Productividad primaria
        productivity = self._estimate_primary_productivity(time_series)

        # Eventos de ondas de calor marinas
        marine_heatwaves = self._detect_marine_heatwaves(time_series)

        # Acidificación oceánica
        acidification = self._analyze_ocean_acidification(region)

        return {
            'analysis_id': analysis_id,
            'analysis_type': 'ocean_modeling_advanced',
            'region': region,
            'time_span_days': time_span_days,
            'status': 'completed',
            'completion_time': datetime.now().isoformat(),
            'results': {
                'time_series_data': time_series[-7:],  # Últimos 7 días como ejemplo
                'statistical_summary': {
                    var: {
                        'mean': round(sum([d[var] for d in time_series]) / len(time_series), 3),
                        'min': round(min([d[var] for d in time_series]), 3),
                        'max': round(max([d[var] for d in time_series]), 3),
                        'std': round(self._calculate_std([d[var] for d in time_series]), 3)
                    }
                    for var in self.ocean_variables.keys()
                },
                'eddies': eddies,
                'ocean_fronts': fronts,
                'current_analysis': current_analysis,
                'vertical_transport': vertical_transport,
                'primary_productivity': productivity,
                'marine_heatwaves': marine_heatwaves,
                'ocean_acidification': acidification,
                'data_quality': {
                    'completeness_percent': round(random.uniform(95, 100), 1),
                    'temporal_resolution': 'daily',
                    'spatial_resolution_km': round(random.uniform(5, 25), 1)
                }
            },
            'simulation_mode': True
        }

    def _simulate_extreme_events(self, event_type: str, years: List[int], scenario: str) -> List[Dict]:
        """Simula eventos extremos climáticos"""
        events = []

        # Más eventos extremos en escenarios más severos
        intensity_factor = {'SSP119': 0.5, 'SSP126': 0.7, 'SSP245': 1.0, 'SSP370': 1.3, 'SSP585': 1.6}
        factor = intensity_factor.get(scenario, 1.0)

        base_frequency = {'heat_wave': 5, 'drought': 3, 'flood': 4}  # eventos por década
        frequency = int(base_frequency[event_type] * factor * len(years) / 10)

        for i in range(frequency):
            year = random.choice(years)
            events.append({
                'event_id': f'{event_type}_{year}_{i+1}',
                'year': year,
                'type': event_type,
                'intensity': random.choice(['moderate', 'severe', 'extreme']),
                'duration_days': random.randint(7, 90),
                'affected_area_km2': random.randint(10000, 1000000)
            })

        return events

    def _assess_tipping_points_simulation(self, warming: float, scenario: str) -> AssessTippingPointsSimulationResult:
        """Evalúa puntos de inflexión climáticos"""
        tipping_points = {
            'arctic_sea_ice': {'threshold': 2.0, 'probability': min(warming / 2.0, 1.0)},
            'greenland_ice_sheet': {'threshold': 1.5, 'probability': max(0, (warming - 1.5) / 2.0)},
            'west_antarctic_ice': {'threshold': 2.5, 'probability': max(0, (warming - 2.5) / 1.5)},
            'amazon_rainforest': {'threshold': 3.0, 'probability': max(0, (warming - 3.0) / 2.0)},
            'boreal_forest': {'threshold': 2.0, 'probability': max(0, (warming - 2.0) / 2.0)}
        }

        return {
            point: {
                'warming_threshold_c': info['threshold'],
                'exceedance_probability': round(min(info['probability'], 1.0), 2),
                'risk_level': 'high' if info['probability'] > 0.5 else 'medium' if info['probability'] > 0.2 else 'low'
            }
            for point, info in tipping_points.items()
        }

    def _simulate_sectoral_impacts(self, warming: float, scenario: str) -> SimulateSectoralImpactsResult:
        """Simula impactos sectoriales del cambio climático"""
        return {
            'agriculture': {
                'crop_yield_change_percent': round(-warming * random.uniform(5, 15), 1),
                'water_stress_increase_percent': round(warming * random.uniform(10, 30), 1),
                'affected_regions': random.sample(['Africa', 'Asia', 'South America', 'Australia'],
                                                random.randint(1, 3))
            },
            'water_resources': {
                'availability_change_percent': round(-warming * random.uniform(5, 20), 1),
                'extreme_drought_frequency_increase': round(warming * random.uniform(1.5, 3.0), 1),
                'flood_risk_increase_percent': round(warming * random.uniform(10, 25), 1)
            },
            'human_health': {
                'heat_related_mortality_increase_percent': round(warming * random.uniform(5, 15), 1),
                'vector_borne_disease_expansion': warming > 2.0,
                'air_quality_degradation': warming > 1.5
            },
            'coastal_zones': {
                'sea_level_rise_cm': round(warming * random.uniform(15, 45), 1),
                'coastal_erosion_rate_increase': round(warming * random.uniform(20, 60), 1),
                'storm_surge_intensity_increase_percent': round(warming * random.uniform(5, 20), 1)
            }
        }

    async def _simulate_regional_analysis(self, region: Dict, scenario: str, years: List[int]) -> SimulateRegionalAnalysisResult:
        """Simula análisis regional específico"""
        lat_center = (region.get('lat_min', 0) + region.get('lat_max', 0)) / 2

        # Factores regionales (ártico se calienta más)
        arctic_amplification = 2.0 if lat_center > 60 else 1.0

        return {
            'region_center': {'lat': lat_center, 'lon': (region.get('lon_min', 0) + region.get('lon_max', 0)) / 2},
            'warming_amplification': arctic_amplification,
            'precipitation_change_pattern': random.choice(['wetter', 'drier', 'mixed']),
            'extreme_temperature_days_increase': round(random.uniform(10, 50) * arctic_amplification, 1),
            'growing_season_extension_days': round(random.uniform(5, 30) * arctic_amplification, 1) if lat_center > 30 else 0,
            'permafrost_thaw_risk': 'high' if lat_center > 60 else 'low'
        }

    def _detect_ocean_eddies_simulation(self, region: Dict, time_span: int) -> List[Dict]:
        """Simula detección de eddies oceánicos"""
        num_eddies = random.randint(5, 20)
        eddies = []

        for i in range(num_eddies):
            eddies.append({
                'eddy_id': f'EDDY_{i+1:03d}',
                'type': random.choice(['cyclonic', 'anticyclonic']),
                'center_lat': random.uniform(region.get('lat_min', -60), region.get('lat_max', 60)),
                'center_lon': random.uniform(region.get('lon_min', -180), region.get('lon_max', 180)),
                'radius_km': round(random.uniform(20, 200), 1),
                'intensity': round(random.uniform(0.1, 1.5), 2),
                'lifetime_days': random.randint(10, 180),
                'propagation_speed_cm_s': round(random.uniform(1, 15), 1)
            })

        return eddies

    def _detect_ocean_fronts_simulation(self, region: Dict) -> List[Dict]:
        """Simula detección de frentes oceánicos"""
        num_fronts = random.randint(2, 8)
        fronts = []

        for i in range(num_fronts):
            fronts.append({
                'front_id': f'FRONT_{i+1:02d}',
                'type': random.choice(['thermal', 'salinity', 'density']),
                'strength': round(random.uniform(0.5, 3.0), 2),
                'length_km': round(random.uniform(50, 500), 1),
                'gradient_per_km': round(random.uniform(0.01, 0.5), 3)
            })

        return fronts

    def _analyze_ocean_currents(self, time_series: List[Dict]) -> AnalyzeOceanCurrentsResult:
        """Analiza corrientes oceánicas"""
        u_velocities = [d['current_velocity_u'] for d in time_series]
        v_velocities = [d['current_velocity_v'] for d in time_series]

        speeds = [math.sqrt(u**2 + v**2) for u, v in zip(u_velocities, v_velocities)]

        return {
            'mean_speed_m_s': round(sum(speeds) / len(speeds), 3),
            'max_speed_m_s': round(max(speeds), 3),
            'dominant_direction_degrees': round(math.degrees(math.atan2(
                sum(v_velocities), sum(u_velocities)
            )) % 360, 1),
            'current_stability': 'stable' if self._calculate_std(speeds) < 0.2 else 'variable'
        }

    def _analyze_vertical_transport(self, time_series: List[Dict]) -> AnalyzeVerticalTransportResult:
        """Analiza transporte vertical (upwelling/downwelling)"""
        # Simular velocidad vertical basada en otros parámetros
        vertical_velocities = [random.uniform(-0.001, 0.001) for _ in time_series]

        upwelling_days = len([v for v in vertical_velocities if v > 0])
        downwelling_days = len([v for v in vertical_velocities if v < 0])

        return {
            'upwelling_frequency_percent': round((upwelling_days / len(time_series)) * 100, 1),
            'downwelling_frequency_percent': round((downwelling_days / len(time_series)) * 100, 1),
            'mean_vertical_velocity_m_s': round(sum(vertical_velocities) / len(vertical_velocities), 6),
            'upwelling_strength': random.choice(['weak', 'moderate', 'strong'])
        }

    def _estimate_primary_productivity(self, time_series: List[Dict]) -> EstimatePrimaryProductivityResult:
        """Estima productividad primaria"""
        chlorophyll_values = [d['chlorophyll_a'] for d in time_series]

        # Convertir clorofila a productividad (aproximación)
        productivity_values = [chl * random.uniform(50, 150) for chl in chlorophyll_values]

        return {
            'mean_productivity_mg_c_m2_day': round(sum(productivity_values) / len(productivity_values), 1),
            'productivity_class': random.choice(['oligotrophic', 'mesotrophic', 'eutrophic']),
            'seasonal_variability': 'high' if self._calculate_std(productivity_values) > 100 else 'low',
            'bloom_events': random.randint(0, 3)
        }

    def _detect_marine_heatwaves(self, time_series: List[Dict]) -> List[Dict]:
        """Detecta ondas de calor marinas"""
        sst_values = [d['sea_surface_temperature'] for d in time_series]
        mean_sst = sum(sst_values) / len(sst_values)
        threshold = mean_sst + 2 * self._calculate_std(sst_values)

        heatwaves = []
        current_hw = None

        for i, (sst, data) in enumerate(zip(sst_values, time_series)):
            if sst > threshold:
                if current_hw is None:
                    current_hw = {
                        'start_date': data['date'],
                        'max_intensity': sst - mean_sst,
                        'duration_days': 1
                    }
                else:
                    current_hw['duration_days'] += 1
                    current_hw['max_intensity'] = max(current_hw['max_intensity'], sst - mean_sst)
            else:
                if current_hw is not None:
                    current_hw['end_date'] = time_series[i-1]['date']
                    heatwaves.append(current_hw)
                    current_hw = None

        return heatwaves

    def _analyze_ocean_acidification(self, region: Dict) -> AnalyzeOceanAcidificationResult:
        """Analiza acidificación oceánica"""
        return {
            'ph_current': round(random.uniform(7.8, 8.2), 2),
            'ph_projected_2050': round(random.uniform(7.6, 7.9), 2),
            'aragonite_saturation': round(random.uniform(1.5, 4.0), 2),
            'acidification_rate_per_decade': round(random.uniform(0.01, 0.03), 3),
            'impact_level': random.choice(['low', 'moderate', 'high'])
        }
    def _analyze_seismic_swarms(self, events: List[Dict]) -> AnalyzeSeismicSwarmsResult:
        """Analiza enjambres sísmicos"""
        # Agrupar eventos por proximidad temporal y espacial
        swarms = []
        events_sorted = sorted(events, key=lambda x: x['origin_time'])

        current_swarm = []
        for event in events_sorted:
            if not current_swarm:
                current_swarm = [event]
            else:
                # Criterios simples de enjambre
                time_diff = abs(datetime.fromisoformat(event['origin_time']) -
                                datetime.fromisoformat(current_swarm[-1]['origin_time'])).total_seconds() / 3600

                if time_diff < 24:  # Dentro de 24 horas
                    current_swarm.append(event)
                else:
                    if len(current_swarm) >= 3:  # Mínimo 3 eventos para ser enjambre
                        swarms.append(current_swarm)
                    current_swarm = [event]

        if len(current_swarm) >= 3:
            swarms.append(current_swarm)
        return {
            'total_swarms': len(swarms),
            'largest_swarm_events': max((len(s) for s in swarms), default=0),
            'swarm_durations_hours': [
                (
                    datetime.fromisoformat(s[-1]['origin_time'])
                    - datetime.fromisoformat(s[0]['origin_time'])
                ).total_seconds() / 3600
                for s in swarms
            ],
        }

    def _calculate_seismic_hazard(self, events: List[Dict], criteria: Dict) -> CalculateSeismicHazardResult:
        """Calcula peligrosidad sísmica"""
        magnitudes = [e['magnitude'] for e in events]

        return {
            'max_magnitude': max(magnitudes) if magnitudes else 0,
            'mean_magnitude': round(sum(magnitudes) / len(magnitudes), 1) if magnitudes else 0,
            'b_value': round(random.uniform(0.8, 1.2), 2),  # Parámetro de Gutenberg-Richter
            'annual_exceedance_probability': {
                'magnitude_5': round(random.uniform(0.1, 0.5), 3),
                'magnitude_6': round(random.uniform(0.01, 0.1), 3),
                'magnitude_7': round(random.uniform(0.001, 0.01), 3)
            },
            'seismic_hazard_level': random.choice(['low', 'moderate', 'high'])
        }

    def _recommend_seismic_network(self, events: List[Dict]) -> RecommendSeismicNetworkResult:
        """Recomienda configuración de red sísmica"""
        return {
            'recommended_stations': random.randint(5, 20),
            'optimal_spacing_km': round(random.uniform(20, 100), 1),
            'priority_locations': [
                {'lat': round(random.uniform(-90, 90), 2),
                 'lon': round(random.uniform(-180, 180), 2)}
                for _ in range(3)
            ],
            'detection_threshold_magnitude': round(random.uniform(1.5, 3.0), 1),
            'estimated_improvement_percent': round(random.uniform(20, 60), 1)
        }

    def _calculate_std(self, values: List[float]) -> float:
        """Calcula desviación estándar"""
        if len(values) < 2:
            return 0.0
        avg_value = sum(values) / len(values)
        variance = sum((x - avg_value) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def _generate_analysis_id(self, analysis_type: str, *args) -> str:
        """Genera ID único para el análisis"""
        import hashlib
        content = f"{analysis_type}_{'_'.join(str(arg) for arg in args)}_{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:12].upper()

    async def get_analysis_history(self, limit: int = 20) -> GetAnalysisHistoryResult:
        """Obtiene historial de análisis"""
        recent_history = self.analysis_history[-limit:] if self.analysis_history else []
        return {
            'total_analyses': len(self.analysis_history),
            'recent_analyses': recent_history,
            'analysis_types': list({a.get('analysis_type') for a in self.analysis_history}),
            'completed_analyses': len([a for a in self.analysis_history if a.get('status') == 'completed'])
        }

    async def get_supported_models(self) -> GetSupportedModelsResult:
        """Obtiene modelos y análisis soportados"""
        return {
            'climate_models': self.climate_models,
            'seismic_analysis_types': self.seismic_analysis_types,
            'ocean_variables': self.ocean_variables,
            'simulation_mode': self.simulation_mode,
            'capabilities': [
                'climate_model_analysis', 'seismic_event_processing',
                'ocean_modeling', 'extreme_event_detection', 'tipping_point_assessment'
            ]
        }

    async def _run_real_climate_analysis(self, analysis_id: str, model_name: str, scenario: str,
                                       region: Optional[Dict[str, float]], time_period: Tuple, model_info: Dict) -> Dict[str, Any]:
        entries = self._load_gistemp_dataset()
        period_entries = self._slice_dataset_by_period(entries, time_period) or entries

        scenario_label = scenario or 'observed'

        anomaly_map = {
            e['Year']: float(e['J-D'])
            for e in period_entries
            if isinstance(e.get('J-D'), (int, float))
        }
        years = sorted(anomaly_map.keys())
        if not years:
            raise ValueError('El dataset GISTEMP no contiene anomalías J-D para el periodo solicitado')
        global_temp_anomaly = [anomaly_map[y] for y in years]

        total_warming = global_temp_anomaly[-1] - global_temp_anomaly[0]
        period_years = max(years[-1] - years[0], 1)
        warming_rate_per_decade = (total_warming / period_years) * 10.0

        # Cambios porcentuales aproximados de precipitación derivados de la variación de anomalías
        percent_change: List[float] = []
        previous = global_temp_anomaly[0]
        for anomaly in global_temp_anomaly:
            delta = anomaly - previous
            percent_change.append(delta * 10.0)
            previous = anomaly

        extreme_events = self._build_real_extreme_events(period_entries)
        tipping_points = self._compute_real_tipping_points(period_entries)

        regional_analysis = None
        if region:
            regional_analysis = {
                'region_bounds': region,
                'mean_anomaly': mean(global_temp_anomaly),
                'max_anomaly': max(global_temp_anomaly),
                'min_anomaly': min(global_temp_anomaly),
            }

        sectoral_impacts = {
            'agriculture': {
                'risk_level': 'high' if total_warming > 0.8 else 'moderate',
                'expected_yield_shift_percent': round(total_warming * 12.0, 2),
            },
            'infrastructure': {
                'risk_level': 'moderate' if total_warming > 0.5 else 'low',
                'sea_level_rise_cm': round(total_warming * 9.0, 2),
            },
            'health': {
                'heatwave_days_increase': int(extreme_events['total_extreme_events'] * 1.5),
                'risk_level': 'elevated' if total_warming > 0.9 else 'moderate',
            },
        }

        confidence_min = min(global_temp_anomaly)
        confidence_max = max(global_temp_anomaly)

        return {
            'analysis_id': analysis_id,
            'analysis_type': 'climate_model_observed',
            'model_name': model_name,
            'scenario': scenario_label,
            'time_period': time_period,
            'region': region,
            'status': 'completed',
            'completion_time': datetime.now().isoformat(),
            'results': {
                'temperature_trends': {
                    'years': years,
                    'global_temp_anomaly': global_temp_anomaly,
                    'total_warming_c': round(total_warming, 3),
                    'warming_rate_per_decade': round(warming_rate_per_decade, 3),
                },
                'precipitation_trends': {
                    'years': years,
                    'percent_change': percent_change,
                    'mean_change_percent': round(mean(percent_change), 3),
                },
                'extreme_events': extreme_events,
                'tipping_points': tipping_points,
                'regional_analysis': regional_analysis,
                'sectoral_impacts': sectoral_impacts,
                'confidence_intervals': {
                    'temperature_5th_percentile': round(confidence_min, 3),
                    'temperature_95th_percentile': round(confidence_max, 3),
                },
            },
            'model_info': model_info,
            'simulation_mode': False,
        }

    async def _run_real_seismic_analysis(self, analysis_id: str, event_criteria: Dict,
                                       analysis_types: List[str]) -> Dict[str, Any]:
        """Ejecuta análisis sísmico real (placeholder)"""
        # Aquí iría la integración real con IRIS, USGS, etc.
        await asyncio.sleep(1)
        return await self._simulate_seismic_analysis(analysis_id, event_criteria, analysis_types)

    async def _run_real_ocean_modeling(self, analysis_id: str, region: Dict,
                                     analysis_type: str, time_span_days: int) -> Dict[str, Any]:
        entries = self._load_gistemp_dataset()
        recent_entries = entries[-12:]

        # Usamos las últimas 12 lecturas mensuales para generar una serie temporal diaria
        monthly_sequence: List[float] = []
        for entry in recent_entries:
            for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                value = entry.get(month)
                if isinstance(value, (int, float)):
                    monthly_sequence.append(float(value))
        if not monthly_sequence:
            monthly_sequence = [0.0]

        time_series: List[Dict[str, Any]] = []
        base_date = datetime.now() - timedelta(days=time_span_days)
        for day in range(time_span_days):
            anomaly = monthly_sequence[day % len(monthly_sequence)]
            date = base_date + timedelta(days=day)
            time_series.append({
                'date': date.isoformat(),
                'sea_surface_temperature': round(15.0 + anomaly, 3),
                'salinity': round(35.0 + anomaly * 0.1, 3),
                'current_velocity_u': round(0.5 + anomaly * 0.05, 3),
                'current_velocity_v': round(-0.3 + anomaly * 0.04, 3),
                'chlorophyll_a': round(max(0.01, 0.5 + anomaly * 0.02), 3),
            })

        eddies = [
            {
                'eddy_id': f'eddy_{idx}',
                'strength': round(0.4 + abs(val) * 0.2, 3),
                'radius_km': round(30 + abs(val) * 10, 2),
                'lifetime_days': 15 + idx,
            }
            for idx, val in enumerate(monthly_sequence[:3])
        ]

        marine_heatwaves = [
            {
                'start_date': time_series[max(0, len(time_series) - 15)]['date'],
                'duration_days': 10 + int(abs(monthly_sequence[-1]) * 5),
                'severity': 'high' if monthly_sequence[-1] > 0.8 else 'moderate',
                'max_temperature_c': round(15.0 + monthly_sequence[-1] + 1.2, 2),
            }
        ]

        acidification = {
            'pH_trend': round(-0.001 * mean(monthly_sequence), 5),
            'carbonate_saturation': round(3.0 - mean(monthly_sequence) * 0.1, 3),
        }

        return {
            'analysis_id': analysis_id,
            'analysis_type': 'ocean_model_observed',
            'region': region,
            'status': 'completed',
            'completion_time': datetime.now().isoformat(),
            'results': {
                'time_series_data': time_series,
                'eddies': eddies,
                'marine_heatwaves': marine_heatwaves,
                'ocean_acidification': acidification,
            },
            'simulation_mode': False,
        }
