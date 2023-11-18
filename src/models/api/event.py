from typing import Any

from pydantic import BaseModel


class Event(BaseModel):
    origin: str
    description: str
    data: dict[Any, Any]
    game_dump: dict[Any, Any]
    received_date: float

    def to_json(self) -> str:
        return (
            f'{{"type": "{self.origin}", "data": {self.data},'
            f'description": {self.description}}}'
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.origin,
            "data": self.data,
            "description": self.description,
        }
