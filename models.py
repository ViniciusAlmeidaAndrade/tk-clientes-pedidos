from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date, datetime
import db

"""
Este arquivo define os modelos de dados (estruturas de dados)
usados em toda a aplicação.

Usar dataclasses em vez de tuplas ou dicionários torna o código
mais legível, mais fácil de manter e introduz verificação de tipo.
"""


@dataclass
class Cliente:
    """Representa um Cliente no banco de dados."""
    id: Optional[int]
    nome: str
    email: Optional[str]
    telefone: Optional[str]

    @classmethod
    def from_tuple(cls, data_tuple: tuple):
        """Cria uma instância de Cliente a partir de uma tupla do banco de dados."""
        # Espera a ordem: (id, nome, email, telefone)
        if not data_tuple:
            return None
        return cls(id=data_tuple[0], nome=data_tuple[1], email=data_tuple[2], telefone=data_tuple[3])


@dataclass
class ItemPedido:
    """Representa um item dentro de um Pedido."""
    produto: str
    quantidade: int
    preco_unit: float
    id: Optional[int] = None
    pedido_id: Optional[int] = None

    @property
    def subtotal(self) -> float:
        """Calcula o subtotal deste item."""
        return self.quantidade * self.preco_unit

    @classmethod
    def from_tuple(cls, data_tuple: tuple):
        """Cria uma instância de ItemPedido a partir de uma tupla do banco de dados."""
        # Espera a ordem: (id, pedido_id, produto, quantidade, preco_unit)
        if not data_tuple:
            return None
        return cls(
            id=data_tuple[0],
            pedido_id=data_tuple[1],
            produto=data_tuple[2],
            quantidade=data_tuple[3],
            preco_unit=data_tuple[4]
        )


@dataclass
class Pedido:
    """
    Representa um Pedido, que é composto por dados do cliente
    e uma lista de itens.
    """
    id: Optional[int]
    cliente_id: int
    data: date | str  # Aceita str do DB, mas idealmente deve ser 'date'
    total: float

    # Esta lista é preenchida separadamente pelo controlador
    itens: List[ItemPedido] = field(default_factory=list)

    # Armazena o nome do cliente para exibição (carregado pelo controlador)
    nome_cliente: Optional[str] = None

    @classmethod
    def from_tuple(cls, data_tuple: tuple):
        """Cria uma instância de Pedido a partir de uma tupla do banco de dados."""
        # Espera a ordem: (id, cliente_id, data, total)
        if not data_tuple:
            return None
        return cls(
            id=data_tuple[0],
            cliente_id=data_tuple[1],
            data=data_tuple[2],
            total=data_tuple[3]
        )


def fetch_dados_dashboard():
    """
    Busca os dados agregados (KPIs) do banco de dados para o Dashboard.
    Retorna: (total_clientes, total_pedidos_mes, ticket_medio_mes)
    """

    # Define o mês atual no formato YYYY-MM para o SQLite
    mes_atual_param = datetime.now().strftime('%Y-%m')

    # Query 1: Total de Clientes (Agregação COUNT)
    # db.executar_comando retorna uma lista de tuplas.
    sql_clientes = "SELECT COUNT(id) FROM clientes;"
    total_clientes = db.executar_comando(sql_clientes)[0][0]

    # Query 2: Total de Pedidos no Mês (COUNT + WHERE)
    sql_pedidos = "SELECT COUNT(id) FROM pedidos WHERE strftime('%Y-%m', data) = ?;"
    total_pedidos_mes = db.executar_comando(sql_pedidos, (mes_atual_param,))[0][0]

    # Query 3: Ticket Médio do Mês (AVG + WHERE)
    sql_ticket = "SELECT AVG(total) FROM pedidos WHERE strftime('%Y-%m', data) = ?;"
    ticket_medio_mes = db.executar_comando(sql_ticket, (mes_atual_param,))[0][0]

    # Se não houver pedidos no mês, AVG retorna None. Tratamos isso.
    if ticket_medio_mes is None:
        ticket_medio_mes = 0.0

    return total_clientes, total_pedidos_mes, ticket_medio_mes


