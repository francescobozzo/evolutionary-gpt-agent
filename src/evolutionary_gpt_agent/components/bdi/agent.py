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

        self._belief_set = {}

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

    # def new_perceiver(self):
    #     print(
    #         f"asking new perceiver to gpt {events_queue.qsize()}",
    #     )
    #     name = f"perceiver_{app.num_perceivers}"

    #     prompt = _load_prompt(_PREFIX_PROMPT, _NEW_EVENT_PROMPT)
    #     prompt = prompt.format(
    #         "\n".join([event.to_json() for event in events]),
    #         json.dumps(beliefset),
    #         name,
    #     )
    #     perceiver_code = app.client.ask(prompt)

    #     perceiver_code = clean_received_python_code(perceiver_code)

    #     perceiver = Perceiver(name, perceiver_code, "", None, "")
    #     perceiver.save_to_file()
    #     perceiver.load_function()
    #     new_belief_set = perceiver.test_code(
    #         [event.to_dict() for event in events],
    #         beliefset,
    #     )

    #     if new_belief_set != {}:
    #         app.current_beliefset = new_belief_set
    #         app.beliefset_history[app.checkpoint_index] = new_belief_set
    #     else:
    #         app.client.invalidate_last_exchange()

    #         print("perceiver received", flush=True)
