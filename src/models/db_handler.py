from os import getenv
from typing import TypeAlias

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session, sessionmaker

from models.db.models import (
    BeliefSet,
    Checkpoint,
    Event,
    Experiment,
    Perceiver,
    Plan,
    PromptTemplate,
)

_Message: TypeAlias = (
    Experiment | Event | Checkpoint | BeliefSet | Perceiver | PromptTemplate | Plan
)


class DatabaseHandler:
    _engine: Engine | None

    def __init__(self) -> None:
        self._engine = None
        while self._engine is None:
            try:
                self._engine = create_engine(
                    f"postgresql+psycopg2://{getenv('POSTGRES_USER')}:"
                    f"{getenv('POSTGRES_PASSWORD')}@{getenv('DB_ADDRESS')}"
                    f":5432/{getenv('POSTGRES_DB')}"
                )
            except Exception as e:
                logger.debug(f"initializing postgres engine {e}")
        self._session: Session = sessionmaker(self._engine, expire_on_commit=False)(
            expire_on_commit=False
        )

    def insert(self, messages: list[_Message]) -> None:
        try:
            for msg in messages:
                self._session.add(msg)
                logger.info(f"new {type(msg).__name__} inserted in the database")

        except Exception as e:
            logger.error(f"unable to insert data inside the databse: {e}")
            self._session.rollback()
            raise
        else:
            self._session.commit()

    def refresh(self) -> None:
        self._session.flush()

        logger.info("postgres session flushed")
