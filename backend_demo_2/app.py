import json
import db
from flask import Flask, request

app = Flask(__name__)
DB = db.DatabaseDriver()

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

@app.route("/")
@app.route("/tasks/")
def get_tasks():
    return success_response(DB.get_all_tasks())


@app.route("/tasks/", methods=["POST"])
def create_task():
    body = json.loads(request.data)
    description = body.get("description", "(no desc)")
    task_id = DB.insert_task_table(description, False)
    task = DB.get_task_by_id(task_id)
    if task:
        return success_response(task, 201)
    return failure_response("Something went wrong while creating task")
    pass


@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    task = DB.get_task_by_id(task_id)
    if task:
        return success_response(task)
    return failure_response("task not found")


@app.route("/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    body = json.loads(request.data)
    DB.update_task_by_id(body.get("description"), body.get("done"), task_id)
    
    task = DB.get_task_by_id(task_id)
    if task:
        return success_response(task)
    
    return failure_response("task not found")


@app.route("/tasks/<int:task_id>/", methods=["DELETE"])
def delete_task(task_id):
    task = DB.get_task_by_id(task_id)
    if task:
        DB.delete_task_by_id(task_id)
        return success_response(task)
    return failure_response("task not found")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
