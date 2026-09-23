"""
Earth Sciences Service (skeleton)
Define configuración y métodos placeholder opcionales.
"""

from typing import Dict, Any


class EarthSciencesService:
    """Servicio integrado de ciencias de la tierra (esqueleto)."""

    def __init__(self, config: Dict[str, Any] | None = None):
        cfg = config or {}
        self.data_path = cfg.get('data_path', '/data/earth')
        self.weather_api_key = cfg.get('weather_api_key')

    # Placeholders para futura implementación
    async def analyze_climate_model(self, model_output: str, scenario: str = 'SSP585') -> Dict[str, Any]:
        raise NotImplementedError

    async def process_seismic_data(self, event_time: Any, magnitude_min: float = 5.0) -> Dict[str, Any]:
        raise NotImplementedError

    async def ocean_modeling(self, region: Dict[str, Any], timespan: str = '1month') -> Dict[str, Any]:
        raise NotImplementedError


