import tkinter as tk
from tkinter import messagebox
from app.db import conectar
import pandas as pd

class Relatorio:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Relatório de Estoque")

        self.text = tk.Text(self.top, width=80, height=25)
        self.text.pack()

        self.frame_opcoes = tk.Frame(self.top)
        self.frame_opcoes.pack(pady=5)

        self.btn_completo = tk.Button(self.frame_opcoes, text="Histórico COMPLETO", command=self.mostrar_completo)
        self.btn_completo.pack(side=tk.LEFT, padx=5)

        self.btn_ativas = tk.Button(self.frame_opcoes, text="Histórico Peças ATIVAS", command=self.mostrar_ativas)
        self.btn_ativas.pack(side=tk.LEFT, padx=5)

        self.btn_exportar = tk.Button(self.top, text="Exportar para Excel", command=self.exportar_excel)
        self.btn_exportar.pack(pady=10)

        self.movimentacoes = []  

        self.mostrar_resumo()

    def mostrar_resumo(self):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*), SUM(quantidade * preco)
            FROM pecas
            WHERE ativa = TRUE
        """)
        total_tipos, valor_total = cur.fetchone()
        self.text.insert(tk.END, f"Total de tipos de peças: {total_tipos}\n")
        self.text.insert(tk.END, f"Valor total em estoque: R$ {valor_total:.2f}\n\n")
        cur.close()
        conn.close()

    def mostrar_completo(self):
        self.text.insert(tk.END, "\nHistórico COMPLETO de Movimentações:\n")
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT id_peca, tipo, quantidade, data
            FROM movimentacoes
            ORDER BY data DESC
            LIMIT 20
        """)
        self.movimentacoes = cur.fetchall()
        for row in self.movimentacoes:
            self.text.insert(tk.END, f"Peça: {row[0]} | Tipo: {row[1]} | Qtd: {row[2]} | Data: {row[3].strftime('%d/%m/%Y %H:%M:%S')}\n")
        cur.close()
        conn.close()

    def mostrar_ativas(self):
        self.text.insert(tk.END, "\nHistórico de Movimentações de Peças ATIVAS:\n")
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id_peca, m.tipo, m.quantidade, m.data
            FROM movimentacoes m
            JOIN pecas p ON m.id_peca = p.id_peca
            WHERE p.ativa = TRUE
            ORDER BY m.data DESC
            LIMIT 20
        """)
        self.movimentacoes = cur.fetchall()
        for row in self.movimentacoes:
            self.text.insert(tk.END, f"Peça: {row[0]} | Tipo: {row[1]} | Qtd: {row[2]} | Data: {row[3].strftime('%d/%m/%Y %H:%M:%S')}\n")
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
