"""Contract tests básicos contra OpenAPI v1.

Requisitos previos:
- Archivo docs/openapi_v1.json generado (script scripts/generate_openapi.py)
- Servidor en ejecución (variable de entorno BASE_URL opcional, default http://localhost:8000)

Validaciones:
- El spec carga y tiene versión.
- Endpoints listados devuelven status esperado (200/401 según auth) usando heurística.
- Campos obligatorios de seguridad presentes si se define el esquema.

Uso rápido:
pytest -q tests/contract/test_openapi_contract.py
"""
from __future__ import annotations
import json
import os
import pathlib
import re
from typing import List

import pytest
import requests

SPEC_PATH = pathlib.Path("docs/openapi_v1.json")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def openapi_spec() -> dict:
    if not SPEC_PATH.exists():
        pytest.skip("OpenAPI spec no encontrado: genera con scripts/generate_openapi.py")
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_spec_metadata(openapi_spec):
    assert "openapi" in openapi_spec
    assert re.match(r"^3\\.\d+\\.\d+", openapi_spec["openapi"]) is not None
    info = openapi_spec.get("info", {})
    assert info.get("title")
    assert info.get("version")


def iter_sample_paths(openapi_spec, limit: int = 10) -> List[str]:
    paths = list(openapi_spec.get("paths", {}).keys())
    # prefer /api/v1 endpoints
    v1 = [p for p in paths if p.startswith("/api/v1/")]
    return v1[:limit] if v1 else paths[:limit]


@pytest.mark.parametrize("path", indirect=False, argvalues=[], ids=None)
def test_dummy():  # placeholder si no hay parametrizaciones dinámicas
    pass


def test_basic_endpoints_reachable(openapi_spec):  # noqa: PT019 fixture param
    sample = iter_sample_paths(openapi_spec)
    if not sample:
        pytest.skip("Sin paths en el spec")
    for p in sample:
        url = BASE_URL + p
        resp = requests.get(url, timeout=5)
        assert resp.status_code in {200, 401, 403}


def test_security_definitions(openapi_spec):  # noqa: PT019 fixture param
    components = openapi_spec.get("components", {})
    security_schemes = components.get("securitySchemes", {})
    # Esperamos al menos un esquema (ej. OAuth2/JWT)
    assert security_schemes, "Falta definición de securitySchemes (OAuth2/JWT esperado)"
