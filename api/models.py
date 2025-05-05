import datetime
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


class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serviceId: str
    date: datetime.date
    time: datetime.time
    clientName: str
    clientPhone: str
    clientEmail: str
    remindedAt: int = Field(default=0)
    depositToken: str = Field(default="")


class AppointmentCreate(SQLModel):
    serviceId: str
    date: datetime.date
    time: Time
    clientName: str
    clientPhone: str
    clientEmail: str
    payment: Payment


class Kiwi(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str = Field()
