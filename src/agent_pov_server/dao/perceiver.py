from typing import Any

from sqlalchemy.orm import Session

from data_model.db.models import Perceiver


def get_perceiver(db: Session, perceiver_id: int) -> Perceiver | Any:
    db_perceiver = (
        db.query(Perceiver).filter(Perceiver.perceiver_id == perceiver_id).first()
    )
    return db_perceiver


def get_perceivers_by_experiment(db: Session, experiment_id: int) -> list[Perceiver]:
    db_perceivers: list[Perceiver] = (
        db.query(Perceiver).filter(Perceiver.experiment_id == experiment_id).all()
    )
    return db_perceivers
