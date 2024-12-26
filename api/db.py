from contextlib import contextmanager
from typing import ContextManager

from sqlmodel import Session, SQLModel, create_engine

import api.models as _  # noqa  Register models


class Database:
    DEFAULT_DATABASE_URL = "sqlite:///api/test.db"

    def __init__(self, database_url: str = DEFAULT_DATABASE_URL) -> None:
        self._engine = self._connect_db(database_url)

    @staticmethod
    def _connect_db(database_url: str, echo: bool = True):
        return create_engine(database_url, echo=echo)

    def create_tables(self) -> None:
        SQLModel.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> ContextManager[Session]:
        with Session(self._engine) as session:
            yield session
