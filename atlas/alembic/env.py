"""
AXIOM Mathematics AI Engine - Alembic Environment Configuration
===============================================================

Alembic environment configuration for database migrations.
This file configures Alembic to work with the AXIOM database models.

Author: AXIOM Mathematics AI Engine Team
Date: September 2025
"""

from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set environment variable to indicate we're in migration context
os.environ['ALEMBIC_MIGRATION'] = 'true'

# Import AXIOM database models and configuration
from app.models.database_models import Base
# Ensure workflow persistence models are registered in metadata
import app.models.workflow_persistence_models  # noqa: F401
import app.models.hypothesis_models  # noqa: F401
import app.models.protgpt2_models  # noqa: F401
import app.models.experiment_scheduler_models  # noqa: F401
import app.models.plausibility_models  # noqa: F401
import app.models.artifacts.manifest_models  # noqa: F401
import app.models.artifacts.ensemble_record  # noqa: F401
import app.models.artifacts.training_metadata  # noqa: F401
import app.models.artifacts.weak_label_record  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata

# Configure database URL from settings
def get_database_url():
    """Get database URL from settings."""
    try:
        from app.config import settings
        # Use PostgreSQL if available and not in migration generation mode
        if (hasattr(settings, 'database_url') and settings.database_url and
            os.getenv('ALEMBIC_MIGRATION', '').lower() not in ('true', '1', 'yes')):
            return settings.database_url
        else:
            # Use SQLite for migration generation or when PostgreSQL is not available
            return "sqlite:///migrations.db"
    except ImportError:
        # Fallback to SQLite if settings import fails
        return "sqlite:///migrations.db"

# Override the sqlalchemy.url with settings-based configuration
config.set_main_option("sqlalchemy.url", get_database_url())

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
