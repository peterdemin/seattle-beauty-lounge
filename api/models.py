from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serviceId: str
    date: date
    time: str
    clientName: str
    clientPhone: str
    clientEmail: str


class AppointmentCreate(SQLModel):
    serviceId: str
    date: date
    time: str
    clientName: str
    clientPhone: str
    clientEmail: str


class Kiwi(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str = Field()
