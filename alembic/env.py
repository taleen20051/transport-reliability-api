from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

config = context.config

# Get repo root and add to PYTHONPATH so import app... works, then load .env for DATABASE_URL
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        f"DATABASE_URL was not detected. Expected it in {ENV_PATH}. "
        "Make a .env file at repo root with DATABASE_URL=..."
    )

# Override the sqlalchemy.url from alembic.ini with our env var
config.set_main_option("sqlalchemy.url", database_url)

# look for alembic.ini in current directory and load logging config from there
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.db.base import Base
import app.models

target_metadata = Base.metadata

# Execute the appropriate migration function based on offline/online mode
def run_migrations_offline() -> None:
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