"""
Blockchain Validation module for compatibility
This is a compatibility stub that redirects to the correct module
"""

# Import specific items from the correct location
from app.validation.blockchain_validation import (
    BlockchainValidationService,
    blockchain_service,
    ValidationResult,
    Block,
    ValidationProof,
    PINNResult,
    ValidationRequest,
    ValidationResponse,
    blockchain_router
)

__all__ = [
    "BlockchainValidationService",
    "blockchain_service",
    "ValidationResult",
    "Block",
    "ValidationProof",
    "PINNResult",
    "ValidationRequest",
    "ValidationResponse",
    "blockchain_router"
]