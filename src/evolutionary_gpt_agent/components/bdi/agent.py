import random
from queue import Queue

from evolutionary_gpt_agent.components.bdi.tester import CodeTester
from evolutionary_gpt_agent.components.db_handler import DatabaseHandler
from evolutionary_gpt_agent.components.gpt_client import Client, load_prompt_templates
from models.db.models import BeliefSet, Checkpoint, Experiment, Perceiver
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
        self._gpt_client = Client(
            openai_api_key,
            openai_api_base,
            openai_api_type,
            openai_api_version,
            openai_deployment,
            openai_model,
        )

        self._belief_sets = [BeliefSet(data={}, experiment=self._experiment)]
        self._perceiver_version = 0
        self._prompt_templates_by_type = load_prompt_templates(self._experiment)
        self._checkpoints = []

    def start_loop(self):
        self._db_handler.insert([self._experiment])
        for perceiver_prompt in self._prompt_templates_by_type.values():
            self._db_handler.insert([perceiver_prompt])

        self._db_handler.insert([self._belief_sets[-1]])

        import time

        time.sleep(5)
        events = [self._events_queue.get() for _ in range(self._events_queue.qsize())]
        db_events = []

        last_event = None
        for e in events:
            db_event = api_event_to_db_event(e, self._experiment, last_event)
            db_events.append(db_event)
            last_event = db_event
        self._db_handler.insert(db_events)

        json_events = [e.to_json() for e in events]
        dict_events = [e.to_dict() for e in events]

        perceiver_name = f"perceiver_{self._perceiver_version}"
        perceiver_prompt, perceiver_code = self._gpt_client.ask_perceiver(
            perceiver_name, self._belief_sets[-1].data, "\n".join(json_events)
        )

        perceiver = CodeTester(
            perceiver_code,
            perceiver_name,
        )

        if perceiver.is_valid(
            events=dict_events, belief_set=self._belief_sets[-1].data
        ):
            new_belief_set_data = perceiver(
                events=dict_events, belief_set=self._belief_sets[-1].data
            )
            self._checkpoints.append(
                Checkpoint(
                    experiment=self._experiment,
                    checkpoint_type="perceiver",
                    game_dump=events[-1].game_dump,
                )
            )
            self._belief_sets.append(
                BeliefSet(data=new_belief_set_data, experiment=self._experiment)
            )
            self._db_handler.insert([self._checkpoints[-1], self._belief_sets[-1]])
            self._db_handler.refresh()

            perceiver_model = Perceiver(
                belief_set_input_id=self._belief_sets[-2].belief_set_id,
                belief_set_output_id=self._belief_sets[-1].belief_set_id,
                start_event_id=db_events[0].event_id,
                end_event_id=db_events[-1].event_id,
                experiment=self._experiment,
                code=perceiver_code,
                prompt_template=self._prompt_templates_by_type["new_perceiver"],
                prompt=perceiver_prompt,
                checkpoint=self._checkpoints[-1],
            )
            self._db_handler.insert([perceiver_model])

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
