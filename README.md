# AutoParts - Sistema de Controle de Estoque

![AutoParts Logo](https://via.placeholder.com/400x100.png?text=AutoParts+Logo) 
Sistema de controle de estoque de peças automotivas com interface gráfica desenvolvida em **Python (Tkinter)** e banco de dados **PostgreSQL**.

---

## Funcionalidades

- [x] Login com dois tipos de usuário: `ADM` e `FUNCIONÁRIO`
- [x] Cadastro de peças (nome, descrição, quantidade, preço)
- [x] Registro de movimentações de entrada e saída (venda ou remoção)
- [x] Consulta de peças ativas no estoque
- [x] Geração de relatórios de movimentações
- [x] Exportação de relatórios para Excel
- [x] Cadastro de novos usuários (somente ADM)

---

## Estrutura do Projeto

```
AutoParts/
├── app.py                 # Arquivo principal (tela login e tela principal)
├── estoque.py             # Telas de cadastro, listagem e remoção de peças
├── vendas.py              # Tela de vendas
├── relatorio.py           # Tela de relatório e exportação
├── db.py                  # Conexão com banco de dados PostgreSQL
├── logo.png               # Logo utilizado no sistema (opcional)
├── requirements.txt       # Bibliotecas necessárias
└── README.md              # Este arquivo
```

---

## Tecnologias e Como Executar o Projeto

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/AutoParts.git
cd AutoParts
```

Crie e ative o ambiente virtual:

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Tecnologias utilizadas: Python 3.10+, Tkinter, PostgreSQL, pandas, psycopg2

Configure o banco de dados PostgreSQL criando o banco `autoparts` e as tabelas conforme abaixo.

Execute o sistema:

```bash
python app.py
```

---

## Configuração do Banco de Dados

```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('ADM', 'FUNCIONARIO')) NOT NULL
);

CREATE TABLE pecas (
    id_peca VARCHAR(20) PRIMARY KEY,
    nome VARCHAR(100),
    descricao TEXT,
    quantidade INT,
    preco DECIMAL,
    ativa BOOLEAN DEFAULT TRUE
);

CREATE TABLE movimentacoes (
    id SERIAL PRIMARY KEY,
    id_peca VARCHAR(20) REFERENCES pecas(id_peca),
    tipo VARCHAR(20), -- ENTRADA ou SAÍDA
    quantidade INT,
    data TIMESTAMP DEFAULT NOW()
);
```

---


## Contribuições

Contribuições são bem-vindas! Para contribuir:

```bash
git fork https://github.com/seu-usuario/AutoParts.git
git checkout -b nova-funcionalidade
git commit -m 'Adiciona nova funcionalidade'
git push origin nova-funcionalidade
```

Abra um Pull Request.

---

## Autora

Lorrayne  
Graduanda em Bacharelado em Tecnologia da Informação  
Apaixonada por soluções práticas e interfaces eficientes.

---

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
