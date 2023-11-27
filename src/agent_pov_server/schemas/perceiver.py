from pydantic import BaseModel


class PerceiverBase(BaseModel):
    perceiver_id: int
    belief_set_input_id: int
    belief_set_output_id: int
    start_event_id: int
    end_event_id: int
    experiment_id: int
    code: str
    prompt_template_id: int
    prompt: str
    checkpoint_id: int

    class Config:
        orm_mode = True
