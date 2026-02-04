# ---------------------------------------------------
# IMPORTS
# ---------------------------------------------------
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os

# ---------------------------------------------------
# INICIALIZAÇÃO DO FLASK
# ---------------------------------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)

# ---------------------------------------------------
# FUNÇÃO PARA CONEXÃO COM MYSQL
# ---------------------------------------------------
def ligar_bd():
    """
    Cria e retorna a conexão com o servidor MySQL
    """
    return mysql.connector.connect(
        host="62.28.39.135",
        user="efa0125",
        password="123.Abc",
        database="efa0125_06_Leonardo_clinica_veterinaria"
    )

# ---------------------------------------------------
# HELPER DE EXECUÇÃO SEGURA (TRY / EXCEPT)
# ---------------------------------------------------
def executar_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    cnx = None
    cursor = None
    try:
        cnx = ligar_bd()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()

        if commit:
            cnx.commit()

    except mysql.connector.Error as err:
        if cnx:
            cnx.rollback()
        print("ERRO BD:", err)
        raise err

    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

# ---------------------------------------------------
# CONTEXT PROCESSOR
# ---------------------------------------------------
@app.context_processor
def coleta_user_role():
    """
    Disponibiliza a role do usuário logado para todos os templates
    """
    return dict(user_role=session.get("user_role"))

# ---------------------------------------------------
# ROTA BASE
# ---------------------------------------------------
@app.route("/")
def base():
    """
    Página inicial: redireciona para login se não estiver logado
    """
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("base.html")

# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login de usuários
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            user = executar_query(
                "SELECT id, username, password, role FROM users WHERE username=%s",
                (username,),
                fetchone=True
            )
        except:
            flash("Erro ao acessar a base de dados.")
            return redirect(url_for("login"))

        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["user_role"] = user["role"]
            session["password"] = user["password"]
            return redirect(url_for("base"))

        flash("Username ou password incorretos.")
        return redirect(url_for("login"))

    return render_template("users/login.html")

# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
@app.route("/logout")
def logout():
    """
    Limpa sessão e redireciona para login
    """
    session.clear()
    return redirect(url_for("login"))

# ---------------------------------------------------
# HOME
# ---------------------------------------------------
@app.route("/home")
def home():
    if "user_id" not in session:
        flash("Faça login primeiro!")
        return redirect(url_for("login"))
    return render_template("global/home.html")

# ---------------------------------------------------
# MINHA ÁREA (CLIENTE)
# ---------------------------------------------------
@app.route("/minha_area")
def minha_area():
    """
    Mostra área do cliente
    """
    if "user_id" not in session:
        flash("Faça login primeiro!")
        return redirect(url_for("login"))

    try:
        user = executar_query(
            "SELECT * FROM users WHERE id=%s",
            (session["user_id"],),
            fetchone=True
        )

        cliente = executar_query(
            "SELECT * FROM clientes WHERE id=%s",
            (user["cliente_id"],),
            fetchone=True
        )

        animais = executar_query(
            "SELECT * FROM animais WHERE cliente_id=%s",
            (cliente["id"],),
            fetchall=True
        )

        consultas = executar_query("""
            SELECT c.*, a.nome AS animal_nome
            FROM consultas c
            JOIN animais a ON c.animal_id = a.id
            WHERE a.cliente_id=%s
        """, (cliente["id"],), fetchall=True)

    except:
        flash("Erro ao carregar dados.")
        return redirect(url_for("login"))

    return render_template(
        "cliente/minha_area.html",
        user=user,
        cliente=cliente,
        animais=animais,
        consultas=consultas
    )

# ---------------------------------------------------
# TABELAS
# ---------------------------------------------------
@app.route("/tabela_utilizadores")
def tabela_utilizadores():
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        utilizadores = executar_query(
            "SELECT id, username, role, created_at FROM users ORDER BY id ASC",
            fetchall=True
        )
    except:
        flash("Erro ao carregar utilizadores.")
        return redirect(url_for("base"))

    return render_template("admin/tabela_utilizadores.html", utilizadores=utilizadores)

# ---------------------------------------------------
# EDITAR UTILIZADOR
# ---------------------------------------------------
@app.route("/editar_utilizador/<int:id>", methods=["GET","POST"])
def editar_users(id):
    """
    Edita dados de um usuário
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            executar_query(
                "UPDATE users SET username=%s, role=%s WHERE id=%s",
                (request.form["username"], request.form["role"], id),
                commit=True
            )
        except:
            flash("Erro ao atualizar utilizador.")
            return redirect(url_for("tabela_utilizadores"))

        return redirect(url_for("tabela_utilizadores"))

    try:
        usuarios = executar_query(
            "SELECT id, username, role FROM users WHERE id=%s",
            (id,),
            fetchone=True
        )
    except:
        flash("Erro ao carregar utilizador.")
        return redirect(url_for("tabela_utilizadores"))

    return render_template("admin/editar_users.html", usuarios=usuarios)

# ---------------------------------------------------
# DELETAR UTILIZADOR
# ---------------------------------------------------
@app.route("/deleta_utilizador/<int:id>", methods=["POST"])
def deleta_utilizador(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        executar_query(
            "DELETE FROM users WHERE id=%s",
            (id,),
            commit=True
        )
    except:
        flash("Erro ao apagar utilizador.")
        return redirect(url_for("tabela_utilizadores"))

    flash("Utilizador apagado com sucesso.")
    return redirect(url_for("tabela_utilizadores"))

# ---------------------------------------------------
# INICIAR SERVIDOR
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
