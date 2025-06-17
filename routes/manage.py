from flask import Blueprint, render_template, jsonify, request
from utils.db import sql_to_table
from flask_login import login_required, current_user
from utils.queries import sql_portfolio
from utils.pricing import refresh_prices, position
from models.models import Portfolio, Trade, Instrument, Price
from extensions import db
from datetime import datetime
from config import get_today

manage_bp = Blueprint('manage', __name__)

""" Site for Managing portfolios """
@manage_bp.route('/portfolio')
@login_required
def manage_portfolio():
    data, columns = sql_to_table(query=sql_portfolio, params=(current_user.id,))
    portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
    return render_template('portfolio.html', data=data, column_names=columns, portfolios=portfolios)

""" Function to delete portfolio """
@manage_bp.route('/delete_portfolio/<int:portfolio_id>', methods=['POST'])
@login_required
def delete_portfolio(portfolio_id):
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=current_user.id).first()
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    db.session.delete(portfolio)
    db.session.commit()
    return jsonify({"message": "Portfolio deleted"})

@manage_bp.route('/add_portfolio', methods=['POST'])
@login_required
def add_portfolio():

    #if not current_user.is_admin:  # Example condition
    #    return "Access denied", 403
    
    data = request.get_json()
    portfolio_name = data.get('portfolio_name')

    # Check if the portfolio already exists, if not create it
    portfolio = Portfolio.query.filter_by(name=portfolio_name).first()
    if portfolio:
        return jsonify({"error": "Portfolio already exists"}), 400

    # Create a new portfolio
    new_portfolio = Portfolio(name=portfolio_name, user_id=current_user.id)
    db.session.add(new_portfolio)
    db.session.commit()

    return jsonify({"message": "Portfolio added successfully"})

""" Site for Managing trades """
@manage_bp.route('/trades')
@login_required
def manage_trades():
    if request.method == 'GET':

        portfolio_id = request.args.get('portfolio',type=int)

        if portfolio_id:
            #print(f'Portfolio {portfolio_id} selected')
            trades = Trade.query.filter_by(portfolio_id=portfolio_id).all()
        else:
            #print(f'No portfolio selected')
            #trades = Trade.query.join(Portfolio).filter(Portfolio.user_id == current_user.id).all()
            trades = (
                Trade.query
                .join(Portfolio)
                .filter(Portfolio.user_id == current_user.id)
                .order_by(Trade.trade_date)
                .all()
            )

        columns = Trade.__table__.columns.keys() 
        portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()

        return render_template('add_trade.html', today_date=get_today(), portfolios=portfolios, trades=trades, columns=columns, portfolio_id=portfolio_id)
    
    if request.method == 'POST':
        '''Adding a new trade here below with all checks:'''
        data = request.json

        print('adding new trade here .....')
        
        try:
            symbol = data['symbol']

            # Step 1: Check if the instrument (symbol) exists in the Instrument table
            instrument = db.session.query(Instrument).filter_by(symbol=symbol).first()

            # Step 2: If it doesn't exist, create a new Instrument record
            if not instrument:
                print(f"Instrument {symbol} is not tracked in the Instruments table")
                
                #Look up on yahoo finance:
                ticker = position(symbol)
                
                instrument = Instrument(symbol=ticker.symbol,name=ticker.name,category=ticker.category)
                db.session.add(instrument)
                db.session.commit()
                print(f"Instrument {symbol} created.")

            #Step3: Check if there is a price for the Instrument
            price = db.session.query(Price).filter_by(symbol=symbol).first()

            if not price:
                print(f"Prices for {symbol} are not available in the prices table")

                history = 60
                print(f"Loading prices to db for {symbol} for last {history} days")
                refresh_prices(history_days=history,symbol=symbol)

            #Step4: Add the new trade now:
            trade_date = datetime.strptime(data['trade_date'], '%Y-%m-%d')
            trade = Trade(
                symbol=data['symbol'],
                trade_date=trade_date,  # Convert string to date
                volume=data['volume'],
                trade_price=data['trade_price'],
                trade_type=data['trade_type'],
                currency=data['currency'],
                portfolio_id=data['portfolio']
            )

            db.session.add(trade)  # Add the trade to the session
            db.session.commit()  # Commit the transaction to the database
            print(f"Trade for {trade.symbol} successfully created with ID {trade.id} to portfolio {trade.portfolio.name}")


            return jsonify({"message": "Trade added successfully"}), 201
        
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            return jsonify({"error": str(e)}), 400

