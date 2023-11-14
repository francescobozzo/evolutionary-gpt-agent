import logging
import time
from datetime import datetime

import requests
import socketio

token = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijk3YzU3ZTcwNWNmIiwibmFt"
    "ZSI6ImJvenpvIiwiaWF0IjoxNjk2MTYzMzY0fQ.DcwaUu65b9EasmYG9br6AE3WXBD2I-"
    "4lkavuD7s4eqE"
)
url_gpt_evolve = "http://agent:8000"

sio = socketio.Client()


@sio.on("*")
def catch_all(event, *data):
    status_code = 500
    while status_code != 200:
        try:
            status_code = requests.get(url_gpt_evolve + "/health-check").status_code
        except Exception as e:
            logging.debug(e)
            time.sleep(1)

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
        game_map = []

        for tile in data[2]:
            game_map.append(tile)
            game_map[-1]["valid"] = True

        status_code = requests.post(
            event_endpoint,
            json={
                "origin": "map",
                "data": {"data": game_map},
                "game_dump": {},
                "description": description,
                "received_date": datetime.now().timestamp(),
            },
        ).status_code
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


def main() -> None:
    while True:
        time.sleep(1)
        try:
            sio.connect("http://deliveroo:8080", headers={"x-token": token})
            sio.wait()
        except Exception:
            print("Deliveroo client can't connect to Deliveroo Server." "Retrying...")
