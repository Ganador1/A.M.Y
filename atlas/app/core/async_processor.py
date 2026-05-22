"""
Compatibility shim for async processor.
Re-exports AdvancedAsyncProcessor from app.processing.async_processor for tests expecting app.async_processor.
"""
from app.processing.async_processor import AdvancedAsyncProcessor

__all__ = ["AdvancedAsyncProcessor"]