import sys
import datetime
import os         # Para carregar variáveis de ambiente e criar pastas
import logging    # Módulo de logging do Python

# --- Caminho do Arquivo de Log ---
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Logger dedicado para ações do usuário
action_logger = logging.getLogger('action_logger')

# =================================================================
# --- DEFINIÇÃO DAS FUNÇÕES DE LOG (CONSOLE) ---
# =================================================================

def log_erro(mensagem: str, excecao: Exception = None):
    """
    Registra uma mensagem de ERRO no stderr com data/hora.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ERRO] {timestamp} - {mensagem}", file=sys.stderr)
    if excecao:
        print(f"       Exceção: {excecao}", file=sys.stderr)


def log_info(mensagem: str):
    """
    Registra uma mensagem de INFORMAÇÃO no stdout com data/hora.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[INFO] {timestamp} - {mensagem}", file=sys.stdout)

# =================================================================
# --- CONFIGURAÇÃO DO LOGGING EM ARQUIVO ---
# =================================================================

def setup_logging():
    """
    Configura o logger 'action_logger' para salvar em logs/app.log.
    Deve ser chamado uma vez quando a aplicação iniciar.
    """
    try:
        # 1. Criar a pasta 'logs' se não existir
        os.makedirs(LOG_DIR, exist_ok=True)

        # 2. Configurar o logger
        action_logger.setLevel(logging.INFO)
        
        # Evitar duplicidade de handlers se a função for chamada por engano mais de uma vez
        if action_logger.hasHandlers():
            action_logger.handlers.clear()

        # 3. Criar o FileHandler (que escreve no arquivo)
        # 'a' = append (continua o log)
        # 'utf-8' = suporta acentos
        file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        
        # 4. Definir o formato da mensagem
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        
        # 5. Adicionar o handler ao logger
        action_logger.addHandler(file_handler)
        
        log_info(f"Logger de ações configurado. Salvando em: {LOG_FILE}")

    except Exception as e:
        log_erro("Falha CRÍTICA ao configurar o logger de arquivo!", e)

def log_acao(mensagem: str):
    """
    Registra uma ação do usuário no arquivo de log.
    Esta é a função que o main.py vai chamar.
    """
    action_logger.info(mensagem)

def ler_log() -> str:
    """
    Lê o conteúdo completo do arquivo de log.
    Retorna uma string vazia se o arquivo não existir.
    """
    try:
        if not os.path.exists(LOG_FILE):
            return "Arquivo de log ainda não criado."
            
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        log_erro("Falha ao ler arquivo de log.", e)
        return f"Erro ao ler log: {e}"

def limpar_log():
    """
    Apaga todo o conteúdo do arquivo de log.
    """
    try:
        # Abre em modo 'w' (write) para truncar (apagar) o conteúdo
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            pass # Apenas abrir e fechar apaga o conteúdo
        log_info("Arquivo de log limpo com sucesso.")
        # Loga a própria limpeza como a primeira nova entrada
        log_acao("HISTÓRICO LIMPO.")
    except Exception as e:
        log_erro("Falha ao limpar arquivo de log.", e)
        # Relança para o controller mostrar o messagebox de erro
        raise e

# =================================================================
# --- CONFIGURAÇÃO DO GEMINI ---
# =================================================================



# --- Bloco de Teste ---
if __name__ == "__main__":
    """
    Permite testar este arquivo diretamente.
    Execute: python utils.py
    """
    print("Testando funções de log...")
    
    # Configura o logger de arquivo
    setup_logging()

    log_info("Esta é uma mensagem de informação (vai para o console).")
    
    log_acao("Esta é uma AÇÃO (vai para o console E para o logs/app.log).")
    log_acao("Teste de exclusão de cliente.")
    
    print("\n--- Testando Leitura de Log ---")
    print(ler_log())
    
    # print("\n--- Testando Limpeza de Log ---")
    # limpar_log()
    # print(ler_log())

    print("\nTeste concluído.")