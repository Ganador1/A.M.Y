"""
Compatibility shim for additive manufacturing service.
Re-exports AdditiveProcess and MaterialType from app.scientific.additive_manufacturing_service
for tests expecting app.additive_manufacturing_service at the app root.
"""
from app.scientific.additive_manufacturing_service import AdditiveProcess, MaterialType

__all__ = ["AdditiveProcess", "MaterialType"]