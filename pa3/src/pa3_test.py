import json
from threading import Thread
from time import sleep
import unittest

from app import app
import requests

# NOTE: Make sure you run 'pip3 install requests' in your virtualenv

# URL pointing to your local dev host
LOCAL_URL = "http://localhost:5000"
SAMPLE_USER1 = {"name": "Conner", "username": "cswenberg", "balance": 10}
SAMPLE_USER2 = {"name": "Alicia", "username": "aawang", "balance": 10}
SAMPLE_TRANSACTION = {"amount": 5, "message": "boba"}


# Request endpoint generators
def gen_users_path(user_id=None):
    base_path = f"{LOCAL_URL}/api/user"
    return (
        base_path + "s/" if user_id is None else f"{base_path}/{str(user_id)}/"
    )


def gen_transactions_path(txn_id=None):
    base_path = f"{LOCAL_URL}/api/transaction"
    return base_path + "s/" if txn_id is None else f"{base_path}/{str(txn_id)}/"


def unwrap_response(response, body={}):
    try:
        return response.json()
    except Exception as e:
        req = response.request
        raise Exception(
            f"""
            Error encountered on the following request:

            request path: {req.url}
            request method: {req.method}
            request body: {str(body)}
            exception: {str(e)}

            There is an uncaught-exception being thrown in your
            method handler for this route!
            """
        )


# Transaction body generator
def gen_transaction_body(sender_id, receiver_id, accepted):
    return {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        **SAMPLE_TRANSACTION,
        "accepted": accepted,
    }


