from queue import Queue

import uvicorn
from fastapi import FastAPI
from typings import Any

from models.api import Event

_app = FastAPI()


@_app.post("/event/")
def send_event(event: Event) -> Any:
    _app.events_queue.put(event)
    return event.to_json()


@_app.get("/health-check/")
def health_check() -> bool:
    return True


def init_listener(events_queue: Queue[Event]) -> None:
    _app.events_queue = events_queue
    uvicorn.run(_app, host="0.0.0.0", port=8000, log_level="error")
