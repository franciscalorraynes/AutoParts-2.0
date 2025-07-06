import tkinter as tk
from tkinter import ttk, messagebox
from db import conectar
import psycopg2
import pandas as pd

# Configurações globais de estilo
def configurar_estilo():
    style = ttk.Style()
    style.theme_use("clam")  # Define um tema mais moderno
    style.configure("TFrame", background="#f7f7f7")
    style.configure("TLabel", background="#f7f7f7", font=("Helvetica", 11))
    style.configure("TButton", font=("Helvetica", 10), padding=5)
    style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), background="#f7f7f7")
    style.configure("TEntry", padding=3)
    return style

# --- Função para validar login ---
def validar_login(username, senha):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT tipo FROM usuarios WHERE username = %s AND senha = %s", (username, senha))
    res = cur.fetchone()
    cur.close()
    conn.close()
    if res:
        return res[0]  # tipo: 'ADM' ou 'FUNCIONARIO'
    else:
        return None

# --- Função para registrar venda ---
def RegistrarVenda(id_peca, quantidade_vendida):
    conn = conectar()
    cur = conn.cursor()

    # Verifica estoque
    cur.execute("SELECT quantidade FROM pecas WHERE id_peca = %s AND ativa = TRUE", (id_peca,))
    res = cur.fetchone()
    if not res:
        cur.close()
        conn.close()
        raise ValueError("Peça não encontrada ou inativa.")
    estoque_atual = res[0]
    if estoque_atual < quantidade_vendida:
        cur.close()
        conn.close()
        raise ValueError("Quantidade insuficiente no estoque.")

    # Atualiza estoque
    nova_quantidade = estoque_atual - quantidade_vendida
    cur.execute("UPDATE pecas SET quantidade = %s WHERE id_peca = %s", (nova_quantidade, id_peca))

    # Registra movimentação de saída (venda)
    cur.execute("""
        INSERT INTO movimentacoes (id_peca, tipo, quantidade, data)
        VALUES (%s, 'SAÍDA', %s, NOW())
    """, (id_peca, quantidade_vendida))

    conn.commit()
    cur.close()
    conn.close()

