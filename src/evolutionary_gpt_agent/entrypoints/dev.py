import json
from os import getenv
from queue import Queue
from threading import Thread
from typing import cast

import toml
from deepdiff import DeepDiff

from data_model.api import Event
from evolutionary_gpt_agent.components.bdi.actuators_handler import GameConfig
from evolutionary_gpt_agent.components.bdi.agent import Agent
from evolutionary_gpt_agent.components.environment_listener import init_listener


def perceivers_refactoring(agent: Agent) -> None:
    experiment = agent._db_handler.get_experiment_by_name("A6DBB3878D80D81C")
    perceivers = agent._db_handler.get_all_perceivers(experiment)
    events_by_perceivers = agent._db_handler.get_and_group_events_by_perceivers(
        perceivers
    )

    print(
        agent._gpt_client.refactor_perceivers(
            events_by_perceivers, "perceiver_refactor"
        )
    )


def inference_rule(agent: Agent) -> None:
    experiment = agent._db_handler.get_experiment_by_name("A6DBB3878D80D81C")
    belief_sets = agent._db_handler.get_all_beliefsets(experiment)

    import pdb

    pdb.set_trace()

    belief_set_A = json.loads(json.dumps(dict(belief_sets[1].data)))
    belief_set_B = json.loads(json.dumps(dict(belief_sets[2].data)))
    # belief_set_B.data["spikes"] = [{"x": 0, "y": 1}, {"x": 5, "y": 5}]
    belief_set_B["agents sensing"] = {"agents": [{"x": 0, "y": 1}, {"x": 5, "y": 5}]}

    diff = DeepDiff(belief_set_A, belief_set_B, ignore_order=True)
    events = agent._db_handler.get_one_event_by_type_until_belief_set(belief_sets[2])

    prompt, is_event_missing = agent._gpt_client.is_event_missing(diff, events)

    prompt, event_generator = agent._gpt_client.new_event_generator(
        belief_set_A, belief_set_B, diff, "generate_event", events
    )

    import pdb

    pdb.set_trace()


def consistency_rule(agent: Agent) -> None:
    experiment = agent._db_handler.get_experiment_by_name("A6DBB3878D80D81C")
    belief_sets = agent._db_handler.get_all_beliefsets(experiment)

    prompt, consistency_rule = agent._gpt_client.new_consistency_rule(
        belief_sets[-1], "check_sat"
    )

    import pdb

    pdb.set_trace()


def main() -> None:
    events_queue: Queue[Event] = Queue()

    listener = Thread(target=init_listener, args=(events_queue,))
    listener.start()

    openai_api_key = getenv("OPENAI_API_KEY")
    openai_api_base = getenv("OPENAI_API_BASE")
    openai_api_type = getenv("OPENAI_API_TYPE")
    openai_api_version = getenv("OPENAI_API_VERSION")
    openai_deployment = getenv("OPENAI_DEPLOYMENT")
    openai_model = getenv("OPENAI_MODEL")
    game_config_raw = toml.load("./game_configuration.toml")

    game_config = cast(GameConfig, game_config_raw)

    if (
        not openai_api_key
        or not openai_api_base
        or not openai_api_type
        or not openai_api_version
        or not openai_deployment
        or not openai_model
    ):
        raise Exception("missing value in the .env config file, see .env.sample")

    if not game_config:
        raise Exception(
            "environment_configuration.toml is not following the right structure"
        )

    agent = Agent(
        events_queue,
        openai_api_key,
        openai_api_base,
        openai_api_type,
        openai_api_version,
        openai_deployment,
        openai_model,
        game_config,
    )
    # perceivers_refactoring(agent)
    # inference_rule(agent)
    consistency_rule(agent)
