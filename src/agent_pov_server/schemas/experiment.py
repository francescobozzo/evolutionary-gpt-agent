from datetime import datetime

from pydantic import BaseModel


class ExperimentBase(BaseModel):
    experiment_id: int
    name: str
    timestamp: datetime

    class Config:
        orm_mode = True


class ExperimentDetail(ExperimentBase):
    num_events: int
    num_beliefsets: int
    num_perceivers: int
    num_plans: int
