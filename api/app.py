import os
import jwt
import requests
import secrets

from db import db, Purchase, User, Item
from flask import Flask, request, render_template, redirect, url_for, current_app, jsonify, make_response, session, abort, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from dotenv import load_dotenv
from urllib.parse import urlencode
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from receipt import get_total_amount
from PIL import Image


load_dotenv()

app = Flask(__name__, template_folder="../front-end/templates",
            static_folder="../front-end/static")
db_filename = "expense_tracker.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['JWT_EXPIRATION_DELTA'] = timedelta(minutes=15)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['OAUTH2_PROVIDERS'] = {
    'google': {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'userinfo': {
            'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'email': lambda json: json['email'],
        },
        'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
    },
}


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main_page'

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(body, code=200):
    return jsonify(body), code


def failure_response(message, code=404):
    return jsonify({"error": message}), code


def generate_tokens(user):
    # Generate access token
    access_token_payload = {'user_id': user.id, 'exp': datetime.utcnow(
    ) + app.config['JWT_EXPIRATION_DELTA']}
    access_token = jwt.encode(access_token_payload,
                              app.config['SECRET_KEY'], algorithm='HS256')

    # Generate refresh token
    refresh_token_payload = {'user_id': user.id}
    refresh_token = jwt.encode(
        refresh_token_payload, app.config['SECRET_KEY'], algorithm='HS256')

    return access_token, refresh_token


def hash_password(password):
    return generate_password_hash(password, method='sha256')


def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# ---------------------Render pages-------------------


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


@app.route('/report/', methods=['GET', 'POST'])
def report_page():
    if request.method == 'POST':
        return redirect(url_for('report'))

    return render_template('report.html')


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        return redirect(url_for('login'))

    return render_template('login.html')


# -----------------------------API routes---------------------

@app.route('/api/login/', methods=['POST'])
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

        # Just realized, with flask-login, we don't need to generate tokens and store them as cookies
        # Below is optional and has no practical use in our app
        # Tokens in cookie is not being verify when the user makes a request to the server
        access_token, refresh_token = generate_tokens(user)

        # Set the access token in an HTTP-only cookie
        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie('access_token', access_token,
                            httponly=True, secure=True, samesite='Strict')

        # Set the refresh token in an HTTP-only cookie
        response.set_cookie('refresh_token', refresh_token,
                            httponly=True, secure=True, samesite='Strict')
        
        flash('Welcome, ' + username + '!')
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
        payload = jwt.decode(
            refresh_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(payload['user_id'])

        if user:
            access_token, new_refresh_token = generate_tokens(user)

            # Set the new access token in an HTTP-only cookie
            response = make_response(jsonify({'message': 'Token refreshed'}))
            response.set_cookie('access_token', access_token,
                                httponly=True, secure=True, samesite='Strict')

            # Set the new refresh token in an HTTP-only cookie
            response.set_cookie('refresh_token', new_refresh_token,
                                httponly=True, secure=True, samesite='Strict')

            return response

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Expired refresh token'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid refresh token'}), 401


@app.route('/api/logout/', methods=['POST'])
@login_required
def logout():
    """
    Logout the user
    Clear the access and refresh tokens by setting their expiration to the immediate time
    """
    logout_user()
    response = make_response(jsonify({'message': 'Logout successful'}))
    # Clear the access and refresh tokens by setting their expiration to the past
    response.set_cookie('access_token', expires=0,
                        httponly=True, secure=True, samesite='Strict')
    response.set_cookie('refresh_token', expires=0,
                        httponly=True, secure=True, samesite='Strict')
    flash('You have been logged out.')
    return response


