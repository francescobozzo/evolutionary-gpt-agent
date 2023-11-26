import random
from itertools import chain
from queue import Queue
from time import sleep
from typing import Any

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
_EVENTS_BATCH_SIZE = 5
_NEW_EVENTS_THRESHOLD = 30
_EVENTS_RESET_THRESHOLD = 1000
_REFACTORED_PERCEIVER_NAME = "refactored_perceiver"


def divide_into_batches(queue: Queue[Event], batch_size: int) -> list[list[Event]]:
    num_batches = queue.qsize() // batch_size

    batches: list[list[Event]] = []

    for i in range(num_batches):
        batches.append([])
        for j in range(batch_size):
            batches[i].append(queue.get())

    return batches


class EventSet:
    def __init__(self, new_events_threshold: int, reset_threshold: int) -> None:
        self._event_types: set[str] = set()
        self._new_events_threshold = new_events_threshold
        self._remaining_events = self._new_events_threshold
        self._reset_threshold = reset_threshold
        self._reset_done = 0

    def add(self, origin: str) -> None:
        if origin not in self._event_types:
            self._remaining_events = self._new_events_threshold
            self._event_types.add(origin)
        else:
            self._remaining_events -= 1

    def should_use_refactored_perceiver(self) -> bool:
        return self._remaining_events <= 0

    def should_reset(self) -> bool:
        return self._remaining_events <= -self._reset_threshold

    def reset(self) -> None:
        self._remaining_events = self._new_events_threshold
        self._event_types.clear()
        self._reset_done += 1
        self._reset_threshold = int(
            self._reset_threshold * 2**self._reset_done * random.uniform(0, 1)
        )

    def get_reset_threshold(self) -> int:
        return self._reset_threshold


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
            game_config["environment"]["prompt_prefix"],
        )

        self._belief_set = BeliefSet(data={}, experiment=self._experiment)
        self._refactored_perceiver: Perceiver | None = None
        self._perceiver_version = 0
        self._plan_version = 0
        self._prompt_templates_by_type = load_prompt_templates(
            self._experiment, game_config["environment"]["prompt_prefix"]
        )
        self._checkpoint: Checkpoint | None = None
        self._last_event: DbEvent | None = None
        self._plan: list[str] = []
        self._event_types: EventSet = EventSet(
            _NEW_EVENTS_THRESHOLD, _EVENTS_RESET_THRESHOLD
        )

    def start_loop(self) -> None:
        first_event: Event | None = self._bdi_loop_setup()

        while True:
            while self._events_queue.qsize() < _EVENTS_BATCH_SIZE:
                logger.info(
                    "waiting for new events"
                    f" {self._events_queue.qsize()}/{_EVENTS_BATCH_SIZE}"
                )
                sleep(_SLEEP_FOR_EVENTS_BATCH)
            logger.info("dividing events into batches")

            event_batches = divide_into_batches(self._events_queue, _EVENTS_BATCH_SIZE)

            if first_event:
                event_batches[0].insert(0, first_event)
                first_event = None

            for i, batch in enumerate(event_batches):
                logger.info(f"processing batch {i}/{len(event_batches)}")
                self._process_event_batch(batch)
                if (
                    self._event_types.should_use_refactored_perceiver()
                    and self._refactored_perceiver is None
                ):
                    self._refactor_perceivers()

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
        self._event_types.add(event.origin)

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
            self._event_types.add(event.origin)
            db_event = api_event_to_db_event(event, self._experiment, self._last_event)
            db_events.append(db_event)

            self._last_event = db_event

        if self._event_types.should_reset():
            self._event_types.reset()
            logger.info("resetting refactored perceiver")

        self._db_handler.insert(db_events)

        json_events = [e.to_json() for e in events]
        dict_events = [e.to_dict() for e in events]

        is_perceiver_valid = False
        while not is_perceiver_valid:
            if (
                not self._event_types.should_use_refactored_perceiver()
                or self._refactored_perceiver is None
            ):
                perceiver_name = f"perceiver_{self._perceiver_version}"
                logger.info(f"asking for perceiver {perceiver_name}")

                perceiver_prompt, perceiver_code = self._gpt_client.ask_perceiver(
                    perceiver_name, self._belief_set.data, "\n".join(json_events)
                )
            else:
                if self._refactored_perceiver is None:
                    raise Exception(
                        "Trying to reuse a refactored perceiver that"
                        " was never initialized."
                    )
                perceiver_name = _REFACTORED_PERCEIVER_NAME
                perceiver_prompt = self._refactored_perceiver.prompt
                perceiver_code = self._refactored_perceiver.code
                logger.info(f"using refactored perceiver {perceiver_name}")

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
            if perceiver_name != _REFACTORED_PERCEIVER_NAME:
                self._perceiver_version += 1
            is_perceiver_valid = True

    def _refactor_perceivers(self) -> None:
        is_perceiver_valid = False
        perceivers = self._db_handler.get_all_perceivers(self._experiment)
        events_by_perceivers = self._db_handler.get_and_group_events_by_perceivers(
            perceivers
        )

        dict_events: list[Any] = [
            {"data": e.data, "type": e.origin, "description": e.description}
            for e in chain(*events_by_perceivers.values())
        ]

        logger.info(
            "refactoring perceivers, it will be used for the next"
            f" {self._event_types.get_reset_threshold()} events"
        )
        while not is_perceiver_valid:
            perceiver_name = _REFACTORED_PERCEIVER_NAME

            perceiver_prompt, perceiver_code = self._gpt_client.refactor_perceivers(
                events_by_perceivers, perceiver_name
            )
            perceiver = CodeTester(
                perceiver_code,
                perceiver_name,
            )

            if not perceiver.is_valid(
                events=dict_events, belief_set=self._belief_set.data
            ):
                logger.warning("refactored perceiver not valid, trying again.")
                continue

            perceiver = Perceiver(
                prompt=perceiver_prompt,
                code=perceiver_code,
            )

            self._refactored_perceiver = perceiver
            is_perceiver_valid = True

    def _new_plan(self) -> None:
        is_plan_valid = False
        while not is_plan_valid:
            plan_name = f"plan_{self._plan_version}"
            logger.info(f"asking for plan {plan_name}")
            try:
                plan_prompt, plan_code = self._gpt_client.ask_plan(
                    plan_name, self._belief_set.data
                )
            except Exception:
                logger.warning("unalbe to retrieve a plan")
                continue

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
                    actions=",".join(self._plan),
                )

                self._db_handler.insert([plan_model])
                self._plan_version += 1
                is_plan_valid = True

    def _execute_plan(self) -> None:
        while self._plan:
            response = self._actuators_handler.actuate(self._plan[0])
            is_blocking = self._actuators_handler.is_action_blocking(self._plan[0])
            if not is_blocking or (is_blocking and response is not None):
                self._plan = self._plan[1:]
