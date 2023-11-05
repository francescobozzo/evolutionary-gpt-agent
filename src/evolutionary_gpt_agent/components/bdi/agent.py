import random
from queue import Queue

from evolutionary_gpt_agent.components.db_handler import DatabaseHandler
from evolutionary_gpt_agent.components.gpt_client import Client
from models.db.models import Experiment
from models.mappers import api_event_to_db_event


class Agent:
    def __init__(
        self,
        events_queue: Queue,
        openai_api_key: str,
        openai_api_base: str,
        openai_api_type: str,
        openai_api_version: str,
        openai_deployment: str,
        openai_model: str,
    ):
        self._events_queue = events_queue
        self._db_handler = DatabaseHandler()
        self._experiment = Experiment(
            name="".join(random.choice("0123456789ABCDEF") for i in range(16))
        )
        self._gpt_client = Client()

    def start_loop(self):
        # while True:
        self._db_handler.insert(self._experiment)
        import time

        time.sleep(5)
        events = [self._events_queue.get() for _ in range(self._events_queue.qsize())]

        last_event = None
        for e in events:
            dbEvent = api_event_to_db_event(e, self._experiment, last_event)
            self._db_handler.insert(dbEvent)
            last_event = dbEvent
