from flask import Blueprint, render_template
from utils.db import sql_to_table
from flask_login import login_required, current_user
from utils.queries import sql_portfolio
from models.models import User

user_bp = Blueprint('user', __name__)

""" Site for Managing portfolios """
@user_bp.route('/')
@login_required
def index():
    user = User.query.filter_by(id=current_user.id).first()
    #users = User.query.filter_by(id=current_user.id).all()

    if user.is_admin:
        all_users = User.query.all()
    else:
        all_users = []


    return render_template('user.html', user=user, all_users = all_users)