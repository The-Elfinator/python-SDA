import datetime

from sqlalchemy import Integer, Column, ForeignKey, DateTime, Boolean, VARCHAR

from .base import Base


class Event(Base):  # type: ignore
    __tablename__ = 'events'

    event_id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.trip_id'))
    title = Column(VARCHAR)
    happened_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    settled_up = Column(Boolean, default=False)
