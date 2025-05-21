# extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy import text
from utils.views import v_stock_prices_last, v_trades_pl, v_portfolio_overview
from context_processors import inject_current_year

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

# Initialize extensions with app
def init_app(app):
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    app.context_processor(inject_current_year)  # Register context processor

    # Only run when changing tables and databse things
    with app.app_context():
        #db.drop_all()
        #db.create_all()  # Create tables if they don't exist
        #create_views()
        pass
    
    # Set the login view for Flask-Login
    login_manager.login_view = "auth.login"  # Redirect here if the user is not logged in
    login_manager.login_message = "Login to view this page."  # Custom message
    login_manager.login_message_category = "danger"  # Category for the message (e.g., 'danger', 'info')

    # User Loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models.models import User
        user = User.query.get(int(user_id))  # Retrieve the user by their ID
        return user


# Function to create all views
def create_views():
    views = [v_stock_prices_last, v_trades_pl, v_portfolio_overview]
    for v in views:
        create_view(v)
    print('Views created ....')

def create_view(view_sql):
    db.session.execute(text(view_sql))
    db.session.commit()  # Commit to apply changes