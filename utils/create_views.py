import sys,os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app 
from extensions import db
from utils.views import v_stock_prices_last, v_trades_pl, v_portfolio_overview


# List of view names
VIEW_NAMES = ["v_stock_prices_last", "v_trades_pl", "v_portfolio_overview"]

# Function to create all views
def create_views():
    app = create_app()
    with app.app_context():
        views = [v_stock_prices_last, v_trades_pl, v_portfolio_overview]
        for v in views:
            create_view(v)

# Function to execute view creation
def create_view(view_sql):
    db.session.execute(text(view_sql))
    db.session.commit()

create_views()