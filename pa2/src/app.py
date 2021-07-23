import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here
@app.route("/api/users/", methods=["GET"])
def get_all_users():
    pass

@app.route("/api/users/", methods=["POST"])
def create_user():
    pass

@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    pass

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    pass

@app.route("/api/send/")
def send_money():
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
