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

        cnx = ligar_bd()
        cursor = cnx.cursor(dictionary=True)

        # Busca usuário pelo username
        cursor.execute("SELECT id, username, password, role FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        cursor.close()
        cnx.close()

        # Valida senha
        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["user_role"] = user["role"]
            session["password"] = user["password"]
            return redirect(url_for("base"))
        else:
            flash("Username ou password incorretos.")
            return redirect(url_for("login"))

    # GET: mostra formulário
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
@app.route("/minha_area")
def minha_area():
    """
    Mostra área do cliente:
    - informações do usuário
    - informações do cliente
    - lista de animais
    - lista de consultas
    """
    user_id = session.get("user_id")
    if not user_id:
        flash("Faça login primeiro!")
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    # Busca info do usuário logado
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if not user:
        flash("Usuário não encontrado!")
        cursor.close()
        cnx.close()
        return redirect(url_for("login"))

    # Busca info do cliente associado
    cliente_id = user["cliente_id"]
    cursor.execute("SELECT * FROM clientes WHERE id=%s", (cliente_id,))
    cliente = cursor.fetchone()

    # Busca animais do cliente
    cursor.execute("SELECT * FROM animais WHERE cliente_id=%s", (cliente_id,))
    animais = cursor.fetchall()

    # Busca consultas do cliente
    cursor.execute("""
        SELECT c.*, a.nome AS animal_nome
        FROM consultas c
        JOIN animais a ON c.animal_id = a.id
        WHERE a.cliente_id=%s
    """, (cliente_id,))
    consultas = cursor.fetchall()

    cursor.close()
    cnx.close()

    # Renderiza template
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

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)
    
    cursor.execute("SELECT id, nome, email, telefone, morada, created_at FROM clientes ORDER BY id ASC")
    clientes = cursor.fetchall()

    cursor.close()
    cnx.close()

    return render_template("staff/tabela_clientes.html", clientes=clientes)

@app.route("/tabela_utilizadores")
def tabela_utilizadores():
    """
    Lista todos os usuários
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY id ASC")
    utilizadores = cursor.fetchall()

    cursor.close()
    cnx.close()

    return render_template("admin/tabela_utilizadores.html", utilizadores=utilizadores)

@app.route("/tabela_animais")
def tabela_animais():
    """
    Lista todos os animais
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute("SELECT id, nome, especie, raca, data_nascimento FROM animais ORDER BY id ASC")
    animais = cursor.fetchall()

    cursor.close()
    cnx.close()

    return render_template("staff/tabela_animais.html", animais=animais)

@app.route("/tabela_consultas")
def tabela_consultas():
    """
    Lista todas as consultas
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute("SELECT id, data_hora, motivo, notas, created_at FROM consultas ORDER BY id ASC")
    consultas = cursor.fetchall()

    cursor.close()
    cnx.close()

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

        cnx = ligar_bd()
        cursor = cnx.cursor(dictionary=True)

        # Verifica se cliente já existe
        cursor.execute("SELECT id FROM clientes WHERE email=%s", (email,))
        if cursor.fetchone():
            flash("Este cliente já está cadastrado!")
            cursor.close()
            cnx.close()
            return redirect(url_for("registrar_novo_cliente"))

        # Insere cliente
        cursor.execute("INSERT INTO clientes (nome, email, telefone, morada) VALUES (%s,%s,%s,%s)",
                        (nome, email, telefone, morada))
        cliente_id = cursor.lastrowid
        cnx.commit()

        # Cria usuário para o cliente
        cursor.execute("INSERT INTO users (username, password, role, cliente_id) VALUES (%s,%s,%s,%s)", 
                        (email, "123", "cliente", cliente_id))
        cnx.commit()

        cursor.close()
        cnx.close()

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

        cnx = ligar_bd()
        cursor = cnx.cursor()

        # Verifica se usuário já existe
        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            flash("Este nome de usuário já está em uso!")
            cursor.close()
            cnx.close()
            return redirect(url_for("registrar_novo_utilizador"))

        # Insere usuário
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s,%s,%s)",
                        (username, password, role))
        cnx.commit()
        cursor.close()
        cnx.close()

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
    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes WHERE id=%s", (cliente_id,))
    cliente = cursor.fetchone()
    if not cliente:
        flash("Cliente não encontrado!")
        return redirect(url_for("tabela_clientes"))

    if request.method == "POST":
        nome = request.form.get("nome")
        especie = request.form.get("especie")
        raca = request.form.get("raca")
        data_nascimento = request.form.get("data_nascimento")

        cursor.execute("INSERT INTO animais (cliente_id, nome, especie, raca, data_nascimento) VALUES (%s,%s,%s,%s,%s)",
                        (cliente_id, nome, especie, raca, data_nascimento))
        cnx.commit()
        cursor.close()
        cnx.close()
        flash("Animal registrado com sucesso!")
        return redirect(url_for("tabela_animais"))

    cursor.close()
    cnx.close()

    return render_template("cliente/novo_animal.html", cliente=cliente)

# ---------------------------------------------------
# NOVA CONSULTA
# ---------------------------------------------------
@app.route("/clientes/<int:cliente_id>/nova_consulta", methods=["GET","POST"])
def nova_consulta(cliente_id):
    """
    Permite registrar nova consulta para os animais do cliente
    """
    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute("SELECT * FROM animais WHERE cliente_id=%s", (cliente_id,))
    animais = cursor.fetchall()
    if not animais:
        flash("Cliente não possui animais cadastrados!")
        return redirect(url_for("tabela_clientes"))

    if request.method == "POST":
        animal_id = request.form.get("animal_id")
        data_hora = request.form.get("data_hora")
        motivo = request.form.get("motivo")

        cursor.execute("INSERT INTO consultas (animal_id, data_hora, motivo) VALUES (%s,%s,%s)",
                        (animal_id, data_hora, motivo))
        cnx.commit()
        cursor.close()
        cnx.close()
        flash("Consulta marcada com sucesso!")
        return redirect(url_for("tabela_consultas"))

    cursor.close()
    cnx.close()

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

    cnx = ligar_bd()
    cursor = cnx.cursor()

    cursor.execute("DELETE FROM clientes WHERE id=%s", (id,))

    cnx.commit()
    cursor.close()
    cnx.close()

    return redirect(url_for("tabela_clientes"))

@app.route("/deleta_utilizador/<int:id>", methods=["POST"])
def deleta_utilizador(id):
    """
    Deleta um usuário pelo ID
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor()

    cursor.execute("DELETE FROM users WHERE id=%s", (id,))

    cnx.commit()
    cursor.close()
    cnx.close()
    
    return redirect(url_for("tabela_utilizadores"))

