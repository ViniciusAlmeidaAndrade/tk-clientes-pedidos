import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import sqlite3

try:
    import db
    import utils
except ImportError:
    # Fallback para execução de teste, se necessário
    pass


class _DialogAddItem(tk.Toplevel):
    """
    Diálogo modal privado para adicionar um item ao pedido,
    selecionando de um catálogo de produtos.
    """

    def __init__(self, parent, lista_produtos: list):
        super().__init__(parent)
        self.title("Adicionar Item")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        # Mapeia o nome do produto para seus dados (id, preco)
        # Formato da tupla em lista_produtos: (id, nome, preco)
        self.produtos_map = {p_nome: (p_id, p_preco) for p_id, p_nome, p_preco in lista_produtos}

        self.resultado = None

        # --- Variáveis ---
        self.produto_var = tk.StringVar()
        self.qtd_var = tk.IntVar(value=1)
        self.preco_var = tk.DoubleVar()

        # --- Widgets ---
        frame = ttk.Frame(self, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Produto:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_produto = ttk.Combobox(frame, textvariable=self.produto_var, values=list(self.produtos_map.keys()),
                                          state="readonly", width=38)
        self.combo_produto.grid(row=0, column=1, pady=5)
        self.combo_produto.bind("<<ComboboxSelected>>", self._on_produto_selecionado)

        ttk.Label(frame, text="Quantidade:").grid(row=1, column=0, sticky="w", pady=5)
        entry_qtd = ttk.Entry(frame, textvariable=self.qtd_var, width=10)
        entry_qtd.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(frame, text="Preço Unitário (R$):").grid(row=2, column=0, sticky="w", pady=5)
        entry_preco = ttk.Entry(frame, textvariable=self.preco_var, width=10)
        entry_preco.grid(row=2, column=1, sticky="w", pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky="e", pady=10)

        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)

        self.combo_produto.focus_set()
        parent.wait_window(self)

    def _on_produto_selecionado(self, event=None):
        """Preenche o preço automaticamente ao selecionar um produto."""
        nome_produto = self.produto_var.get()
        if nome_produto in self.produtos_map:
            _, preco = self.produtos_map[nome_produto]
            self.preco_var.set(preco)

    def _on_ok(self):
        nome_produto = self.produto_var.get()
        if not nome_produto:
            messagebox.showerror("Erro", "Selecione um produto.", parent=self)
            return

        try:
            qtd = self.qtd_var.get()
            preco = self.preco_var.get()
        except tk.TclError:
            messagebox.showerror("Erro", "Quantidade e Preço devem ser números válidos.", parent=self)
            return

        if qtd <= 0:
            messagebox.showerror("Erro", "A Quantidade deve ser maior que zero.", parent=self)
            return
        if preco < 0:
            messagebox.showerror("Erro", "O Preço não pode ser negativo.", parent=self)
            return

        produto_id, _ = self.produtos_map[nome_produto]

        self.resultado = {
            "produto_id": produto_id,
            "produto_nome": nome_produto,  # Guardamos o nome para exibir na lista
            "quantidade": qtd,
            "preco_unit": preco
        }
        self.destroy()


