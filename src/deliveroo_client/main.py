from threading import Thread

from deliveroo_client.components.agent_to_environment import (
    init_agent_to_environment_listener,
)
from deliveroo_client.components.environment_to_agent import (
    init_environment_to_agent_listener,
)
from deliveroo_client.components.socket_client import sio, token


def main() -> None:
    sio.connect("http://deliveroo:8080", headers={"x-token": token})

    listener = Thread(target=init_agent_to_environment_listener)
    listener.start()

    init_environment_to_agent_listener()
