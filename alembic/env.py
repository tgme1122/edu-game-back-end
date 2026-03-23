import os
import sys
from pathlib import Path
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context


# ✅ 1) Project root (back_end/) ni sys.path ga qo'shamiz (IMPORTLARDAN OLDIN!)
BASE_DIR = Path(__file__).resolve().parents[1]  # back_end/
sys.path.insert(0, str(BASE_DIR))

# ✅ 2) .env ni yuklaymiz (default: back_end/.env)
load_dotenv(BASE_DIR / ".env")

# ✅ 3) Alembic config
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ 4) Endi app importlar xavfsiz
from app.core.database import Base  # noqa: E402
from app.models.users import User   # noqa: F401,E402  (autogenerate uchun kerak)
from app.models.questions import Question
from app.models.frog_game import FrogGameQuestion
from app.models.lugat_duel_question import LugatDuelQuestion


target_metadata = Base.metadata


def get_url() -> str:
    # 1) Agar DATABASE_URL bo'lsa, shu ishlatiladi
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # 2) Aks holda bo'laklab yig'amiz
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "postgres")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "postgres")

    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


# Alembic sqlalchemy.url ni runtime'da set qilamiz
config.set_main_option("sqlalchemy.url", get_url())


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # type o'zgarishlarini ham ko'rsin
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
