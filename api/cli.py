from sqlmodel import select

from api.config import Settings
from api.db import Database
from api.models import Appointment


def main() -> None:
    settings = Settings()
    db = Database(database_url=settings.database_url)
    for appointment in list_appointment(db):
        for k, v in appointment.items():
            print(f"{k}: {v}")
        print("---")


def list_appointment(db: Database) -> list[dict]:
    with db.session() as session:
        appointments = session.exec(select(Appointment)).all()
        return [appointment.model_dump() for appointment in appointments]


if __name__ == "__main__":
    main()
