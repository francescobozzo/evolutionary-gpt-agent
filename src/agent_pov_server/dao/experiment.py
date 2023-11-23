from sqlalchemy.orm import Session

from models.db.models import Experiment


def get_all_experiments(db: Session) -> list[Experiment]:
    db_experiments: list[Experiment] = db.query(Experiment).all()
    return db_experiments
