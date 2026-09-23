"""Gestión de exportación y versionado de mini-papers y artefactos.

Responsabilidades:
    - Escribir representaciones Markdown.
    - Guardar manifest JSON con metadatos (hash, fecha, componentes usados).
    - Estrategia de versionado incremental (v1, v2, ... por título base).

API inicial:
    export_paper(paper: MiniPaper, out_dir: str) -> dict
"""
from __future__ import annotations
import asyncio

import hashlib
import json
from pathlib import Path
from typing import Dict, Any

from .paper_builder import MiniPaper


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def export_paper(paper: MiniPaper, out_dir: str) -> Dict[str, Any]:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    base_slug = paper.title.lower().replace(" ", "_")
    versions = sorted(p for p in out_path.glob(f"{base_slug}_v*.md"))
    next_idx = len(versions) + 1
    md_filename = f"{base_slug}_v{next_idx}.md"
    md_path = out_path / md_filename

    markdown = paper.to_markdown()
    content_hash = _hash_text(markdown)
    md_path.write_text(markdown, encoding="utf-8")

    manifest = {
        "title": paper.title,
        "version": next_idx,
        "file": str(md_path),
        "hash": content_hash,
        "sections": [s.key for s in paper.sections],
        "artifacts": [a.path for a in paper.artifacts],
        "metadata": paper.metadata,
    }
    (out_path / f"{base_slug}_v{next_idx}.manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return manifest

__all__ = ["export_paper"]
