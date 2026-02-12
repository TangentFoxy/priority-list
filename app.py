from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB = "db/tasks.db"

def initialize_database():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at INTEGER DEFAULT (strftime('%s','now')),
                name TEXT NOT NULL,
                upvotes INTEGER NOT NULL DEFAULT 0,
                downvotes INTEGER NOT NULL DEFAULT 0
            )
        """)

def get_tasks():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM tasks ORDER BY upvotes - downvotes DESC, id ASC"
        ).fetchall()

def upvote_task(task_id):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "UPDATE tasks SET upvotes = upvotes + 1 WHERE id = ?",
            (task_id,)
        )

def downvote_task(task_id):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "UPDATE tasks SET downvotes = downvotes + 1 WHERE id = ?",
            (task_id,)
        )

def add_task(name):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT INTO tasks (name) VALUES (?)",
            (name,)
        )

def remove_task(task_id):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

HTML = """
<!doctype html>
<title>priority-list</title>
<h1>priority-list</h1>

<form method="post" action="/add">
    <input name="name" placeholder="new item" required autofocus>
    <button type="submit">+</button>
</form>

<hr>

{% for task in tasks %}
<div style="margin-bottom:8px;">
    <form style="display:inline;" method="post" action="/delete/{{task.id}}">
        <button style="color:red;">×</button>
    </form>

    <form style="display:inline;" method="post" action="/increment/{{task.id}}">
        <button>+</button>
    </form>

    <form style="display:inline;" method="post" action="/decrement/{{task.id}}">
        <button>-</button>
    </form>

    <div style="width:192px;display:inline-block;"><strong>{{ task.upvotes - task.downvotes }}</strong> ({{ task.upvotes }} - {{ task.downvotes }})</div>
    {{ task.name }}
</div>
{% endfor %}
"""

@app.route("/")
def index():
    return render_template_string(HTML, tasks=get_tasks())

@app.route("/add", methods=["POST"])
def add():
    add_task(request.form["name"].strip())
    return redirect(url_for("index"))

@app.route("/increment/<int:task_id>", methods=["POST"])
def increment(task_id):
    upvote_task(task_id)
    return redirect(url_for("index"))

@app.route("/decrement/<int:task_id>", methods=["POST"])
def decrement(task_id):
    downvote_task(task_id)
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    remove_task(task_id)
    return redirect(url_for("index"))

initialize_database()
app.run(debug=True)
