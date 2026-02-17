from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides access to the values
# within the .ini file in use.
config = context.config

# FIX: Ensure we can import `app.*` and always load .env from repo root
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # repo root (folder containing alembic.ini)
sys.path.insert(0, str(PROJECT_ROOT))

ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        f"DATABASE_URL is not set. Expected it in {ENV_PATH}. "
        "Create a .env file at repo root with DATABASE_URL=..."
    )

# Inject into Alembic at runtime (avoid ini interpolation issues)
config.set_main_option("sqlalchemy.url", database_url)
# ------------------------------------------------------------

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ------------------------------------------------------------
# FIX: Tell Alembic what metadata to scan + ensure models imported
# ------------------------------------------------------------
from app.db.base import Base  # noqa: E402
import app.models  # noqa: F401, E402  (imports Route/Station/etc so Base.metadata has tables)

target_metadata = Base.metadata
# ------------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()