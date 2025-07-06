import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import psycopg2

from app.db import conectar  
from PIL import Image, ImageTk
import os


# ------------------------- Estilização ---------------------------------- #

PRIMARY_COLOR = "#0d6efd"  # azul
DARK_PRIMARY = "#084298"   # azul escuro
BG_COLOR = "#f7f7f7"       # fundo geral
FONT_FAMILY = "Helvetica"


def center_window(win: tk.Toplevel | tk.Tk, w: int = 420, h: int = 520):
    """Centraliza a janela na tela do usuário."""
    win.update_idletasks()
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")


def configurar_estilo() -> ttk.Style:
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, font=(FONT_FAMILY, 11))
    style.configure("Header.TLabel", font=(FONT_FAMILY, 16, "bold"), background=BG_COLOR)

    style.configure(
        "TButton",
        font=(FONT_FAMILY, 10, "bold"),
        foreground="white",
        background=PRIMARY_COLOR,
        padding=6,
        borderwidth=0,
    )
    style.map("TButton",
              background=[("pressed", DARK_PRIMARY), ("active", DARK_PRIMARY)])

    style.configure("TEntry", padding=4)

    # Treeview
    style.configure(
        "Custom.Treeview",
        font=(FONT_FAMILY, 10),
        rowheight=26,
        background="white",
        fieldbackground="white",
    )
    style.configure(
        "Custom.Treeview.Heading",
        font=(FONT_FAMILY, 10, "bold"),
        background=PRIMARY_COLOR,
        foreground="white",
    )
    style.map("Custom.Treeview.Heading",
              background=[("active", DARK_PRIMARY)])

    return style


# ----------------------- Funções de Negócio ----------------------------- #


def validar_login(username: str, senha: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "SELECT tipo FROM usuarios WHERE username = %s AND senha = %s",
        (username, senha),
    )
    res = cur.fetchone()
    cur.close(); conn.close()
    return res[0] if res else None


def RegistrarVenda(id_peca: str, quantidade_vendida: int):
    conn = conectar()
    cur = conn.cursor()

    # 1) Verifica estoque ativo
    cur.execute(
        "SELECT quantidade FROM pecas WHERE id_peca = %s AND ativa = TRUE",
        (id_peca,),
    )
    row = cur.fetchone()
    if not row:
        raise ValueError("Peça não encontrada ou inativa.")

    estoque_atual = row[0]
    if estoque_atual < quantidade_vendida:
        raise ValueError("Quantidade insuficiente no estoque.")

    # 2) Atualiza estoque
    nova_quantidade = estoque_atual - quantidade_vendida
    cur.execute(
        "UPDATE pecas SET quantidade = %s WHERE id_peca = %s",
        (nova_quantidade, id_peca),
    )

    # 3) Registra movimentação
    cur.execute(
        """
        INSERT INTO movimentacoes (id_peca, tipo, quantidade, data)
        VALUES (%s, 'SAÍDA', %s, NOW())
        """,
        (id_peca, quantidade_vendida),
    )

    conn.commit(); cur.close(); conn.close()


# -------------------------- Classes de UI -------------------------------- #

class TelaLogin:
    def __init__(self, root, on_login_sucesso):
        self.root = root
        self.on_login_sucesso = on_login_sucesso

        self.frame = ttk.Frame(root, padding=30)
        self.frame.pack(expand=True)

        ttk.Label(self.frame, text="Login", style="Header.TLabel").grid(columnspan=2, pady=(0, 20))
        ttk.Label(self.frame, text="Usuário:").grid(row=1, column=0, sticky="e", pady=6, padx=5)
        ttk.Label(self.frame, text="Senha:").grid(row=2, column=0, sticky="e", pady=6, padx=5)

        self.entry_user = ttk.Entry(self.frame, width=28)
        self.entry_senha = ttk.Entry(self.frame, show="*", width=28)
        self.entry_user.grid(row=1, column=1, pady=6, padx=5)
        self.entry_senha.grid(row=2, column=1, pady=6, padx=5)

        ttk.Button(self.frame, text="Entrar", command=self._login).grid(
            row=3, columnspan=2, pady=(20, 0)
        )

        
        self.entry_senha.bind("<Return>", lambda _: self._login())
        center_window(root, 360, 300)

    def _login(self):
        username, senha = self.entry_user.get(), self.entry_senha.get()
        tipo = validar_login(username, senha)
        if tipo:
            self.frame.destroy()
            self.on_login_sucesso(tipo)
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")


