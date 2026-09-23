import os
import json
import tempfile
import unittest

from app.mathlab.persistence.conjecture_persistence import ConjecturePersistenceService, ConjectureType
from app.mathlab.export.fair_exporter import MathFairExporter


class TestMathFairExporter(unittest.TestCase):
    def setUp(self):
        self.persistence = ConjecturePersistenceService("sqlite:///:memory:")
        # Crear conjetura de ejemplo
        self.conj_id = self.persistence.store_conjecture(
            title="Ejemplo",
            statement="forall x: x^2 >= 0",
            conjecture_type=ConjectureType.GENERAL,
            confidence=0.6,
        )

    def test_export(self):
        exporter = MathFairExporter(self.persistence)
        with tempfile.TemporaryDirectory() as tmpdir:
            out = exporter.export_conjectures_dataset(tmpdir)

            self.assertIn("conjectures", out["files"])  # rutas devueltas
            self.assertIn("manifest", out["files"])     # rutas devueltas

            # Archivos existen
            self.assertTrue(os.path.exists(out["files"]["conjectures"]))
            self.assertTrue(os.path.exists(out["files"]["manifest"]))

            # Manifest válido
            with open(out["files"]["manifest"], "r", encoding="utf-8") as f:
                manifest = json.load(f)
            self.assertEqual(manifest["type"], "axiom_math_fair_dataset")
            self.assertGreaterEqual(manifest["files"][0]["size_bytes"], 0)


if __name__ == "__main__":
    unittest.main()


