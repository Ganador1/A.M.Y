"""
Cloud Lab Service (ECL stub)
Provee interfaz mínima y segura; en este entorno retorna error controlado.
"""

from typing import Dict, Any


class CloudLabService:
    """
    Stub de integración con Emerald Cloud Lab.
    Por defecto, lanza excepción indicando que no está configurado.
    """

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('ecl_api_key')

    async def submit_experiment(self, protocol: Dict[str, Any]) -> str:
        raise Exception("ECL no está configurado en este entorno (stub)")


