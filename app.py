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
            session["password"] = user["password"]
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
# Editar users (conta de acesso)
# ---------------------------------------------------

@app.route("/editar_users<int:id>", methods=["GET", "POST"]) # USUARIO E ROLE
def editar_users(id):
    # Proteger a página
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]

        # Atualizar dados no banco
        cursor2 = cnx.cursor()
        cursor2.execute(
            "UPDATE login SET username = %s, role = %s WHERE id = %s", 
            (username, role, id)
        )
        cnx.commit()
        cursor2.close()

        cursor.close()
        cnx.close()
        return redirect("/")

    # Se GET, buscar dados do utilizador para preencher o formulário
    cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (id,))
    usuarios = cursor.fetchone()

    cursor.close()
    cnx.close()

    return render_template("admin/editar_users.html", usuarios=usuarios)


@app.route("/trocar_password/<int:id>", methods=["GET", "POST"])
def trocar_password(id):
    # Proteger a página
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        cursor.execute(
            """
            UPDATE users 
            SET username = %s, password = %s, role = %s 
            WHERE id = %s
            """,
            (username, password, role, id)
        )

        cnx.commit()
        cursor.close()
        cnx.close()

        return redirect("/")

    # GET - buscar dados do utilizador
    cursor.execute(
        "SELECT id, username, role FROM users WHERE id = %s",
        (id,)
    )
    usuarios = cursor.fetchone()

    cursor.close()
    cnx.close()

    return render_template("users/trocar_password.html", usuarios=usuarios )




# ---------------------------------------------------
# Editar dados do cliente
# ---------------------------------------------------

@app.route("/editar_cliente/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    # Proteger a página
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        morada = request.form["morada"]

        # Atualizar dados no banco
        cursor2 = cnx.cursor()
        cursor2.execute(
            "UPDATE clientes SET nome = %s, email = %s, telefone = %s, morada = %s WHERE id = %s", 
            (nome, email, telefone, morada, id)
        )
        cnx.commit()
        cursor2.close()

        cursor.close()
        cnx.close()
        return redirect("/")

    # Se GET, buscar dados do utilizador para preencher o formulário
    cursor.execute("SELECT id, nome, email, telefone, morada FROM clientes WHERE id = %s", (id,))
    cliente = cursor.fetchone()

    cursor.close()
    cnx.close()

    return render_template("admin/editar_clientes.html", titulo="Editar clientes", cliente=cliente)



# ---------------------------------------------------
# Editar dados do Animal
# ---------------------------------------------------

@app.route("/editar_animal/<int:id>", methods=["GET", "POST"])
def editar_animal(id):
    # Proteger a página
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    if request.method == "POST":
        nome = request.form["nome"]
        especie = request.form["especie"]
        raca = request.form["raca"]
        data_nascimento = request.form["data_nascimento"]

        # Atualizar dados no banco
        cursor2 = cnx.cursor()
        cursor2.execute(
            "UPDATE animais SET nome = %s, especie = %s, raca = %s, data_nascimento = %s WHERE id = %s", 
            (nome, especie, raca, data_nascimento, id)
        )
        cnx.commit()
        cursor2.close()

        cursor.close()
        cnx.close()
        return redirect("/")

    # Se GET, buscar dados do utilizador para preencher o formulário
    cursor.execute("SELECT id, nome, especie, raca, data_nascimento FROM animais WHERE id = %s", (id,))
    animal = cursor.fetchone()

    cursor.close()
    cnx.close()

    return render_template("staff/editar_animais.html", titulo="Editar animal", animal=animal)




# ---------------------------------------------------
# Editar dados da Consulta
# ---------------------------------------------------

@app.route("/editar_consulta/<int:id>", methods=["GET", "POST"])
def editar_consulta(id):
    # Proteger a página
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    if request.method == "POST":
        data_hora = request.form["data_hora"]
        motivo = request.form["motivo"]
        notas = request.form["notas"]

        # Atualizar dados no banco
        cursor2 = cnx.cursor()
        cursor2.execute(
            "UPDATE consultas SET data_hora = %s, motivo = %s, notas = %s WHERE id = %s", 
            (data_hora, motivo, notas, id)
        )
        cnx.commit()
        cursor2.close()

        cursor.close()
        cnx.close()
        return redirect("/")

    # Se GET, buscar dados do utilizador para preencher o formulário
    cursor.execute("SELECT id, data_hora, motivo, notas FROM consultas WHERE id = %s", (id,))
    consulta = cursor.fetchone()

    cursor.close()
    cnx.close()

    return render_template("staff/editar_consulta.html", titulo="Editar consulta", consulta=consulta)




# ---------------------------------------------------
# Acesso a tabela de Clientes
# ---------------------------------------------------

@app.route("/tabela_clientes")
def tabela_clientes():
    # Proteger a página: só permite acesso se o utilizador estiver logado
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Conectar à base de dados
    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    # Buscar todos os utilizadores
    cursor.execute("SELECT id, nome, email, telefone, morada, created_at FROM clientes ORDER BY id ASC")
    clientes = cursor.fetchall()

    # Fechar cursor e conexão
    cursor.close()
    cnx.close()

    # Renderizar o template com os utilizadores
    return render_template("staff/tabela_clientes.html", clientes=clientes)



# ---------------------------------------------------
# Acesso a tabela de Animais
# ---------------------------------------------------

@app.route("/tabela_animais")
def tabela_animais():
    # Proteger a página: só permite acesso se o utilizador estiver logado
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Conectar à base de dados
    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    # Buscar todos os utilizadores
    cursor.execute("SELECT id, nome, especie, raca, data_nascimento FROM animais ORDER BY id ASC")
    animais = cursor.fetchall()

    # Fechar cursor e conexão
    cursor.close()
    cnx.close()

    # Renderizar o template com os utilizadores
    return render_template("staff/tabela_animais.html", animais=animais)


# ---------------------------------------------------
# Acesso a tabela de Consultas
# ---------------------------------------------------

@app.route("/tabela_consultas")
def tabela_consultas():
    # Proteger a página: só permite acesso se o utilizador estiver logado
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Conectar à base de dados
    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    # Buscar todos os utilizadores
    cursor.execute("SELECT id, data_hora, motivo, notas, created_at FROM consultas ORDER BY id ASC")
    consultas = cursor.fetchall()

    # Fechar cursor e conexão
    cursor.close()
    cnx.close()

    # Renderizar o template com os utilizadores
    return render_template("staff/tabela_consultas.html", consultas=consultas)



# ---------------------------------------------------
# Inserir novo utilizador
# ---------------------------------------------------
@app.route("/registrar_novo_utilizador", methods=["GET", "POST"])
def registrar_novo_utilizador():
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if not username or not password or not role:
            flash("Preencha todos os campos!")
            return redirect(url_for("registrar_novo_utilizador"))

        # Conectar ao banco
        cnx = ligar_bd()
        cursor = cnx.cursor()

        # Verificar se o usuário já existe
        cursor.execute(
            "SELECT id FROM users WHERE username = %s", (username,)
        )
        existe = cursor.fetchone()

        if existe:
            flash("Este nome de usuário já está em uso!")
            cursor.close()
            cnx.close()
            return redirect(url_for("registrar_novo_utilizador"))

        # Inserir novo usuário
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, role)
        )
        cnx.commit()

        cursor.close()
        cnx.close()

        flash("Conta criada com sucesso!")
        return redirect(url_for("base"))

    return render_template("admin/registrar_novo_utilizador.html")


