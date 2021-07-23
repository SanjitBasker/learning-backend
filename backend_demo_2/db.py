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
        self.conn = sqlite3.connect('todo.db', check_same_thread=False)
        self.create_task_table()
    
    def create_task_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE task (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    done INTEGER NOT NULL
                );
            """)
            self.conn.commit()
        except Exception as e:
            print(e)

    def delete_task_table(self):
        self.conn.execute("""
            DROP TABLE IF EXISTS task;
        """)
        self.conn.commmit()

    def get_all_tasks(self):
        cursor = self.conn.execute("""
            SELECT * FROM task;
        """)
        tasks = []
        for row in cursor:
            tasks.append({
                "id": row[0],
                "description": row[1],
                "done": bool(row[2])
            })
        return tasks
    
    def insert_task_table(self, description, done):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO task (DESCRIPTION, DONE) VALUES (?, ?);
        """, (description, done))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_task_by_id(self, id):
        cursor = self.conn.execute("""
            SELECT * from task where ID = ?;
        """, (id,))
        for row in cursor:
            return {"id": row[0], "description": row[1], "done": bool(row[2])}
        return None

    def update_task_by_id(self, description, done, id):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE task SET DESCRIPTION = ?, DONE = ?
            WHERE ID = ?;
        """, (description, done, id))
        self.conn.commit()

    def delete_task_by_id(self, id):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM task WHERE id = ?;
        """, (id,))
        self.conn.commit()


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
