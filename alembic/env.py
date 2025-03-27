from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.database.models import Base  # Импортируйте Base из ваших моделей

# Настройка Alembic
config = context.config

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Добавьте metadata Alembic
target_metadata = Base.metadata

# Интерпретация строки подключения
url = config.get_main_option("sqlalchemy.url")


async def run_migrations_online():
    """Запуск миграций в асинхронном режиме."""
    connectable = create_async_engine(url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    """Запуск миграций."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise NotImplementedError("Offline mode is not supported for async engines")
else:
    import asyncio
    asyncio.run(run_migrations_online())
