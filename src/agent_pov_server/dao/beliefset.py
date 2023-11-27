from sqlalchemy.orm import Session

from models.db.models import BeliefSet


def get_beliefset(db: Session, beliefset_id: int) -> BeliefSet | None:
    db_beliefset = (
        db.query(BeliefSet).filter(BeliefSet.belief_set_id == beliefset_id).first()
    )
    return db_beliefset


def get_beliefsets_by_experiment(db: Session, experiment_id: int) -> list[BeliefSet]:
    db_beliefsets: list[BeliefSet] = (
        db.query(BeliefSet).filter(BeliefSet.experiment_id == experiment_id).all()
    )
    return db_beliefsets
