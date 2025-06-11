from sqlalchemy import Column, Integer, Date
from sqlalchemy.orm import relationship
from src.utils.db import Base

class ConfigDate(Base):
    __tablename__ = 'config_date'
    __table_args__ = {'schema': 'mcs'}

    year = Column(Integer, primary_key=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    holidays = relationship('HolidayDate', back_populates='config', cascade='all, delete-orphan')
