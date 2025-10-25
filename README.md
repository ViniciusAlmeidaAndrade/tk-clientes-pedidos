# 🛒 Gestão de Clientes & Pedidos com Tkinter + IA 🤖

Este é um projeto de um sistema simples (CRUD) para gestão de clientes e seus respectivos pedidos, desenvolvido em Python com a biblioteca Tkinter para a interface gráfica e SQLite para a persistência de dados.

O projeto foi desenvolvido como uma atividade acadêmica, com o objetivo de praticar a modelagem de entidades, construção de GUIs, persistência de dados e o uso responsável de assistentes de IA para acelerar o desenvolvimento e prototipação.

---

## ✅ Funcionalidades Principais

* **Clientes:** CRUD completo para o cadastro de clientes.
* **Produtos:** CRUD completo para um catálogo de produtos reutilizáveis (Nome e Preço).
* **Pedidos:** Criação de pedidos selecionando produtos de um catálogo, com cálculo automático do total.
* **Busca:** Filtro de clientes e produtos por nome.
* **Persistência:** Todos os dados são salvos em um banco de dados SQLite local.
* **UX:** Interface gráfica intuitiva com validações e mensagens de confirmação/erro.
---

## 🏗️ Arquitetura do Projeto

O projeto segue uma estrutura modular para separar responsabilidades, facilitando a manutenção e a legibilidade do código.

```text
tk-clientes-pedidos/
├── .gitignore          # Configuração para ignorar arquivos e pastas (como .venv, .idea)
├── .venv/              # Pasta do ambiente virtual (ignorada pelo Git)
├── app_database.db     # Arquivo do banco de dados (ignorado pelo Git)
├── db.py               # Módulo para interações com o banco de dados (SQLite)
├── main.py             # Ponto de entrada da aplicação (Controlador Principal)
├── models.py           # Definição das estruturas de dados (dataclasses)
├── README.md           # Documentação do projeto
├── requirements.txt    # Lista de dependências (vazio, usa apenas bibliotecas padrão)
├── utils.py            # Funções utilitárias (ex: logs)
└── views/              # Pacote com os módulos da interface gráfica (GUI)
    ├── __init__.py     # Inicializador do pacote 'views'
    ├── form_cliente.py # Janela de formulário para criar/editar clientes
    ├── form_pedido.py  # Janela de formulário para criar pedidos
    └── lista_cliente.py# Frame que exibe a lista de clientes
```
---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
* **Python 3.10+**

Nenhuma biblioteca externa é necessária, pois o projeto utiliza apenas a biblioteca padrão do Python (Tkinter, SQLite3, etc.).

### Passos para Execução
1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/tk-clientes-pedidos.git](https://github.com/seu-usuario/tk-clientes-pedidos.git)
    ```

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd tk-clientes-pedidos
    ```

3.  **(Opcional, mas recomendado) Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  **Execute a aplicação:**
    ```bash
    python main.py
    ```
    > ℹ️ Ao ser executado pela primeira vez, o arquivo `app_database.db` será criado automaticamente na raiz do projeto.

---

## 📖 Como Usar a Aplicação

Para criar um pedido, siga o fluxo de trabalho abaixo:

1.  **📦 Cadastre os Produtos:** Vá para a aba **"Produtos"** e adicione os itens que você vende ao catálogo.
2.  **👤 Cadastre os Clientes:** Na aba **"Clientes"**, adicione um ou mais clientes.
3.  **🛒 Crie um Pedido:** Com clientes e produtos já cadastrados, vá para a aba **"Pedidos"**, clique em "Novo Pedido", selecione o cliente e adicione itens do seu catálogo ao pedido.

---
## 🧠 Registro de IA

Este projeto foi desenvolvido com o auxílio de um assistente de IA para gerar código base, explicar conceitos e refinar funcionalidades. Abaixo estão os principais prompts utilizados no processo.

### Prompt 1 — Modelagem e DB 📊
> “Crie, para um app Tkinter, o esquema de SQLite com tabelas clientes (id, nome, email, telefone) e pedidos (id, cliente_id, data, total) e itens_pedido (id, pedido_id, produto, quantidade, preco_unit). Gere funções Python em db.py para inicializar o banco e executar comandos parametrizados com tratamento de erros.”

---

### Prompt 2 — Formulário de Cliente 📝
> “Gere um formulário Tkinter (janela Toplevel) para cadastrar/editar Clientes com campos nome, e-mail e telefone. Valide: nome obrigatório, e-mail em formato simples, telefone com 8–15 dígitos. Inclua botões Salvar/Cancelar e callbacks separados.”

---

### Prompt 3 — Lista de Clientes com busca 🔍
> “Crie um frame Tkinter com Treeview para listar clientes, com barra de busca por nome/email e botões Novo/Editar/Excluir. Ao excluir, peça confirmação. Recarregue a lista após operações.”

---

### Prompt 4 — Pedido com itens 📦
> “Implemente uma janela Tkinter para criar Pedido: selecione Cliente (Combobox), campo Data (hoje por padrão), tabela de itens (produto/quantidade/preço), botões Adicionar/Remover item e cálculo automático do total. Salve em pedidos e itens_pedido de forma transacional.”

---

### Prompt 5 — Extensão com Catálogo de Produtos 🧩
> > “Implemente uma nova funcionalidade no sistema. Quero uma lista de produtos onde possam ser adicionados e excluídos, e que no pedido o usuário apenas escolha o produto.
---

### Prompt 6 — UX e validações 🛡️
> “Melhore UX do app: mensagens amigáveis (messagebox), validações com feedback, prevenção de fechar janela com dados não salvos, e try/except com logs simples.”

---

### Prompts Adicionais de Estrutura 🧩
> "Gostaria de criar um models.py (para desacoplar a lógica usando dataclasses)."
> "Agora crie um main.py para mim (para conectar todas as views, modelos e o banco de dados)."
> "Quero que crie um readme explicando como rodar e com os principais prompts usados."

---

### Prompt Final — Refinamento do README ✨
> "Melhore visualmente o readme com emoji e bem divididos, e faça como .md"
