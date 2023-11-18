from datetime import datetime
from typing import Any

import requests

from deliveroo_client.components.socket_client import sio

url_gpt_evolve = "http://agent:8000"


@sio.on("*")
def catch_all(event: str, *data: dict[str, Any]) -> None:
    event_endpoint = f"{url_gpt_evolve}/event"
    if event == "map":
        description = (
            "Map composition. The map is divided into tiles,"
            " one action move you (the agent) of one tile. There are"
            " three different types of tile: walkable, not-walkable,"
            " and delivery zones. You can move on walkable (or valid"
            " tiles) but you cannot move on not-walkable tiles (not"
            " valid)"
        )
        game_map: list[Any] = []

        for tile in data[2]:
            game_map.append(tile)
            game_map[-1]["valid"] = True

        requests.post(
            event_endpoint,
            json={
                "origin": "map",
                "data": {"data": game_map},
                "game_dump": {},
                "description": description,
                "received_date": datetime.now().timestamp(),
            },
        )
    elif event == "parcels sensing":
        requests.post(
            event_endpoint,
            json={
                "origin": event,
                "data": {"parcels": data[0]["parcels"]},
                "game_dump": data[0].get("game_dump", {}),
                "description": "Event associated to parcels",
                "received_date": datetime.now().timestamp(),
            },
        )
    elif event == "agents sensing":
        requests.post(
            event_endpoint,
            json={
                "origin": event,
                "data": {"agents": data[0]["agents"]},
                "game_dump": data[0].get("game_dump", {}),
                "description": "Event associated to agents",
                "received_date": datetime.now().timestamp(),
            },
        )
    elif event == "you":
        if isinstance(data[0]["x"], int) and isinstance(data[0]["y"], int):
            requests.post(
                event_endpoint,
                json={
                    "origin": "myself",
                    "data": data[0],
                    "game_dump": {},
                    "description": "Update of yourself",
                    "received_date": datetime.now().timestamp(),
                },
            )
        else:
            print("Not sending event with float data:", event, data)


def init_environment_to_agent_listener() -> None:
    sio.wait()
