from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models.models import User
from extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))  # Redirect to login page

@auth_bp.route('/profile')
def profile():
    if current_user.is_authenticated:
        return jsonify({"username": current_user.username})
    else:
        return jsonify({"error": "User not logged in"}), 401

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))

        # Hash the password and create the user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, name=name, password=hashed_password, role='client')
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    get_args = request.args.get('next')
    print(get_args)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):  # Assuming you have check_password method
            login_user(user)
            
            # Handle redirection after login
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.index'))  # Redirect to homepage or a default page
            
        else:
            flash('Invalid login credentials', 'danger')
    
    return render_template('login.html')