# --- Tela de Login ---
class TelaLogin:
    def __init__(self, root, on_login_sucesso):
        self.root = root
        self.on_login_sucesso = on_login_sucesso
        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(expand=True)

        ttk.Label(self.frame, text="Usuário:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
        ttk.Label(self.frame, text="Senha:").grid(row=1, column=0, sticky="e", pady=5, padx=5)

        self.entry_user = ttk.Entry(self.frame, width=30)
        self.entry_senha = ttk.Entry(self.frame, show="*", width=30)
        self.entry_user.grid(row=0, column=1, pady=5, padx=5)
        self.entry_senha.grid(row=1, column=1, pady=5, padx=5)

        btn_login = ttk.Button(self.frame, text="Login", command=self.fazer_login)
        btn_login.grid(row=2, column=0, columnspan=2, pady=15)

    def fazer_login(self):
        user = self.entry_user.get()
        senha = self.entry_senha.get()
        tipo = validar_login(user, senha)
        if tipo:
            self.frame.destroy()
            self.on_login_sucesso(tipo)
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")

# --- Tela Principal ---
class TelaPrincipal:
    def __init__(self, root, user_type):
        self.root = root
        self.user_type = user_type
        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(expand=True)

        ttk.Label(self.frame, text=f"Logado como: {user_type}", style="Header.TLabel").pack(pady=10)

        btn_cadastrar = ttk.Button(self.frame, text="Cadastrar Peça", width=30, command=self.abrir_cadastro)
        btn_listar = ttk.Button(self.frame, text="Listar Peças", width=30, command=self.abrir_listagem)
        btn_vender = ttk.Button(self.frame, text="Registrar Venda", width=30, command=self.abrir_venda)
        btn_relatorio = ttk.Button(self.frame, text="Relatório", width=30, command=self.abrir_relatorio)
        btn_sair = ttk.Button(self.frame, text="Sair", width=30, command=root.destroy)

        btn_cadastrar.pack(pady=5)
        btn_listar.pack(pady=5)
        btn_vender.pack(pady=5)
        btn_relatorio.pack(pady=5)
        btn_sair.pack(pady=5)

        if self.user_type == "ADM":
            btn_remover = ttk.Button(self.frame, text="Remover Peça (ADM)", width=30, command=self.abrir_remocao)
            btn_remover.pack(pady=5)

            btn_cadastrar_usuario = ttk.Button(self.frame, text="Cadastrar Usuário (ADM)", width=30, command=self.abrir_cadastro_usuario)
            btn_cadastrar_usuario.pack(pady=5)

    def abrir_cadastro(self):
        CadastroPeca(self.root)

    def abrir_listagem(self):
        ListarPecas(self.root)

    def abrir_remocao(self):
        RemoverPeca(self.root)

    def abrir_cadastro_usuario(self):
        CadastroUsuario(self.root)

    def abrir_venda(self):
        TelaVendas(self.root)

    def abrir_relatorio(self):
        TelaRelatorio(self.root)

# --- Tela de Relatório Completo com Exportação Excel ---
class TelaRelatorio:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Relatório de Estoque")
        self.top.configure(background="#f7f7f7")

        self.text = tk.Text(self.top, width=80, height=25, font=("Helvetica", 10))
        self.text.pack(padx=10, pady=10)

        self.frame_opcoes = ttk.Frame(self.top, padding=5)
        self.frame_opcoes.pack(pady=5)

        self.btn_completo = ttk.Button(self.frame_opcoes, text="Histórico COMPLETO", command=self.mostrar_completo)
        self.btn_completo.pack(side=tk.LEFT, padx=5)

        self.btn_ativas = ttk.Button(self.frame_opcoes, text="Histórico Peças ATIVAS", command=self.mostrar_ativas)
        self.btn_ativas.pack(side=tk.LEFT, padx=5)

        self.btn_exportar = ttk.Button(self.top, text="Exportar para Excel", command=self.exportar_excel)
        self.btn_exportar.pack(pady=10)

        self.movimentacoes = []  # Guarda o resultado da consulta

        self.mostrar_resumo()

    def mostrar_resumo(self):
        self.text.delete("1.0", tk.END)
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*), COALESCE(SUM(quantidade * preco), 0)
            FROM pecas
            WHERE ativa = TRUE
        """)
        total_tipos, valor_total = cur.fetchone()
        cur.close()
        conn.close()
        self.text.insert(tk.END, f"Total de tipos de peças: {total_tipos}\n")
        self.text.insert(tk.END, f"Valor total em estoque: R$ {valor_total:.2f}\n\n")

    def mostrar_completo(self):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, "Histórico COMPLETO de Movimentações:\n\n")
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT id_peca, tipo, quantidade, data
            FROM movimentacoes
            ORDER BY data DESC
            LIMIT 30
        """)
        self.movimentacoes = cur.fetchall()
        for row in self.movimentacoes:
            data_formatada = row[3].strftime('%d/%m/%Y %H:%M:%S') if row[3] else ""
            self.text.insert(tk.END, f"Peça: {row[0]} | Tipo: {row[1]} | Qtd: {row[2]} | Data: {data_formatada}\n")
        cur.close()
        conn.close()

    def mostrar_ativas(self):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, "Histórico de Movimentações de Peças ATIVAS:\n\n")
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id_peca, m.tipo, m.quantidade, m.data
            FROM movimentacoes m
            JOIN pecas p ON m.id_peca = p.id_peca
            WHERE p.ativa = TRUE
            ORDER BY m.data DESC
            LIMIT 30
        """)
        self.movimentacoes = cur.fetchall()
        for row in self.movimentacoes:
            data_formatada = row[3].strftime('%d/%m/%Y %H:%M:%S') if row[3] else ""
            self.text.insert(tk.END, f"Peça: {row[0]} | Tipo: {row[1]} | Qtd: {row[2]} | Data: {data_formatada}\n")
        cur.close()
        conn.close()

    def exportar_excel(self):
        if not self.movimentacoes:
            messagebox.showwarning("Aviso", "Nenhum histórico carregado! Clique primeiro em 'Histórico COMPLETO' ou 'Peças ATIVAS'.")
            return
        try:
            df = pd.DataFrame(self.movimentacoes, columns=["ID Peça", "Tipo", "Quantidade", "Data"])
            df["Data"] = df["Data"].dt.strftime('%d/%m/%Y %H:%M:%S')
            df.to_excel("relatorio_autoparts.xlsx", index=False)
            messagebox.showinfo("Sucesso", "Relatório exportado para 'relatorio_autoparts.xlsx' com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")

# --- Tela de Vendas ---
class TelaVendas:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Registrar Venda")
        self.top.configure(background="#f7f7f7")

        ttk.Label(self.top, text="ID da Peça:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self.top, text="Quantidade:").grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.entry_id = ttk.Entry(self.top, width=30)
        self.entry_qtd = ttk.Entry(self.top, width=30)
        self.entry_id.grid(row=0, column=1, padx=5, pady=5)
        self.entry_qtd.grid(row=1, column=1, padx=5, pady=5)

        btn_vender = ttk.Button(self.top, text="Registrar Venda", command=self.registrar_venda)
        btn_vender.grid(row=2, column=0, columnspan=2, pady=10)

    def registrar_venda(self):
        id_peca = self.entry_id.get()
        try:
            quantidade = int(self.entry_qtd.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro.")
            return

        try:
            RegistrarVenda(id_peca, quantidade)
            messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
            self.top.destroy()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

# --- Cadastro Peça ---
class CadastroPeca:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Cadastrar Peça")
        self.top.configure(background="#f7f7f7")

        ttk.Label(self.top, text="ID da Peça:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self.top, text="Nome:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self.top, text="Descrição:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self.top, text="Quantidade:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self.top, text="Preço (R$):").grid(row=4, column=0, sticky="e", padx=5, pady=5)

        self.entry_id = ttk.Entry(self.top, width=30)
        self.entry_nome = ttk.Entry(self.top, width=30)
        self.entry_desc = ttk.Entry(self.top, width=30)
        self.entry_qtd = ttk.Entry(self.top, width=30)
        self.entry_preco = ttk.Entry(self.top, width=30)

        self.entry_id.grid(row=0, column=1, padx=5, pady=5)
        self.entry_nome.grid(row=1, column=1, padx=5, pady=5)
        self.entry_desc.grid(row=2, column=1, padx=5, pady=5)
        self.entry_qtd.grid(row=3, column=1, padx=5, pady=5)
        self.entry_preco.grid(row=4, column=1, padx=5, pady=5)

        btn_salvar = ttk.Button(self.top, text="Salvar", command=self.salvar_peca)
        btn_salvar.grid(row=5, column=0, columnspan=2, pady=10)

    def salvar_peca(self):
        id_peca = self.entry_id.get()
        nome = self.entry_nome.get()
        descricao = self.entry_desc.get()
        try:
            quantidade = int(self.entry_qtd.get())
            preco = float(self.entry_preco.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser inteiro e preço deve ser número decimal.")
            return

        conn = conectar()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO pecas (id_peca, nome, descricao, quantidade, preco, ativa)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            """, (id_peca, nome, descricao, quantidade, preco))
            # Registra movimentação de entrada (cadastro)
            cur.execute("""
                INSERT INTO movimentacoes (id_peca, tipo, quantidade, data)
                VALUES (%s, 'ENTRADA', %s, NOW())
            """, (id_peca, quantidade))
            conn.commit()
            messagebox.showinfo("Sucesso", "Peça cadastrada com sucesso!")
            self.top.destroy()
        except psycopg2.IntegrityError:
            conn.rollback()
            messagebox.showerror("Erro", "ID da peça já existe.")
        finally:
            cur.close()
            conn.close()

