import json
from flask import request
from flask import Flask

app = Flask(__name__)

tasks = {
    0: {
        "id": 0,
        "description": "fold laundry",
        "done": False
    },
    1: {
        "id": 1,
        "description": "homework",
        "done": False
    }
}
task_id_counter = 2

@app.route("/")
@app.route("/tasks")
def get_tasks():
    res = {
        "success": True,
        "data": list(tasks.values())
    }
    return json.dumps(res), 200

@app.route("/tasks", methods=["POST"])
def create_task():
    global task_id_counter
    body = json.loads(request.data)
    description = body.get("description", "(no description)")
    task = {"id": task_id_counter, "description": description, "done": False}
    tasks[task_id_counter] = task
    task_id_counter += 1
    return json.dumps({"success": True, "data": task}), 201 # https://httpstatuses.com/

@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"success": False, "error": "Task not found"}), 404
    return json.dumps({"success": True, "data": task}), 200

@app.route("/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"success": False, "error": "Task not found"}), 404
    body = json.loads(request.data)
    task["description"] = body.get("description", "(no updated description)")
    task["done"] = body.get("done", False)
    return json.dumps({"success": True, "data": task}), 200



if __name__=="__main__":
        app.run(host="0.0.0.0", port=5000, debug=True)