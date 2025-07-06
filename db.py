# db.py
import psycopg2

def conectar():
    return psycopg2.connect(
        host="localhost",
        database="estoque",
        user="postgres",
        password="12345",
        port=5432
    )

def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pecas (
            id SERIAL PRIMARY KEY,
            id_peca VARCHAR(50) UNIQUE NOT NULL,
            nome VARCHAR(100),
            descricao TEXT,
            quantidade INTEGER,
            preco REAL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id SERIAL PRIMARY KEY,
            id_peca VARCHAR(50) REFERENCES pecas(id_peca),
            tipo VARCHAR(10),
            quantidade INTEGER,
            data TIMESTAMP DEFAULT NOW()
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            senha VARCHAR(100) NOT NULL,
            tipo VARCHAR(20)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()