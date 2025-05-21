from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from config import DevConfig

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)


with app.app_context():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT NOW()"))
            print("Connection successful, time is:", result.fetchone()[0])
    except Exception as e:
        print("Connection failed:", e)
