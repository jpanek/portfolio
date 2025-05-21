from datetime import datetime
from flask_login import UserMixin
from extensions import db, bcrypt

# User Table
class User(db.Model, UserMixin):  # Inherit from db.Model for Flask-SQLAlchemy
    __tablename__ = 'users'  # Define table name
    
    id = db.Column(db.Integer, primary_key=True)  # Unique user ID
    username = db.Column(db.String(100), unique=True, nullable=False)  # Unique username
    name = db.Column(db.String(100), nullable=False)  # Name of the user
    password = db.Column(db.String(200), nullable=False)  # Hashed password
    role = db.Column(db.String(50), nullable=False, default='client')  # New role column
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # DateTime column

    portfolios = db.relationship("Portfolio", back_populates="user")  # One-to-many relationship with Portfolio

    def __repr__(self):
        return f'<User {self.username}>'

    def save(self):
        """Save the user to the database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_user_by_username(username):
        """Retrieve a user by username"""
        return User.query.filter_by(username=username).first()

    def check_password(self, password):
        """Check if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)

    @property
    def is_admin(self):
        """Check if the user is an admin."""
        return self.role == 'admin'

    def is_client(self):
        """Check if the user is a client."""
        return self.role == 'client'


# Portfolio Table
class Portfolio(db.Model):  # Inherit from db.Model for Flask-SQLAlchemy
    __tablename__ = 'portfolio'  # Define table name
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to User table
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="portfolios")  # One-to-many relationship with User
    trades = db.relationship("Trade", back_populates="portfolio")  # One-to-many relationship with Trade

    # Add q unique index on portfolio name and user_id
    __table_args__ = (
        db.UniqueConstraint('name','user_id',name='uq_portfolio_name_user'),
    )

    def __repr__(self):
        return f'<Portfolio {self.name}>'


# Instrument Table
class Instrument(db.Model):  # Inherit from db.Model for Flask-SQLAlchemy
    __tablename__ = 'instruments'  # Define table name
    
    symbol = db.Column(db.String(10), primary_key=True)  # Instrument symbol (e.g., AAPL)
    name = db.Column(db.String(100))  # Company name (e.g., Apple Inc.)
    category = db.Column(db.String(50))
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)

    stock_prices = db.relationship("Price", back_populates="instrument")  # One-to-many relationship with StockPrices
    trades = db.relationship("Trade", back_populates="instrument")  # One-to-many relationship with Trades

    def __repr__(self):
        return f'<Instrument {self.symbol} - {self.name}>'


# Prices Table
class Price(db.Model):  # Inherit from db.Model for Flask-SQLAlchemy
    __tablename__ = 'prices'  # Define table name

    # Add a unique index on symbol, date, and price_type
    __table_args__ = (
        db.UniqueConstraint('symbol', 'date', 'price_type', name='_symbol_date_price_type_uc'),
    )

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), db.ForeignKey('instruments.symbol'), nullable=False)  # Foreign key to Instruments
    date = db.Column(db.Date, nullable=False)  # Changed to String (TEXT format)
    price = db.Column(db.Float, nullable=False)  # Stock price value
    price_type = db.Column(db.String(50), default='Close')  # Price type (e.g., Open, Close)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    time = db.Column(db.DateTime)  # New column for the price datetime

    instrument = db.relationship("Instrument", back_populates="stock_prices")  # Many-to-one relationship with Instrument

    def __repr__(self):
        return f'<Price {self.symbol} - {self.price} on {self.date}>'


# Trade Table
class Trade(db.Model):  # Inherit from db.Model for Flask-SQLAlchemy
    __tablename__ = 'trades'  # Define table name
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), db.ForeignKey('instruments.symbol'), nullable=False)  # Foreign key to Instruments
    trade_date = db.Column(db.DateTime, nullable=False)  # Date of trade
    volume = db.Column(db.Integer, nullable=False)  # Number of shares
    trade_price = db.Column(db.Float, nullable=False)  # Price per share at trade time
    trade_type = db.Column(db.String(10), nullable=False)  # Type of trade (BUY/SELL)
    currency = db.Column(db.String(10), nullable=False)  # Currency of the trade
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)  # Foreign key to Portfolio
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)

    instrument = db.relationship("Instrument", back_populates="trades")  # Many-to-one relationship with Instrument
    portfolio = db.relationship("Portfolio", back_populates="trades")  # Many-to-one relationship with Portfolio

    def __repr__(self):
        return f'<Trade {self.symbol} - {self.trade_type} {self.volume} shares at {self.trade_price}>'
