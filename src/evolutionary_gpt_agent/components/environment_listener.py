from queue import Queue

import uvicorn
from fastapi import FastAPI

from models.api import Event

_app = FastAPI()


@_app.post("/event/")
def send_event(event: Event):
    _app.events_queue.put(event)
    return event.to_json()


@_app.get("/health-check/")
def health_check():
    return True


def init_listener(events_queue: Queue):
    _app.events_queue = events_queue
    uvicorn.run(_app, host="0.0.0.0", port=8000, log_level="error")
