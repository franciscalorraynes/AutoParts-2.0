from app.db import conectar

def cadastrar_usuario():
    print("\nCadastro de Novo Usuário")
    username = input("Usuário: ")
    senha = input("Senha: ")
    tipo = input("Tipo (ADM/FUNCIONARIO): ").upper()

    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usuarios (username, senha, tipo)
        VALUES (%s, %s, %s)
    """, (username, senha, tipo))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Usuário '{username}' cadastrado com sucesso!")

def login():
    print("\nLogin")
    username = input("Usuário: ")
    senha = input("Senha: ")

    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT tipo FROM usuarios WHERE username = %s AND senha = %s
    """, (username, senha))
    resultado = cur.fetchone()
    cur.close()
    conn.close()

    if resultado:
        return resultado[0]
    else:
        print("Usuário ou senha incorretos!")
        return None
