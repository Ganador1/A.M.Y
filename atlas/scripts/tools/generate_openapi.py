"""Genera OpenAPI v1 y guarda en docs/openapi_v1.json.

Uso:
  python scripts/generate_openapi.py
"""
from __future__ import annotations
import json
from pathlib import Path

from fastapi.encoders import jsonable_encoder

# Importa la app principal
from main import app  # noqa: E402


def main() -> int:
    openapi = app.openapi()
    out_path = Path("docs/openapi_v1.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(jsonable_encoder(openapi), indent=2), encoding="utf-8")
    print(f"OpenAPI v1 generado en {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


