import os, secrets, json, jwt, requests

from db import db, Purchase, User, Item
from flask import Flask, request, render_template, redirect, url_for, current_app, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from dotenv import load_dotenv
from urllib.parse import urlencode
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()

app = Flask(__name__, template_folder= "../front-end/templates", static_folder="../front-end/static")
db_filename = "expense_tracker.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['JWT_EXPIRATION_DELTA'] = timedelta(minutes=15)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


login = LoginManager(app)
login.login_view = 'main_page'

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(body, code = 200):
    return jsonify(body), code

def failure_response(message, code = 404):
    return jsonify({"error": message}), code

def generate_tokens(user):
    # Generate access token
    access_token_payload = {'user_id': user.id, 'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']}
    access_token = jwt.encode(access_token_payload, app.config['SECRET_KEY'], algorithm='HS256')

    # Generate refresh token
    refresh_token_payload = {'user_id': user.id}
    refresh_token = jwt.encode(refresh_token_payload, app.config['SECRET_KEY'], algorithm='HS256')

    return access_token, refresh_token

def hash_password(password):
    return generate_password_hash(password, method='sha256')

def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

#---------------------Render pages-------------------
@app.route("/")
def main_page():
    # main page
    return render_template('index.html')

@app.route('/currency/', methods=['GET', 'POST'])
def currency_page():
    if request.method == 'POST':
        return redirect(url_for('currency'))

    return render_template('currency.html')

@app.route('/header/', methods=['GET', 'POST'])
def header_page():
    if request.method == 'POST':
        return redirect(url_for('header'))

    return render_template('header.html')

@app.route('/settings/', methods=['GET', 'POST'])
def settings_page():
    if request.method == 'POST':
        return redirect(url_for('settings'))

    return render_template('settings.html')

@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        return redirect(url_for('login'))

    return render_template('login.html')


#-----------------------------API routes---------------------

@app.route('/api/login/', methods = ['POST'])
def login():
    """
    Get the username and password from the request body
    Verify the user exists in the database
    Verify the password is correct
    Generate an access token and a refresh token
    Set the access token and refresh token as cookies in the response
    """

    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    

    if user and verify_password(user.password, password):
        login_user(user)
        access_token, refresh_token = generate_tokens(user)

        # Set the access token in an HTTP-only cookie
        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='Strict')

        # Set the refresh token in an HTTP-only cookie
        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Strict')

        return response
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/refresh-token/', methods=['POST'])
def refresh_token():
    """
    Refresh the access token
    Given a refresh token in the request body, verify it and generate a new access token
    Set the new access token as a cookie in the response
    """
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    try:
        payload = jwt.decode(refresh_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(payload['user_id'])

        if user:
            access_token, new_refresh_token = generate_tokens(user)

            # Set the new access token in an HTTP-only cookie
            response = make_response(jsonify({'message': 'Token refreshed'}))
            response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='Strict')

            # Set the new refresh token in an HTTP-only cookie
            response.set_cookie('refresh_token', new_refresh_token, httponly=True, secure=True, samesite='Strict')

            return response

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Expired refresh token'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid refresh token'}), 401

@app.route('/api/logout/', methods = ['POST'])
@login_required
def logout():
    """
    Logout the user
    Clear the access and refresh tokens by setting their expiration to the immediate time
    """
    logout_user()
    response = make_response(jsonify({'message': 'Logout successful'}))
    # Clear the access and refresh tokens by setting their expiration to the past
    response.set_cookie('access_token', expires=0, httponly=True, secure=True, samesite='Strict')
    response.set_cookie('refresh_token', expires=0, httponly=True, secure=True, samesite='Strict')
    return response

@app.route('/api/register/', methods = ['POST'])
def register():
    """
    Register a new user
    Get the username and password from the request body
    Verify the user does not already exist in the database
    Hash the password
    Create a new user object and add it to the database
    """
    username = request.form.get('username')
    password = request.form.get('password')

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 400
    
    new_user = User(username=username, password=hash_password(password))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registration successful. You can now log in.'}), 201


@app.route("/api/submit_expense/", methods=['POST'])
def submit_expense():
    """
    Takes in a receipt or amount and returns the amount and type of expense
    If amount is provided, it will be used with the highest piroity
    If the receipt is provided, it will be given to the OCR method to extracted the amount #TODO
    Records the expense in the database
    """
    amount = request.form.get('amount')
    receipt_file = request.files['receipt'] if 'receipt' in request.files else None
    expense_type = request.form.get('type')

    if expense_type is None:
        expense_type = "uncategorized"

    if amount is not None:
        amount = int(request.form.get('amount')) # type: ignore
        purchase = Purchase(amount = amount, type = expense_type, date = datetime.now())
        db.session.add(purchase)
        db.session.commit()
        return success_response({"adjustedAmount":amount,
                                 "type":expense_type
                                 })
    else:
        return failure_response("parameter not provided", 400)

    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
