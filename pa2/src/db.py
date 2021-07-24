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


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect('user.db', check_same_thread=False)
        self.create_user_table()

    def create_user_table(self):
        self.conn.execute("DROP TABLE IF EXISTS user;")
        self.conn.commit()
        self.conn.execute("""
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                passwordhash TEXT,
                balance INTEGER NOT NULL
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

    
