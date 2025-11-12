import threading
import os
from dotenv import load_dotenv
import google.generativeai as genai
from utils import log_info, log_erro
from . import database 

try:
    # Carrega as variáveis do arquivo .env
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        # Modelo estável e compatível
        GEMINI_MODEL = "models/gemini-flash-latest"
    else:
        log_erro("Variável de ambiente GOOGLE_API_KEY não encontrada.", None)

except ImportError:
    log_erro("Bibliotecas 'google-generativeai' ou 'python-dotenv' não instaladas.", None)
except Exception as e:
    log_erro(f"Erro ao configurar a API Gemini: {e}", e)
# -----------------------------


# =================================================================
# --- LÓGICA DE ANÁLISE COM IA (GEMINI) ---
# =================================================================



def _get_prompt_analise():
    """Lê o prompt (o mesmo de antes) que será enviado para a IA."""
    
    prompt_template = """
Você é um assistente de análise de vendas para um pequeno negócio.
Analise os dados brutos dos últimos 5 pedidos fornecidos a seguir e retorne um resumo em português brasileiro com insights acionáveis.

Formate sua resposta em 3 a 5 tópicos curtos (bullet points).

**Insights esperados (se os dados permitirem):**
* Qual o produto mais vendido (em quantidade total)?
* Qual o valor médio por pedido (calculado a partir destes 5 pedidos)?
* Algum cliente se destaca (comprando mais ou com pedidos de maior valor)?
* Qualquer outro padrão interessante que você notar (ex: produtos comprados juntos).

Responda APENAS com os insights.

---
[DADOS DOS PEDIDOS]
{dados_formatados}
---
[/DADOS DOS PEDIDOS]
"""
    return prompt_template.strip()

def _formatar_dados_para_ia(pedidos: list) -> str:
    """Converte a lista de pedidos em um texto simples para o prompt."""
    texto_formatado = ""
    if not pedidos:
        return "Nenhum pedido encontrado para análise."

    for p in pedidos:
        texto_formatado += f"Pedido ID: {p['id_pedido']} (Cliente: {p['cliente']}, Data: {p['data']}, Total: R$ {p['total']:.2f})\n"
        if not p['itens']:
            texto_formatado += "  - (Pedido sem itens registrados)\n"
        for item in p['itens']:
            texto_formatado += f"  - Item: {item['produto']}, Qtd: {item['quantidade']}, Preço Unit: R$ {item['preco_unit']:.2f}\n"
        texto_formatado += "---\n"
    return texto_formatado


def analisar_pedidos_com_ia(callback_sucesso, callback_erro):
    """
    Função principal que busca dados, formata, chama a API GEMINI em uma thread
    e usa callbacks para retornar a resposta ao AppController.
    """
    
    def worker():
        """Função que roda na thread separada."""
        try:
            log_info("Iniciando análise de IA com Gemini (worker thread)...")

            if not GEMINI_API_KEY:
                callback_erro("Erro de Configuração: A chave GOOGLE_API_KEY não foi encontrada.\n\nVerifique seu arquivo .env e reinicie o aplicativo.")
                return

            pedidos_data = database.fetch_ultimos_pedidos_para_analise(limite=5)
            dados_formatados = _formatar_dados_para_ia(pedidos_data)
            prompt_template = _get_prompt_analise()
            prompt_final = prompt_template.format(dados_formatados=dados_formatados)
            
            log_info(f"Enviando para API Gemini (modelo: {GEMINI_MODEL})...")

            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt_final)
            
            resultado_ia = response.text
            
            log_info("Análise de IA (Gemini) recebida com sucesso.")
            callback_sucesso(resultado_ia.strip())

        except Exception as e:
            log_erro("Erro inesperado na análise com Gemini.", e)
            if "API_KEY_INVALID" in str(e):
                callback_erro(f"Erro de Autenticação: Sua chave de API do Google é inválida. Verifique o arquivo .env.")
            else:
                callback_erro(f"Ocorreu um erro ao chamar a API do Gemini:\n{e}")

    log_info("Disparando thread de análise Gemini.")
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
