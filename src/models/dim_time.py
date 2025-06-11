from sqlalchemy import Column, Integer, SmallInteger, Boolean, String, Date
from sqlalchemy.orm import relationship
from src.utils.db import Base

class DimTime(Base):
    __tablename__ = 'dim_time'
    __table_args__ = {'schema': 'energy'}

    time_id = Column(Integer, primary_key=True, autoincrement=True)
    consumption_date = Column(Date, unique=True, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(SmallInteger, nullable=False)
    month = Column(SmallInteger, nullable=False)
    day = Column(SmallInteger, nullable=False)
    weekday = Column(SmallInteger, nullable=False)
    is_weekend = Column(Boolean, nullable=False)
    season = Column(String(10))
    is_school_term = Column(Boolean)
    is_holiday = Column(Boolean)

    facts = relationship('FactEnergy', back_populates='time')