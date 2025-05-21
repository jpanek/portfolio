# hooks.py

from flask import g
from sqlalchemy import text
from extensions import db

def before_request():
    query = """
        SELECT 
         TO_CHAR(updated_date AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Prague', 'HH24:MI:SS')
         --TO_CHAR(updated_date AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Prague', 'YYYY-MM-DD HH24:MI:SS') 
        FROM prices 
        ORDER BY updated_date DESC 
        LIMIT 1
    """
    latest_price = db.session.execute(text(query)).fetchone()

    g.latest_updated_date = latest_price[0] if latest_price else None

