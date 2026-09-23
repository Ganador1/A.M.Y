import unittest

from app.mathlab.persistence.conjecture_persistence import (
    ConjecturePersistenceService,
    ConjectureType,
    ConjectureStatus,
    Conjecture,
)


class TestConjecturePersistenceUpdates(unittest.TestCase):

    def setUp(self):
        self.service = ConjecturePersistenceService("sqlite:///:memory:")
        self.conjecture_id = self.service.store_conjecture(
            title="Test Conjecture",
            statement="forall x: x > 0 => x+1 > 1",
            conjecture_type=ConjectureType.NUMBER_THEORY,
            confidence=0.5
        )

    def test_update_with_proven_verification(self):
        verification_result = {
            "conjecture": {"id": self.conjecture_id},
            "normalization": {"status": "OK"},
            "verification": {"status": "PROVEN", "verified": True},
            "elapsed_ms": 100
        }

        success = self.service.update_conjecture_with_verification(
            self.conjecture_id,
            verification_result
        )

        self.assertTrue(success)

        with self.service.get_db_session() as db:
            conjecture = db.query(Conjecture).filter_by(
                id=self.conjecture_id).one()
            self.assertEqual(conjecture.status,
                             ConjectureStatus.VERIFIED.value)
            self.assertAlmostEqual(conjecture.confidence, 0.75)
            self.assertIsNotNone(conjecture.agent1_verification_info)
            self.assertEqual(
                conjecture.agent1_verification_info["verification"]["status"], "PROVEN")

    def test_update_with_refuted_verification(self):
        verification_result = {
            "conjecture": {"id": self.conjecture_id},
            "normalization": {"status": "OK"},
            "verification": {"status": "REFUTED", "verified": False, "counterexample": {"x": -1}},
            "elapsed_ms": 50
        }

        success = self.service.update_conjecture_with_verification(
            self.conjecture_id,
            verification_result
        )

        self.assertTrue(success)

        with self.service.get_db_session() as db:
            conjecture = db.query(Conjecture).filter_by(
                id=self.conjecture_id).one()
            self.assertEqual(conjecture.status,
                             ConjectureStatus.DISPROVEN.value)
            self.assertAlmostEqual(conjecture.confidence, 0.25)
            self.assertIsNotNone(conjecture.agent1_verification_info)

    def test_update_with_unknown_verification(self):
        verification_result = {
            "conjecture": {"id": self.conjecture_id},
            "normalization": {"status": "OK"},
            "verification": {"status": "UNKNOWN", "verified": None},
            "elapsed_ms": 2000
        }

        success = self.service.update_conjecture_with_verification(
            self.conjecture_id,
            verification_result
        )

        self.assertTrue(success)

        with self.service.get_db_session() as db:
            conjecture = db.query(Conjecture).filter_by(
                id=self.conjecture_id).one()
            self.assertEqual(conjecture.status,
                             ConjectureStatus.UNDER_REVIEW.value)
            self.assertAlmostEqual(conjecture.confidence, 0.45)


if __name__ == '__main__':
    unittest.main()
