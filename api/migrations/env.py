# pylint: disable=no-member
from alembic import context
from sqlmodel import SQLModel

import api.models as _  # noqa register models
from api.config import Settings
from api.db import Database

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=Settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    db = Database(database_url=Settings().database_url)
    with db.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
