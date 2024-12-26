from contextlib import contextmanager
from typing import ContextManager

from sqlmodel import Session, SQLModel, create_engine

import api.models as _  # noqa  Register models


class Database:
    def __init__(self, database_url: str) -> None:
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