@app.route("/deleta_animal/<int:id>", methods=["POST"])
def deleta_animal(id):
    """
    Deleta um animal pelo ID
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor()

    cursor.execute("DELETE FROM animais WHERE id=%s", (id,))
    
    cnx.commit()
    cursor.close()
    cnx.close()
    return redirect(url_for("tabela_animais"))

@app.route("/deleta_consulta/<int:id>", methods=["POST"])
def deleta_consulta(id):
    """
    Deleta uma consulta pelo ID (somente admin)
    """
    if "user_id" not in session or session.get("user_role") != "admin":
        flash("Acesso não autorizado.")
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor()

    cursor.execute("DELETE FROM consultas WHERE id=%s", (id,))
    
    cnx.commit()
    cursor.close()
    cnx.close()
    flash("Consulta apagada com sucesso.")
    return redirect(url_for("tabela_consultas"))

# ---------------------------------------------------
# EDITAR DADOS (USUÁRIO, CLIENTE, ANIMAL, CONSULTA)
# ---------------------------------------------------
@app.route("/editar_users<int:id>", methods=["GET","POST"])
def editar_users(id):
    """
    Edita dados de um usuário
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]
        
        cursor.execute("UPDATE login SET username=%s, role=%s WHERE id=%s", (username, role, id))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return redirect("/")

    cursor.execute("SELECT id, username, role FROM users WHERE id=%s", (id,))
    usuarios = cursor.fetchone()
    
    cursor.close()
    cnx.close()

    return render_template("admin/editar_users.html", usuarios=usuarios)

@app.route("/editar_cliente/<int:id>", methods=["GET","POST"])
def editar_cliente(id):
    """
    Edita dados do cliente
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        morada = request.form["morada"]

        cursor.execute("UPDATE clientes SET nome=%s,email=%s,telefone=%s,morada=%s WHERE id=%s",
                        (nome,email,telefone,morada,id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return redirect("/")

    cursor.execute("SELECT id,nome,email,telefone,morada FROM clientes WHERE id=%s", (id,))
    cliente = cursor.fetchone()
    
    cursor.close()
    cnx.close()

    return render_template("admin/editar_clientes.html", cliente=cliente)

@app.route("/editar_animal/<int:id>", methods=["GET","POST"])
def editar_animal(id):
    """
    Edita dados de um animal
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    if request.method == "POST":
        nome = request.form["nome"]
        especie = request.form["especie"]
        raca = request.form["raca"]
        data_nascimento = request.form["data_nascimento"]

        cursor.execute("UPDATE animais SET nome=%s,especie=%s,raca=%s,data_nascimento=%s WHERE id=%s",
                        (nome,especie,raca,data_nascimento,id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return redirect("/tabela_animais")

    cursor.execute("SELECT id,nome,especie,raca,data_nascimento FROM animais WHERE id=%s", (id,))
    animal = cursor.fetchone()

    cursor.close()
    cnx.close()

    return render_template("staff/editar_animais.html", animal=animal)

@app.route("/editar_consulta/<int:id>", methods=["GET","POST"])
def editar_consulta(id):
    """
    Edita dados de uma consulta
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    if request.method == "POST":
        data_hora = request.form["data_hora"]
        motivo = request.form["motivo"]
        notas = request.form["notas"]

        cursor.execute("UPDATE consultas SET data_hora=%s,motivo=%s,notas=%s WHERE id=%s",
                        (data_hora,motivo,notas,id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return redirect("/tabela_consultas")

    cursor.execute("SELECT id,data_hora,motivo,notas FROM consultas WHERE id=%s", (id,))
    
    consulta = cursor.fetchone()
    cursor.close()
    cnx.close()

    return render_template("staff/editar_consulta.html", consulta=consulta)

@app.route("/trocar_password/<int:id>", methods=["GET","POST"])
def trocar_password(id):
    """
    Permite trocar senha do usuário
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cnx = ligar_bd()
    cursor = cnx.cursor(dictionary=True)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        cursor.execute("UPDATE users SET username=%s,password=%s,role=%s WHERE id=%s",
                        (username,password,role,id))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return redirect("/")

    cursor.execute("SELECT id,username,role FROM users WHERE id=%s", (id,))
    usuarios = cursor.fetchone()
    cursor.close()
    cnx.close()

    return render_template("users/trocar_password.html", usuarios=usuarios)

# ---------------------------------------------------
# INICIAR O SERVIDOR
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
