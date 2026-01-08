import os
import sqlite3
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

from flask import Flask, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')

POSTGRES_URL = os.environ.get('POSTGRES_URL')

# IMPORTANT: SAME DB AS USER-ADMIN
DB_PATH = '/app/data/users.db' 


# -----------------------------------------
# DATABASE CONNECTION
# -----------------------------------------
def get_db_connection():
    if POSTGRES_URL and PSYCOPG2_AVAILABLE:
        try:
            conn = psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)
            print("✅ Connected to PostgreSQL")
            return conn
        except Exception as e:
            print(f"❌ PostgreSQL failed → Using SQLite: {e}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    print("✅ Connected to SQLite")
    return conn


# -----------------------------------------
# INIT DATABASE
# -----------------------------------------
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    if POSTGRES_URL and PSYCOPG2_AVAILABLE and 'psycopg2' in str(type(conn)):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database ready")


# -----------------------------------------
# LOGIN
# -----------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        if POSTGRES_URL and PSYCOPG2_AVAILABLE and 'psycopg2' in str(type(conn)):
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        else:
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        user = dict(row) if row else None

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']

            return """
<!DOCTYPE html>
<html>
<head>
<title>Academic System - UCE</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:#f5f6fa;}
.header{position:fixed;top:0;left:0;right:0;background:#003087;color:white;padding:10px 20px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 2px 10px rgba(0,0,0,0.1);z-index:1000;}
.logo{font-size:24px;font-weight:bold;}
.user-info{display:flex;align-items:center;gap:15px;}
.username{font-weight:500;}
.logout-btn{background:#dc3545;color:white;padding:8px 16px;border:none;border-radius:6px;cursor:pointer;font-size:14px;transition:background 0.3s;}
.logout-btn:hover{background:#c82333;}
.main-content{margin-top:80px;padding:40px;max-width:1200px;margin-left:auto;margin-right:auto;}
.welcome{background:linear-gradient(135deg,#003087,#0056b3);color:white;padding:60px;border-radius:15px;text-align:center;margin-bottom:40px;box-shadow:0 10px 30px rgba(0,48,135,0.3);}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:25px;margin-top:40px;}
.card{background:white;padding:30px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.08);text-align:center;transition:transform 0.3s;}
.card:hover{transform:translateY(-5px);}
.footer{background:#003087;color:white;padding:20px;text-align:center;margin-top:60px;}
</style>
</head>
<body>
<div class="header">
<div class="logo">UCE <span style="font-size:14px;">Academic System</span></div>
<div class="user-info">
<span class="username">User Logged</span>
<button class="logout-btn" onclick="window.location.href='/logout'">Logout</button>
</div>
</div>

<div class="main-content">
<div class="welcome">
<h1>Welcome to the Academic System</h1>
<p>University Management Platform</p>
</div>

<div class="cards">
<div class="card">
<h3>📚 Student Management</h3>
<p>Register, edit and consult academic data</p>
</div>

<div class="card">
<h3>📊 Degree Reports</h3>
<p>Automatic academic report generation</p>
</div>

<div class="card">
<h3>⚙️ Configuration</h3>
<p>Manage academic periods and settings</p>
</div>
</div>
</div>

<div class="footer">
<p>© 2026 University Academic System</p>
</div>
</body>
</html>
"""

        return """
        <div style="background:#e74c3c;color:white;padding:10px;text-align:center;font-weight:bold;">
            ❌ Invalid username or password
        </div>
        <script>history.back();</script>
        """

    return """
<!DOCTYPE html>
<html>
<head>
<title>UCE Academic System</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI';background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center;}
.header{position:fixed;top:0;left:0;right:0;background:#1e3c72;color:white;text-align:center;padding:15px;}
.container{background:white;padding:40px;border-radius:15px;box-shadow:0 15px 35px rgba(0,0,0,0.2);width:380px;margin-top:70px;}
button{width:100%;padding:15px;background:#2a5298;color:white;border:none;border-radius:10px;font-size:18px;cursor:pointer;}
input{width:100%;padding:15px;border:2px solid #ddd;border-radius:10px;margin-bottom:20px;}
</style>
</head>
<body>
<div class="header">
<h1>UNIVERSITY ACADEMIC SYSTEM</h1>
</div>
<div class="container">
<h2 style="text-align:center;color:#2a5298;">Login</h2>
<form method="POST">
<input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Login</button>
</form>
<br>
<div style="text-align:center">
<a href="http://192.168.59.101:30081">➕ Nuevo Usuario (Crear-Usuario)</a>
</div>
</div>
</body>
</html>
"""


# -----------------------------------------
# REGISTER
# -----------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            if POSTGRES_URL and PSYCOPG2_AVAILABLE and 'psycopg2' in str(type(conn)):
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                            (username, password))
            else:
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                            (username, password))

            conn.commit()

            return '''
            <div style="background:#27ae60;color:white;padding:20px;text-align:center;">
                ✅ User registered successfully! <a href="/">Login</a>
            </div>
            '''

        except:
            return '''
            <div style="background:#e74c3c;color:white;padding:20px;text-align:center;">
                ❌ Username already exists
            </div>
            <script>setTimeout(()=>history.back(),2000);</script>
            '''

        finally:
            cur.close()
            conn.close()

    return "<h2>Register Page</h2>"


# -----------------------------------------
# USERS JSON
# -----------------------------------------
@app.route('/users')
def users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, created_at FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    users = [dict(r) if not isinstance(r, dict) else r for r in rows]
    return jsonify(users)


# -----------------------------------------
# LOGOUT
# -----------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return """
    <div style="background:#27ae60;color:white;padding:40px;text-align:center;font-size:22px;">
        ✅ Session closed successfully
        <br><br>
        <a href="/">Return to Login</a>
    </div>
    """


# -----------------------------------------
# RUN
# -----------------------------------------
if __name__ == '__main__':
    init_db()
    print("🚀 AUTH SERVICE RUNNING ON PORT 5001")
    app.run(host="0.0.0.0", port=5000, debug=True)
