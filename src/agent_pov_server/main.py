from typing import Any, Generator

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy.orm import Session

from agent_pov_server.dao.beliefset import get_beliefset, get_beliefsets_by_experiment
from agent_pov_server.dao.experiment import (
    delete_experiment,
    get_all_experiments,
    get_experiment_detail,
)
from agent_pov_server.dao.perceiver import get_perceiver, get_perceivers_by_experiment
from agent_pov_server.schemas.beliefset import BeliefsetBase
from agent_pov_server.schemas.experiment import ExperimentBase, ExperimentDetail
from agent_pov_server.schemas.perceiver import PerceiverBase
from models.db_handler import DatabaseHandler

_app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]

_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.level("INFO")


def get_db() -> Generator[Session, Any, None]:
    db_handler = DatabaseHandler()
    try:
        yield db_handler._session
    finally:
        db_handler._session.close()


@_app.get("/health-check/")
def health_check() -> Any:
    return {"data": "yes"}


@_app.get("/experiments/", response_model=list[ExperimentBase])
def fetch_experiments(db: Session = Depends(get_db)) -> Any:
    db_experiments = get_all_experiments(db)
    return db_experiments


@_app.get("/experiments/{experiment_id}", response_model=ExperimentDetail)
def fetch_experiment_detail(experiment_id: int, db: Session = Depends(get_db)) -> Any:
    db_experiment_detail = get_experiment_detail(db, experiment_id)
    return db_experiment_detail


@_app.delete("/experiments/")
def delete_experiments(ids: str, db: Session = Depends(get_db)) -> Any:
    for experiment_id in ids.split(","):
        try:
            delete_experiment(db, int(experiment_id))
        except Exception:
            logger.error(f"Could not delete experiment with id '{experiment_id}'")


@_app.get("/beliefsets/", response_model=list[BeliefsetBase])
def fetch_beliefsets(experiment_id: int, db: Session = Depends(get_db)) -> Any:
    db_beliefsets = get_beliefsets_by_experiment(db, experiment_id)
    return db_beliefsets


@_app.get("/beliefsets/{beliefset_id}", response_model=BeliefsetBase)
def fetch_beliefset(beliefset_id: int, db: Session = Depends(get_db)) -> Any:
    db_beliefset = get_beliefset(db, beliefset_id)
    return db_beliefset


@_app.get("/perceivers/", response_model=list[PerceiverBase])
def fetch_perceivers(experiment_id: int, db: Session = Depends(get_db)) -> Any:
    db_perceivers = get_perceivers_by_experiment(db, experiment_id)
    return db_perceivers


@_app.get("/perceivers/{perceiver_id}", response_model=PerceiverBase)
def fetch_perceiver(perceiver_id: int, db: Session = Depends(get_db)) -> Any:
    db_perceiver = get_perceiver(db, perceiver_id)
    return db_perceiver


def main() -> None:
    uvicorn.run(_app, host="0.0.0.0", port=9876, log_level="error")
