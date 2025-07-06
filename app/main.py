# main.py

from estoque import cadastrar_peca, listar_pecas, consultar_peca, atualizar_peca, remover_peca
from relatorio import Relatorio
from usuarios import login, cadastrar_usuario
from utils import exibir_menu
from app.db import criar_tabelas
from vendas import RegistrarVenda

def main():
    criar_tabelas()  

    print("Bem-vindo ao AutoParts Inventory System")
    user_type = None

    while not user_type:
        user_type = login()

    print(f"\nLogado como: {user_type}")

    while True:
        exibir_menu(user_type)
        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            cadastrar_peca()
        elif opcao == '2':
            listar_pecas()
        elif opcao == '3':
            consultar_peca()
        elif opcao == '4':
            atualizar_peca()
        elif opcao == '5':
            if user_type == "ADM":
                remover_peca(user_type)
            else:
                print("Permissão negada! Apenas ADM pode remover peças.")

        elif opcao == '6':
            Relatorio()
        elif opcao == '7' and user_type == 'ADM':
            cadastrar_usuario()
        elif opcao == '0':
            print("Saindo... Até logo!")
            break
        else:
            print("Opção inválida ou não permitida!")

if __name__ == "__main__":
    main()
