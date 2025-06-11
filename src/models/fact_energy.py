from sqlalchemy import Column, Integer, SmallInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from src.utils.db import Base

class FactEnergy(Base):
    __tablename__ = 'fact_energy'
    __table_args__ = {'schema': 'energy'}

    fact_id = Column(Integer, primary_key=True, autoincrement=True)
    time_id = Column(Integer, ForeignKey('energy.dim_time.time_id'), nullable=False)
    consumption_hour = Column(SmallInteger, nullable=False)
    consumption_mwh = Column(Numeric, nullable=False)
    price = Column(Numeric, nullable=False)
    cost = Column(Numeric, nullable=False)

    # Relación inversa
    time = relationship('DimTime', back_populates='facts')