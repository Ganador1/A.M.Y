"""Herramientas para manipular datos climáticos reales (GISTEMP)."""
from __future__ import annotations
import aiofiles

from pathlib import Path
import csv
from typing import Any, Dict, List, Optional


_DEFAULT_GISTEMP_PATH = Path(__file__).resolve().parents[3] / "real_data_tests" / "climate_nasa_gistemp.csv"


def resolve_gistemp_path(path: Optional[str | Path] = None) -> Path:
    if path is None:
        return _DEFAULT_GISTEMP_PATH
    return path if isinstance(path, Path) else Path(path)


def load_gistemp_dataset(path: Optional[str | Path] = None) -> List[Dict[str, Any]]:
    target = resolve_gistemp_path(path)
    if not target.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset GISTEMP en {target}. Descarga el archivo o ajusta la ruta."
        )

    entries: List[Dict[str, Any]] = []
    with target.open(newline="", encoding="utf-8") as handle:
        handle.readline()
        reader = csv.reader(handle)
        header = next(reader)
        for row in reader:
            if not row:
                continue
            try:
                year = int(row[0])
            except (TypeError, ValueError):
                continue
            entry: Dict[str, Any] = {"Year": year}
            for idx, column in enumerate(header[1:], start=1):
                value = None
                if idx < len(row):
                    cell = row[idx].strip()
                    if cell and cell != "***":
                        try:
                            value = float(cell)
                        except ValueError:
                            value = None
                entry[column] = value
            entries.append(entry)

    if not entries:
        raise ValueError("El dataset GISTEMP está vacío o no se pudo parsear correctamente")

    return entries
