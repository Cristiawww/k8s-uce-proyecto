import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    cur.execute(
        "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
        ("admin", "admin123")
    )
    conn.commit()
    conn.close()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None)

    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM users WHERE username=? AND password=?",
        (username, password)
    )
    row = cur.fetchone()
    conn.close()

    if row:
        return redirect(url_for("welcome", user=username))
    else:
        return render_template("login.html", error="Invalid credentials")


# NUEVO: endpoint para crear usuarios desde user-admin
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # usuario ya existe
        conn.close()
        return jsonify({"error": "user already exists"}), 409

    conn.close()
    return jsonify({"message": "user created"}), 201


@app.route("/")
def root():
    return render_template("login.html", error=None)


@app.route("/welcome")
def welcome():
    username = request.args.get("user", "usuario")
    return render_template("welcome.html", username=username)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
