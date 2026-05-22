"""Simplified consolidated blockchain validation module.

This file replaces multiple historical duplicated implementations with a single
lightweight version focused on deterministic hashing and minimal block storage.

Public symbols preserved for backward compatibility:
 - BlockchainValidationService
 - blockchain_service (guarded global instance)
 - blockchain_router (FastAPI router)
 - PINNResult, ValidationBlock, ValidationProof dataclasses
 - create_pinn_result_hash utility

Side‑effect guard: set environment variable AXIOM_SKIP_AUTOINIT=1 to skip
automatic service instantiation during bulk import verification.
"""

from __future__ import annotations
import asyncio

import os
import hashlib
import json
import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class PINNResult:
    result_id: str
    model_type: str
    pde_type: str
    input_parameters: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence_score: float
    execution_time: float
    timestamp: datetime
    node_id: str
    version: str = "1.0"

@dataclass
class ValidationBlock:
    block_id: str
    previous_hash: str
    timestamp: datetime
    pinn_result: PINNResult
    validator_nodes: List[str]
    signatures: Dict[str, str]
    consensus_hash: str
    nonce: int
    difficulty: int

@dataclass
class ValidationProof:
    proof_id: str
    result_hash: str
    validator_signatures: Dict[str, str]
    consensus_reached: bool
    timestamp: datetime
    block_height: int

@dataclass
class Block:
    index: int
    timestamp: float
    data: Dict[str, Any]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    signatures: Dict[str, str] | None = None
    def __post_init__(self):
        if self.signatures is None:
            self.signatures = {}
        if not self.hash:
            self.hash = self.calculate_hash()
    def calculate_hash(self) -> str:
        payload = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

@dataclass
class ValidationResult:
    is_valid: bool
    block_hash: str
    timestamp: float
    confidence_score: float
    validation_details: Dict[str, Any]

class BlockchainValidationService:
    """Minimal blockchain-like validation ledger.

    Provides deterministic hashing, append-only block list and simple
    validation records sufficient for integrity checks in tests and docs.
    """

    def __init__(self, difficulty: int = 3):
        self.difficulty = difficulty
        self.chain: List[Block] = []
        self.pending_validations: Dict[str, ValidationResult] = {}
        self.node_id = str(uuid.uuid4())
        self._create_genesis_block()
        logger.info("BlockchainValidationService initialized (simplified)")

    def _create_genesis_block(self) -> None:
        self.chain.append(Block(
            index=0,
            timestamp=time.time(),
            data={"type": "genesis"},
            previous_hash="0" * 64
        ))

    def _proof_of_work(self, block: Block) -> int:
        target = "0" * self.difficulty
        nonce = 0
        while True:
            block.nonce = nonce
            if block.calculate_hash().startswith(target):
                return nonce
            nonce += 1
            if nonce > 50000:  # safety limit
                break
        return nonce

    def add_block(self, data: Dict[str, Any]) -> Block:
        prev = self.chain[-1]
        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=data,
            previous_hash=prev.hash
        )
        block.nonce = self._proof_of_work(block)
        block.hash = block.calculate_hash()
        self.chain.append(block)
        return block

    def validate_pinn_result(self, result_data: Dict[str, Any]) -> ValidationResult:
        try:
            validation_id = str(uuid.uuid4())
            
            # Convert result_data to JSON-serializable format if it's a dataclass
            if hasattr(result_data, '__dataclass_fields__'):
                import dataclasses
                serializable_data = {}
                for field in dataclasses.fields(result_data):
                    value = getattr(result_data, field.name)
                    # Convert datetime to ISO string
                    if isinstance(value, datetime):
                        serializable_data[field.name] = value.isoformat()
                    else:
                        serializable_data[field.name] = value
                result_data = serializable_data
            
            block = self.add_block({
                "type": "pinn_validation",
                "validation_id": validation_id,
                "result_data": result_data,
                "node": self.node_id,
                "ts": time.time()
            })
            vr = ValidationResult(
                is_valid=True,
                block_hash=block.hash,
                timestamp=block.timestamp,
                confidence_score=0.5,
                validation_details={
                    "block_index": block.index,
                    "validation_id": validation_id
                }
            )
            self.pending_validations[validation_id] = vr
            return vr
        except Exception as exc:  # noqa: BLE001
            logger.error("Validation error: %s", exc)
            return ValidationResult(False, "", time.time(), 0.0, {"error": str(exc)})

    def get_validation_status(self, validation_id: str) -> Optional[ValidationResult]:
        return self.pending_validations.get(validation_id)

    def get_chain_length(self) -> int:
        return len(self.chain)

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current, previous = self.chain[i], self.chain[i-1]
            if current.hash != current.calculate_hash() or current.previous_hash != previous.hash:
                return False
        return True

    def _calculate_result_hash(self, result: PINNResult) -> str:  # pragma: no cover
        return hashlib.sha256(json.dumps(asdict(result), sort_keys=True, default=str).encode()).hexdigest()

