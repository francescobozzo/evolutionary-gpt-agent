from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy_json import NestedMutableJson


class Base(DeclarativeBase):
    pass


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    received_date: Mapped[datetime] = mapped_column(DateTime)
    processed_date: Mapped[datetime] = mapped_column(DateTime)
    id_parent: Mapped[int] = relationship("events", remote_side=["id"])
    experiment: Mapped[int] = relationship("experiments", remote_side=["id"])
    origin: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    data: Mapped[dict] = mapped_column(NestedMutableJson)


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiment: Mapped[int] = relationship("experiments", remote_side=["id"])
    id_parent: Mapped[int] = relationship("checkpoint", remote_side=["id"])
    type: Mapped[str] = mapped_column(String)
    game_dump: Mapped[dict] = mapped_column(NestedMutableJson)
