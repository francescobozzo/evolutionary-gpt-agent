"""experiment-event

Revision ID: 4f24a0671402
Revises:
Create Date: 2023-11-04 17:45:32.163743

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "4f24a0671402"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "experiments",
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("experiment_id"),
    )
    op.create_table(
        "events",
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("received_date", sa.DateTime(), nullable=False),
        sa.Column("processed_date", sa.DateTime(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("origin", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["experiment_id"],
            ["experiments.experiment_id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["events.event_id"],
        ),
        sa.PrimaryKeyConstraint("event_id"),
    )


def downgrade() -> None:
    op.drop_table("events")
    op.drop_table("experiments")
