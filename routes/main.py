from flask import Blueprint, render_template, jsonify, request, abort
from flask_login import login_required, current_user
from utils.db import sql_to_table, get_db_connection
from utils.queries import sql_stocks, sql_ccy, sql_history, sql_trades_detail, sql_trades, sql_pl, sql_pl_month, sql_pl_all_start, sql_pl_all_end 
from utils.queries import modify_query
from utils.pricing import refresh_prices, position
from config import get_today
from models.models import Portfolio, Trade, Instrument, Price
from extensions import db
from datetime import datetime


main_bp = Blueprint('main',__name__)


""" Index route 
------------------------------------------------------------------------- """
@main_bp.route('/')
@login_required  # Protect this route with authentication
def index():
    data, columns = sql_to_table(query=sql_stocks)

    return render_template('index.html', data=data, column_names=columns)

""" Manage 
------------------------------------------------------------------------- """
@main_bp.route('/manage')
@login_required  # Protect this route with authentication
def manage():
    data, columns = sql_to_table(query=sql_stocks)

    return render_template('manage.html')


""" Trades overview 
------------------------------------------------------------------------- """
@main_bp.route('/trades')
@login_required  # Protect this route with authentication
def trades():
    portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
    # Dictionary to store trade data for each portfolio
    trades_by_portfolio = {}

    # Execute the query for each portfolio
    for portfolio in portfolios:
        #Store trades detail
        data, columns = sql_to_table(query=sql_trades_detail, params=(portfolio.id,))
        data_sum, columns_sum = sql_to_table(query=sql_trades, params =(portfolio.id,))
        trades_by_portfolio[portfolio.name] = {
            "data": data, 
            "columns": columns, 
            "data_sum":data_sum, 
            "columns_sum":columns_sum,
            "portfolio_id":portfolio.id
        }

    return render_template('trades.html', trades_by_portfolio = trades_by_portfolio)


""" Currencies overview 
------------------------------------------------------------------------- """
@main_bp.route('/ccy')
def ccy():
    data_ccy,columns = sql_to_table(query=sql_ccy)

    return render_template('ccy.html', column_names=columns, data_ccy=data_ccy)


""" History of prices 
------------------------------------------------------------------------- """
@main_bp.route("/history/<symbol>", methods=['GET'])
@login_required  # Protect this route with authentication
def history(symbol):
    start_date = request.args.get('start_date') #getting the date from GET parmeter
    end_date = request.args.get('end_date') #getting the date from GET parmeter

    if not start_date:
        start_date = '2025-01-01'
    if not end_date:
        end_date = get_today()

    #trade = Trade.query.filter_by(symbol=symbol).first()
    #print(trade)


    params = (symbol,start_date, end_date)

    #query the data
    data,columns = sql_to_table(query=sql_history,params=params)
    
    #prepare data for Chart:
    chart_dates = [row[1] for row in data]
    chart_prices = [row[2] for row in data]

    return render_template("history.html",
                           symbol=symbol, 
                           data=data, 
                           column_names=columns,
                           chart_dates=chart_dates,
                           chart_prices=chart_prices,
                           start_date=start_date, end_date=end_date
                           )


""" Refresh prices in DB 
------------------------------------------------------------------------- """
@main_bp.route('/trigger_function', methods=['POST'])
@login_required  # Protect this route with authentication
def trigger_function():
    result = refresh_prices(history_days=3,symbol=None)
    # Return a response to the client
    return jsonify({"message": f"Prices refreshed in {result}s."})


""" PL details
------------------------------------------------------------------------- """
@main_bp.route("/pl/<symbol>", methods=['GET'])
@login_required  # Protect this route with authentication
def pl(symbol):
    start_date = request.args.get('start_date') #getting the start date from GET parmeter
    end_date = request.args.get('end_date') #getting the end date from GET parmeter
    period = request.args.get('period') # getting period for report, default = daily
    conn = get_db_connection()
    curr = conn.cursor()

    if not start_date:
        start_date = '2025-01-01'

    if not end_date:
        end_date = get_today()

    if period == "monthly":
        print('Display monthly report:')
        query = sql_pl_month
        start_date = '2024-01-01'
    else:
        print('Display daily report:')
        query = sql_pl
    
    params = (current_user.id,symbol,start_date, end_date)
    
    curr.execute(query,params)
    data = curr.fetchall()
    columns = [desc[0] for desc in curr.description]

    #prepare data for Chart:
    chart_dates = [row[1] for row in data]
    chart_pl_day = [row[2] for row in data]
    chart_pl_cum = [row[3] for row in data]

    conn.close()

    return render_template("pl.html",
                           symbol=symbol, 
                           data=data, 
                           column_names=columns,
                           chart_dates=chart_dates,
                           chart_pl_cum=chart_pl_cum,
                           chart_pl_day=chart_pl_day,
                           start_date=start_date, end_date=end_date,
                           period=period
                           )


""" PL grouped overview
------------------------------------------------------------------------- """
@main_bp.route("/pl_all/", defaults={'portfolio': None}, methods=['GET'])
@main_bp.route("/pl_all/<portfolio>", methods=['GET'])
@login_required  # Protect this route with authentication
def pl_all(portfolio=None):
    portfolio = request.args.get('portfolio',type=int) #getting the portfolio from GET parameter
    start_date = request.args.get('start_date') #getting the date from GET parmeter
    end_date = request.args.get('end_date') #getting the date from GET parmeter
    period = request.args.get('period') # getting period for report, default = daily
    conn = get_db_connection()
    curr = conn.cursor()

    portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
    portfolio = Portfolio.query.filter_by(id=portfolio).first()
    portfolio = portfolio if portfolio else Portfolio()

    if not start_date:
        start_date = '2025-01-01'

    if not end_date:
        end_date = get_today()
    
    params = []
    params.append(start_date)
    params.append(end_date)
    params.append(current_user.id)
    query = sql_pl_all_start

    if portfolio.id :
        query += " AND portfolio_id = %s"
        params.append(portfolio.id)
    
    query += sql_pl_all_end

    if period == "monthly":
        query = modify_query(query,'month_end')
        #params[0] = '2023-01-01'
    else:
        period = 'daily'
        query = modify_query(query,'date')

    curr.execute(query,params)
    data = curr.fetchall()
    columns = [desc[0] for desc in curr.description]

    #prepare data for Chart:
    if period == "daily":
        chart_dates = [row[0].strftime("%Y-%m-%d") for row in data]
    else:
        chart_dates = [row[0] for row in data]
    chart_pl_day = [row[1] for row in data]
    chart_pl_period = [row[2] for row in data]
    chart_pl_total = [row[3] for row in data]

    conn.close()

    return render_template("pl_all.html",
                           data=data, 
                           portfolio=portfolio.id,
                           portfolio_name = portfolio.name,
                           column_names=columns,
                           chart_dates=chart_dates,
                           chart_pl_day=chart_pl_day,
                           chart_pl_period=chart_pl_period,
                           chart_pl_total=chart_pl_total,
                           start_date=start_date, end_date=end_date,
                           period=period,
                           portfolios=portfolios
                           )


