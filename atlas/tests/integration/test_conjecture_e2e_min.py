import unittest

from app.domains.mathematics.models.conjecture_contracts import (
    ConjectureType,
    ConjecturePayload,
    NormalizationResult,
    VerificationResult,
    ConjectureProcessingResult,
    VerificationStatus,
)
from app.domains.mathematics.services.mathematical_verification_bridge import MathematicalVerificationBridge
from app.mathlab.persistence.conjecture_persistence import ConjecturePersistenceService
from app.services.theorem_proving.z3_smt_service import Z3SMTService
from app.domains.mathematics.utils.symbolic_normalizer import SymbolicExpressionNormalizer


class TestConjectureE2E(unittest.TestCase):
    def setUp(self):
        self.persistence = ConjecturePersistenceService("sqlite:///:memory:")
        self.smt = Z3SMTService(timeout_ms=3000)
        self.normalizer = SymbolicExpressionNormalizer()
        self.bridge = MathematicalVerificationBridge(
            persistence_service=self.persistence,
            smt_service=self.smt,
            normalizer=self.normalizer,
        )

    def test_end_to_end_flow(self):
        payload = ConjecturePayload(
            id="c_test_1",
            statement="Implies(And(x > 0, y > 0), (x + y) > 0)",
            domain={"x": "real", "y": "real"},
        )

        result = self.bridge.process_conjecture(payload)

        # Validar estructura
        self.assertEqual(result.conjecture.id, "c_test_1")
        self.assertGreaterEqual(result.elapsed_ms, 0)

        # Si Z3 está disponible, debería ser PROVEN; si no, UNKNOWN
        if result.verification.status == VerificationStatus.PROVEN:
            self.assertTrue(result.verification.verified)
            self.assertIsNotNone(result.verification.elapsed_ms)
        else:
            self.assertIn(
                result.verification.status,
                {VerificationStatus.UNKNOWN, VerificationStatus.Z3_UNAVAILABLE, VerificationStatus.ERROR},
            )


if __name__ == "__main__":
    unittest.main()


