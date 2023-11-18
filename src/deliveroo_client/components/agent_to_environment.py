from typing import Any

import uvicorn
from fastapi import FastAPI

from deliveroo_client.components.socket_client import sio

_app = FastAPI()


def _move(action: str) -> None:
    sio.emit("move", action)


@_app.get("/up/")
def up() -> Any:
    _move("up")


@_app.get("/right/")
def right() -> Any:
    _move("right")


@_app.get("/down/")
def down() -> Any:
    _move("down")


@_app.get("/left/")
def left() -> Any:
    _move("left")


@_app.get("/pickup/")
def pickup() -> Any:
    ...


@_app.get("/putdown/")
def putdown() -> Any:
    ...


@_app.get("/health-check/")
def health_check() -> bool:
    return True


def init_agent_to_environment_listener() -> None:
    uvicorn.run(_app, host="0.0.0.0", port=9999, log_level="error")
