from flask import Flask, render_template
import os

app = Flask(__name__)

MENU_FILE = os.path.join("data", "menu.json")
ORDERS_FILE = os.path.join("data", "orders.json")
USERS_FILE = os.path.join("data", "users.json")

@app.route('/')
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
