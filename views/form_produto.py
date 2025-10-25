import tkinter as tk
from tkinter import ttk, messagebox


class FormProduto(tk.Toplevel):
    """
    Janela Toplevel para cadastro ou edição de produtos.
    """

    def __init__(self, parent, on_save_callback, produto_data=None):
        super().__init__(parent)

        self.on_save_callback = on_save_callback
        self.nome_var = tk.StringVar()
        self.preco_var = tk.DoubleVar()
        self.produto_id = None

        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        if produto_data:
            self.title("Editar Produto")
            self.produto_id = produto_data.get('id')
            self.nome_var.set(produto_data.get('nome', ''))
            self.preco_var.set(produto_data.get('preco', 0.0))
        else:
            self.title("Novo Produto")

        self._criar_widgets()
        parent.wait_window(self)

    def _criar_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Nome:*").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_nome = ttk.Entry(main_frame, textvariable=self.nome_var, width=40)
        self.entry_nome.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(main_frame, text="Preço (R$):*").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_preco = ttk.Entry(main_frame, textvariable=self.preco_var, width=20)
        self.entry_preco.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="e", pady=10)

        btn_salvar = ttk.Button(btn_frame, text="Salvar", command=self._on_save)
        btn_salvar.pack(side=tk.RIGHT, padx=5)
        btn_cancelar = ttk.Button(btn_frame, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side=tk.RIGHT)

        self.entry_nome.focus_set()

    def _validar_dados(self):
        nome = self.nome_var.get().strip()
        if not nome:
            messagebox.showerror("Erro de Validação", "O campo 'Nome' é obrigatório.", parent=self)
            return None

        try:
            preco = self.preco_var.get()
            if preco < 0:
                messagebox.showerror("Erro de Validação", "O preço não pode ser negativo.", parent=self)
                return None
        except tk.TclError:
            messagebox.showerror("Erro de Validação", "O preço deve ser um número válido.", parent=self)
            return None

        return {
            "id": self.produto_id,
            "nome": nome,
            "preco": preco
        }

    def _on_save(self):
        dados_validados = self._validar_dados()
        if dados_validados:
            self.on_save_callback(dados_validados)
            self.destroy()