from sqlalchemy.orm import Session

from agent_pov_server.schemas.checkpoint import CheckpointAttributesBase, CheckpointBase
from data_model.db.models import Checkpoint as CheckpointDb


def get_checkpoint_tree_by_experiment(
    db: Session, experiment_id: int
) -> CheckpointBase | None:
    db_checkpoints = _get_db_checkpoint_list_by_experiment(db, experiment_id)
    if not db_checkpoints:
        return None

    nodes = {
        db_checkpoint.checkpoint_id: CheckpointBase(
            name="test",
            attributes=CheckpointAttributesBase(
                id=db_checkpoint.checkpoint_id, type=db_checkpoint.checkpoint_type
            ),
            children=[],
        )
        for db_checkpoint in db_checkpoints
    }

    root_id = None
    for db_checkpoint in db_checkpoints:
        if db_checkpoint.parent_id is not None:
            nodes[db_checkpoint.parent_id].children.append(
                nodes[db_checkpoint.checkpoint_id]
            )
        else:
            root_id = db_checkpoint.checkpoint_id

    return nodes[root_id] if root_id else None


def _get_db_checkpoint_list_by_experiment(
    db: Session, experiment_id: int
) -> list[CheckpointDb]:
    db_checkpoints: list[CheckpointDb] = (
        db.query(CheckpointDb).filter(CheckpointDb.experiment_id == experiment_id).all()
    )
    return db_checkpoints
