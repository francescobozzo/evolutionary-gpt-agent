"""perceiver

Revision ID: 14c9b1f5fa23
Revises: 4f24a0671402
Create Date: 2023-11-05 10:49:49.920269

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "14c9b1f5fa23"
down_revision: Union[str, None] = "4f24a0671402"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "belief_sets",
        sa.Column("belief_set_id", sa.Integer(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("belief_set_id"),
    )
    op.create_table(
        "checkpoints",
        sa.Column("checkpoint_id", sa.Integer(), nullable=False),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("checkpoint_type", sa.String(), nullable=False),
        sa.Column("game_dump", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["experiment_id"],
            ["experiments.experiment_id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["checkpoints.checkpoint_id"],
        ),
        sa.PrimaryKeyConstraint("checkpoint_id"),
    )
    op.create_table(
        "prompt_templates",
        sa.Column("prompt_template_id", sa.Integer(), nullable=False),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("template_type", sa.String(), nullable=False),
        sa.Column("template", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["experiment_id"],
            ["experiments.experiment_id"],
        ),
        sa.PrimaryKeyConstraint("prompt_template_id"),
    )
    op.create_table(
        "perceivers",
        sa.Column("perceiver_id", sa.Integer(), nullable=False),
        sa.Column("belief_set_input_id", sa.Integer(), nullable=False),
        sa.Column("belief_set_output_id", sa.Integer(), nullable=False),
        sa.Column("start_event_id", sa.Integer(), nullable=False),
        sa.Column("end_event_id", sa.Integer(), nullable=False),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("prompt_template_id", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["belief_set_input_id"],
            ["belief_sets.belief_set_id"],
        ),
        sa.ForeignKeyConstraint(
            ["belief_set_output_id"],
            ["belief_sets.belief_set_id"],
        ),
        sa.ForeignKeyConstraint(
            ["end_event_id"],
            ["events.event_id"],
        ),
        sa.ForeignKeyConstraint(
            ["experiment_id"],
            ["experiments.experiment_id"],
        ),
        sa.ForeignKeyConstraint(
            ["prompt_template_id"],
            ["prompt_templates.prompt_template_id"],
        ),
        sa.ForeignKeyConstraint(
            ["start_event_id"],
            ["events.event_id"],
        ),
        sa.PrimaryKeyConstraint("perceiver_id"),
    )


def downgrade() -> None:
    op.drop_table("perceivers")
    op.drop_table("prompt_templates")
    op.drop_table("checkpoints")
    op.drop_table("belief_sets")
