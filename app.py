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
app.secret_key = os.urandom(24)  # Chave secreta para sessões

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
    - GET: mostra formulário
    - POST: valida usuário e cria sessão
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
        else:
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
# MINHA ÁREA (CLIENTE)
# ---------------------------------------------------
@app.route("/home")
def home():
    """
    Página inicial do cliente
    """
    if "user_id" not in session:
        flash("Faça login primeiro!")
        return redirect(url_for("login"))
    return render_template("global/home.html")

# ---------------------------------------------------
@app.route("/minha_area")
def minha_area():
    """
    Mostra área do cliente:
    - informações do usuário
    - informações do cliente
    - lista de animais
    - lista de consultas
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
        if not user:
            flash("Usuário não encontrado!")
            return redirect(url_for("login"))

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
# MEUS DADOS (UTILIZADOR)
# ---------------------------------------------------
@app.route("/meus_dados")
def meus_dados():
    """
    Mostra dados do usuário logado
    """
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
# TABELAS
# ---------------------------------------------------
@app.route("/tabela_clientes")
def tabela_clientes():
    """
    Lista todos os clientes
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        clientes = executar_query(
            "SELECT id, nome, email, telefone, morada, created_at FROM clientes ORDER BY id ASC",
            fetchall=True
        )
    except:
        flash("Erro ao carregar clientes.")
        return redirect(url_for("base"))

    return render_template("staff/tabela_clientes.html", clientes=clientes)

@app.route("/tabela_utilizadores")
def tabela_utilizadores():
    """
    Lista todos os usuários
    """
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

@app.route("/tabela_animais")
def tabela_animais():
    """
    Lista todos os animais
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        animais = executar_query(
            "SELECT id, nome, especie, raca, data_nascimento FROM animais ORDER BY id ASC",
            fetchall=True
        )
    except:
        flash("Erro ao carregar animais.")
        return redirect(url_for("base"))

    return render_template("staff/tabela_animais.html", animais=animais)

@app.route("/tabela_consultas")
def tabela_consultas():
    """
    Lista todas as consultas
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        consultas = executar_query(
            "SELECT id, data_hora, motivo, notas, created_at FROM consultas ORDER BY id ASC",
            fetchall=True
        )
    except:
        flash("Erro ao carregar consultas.")
        return redirect(url_for("base"))

    return render_template("staff/tabela_consultas.html", consultas=consultas)

# ---------------------------------------------------
# REGISTRAR NOVO CLIENTE
# ---------------------------------------------------
@app.route("/registrar_novo_cliente", methods=["GET", "POST"])
def registrar_novo_cliente():
    """
    Registra novo cliente e cria usuário automaticamente
    """
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        morada = request.form.get("morada")

        if not nome or not email or not telefone or not morada:
            flash("Preencha todos os campos!")
            return redirect(url_for("registrar_novo_cliente"))

        try:
            existe = executar_query(
                "SELECT id FROM clientes WHERE email=%s",
                (email,),
                fetchone=True
            )
            if existe:
                flash("Este cliente já está cadastrado!")
                return redirect(url_for("registrar_novo_cliente"))

            executar_query(
                "INSERT INTO clientes (nome, email, telefone, morada) VALUES (%s,%s,%s,%s)",
                (nome,email,telefone,morada),
                commit=True
            )

            cliente = executar_query(
                "SELECT id FROM clientes WHERE email=%s",
                (email,),
                fetchone=True
            )

            executar_query(
                "INSERT INTO users (username, password, role, cliente_id) VALUES (%s,%s,%s,%s)", 
                (email, "123", "cliente", cliente["id"]),
                commit=True
            )

        except:
            flash("Erro ao registrar cliente.")
            return redirect(url_for("registrar_novo_cliente"))

        flash("Cliente e login criados com sucesso!")
        return redirect(url_for("tabela_clientes"))

    return render_template("staff/registrar_novo_cliente.html")

