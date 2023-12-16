from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now
from sqlalchemy.types import LargeBinary
from sqlalchemy_json import NestedMutableJson


class CheckpointType(str, Enum):
    BEGIN = "begin"
    PERCEIVER = "perceiver"
    PLAN = "plan"


class Base(DeclarativeBase):
    pass


class Experiment(Base):
    __tablename__ = "experiments"

    experiment_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    events: Mapped[list["Event"]] = relationship(back_populates="experiment")
    checkpoints: Mapped[list["Checkpoint"]] = relationship(back_populates="experiment")
    belief_sets: Mapped[list["BeliefSet"]] = relationship(back_populates="experiment")
    perceivers: Mapped[list["Perceiver"]] = relationship(back_populates="experiment")
    prompt_templates: Mapped[list["PromptTemplate"]] = relationship(
        back_populates="experiment"
    )
    plans: Mapped[list["Plan"]] = relationship(back_populates="experiment")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=now())


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(primary_key=True)
    received_date: Mapped[datetime] = mapped_column(DateTime)
    processed_date: Mapped[datetime] = mapped_column(DateTime, default=now())
    parent_id: Mapped[int] = mapped_column(ForeignKey("events.event_id"), nullable=True)
    parent: Mapped["Event"] = relationship(
        remote_side=[event_id], back_populates="children"
    )
    children: Mapped[list["Event"]] = relationship(back_populates="parent")
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.experiment_id"))
    experiment: Mapped[Experiment] = relationship(back_populates="events")
    origin: Mapped[str]
    description: Mapped[str | None]
    data: Mapped[dict] = mapped_column(NestedMutableJson)
    game_dump: Mapped[dict] = mapped_column(NestedMutableJson, nullable=True)


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    checkpoint_id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.experiment_id"))
    experiment: Mapped[Experiment] = relationship(back_populates="checkpoints")
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("checkpoints.checkpoint_id"), nullable=True
    )
    parent: Mapped["Checkpoint"] = relationship(
        remote_side=[checkpoint_id], back_populates="children"
    )
    children: Mapped[list["Checkpoint"]] = relationship(back_populates="parent")
    checkpoint_type: Mapped[str]
    game_dump: Mapped[dict] = mapped_column(NestedMutableJson, nullable=True)
    perceivers: Mapped["Perceiver"] = relationship(back_populates="checkpoint")
    plans: Mapped["Plan"] = relationship(back_populates="checkpoint")


class BeliefSet(Base):
    __tablename__ = "belief_sets"

    belief_set_id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[dict] = mapped_column(NestedMutableJson, default={})
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.experiment_id"))
    experiment: Mapped[Experiment] = relationship(back_populates="belief_sets")
    representation: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=True)
    # input_perceivers: Mapped[list["Perceiver"]] = relationship(
    #     back_populates="belief_set_input"
    # )
    # output_perceivers: Mapped[list["Perceiver"]] = relationship(
    #     back_populates="belief_set_output"
    # )


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    prompt_template_id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.experiment_id"))
    experiment: Mapped[Experiment] = relationship(back_populates="prompt_templates")
    template_type: Mapped[str]
    template: Mapped[str]
    perceivers: Mapped[list["Perceiver"]] = relationship(
        back_populates="prompt_template"
    )
    plans: Mapped[list["Plan"]] = relationship(back_populates="prompt_template")


class Perceiver(Base):
    __tablename__ = "perceivers"

    perceiver_id: Mapped[int] = mapped_column(primary_key=True)
    belief_set_input_id: Mapped[int] = mapped_column(
        ForeignKey("belief_sets.belief_set_id")
    )
    belief_set_output_id: Mapped[int] = mapped_column(
        ForeignKey("belief_sets.belief_set_id")
    )
    # belief_set_input: Mapped[BeliefSet] = relationship(
    #     back_populates="input_perceivers", foreign_keys=[belief_set_input_id]
    # )
    # belief_set_output: Mapped[BeliefSet] = relationship(
    #     back_populates="output_perceivers", foreign_keys=[belief_set_output_id]
    # )
    start_event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id"))
    end_event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id"))
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.experiment_id"))
    experiment: Mapped[Experiment] = relationship(back_populates="perceivers")
    code: Mapped[str]
    prompt_template_id: Mapped[int] = mapped_column(
        ForeignKey("prompt_templates.prompt_template_id")
    )
    prompt_template: Mapped[PromptTemplate] = relationship(back_populates="perceivers")
    prompt: Mapped[str]
    checkpoint_id: Mapped[int] = mapped_column(ForeignKey("checkpoints.checkpoint_id"))
    checkpoint: Mapped[Checkpoint] = relationship(back_populates="perceivers")


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    belief_set_input_id: Mapped[int] = mapped_column(
        ForeignKey("belief_sets.belief_set_id")
    )
    belief_set_output_id: Mapped[int] = mapped_column(
        ForeignKey("belief_sets.belief_set_id")
    )
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.experiment_id"))
    experiment: Mapped[Experiment] = relationship(back_populates="plans")
    # belief_set_input: Mapped["belief_set_input"] = relationship(
    #     "belief_sets", remote_side=["id"]
    # )
    # belief_set_output: Mapped["belief_set_output"] = relationship(
    #     "belief_sets", remote_side=["id"]
    # )
    prompt_template_id: Mapped[int] = mapped_column(
        ForeignKey("prompt_templates.prompt_template_id")
    )
    actions: Mapped[str]
    prompt_template: Mapped[PromptTemplate] = relationship(back_populates="plans")
    prompt: Mapped[str]
    checkpoint_id: Mapped[int] = mapped_column(ForeignKey("checkpoints.checkpoint_id"))
    checkpoint: Mapped[Checkpoint] = relationship(back_populates="plans")
    code: Mapped[str]
