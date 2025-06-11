from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
EXCEL_PATH = os.getenv('EXCEL_PATH', 'data/raw/POE_2023.xlsx')

if not DATABASE_URL:
    raise ValueError("ERROR AL CARGAR DATABASE_URL")