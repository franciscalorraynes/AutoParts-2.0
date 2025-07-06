# utils.py

def exibir_menu(user_type):
    print("""
==============================
   AutoParts Inventory System
==============================
1️⃣  Cadastrar Peça
2️⃣  Listar Peças
3️⃣  Consultar Peça
4️⃣  Atualizar Peça
5️⃣  Remover Peça (ADM)
6️⃣  Gerar Relatório
""")
    if user_type == "ADM":
        print("7️⃣  Cadastrar Novo Usuário (ADM)")
    print("0️⃣  Sair")
