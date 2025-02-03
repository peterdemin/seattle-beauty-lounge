import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from api.square_client import Payment


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
    time: datetime.time
    clientName: str
    clientPhone: str
    clientEmail: str
    payment: Payment


class Kiwi(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str = Field()
