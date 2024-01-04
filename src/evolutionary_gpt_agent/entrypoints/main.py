from os import getenv
from queue import Queue
from threading import Thread
from typing import cast

import toml

from data_model.api import Event
from evolutionary_gpt_agent.components.bdi.actuators_handler import GameConfig
from evolutionary_gpt_agent.components.bdi.agent import Agent
from evolutionary_gpt_agent.components.environment_listener import init_listener


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
    agent.start_loop()
