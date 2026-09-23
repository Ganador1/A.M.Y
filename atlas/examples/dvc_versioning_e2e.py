import asyncio
from pathlib import Path
from datetime import datetime
import csv
import json
import sys

# Asegura que el directorio raíz del proyecto esté en sys.path para importar 'app.*'
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.data_versioning import DataVersioningService


def _write_sample_csv(path: Path):
    rows = [
        {"id": 1, "value": 3.14},
        {"id": 2, "value": 2.71},
        {"id": 3, "value": 1.41},
    ]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "value"])
        w.writeheader()
        w.writerows(rows)


async def main():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    dataset_path = data_dir / f"toy_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    _write_sample_csv(dataset_path)

    svc = DataVersioningService()
    res = await svc.version_data({
        "action": "version_data",
        "data_path": str(dataset_path),
        "metadata": {"source": "generated", "rows": 3},
        "tags": ["example", "toy"],
        # permitir ruta externa si STRICT_DATA_PATHS=0 y se desea
        "allow_external_path": False,
    })

    # Crear reporte de procedencia (requiere data_path)
    prov = svc.create_provenance_report({
        "action": "create_provenance_report",
        "data_path": str(dataset_path)
    })

    # Guardar reporte si fue exitoso
    if prov.get("success"):
        out = Path("data/provenance_report.json")
        out.write_text(json.dumps(prov["report"], indent=2))

    print("OK DVC E2E")
    print(json.dumps({
        "versioning": res,
        "provenance_report": prov
    }, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
