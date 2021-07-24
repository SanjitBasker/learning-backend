import os
import sqlite3


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("todo.db", check_same_thread=False)
        self.create_task_table()

#-- TASKS -----------------------------------------------------------

    def create_task_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE task (
                    ID INTEGER PRIMARY KEY,
                    DESCRIPTION TEXT NOT NULL,
                    DONE BOOLEAN NOT NULL
                );
            """
            )
        except Exception as e:
            print(e)

    def delete_task_table(self):
        self.conn.execute("DROP TABLE IF EXISTS task;")

    def get_all_tasks(self):
        cursor = self.conn.execute("SELECT * FROM task;")
        tasks = []
        for row in cursor:
            tasks.append({"id": row[0], "description": row[1], "done": row[2]})
        return tasks

    def insert_task_table(self, description, done):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO task (DESCRIPTION, DONE) VALUES (?, ?);", (description, done)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_task_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM task WHERE ID = ?", (id,))
        for row in cursor:
            return {"id": row[0], "description": row[1], "done": row[2]}
        return None

    def update_task_by_id(self, id, description, done):
        self.conn.execute(
            """
            UPDATE task
            SET description = ?, done = ?
            WHERE id = ?;
        """,
            (description, done, id),
        )
        self.conn.commit()

    def delete_task_by_id(self, id):
        self.conn.execute(
            """
            DELETE FROM task
            WHERE id = ?;
        """,
            (id,),
        )
        self.conn.commit()

#-- SUBTASKS --------------------------------------------------------
