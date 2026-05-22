"""Bridge entre laboratorio matemático y verificación simbólica SMT.

Responsabilidades:
- Recibir una `ConjecturePayload`
- Normalizar usando `Z3SMTService.normalize_expression`
- Verificar usando `Z3SMTService.verify_smt2` (si normalización exitosa)
- Construir `ConjectureProcessingResult`

Notas:
- Mantiene dependencia débil: sólo requiere instancia de Z3SMTService inyectada.
- Incluye helper para procesar lote de conjeturas.
"""
from __future__ import annotations
from typing import Iterable, List
import time
import logging

from app.mathlab.persistence.conjecture_persistence import ConjecturePersistenceService
from app.services.theorem_proving.z3_smt_service import Z3SMTService
from app.domains.mathematics.models.conjecture_contracts import (
    ConjecturePayload,
    ConjectureProcessingResult,
    VerificationResult,
    VerificationStatus,
    NormalizationResult,
    NormalizationStatus,
)
from app.exceptions.domain.mathematics import MathematicsError
from app.domains.mathematics.utils.symbolic_normalizer import SymbolicExpressionNormalizer

logger = logging.getLogger(__name__)


class MathematicalVerificationBridge:
    """
    A bridge to connect mathematical conjecture generation with symbolic verification.
    """
    def __init__(self, persistence_service: ConjecturePersistenceService, smt_service: Z3SMTService, normalizer: SymbolicExpressionNormalizer):
        self.persistence_service = persistence_service
        self.smt_service = smt_service
        self.normalizer = normalizer

    def process_conjecture(self, payload: ConjecturePayload) -> ConjectureProcessingResult:
        """
        Processes a conjecture, normalizes it, verifies it, and persists the result.
        """
        logging.info(f"Processing conjecture ID: {payload.id}")
        start_time = time.time()
        
        try:
            # The normalizer now handles the conversion from string internally
            expr_node = self.normalizer.from_python(payload.statement, payload.domain)
            smt_script = self.normalizer.to_smt_script(expr_node)
            
            norm = NormalizationResult(
                status=NormalizationStatus.OK,
                smt_script=smt_script,
                error=None
            )
            
            verification_raw = self.smt_service.verify_smt2(smt_script)
            verification = VerificationResult.model_validate(verification_raw)

            logging.info(f"Conjecture {payload.id} verified with status: {verification.status}")

        except MathematicsError as e:
            logging.error(f"Error processing conjecture {payload.id}: {e}", exc_info=True)
            norm = NormalizationResult(status=NormalizationStatus.ERROR, smt_script=None, error=str(e))
            verification = VerificationResult(status=VerificationStatus.NORMALIZATION_FAILED, verified=None, counterexample=None)

        elapsed_ms = int((time.time() - start_time) * 1000)
        result = ConjectureProcessingResult(
            conjecture=payload,
            normalization=norm,
            verification=verification,
            elapsed_ms=elapsed_ms,
        )

        if payload.id:
            try:
                self.persistence_service.update_conjecture_with_verification(
                    conjecture_id=payload.id,
                    verification_result=result.model_dump()
                )
            except MathematicsError as e:
                # Registrar el error pero no fallar en la operación principal
                logger.error(f"Error al persistir la verificación para la conjetura {payload.id}: {e}")

        return result

    def process_batch(self, payloads: Iterable[ConjecturePayload]) -> List[ConjectureProcessingResult]:
        return [self.process_conjecture(p) for p in payloads]


__all__ = ["MathematicalVerificationBridge"]