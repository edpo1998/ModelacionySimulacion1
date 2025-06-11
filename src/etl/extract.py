import pandas as pd
import calendar

from datetime import datetime, date
from src.config import EXCEL_PATH

def extract()-> pd.DataFrame:
    xls = pd.ExcelFile(EXCEL_PATH)
    frames = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=2)
        df = df.rename(columns={df.columns[0]: 'Hora_inicio', df.columns[1]: 'Hora_fin'})
        df = df.iloc[:24]
        long = df.melt( id_vars=['Hora_inicio', 'Hora_fin'], var_name='day', value_name='price')
        long['day'] = long['day'].astype(int)
        long['hour_start'] = pd.to_datetime(long['Hora_inicio'], format='%H:%M:%S', errors='coerce').dt.hour
        long['hour_end'] = pd.to_datetime(long['Hora_fin'], format='%H:%M:%S', errors='coerce').dt.hour
        try:
            month_num = datetime.strptime(sheet, '%B').month
        except ValueError:
            month_num = list(xls.sheet_names).index(sheet) + 1
        days_in_month = calendar.monthrange(2023, month_num)[1]
        long = long[long['day'] <= days_in_month]
        long['consumption_date'] = long['day'].apply(lambda d: date(2023, month_num, d))
        frames.append(long)
    data = pd.concat(frames, ignore_index=True)
    return data.dropna(subset=['hour_start', 'price', 'consumption_date'])