class TestRoutes(unittest.TestCase):

    # ---- USERS -----------------------------------------------------------

    def test_get_initial_users(self):
        res = requests.get(gen_users_path())
        body = unwrap_response(res)
        assert body.get("success")

    def test_create_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER1))
        body = unwrap_response(res, SAMPLE_USER1)
        user = body.get("data")
        assert body.get("success")
        assert user.get("name") == SAMPLE_USER1["name"]
        assert user.get("username") == SAMPLE_USER1["username"]
        assert user.get("balance") == SAMPLE_USER1["balance"]

    def test_get_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER1))
        body = unwrap_response(res, SAMPLE_USER1)
        user = body.get("data")

        res = requests.get(gen_users_path(user.get("id")))
        body = unwrap_response(res)
        user = body.get("data")
        assert body.get("success")
        assert user.get("id") is not None
        assert user.get("name") == SAMPLE_USER1["name"]
        assert user.get("username") == SAMPLE_USER1["username"]
        assert user.get("balance") == SAMPLE_USER1["balance"]

    def test_delete_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER1))
        body = unwrap_response(res, SAMPLE_USER1)
        user_id = body.get("data").get("id")

        res = requests.delete(gen_users_path(user_id))
        body = unwrap_response(res)
        assert body.get("success")

        res = requests.get(gen_users_path(user_id))
        body = unwrap_response(res)
        assert not body.get("success")

    def test_get_invalid_user(self):
        res = requests.get(gen_users_path(1000))
        body = unwrap_response(res)
        assert not body.get("success")

    def test_delete_invalid_user(self):
        res = requests.delete(gen_users_path(1000))
        body = unwrap_response(res)
        assert not body.get("success")

    # ---- TRANSACTIONS  ---------------------------------------------------

    def create_transaction(self, sender_id, receiver_id, accepted):
        res = requests.post(
            gen_transactions_path(),
            data=json.dumps(
                gen_transaction_body(sender_id, receiver_id, accepted)
            ),
        )
        return unwrap_response(res)

    def setup_transaction(self, accepted):
        """
        Creates a sender and receiver user and creates a transaction between them.
        """
        res1 = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER1))
        body1 = unwrap_response(res1)
        user1 = body1.get("data")
        res2 = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER2))
        body2 = unwrap_response(res2)
        user2 = body2.get("data")

        body = self.create_transaction(
            user1.get("id"), user2.get("id"), accepted
        )

        return [user1, user2, body]

    def test_send_money(self):
        user1, user2, body = self.setup_transaction(True)

        user1_initial_balance = user1.get("balance")
        user2_initial_balance = user2.get("balance")

        data = body.get("data")
        assert body.get("success")
        assert data.get("sender_id") == user1.get("id")
        assert data.get("receiver_id") == user2.get("id")
        assert data.get("amount") == SAMPLE_TRANSACTION["amount"]
        assert data.get("message") == SAMPLE_TRANSACTION["message"]
        assert data.get("accepted")

        res1 = requests.get(gen_users_path(user1.get("id")))
        body1 = unwrap_response(res1)
        user1 = body1.get("data")

        res2 = requests.get(gen_users_path(user2.get("id")))
        body2 = unwrap_response(res2)
        user2 = body2.get("data")

        assert user1.get("balance") == user1_initial_balance - data.get(
            "amount"
        )
        assert len(user1.get("transactions")) == 1
        assert user2.get("balance") == user2_initial_balance + data.get(
            "amount"
        )
        assert len(user2.get("transactions")) == 1

    def test_request_payment(self):
        user1, user2, body = self.setup_transaction(None)

        user1_initial_balance = user1.get("balance")
        user2_initial_balance = user2.get("balance")

        data = body.get("data")
        assert body.get("success")
        assert data.get("sender_id") == user1.get("id")
        assert data.get("receiver_id") == user2.get("id")
        assert data.get("amount") == SAMPLE_TRANSACTION["amount"]
        assert data.get("message") == SAMPLE_TRANSACTION["message"]
        assert not data.get("accepted")

        res1 = requests.get(gen_users_path(user1.get("id")))
        body1 = unwrap_response(res1)
        user1 = body1.get("data")

        res2 = requests.get(gen_users_path(user2.get("id")))
        body2 = unwrap_response(res2)
        user2 = body2.get("data")

        assert user1.get("balance") == user1_initial_balance
        assert len(user1.get("transactions")) == 1
        assert user2.get("balance") == user2_initial_balance
        assert len(user2.get("transactions")) == 1

    def test_accept_request(self):
        user1, user2, body = self.setup_transaction(None)
        data = body.get("data")

        user1_initial_balance = user1.get("balance")
        user2_initial_balance = user2.get("balance")

        res = requests.post(
            gen_transactions_path(data.get("id")),
            data=json.dumps({"sender": user1.get("id"), "accepted": True}),
        )
        body = unwrap_response(res)
        data = body.get("data")
        assert body.get("success")
        assert data.get("sender_id") == user1.get("id")
        assert data.get("receiver_id") == user2.get("id")
        assert data.get("amount") == SAMPLE_TRANSACTION["amount"]
        assert data.get("message") == SAMPLE_TRANSACTION["message"]
        assert data.get("accepted")

        res1 = requests.get(gen_users_path(user1.get("id")))
        body1 = unwrap_response(res1)
        user1 = body1.get("data")

        res2 = requests.get(gen_users_path(user2.get("id")))
        body2 = unwrap_response(res2)
        user2 = body2.get("data")

        assert user1.get("balance") == user1_initial_balance - data.get(
            "amount"
        )
        assert len(user1.get("transactions")) == 1
        assert user2.get("balance") == user2_initial_balance + data.get(
            "amount"
        )
        assert len(user2.get("transactions")) == 1

    def test_deny_request(self):
        user1, user2, body = self.setup_transaction(None)

        user1_initial_balance = user1.get("balance")
        user2_initial_balance = user2.get("balance")

        data = body.get("data")
        res = requests.post(
            gen_transactions_path(data.get("id")),
            data=json.dumps({"accepted": False}),
        )
        body = unwrap_response(res)
        data = body.get("data")
        assert body.get("success")
        assert data.get("sender_id") == user1.get("id")
        assert data.get("receiver_id") == user2.get("id")
        assert data.get("amount") == SAMPLE_TRANSACTION["amount"]
        assert data.get("message") == SAMPLE_TRANSACTION["message"]
        assert not data.get("accepted")

        res1 = requests.get(gen_users_path(user1.get("id")))
        body1 = unwrap_response(res1)
        user1 = body1.get("data")

        res2 = requests.get(gen_users_path(user2.get("id")))
        body2 = unwrap_response(res2)
        user2 = body2.get("data")

        assert user1.get("balance") == user1_initial_balance
        assert len(user1.get("transactions")) == 1
        assert user2.get("balance") == user2_initial_balance
        assert len(user2.get("transactions")) == 1

    def test_overdraw_send(self):
        user1, user2, _ = self.setup_transaction(True)

        # balances should be 5 and 15 respectively
        body1 = self.create_transaction(user1.get("id"), user2.get("id"), True)
        assert body1["success"]

        # balances should be 0 and 20 respectively
        # should not go through because user1 has no more money
        # meaning that the transaction is not created in the table either
        body2 = self.create_transaction(user1.get("id"), user2.get("id"), True)
        assert not body2["success"]

        res1 = requests.get(gen_users_path(user1.get("id")))
        body1 = unwrap_response(res1)
        user1 = body1.get("data")

        res2 = requests.get(gen_users_path(user2.get("id")))
        body2 = unwrap_response(res2)
        user2 = body2.get("data")

        # balances should still be the same
        assert user1.get("balance") == 0
        assert len(user1.get("transactions")) == 2
        assert user2.get("balance") == 20
        assert len(user2.get("transactions")) == 2

    def test_overdraw_accept(self):
        user1, user2, body = self.setup_transaction(True)
        # balances should be 5 and 15 respectively
        res1 = self.create_transaction(user1.get("id"), user2.get("id"), True)
        # balances should be 0 and 20 respectively
        # this will still create a transaction in the table though because it hasn't been accepted yet
        body2 = self.create_transaction(user1.get("id"), user2.get("id"), None)
        # sends request that user1 cannot fulfill
        data = body.get("data")

        res3 = requests.post(
            gen_transactions_path(data.get("id")),
            data=json.dumps({"sender": user1.get("id"), "accepted": True}),
        )
        body3 = unwrap_response(res3)

        assert not body3["success"]

        res1 = requests.get(gen_users_path(user1.get("id")))
        body1 = unwrap_response(res1)
        user1 = body1.get("data")

        res2 = requests.get(gen_users_path(user2.get("id")))
        body2 = unwrap_response(res2)
        user2 = body2.get("data")

        # balances should still be the same
        assert user1.get("balance") == 0
        print("bad", len(user1.get("transactions")))
        assert len(user1.get("transactions")) == 3
        assert user2.get("balance") == 20
        assert len(user2.get("transactions")) == 3


def run_tests():
    sleep(1.5)
    unittest.main()


if __name__ == "__main__":
    thread = Thread(target=run_tests)
    thread.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