class TelaPrincipal:
    def __init__(self, root, user_type):
        self.root = root
        self.user_type = user_type

        self.frame = ttk.Frame(root, padding=15)
        self.frame.pack(fill="both", expand=True)

        # # Cabeçalho
        # ttk.Label(self.frame, text="AutoParts Inventory", style="Header.TLabel").pack(pady=(0, 10))
        # ttk.Label(self.frame, text=f"Logado como: {user_type}").pack(pady=(0, 15))
        # # # Adicionar logo
        # img_path = os.path.join(os.path.dirname(__file__), "logo_autoparts.png")
        # if os.path.exists(img_path):
        #     img = Image.open(img_path).resize((80, 80))  # ajuste o tamanho conforme necessário
        #     self.logo = ImageTk.PhotoImage(img)
        #     tk.Label(self.frame, image=self.logo, bg=BG_COLOR).pack(pady=(0, 10))

        # # Adicionar logo (acima do cabeçalho)
        # img_path = os.path.join(os.path.dirname(__file__), "logo_autoparts.png")
        # if os.path.exists(img_path):
        #     img = Image.open(img_path)
        #     img.thumbnail((120, 120), Image.LANCZOS)   # mantém proporção, tamanho regulável
        #     self.logo = ImageTk.PhotoImage(img)
        #     ttk.Label(self.frame, image=self.logo, background=BG_COLOR).pack(pady=(0, 12))

        # # Cabeçalho
        # ttk.Label(self.frame, text="AutoParts Inventory", style="Header.TLabel").pack(pady=(0, 6))
        # ttk.Label(self.frame, text=f"Logado como: {user_type}").pack(pady=(0, 15))
    # Cabeçalho com logo
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(pady=(0, 20))

        # Logo
        img_path = os.path.join(os.path.dirname(__file__), "logo_autoparts.png")
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img.thumbnail((100, 100))  # mantém proporção e tamanho adequado
            self.logo = ImageTk.PhotoImage(img)
            ttk.Label(header_frame, image=self.logo, background=BG_COLOR).pack()

        # Título e subtítulo
        ttk.Label(header_frame, text="AutoParts Inventory", style="Header.TLabel").pack(pady=(10, 0))
        ttk.Label(header_frame, text=f"Logado como: {user_type}").pack()



        # Botões principais
        buttons = [
            ("Cadastrar Peça", self._abrir_cadastro),
            ("Listar Peças", self._abrir_listagem),
            ("Registrar Venda", self._abrir_venda),
            ("Relatório", self._abrir_relatorio),
            ("Sair", self.root.destroy),
        ]
        if user_type == "ADM":
            buttons.insert(3, ("Cadastrar Usuário (ADM)", self._abrir_cadastro_usuario))
            buttons.insert(3, ("Remover Peça (ADM)", self._abrir_remocao))

        # for text, cmd in buttons:
        #     ttk.Button(self.frame, text=text, width=30, command=cmd).pack(pady=4)
        for text, cmd in buttons:
            ttk.Button(self.frame, text=text, width=30, command=cmd).pack(pady=6)

          # Rodapé
        ttk.Label(self.frame, text="© 2025 AutoParts Inc.", font=(FONT_FAMILY, 8), foreground="#888").pack(pady=(20, 0))

        center_window(root)

    # Aberturas ------------------------------------
    def _abrir_cadastro(self):
        CadastroPeca(self.root)

    def _abrir_listagem(self):
        ListarPecas(self.root)

    def _abrir_remocao(self):
        RemoverPeca(self.root)

    def _abrir_cadastro_usuario(self):
        CadastroUsuario(self.root)

    def _abrir_venda(self):
        TelaVendas(self.root)

    def _abrir_relatorio(self):
        TelaRelatorio(self.root)


