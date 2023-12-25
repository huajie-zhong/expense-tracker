import json, datetime

from db import db, Purchase, User, Item
from flask import Flask, request, render_template

app = Flask(__name__, template_folder= "../front-end/templates", static_folder="../front-end/static")
db_filename = "expense_tracker.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(body, code = 200):
    return json.dumps(body), code

def failure_response(message, code = 404):
    return json.dumps({"error": message}), code


@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/api/submit_expense/", methods=['POST'])
def submit_expense():
    amount = request.form.get('amount')
    receipt_file = request.files['receipt'] if 'receipt' in request.files else None
    expense_type = request.form.get('type')

    if expense_type is None:
        expense_type = "uncategorized"

    if amount is not None:
        #TODO handle type
        purchase = Purchase(amount = amount, type = expense_type, date = datetime.datetime.now())
        db.session.add(purchase)
        db.session.commit()
        print("created")
        return success_response({amount:amount})
    else:
        return failure_response("parameter not provided", 400)

    
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
