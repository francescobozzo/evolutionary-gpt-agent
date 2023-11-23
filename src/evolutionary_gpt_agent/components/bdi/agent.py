import random
from queue import Queue
from time import sleep

from loguru import logger

from evolutionary_gpt_agent.components.bdi.actuators_handler import (
    ActuatorHandler,
    GameConfig,
)
from evolutionary_gpt_agent.components.bdi.tester import CodeTester
from evolutionary_gpt_agent.components.gpt_client import Client, load_prompt_templates
from models.api import Event
from models.db.models import BeliefSet, Checkpoint
from models.db.models import Event as DbEvent
from models.db.models import Experiment, Perceiver
from models.db.models import Plan as DbPlan
from models.db_handler import DatabaseHandler
from models.mappers import api_event_to_db_event

_SLEEP_FOR_FIRST_EVENT = 1
_SLEEP_FOR_EVENTS_BATCH = 1
_EVENTS_BATCH_SIZE = 3


def divide_into_batches(queue: Queue[Event], batch_size: int) -> list[list[Event]]:
    num_batches = queue.qsize()

    batches: list[list[Event]] = []

    for i in range(num_batches):
        batches.append([])
        for j in range(batch_size):
            batches[i].append(queue.get())

    return batches


class Agent:
    def __init__(
        self,
        events_queue: Queue[Event],
        openai_api_key: str,
        openai_api_base: str,
        openai_api_type: str,
        openai_api_version: str,
        openai_deployment: str,
        openai_model: str,
        game_config: GameConfig,
    ):
        self._events_queue = events_queue
        self._db_handler = DatabaseHandler()
        self._actuators_handler = ActuatorHandler(game_config)
        self._experiment = Experiment(
            name="".join(random.choice("0123456789ABCDEF") for i in range(16))
        )
        self._gpt_client = Client(
            openai_api_key,
            openai_api_base,
            openai_api_type,
            openai_api_version,
            openai_deployment,
            openai_model,
        )

        self._belief_set = BeliefSet(data={}, experiment=self._experiment)
        self._perceiver_version = 0
        self._plan_version = 0
        self._prompt_templates_by_type = load_prompt_templates(self._experiment)
        self._checkpoint: Checkpoint | None = None
        self._last_event: DbEvent | None = None
        self._plan: list[str] = []

    def start_loop(self) -> None:
        first_event: Event | None = self._bdi_loop_setup()

        while True:
            while self._events_queue.qsize() < _EVENTS_BATCH_SIZE:
                logger.info(
                    "waiting for new events"
                    f" {self._events_queue.qsize()}/{_EVENTS_BATCH_SIZE}"
                )
                sleep(_SLEEP_FOR_EVENTS_BATCH)

            event_batches = divide_into_batches(self._events_queue, _EVENTS_BATCH_SIZE)

            if first_event:
                event_batches[0].insert(0, first_event)
                first_event = None

            for batch in event_batches:
                self._process_event_batch(batch)

            self._new_plan()
            self._execute_plan()

    def _bdi_loop_setup(self) -> Event:
        self._db_handler.insert([self._experiment])
        for perceiver_prompt in self._prompt_templates_by_type.values():
            self._db_handler.insert([perceiver_prompt])

        self._db_handler.refresh()

        while self._events_queue.qsize() > 0:
            sleep(_SLEEP_FOR_FIRST_EVENT)

        event = self._events_queue.get()

        self._current_checkpoint = Checkpoint(
            experiment=self._experiment,
            checkpoint_type="begin",
            game_dump=event.game_dump,
        )

        self._db_handler.insert([self._belief_set, self._current_checkpoint])
        self._db_handler.refresh()

        return event

    def _process_event_batch(self, events: list[Event]) -> None:
        db_events = []

        for event in events:
            db_event = api_event_to_db_event(event, self._experiment, self._last_event)
            db_events.append(db_event)

            self._last_event = db_event

        self._db_handler.insert(db_events)

        json_events = [e.to_json() for e in events]
        dict_events = [e.to_dict() for e in events]

        perceiver_valid = False
        while not perceiver_valid:
            perceiver_name = f"perceiver_{self._perceiver_version}"
            perceiver_prompt, perceiver_code = self._gpt_client.ask_perceiver(
                perceiver_name, self._belief_set.data, "\n".join(json_events)
            )

            FIRST_EVENT_INDEX = 0
            LAST_EVENT_INDEX = -1

            perceiver = CodeTester(
                perceiver_code,
                perceiver_name,
            )
            if perceiver.is_valid(events=dict_events, belief_set=self._belief_set.data):
                new_belief_set_data = perceiver(
                    events=dict_events, belief_set=self._belief_set.data
                )
            else:
                logger.warning(f"Perceiver {perceiver_name} not valid, trying again.")
                continue

            if not self._last_event:
                raise Exception("no last event, this is completely unexpected")

            self._checkpoint = Checkpoint(
                experiment=self._experiment,
                checkpoint_type="perceiver",
                game_dump=self._last_event.game_dump,
            )

            previous_belief_set = self._belief_set
            self._belief_set = BeliefSet(
                data=new_belief_set_data, experiment=self._experiment
            )

            self._db_handler.insert([self._checkpoint, self._belief_set])
            self._db_handler.refresh()

            perceiver_model = Perceiver(
                belief_set_input_id=previous_belief_set.belief_set_id,
                belief_set_output_id=self._belief_set.belief_set_id,
                start_event_id=db_events[FIRST_EVENT_INDEX].event_id,
                end_event_id=db_events[LAST_EVENT_INDEX].event_id,
                experiment=self._experiment,
                code=perceiver_code,
                prompt_template=self._prompt_templates_by_type["new_perceiver"],
                prompt=perceiver_prompt,
                checkpoint=self._checkpoint,
            )

            self._db_handler.insert([perceiver_model])
            self._perceiver_version += 1
            perceiver_valid = True

    def _new_plan(self) -> None:
        plan_valid = False
        while not plan_valid:
            plan_name = f"plan_{self._plan_version}"
            plan_prompt, plan_code = self._gpt_client.ask_plan(
                plan_name, self._belief_set.data
            )

            plan = CodeTester(plan_code, plan_name)

            if plan.is_valid(belief_set=self._belief_set.data):
                self._plan = plan(belief_set=self._belief_set.data)
                if not self._last_event:
                    raise Exception("no last event, this is completely unexpected")

                self._checkpoint = Checkpoint(
                    experiment=self._experiment,
                    checkpoint_type="plan",
                    game_dump=self._last_event.game_dump,
                )

                self._db_handler.insert([self._checkpoint])
                self._db_handler.refresh()

                plan_model = DbPlan(
                    belief_set_input_id=self._belief_set.belief_set_id,
                    belief_set_output_id=self._belief_set.belief_set_id,
                    experiment=self._experiment,
                    code=plan_code,
                    prompt_template=self._prompt_templates_by_type["expand_goal"],
                    prompt=plan_prompt,
                    checkpoint=self._checkpoint,
                )

                self._db_handler.insert([plan_model])
                self._plan_version += 1
                plan_valid = True

    def _execute_plan(self) -> None:
        while self._plan:
            response = self._actuators_handler.actuate(self._plan[0])
            is_blocking = self._actuators_handler.is_action_blocking(self._plan[0])
            if not is_blocking or (is_blocking and response is not None):
                self._plan = self._plan[1:]
