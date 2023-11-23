from typing import Any, Generator

import uvicorn
from fastapi import FastAPI
from loguru import logger
from sqlalchemy.orm import Session

from models.db_handler import DatabaseHandler

_app = FastAPI()

logger.level("INFO")


def get_db() -> Generator[Session, Any, None]:
    db_handler = DatabaseHandler()
    try:
        yield db_handler._session
    finally:
        db_handler._session.close()


@_app.get("/health-check/")
def health_check() -> Any:
    return {"data": "yes"}


def main() -> None:
    uvicorn.run(_app, host="0.0.0.0", port=9876, log_level="error")
