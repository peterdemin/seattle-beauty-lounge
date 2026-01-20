import datetime
import uuid
from typing import Annotated, Any, Optional

from pydantic import PlainValidator
from sqlmodel import Field, SQLModel

from api.square_client import Payment


def parse_time(value: Any) -> datetime.time:
    if not isinstance(value, str):
        return value
    supported_formats = ("%I:%M %p", "%H:%M")
    for i, time_format in enumerate(supported_formats):
        try:
            return datetime.datetime.strptime(value, time_format).time()
        except ValueError:
            if i == len(supported_formats) - 1:
                raise
    # Unreachable
    return datetime.time()


Time = Annotated[datetime.time, PlainValidator(parse_time)]


class AppointmentPub(SQLModel):
    pubid: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        index=True,
        unique=True,
        nullable=False,
        sa_column_kwargs={"server_default": uuid.UUID("0" * 32).hex},
    )
    serviceId: str
    date: datetime.date
    time: datetime.time

    @staticmethod
    def extract_pub(inst: "AppointmentPub") -> "AppointmentPub":
        return AppointmentPub(
            pubid=inst.pubid,
            serviceId=inst.serviceId,
            date=inst.date,
            time=inst.time,
        )


class Appointment(AppointmentPub, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    clientName: str
    clientPhone: str
    clientEmail: str
    remindedAt: int = Field(default=0)
    depositToken: str = Field(default="")


class AppointmentCreate(AppointmentPub):
    time: Time
    clientName: str
    clientPhone: str
    clientEmail: str
    payment: Optional[Payment]


class Kiwi(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str = Field()
