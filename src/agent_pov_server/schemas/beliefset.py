from typing import Any

from pydantic import BaseModel


class BeliefsetBase(BaseModel):
    belief_set_id: int
    data: dict[str, Any]
    experiment_id: int

    class Config:
        orm_mode = True
