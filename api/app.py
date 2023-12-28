import os, secrets, json, jwt, requests

from db import db, Purchase, User, Item
from flask import Flask, request, render_template, redirect, url_for, current_app, flash, jsonify, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from dotenv import load_dotenv
from urllib.parse import urlencode
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


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
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        login_user(user)
        access_token, refresh_token = generate_tokens(user)

        # Set the access token in an HTTP-only cookie
        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='Strict')

        # Set the refresh token in an HTTP-only cookie
        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Strict')

        return response
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/refresh-token/', methods=['POST'])
def refresh_token():
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
    logout_user()
    response = make_response(jsonify({'message': 'Logout successful'}))
    # Clear the access and refresh tokens by setting their expiration to the past
    response.set_cookie('access_token', expires=0, httponly=True, secure=True, samesite='Strict')
    response.set_cookie('refresh_token', expires=0, httponly=True, secure=True, samesite='Strict')
    return response

@app.route('/api/register/', methods = ['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({'message': 'User with this email already exists'}), 400
    
    new_user = User(email=email, password=hash_password(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful. You can now log in.'}), 201


@app.route("/api/submit_expense/", methods=['POST'])
def submit_expense():
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
