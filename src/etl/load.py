import os
import pandas as pd
from datetime import datetime
from src.utils.db import SessionLocal, engine, Base
from src.models.dim_time import DimTime
from src.models.fact_energy import FactEnergy

def init_db():
    Base.metadata.create_all(bind=engine)

def load_dim_time(dim_df):
    session = SessionLocal()
    try:
        for _, row in dim_df.iterrows():
            obj = DimTime(
                consumption_date=row['consumption_date'],
                year=row['year'],
                quarter=row['quarter'],
                month=row['month'],
                day=row['day'],
                weekday=row['weekday'],
                is_weekend=row['is_weekend'],
                season=row.get('season'),
                is_school_term=row.get('is_school_term'),
                is_holiday=row.get('is_holiday')
            )
            session.merge(obj)
        session.commit()
    finally:
        session.close()

def load_fact(fact_df):
    session = SessionLocal()
    try:
        dates = session.query(DimTime.time_id, DimTime.consumption_date).all()
        date_map = {d.consumption_date: d.time_id for d in dates}
        for _, row in fact_df.iterrows():
            fact = FactEnergy(
                time_id=date_map.get(row['consumption_date']),
                consumption_hour=row['consumption_hour'],
                consumption_mwh=row['consumption_mwh'],
                price=row['price'],
                cost=row['cost']
            )
            session.add(fact)
        session.commit()
    finally:
        session.close()