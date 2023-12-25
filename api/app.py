import json

from db import db, Purchase, User, Item
from flask import Flask, request, render_template

app = Flask(__name__, template_folder= "../front-end/templates", static_folder="../front-end/static")
db_filename = "expense_tracker.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/api/submit_expense", methods=['POST'])
def submit_expense():
    amount = request.form.get('amount')
    receipt_file = request.files['receipt'] if 'receipt' in request.files else None

    
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
