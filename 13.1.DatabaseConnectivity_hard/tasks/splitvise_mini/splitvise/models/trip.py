import datetime

from sqlalchemy import Column, Integer, DateTime, Table, ForeignKey, VARCHAR
from sqlalchemy.orm import relationship

from .base import Base

UserTrip = Table(
    'users_trips', Base.metadata,
    Column('user_id', ForeignKey('users.user_id'), primary_key=True),
    Column('trip_id', ForeignKey('trips.trip_id'), primary_key=True)
)


class Trip(Base):  # type: ignore
    __tablename__ = 'trips'

    trip_id = Column(Integer, primary_key=True)
    title = Column(VARCHAR)
    description = Column(VARCHAR)
    created_timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relations
    users = relationship('User', secondary=UserTrip, back_populates='trips')
