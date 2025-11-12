# 🛒 Gestão de Clientes & Pedidos com Tkinter + IA 🤖

Este é um projeto de um sistema de gestão (CRUD) para clientes e pedidos, desenvolvido em Python com a biblioteca Tkinter para a interface gráfica e SQLite para a persistência de dados.

O projeto evoluiu para incluir um dashboard de métricas, relatórios em PDF/CSV, um log de auditoria e integração com a API Google Gemini para análise de dados.

---

## ✅ Funcionalidades Principais

* **Dashboard:** Uma tela inicial com métricas de negócios (KPIs) como total de clientes, pedidos no mês e ticket médio.
* **Análise com IA:** Um botão no dashboard que utiliza a API Google Gemini para analisar os últimos 5 pedidos e fornecer insights acionáveis (ex: produtos mais vendidos, média de valor).
* **CRUDs Completos:**
    * **Clientes:** Cadastro, edição, exclusão e busca.
    * **Produtos:** Gerenciamento de um catálogo de produtos reutilizáveis.
* **Criação de Pedidos:** Um formulário que seleciona clientes e produtos do catálogo para criar novos pedidos, calculando o total automaticamente.
* **Relatórios:** Uma aba dedicada para filtrar pedidos por período (data) e por cliente, com opções de exportação para **CSV** e **PDF**.
* **Histórico (Log de Auditoria):**
    * Registra automaticamente todas as ações de criação, edição e exclusão em um arquivo `logs/app.log`.
    * Exibe esse histórico em uma tela própria com opção de limpeza.
* **Temas:** Um menu de opções permite alternar a interface entre **Tema Claro** e **Tema Escuro** em tempo real.
* **Navegação:** Interface moderna com abas e uma barra de menu superior para navegação rápida.
* **Persistência:** Todos os dados são salvos em um banco de dados SQLite local (`app_database.db`).

---

## 🏗️ Arquitetura do Projeto

O projeto segue uma estrutura modular para separar a Interface (Views), a Lógica de Negócios (Core) e os Dados (Models/DB).

```text
tk-clientes-pedidos/
├── .venv/                  # Ambiente virtual
├── core/                   # Lógica de negócios
│   ├──__init__.py
|   ├── analysis.py         # Lógica de integração com API (Gemini)
│   └── database.py         # Funções de consulta ao banco (SELECTs)
├── logs/                   # Logs de auditoria
│   └── app.log
├── views/                  # Pacote com os módulos da UI (Telas)
│   ├── __init__.py
│   ├── dashboard_view.py
│   ├── form_cliente.py
│   ├── form_pedido.py
│   ├── form_produto.py
│   ├── historico_view.py
│   ├── lista_cliente.py
│   ├── lista_produto.py
│   └── relatorios_view.py
├── .env                    # Arquivo de chave de API (Ignorado pelo Git)
├── .gitignore
├── app_database.db         # Banco de dados (Ignorado pelo Git)
├── db.py                   # Funções de baixo-nível do SQLite (Init, C/U/D)
├── main.py                 # Ponto de entrada (AppController principal)
├── models.py               # Definição das Dataclasses (estruturas)
├── README.md               # Este arquivo
├── requirements.txt        # Lista de dependências do projeto
└── styles.py               # Definições dos temas Claro/Escuro
```
---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
* **Python 3.10+**
* Uma chave de API do **Google AI Studio** (para a funcionalidade de IA).

### Passos para Execução
1.  **Clone o repositório:**
    ```bash
    git clone [URL-DO-SEU-REPOSITORIO]
    cd tk-clientes-pedidos
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    O projeto agora usa bibliotecas externas. Instale-as com:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure a Chave de API (Obrigatório para IA):**
    * Crie um arquivo chamado `.env` na pasta raiz do projeto.
    * Abra o arquivo e adicione sua chave de API do Google AI Studio:
        ```
        GOOGLE_API_KEY=SUA_CHAVE_DE_API_AIza...
        ```

5.  **Execute a aplicação:**
    ```bash
    python main.py
    ```
    > ℹ️ Ao ser executado pela primeira vez, o arquivo `app_database.db` e a pasta `logs/` serão criados automaticamente.

---

## 🧠 Registro de IA

Este projeto foi desenvolvido com o auxílio de um assistente de IA. Abaixo estão os principais prompts utilizados no processo.

### Prompt 1 — Modelagem e DB 📊
> “Crie, para um app Tkinter, o esquema de SQLite com tabelas clientes, pedidos e itens_pedido. Gere funções Python em db.py para inicializar o banco e executar comandos parametrizados...”

### Prompt 2 — Formulário e Lista de Clientes 📝
> “Gere um formulário Tkinter (Toplevel) para cadastrar/editar Clientes... Crie um frame Tkinter com Treeview para listar clientes, com barra de busca por nome/email e botões Novo/Editar/Excluir.”

### Prompt 3 — Pedido com Itens 📦
> “Implemente uma janela Tkinter para criar Pedido: selecione Cliente (Combobox), campo Data, tabela de itens (produto/quantidade/preço), botões Adicionar/Remover item e cálculo automático do total...”

### Prompt 4 — Dashboard de Métricas 📈
> “Crie uma tela inicial (Dashboard) que exiba: total de clientes, total de pedidos no mês, e ticket médio. Use consultas SQLite agregadas e widgets Label...”

### Prompt 5 — Relatórios com Filtro e Exportação 📄
> “Implemente uma janela ‘Relatórios’ com filtros por data inicial/final e cliente (Combobox). Liste os pedidos filtrados em uma Treeview. Adicione botões para Exportar CSV e Exportar PDF (usando reportlab)...”

### Prompt 6 — Análise com IA (Gemini) 🤖
> “Adicione botão ‘Analisar Pedidos’ que lê os 5 últimos pedidos do banco, gera um resumo textual e envia via API para o Google Gemini. Mostre o resultado em Text widget com rolagem.”

**Prompt enviado para o Gemini (registrado conforme solicitado):**
```
Você é um assistente de análise de vendas para um pequeno negócio.
Analise os dados brutos dos últimos 5 pedidos fornecidos a seguir e retorne um resumo em português brasileiro com insights acionáveis.
Formate sua resposta em 3 a 5 tópicos curtos (bullet points).
[...]
Responda APENAS com os insights.
---
[DADOS DOS PEDIDOS]
{dados_formatados}
---
[/DADOS DOS PEDIDOS]
```

### Prompt 7 — Log de Auditoria (Histórico) 🔍
> “Adicione registro automático de ações (Criar, Editar, Excluir Cliente/Pedido) em logs/app.log com timestamp. Crie janela ‘Histórico’ que lê esse arquivo e exibe os eventos em Listbox. Inclua botão ‘Limpar Histórico’...”

### Prompt 8 — Menu Principal e Temas 🎨
> “Implemente menu principal (Menu bar) com opções: Clientes, Pedidos, Sair, etc. Bloqueie fechamento com confirmação, e permita alternar tema claro/escuro via ttk.Style().”