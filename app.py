# app.py

import os 
from flask import Flask
from config import DevConfig
from extensions import init_app
from hooks import before_request  # Import the hook

# Import blueprints
from routes.main import main_bp
from routes.auth import auth_bp  
from routes.manage import manage_bp  
from routes.user import user_bp

from dotenv import load_dotenv
load_dotenv()

app = create_app()

# Initialize app creation function
def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(manage_bp, url_prefix='/manage')
    app.register_blueprint(user_bp, url_prefix='/user')

    # Load config from Config class
    app.config.from_object(DevConfig)  # Apply the configuration from config.py

    # Initialize extensions
    init_app(app)

    # Register the before_request function
    app.before_request(before_request)

    return app


# This is for running the app directly
if __name__ == '__main__':
    app = create_app()  # Create the app instance
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
