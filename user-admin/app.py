from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__)

# URL interna del auth-service dentro de Kubernetes (Service ClusterIP)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:5000")

@app.route("/", methods=["GET"])
def index():
    # Solo muestra el formulario; la base la maneja auth-service
    return render_template("manage_users.html")

@app.route("/add", methods=["POST"])
def add():
    username = request.form["username"]
    password = request.form["password"]

    # Llamar al microservicio de auth para crear el usuario
    resp = requests.post(
        f"{AUTH_SERVICE_URL}/users",
        json={"username": username, "password": password},
        timeout=5,
    )

    if resp.status_code != 201:
        # Aquí puedes mostrar un mensaje de error si quieres
        # por ahora solo volvemos al formulario
        return render_template(
            "manage_users.html",
            error="No se pudo crear el usuario (auth-service devolvió error)."
        )

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
