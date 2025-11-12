import db
import utils
from datetime import datetime

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
    

def fetch_ultimos_pedidos_para_analise(limite: int = 5):
    """
    Busca os últimos N pedidos e seus respectivos itens para análise de IA.
    Retorna uma lista de dicionários, cada um representando um pedido.
    """
    utils.log_info(f"Buscando {limite} últimos pedidos para análise.")
    
    # 1. Buscar os últimos 5 pedidos
    sql_pedidos = """
    SELECT p.id, p.data, p.total, c.nome
    FROM pedidos p
    JOIN clientes c ON p.cliente_id = c.id
    ORDER BY p.data DESC, p.id DESC
    LIMIT ?;
    """
    try:
        ultimos_pedidos = db.executar_comando(sql_pedidos, (limite,))
        
        pedidos_formatados = []
        
        # 2. Para cada pedido, buscar seus itens
        for p in ultimos_pedidos:
            pedido_id, data, total, cliente_nome = p
            
            sql_itens = """
            SELECT pr.nome, ip.quantidade, ip.preco_unit
            FROM itens_pedido ip
            JOIN produtos pr ON ip.produto_id = pr.id
            WHERE ip.pedido_id = ?;
            """
            itens_tuplas = db.executar_comando(sql_itens, (pedido_id,))
            
            itens_list = []
            for item in itens_tuplas:
                itens_list.append({
                    "produto": item[0],
                    "quantidade": item[1],
                    "preco_unit": item[2]
                })
            
            pedidos_formatados.append({
                "id_pedido": pedido_id,
                "data": data,
                "total": total,
                "cliente": cliente_nome,
                "itens": itens_list
            })
            
        return pedidos_formatados

    except Exception as e:
        raise Exception(f"Erro ao buscar dados detalhados dos pedidos: {e}")