# ---------------------------------------------------
# REGISTRAR NOVO USUÁRIO
# ---------------------------------------------------
@app.route("/registrar_novo_utilizador", methods=["GET", "POST"])
def registrar_novo_utilizador():
    """
    Registra novo usuário (admin/staff)
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if not username or not password or not role:
            flash("Preencha todos os campos!")
            return redirect(url_for("registrar_novo_utilizador"))

        try:
            existe = executar_query(
                "SELECT id FROM users WHERE username=%s",
                (username,),
                fetchone=True
            )
            if existe:
                flash("Este nome de usuário já está em uso!")
                return redirect(url_for("registrar_novo_utilizador"))

            executar_query(
                "INSERT INTO users (username, password, role) VALUES (%s,%s,%s)",
                (username,password,role),
                commit=True
            )

        except:
            flash("Erro ao registrar utilizador.")
            return redirect(url_for("registrar_novo_utilizador"))

        flash("Conta criada com sucesso!")
        return redirect(url_for("base"))

    return render_template("admin/registrar_novo_utilizador.html")

# ---------------------------------------------------
# NOVO ANIMAL
# ---------------------------------------------------
@app.route("/clientes/<int:cliente_id>/novo_animal", methods=["GET","POST"])
def novo_animal(cliente_id):
    """
    Permite registrar um novo animal para o cliente
    """
    try:
        cliente = executar_query(
            "SELECT * FROM clientes WHERE id=%s",
            (cliente_id,),
            fetchone=True
        )
        if not cliente:
            flash("Cliente não encontrado!")
            return redirect(url_for("tabela_clientes"))

        if request.method == "POST":
            executar_query(
                "INSERT INTO animais (cliente_id, nome, especie, raca, data_nascimento) VALUES (%s,%s,%s,%s,%s)",
                (
                    cliente_id,
                    request.form.get("nome"),
                    request.form.get("especie"),
                    request.form.get("raca"),
                    request.form.get("data_nascimento")
                ),
                commit=True
            )
            flash("Animal registrado com sucesso!")
            return redirect(url_for("tabela_animais"))

    except:
        flash("Erro ao registrar animal.")
        return redirect(url_for("tabela_animais"))

    return render_template("cliente/novo_animal.html", cliente=cliente)

# ---------------------------------------------------
# NOVA CONSULTA
# ---------------------------------------------------
@app.route("/clientes/<int:cliente_id>/nova_consulta", methods=["GET","POST"])
def nova_consulta(cliente_id):
    """
    Permite registrar nova consulta para os animais do cliente
    """
    try:
        animais = executar_query(
            "SELECT * FROM animais WHERE cliente_id=%s",
            (cliente_id,),
            fetchall=True
        )
        if not animais:
            flash("Cliente não possui animais cadastrados!")
            return redirect(url_for("tabela_clientes"))

        if request.method == "POST":
            executar_query(
                "INSERT INTO consultas (animal_id, data_hora, motivo) VALUES (%s,%s,%s)",
                (
                    request.form.get("animal_id"),
                    request.form.get("data_hora"),
                    request.form.get("motivo")
                ),
                commit=True
            )
            flash("Consulta marcada com sucesso!")
            return redirect(url_for("tabela_consultas"))

    except:
        flash("Erro ao registrar consulta.")
        return redirect(url_for("tabela_consultas"))

    return render_template("cliente/nova_consulta.html", animais=animais)

# ---------------------------------------------------
# DELETAR REGISTROS
# ---------------------------------------------------
@app.route("/deleta_cliente/<int:id>", methods=["POST"])
def deleta_cliente(id):
    """
    Deleta um cliente pelo ID
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        executar_query(
            "DELETE FROM clientes WHERE id=%s",
            (id,),
            commit=True
        )
    except:
        flash("Erro ao apagar cliente.")
        return redirect(url_for("tabela_clientes"))

    return redirect(url_for("tabela_clientes"))

@app.route("/deleta_utilizador/<int:id>", methods=["POST"])
def deleta_utilizador(id):
    """
    Deleta um usuário pelo ID
    """
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

