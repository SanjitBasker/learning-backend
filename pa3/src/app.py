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
    user["transactions"] = []
    return success_response(user)


@app.route("/api/user/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user:
        transactions = DB.get_transactions_by_uid(user_id)
        user["transactions"] = transactions
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

# transactions


@app.route("/api/transactions/", methods=["GET"])
def get_transactions():
    return success_response(DB.get_all_transactions())


@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    message = body.get("message")
    accepted = body.get("accepted")

    u1 = DB.get_user_by_id(sender_id)
    u2 = DB.get_user_by_id(receiver_id)
    if not(u1 and u2 and amount is not None and message):
        print(u1)
        print(u2)
        print(message)
        return failure_response("not enough arguments")
    if accepted and u1["balance"] < amount:
        return failure_response("not enough funds")
    x_id = DB.insert_transaction_table(
        sender_id, receiver_id, amount, message, accepted)
    if accepted:
        DB.mark_transaction(x_id, True)
    return success_response(DB.get_transaction_by_id(x_id))


@app.route("/api/transaction/<int:x_id>/", methods=["POST"])
def mark_transaction(x_id):
    body = json.loads(request.data)
    b = body.get("accepted")
    if b is None:
        return failure_response("accept or not?")
    t = DB.get_transaction_by_id(x_id)
    if t is None:
        return failure_response("could not find transaction")
    if t["accepted"] is not None:
        return failure_response("transation already accepted/denied")
    if b and DB.get_user_by_id(t["sender_id"])["balance"] < t["amount"]:
        return failure_response("not enough funds")
    else:
        DB.mark_transaction(x_id, b)
        return success_response(DB.get_transaction_by_id(x_id))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