class TelaRelatorio:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Relatório de Estoque")
        self.top.configure(background=BG_COLOR)
        center_window(self.top, 720, 560)

        # Text widget para mostrar resultados
        self.text = tk.Text(self.top, width=88, height=26, font=(FONT_FAMILY, 10))
        self.text.pack(padx=10, pady=10, fill="both", expand=True)

        # Frame de botões
        frame_btns = ttk.Frame(self.top)
        frame_btns.pack(pady=6)

        ttk.Button(frame_btns, text="Resumo", command=self._mostrar_resumo).pack(side="left", padx=4)
        ttk.Button(frame_btns, text="Histórico COMPLETO", command=self._mostrar_completo).pack(side="left", padx=4)
        ttk.Button(frame_btns, text="Peças ATIVAS", command=self._mostrar_ativas).pack(side="left", padx=4)
        ttk.Button(self.top, text="Exportar para Excel", command=self._exportar_excel).pack(pady=(4, 10))

        self.movimentacoes: list[tuple] = []
        self._mostrar_resumo()

    # --- funções internas ---
    def _mostrar_resumo(self):
        self.text.delete("1.0", tk.END)
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*), COALESCE(SUM(quantidade * preco), 0) FROM pecas WHERE ativa = TRUE")
        total_tipos, valor_total = cur.fetchone()
        cur.close(); conn.close()
        self.text.insert(tk.END, f"Total de tipos de peças: {total_tipos}\n")
        self.text.insert(tk.END, f"Valor total em estoque: R$ {valor_total:.2f}\n\n")

    def _mostrar_completo(self):
        self._consultar_movimentacoes("""
            SELECT id_peca, tipo, quantidade, data
            FROM movimentacoes
            ORDER BY data DESC
            LIMIT 40
        """)

    def _mostrar_ativas(self):
        self._consultar_movimentacoes("""
            SELECT m.id_peca, m.tipo, m.quantidade, m.data
            FROM movimentacoes m
            JOIN pecas p ON m.id_peca = p.id_peca
            WHERE p.ativa = TRUE
            ORDER BY m.data DESC
            LIMIT 40
        """)

    def _consultar_movimentacoes(self, sql: str):
        conn = conectar(); cur = conn.cursor()
        cur.execute(sql)
        self.movimentacoes = cur.fetchall()
        cur.close(); conn.close()

        self.text.delete("1.0", tk.END)
        cabecalho = "Histórico de Movimentações:\n\n"
        self.text.insert(tk.END, cabecalho)
        for row in self.movimentacoes:
            data_fmt = row[3].strftime("%d/%m/%Y %H:%M:%S") if isinstance(row[3], datetime) else str(row[3])
            self.text.insert(tk.END, f"Peça {row[0]} | Tipo: {row[1]} | Qtd: {row[2]} | Data: {data_fmt}\n")

    def _exportar_excel(self):
        if not self.movimentacoes:
            return messagebox.showwarning("Aviso", "Nenhum histórico carregado!")
        try:
            df = pd.DataFrame(self.movimentacoes, columns=["ID Peça", "Tipo", "Quantidade", "Data"])
            df.to_excel("relatorio_autoparts.xlsx", index=False)
            messagebox.showinfo("Sucesso", "Arquivo 'relatorio_autoparts.xlsx' criado na pasta do programa.")
        except Exception as exc:
            messagebox.showerror("Erro", f"Erro ao exportar: {exc}")


class TelaVendas:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Registrar Venda")
        self.top.configure(background=BG_COLOR)
        center_window(self.top, 360, 220)

        ttk.Label(self.top, text="ID da Peça:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self.top, text="Quantidade:").grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.entry_id = ttk.Entry(self.top, width=28)
        self.entry_qtd = ttk.Entry(self.top, width=28)
        self.entry_id.grid(row=0, column=1, padx=5, pady=5)
        self.entry_qtd.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.top, text="Registrar", command=self._registrar).grid(
            row=2, columnspan=2, pady=15
        )

    def _registrar(self):
        id_peca = self.entry_id.get().strip()
        try:
            qtd = int(self.entry_qtd.get())
        except ValueError:
            return messagebox.showerror("Erro", "Quantidade deve ser inteiro.")

        try:
            RegistrarVenda(id_peca, qtd)
            messagebox.showinfo("Sucesso", "Venda registrada!")
            self.top.destroy()
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))


