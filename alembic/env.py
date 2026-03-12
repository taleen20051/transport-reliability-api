# This file tells Alembic how to connect to the database
# and where to find the SQLAlchemy models for migration generation.
from __future__ import annotations

import os
import app.models
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from app.db.base import Base

config = context.config

# Determine the repository root so the app package can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from the project's .env file
dotenv_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Migrations cannot run without a valid database URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        f"DATABASE_URL was not seen. Expected it in {dotenv_path}. "
        "Make a .env file at repo root with DATABASE_URL=..."
    )

# Replace the placeholder database URL in alembic.ini with the value from the environment variable
config.set_main_option("sqlalchemy.url", database_url)

# look for alembic.ini in current directory and load logging config from there
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Offline migrations generate SQL scripts without connecting to the database
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

# Online migrations run directly against the database connection
def run_migrations_online() -> None:
    engine = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with engine.connect() as db_connection:
        context.configure(
            connection=db_connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()