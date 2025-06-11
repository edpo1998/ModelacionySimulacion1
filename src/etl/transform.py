import pandas as pd
from datetime import date
from src.utils.db import SessionLocal
from src.models.config_date import ConfigDate
from src.models.holiday_date import HolidayDate

def _map_season(month: int) -> str:
    if month in (12, 1, 2): return 'invierno' # ENERO A FEBRERO
    if month in (3, 4, 5): return 'primavera' # MARZO A MAYO
    if month in (6, 7, 8): return 'verano' # JUNIO A AGOSTO
    return 'otoño' # SEPTIEMBRE A DICIEMBRE

def transform(data: pd.DataFrame):
    session = SessionLocal()
    try:
        year = 2023
        config = session.query(ConfigDate).filter_by(year=year).first()
        if config:
            school_start = config.start_date
            school_end = config.end_date
        else:
            school_start = school_end = None
        holidays = session.query(HolidayDate).filter_by(year=year).all()
        holiday_set = {h.holiday_date for h in holidays}
    finally:
        session.close()

    unique_dates = pd.DataFrame({'consumption_date': data['consumption_date'].unique()})
    dt = pd.DatetimeIndex(unique_dates['consumption_date'])
    unique_dates['year'] = dt.year
    unique_dates['quarter'] = dt.quarter
    unique_dates['month'] = dt.month
    unique_dates['day'] = dt.day
    unique_dates['weekday'] = dt.weekday + 1
    unique_dates['is_weekend'] = unique_dates['weekday'].isin([6, 7])
    unique_dates['season'] = unique_dates['month'].apply(_map_season)

    if school_start and school_end:
        unique_dates['is_school_term'] = unique_dates['consumption_date'].apply(
            lambda d: school_start <= d <= school_end
        )
    else:
        unique_dates['is_school_term'] = False
    unique_dates['is_holiday'] = unique_dates['consumption_date'].isin(holiday_set)
    data['consumption_mwh'] = 0.2
    data['cost'] = data['consumption_mwh'] * data['price']
    fact_df = data[['consumption_date', 'hour_start', 'consumption_mwh', 'price', 'cost']].copy()
    fact_df.rename(columns={'hour_start': 'consumption_hour'}, inplace=True)

    return unique_dates, fact_df