# --- Listar Peças ---
class ListarPecas:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Lista de Peças")
        self.top.configure(background="#f7f7f7")

        self.tree = ttk.Treeview(self.top, columns=("ID", "Nome", "Descrição", "Qtd", "Preço"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Descrição", text="Descrição")
        self.tree.heading("Qtd", text="Quantidade")
        self.tree.heading("Preço", text="Preço (R$)")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.carregar_pecas()

    def carregar_pecas(self):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id_peca, nome, descricao, quantidade, preco FROM pecas WHERE ativa = TRUE")
        rows = cur.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        cur.close()
        conn.close()

# --- Remover Peça (Arquivar) ---
class RemoverPeca:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Remover Peça (Arquivar)")
        self.top.configure(background="#f7f7f7")

        ttk.Label(self.top, text="ID da peça para remover:").pack(pady=10, padx=5)
        self.entry_id = ttk.Entry(self.top, width=30)
        self.entry_id.pack(padx=5)

        btn_remover = ttk.Button(self.top, text="Remover", command=self.remover_peca)
        btn_remover.pack(pady=10)

    def remover_peca(self):
        id_peca = self.entry_id.get()
        conn = conectar()
        cur = conn.cursor()
        cur.execute("UPDATE pecas SET ativa = FALSE WHERE id_peca = %s", (id_peca,))
        if cur.rowcount > 0:
            # Registra movimentação de saída por remoção (arquivamento)
            cur.execute("""
                INSERT INTO movimentacoes (id_peca, tipo, quantidade, data)
                VALUES (%s, 'SAÍDA', 0, NOW())
            """, (id_peca,))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Peça '{id_peca}' arquivada com sucesso!")
            self.top.destroy()
        else:
            messagebox.showerror("Erro", "Peça não encontrada.")
        cur.close()
        conn.close()

# --- Cadastro Usuário (só ADM) ---
class CadastroUsuario:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Cadastrar Usuário")
        self.top.configure(background="#f7f7f7")

        ttk.Label(self.top, text="Usuário:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self.top, text="Senha:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self.top, text="Tipo:").grid(row=2, column=0, sticky="e", padx=5, pady=5)

        self.entry_user = ttk.Entry(self.top, width=30)
        self.entry_senha = ttk.Entry(self.top, show="*", width=30)
        self.combo_tipo = ttk.Combobox(self.top, values=["ADM", "FUNCIONARIO"], state="readonly", width=28)
        self.combo_tipo.current(1)  # default FUNCIONARIO selecionado

        self.entry_user.grid(row=0, column=1, padx=5, pady=5)
        self.entry_senha.grid(row=1, column=1, padx=5, pady=5)
        self.combo_tipo.grid(row=2, column=1, padx=5, pady=5)

        btn_salvar = ttk.Button(self.top, text="Salvar", command=self.salvar_usuario)
        btn_salvar.grid(row=3, column=0, columnspan=2, pady=10)

    def salvar_usuario(self):
        user = self.entry_user.get().strip()
        senha = self.entry_senha.get().strip()
        tipo = self.combo_tipo.get()

        if not user or not senha:
            messagebox.showerror("Erro", "Usuário e senha são obrigatórios")
            return

        conn = conectar()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO usuarios (username, senha, tipo)
                VALUES (%s, %s, %s)
            """, (user, senha, tipo))
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            self.top.destroy()
        except psycopg2.IntegrityError:
            conn.rollback()
            messagebox.showerror("Erro", "Usuário já existe.")
        finally:
            cur.close()
            conn.close()

# --- Função principal ---
def main():
    root = tk.Tk()
    root.title("AutoParts Inventory System")
    root.geometry("400x500")
    root.configure(background="#f7f7f7")
    configurar_estilo()

    def abrir_tela_principal(tipo_usuario):
        TelaPrincipal(root, tipo_usuario)

    TelaLogin(root, abrir_tela_principal)
    root.mainloop()

if __name__ == "__main__":
    main()