# --- NOVAS FUNÇÕES DE RELATÓRIO ---

def fetch_clientes_para_combobox():
    """Busca todos os clientes (ID, Nome) para preencher comboboxes."""
    sql = "SELECT id, nome FROM clientes ORDER BY nome"
    try:
        resultados = db.executar_comando(sql)
        return resultados
    except Exception as e:
        # Relança a exceção para ser tratada pelo controller
        raise Exception(f"Erro ao buscar lista de clientes: {e}")


def fetch_relatorio_pedidos(data_inicio=None, data_fim=None, cliente_id=None):
    """
    Busca pedidos filtrados para o relatório, incluindo contagem de itens.
    """

    # Parâmetros e cláusulas WHERE dinâmicas
    params = []
    where_clauses = []

    # --- Montagem dinâmica da Query ---
    if data_inicio:
        where_clauses.append("p.data >= ?")
        params.append(data_inicio)

    if data_fim:
        where_clauses.append("p.data <= ?")
        params.append(data_fim)

    if cliente_id:
        where_clauses.append("p.cliente_id = ?")
        params.append(cliente_id)

    # Constrói a string WHERE
    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    # Query principal com JOIN e Subquery para contagem de itens
    sql = f"""
    SELECT 
        p.id,
        p.data,
        c.nome,
        (SELECT COUNT(ip.id) 
         FROM itens_pedido ip 
         WHERE ip.pedido_id = p.id) as total_itens,
        p.total
    FROM pedidos p
    JOIN clientes c ON p.cliente_id = c.id
    {where_sql}
    ORDER BY p.data DESC;
    """

    try:
        # Converte a lista de params para tupla
        resultados = db.executar_comando(sql, tuple(params))
        return resultados
    except Exception as e:
        raise Exception(f"Erro ao gerar relatório de pedidos: {e}")


# --- Bloco de Teste ---
if __name__ == "__main__":
    print("--- Testando Modelos de Dados ---")

    # 1. Testando Cliente
    print("\n[Cliente]")
    tupla_cliente = (1, "Ana Beatriz", "ana.b@email.com", "11988776655")
    cliente_obj = Cliente.from_tuple(tupla_cliente)
    print(f"Objeto: {cliente_obj}")
    print(f"Nome: {cliente_obj.nome}")
    print(f"ID: {cliente_obj.id}")

    # 2. Testando ItemPedido
    print("\n[ItemPedido]")
    item_obj = ItemPedido(produto="Teclado USB", quantidade=2, preco_unit=89.90)
    print(f"Objeto: {item_obj}")
    print(f"Produto: {item_obj.produto}")
    print(f"Subtotal: R$ {item_obj.subtotal:.2f}")

    tupla_item = (10, 5, "Mouse sem Fio", 1, 120.50)
    item_obj_db = ItemPedido.from_tuple(tupla_item)
    print(f"Objeto (do DB): {item_obj_db}")
    print(f"Subtotal (do DB): R$ {item_obj_db.subtotal:.2f}")

    # 3. Testando Pedido
    print("\n[Pedido]")
    tupla_pedido = (5, 1, "2024-10-25", 300.30)
    pedido_obj = Pedido.from_tuple(tupla_pedido)

    # O controlador seria responsável por adicionar os itens
    pedido_obj.itens.append(item_obj)
    pedido_obj.itens.append(item_obj_db)
    pedido_obj.nome_cliente = cliente_obj.nome

    print(f"Objeto: {pedido_obj}")
    print(f"Nome do Cliente: {pedido_obj.nome_cliente}")
    print(f"Data: {pedido_obj.data}")
    print(f"Total (Armazenado): R$ {pedido_obj.total:.2f}")

    # Podemos verificar o total calculado vs. armazenado
    total_calculado = sum(item.subtotal for item in pedido_obj.itens)
    print(f"Total (Calculado dos itens): R$ {total_calculado:.2f}")

    print("\n--- Testes Concluídos ---")