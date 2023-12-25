import json

from flask import Flask, request, render_template

app = Flask(__name__, template_folder= "../front-end/templates", static_folder="../front-end/static")

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/api/submit_expense", methods=['POST'])
def submit_expense():
    expense_data = request.get_json()
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
