from datetime import datetime

from pydantic import BaseModel


class ExperimentBase(BaseModel):
    experiment_id: int
    name: str
    timestamp: datetime

    class Config:
        orm_mode = True
