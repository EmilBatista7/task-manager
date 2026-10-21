
from flask import Flask, render_template, request, redirect, url_for
from db import get_connection

app = Flask(__name__)


from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
)
from db import get_connection

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify(status="ok"), 200


@app.route("/health/db")
def database_health():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()

        return jsonify(status="ok", database="connected"), 200

    except Exception:
        app.logger.exception("Error comprobando la conexion a MySQL")
        return jsonify(status="error", database="unavailable"), 503

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/")
def home():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id, title, completed, created_at "
            "FROM tasks ORDER BY id DESC"
        )
        tasks = cursor.fetchall()

        total = len(tasks)
        completed = sum(bool(task["completed"]) for task in tasks)
        pending = total - completed

        return render_template(
            "index.html",
            tasks=tasks,
            total=total,
            completed=completed,
            pending=pending,
        )
    finally:
        cursor.close()
        connection.close()


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()

    if title:
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO tasks (title) VALUES (%s)",
                (title,),
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    return redirect(url_for("home"))


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE tasks
            SET completed = NOT completed
            WHERE id = %s
            """,
            (task_id,),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s",
            (task_id,),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
