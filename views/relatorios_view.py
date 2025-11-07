# Em views/relatorios_view.py

import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry  # Importa o seletor de data


class RelatoriosView(ttk.Frame):
    """
    Frame que exibe a interface de filtros e listagem para relatórios.
    """

    def __init__(self, parent, on_filtrar_callback, on_exportar_csv_callback, on_exportar_pdf_callback):
        super().__init__(parent, padding=10)

        # Callbacks
        self.on_filtrar_callback = on_filtrar_callback
        self.on_exportar_csv_callback = on_exportar_csv_callback
        self.on_exportar_pdf_callback = on_exportar_pdf_callback

        # Armazena a lista de clientes (id, nome)
        self.clientes_list = []

        # --- 1. Frame de Filtros ---
        filtro_frame = ttk.LabelFrame(self, text="Filtros do Relatório", padding=10)
        filtro_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self._criar_filtros(filtro_frame)

        # --- 2. Frame da Treeview ---
        tree_frame = ttk.Frame(self, padding=(0, 10, 0, 0))
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._criar_treeview(tree_frame)

        # --- 3. Frame de Botões de Exportação ---
        botoes_frame = ttk.Frame(self, padding=(0, 10, 0, 0))
        botoes_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self._criar_botoes_exportar(botoes_frame)

    def _criar_filtros(self, parent):
        """Cria os widgets de filtro (Datas e Cliente)."""
        parent.columnconfigure((1, 3, 5), weight=1)

        # Data Inicial
        ttk.Label(parent, text="Data Inicial:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.entry_data_inicio = DateEntry(parent, width=12, background='darkblue',
                                           foreground='white', borderwidth=2,
                                           date_pattern='dd/MM/yyyy', locale='pt_BR')
        self.entry_data_inicio.grid(row=0, column=1, padx=5, sticky=tk.EW)

        # Data Final
        ttk.Label(parent, text="Data Final:").grid(row=0, column=2, padx=(10, 5), sticky=tk.W)
        self.entry_data_fim = DateEntry(parent, width=12, background='darkblue',
                                        foreground='white', borderwidth=2,
                                        date_pattern='dd/MM/yyyy', locale='pt_BR')
        self.entry_data_fim.grid(row=0, column=3, padx=5, sticky=tk.EW)

        # Cliente (Combobox)
        ttk.Label(parent, text="Cliente:").grid(row=0, column=4, padx=(10, 5), sticky=tk.W)
        self.combo_cliente = ttk.Combobox(parent, state="readonly", values=["Todos"])
        self.combo_cliente.current(0)
        self.combo_cliente.grid(row=0, column=5, padx=5, sticky=tk.EW)

        # Botão Filtrar
        self.btn_filtrar = ttk.Button(parent, text="Filtrar", command=self.on_filtrar_callback)
        self.btn_filtrar.grid(row=0, column=6, padx=(10, 0), sticky=tk.E)

    def _criar_treeview(self, parent):
        """Cria a Treeview para exibir os pedidos filtrados."""
        colunas = ("id", "data", "cliente", "itens", "total")
        self.pedidos_tree = ttk.Treeview(parent, columns=colunas, show="headings")

        self.pedidos_tree.heading("id", text="ID Pedido")
        self.pedidos_tree.heading("data", text="Data")
        self.pedidos_tree.heading("cliente", text="Cliente")
        self.pedidos_tree.heading("itens", text="Nº Itens")
        self.pedidos_tree.heading("total", text="Total (R$)")

        self.pedidos_tree.column("id", width=80, stretch=False, anchor=tk.CENTER)
        self.pedidos_tree.column("data", width=120, stretch=False)
        self.pedidos_tree.column("cliente", width=300, stretch=True)
        self.pedidos_tree.column("itens", width=80, stretch=False, anchor=tk.CENTER)
        self.pedidos_tree.column("total", width=120, stretch=False, anchor=tk.E)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.pedidos_tree.yview)
        self.pedidos_tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pedidos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _criar_botoes_exportar(self, parent):
        """Cria os botões de exportação."""
        ttk.Label(parent, text="Exportar resultados para:").pack(side=tk.LEFT, padx=(0, 10))

        self.btn_export_csv = ttk.Button(parent, text="Exportar CSV",
                                         command=self.on_exportar_csv_callback)
        self.btn_export_csv.pack(side=tk.LEFT, padx=5)

        self.btn_export_pdf = ttk.Button(parent, text="Exportar PDF",
                                         command=self.on_exportar_pdf_callback)
        self.btn_export_pdf.pack(side=tk.LEFT, padx=5)

    def set_clientes_combobox(self, clientes: list):
        """Recebe a lista de clientes [ (id, nome), ... ] e popula o combobox."""
        self.clientes_list = clientes
        nomes = ["Todos"] + [c[1] for c in clientes]  # Extrai apenas os nomes
        self.combo_cliente["values"] = nomes
        self.combo_cliente.current(0)  # Define "Todos" como padrão

    def get_filtros(self) -> dict:
        """Retorna os valores dos filtros selecionados."""

        # Converte a data do DateEntry para o formato YYYY-MM-DD
        data_inicio = self.entry_data_inicio.get_date().strftime('%Y-%m-%d')
        data_fim = self.entry_data_fim.get_date().strftime('%Y-%m-%d')

        # Pega o ID do cliente
        cliente_id = None
        idx_selecionado = self.combo_cliente.current()
        if idx_selecionado > 0:  # Se não for "Todos"
            # Pega o cliente da lista (índice - 1, pois "Todos" é o 0)
            cliente_id = self.clientes_list[idx_selecionado - 1][0]

        return {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "cliente_id": cliente_id
        }

    def set_lista_pedidos(self, pedidos: list):
        """Limpa a Treeview e insere a nova lista de pedidos."""
        # Limpa a lista antiga
        for i in self.pedidos_tree.get_children():
            self.pedidos_tree.delete(i)

        # Insere os novos dados
        for item in pedidos:
            # (id, data, cliente, itens, total)
            total_formatado = f"{item[4]:.2f}"
            dados_view = (item[0], item[1], item[2], item[3], total_formatado)
            self.pedidos_tree.insert("", tk.END, values=dados_view)