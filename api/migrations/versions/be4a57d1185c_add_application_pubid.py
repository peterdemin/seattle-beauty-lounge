"""Add application pubid

Revision ID: be4a57d1185c
Revises: 907ca147cafc
Create Date: 2025-10-22 20:51:00.795230
"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "be4a57d1185c"
down_revision: Union[str, None] = "907ca147cafc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    default = uuid.UUID("0" * 32)
    op.add_column(
        "appointment",
        sa.Column(
            "pubid",
            sa.Uuid(),
            nullable=False,
            server_default=default.hex,
        ),
    )
    backfill(default)
    op.create_index(op.f("ix_appointment_pubid"), "appointment", ["pubid"], unique=True)


def backfill(default) -> None:
    t_appointment = sa.Table(
        "appointment",
        sa.MetaData(),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "pubid",
            sa.Uuid(),
            nullable=False,
        ),
    )
    connection = op.get_bind()
    records = connection.execute(
        t_appointment.select().where(t_appointment.c.pubid == default)
    ).fetchall()
    for record in records:
        connection.execute(
            t_appointment.update()
            .where(t_appointment.c.id == record.id)
            .values(
                pubid=uuid.uuid4(),
            )
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_appointment_pubid"), table_name="appointment")
    op.drop_column("appointment", "pubid")
