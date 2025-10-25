import sqlite3
import os

# Define o nome do arquivo do banco de dados
DB_FILE = 'app_database.db'


def inicializar_banco():
    """
    Cria as tabelas no banco de dados SQLite se elas ainda não existirem.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # SQL para criar a tabela de produtos
        sql_criar_tabela_produtos = """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            preco REAL NOT NULL CHECK(preco >= 0)
        );
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

        # SQL para criar a tabela de itens do pedido (MODIFICADA)
        sql_criar_tabela_itens_pedido = """
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER NOT NULL,
            preco_unit REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        );
        """

        # Executa a criação das tabelas
        cursor.execute(sql_criar_tabela_produtos)
        cursor.execute(sql_criar_tabela_clientes)
        cursor.execute(sql_criar_tabela_pedidos)
        cursor.execute(sql_criar_tabela_itens_pedido)

        conn.commit()
        print(f"Banco de dados '{DB_FILE}' inicializado com sucesso.")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao inicializar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()


def executar_comando(sql: str, parametros: tuple = ()):
    """
    Executa um comando SQL parametrizado (INSERT, UPDATE, DELETE, SELECT).
    """
    conn = None
    resultados = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(sql, parametros)

        if sql.strip().upper().startswith("SELECT"):
            resultados = cursor.fetchall()
        else:
            conn.commit()
            resultados = True

    except sqlite3.Error as e:
        print(f"Erro ao executar comando SQL: {e}")
        if conn:
            conn.rollback()
        # Lança a exceção para que a camada de controle possa tratá-la
        raise e

    finally:
        if conn:
            conn.close()
    return resultados


# --- Bloco de Teste ---
if __name__ == "__main__":
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Banco de dados antigo '{DB_FILE}' removido para teste.")

    inicializar_banco()
    print("\n--- Testando Funções ---")

    try:
        # Inserindo Produtos
        print("Inserindo produtos...")
        executar_comando("INSERT INTO produtos (nome, preco) VALUES (?, ?)", ("Teclado Mecânico RGB", 299.90))
        executar_comando("INSERT INTO produtos (nome, preco) VALUES (?, ?)", ("Mouse Gamer Sem Fio", 180.50))

        # Inserindo Clientes
        print("Inserindo clientes...")
        executar_comando("INSERT INTO clientes (nome, email) VALUES (?, ?)", ("Carlos Pereira", "carlos@email.com"))

        # Inserindo Pedido
        print("Inserindo pedido para cliente 1...")
        executar_comando("INSERT INTO pedidos (cliente_id, data, total) VALUES (?, ?, ?)", (1, "2025-10-25", 779.90))

        # Inserindo Itens no Pedido (usando produto_id)
        print("Inserindo itens para o pedido 1...")
        sql_insert_item = "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unit) VALUES (?, ?, ?, ?)"
        executar_comando(sql_insert_item, (1, 1, 2, 299.90)) # 2 teclados
        executar_comando(sql_insert_item, (1, 2, 1, 180.50)) # 1 mouse

        # Teste de SELECT com JOIN triplo
        print("\nBuscando detalhes do pedido...")
        sql_join = """
            SELECT c.nome, pr.nome, ip.quantidade, ip.preco_unit
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            JOIN itens_pedido ip ON ip.pedido_id = p.id
            JOIN produtos pr ON ip.produto_id = pr.id
            WHERE p.id = 1
        """
        detalhes = executar_comando(sql_join)
        for detalhe in detalhes:
            print(detalhe)

    except Exception as e:
        print(f"\nOcorreu um erro durante o teste: {e}")