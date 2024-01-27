from sqlalchemy import Integer, Column, ForeignKey, Numeric

from .base import Base


class Summary(Base):  # type: ignore
    __tablename__ = 'summaries'

    summary_id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.trip_id'))
    user_from_id = Column(Integer, ForeignKey('users.user_id'))
    user_to_id = Column(Integer, ForeignKey('users.user_id'))
    value = Column(Numeric)
