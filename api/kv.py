from sqlmodel import select

from api.db import Database
from api.models import Kiwi


class KiwiStore:
    """Key-Value store as a SQL table."""

    def __init__(self, db: Database) -> None:
        self._db = db

    def get(self, key: str) -> str | None:
        with self._db.session() as session:
            return session.exec(select(Kiwi.value).where(Kiwi.key == key)).first()

    def set(self, key: str, value: str) -> None:
        record = Kiwi(key=key, value=value)
        with self._db.session() as session:
            session.add(record)
            session.commit()
