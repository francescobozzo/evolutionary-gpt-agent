from typing import Any, TypedDict

import requests


class _Environment(TypedDict):
    prompt_prefix: str


class _Action(TypedDict):
    host: str
    sync: bool
    with_response: bool


class GameConfig(TypedDict):
    environment: _Environment
    actions: dict[str, _Action]


class ActuatorHandler:
    def __init__(self, game_config: GameConfig) -> None:
        self._game_config = game_config

    def actuate(self, action: str) -> Any:
        if action not in self._game_config["actions"]:
            raise Exception(
                f"{action} is not described in the environment configuartion file"
            )

        host = self._game_config["actions"][action]["host"]
        response = requests.get(host)

        if (
            self._game_config["actions"][action]["with_response"]
            and response.status_code == 200
        ):
            return response.content

        return
