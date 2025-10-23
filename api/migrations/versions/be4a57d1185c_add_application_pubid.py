"""Add application pubid

Revision ID: be4a57d1185c
Revises: 907ca147cafc
Create Date: 2025-10-22 20:51:00.795230
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = "be4a57d1185c"
down_revision: Union[str, None] = "907ca147cafc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "appointment",
        sa.Column(
            "pubid",
            sa.Uuid(),
            server_default=func.gen_random_uuid(),
            nullable=True,
        ),
    )
    op.create_index(
        op.f("ix_appointment_pubid"),
        "appointment",
        ["pubid"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_appointment_pubid"), table_name="appointment")
    op.drop_column("appointment", "pubid")