# ---------------------------------------------------
# Deleta dados do cliente
# ---------------------------------------------------
@app.route("/deleta_cliente/<int:id>", methods=["POST"])
def deleta_cliente(id):
    # Proteger a página
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor()

    # Apagar pelo ID
    cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
    cnx.commit()

    cursor.close()
    cnx.close()

    return redirect(url_for("tabela_clientes"))


# ---------------------------------------------------
# Deleta dados do Animal
# ---------------------------------------------------
@app.route("/deleta_animal/<int:id>", methods=["POST"])
def deleta_animal(id):
    # Proteger a página
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor()

    # Apagar pelo ID
    cursor.execute("DELETE FROM animais WHERE id = %s", (id,))
    cnx.commit()

    cursor.close()
    cnx.close()

    return redirect(url_for("tabela_animais"))



# ---------------------------------------------------
# Deleta consulta
# ---------------------------------------------------
@app.route("/deleta_consulta/<int:id>", methods=["POST"])
def deleta_consulta(id):

    if "user_id" not in session or session.get("user_role") != "admin":
        flash("Acesso não autorizado.")
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor()

    cursor.execute(
        "DELETE FROM consultas WHERE id = %s",
        (id,)
    )
    cnx.commit()

    cursor.close()
    cnx.close()

    flash("Consulta apagada com sucesso.")
    return redirect(url_for("tabela_consultas"))




# ---------------------------------------------------
# Consultar os dados do utilizador
# ---------------------------------------------------
@app.route("/meus_dados")
def meus_dados():
    if "user_id" not in session:
        return redirect(url_for("login")) 

    return render_template(
        "users/meus_dados.html",
        titulo="Meus dados do utilizador",
        username=session.get("username"),
        role=session.get("user_role"),
        user_id=session.get("user_id")  
    )





# ---------------------------------------------------
# Iniciar o servidor Flask
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
