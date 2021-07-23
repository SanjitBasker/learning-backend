import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

posts = {
}

comments = {
}

post_count = 0

@app.route("/api/posts/")
def get_all_posts():
    res = {
        "success": True,
        "data": [posts[i] for i in posts]
    }
    return json.dumps(res), 200


@app.route("/api/posts/", methods = ['POST'])
def create_post():
    global post_count
    body = json.loads(request.data)
    for key in ["title", "link", "username"]:
        if not key in body:
            return json.dumps({
                "success": False,
                "error": "Not enough info"
            }), 400
    post = {
        "id": post_count,
        "upvotes": 1,
        "title": body["title"],
        "link": body["link"],
        "username": body["username"]
        }
    posts[post_count] = post
    comments[post_count] = {"comment_count": 0}
    post_count += 1
    return json.dumps({"success": True, "data": post}), 201

@app.route("/api/posts/<int:post_id>/", methods = ['GET'])
def get_post(post_id):
    if not post_id in posts:
        return json.dumps({"success": False,
        "error": "no such post"}), 400
    
    return json.dumps({
        "success": True,
        "data": posts[post_id]
    }), 200

@app.route("/api/posts/<int:post_id>/", methods = ['DELETE'])
def delete_post(post_id):
    a = post_id in posts
    b = post_id in comments
    if a ^ b:
        return json.dumps({
            "success": False, 
            "error": "Internal error"
            }), 500
    elif a and b:
        post = posts[post_id]
        del posts[post_id]
        del comments[post_id]
        return json.dumps({
            "success": True,
            "data": post
        }), 200
    else:
        return json.dumps({
            "success": False,
            "error": "no such post"
        }), 400


@app.route("/api/posts/<int:post_id>/comments/", methods = ['GET'])
def get_comments(post_id):
    if not post_id in comments:
        return json.dumps({
            "success": False,
            "error": "No such post"
        }), 400
    else:
        return json.dumps({
            "success": True,
            "data": [comments[post_id][i] for i in comments[post_id] if i != "comment_count"]
            }), 200
    

@app.route("/api/posts/<int:post_id>/comments/", methods = ['POST'])
def create_comment(post_id):
    body = json.loads(request.data)
    for key in ["text", "username"]:
        if not key in body:
            return json.dumps({
                "success": False,
                "error": "Not enough info"
            }), 400
    if not post_id in posts:
        return json.dumps({
                "success": False,
                "error": "No such post"
            }), 400
    these_comments = comments[post_id]
    comment_id = these_comments['comment_count']
    comment = {
        "id": comment_id,
        "upvotes": 1,
        "text": body["text"],
        "username": body["username"]
    }
    these_comments[comment_id] = comment
    these_comments['comment_count'] += 1
    return json.dumps({
        "success": True,
        "data": comment
    }), 200

@app.route("/api/posts/<int:post_id>/comments/<int:comment_id>/", methods = ['POST'])
def edit_comment(post_id, comment_id):
    body = json.loads(request.data)
    if not "text" in body:
        return json.dumps({
                "success": False,
                "error": "No text"
            }), 400
    comments[post_id][comment_id]['text'] = body["text"]
    return json.dumps({
        "success": True,
        "data": comments[post_id][comment_id]
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
