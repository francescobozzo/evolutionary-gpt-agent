from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now
from sqlalchemy_json import NestedMutableJson


class Base(DeclarativeBase):
    pass


class Experiment(Base):
    __tablename__ = "experiments"

    experiment_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    events: Mapped[list["Event"]] = relationship(back_populates="experiment")
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


# class Checkpoint(Base):
#     __tablename__ = "checkpoints"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     experiment: Mapped["experiment"] = relationship(
#         "experiments", remote_side=["id"]
#     )
#     id_parent: Mapped["id_parent"] = relationship(
#         "checkpoint", remote_side=["id"]
#     )
#     checkpoint_type: Mapped[str]
#     game_dump: Mapped[dict] = mapped_column(NestedMutableJson, nullable=True)


# class BeliefSet(Base):
#     __tablename__ = "belief_sets"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     data: Mapped[dict] = mapped_column(NestedMutableJson, default={})


# class PromptTemplates(Base):
#     __tablename__ = "prompt_templates"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     experiment: Mapped["experiment"] = relationship(
#         "experiments", remote_side=["id"]
#     )
#     template_type: Mapped[str]
#     template: Mapped[str]


# class Perceiver(Base):
#     __tablename__ = "perceivers"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     belief_set_input: Mapped["belief_set_input"] = relationship(
#         "belief_sets", remote_side=["id"]
#     )
#     belief_set_output: Mapped["belief_set_output"] = relationship(
#         "belief_sets", remote_side=["id"]
#     )
#     start_event_id: Mapped[int] = relationship("events", remote_side=["id"])
#     end_event_id: Mapped[int] = relationship("events", remote_side=["id"])
#     experiment: Mapped[int] = relationship("experiments", remote_side=["id"])
#     code: Mapped[str]
#     prompt_template: Mapped[int] = relationship(
#         "prompt_templates", remote_side=["id"]
#     )
#     prompt: Mapped[str]
#     checkpoint_id: Mapped[int] = relationship(
#         "checkpoints", remote_side=["id"]
#     )


# class Plan(Base):
#     __tablename__ = "plans"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     belief_set_input: Mapped["belief_set_input"] = relationship(
#         "belief_sets", remote_side=["id"]
#     )
#     belief_set_output: Mapped["belief_set_output"] = relationship(
#         "belief_sets", remote_side=["id"]
#     )
#     checkpoint: Mapped["checkpoint"] = relationship(
#         "checkpoints", remote_side=["id"]
#     )
#     code: Mapped[str]
