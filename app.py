# ---------------------------------------------------
# Imports
# ---------------------------------------------------
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
import requests
import json

# ---------------------------------------------------
# Inicialização do Flask
# ---------------------------------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Chave secreta para a sessão

# ---------------------------------------------------
# Função para ligar à base de dados MySQL
# ---------------------------------------------------
def ligar_bd():
    """
    Cria e retorna a conexão com o servidor MySQL.
    """
    return mysql.connector.connect(
        host="62.28.39.135",
        user="efa0125",
        password="123.Abc",
        database="efa0125_06_Leonardo_clinica_veterinaria"
    )
# ---------------------------------------------------
# Base
# ---------------------------------------------------
@app.route("/")
def base():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    return render_template("base.html") 
# ---------------------------------------------------
# Login
# ---------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cnx = ligar_bd()
        cursor = cnx.cursor(dictionary=True)

        # Verificar se o utilizador existe
        cursor.execute(
            "SELECT id, username, password, role FROM users WHERE username = %s", (username,)
        )
        user = cursor.fetchone()

        cursor.close()
        cnx.close()

        # Validar senha
        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["user_role"] = user["role"]
            return redirect(url_for("base"))
        else:
            flash("Username ou password incorretos.")
            return redirect(url_for("login"))

    # Se GET, exibir formulário de login
    return render_template("users/login.html")

# ---------------------------------------------------
# Logout
# ---------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()  # Limpar sessão
    return redirect(url_for("login"))













# ---------------------------------------------------
# Iniciar o servidor Flask
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