class FormPedido(tk.Toplevel):
    """
    Janela Toplevel para criação de um novo pedido.
    """

    def __init__(self, parent, lista_clientes: list, lista_produtos: list, on_save_success_callback):
        super().__init__(parent)
        self.title("Criar Novo Pedido")
        self.geometry("700x500")

        self.transient(parent)
        self.grab_set()

        self.on_save_success_callback = on_save_success_callback
        self.lista_produtos_completa = lista_produtos  # Guardamos para passar ao diálogo

        self.itens_pedido = []
        self.clientes_map = {nome: id for id, nome in lista_clientes}

        self.cliente_var = tk.StringVar()
        self.data_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        self.total_var = tk.StringVar(value="Total: R$ 0.00")

        clientes_nomes = sorted(list(self.clientes_map.keys()))
        if clientes_nomes:
            self.cliente_var.set(clientes_nomes[0])

        self._criar_widgets(clientes_nomes)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        parent.wait_window(self)

    def _criar_widgets(self, clientes_nomes):
        # ... (O layout geral permanece o mesmo) ...
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top_frame, text="Cliente:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_cliente = ttk.Combobox(top_frame, textvariable=self.cliente_var, values=clientes_nomes,
                                          state="readonly", width=40)
        self.combo_cliente.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        top_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(top_frame, text="Data:").grid(row=0, column=2, sticky="w", padx=15, pady=5)
        entry_data = ttk.Entry(top_frame, textvariable=self.data_var, width=12)
        entry_data.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        items_frame = ttk.LabelFrame(self, text="Itens do Pedido", padding="10")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tree_container = ttk.Frame(items_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree_itens = ttk.Treeview(tree_container, columns=("produto", "qtd", "preco_unit", "subtotal"),
                                       show="headings")
        self.tree_itens.heading("produto", text="Produto")
        self.tree_itens.heading("qtd", text="Qtd.")
        self.tree_itens.heading("preco_unit", text="Preço Unit. (R$)")
        self.tree_itens.heading("subtotal", text="Subtotal (R$)")
        self.tree_itens.column("produto", width=250, stretch=True)
        self.tree_itens.column("qtd", width=60, anchor=tk.CENTER, stretch=False)
        self.tree_itens.column("preco_unit", width=120, anchor=tk.E, stretch=False)
        self.tree_itens.column("subtotal", width=120, anchor=tk.E, stretch=False)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree_itens.yview)
        self.tree_itens.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_itens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        item_btn_frame = ttk.Frame(items_frame)
        item_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(item_btn_frame, text="Adicionar Item", command=self._on_add_item).pack(side=tk.LEFT)
        ttk.Button(item_btn_frame, text="Remover Item", command=self._on_remove_item).pack(side=tk.LEFT, padx=5)

        bottom_frame = ttk.Frame(self, padding="10")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        lbl_total = ttk.Label(bottom_frame, textvariable=self.total_var, font=("-weight bold", 12))
        lbl_total.pack(side=tk.LEFT)
        btn_salvar = ttk.Button(bottom_frame, text="Salvar Pedido", command=self._on_save_pedido)
        btn_salvar.pack(side=tk.RIGHT)
        btn_cancelar = ttk.Button(bottom_frame, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side=tk.RIGHT, padx=5)

    def _atualizar_treeview_e_total(self):
        for i in self.tree_itens.get_children():
            self.tree_itens.delete(i)

        total_geral = 0.0
        for item in self.itens_pedido:
            subtotal = item["quantidade"] * item["preco_unit"]
            total_geral += subtotal
            self.tree_itens.insert("", tk.END,
                                   values=(item["produto_nome"], item["quantidade"], f"{item['preco_unit']:.2f}",
                                           f"{subtotal:.2f}"))

        self.total_var.set(f"Total: R$ {total_geral:.2f}")

    def _on_add_item(self):
        """Abre o diálogo para adicionar um novo item, passando a lista de produtos."""
        dialog = _DialogAddItem(self, self.lista_produtos_completa)
        if dialog.resultado:
            self.itens_pedido.append(dialog.resultado)
            self._atualizar_treeview_e_total()

    def _on_remove_item(self):
        selected_iid = self.tree_itens.focus()
        if not selected_iid:
            messagebox.showwarning("Atenção", "Selecione um item para remover.", parent=self)
            return

        item_index = self.tree_itens.index(selected_iid)
        self.itens_pedido.pop(item_index)
        self._atualizar_treeview_e_total()

    def _on_save_pedido(self):
        """Valida e salva o pedido de forma transacional."""
        cliente_nome = self.cliente_var.get()
        data_pedido = self.data_var.get()

        if not all([cliente_nome, data_pedido, self.itens_pedido]):
            messagebox.showerror("Erro de Validação", "Todos os campos são obrigatórios e o pedido deve conter itens.",
                                 parent=self)
            return

        cliente_id = self.clientes_map[cliente_nome]
        total_final = sum(item["quantidade"] * item["preco_unit"] for item in self.itens_pedido)

        conn = None
        try:
            conn = sqlite3.connect(db.DB_FILE)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("BEGIN TRANSACTION;")

            sql_pedido = "INSERT INTO pedidos (cliente_id, data, total) VALUES (?, ?, ?)"
            cursor.execute(sql_pedido, (cliente_id, data_pedido, total_final))
            pedido_id = cursor.lastrowid

            # MODIFICADO: Salva os itens com produto_id
            sql_item = "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unit) VALUES (?, ?, ?, ?)"
            itens_para_db = [(pedido_id, item["produto_id"], item["quantidade"], item["preco_unit"]) for item in
                             self.itens_pedido]
            cursor.executemany(sql_item, itens_para_db)

            conn.commit()
            messagebox.showinfo("Sucesso", f"Pedido Nº {pedido_id} salvo com sucesso!", parent=self)
            self.on_save_success_callback()
            self.destroy()

        except sqlite3.Error as e:
            if conn: conn.rollback()
            utils.log_erro("Falha ao salvar pedido (transação revertida).", e)
            messagebox.showerror("Erro no Banco de Dados", f"Falha ao salvar o pedido:\n{e}", parent=self)
        finally:
            if conn: conn.close()