"""
Compatibility shim for legacy imports expecting `app.database`.
Re-exports the database primitives from app.core.database so tests and code that
import from `app.database` continue to work.
"""
from __future__ import annotations

from sqlalchemy import create_engine  # re-export for tests that patch it
from sqlalchemy.orm import sessionmaker  # re-export for tests that patch it

# Re-export core database symbols
from app.core.database import (  # noqa: F401
    Base,
    get_db,
    get_db_session,
    init_database,
    close_database,
)

# engine and SessionLocal are module-level variables in app.core.database.
# Import them so tests can patch/inspect via app.database.engine / SessionLocal.
from app.core import database as _core_db

engine = _core_db.engine
SessionLocal = _core_db.SessionLocal

__all__ = [
    "Base",
    "get_db",
    "get_db_session",
    "init_database",
    "close_database",
    "engine",
    "SessionLocal",
    # Expose these for patching in tests
    "create_engine",
    "sessionmaker",
]