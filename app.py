from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB = "tasks.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL DEFAULT 0
            )
        """)

def get_tasks():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM tasks ORDER BY score DESC, id ASC"
        ).fetchall()

def update_score(task_id, delta):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "UPDATE tasks SET score = score + ? WHERE id = ?",
            (delta, task_id)
        )

def add_task(name):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT INTO tasks (name) VALUES (?)",
            (name,)
        )

HTML = """
<!doctype html>
<title>Task Scorer</title>
<h1>Task List</h1>

<form method="post" action="/add">
    <input name="name" placeholder="New task" required>
    <button type="submit">Add</button>
</form>

<hr>

{% for task in tasks %}
<div style="margin-bottom:8px;">
    <strong>{{ task.score }}</strong>
    {{ task.name }}

    <form style="display:inline;" method="post" action="/inc/{{task.id}}">
        <button>+</button>
    </form>

    <form style="display:inline;" method="post" action="/dec/{{task.id}}">
        <button>-</button>
    </form>
</div>
{% endfor %}
"""

@app.route("/")
def index():
    return render_template_string(HTML, tasks=get_tasks())

@app.route("/add", methods=["POST"])
def add():
    add_task(request.form["name"])
    return redirect(url_for("index"))

@app.route("/inc/<int:task_id>", methods=["POST"])
def inc(task_id):
    update_score(task_id, 1)
    return redirect(url_for("index"))

@app.route("/dec/<int:task_id>", methods=["POST"])
def dec(task_id):
    update_score(task_id, -1)
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, user_reloader=False)
