from __future__ import annotations
import unittest
import uuid
import logging

from app.domains.mathematics.services.mathematical_verification_bridge import MathematicalVerificationBridge
from app.domains.mathematics.models.conjecture_contracts import ConjecturePayload
from app.mathlab.persistence.conjecture_persistence import (
    ConjecturePersistenceService,
    ConjectureType,
    ConjectureStatus,
)
from app.services.theorem_proving.z3_smt_service import smt_service_singleton
from app.domains.mathematics.utils.symbolic_normalizer import symbolic_normalizer_singleton

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class TestAgentBridgeIntegration(unittest.TestCase):
    def setUp(self):
        db_name = f"file:{uuid.uuid4()}?mode=memory&cache=shared"
        self.persistence_service = ConjecturePersistenceService(
            database_url=f"sqlite:///{db_name}"
        )
        self.bridge = MathematicalVerificationBridge(
            persistence_service=self.persistence_service,
            smt_service=smt_service_singleton,
            normalizer=symbolic_normalizer_singleton,
        )

    def test_full_process_and_persistence_proven(self):
        statement_str = "Implies(And(x > 0, y > 0), (x + y) > 0)"
        conjecture_id = self.persistence_service.store_conjecture(
            title="Provable Conjecture",
            statement=statement_str,
            conjecture_type=ConjectureType.NUMBER_THEORY,
            confidence=0.6,
        )
        self.assertIsNotNone(conjecture_id)

        payload = ConjecturePayload(
            id=conjecture_id,
            statement=statement_str,
            domain={"x": "Real", "y": "Real"},
        )
        result = self.bridge.process_conjecture(payload)
        self.assertEqual(result.verification.status, "PROVEN")
        self.assertTrue(result.verification.verified)

        conjecture = self.persistence_service.get_conjecture_by_id(conjecture_id)
        self.assertIsNotNone(conjecture)
        if conjecture is None:  # defensa para el analizador estático
            self.fail("Conjecture retrieval returned None")
            return
        self.assertEqual(conjecture.status, ConjectureStatus.VERIFIED.value)
        self.assertIsNotNone(conjecture.agent1_verification_info)
        verification_info = conjecture.agent1_verification_info
        self.assertEqual(
            verification_info.get("verification", {}).get("status"), "PROVEN"
        )
        self.assertGreater(conjecture.confidence, 0.6)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