@app.route("/deleta_animal/<int:id>", methods=["POST"])
def deleta_animal(id):
    """
    Deleta um animal pelo ID
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        executar_query(
            "DELETE FROM animais WHERE id=%s",
            (id,),
            commit=True
        )
    except:
        flash("Erro ao apagar animal.")
        return redirect(url_for("tabela_animais"))

    return redirect(url_for("tabela_animais"))

@app.route("/deleta_consulta/<int:id>", methods=["POST"])
def deleta_consulta(id):
    """
    Deleta uma consulta pelo ID (somente admin)
    """
    if "user_id" not in session or session.get("user_role") != "admin":
        flash("Acesso não autorizado.")
        return redirect(url_for("login"))

    try:
        executar_query(
            "DELETE FROM consultas WHERE id=%s",
            (id,),
            commit=True
        )
        flash("Consulta apagada com sucesso.")
    except:
        flash("Erro ao apagar consulta.")
        return redirect(url_for("tabela_consultas"))

    return redirect(url_for("tabela_consultas"))

# ---------------------------------------------------
# EDITAR DADOS
# ---------------------------------------------------
@app.route("/editar_cliente/<int:id>", methods=["GET","POST"])
def editar_cliente(id):
    """
    Edita dados do cliente
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            executar_query(
                "UPDATE clientes SET nome=%s,email=%s,telefone=%s,morada=%s WHERE id=%s",
                (
                    request.form["nome"],
                    request.form["email"],
                    request.form["telefone"],
                    request.form["morada"],
                    id
                ),
                commit=True
            )
        except:
            flash("Erro ao atualizar cliente.")
            return redirect("/")

        return redirect("/")

    try:
        cliente = executar_query(
            "SELECT id,nome,email,telefone,morada FROM clientes WHERE id=%s",
            (id,),
            fetchone=True
        )
    except:
        flash("Erro ao carregar cliente.")
        return redirect("/")

    return render_template("admin/editar_clientes.html", cliente=cliente)

@app.route("/editar_animal/<int:id>", methods=["GET","POST"])
def editar_animal(id):
    """
    Edita dados de um animal
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            executar_query(
                "UPDATE animais SET nome=%s,especie=%s,raca=%s,data_nascimento=%s WHERE id=%s",
                (
                    request.form["nome"],
                    request.form["especie"],
                    request.form["raca"],
                    request.form["data_nascimento"],
                    id
                ),
                commit=True
            )
        except:
            flash("Erro ao atualizar animal.")
            return redirect("/tabela_animais")

        return redirect("/tabela_animais")

    try:
        animal = executar_query(
            "SELECT id,nome,especie,raca,data_nascimento FROM animais WHERE id=%s",
            (id,),
            fetchone=True
        )
    except:
        flash("Erro ao carregar animal.")
        return redirect("/tabela_animais")

    return render_template("staff/editar_animais.html", animal=animal)

@app.route("/editar_consulta/<int:id>", methods=["GET","POST"])
def editar_consulta(id):
    """
    Edita dados de uma consulta
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            executar_query(
                "UPDATE consultas SET data_hora=%s,motivo=%s,notas=%s WHERE id=%s",
                (
                    request.form["data_hora"],
                    request.form["motivo"],
                    request.form["notas"],
                    id
                ),
                commit=True
            )
        except:
            flash("Erro ao atualizar consulta.")
            return redirect("/tabela_consultas")

        return redirect("/tabela_consultas")

    try:
        consulta = executar_query(
            "SELECT id,data_hora,motivo,notas FROM consultas WHERE id=%s",
            (id,),
            fetchone=True
        )
    except:
        flash("Erro ao carregar consulta.")
        return redirect("/tabela_consultas")

    return render_template("staff/editar_consulta.html", consulta=consulta)

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
                (
                    request.form["username"],
                    request.form["role"],
                    id
                ),
                commit=True
            )
        except:
            flash("Erro ao atualizar usuário.")
            return redirect("/tabela_utilizadores")

        return redirect("/tabela_utilizadores")

    try:
        usuarios = executar_query(
            "SELECT id,username,role FROM users WHERE id=%s",
            (id,),
            fetchone=True
        )
    except:
        flash("Erro ao carregar usuário.")
        return redirect("/tabela_utilizadores")

    return render_template("admin/editar_users.html", usuarios=usuarios)

@app.route("/trocar_password/<int:id>", methods=["GET","POST"])
def trocar_password(id):
    """
    Permite trocar senha do usuário
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            executar_query(
                "UPDATE users SET username=%s,password=%s,role=%s WHERE id=%s",
                (
                    request.form["username"],
                    request.form["password"],
                    request.form["role"],
                    id
                ),
                commit=True
            )
        except:
            flash("Erro ao atualizar usuário.")
            return redirect("/")

        return redirect("/")

    try:
        usuarios = executar_query(
            "SELECT id,username,role FROM users WHERE id=%s",
            (id,),
            fetchone=True
        )
    except:
        flash("Erro ao carregar usuário.")
        return redirect("/")

    return render_template("users/trocar_password.html", usuarios=usuarios)

# ---------------------------------------------------
# INICIAR O SERVIDOR
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
