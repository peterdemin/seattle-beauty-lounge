"""reminded_at

Revision ID: f6d14fcf9ae3
Revises: 57feef9cbfef
Create Date: 2025-01-06 10:21:48.626154
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f6d14fcf9ae3"
down_revision: Union[str, None] = "57feef9cbfef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "appointment",
        sa.Column(
            "remindedAt",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("appointment", "remindedAt")
