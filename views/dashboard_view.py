# Em views/dashboard_view.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class DashboardView(ttk.Frame):
    """
    Frame que exibe os principais indicadores (KPIs) da aplicação.
    """

    def __init__(self, parent, on_atualizar_callback):
        super().__init__(parent, padding=20)

        # Callback para o AppController
        self.on_atualizar_callback = on_atualizar_callback

        # --- Variáveis de Controle ---
        self.var_total_clientes = tk.StringVar(value="...")
        self.var_pedidos_mes = tk.StringVar(value="...")
        self.var_ticket_medio = tk.StringVar(value="...")

        # --- Estilos ---
        style = ttk.Style(self)
        style.configure("Dashboard.TLabel", font=("Segoe UI", 12))
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Metrica.TLabel", font=("Segoe UI", 24, "bold"), foreground="#00529B")
        style.configure("TButton", font=("Segoe UI", 12))

        # --- Layout ---
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Visão Geral", style="Header.TLabel").pack(pady=(0, 25))

        # 1. Total de Clientes
        self._criar_painel_metrica(main_frame, "Total de Clientes", self.var_total_clientes)

        # 2. Pedidos no Mês
        mes_atual = datetime.now().strftime('%m/%Y')
        self._criar_painel_metrica(main_frame, f"Pedidos no Mês ({mes_atual})", self.var_pedidos_mes)

        # 3. Ticket Médio
        self._criar_painel_metrica(main_frame, "Ticket Médio (Mês)", self.var_ticket_medio)

        # Separador
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=25)

        # Botão Atualizar
        btn_atualizar = ttk.Button(main_frame, text="Atualizar Dados", command=self.on_atualizar_callback)
        btn_atualizar.pack(pady=10)

    def _criar_painel_metrica(self, parent, titulo, variavel):
        """Helper para criar os painéis de exibição."""
        # Usamos 'borderwidth' e 'relief' para criar as "caixas"
        frame = ttk.Frame(parent, padding=15, relief="solid", borderwidth=1)
        frame.pack(fill="x", pady=8, ipady=5)

        ttk.Label(frame, text=titulo, style="Dashboard.TLabel").pack()

        lbl_valor = ttk.Label(frame, textvariable=variavel, style="Metrica.TLabel")
        lbl_valor.pack(pady=5)

    def set_dados(self, total_clientes, total_pedidos, ticket_medio):
        """
        Método público chamado pelo AppController para atualizar os valores.
        """
        self.var_total_clientes.set(f"{total_clientes}")
        self.var_pedidos_mes.set(f"{total_pedidos}")
        self.var_ticket_medio.set(f"R$ {ticket_medio:.2f}")