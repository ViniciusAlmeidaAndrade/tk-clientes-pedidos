import sys
import datetime


def log_erro(mensagem: str, excecao: Exception = None):
    """
    Registra uma mensagem de ERRO no stderr com data/hora.
    'stderr' é o fluxo de saída padrão para erros.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Imprime a mensagem de erro no console de erro
    print(f"[ERRO] {timestamp} - {mensagem}", file=sys.stderr)

    if excecao:
        # Se uma exceção foi passada, imprime seus detalhes
        print(f"       Exceção: {excecao}", file=sys.stderr)

        # Opcional: Se quiser o "rastreamento" completo do erro,
        # descomente as duas linhas abaixo.
        # import traceback
        # traceback.print_exc(file=sys.stderr)


def log_info(mensagem: str):
    """
    Registra uma mensagem de INFORMAÇÃO no stdout com data/hora.
    'stdout' é o fluxo de saída padrão para informações.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Imprime a mensagem de informação no console normal
    print(f"[INFO] {timestamp} - {mensagem}", file=sys.stdout)


# --- Bloco de Teste ---
if __name__ == "__main__":
    """
    Permite testar este arquivo diretamente.
    Execute: python utils.py
    """
    print("Testando funções de log...")

    log_info("Esta é uma mensagem de informação.")

    try:
        # Simula um erro
        x = 10 / 0
    except Exception as e:
        log_erro("Ocorreu um erro ao dividir por zero!", e)

    log_info("Teste concluído.")