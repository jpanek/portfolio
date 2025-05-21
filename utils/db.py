# db.py
import psycopg2
from sqlalchemy import create_engine
from config import DevConfig

def get_db_connection():
    """Returns a psycopg2 connection (for manual SQL execution)."""
    return psycopg2.connect(
        host=DevConfig.HOST,
        dbname=DevConfig.DBNAME,
        user=DevConfig.USER,
        password=DevConfig.PASSWORD
    )

def get_sqlalchemy_engine():
    """Returns a SQLAlchemy engine (for use with pandas, etc.)."""
    return create_engine(DevConfig.SQLALCHEMY_DATABASE_URI)

def sql_to_table(query=None, params=None):
    if query is None:
        query = "SELECT current_timestamp AS now"

    conn = get_db_connection()
    curr = conn.cursor()
    
    if params:
        curr.execute(query, params)
    else:
        curr.execute(query)

    data = curr.fetchall()
    column_names = [desc[0] for desc in curr.description]

    curr.close()
    conn.close()

    return data, column_names