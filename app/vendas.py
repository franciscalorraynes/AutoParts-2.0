from db import conectar
def registrar_venda(id_peca, quantidade_vendida):
    conn = conectar()
    cur = conn.cursor()

    # Verifica se peça existe e está ativa
    cur.execute("SELECT quantidade FROM pecas WHERE id_peca = %s AND ativa = TRUE", (id_peca,))
    res = cur.fetchone()
    if not res:
        cur.close()
        conn.close()
        return False, "Peça não encontrada ou arquivada."
    
    estoque_atual = res[0]
    if estoque_atual < quantidade_vendida:
        cur.close()
        conn.close()
        return False, f"Estoque insuficiente. Estoque atual: {estoque_atual}"

    # Atualiza estoque
    nova_qtd = estoque_atual - quantidade_vendida
    cur.execute("UPDATE pecas SET quantidade = %s WHERE id_peca = %s", (nova_qtd, id_peca))

    # Registra movimentação de saída
    cur.execute("""
        INSERT INTO movimentacoes (id_peca, tipo, quantidade, data)
        VALUES (%s, 'SAÍDA', %s, NOW())
    """, (id_peca, quantidade_vendida))

    conn.commit()
    cur.close()
    conn.close()
    return True, "Venda registrada com sucesso."
