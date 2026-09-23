"""External science adapters for Atlas."""

from app.services.external_science.base import ExternalScienceAdapter, HttpExternalScienceAdapter
from app.services.external_science.external_science_service import ExternalScienceService, external_science_service
from app.services.external_science.paperqa2_adapter import PaperQA2Adapter
from app.services.external_science.remote_adapters import AlphaGenomeAdapter, MatterGenAdapter, MatterSimAdapter

__all__ = [
    "AlphaGenomeAdapter",
    "ExternalScienceAdapter",
    "ExternalScienceService",
    "HttpExternalScienceAdapter",
    "MatterGenAdapter",
    "MatterSimAdapter",
    "PaperQA2Adapter",
    "external_science_service",
]
