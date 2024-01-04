from os import getenv
from typing import TypeAlias

from loguru import logger
from sqlalchemy import create_engine, select
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session, sessionmaker

from data_model.db.models import (
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

    def get_all_experiments(self) -> list[Experiment]:
        return [row[0] for row in self._session.execute(select(Experiment)).all()]

    def get_experiment_by_name(self, name: str) -> Experiment:
        experiment = self._session.execute(
            select(Experiment).where(Experiment.name == name)
        ).one()[0]

        if not isinstance(experiment, Experiment):
            raise Exception(f"not able to fetch experiment {name} from db")

        return experiment

    def get_all_perceivers(self, experiment: Experiment) -> list[Perceiver]:
        return [
            row[0]
            for row in self._session.execute(
                select(Perceiver).where(Perceiver.experiment == experiment)
            ).all()
        ]

    def get_all_beliefsets(self, experiment: Experiment) -> list[BeliefSet]:
        return [
            row[0]
            for row in self._session.execute(
                select(BeliefSet).where(BeliefSet.experiment == experiment)
            ).all()
        ]

    def get_one_event_by_type_until_belief_set(
        self, belief_set: BeliefSet
    ) -> list[Event]:
        perceiver = self._session.execute(
            select(Perceiver).where(
                Perceiver.belief_set_output_id == belief_set.belief_set_id
            )
        ).first()[0]
        events = [
            row[0]
            for row in self._session.execute(
                select(Event).where(Event.event_id <= perceiver.end_event_id)
            ).all()
        ]

        event_by_type = {}
        for e in events:
            event_by_type[e.origin] = e

        return list(event_by_type.values())

    def get_and_group_events_by_perceivers(
        self, perceivers: list[Perceiver]
    ) -> dict[Perceiver, list[Event]]:
        events_by_perceivers: dict[Perceiver, list[Event]] = {}

        for perceiver in perceivers:
            events = [
                event[0]
                for event in self._session.execute(
                    select(Event).filter(
                        Event.event_id >= perceiver.start_event_id,
                        Event.event_id <= perceiver.end_event_id,
                    )
                ).all()
            ]
            events_by_perceivers[perceiver] = events

        return events_by_perceivers
