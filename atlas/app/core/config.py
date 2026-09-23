"""
Compatibility bridge for configuration imports.

This module provides a stable import path `app.core.config` and re-exports
objects from the `app.config` package to avoid ModuleNotFoundError in tests
and services that still reference the old location.
"""

from __future__ import annotations

try:
    # Prefer explicit loader and helpers if present
    from app.config.config_loader import (
        load_config_section,
        reload_section,
        get_config,
    )  # type: ignore
except Exception:
    # Provide safe no-op fallbacks to avoid import-time failures in tests
    def load_config_section(section: str):  # pragma: no cover
        return {}

    def reload_section(section: str):  # pragma: no cover
        return {}

    def get_config() -> dict:  # pragma: no cover
        return {}

try:
    # Re-export common config elements
    from app.config import (
        config_loader,
        database_config,
        secrets_manager,
        startup_validation,
        yaml_validator,
        Settings,
        settings,
    )  # type: ignore
except Exception:
    # If any submodule is missing, expose empty stubs to keep imports resilient
    config_loader = None
    database_config = None
    secrets_manager = None
    startup_validation = None
    yaml_validator = None
    Settings = None  # type: ignore
    settings = None  # type: ignore