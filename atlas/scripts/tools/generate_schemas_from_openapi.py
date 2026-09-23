"""Genera JSONSchema por endpoint a partir de docs/openapi_v1.json.

Salida:
  - docs/schemas/<tag>/<method>_<path_sanitized>.request.json
  - docs/schemas/<tag>/<method>_<path_sanitized>.response.json
"""
from __future__ import annotations
import json
import re
from pathlib import Path


def sanitize_path(p: str) -> str:
    p = p.strip('/').replace('/', '_')
    p = re.sub(r'[^a-zA-Z0-9_\-]', '_', p)
    return p or 'root'


def main() -> int:
    openapi_path = Path('docs/openapi_v1.json')
    data = json.loads(openapi_path.read_text(encoding='utf-8'))
    out_root = Path('docs/schemas')
    out_root.mkdir(parents=True, exist_ok=True)

    paths = data.get('paths', {})
    for route, methods in paths.items():
        for method, spec in methods.items():
            method_upper = method.upper()
            tags = spec.get('tags', ['misc'])
            tag_dir = out_root / sanitize_path(tags[0])
            tag_dir.mkdir(parents=True, exist_ok=True)

            base_name = f"{method_upper}_{sanitize_path(route)}"

            # Request body schema (si existe)
            req = spec.get('requestBody', {})
            content = req.get('content', {}) if isinstance(req, dict) else {}
            app_json = content.get('application/json', {})
            schema = app_json.get('schema')
            if schema:
                (tag_dir / f"{base_name}.request.json").write_text(
                    json.dumps(schema, indent=2), encoding='utf-8'
                )

            # Response 200 schema (si existe)
            responses = spec.get('responses', {})
            resp200 = responses.get('200') or responses.get('201')
            if isinstance(resp200, dict):
                c2 = (resp200.get('content') or {}).get('application/json', {})
                s2 = c2.get('schema')
                if s2:
                    (tag_dir / f"{base_name}.response.json").write_text(
                        json.dumps(s2, indent=2), encoding='utf-8'
                    )

    print(f"Schemas exportados en {out_root}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