""" Functon to handle editing a trade """
@manage_bp.route('/edit_trade/<int:trade_id>', methods=['POST'])
@login_required
def edit_trade(trade_id):
    trade = Trade.query.filter_by(id=trade_id).first()

    if not trade:
        return jsonify({"error": "Trade not found"}), 404

    try:
        trade.symbol = request.json['symbol']
        trade.trade_date = datetime.strptime(request.json['trade_date'], '%Y-%m-%d')
        trade.volume = request.json['volume']
        trade.trade_price = request.json['trade_price']
        trade.portfolio_id = request.json['portfolio_id']

        db.session.commit()
        return jsonify({"message": "Trade updated successfully"})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

""" Function to hande deleting a trade """
@manage_bp.route('/delete_trade/<int:trade_id>', methods=['DELETE'])
@login_required
def delete_trade(trade_id):
    trade = Trade.query.filter_by(id=trade_id).first()

    if not trade:
        return jsonify({"error": "Trade not found"}), 404

    db.session.delete(trade)
    db.session.commit()
    return jsonify({"message": "Trade deleted successfully"})

""" Adding a new trade """
@manage_bp.route('/add_trade', methods=['GET','POST'])
@login_required  # Protect this route with authentication
def add_trade():

    #if not current_user.is_admin:  # Example condition
        #return "Access denied", 403

    if request.method == 'GET':
        # Get available portfolios for current user:
        portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
        return render_template('add_trade.html', today_date=get_today(), portfolios=portfolios)
    
    if request.method == 'POST':
        '''Adding a new trade here below with all checks:'''
        data = request.json
        
        try:
            symbol = data['symbol']

            # Step 1: Check if the instrument (symbol) exists in the Instrument table
            instrument = db.session.query(Instrument).filter_by(symbol=symbol).first()

            # Step 2: If it doesn't exist, create a new Instrument record
            if not instrument:
                print(f"Instrument {symbol} is not tracked in the Instruments table")
                
                #Look up on yahoo finance:
                ticker = position(symbol)
                
                instrument = Instrument(symbol=ticker.symbol,name=ticker.name,category=ticker.category)
                db.session.add(instrument)
                db.session.commit()
                print(f"Instrument {symbol} created.")

            #Step3: Check if there is a price for the Instrument
            price = db.session.query(Price).filter_by(symbol=symbol).first()

            if not price:
                print(f"Prices for {symbol} are not available in the prices table")

                history = 60
                print(f"Loading prices to db for {symbol} for last {history} days")
                refresh_prices(history_days=history,symbol=symbol)

            #Step4: Add the new trade now:
            print(data['trade_date'])
            trade_date = datetime.strptime(data['trade_date'], '%Y-%m-%d')
            
            print(data['trade_date'])
            print(trade_date)
            
            trade = Trade(
                symbol=data['symbol'],
                trade_date=trade_date,  # Convert string to date
                volume=data['volume'],
                trade_price=data['trade_price'],
                trade_type=data['trade_type'],
                currency=data['currency'],
                portfolio_id=data['portfolio']
            )

            db.session.add(trade)  # Add the trade to the session
            db.session.commit()  # Commit the transaction to the database
            print(f"Trade for {trade.symbol} successfully created with ID {trade.id} to portfolio {trade.portfolio.name}")


            return jsonify({"message": "Trade added successfully"}), 201
        
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            return jsonify({"error": str(e)}), 400