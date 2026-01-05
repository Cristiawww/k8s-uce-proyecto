import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)
AUTH_SERVICE_URL = "http://localhost:5001"  # auth-service (local dev)

def generate_username(first_name, last_name):
    """Acrónimo 6-8 chars: pri3nom + pri4apell"""
    name_short = first_name[:3].lower()
    last_short = last_name[:4].lower()
    username = f"{name_short}{last_short}"
    return username[:8]  # Máx 8 chars

@app.route('/', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        email = request.form['email'].strip()
        
        username = generate_username(first_name, last_name)
        password = request.form.get('password', username.upper())  # Password = USERNAME.MAYUS si vacío
        
        # Enviar a auth-service
        resp = requests.post(
            f"{AUTH_SERVICE_URL}/register",
            data={'username': username, 'password': password},
            timeout=5
        )
        
        if resp.status_code == 200:
            return f'''
            <div style="background:#27ae60;color:white;padding:30px;text-align:center;font-size:20px;border-radius:15px;">
                ✅ Usuario CREADO!<br>
                <b>Usuario:</b> <code>{username}</code><br>
                <b>Password:</b> <code>{password}</code><br><br>
                <a href="/" style="color:#fff;background:#2a5298;padding:12px 24px;border-radius:8px;text-decoration:none;">← Nuevo Usuario</a>
            </div>
            '''
        return '''
        <div style="background:#e74c3c;color:white;padding:30px;text-align:center;font-size:20px;border-radius:15px;">
            ❌ Error creando usuario. Verifica que auth-service esté en localhost:5001
        </div>
        '''
    
    return '''
<!DOCTYPE html>
<html>
<head><title>Agregar Usuario - UCE</title>
<style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;}
    .header{position:fixed;top:0;left:0;right:0;background:linear-gradient(90deg,#1e3c72,#2a5298);color:white;padding:15px 0;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,0.3);z-index:1000;}
    .header h1{font-size:22px;font-weight:300;letter-spacing:1px;}
    .form-container{background:rgba(255,255,255,0.95);padding:40px;border-radius:15px;box-shadow:0 15px 35px rgba(0,0,0,0.2);width:100%;max-width:420px;margin:100px 20px 20px;backdrop-filter:blur(10px);}
    .form-title{text-align:center;color:#2a5298;font-size:26px;margin-bottom:30px;font-weight:600;}
    .form-group{margin-bottom:22px;}
    .form-group input{width:100%;padding:15px 18px;border:2px solid #e1e5e9;border-radius:10px;font-size:16px;transition:all 0.3s;background:#f8f9fa;}
    .form-group input:focus{outline:none;border-color:#2a5298;box-shadow:0 0 0 3px rgba(42,82,152,0.1);background:white;transform:translateY(-2px);}
    .add-btn{width:100%;padding:16px;background:linear-gradient(90deg,#2a5298,#1e3c72);color:white;border:none;border-radius:10px;font-size:18px;font-weight:600;cursor:pointer;transition:all 0.3s;text-transform:uppercase;}
    .add-btn:hover{transform:translateY(-3px);box-shadow:0 10px 25px rgba(42,82,152,0.4);}
    .auth-link{text-align:center;margin-top:25px;}
    .auth-link a{color:#2a5298;text-decoration:none;font-weight:500;font-size:16px;}
</style>
</head>
<body>
<div class="header">
    <h1>UNIVERSIDAD CENTRAL DEL ECUADOR</h1>
    <p>ADMIN USUARIOS</p>
</div>
<div class="form-container">
    <h2 class="form-title">Agregar Nuevo Usuario</h2>
    <form method="POST">
        <div class="form-group">
            <input name="first_name" placeholder="Nombres" required>
        </div>
        <div class="form-group">
            <input name="last_name" placeholder="Apellidos" required>
        </div>
        <div class="form-group">
            <input name="email" type="email" placeholder="Correo Electrónico">
        </div>
        <div class="form-group">
            <input name="password" type="password" placeholder="Contraseña (opcional, auto si vacío)">
        </div>
        <button class="add-btn">Agregar Usuario</button>
    </form>
    <div class="auth-link">
        <a href="http://localhost:5001">← Ir a Login</a>
    </div>
</div>
</body>
</html>
    '''

if __name__ == '__main__':
    print("🚀 User-Admin → localhost:6001")
    app.run(host="0.0.0.0", port=6000, debug=True)
