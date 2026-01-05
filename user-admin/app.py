import os
import sqlite3
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'uce-k8s-project-2025')

POSTGRES_URL = os.environ.get('POSTGRES_URL')
DB_PATH = '/app/data/users.db'  # Volumen compartido



def get_db_connection():
    """Prefer PostgreSQL → fallback SQLite"""
    if POSTGRES_URL and PSYCOPG2_AVAILABLE:
        try:
            return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"❌ PostgreSQL error, switching to SQLite: {e}")

    print("✅ Using SQLite database")
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    if PSYCOPG2_AVAILABLE and POSTGRES_URL:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(20) UNIQUE NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database ready")


def generate_username(first_name, last_name):
    name_short = first_name[:3].lower()
    last_short = last_name[:4].lower()
    username = f"{name_short}{last_short}"

    if len(username) > 7:
        username = username[:7]
    elif len(username) < 5:
        username += "01"

    username = ''.join(c for c in username if c.isalnum())

    conn = get_db_connection()
    cur = conn.cursor()

    # Pick correct placeholder depending on DB
    if PSYCOPG2_AVAILABLE and POSTGRES_URL:
        query = "SELECT 1 FROM users WHERE username = %s"
    else:
        query = "SELECT 1 FROM users WHERE username = ?"

    original = username
    counter = 1

    while True:
        cur.execute(query, (username,))
        if not cur.fetchone():
            break
        username = f"{original[:5]}{counter}"
        counter += 1

    cur.close()
    conn.close()
    return username


@app.route("/", methods=["GET", "POST"])
def index():
    success_username = None

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # VALIDATIONS
        if not all([first_name, last_name, email, password, confirm_password]):
            flash("All fields are required.", "error")

        elif password != confirm_password:
            flash("Passwords do not match.", "error")

        elif len(password) < 8:
            flash("Password must be at least 8 characters.", "error")

        elif not email.endswith("@uce.edu.ec"):
            flash("Institutional email @uce.edu.ec is required.", "error")

        else:
            username = generate_username(first_name, last_name)

            try:
                conn = get_db_connection()
                cur = conn.cursor()
                password_hash = generate_password_hash(password)

                # Pick correct INSERT placeholder
                if PSYCOPG2_AVAILABLE and POSTGRES_URL:
                    query = """
                        INSERT INTO users (username, first_name, last_name, email, password_hash)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                else:
                    query = """
                        INSERT INTO users (username, first_name, last_name, email, password_hash)
                        VALUES (?, ?, ?, ?, ?)
                    """

                cur.execute(query, (username, first_name, last_name, email, password_hash))
                conn.commit()

                flash(f"User '{username}' successfully created!", "success")
                success_username = username

            except Exception as e:
                flash(f"Error creating user: {str(e)}", "error")

            finally:
                cur.close()
                conn.close()

        return render_template("manage_users.html", success_username=success_username)

    return render_template("manage_users.html")


@app.route("/users", methods=["GET"])
def list_users():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, username, first_name, last_name, email, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()

    cur.close()
    conn.close()

    users_list = []

    for user in users:
        if isinstance(user, dict):
            users_list.append(user)
        else:
            users_list.append({
                "id": user[0],
                "username": user[1],
                "first_name": user[2],
                "last_name": user[3],
                "email": user[4],
                "created_at": user[5]
            })

    return jsonify(users_list)


@app.route("/login")
def login_link():
    return redirect("http://localhost:5001")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=6000, debug=True)
