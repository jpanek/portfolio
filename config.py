# config.py

from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # load .env variables

FOLDER_PATH = Path(__file__).parent.resolve()
DB_FILE = "database/portfolio.db"
SQLITE_DATABASE_URL = f"sqlite:///{FOLDER_PATH / DB_FILE}"

def get_today():
    return datetime.today().strftime('%Y-%m-%d')

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key_here'

class DevConfig(Config):
    # Use Supabase Postgres if env vars set, else fallback to SQLite
    USER = os.getenv("user")
    PASSWORD = os.getenv("password")
    HOST = os.getenv("host")
    PORT = os.getenv("port")
    DBNAME = os.getenv("dbname")

    if USER and PASSWORD and HOST and PORT and DBNAME:
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = SQLITE_DATABASE_URL
