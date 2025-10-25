import tkinter as tk
from tkinter import ttk, messagebox

class ProdutosView(ttk.Frame):
    """
    Frame para exibir e gerenciar a lista de produtos.
    """
    def __init__(self, parent, on_novo, on_editar, on_excluir, on_buscar):
        super().__init__(parent)

        self.on_novo_callback = on_novo
        self.on_editar_callback = on_editar
        self.on_excluir_callback = on_excluir
        self.on_buscar_callback = on_buscar

        self.busca_var = tk.StringVar()
        self.status_var = tk.StringVar(value="0 produtos carregados.")
        self._criar_widgets()

    def _criar_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(top_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        entry_busca = ttk.Entry(top_frame, textvariable=self.busca_var, width=30)
        entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(top_frame, text="Buscar", command=self._on_buscar).pack(side=tk.LEFT, padx=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Novo", command=self.on_novo_callback).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Editar", command=self._on_editar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self._on_excluir).pack(side=tk.LEFT)

        tree_frame = ttk.Frame(self, padding=(10, 0, 10, 5))
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        colunas = ("id", "nome", "preco")
        self.tree = ttk.Treeview(tree_frame, columns=colunas, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome do Produto")
        self.tree.heading("preco", text="Preço (R$)")

        self.tree.column("id", width=50, stretch=False, anchor=tk.CENTER)
        self.tree.column("nome", width=350, stretch=True)
        self.tree.column("preco", width=120, stretch=False, anchor=tk.E)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(self, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(5, 10))

    def _get_dados_selecionados(self):
        item_selecionado = self.tree.focus()
        if not item_selecionado:
            return None, None
        valores = self.tree.item(item_selecionado).get('values')
        return (valores[0], valores[1]) if valores else (None, None)

    def _on_buscar(self):
        self.on_buscar_callback(self.busca_var.get())

    def _on_editar(self):
        produto_id, _ = self._get_dados_selecionados()
        if produto_id is None:
            messagebox.showwarning("Atenção", "Selecione um produto para editar.", parent=self)
            return
        self.on_editar_callback(produto_id)

    def _on_excluir(self):
        produto_id, produto_nome = self._get_dados_selecionados()
        if produto_id is None:
            messagebox.showwarning("Atenção", "Selecione um produto para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o produto: {produto_nome}?", icon='warning', parent=self):
            self.on_excluir_callback(produto_id)

    def set_lista_produtos(self, dados: list):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for item in dados:
            preco_formatado = f"{item[2]:.2f}"
            self.tree.insert("", tk.END, values=(item[0], item[1], preco_formatado))
        self.status_var.set(f"{len(dados)} produto(s) encontrado(s).")