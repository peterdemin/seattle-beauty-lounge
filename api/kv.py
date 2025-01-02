from sqlmodel import Session, select

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
        with self._db.session() as session:
            if record := self._select_for_update(session, key):
                if record.value == value:
                    return
                record.value = value
            else:
                record = Kiwi(key=key, value=value)
            session.add(record)
            session.commit()

    def _select_for_update(self, session: Session, key: str) -> Kiwi | None:
        return session.exec(select(Kiwi).where(Kiwi.key == key)).first()
