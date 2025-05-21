from flask import Blueprint, render_template, request, jsonify
from utils.db import sql_to_table, execute_query
from utils.queries import sql_trades_usd, sql_trades_eur, sql_usd, sql_eur

trades_bp = Blueprint('trades', __name__)

@trades_bp.route('/trades')
def trades():
    data1, columns = sql_to_table(query=sql_trades_usd) 
    data2, _ = sql_to_table(query=sql_trades_eur) 
    usd_all, all_columns = sql_to_table(query=sql_usd) 
    eur_all, _  = sql_to_table(query=sql_eur)

    return render_template('trades.html', 
                           data1=data1, 
                           column_names=columns, 
                           data2=data2,
                           usd_all=usd_all,
                           all_columns=all_columns,
                           eur_all=eur_all)