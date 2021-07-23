import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)

def myHash(word):
    return word

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code


@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here
@app.route("/api/users/", methods=["GET"])
def get_users():
    return success_response(DB.get_all_users())

@app.route("/api/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    passwordhash = myHash(body.get("password", "password"))
    balance = body.get("balance", 0)
    if not (name and username):
        return failure_response("not enough information", 400)

    user = DB.insert_user_table(name, username, passwordhash, balance)
    return success_response(user)


@app.route("/api/user/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user:
        return success_response(user)
    return failure_response("user not found")


@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user:
        DB.delete_user_by_id(user_id)
        return success_response(user)
    return failure_response("user not found", code=400)


@app.route("/api/send/", methods=["POST"])
def send_money():
    body = json.loads(request.data)
    id1 = body.get("sender_id")
    id2 = body.get("receiver_id")
    change = body.get("amount")
    if id1 is not None and id2 is not None and change:
        usr1bal = DB.get_user_by_id(id1)["balance"]
        if usr1bal < change:
            return failure_response("not enough monies", 400)
        DB.change_balance(id1, -change)
        DB.change_balance(id2, change)
        return success_response({
            "sender_id": id1, 
            "receiver_id": id2,
            "amount": change})
    return failure_response("not enough inputs")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
