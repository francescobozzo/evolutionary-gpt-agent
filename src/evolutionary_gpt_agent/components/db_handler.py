from os import getenv

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from models.db.models import Event, Experiment

# from models.models import (
#     Experiment,
#     Event,
#     Plan,
#     Checkpoint,
#     BeliefSet,
#     Perceiver,
#     PromptTemplates,
# )

# _Message = (
#     Experiment
#     | Event
#     | Plan
#     | Checkpoint
#     | BeliefSet
#     | Perceiver
#     | PromptTemplates
# )


_Message = Experiment | Event


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
                print(e)
        self._session = sessionmaker(self._engine, expire_on_commit=False)(
            expire_on_commit=False
        )

    def enque(self, *messages: _Message):
        for msg in messages:
            self._message_queue.append(msg)

    def insert(self, messages: list[_Message]):
        # self._session.begin()

        try:
            for msg in messages:
                self._session.add(msg)
        except Exception as e:
            print(f"unable to insert data inside the databse: {e}", flush=True)
            self._session.rollback()
            raise
        else:
            self._session.commit()

    def get_last_checkpoint():
        ...

    def refresh(self):
        self._session.flush()


# if __name__ == "__main__":
