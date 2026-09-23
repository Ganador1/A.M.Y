"""
Compatibility shim for advanced torch operations.
Re-exports AdvancedTorchOperations and TorchConfig from app.advanced_ops.advanced_torch_operations
for tests expecting app.advanced_torch_operations at the app root.
"""
from app.advanced_ops.advanced_torch_operations import AdvancedTorchOperations, TorchConfig

__all__ = ["AdvancedTorchOperations", "TorchConfig"]