Principais Funcionalidades

Gestão de Clientes (CRUD):

Listar, buscar (por nome/email), criar, editar e excluir clientes.

Validação de formulário (nome obrigatório, formato de e-mail, dígitos de telefone).

Gestão de Pedidos:

Listar pedidos existentes (com nome do cliente).

Criar novos pedidos associados a um cliente.

Adicionar/Remover múltiplos itens (produto, quantidade, preço) em um pedido.

Cálculo automático do total do pedido.

Banco de Dados:

Salvamento transacional (garante que um pedido e todos os seus itens sejam salvos juntos, ou nada é salvo).

Uso de Chaves Estrangeiras (FOREIGN KEY) para garantir a integridade (impede a exclusão de clientes com pedidos).

Experiência do Usuário (UX):

Mensagens de erro, sucesso e confirmação amigáveis (messagebox).

Prevenção de perda de dados (pergunta ao usuário se deseja salvar antes de fechar uma janela com dados alterados).

Logging simples de erros e informações no console (utils.py).

Arquitetura do Projeto

O projeto está estruturado da seguinte forma:

tk-clientes-pedidos/
├── main.py           # Ponto de entrada, controlador principal (AppController)
├── db.py             # Funções de inicialização e acesso ao DB (SQLite)
├── models.py         # Classes de dados (dataclasses: Cliente, Pedido, ItemPedido)
├── utils.py          # Funções utilitárias (ex: logging)
├── views/
│   ├── lista_cliente.py # View (Frame) da lista de clientes (ClientesView)
│   ├── form_clientes.py # View (Toplevel) do formulário de cliente (FormCliente)
│   └── form_pedido.py   # View (Toplevel) do formulário de pedido (FormPedido)
├── pedidos_app.db    # (Gerado automaticamente ao executar)
└── README.md         # Este arquivo


Como Executar

Pré-requisitos

Python 3.x (versão 3.7 ou superior recomendada).

Não são necessárias bibliotecas externas! O projeto utiliza apenas a biblioteca padrão do Python (tkinter, sqlite3, re, datetime, os, sys).

Passos para Execução

Clone ou baixe este repositório para o seu computador.

Abra um terminal ou prompt de comando.

Navegue até o diretório raiz do projeto (a pasta tk-clientes-pedidos/ que contém o main.py).

Execute o aplicativo:

python main.py


A aplicação será iniciada, e o arquivo de banco de dados pedidos_app.db será criado automaticamente no mesmo diretório.

Histórico de Prompts (Desenvolvimento)

Este aplicativo foi construído iterativamente usando os seguintes comandos principais:

Criação do Banco de Dados: "Crie, para um app Tkinter, o esquema de SQLite com tabelas clientes (...) e pedidos (...) e itens_pedido (...). Gere funções Python em db.py para inicializar o banco e executar comandos parametrizados com tratamento de erros."

Formulário de Cliente: "Gere um formulário Tkinter (janela Toplevel) para cadastrar/editar Clientes com campos nome, e-mail e telefone. Valide: nome obrigatório, e-mail em formato simples, telefone com 8–15 dígitos. Inclua botões Salvar/Cancelar e callbacks separados."

Lista de Clientes: "Crie um frame Tkinter com Treeview para listar clientes, com barra de busca por nome/email e botões Novo/Editar/Excluir. Ao excluir, peça confirmação. Recarregue a lista após operações."

Formulário de Pedido: "Implemente uma janela Tkinter para criar Pedido: selecione Cliente (Combobox), campo Data (hoje por padrão), tabela de itens (produto/quantidade/preço), botões Adicionar/Remover item e cálculo automático do total. Salve em pedidos e itens_pedido de forma transacional."

Melhorias de UX e Logging: "Melhore UX do app: mensagens amigáveis (messagebox), validações com feedback, prevenção de fechar janela com dados não salvos, e try/except com logs simples (crie utils.py)."

Criação dos Modelos: "Gostaria de criar um models.py (para desacoplar a lógica usando dataclasses)."

Criação do Controlador Principal: "Agora crie um main.py para min (para conectar todas as views, modelos e o banco de dados)."

Criação do README: "Quero que crie um readme explicando como rodar e com os principais prompts usados."