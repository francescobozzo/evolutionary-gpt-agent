from pydantic import BaseModel


class CheckpointAttributesBase(BaseModel):
    id: int
    type: str


class CheckpointBase(BaseModel):
    name: str
    attributes: CheckpointAttributesBase
    # game_dump: dict[str, Any]
    children: list["CheckpointBase"]
