from queue import Queue
from threading import Thread

from evolutionary_gpt_agent.components.bdi.agent import Agent
from evolutionary_gpt_agent.components.environment_listener import init_listener


def main() -> None:
    events_queue = Queue()

    listener = Thread(target=init_listener, args=(events_queue,))
    listener.start()

    agent = Agent(events_queue)
    agent.start_loop()