@app.route('/api/register/', methods=['POST'])
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

    if amount is not None and amount.strip() != "":
        # If user is not logged in, don't store the purchase into the database and return the amount and type
        if current_user.is_anonymous:
            return success_response({"adjustedAmount": amount,
                                     "type": expense_type
                                     })

        # If user is logged in, store the purchase into the database and return the amount and type
        amount = int(request.form.get('amount'))  # type: ignore
        user = User.query.filter_by(id=current_user.id).first()
        purchase = Purchase(
            amount=amount, type=expense_type, date=datetime.now())
        user.purchases.append(purchase)
        db.session.add(purchase)
        db.session.add(user)
        db.session.commit()
        return success_response({"adjustedAmount": amount,
                                 "type": expense_type
                                 })
    elif receipt_file is not None:
        # If user is not logged in, don't store the purchase into the database and return the amount and type
        receipt = Image.open(receipt_file)
        amount = get_total_amount(receipt)
        if amount is None:
            return failure_response("total not found", 400)
        
        if current_user.is_anonymous:
            return success_response({"adjustedAmount": amount,
                                     "type": expense_type
                                     })

        # If user is logged in, store the purchase into the database and return the amount and type
        user = User.query.filter_by(id=current_user.id).first()
        purchase = Purchase(
            amount=amount, type=expense_type, date=datetime.now())
        user.purchases.append(purchase)
        db.session.add(purchase)
        db.session.add(user)
        db.session.commit()
        return success_response({"adjustedAmount": amount,
                                 "type": expense_type
                                 })
    else:
        return failure_response("parameter not provided", 400)


@app.route("/api/get_expenses/", methods=['GET'])
@login_required
def get_expenses():
    """
    Returns all the expenses for the user
    """
    user = User.query.filter_by(id=current_user.id).first()
    purchases = user.purchases
    return success_response({"purchases": [purchase.serialize() for purchase in purchases]})


#Temporary storing the data from the api, reduce the number of api calls and optimize the performance
#Set to be expired after 1 day
exchange_rate=(datetime.now()-timedelta(days=1), 
               {
                     "rates": None
               })

@app.route("/api/exchange/")
def get_exchange():

    amount = request.args.get('fromCurrencyAmount', type=float)
    fromCurrencyCode = request.args.get('fromCurrency', type=str)
    toCurrencyCode = request.args.get('toCurrency', type=str)
    
    global exchange_rate

    if datetime.now() - exchange_rate[0] >= timedelta(days=1):
        # this is an api i found online that does not require a api key
        api_key = os.environ.get('CURRENCY_API_KEY')
        url = f'https://api.freecurrencyapi.com/v1/latest?apikey={api_key}'
        response = requests.get(url)

        # The 'data' dictionary holds exchange rates for various currencies, 
        # with the US Dollar (USD) as the base currency.
        data = response.json()
        
        exchange_rate = (datetime.now(), data.get('data'))

    # get the fromCurrency rate
    fromCurrencyCode_rate = exchange_rate[1].get(fromCurrencyCode)
    # get the toCurrency_rate
    toCurrencyCode_rate = exchange_rate[1].get(toCurrencyCode)

    # do some simple math
    rate = toCurrencyCode_rate/fromCurrencyCode_rate
    res = amount * rate

    return success_response({"toCurrencyAmount": round(res,2)})


#---------------------OAuth login api-------------------
@app.route('/api/authorize/<provider>')
def oauth2_authorize(provider):
    """
    Authorize the user with the given provider
    """
    if not current_user.is_anonymous:
        return redirect(url_for('main_page'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)
    
    session['oauth2_state'] = secrets.token_urlsafe(16)
    
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('oauth2_callback', provider=provider, _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    return redirect(provider_data['authorize_url'] + '?' + qs)

@app.route("/api/callback/<provider>")
def oauth2_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main_page'))
    
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)
    
    if 'error' in request.args:
        return redirect(url_for('main_page'))
    
    if request.args.get('state') != session.pop('oauth2_state', None):
        abort(401)
    
    if 'code' not in request.args:
        abort(401)

    response = requests.post(provider_data['token_url'], data = {
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args.get('code'),
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('oauth2_callback', provider=provider, _external=True),
    }, headers = {'Accept': 'application/json'})

    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)
    
    response = requests.get(provider_data['userinfo']['url'], headers = {
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    
    username = provider_data['userinfo']['email'](response.json()).split('@')[0]

    user = db.session.scalar(db.select(User).where(User.username == username))
    if user is None:
        user = User(username=username, password=hash_password(os.urandom(16).hex()))
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    flash('Welcome, ' + username + '!')
    return redirect(url_for('main_page'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Unauthorized'}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
