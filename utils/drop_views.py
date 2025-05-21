import sys,os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app 
from extensions import db

# List of view names
VIEW_NAMES = ["v_portfolio_overview","v_stock_prices_last", "v_trades_pl"]

# Function to drop all views
def drop_views():
    app = create_app()
    with app.app_context():
        for view in VIEW_NAMES:
            db.session.execute(text(f"DROP VIEW IF EXISTS {view}"))
            print(f"View {view} has been dropped")
        db.session.commit()

drop_views()