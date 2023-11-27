from loguru import logger
from sqlalchemy.orm import Session

from models.db.models import Experiment


def get_all_experiments(db: Session) -> list[Experiment]:
    db_experiments: list[Experiment] = (
        db.query(Experiment).order_by(Experiment.timestamp.desc()).all()
    )
    return db_experiments


def delete_experiment(db: Session, experiment_id: int) -> bool:
    try:
        db.query(Experiment).filter(Experiment.experiment_id == experiment_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(e)
        return False

    return True
