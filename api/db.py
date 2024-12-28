from contextlib import contextmanager
from typing import ContextManager

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import api.models as _  # noqa  Register models


class Database:
    def __init__(self, database_url: str) -> None:
        self._engine = self._connect_db(database_url)

    @staticmethod
    def _connect_db(database_url: str, echo: bool = True):
        if database_url == "sqlite://":
            return create_engine(
                database_url,
                echo=echo,
                connect_args=({"check_same_thread": False}),
                poolclass=StaticPool,
            )
        else:
            return create_engine(
                database_url,
                echo=echo,
                connect_args=(
                    {"check_same_thread": False} if database_url.startswith("sqlite://") else {}
                ),
            )

    def create_tables(self) -> None:
        SQLModel.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> ContextManager[Session]:
        with Session(self._engine) as session:
            yield session
