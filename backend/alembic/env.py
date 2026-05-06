import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add backend/ to path so app imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base
from app.models import ROIRecord  # noqa: F401 — needed for autogenerate

# Alembic Config object
config = context.config

# Override sqlalchemy.url from environment variable
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/facedb"))

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine

    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()