"""Pydantic compatibility helpers for legacy Config classes.

Esta utilidad crea una subclase de ``pydantic.BaseModel`` que traduce
automáticamente las clases internas ``Config`` (estilo Pydantic v1) al nuevo
atributo ``model_config`` introducido en Pydantic v2. Al importarla durante el
arranque, podemos seguir usando modelos existentes sin migrarlos de inmediato.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, cast

from pydantic import ConfigDict
from pydantic._internal._model_construction import ModelMetaclass


def _extract_config_values(config: Any) -> Dict[str, Any]:
    """Extrae atributos públicos no invocables de una clase Config heredada."""

    values: Dict[str, Any] = {}
    for attr in dir(config):
        if attr.startswith("_"):
            continue
        value = getattr(config, attr)
        if callable(value):
            continue
        values[attr] = value
    return values


def _merge_config(existing: Any, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Combina la configuración previa con los valores heredados."""

    merged: Dict[str, Any] = {}
    if isinstance(existing, Mapping):
        merged.update(existing)
    merged.update(updates)
    return merged


_ORIGINAL_MODEL_METACLASS_NEW = ModelMetaclass.__new__


def _compat_model_metaclass_new(
    cls: type,
    name: str,
    bases: tuple[type, ...],
    namespace: dict[str, Any],
    **kwargs: Any,
) -> type:
    legacy_config = namespace.get("Config")
    if legacy_config is not None:
        config_values = _extract_config_values(legacy_config)
        if config_values:
            existing = namespace.get("model_config")
            merged_config = _merge_config(existing, config_values)
            namespace["model_config"] = cast(ConfigDict, merged_config)
        namespace.pop("Config", None)
    return cast(type, _ORIGINAL_MODEL_METACLASS_NEW(cls, name, bases, namespace, **kwargs))


if getattr(ModelMetaclass.__new__, "__name__", "") != "_compat_model_metaclass_new":
    ModelMetaclass.__new__ = _compat_model_metaclass_new  # type: ignore[assignment]
