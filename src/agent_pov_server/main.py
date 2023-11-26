from typing import Any, Generator

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy.orm import Session

from agent_pov_server.dao.experiment import get_all_experiments
from agent_pov_server.schemas.experiment import ExperimentBase
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


def main() -> None:
    uvicorn.run(_app, host="0.0.0.0", port=9876, log_level="error")
