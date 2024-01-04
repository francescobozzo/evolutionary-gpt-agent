from typing import Optional

from loguru import logger
from sqlalchemy.orm import Session

from agent_pov_server.schemas.experiment import ExperimentDetail
from data_model.db.models import Experiment


def get_all_experiments(db: Session) -> list[Experiment]:
    db_experiments: list[Experiment] = (
        db.query(Experiment).order_by(Experiment.timestamp.desc()).all()
    )
    return db_experiments


def get_experiment_detail(
    db: Session, experiment_id: int
) -> Optional[ExperimentDetail]:
    db_experiment = (
        db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    )

    if not db_experiment:
        return None

    return ExperimentDetail(
        experiment_id=db_experiment.experiment_id,
        name=db_experiment.name,
        timestamp=db_experiment.timestamp,
        num_events=len(db_experiment.events),
        num_beliefsets=len(db_experiment.belief_sets),
        num_perceivers=len(db_experiment.perceivers),
        num_plans=len(db_experiment.plans),
    )


def delete_experiment(db: Session, experiment_id: int) -> bool:
    try:
        db.query(Experiment).filter(Experiment.experiment_id == experiment_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(e)
        return False

    return True
    return True
