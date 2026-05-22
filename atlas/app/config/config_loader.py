"""Centralizado de configuración con cache y soporte YAML/JSON.

Características:
- Carga perezosa de archivos en `config/` (raíz del repo) o paquete `app/config/`.
- Soporta YAML (.yml/.yaml) y JSON.
- Cache in-memory (invalidación opcional por timestamp/force_reload).
- Overrides por entorno: si existe VARIABLE `ATLAS_ENV` y un archivo `nombre.<env>.yaml` se prioriza.
- Acceso jerárquico por path con get_config().
- Fallback de variables de entorno desde `.env` en la raíz del repo (si existe).

Uso:
    from app.config.config_loader import get_config
    db_host = get_config('database.host')

"""
from __future__ import annotations
import os
import json
import threading
from pathlib import Path
from app.config import settings
from typing import Any, Dict, Optional
import aiofiles
import asyncio

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

# Carga .env de forma pasiva (si python-dotenv está disponible)
_BASE_DIR = Path(__file__).resolve().parent.parent.parent  # apunta a raíz del repo
try:  # pragma: no cover - defensivo
    from dotenv import load_dotenv  # type: ignore
    _DOTENV_LOADED = False
    if not _DOTENV_LOADED:
        env_path = _BASE_DIR / ".env"
        if env_path.exists():
            # override=False para respetar variables ya definidas en el entorno
            load_dotenv(dotenv_path=env_path, override=False)
        _DOTENV_LOADED = True
except Exception:  # pragma: no cover
    # Fallback mínimo: parseo simple de .env si no está instalado python-dotenv
    env_path = _BASE_DIR / ".env"
    if env_path.exists():
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)
        except Exception:
            pass

_LOCK = threading.RLock()
_CACHE: Dict[str, Dict[str, Any]] = {}
_CONFIG_DIRS = [
    _BASE_DIR / "config",           # carpeta externa principal
    Path(__file__).resolve().parent  # app/config
]
_ENV = settings.atlas_env

_SUPPORTED_EXTS = (".yaml", ".yml", ".json")


def _merge_dict(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            _merge_dict(a[k], v)
        else:
            a[k] = v
    return a


def _load_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        if path.suffix in (".yaml", ".yml") and yaml:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                if not isinstance(data, dict):
                    return {"_raw": data}
                return data
        if path.suffix == ".json":
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    return {"_raw": data}
                return data
    except Exception as e:  # pragma: no cover
        return {"_error": str(e)}
    return {}


def _resolve_candidates(base_name: str) -> list[Path]:
    names = []
    # environment override primero
    if _ENV:
        names.append(f"{base_name}.{_ENV}")
    names.append(base_name)
    candidates: list[Path] = []
    for cfg_dir in _CONFIG_DIRS:
        for name in names:
            for ext in _SUPPORTED_EXTS:
                p = cfg_dir / f"{name}{ext}"
                if p.exists():
                    candidates.append(p)
    return candidates


def load_config_section(section: str, force_reload: bool = False) -> Dict[str, Any]:
    """Carga y cachea una sección de config (archivo). section sin extensión.
    Precedencia: config externa > interna (último merge gana). Env override se evalúa individualmente.
    """
    with _LOCK:
        if section in _CACHE and not force_reload:
            return _CACHE[section]
        data: Dict[str, Any] = {}
        for path in _resolve_candidates(section):
            fragment = _load_file(path)
            _merge_dict(data, fragment)
        _CACHE[section] = data
        return data


def get_config(path: str, default: Any = None) -> Any:
    """Obtiene un valor por path jerárquico: section.subkey1.subkey2
    Ej: get_config('database.host')
    """
    parts = path.split(".")
    if not parts:
        return default
    section = parts[0]
    data = load_config_section(section)
    cur: Any = data
    for key in parts[1:]:
        if not isinstance(cur, dict):
            return default
        if key not in cur:
            return default
        cur = cur[key]
    return cur


def reload_section(section: str) -> Dict[str, Any]:
    return load_config_section(section, force_reload=True)

__all__ = [
    "get_config",
    "load_config_section",
    "reload_section",
]