class CadastroPeca:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Cadastrar Peça")
        self.top.configure(background=BG_COLOR)
        center_window(self.top, 400, 330)

        labels = ["ID da Peça:", "Nome:", "Descrição:", "Quantidade:", "Preço (R$):"]
        self.entries = []
        for i, txt in enumerate(labels):
            ttk.Label(self.top, text=txt).grid(row=i, column=0, sticky="e", padx=5, pady=4)
            ent = ttk.Entry(self.top, width=30)
            ent.grid(row=i, column=1, padx=5, pady=4)
            self.entries.append(ent)

        ttk.Button(self.top, text="Salvar", command=self._salvar).grid(row=5, columnspan=2, pady=12)

    def _salvar(self):
        id_peca, nome, desc, qtd_txt, preco_txt = [e.get().strip() for e in self.entries]
        try:
            quantidade = int(qtd_txt); preco = float(preco_txt)
        except ValueError:
            return messagebox.showerror("Erro", "Quantidade deve ser inteiro e preço decimal.")

        conn = conectar(); cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO pecas (id_peca, nome, descricao, quantidade, preco, ativa)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                """,
                (id_peca, nome, desc, quantidade, preco),
            )
            cur.execute(
                "INSERT INTO movimentacoes (id_peca, tipo, quantidade, data) VALUES (%s, 'ENTRADA', %s, NOW())",
                (id_peca, quantidade),
            )
            conn.commit(); messagebox.showinfo("Sucesso", "Peça cadastrada!")
            self.top.destroy()
        except psycopg2.IntegrityError:
            conn.rollback(); messagebox.showerror("Erro", "ID da peça já existe.")
        finally:
            cur.close(); conn.close()


class ListarPecas:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Lista de Peças Ativas")
        self.top.configure(background=BG_COLOR)
        center_window(self.top, 680, 420)

        cols = ("ID", "Nome", "Descrição", "Qtd", "Preço")
        self.tree = ttk.Treeview(
            self.top,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
        )
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Row stripes
        self.tree.tag_configure("odd", background="#fafafa")
        self.tree.tag_configure("even", background="#ececec")

        self._carregar()

    def _carregar(self):
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT id_peca, nome, descricao, quantidade, preco FROM pecas WHERE ativa = TRUE")
        for i, row in enumerate(cur.fetchall()):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", tk.END, values=row, tags=(tag,))
        cur.close(); conn.close()


class RemoverPeca:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Remover Peça (Arquivar)")
        self.top.configure(background=BG_COLOR)
        center_window(self.top, 360, 180)

        ttk.Label(self.top, text="ID da peça para remover:").pack(pady=12)
        self.entry_id = ttk.Entry(self.top, width=28); self.entry_id.pack(pady=4)
        ttk.Button(self.top, text="Remover", command=self._remover).pack(pady=14)

    def _remover(self):
        id_peca = self.entry_id.get().strip()
        conn = conectar(); cur = conn.cursor()
        cur.execute("UPDATE pecas SET ativa = FALSE WHERE id_peca = %s", (id_peca,))
        if cur.rowcount:
            cur.execute("INSERT INTO movimentacoes (id_peca, tipo, quantidade, data) VALUES (%s, 'SAÍDA', 0, NOW())", (id_peca,))
            conn.commit(); messagebox.showinfo("Sucesso", "Peça arquivada!")
            self.top.destroy()
        else:
            messagebox.showerror("Erro", "Peça não encontrada.")
        cur.close(); conn.close()


class CadastroUsuario:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Cadastrar Usuário")
        self.top.configure(background=BG_COLOR)
        center_window(self.top, 360, 260)

        labels = ["Usuário:", "Senha:", "Tipo:"]
        for i, txt in enumerate(labels):
            ttk.Label(self.top, text=txt).grid(row=i, column=0, sticky="e", padx=5, pady=5)

        self.ent_user = ttk.Entry(self.top, width=28)
        self.ent_senha = ttk.Entry(self.top, show="*", width=28)
        self.cmb_tipo = ttk.Combobox(self.top, values=["ADM", "FUNCIONARIO"], state="readonly", width=26)
        self.cmb_tipo.current(1)
        self.ent_user.grid(row=0, column=1, padx=5, pady=5)
        self.ent_senha.grid(row=1, column=1, padx=5, pady=5)
        self.cmb_tipo.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self.top, text="Salvar", command=self._salvar).grid(row=3, columnspan=2, pady=12)

    def _salvar(self):
        user, senha, tipo = self.ent_user.get().strip(), self.ent_senha.get().strip(), self.cmb_tipo.get()
        if not user or not senha:
            return messagebox.showerror("Erro", "Usuário e senha são obrigatórios.")

        conn = conectar(); cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO usuarios (username, senha, tipo) VALUES (%s, %s, %s)", (user, senha, tipo)
            )
            conn.commit(); messagebox.showinfo("Sucesso", "Usuário criado.")
            self.top.destroy()
        except psycopg2.IntegrityError:
            conn.rollback(); messagebox.showerror("Erro", "Usuário já existe.")
        finally:
            cur.close(); conn.close()


# ----------------------------- Main -------------------------------------- #

def main():
    root = tk.Tk(); root.title("AutoParts Inventory System")
    root.configure(background=BG_COLOR)
    configurar_estilo()

    def abrir_principal(tipo_usuario):
        TelaPrincipal(root, tipo_usuario)

    TelaLogin(root, abrir_principal)
    root.iconphoto(False, tk.PhotoImage(file="logo_autoparts.png"))
    root.mainloop()


if __name__ == "__main__":
    main()
