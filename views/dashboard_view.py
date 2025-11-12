import tkinter as tk
from tkinter import ttk
from datetime import datetime

class DashboardView(ttk.Frame):
    """
    Frame que exibe os principais indicadores (KPIs) da aplicação.
    """
    def __init__(self, parent, on_atualizar_callback, on_analisar_callback): # 1. Adicionado on_analisar_callback
        super().__init__(parent, padding=20)
        
        # Callbacks
        self.on_atualizar_callback = on_atualizar_callback
        self.on_analisar_callback = on_analisar_callback # 2. Salva o novo callback

        # ... (mantenha as StringVars e Estilos) ...
        self.var_total_clientes = tk.StringVar(value="...")
        self.var_pedidos_mes = tk.StringVar(value="...")
        self.var_ticket_medio = tk.StringVar(value="...")

        style = ttk.Style(self)
        style.configure("Dashboard.TLabel", font=("Segoe UI", 12))
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Metrica.TLabel", font=("Segoe UI", 24, "bold"), foreground="#00529B")
        style.configure("TButton", font=("Segoe UI", 12))

        # --- Layout ---
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Visão Geral", style="Header.TLabel").pack(pady=(0, 25))

        # 1. Métricas (Clientes, Pedidos, Ticket)
        self._criar_painel_metrica(main_frame, "Total de Clientes", self.var_total_clientes)
        
        mes_atual = datetime.now().strftime('%m/%Y')
        self._criar_painel_metrica(main_frame, f"Pedidos no Mês ({mes_atual})", self.var_pedidos_mes)

        self._criar_painel_metrica(main_frame, "Ticket Médio (Mês)", self.var_ticket_medio)

        # Separador
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=20)

        # --- 3. Botões de Ação ---
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill="x", pady=5)
        
        btn_atualizar = ttk.Button(botoes_frame, text="Atualizar Dados", command=self.on_atualizar_callback)
        btn_atualizar.pack(side=tk.LEFT, padx=(0, 10))
        
        # 4. Novo Botão de Análise
        self.btn_analisar = ttk.Button(botoes_frame, text="Analisar Últimos Pedidos (IA)", command=self.on_analisar_callback)
        self.btn_analisar.pack(side=tk.LEFT)

        # --- 5. Nova Área de Resultado da IA ---
        analise_frame = ttk.LabelFrame(main_frame, text="Insights da Inteligência Artificial", padding=10)
        analise_frame.pack(fill="both", expand=True, pady=(15, 0))

        # Adiciona Scrollbar
        scrollbar = ttk.Scrollbar(analise_frame, orient=tk.VERTICAL)
        self.txt_resultado_ia = tk.Text(
            analise_frame, 
            wrap=tk.WORD, 
            height=8, 
            font=("Segoe UI", 10),
            yscrollcommand=scrollbar.set,
            bg="#f0f0f0", # Cor de fundo leve
            borderwidth=0,
            relief="flat"
        )
        scrollbar.config(command=self.txt_resultado_ia.yview)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_resultado_ia.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Inicia com texto e desabilitado para edição
        self.set_analise_resultado("Clique no botão 'Analisar Últimos Pedidos (IA)' para gerar insights...")


    def _criar_painel_metrica(self, parent, titulo, variavel):
        # ... (mantenha esta função como estava) ...
        frame = ttk.Frame(parent, padding=15, relief="solid", borderwidth=1)
        frame.pack(fill="x", pady=8, ipady=5)
        
        ttk.Label(frame, text=titulo, style="Dashboard.TLabel").pack()
        
        lbl_valor = ttk.Label(frame, textvariable=variavel, style="Metrica.TLabel")
        lbl_valor.pack(pady=5)

    def set_dados(self, total_clientes, total_pedidos, ticket_medio):
        # ... (mantenha esta função como estava) ...
        self.var_total_clientes.set(f"{total_clientes}")
        self.var_pedidos_mes.set(f"{total_pedidos}")
        self.var_ticket_medio.set(f"R$ {ticket_medio:.2f}")

    # --- 6. Novas Funções para controlar o Text ---
    
    def _limpar_analise(self):
        """Limpa o texto e habilita a edição."""
        self.txt_resultado_ia.config(state=tk.NORMAL, fg="black")
        self.txt_resultado_ia.delete("1.0", tk.END)

    def set_analise_resultado(self, texto: str):
        """Insere o resultado da IA e desabilita a edição."""
        self._limpar_analise()
        self.txt_resultado_ia.insert("1.0", texto)
        self.txt_resultado_ia.config(state=tk.DISABLED) # Impede edição pelo usuário

    def set_analise_carregando(self, mensagem: str):
        """Mostra uma mensagem de carregamento."""
        self._limpar_analise()
        self.txt_resultado_ia.config(fg="grey") # Cor cinza para 'carregando'
        self.txt_resultado_ia.insert("1.0", mensagem)
        self.txt_resultado_ia.config(state=tk.DISABLED)

    def set_analise_erro(self, erro: str):
        """Mostra uma mensagem de erro em vermelho."""
        self._limpar_analise()
        self.txt_resultado_ia.config(fg="#A80000") # Cor vermelha para erro
        self.txt_resultado_ia.insert("1.0", f"ERRO:\n{erro}")
        self.txt_resultado_ia.config(state=tk.DISABLED)