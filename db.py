import sqlite3
import os

# Define o nome do arquivo do banco de dados
DB_FILE = 'app_database.db'


def inicializar_banco():
    """
    Cria as tabelas no banco de dados SQLite se elas ainda não existirem.
    """
    # SQL para criar a tabela de clientes
    sql_criar_tabela_clientes = """
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT
    );
    """

    # SQL para criar a tabela de pedidos
    sql_criar_tabela_pedidos = """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        data TEXT NOT NULL,
        total REAL,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
    );
    """

    # SQL para criar a tabela de itens do pedido
    sql_criar_tabela_itens_pedido = """
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        produto TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unit REAL NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
    );
    """

    conn = None
    try:
        # Conecta ao banco (ou cria se não existir)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Executa a criação das tabelas
        cursor.execute(sql_criar_tabela_clientes)
        cursor.execute(sql_criar_tabela_pedidos)
        cursor.execute(sql_criar_tabela_itens_pedido)

        # Confirma as alterações
        conn.commit()
        print(f"Banco de dados '{DB_FILE}' inicializado com sucesso.")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao inicializar o banco de dados: {e}")
    finally:
        # Garante que a conexão seja fechada
        if conn:
            conn.close()


def executar_comando(sql: str, parametros: tuple = ()):
    """
    Executa um comando SQL parametrizado (INSERT, UPDATE, DELETE, SELECT).

    Para comandos SELECT, retorna os resultados (lista de tuplas).
    Para outros comandos (INSERT, UPDATE, DELETE), retorna True em sucesso.
    Retorna None em caso de falha.
    """
    conn = None
    resultados = None

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Habilita o suporte a chaves estrangeiras
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute(sql, parametros)

        # Verifica se é um comando SELECT para buscar resultados
        if sql.strip().upper().startswith("SELECT"):
            resultados = cursor.fetchall()
        else:
            # Se não for SELECT, é uma modificação, então faz commit
            conn.commit()
            resultados = True  # Indica sucesso para INSERT/UPDATE/DELETE

    except sqlite3.Error as e:
        print(f"Erro ao executar comando SQL: {e}")
        if conn:
            # Desfaz qualquer alteração pendente em caso de erro
            conn.rollback()
        resultados = None  # Indica falha

    finally:
        if conn:
            conn.close()

    return resultados


# --- Bloco de Teste ---
if __name__ == "__main__":
    # Remove o banco de dados antigo (se existir) para um teste limpo
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Banco de dados antigo '{DB_FILE}' removido para teste.")

    # 1. Inicializa o banco
    inicializar_banco()

    print("\n--- Testando Funções ---")

    # 2. Teste de INSERT (Clientes)
    print("Inserindo clientes...")
    sql_insert_cliente = "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)"
    executar_comando(sql_insert_cliente, ("João Silva", "joao@email.com", "11987654321"))
    executar_comando(sql_insert_cliente, ("Maria Souza", "maria@email.com", "21912345678"))

    # 3. Teste de SELECT (Clientes)
    print("Buscando clientes...")
    sql_select_clientes = "SELECT * FROM clientes"
    clientes = executar_comando(sql_select_clientes)
    if clientes is not None:
        for cliente in clientes:
            print(cliente)

    # 4. Teste de INSERT (Pedido para o cliente 1)
    print("Inserindo pedido para cliente 1...")
    sql_insert_pedido = "INSERT INTO pedidos (cliente_id, data, total) VALUES (?, ?, ?)"
    executar_comando(sql_insert_pedido, (1, "2025-10-24", 150.50))

    # 5. Teste de INSERT (Itens para o pedido 1)
    print("Inserindo itens para o pedido 1...")
    sql_insert_item = "INSERT INTO itens_pedido (pedido_id, produto, quantidade, preco_unit) VALUES (?, ?, ?, ?)"
    executar_comando(sql_insert_item, (1, "Produto A", 2, 50.25))
    executar_comando(sql_insert_item, (1, "Produto B", 1, 50.00))

    # 6. Teste de SELECT (Pedidos com JOIN)
    print("Buscando pedidos e nomes dos clientes...")
    sql_select_pedidos_join = """
    SELECT p.id, p.data, p.total, c.nome 
    FROM pedidos p
    JOIN clientes c ON p.cliente_id = c.id
    """
    pedidos_com_nomes = executar_comando(sql_select_pedidos_join)
    if pedidos_com_nomes is not None:
        for pedido in pedidos_com_nomes:
            print(pedido)

    # 7. Teste de erro (tentando inserir pedido com cliente_id que não existe)
    print("Testando erro de chave estrangeira...")
    executar_comando(sql_insert_pedido, (99, "2025-10-25", 10.00))