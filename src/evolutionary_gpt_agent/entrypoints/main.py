from os import getenv
from queue import Queue
from threading import Thread

from evolutionary_gpt_agent.components.bdi.agent import Agent
from evolutionary_gpt_agent.components.environment_listener import init_listener


def main() -> None:
    events_queue = Queue()

    listener = Thread(target=init_listener, args=(events_queue,))
    listener.start()

    openai_api_key = getenv("OPENAI_API_KEY")
    openai_api_base = getenv("OPENAI_API_BASE")
    openai_api_type = getenv("OPENAI_API_TYPE")
    openai_api_version = getenv("OPENAI_API_VERSION")
    openai_deployment = getenv("OPENAI_DEPLOYMENT")
    openai_model = getenv("OPENAI_MODEL")

    agent = Agent(
        events_queue,
        openai_api_key,
        openai_api_base,
        openai_api_type,
        openai_api_version,
        openai_deployment,
        openai_model,
    )
    agent.start_loop()
