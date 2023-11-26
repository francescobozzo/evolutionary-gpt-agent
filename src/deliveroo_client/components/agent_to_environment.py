from typing import Any

import uvicorn
from fastapi import FastAPI
from loguru import logger

from deliveroo_client.components.socket_client import sio

_app = FastAPI()

logger.level("INFO")


def _move(action: str) -> Any:
    logger.debug(f"agent action received: {action}")
    return sio.call("move", action)


def _pickup() -> Any:
    logger.debug("agent action received: pickup")
    return sio.call("pickup")


def _putdown() -> Any:
    logger.debug("agent action received: putdown")
    return sio.emit("putdown")


@_app.get("/up/")
def up() -> Any:
    return _move("up")


@_app.get("/right/")
def right() -> Any:
    return _move("right")


@_app.get("/down/")
def down() -> Any:
    return _move("down")


@_app.get("/left/")
def left() -> Any:
    return _move("left")


@_app.get("/pickup/")
def pickup() -> Any:
    _pickup()


@_app.get("/putdown/")
def putdown() -> Any:
    _putdown()


@_app.get("/health-check/")
def health_check() -> bool:
    return True


def init_agent_to_environment_listener() -> None:
    logger.info("agent to environment listener initialized")
    uvicorn.run(_app, host="0.0.0.0", port=9999, log_level="error")
