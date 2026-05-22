"""Fuzzing básico de la API usando Schemathesis.

Ejecuta un subconjunto de endpoints definidos en docs/openapi_v1.json.
Requiere servidor activo. BASE_URL opcional.
"""
from __future__ import annotations
import os
import pathlib
import pytest

try:
    import schemathesis as st  # type: ignore
except ImportError:  # pragma: no cover
    pytest.skip("Schemathesis no instalado", allow_module_level=True)

SPEC_PATH = pathlib.Path("docs/openapi_v1.json")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

if not SPEC_PATH.exists():  # pragma: no cover
    pytest.skip("OpenAPI spec no encontrado", allow_module_level=True)

schema = st.from_path(str(SPEC_PATH), base_url=BASE_URL)


@schema.parametrize()
def test_api_fuzz(case):  # type: ignore
    response = case.call()
    case.validate_response(response)
