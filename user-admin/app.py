import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'uce-k8s-proyecto-2025'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def index():
    return render_template("manage_users.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validaciones
        if not all([first_name, last_name, email, password, confirm_password]):
            flash("Todos los campos son obligatorios", "error")
            return render_template("manage_users.html")
        
        if password != confirm_password:
            flash("Las contraseñas no coinciden", "error")
            return render_template("manage_users.html")
        
        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres", "error")
            return render_template("manage_users.html")

        # Email institucional UCE
        if not email.endswith("@uce.edu.ec"):
            flash("Debe usar correo institucional @uce.edu.ec", "error")
            return render_template("manage_users.html")

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            password_hash = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (first_name, last_name, email, password_hash) VALUES (?, ?, ?, ?)",
                (first_name, last_name, email, password_hash)
            )
            conn.commit()
            flash(f"Usuario {first_name} {last_name} creado exitosamente", "success")
        except sqlite3.IntegrityError:
            flash("El correo ya está registrado", "error")
        finally:
            conn.close()

    return render_template("manage_users.html")

@app.route("/login")
def login_link():
    return redirect("http://localhost:5000")  # ← auth-service

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=True)