blockchain_service: Optional[BlockchainValidationService]
# Guard automatic instantiation during bulk import/testing runs
_skip_autoinit = str(getattr(settings, "AXIOM_SKIP_AUTOINIT", "0")).lower()
if _skip_autoinit not in ("1", "true", "yes"):
    blockchain_service = BlockchainValidationService()
else:  # pragma: no cover
    blockchain_service = None

class ValidationRequest(BaseModel):
    result_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class ValidationResponse(BaseModel):
    validation_id: str
    is_valid: bool
    block_hash: str
    timestamp: float
    confidence_score: float
    validation_details: Dict[str, Any]

router = APIRouter(prefix="/validation/blockchain", tags=["blockchain-validation"])  # legacy path
blockchain_router = APIRouter(prefix="/api/blockchain", tags=["blockchain-validation"])  # new path

@router.post('/validate', response_model=ValidationResponse)
async def legacy_validate(req: ValidationRequest):
    if blockchain_service is None:
        raise HTTPException(status_code=503, detail="Blockchain service unavailable")
    res = blockchain_service.validate_pinn_result(req.result_data)
    return ValidationResponse(
        validation_id=res.validation_details.get('validation_id', ''),
        is_valid=res.is_valid,
        block_hash=res.block_hash,
        timestamp=res.timestamp,
        confidence_score=res.confidence_score,
        validation_details=res.validation_details
    )

@blockchain_router.post('/validate', response_model=ValidationResponse)
async def validate(req: ValidationRequest):  # consolidated path
    return await legacy_validate(req)

@router.get('/status/{validation_id}')
async def legacy_status(validation_id: str):
    if blockchain_service is None:
        raise HTTPException(status_code=503, detail="Blockchain service unavailable")
    res = blockchain_service.get_validation_status(validation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Validation not found")
    return {
        'validation_id': validation_id,
        'status': 'completed' if res.is_valid else 'failed',
        'result': {
            'is_valid': res.is_valid,
            'block_hash': res.block_hash,
            'timestamp': res.timestamp,
            'confidence_score': res.confidence_score,
            'validation_details': res.validation_details
        }
    }

@blockchain_router.get('/stats')
async def stats():
    if blockchain_service is None:
        raise HTTPException(status_code=503, detail="Blockchain service unavailable")
    return {
        'chain_length': blockchain_service.get_chain_length(),
        'is_valid': blockchain_service.is_chain_valid(),
        'node_id': blockchain_service.node_id,
        'difficulty': blockchain_service.difficulty
    }

def create_pinn_result_hash(result_data: Dict[str, Any]) -> str:
    """Deterministic hash for a PINN result payload independent of service state."""
    payload = json.dumps(result_data, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()

__all__ = [
    'BlockchainValidationService',
    'blockchain_service',
    'router',
    'blockchain_router',
    'PINNResult',
    'ValidationBlock',
    'ValidationProof',
    'create_pinn_result_hash'
]
