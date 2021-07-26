import os
import sqlite3

# From: https://goo.gl/YzypOI


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


def parse_row(row, columns):
    parsed_row = {}
    for i, col in enumerate(columns):
        parsed_row[col] = row[i]
    return parsed_row


def parse_cursor(cursor, columns):
    return [parse_row(row, columns) for row in cursor]


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect('user.db', check_same_thread=False)
        self.create_user_table()
        self.create_transaction_table()

    def create_user_table(self):
        # self.conn.execute("DROP TABLE IF EXISTS user;")
        self.conn.commit()
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                passwordhash TEXT,
                balance INTEGER NOT NULL
            );
        """)
        self.conn.commit()

    def create_transaction_table(self):
        self.conn.execute("DROP TABLE IF EXISTS transactions;")
        self.conn.commit()
        self.conn.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                message CHAR[100] NOT NULL,
                accepted INTEGER,
                timestamp TEXT NOT NULL
            );
        """)
        self.conn.commit()

    def get_all_users(self):
        users = self.conn.execute("""
            SELECT * FROM user;
        """)
        users_list = []
        for row in users:
            user = {}
            user["id"] = row[0]
            user["name"] = row[1]
            user["username"] = row[2]
            users_list.append(user)
        return users_list

    def insert_user_table(self, name, username, passwordhash, balance=0):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO user (name, username, passwordhash, balance) 
            VALUES (?,?,?,?);
        """, (name, username, passwordhash, balance))
        self.conn.commit()
        return self.get_user_by_id(cursor.lastrowid)

    def get_user_by_id(self, user_id):
        cursor = self.conn.execute("""
            SELECT * from user WHERE id = ?;
        """, (user_id,))
        for row in cursor:
            user = {}
            user["id"] = row[0]
            user["name"] = row[1]
            user["username"] = row[2]
            user["balance"] = row[4]
            return user
        return None

    def delete_user_by_id(self, id):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM user WHERE id = ?;
        """, (id,))
        self.conn.commit()

    def change_balance(self, id, change):
        cursor = self.conn.execute("""
            SELECT * FROM user where id = ?;
        """, (id,))
        currentBal = None
        for row in cursor:
            currentBal = row[4]
            currentBal += change

        if currentBal is not None:
            cursor = self.conn.cursor()
            cursor.execute("""
            UPDATE user SET BALANCE = ?
            WHERE id = ?;
            """, (currentBal, id))
            self.conn.commit()
            return self.get_user_by_id(id)
        else:
            return None

    def get_all_transactions(self):
        xs = self.conn.execute("""
            SELECT * FROM transactions;
        """)
        x_list = parse_cursor(
            xs, ["id", "sender_id", "receiver_id", "amount", "message", "accepted", "timestamp"])
        return x_list

    def get_transaction_by_id(self, x_id):
        cursor = self.conn.execute(
            """
            SELECT * FROM transactions WHERE id = ?;
            """, (x_id,)
        )
        for row in cursor:
            return parse_row(row, ["id", "sender_id", "receiver_id", "amount", "message", "accepted", "timestamp"])

    def get_transactions_by_uid(self, user_id):
        cursor = self.conn.execute(
            """
            SELECT * FROM transactions WHERE (sender_id = ? OR receiver_id = ?);
            """, (user_id, user_id)
        )
        return parse_cursor(cursor, ["id", "sender_id", "receiver_id", "amount", "message", "accepted", "timestamp"])

    def insert_transaction_table(self, sender_id, receiver_id, amount, message, accepted):
        if accepted:
            accepted = 1
        elif accepted is None:
            accepted = None
        elif not accepted:
            accepted = 0
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (sender_id, receiver_id, amount, message, accepted, timestamp) VALUES
            (?, ?, ?, ?, ?, ?);
            """, (sender_id, receiver_id, amount, message, accepted, "notime")
        )
        self.conn.commit()
        return cursor.lastrowid

    def mark_transaction(self, x_id, b):
        t = self.conn.execute(
            """
            SELECT * FROM transactions WHERE id = ?;
            """, (x_id,)
        )
        r = None
        for row in t:
            r = parse_row(row, ["id", "sender_id", "receiver_id",
                                "amount", "message", "accepted", "timestamp"])
        cursor = self.conn.execute(
            """
            UPDATE transactions SET accepted=? WHERE id = ?;
            """, (int(b), x_id)
        )
        self.conn.commit()
        if b:
            u1 = r["sender_id"]
            u2 = r["receiver_id"]
            c = r["amount"]
            self.change_balance(u1, -c)
            self.change_balance(u2, c)
        return self.get_transaction_by_id(x_id)
