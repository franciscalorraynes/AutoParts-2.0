# estoque.py

from db import conectar

def cadastrar_peca():
    print("\nCadastro de Peça")
    id_peca = input("Digite o ID da peça: ")
    nome = input("Digite o nome da peça: ")
    descricao = input("Digite a descrição da peça: ")
    quantidade = int(input("Digite a quantidade em estoque: "))
    preco = float(input("Digite o preço da peça: "))

    conn = conectar()
    cur = conn.cursor()

    # Insere na tabela de peças
    cur.execute("""
        INSERT INTO pecas (id_peca, nome, descricao, quantidade, preco)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_peca, nome, descricao, quantidade, preco))

    # Registra a movimentação de entrada
    cur.execute("""
        INSERT INTO movimentacoes (id_peca, tipo, quantidade)
        VALUES (%s, 'ENTRADA', %s)
    """, (id_peca, quantidade))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Peça '{nome}' cadastrada com sucesso!")

def listar_pecas():
    print("\nLista de Peças")
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT id_peca, nome, quantidade, preco FROM pecas WHERE ativa = TRUE")
    pecas = cur.fetchall()

    if not pecas:
        print("Nenhuma peça cadastrada.")
    else:
        for peca in pecas:
            print(f"ID: {peca[0]} | Nome: {peca[1]} | Qtd: {peca[2]} | Preço: R$ {peca[3]:.2f}")

    cur.close()
    conn.close()

def consultar_peca():
    print("\nConsulta de Peça")
    id_peca = input("Digite o ID da peça: ")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_peca, nome, descricao, quantidade, preco
        FROM pecas WHERE id_peca = %s
    """, (id_peca,))
    peca = cur.fetchone()

    if peca:
        print(f"ID: {peca[0]}")
        print(f"Nome: {peca[1]}")
        print(f"Descrição: {peca[2]}")
        print(f"Quantidade: {peca[3]}")
        print(f"Preço: R$ {peca[4]:.2f}")
    else:
        print(f"Peça com ID '{id_peca}' não encontrada.")

    cur.close()
    conn.close()

def atualizar_peca():
    print("\nAtualização de Peça")
    id_peca = input("Digite o ID da peça a ser atualizada: ")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT * FROM pecas WHERE id_peca = %s", (id_peca,))
    peca = cur.fetchone()

    if peca:
        novo_nome = input("Novo nome: ")
        nova_desc = input("Nova descrição: ")
        nova_qtd = int(input("Nova quantidade: "))
        novo_preco = float(input("Novo preço (R$): "))

        cur.execute("""
            UPDATE pecas
            SET nome = %s, descricao = %s, quantidade = %s, preco = %s
            WHERE id_peca = %s
        """, (novo_nome, nova_desc, nova_qtd, novo_preco, id_peca))

        # Registra movimentação (ajuste de estoque)
        diferenca_qtd = nova_qtd - peca[4]  # peca[4] = quantidade antiga
        tipo = 'ENTRADA' if diferenca_qtd > 0 else 'SAIDA'
        if diferenca_qtd != 0:
            cur.execute("""
                INSERT INTO movimentacoes (id_peca, tipo, quantidade)
                VALUES (%s, %s, %s)
            """, (id_peca, tipo, abs(diferenca_qtd)))

        conn.commit()
        print("Peça atualizada!")
    else:
        print(f"Peça com ID '{id_peca}' não encontrada.")

    cur.close()
    conn.close()

def remover_peca(user_type):
    if user_type != "ADM":
        print("Permissão negada! Apenas ADM pode remover peças.")
        return

    print("\nRemover (Arquivar) Peça")
    id_peca = input("Digite o ID da peça a ser removida: ")

    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE pecas SET ativa = FALSE WHERE id_peca = %s", (id_peca,))
    if cur.rowcount > 0:
        conn.commit()
        print(f"Peça com ID '{id_peca}' arquivada com sucesso!")
    else:
        print(f"Peça com ID '{id_peca}' não encontrada.")
    cur.close()
    conn.close()