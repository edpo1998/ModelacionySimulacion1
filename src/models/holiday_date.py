from sqlalchemy import Column, Integer, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from src.utils.db import Base

class HolidayDate(Base):
    __tablename__ = 'holiday_dates'
    __table_args__ = {'schema': 'mcs'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, ForeignKey('mcs.config_date.year'), nullable=False)
    holiday_date = Column(Date, nullable=False)
    description = Column(String(100))

    config = relationship('ConfigDate', back_populates='holidays')
