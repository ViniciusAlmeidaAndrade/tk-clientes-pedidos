import tkinter as tk
from tkinter import ttk, messagebox


class ClientesView(ttk.Frame):
    """
    Frame para exibir e gerenciar a lista de clientes.
    """

    def __init__(self, parent, on_novo, on_editar, on_excluir, on_buscar):
        """
        Inicializa o Frame da view de clientes.

        Args:
            parent: O widget pai (ex: um Notebook).
            on_novo: Função callback a ser chamada ao clicar em "Novo".
            on_editar: Callback (recebe id) para "Editar".
            on_excluir: Callback (recebe id) para "Excluir".
            on_buscar: Callback (recebe termo) para "Buscar".
        """
        super().__init__(parent)

        # Armazena os callbacks
        self.on_novo_callback = on_novo
        self.on_editar_callback = on_editar
        self.on_excluir_callback = on_excluir
        self.on_buscar_callback = on_buscar

        # Variável de controle para a busca
        self.busca_var = tk.StringVar()

        # Variável para o status
        self.status_var = tk.StringVar()
        self.status_var.set("0 clientes carregados.")

        # Cria os widgets
        self._criar_widgets()

    def _criar_widgets(self):
        """Cria e posiciona os widgets no frame."""

        # --- Frame Superior (Busca e Botões) ---
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))

        lbl_busca = ttk.Label(top_frame, text="Buscar:")
        lbl_busca.pack(side=tk.LEFT, padx=(0, 5))

        entry_busca = ttk.Entry(top_frame, textvariable=self.busca_var, width=30)
        entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_buscar = ttk.Button(top_frame, text="Buscar", command=self._on_buscar)
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # --- Frame de Botões (Ações) ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        btn_novo = ttk.Button(btn_frame, text="Novo", command=self.on_novo_callback)
        btn_novo.pack(side=tk.LEFT)

        btn_editar = ttk.Button(btn_frame, text="Editar", command=self._on_editar)
        btn_editar.pack(side=tk.LEFT, padx=5)

        btn_excluir = ttk.Button(btn_frame, text="Excluir", command=self._on_excluir)
        btn_excluir.pack(side=tk.LEFT)

        # --- Frame do Treeview (Lista de Clientes) ---
        tree_frame = ttk.Frame(self, padding=(10, 0, 10, 5))
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Colunas do Treeview
        colunas = ("id", "nome", "email", "telefone")

        self.tree = ttk.Treeview(tree_frame, columns=colunas, show="headings")

        # Configura os Cabeçalhos
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("email", text="E-mail")
        self.tree.heading("telefone", text="Telefone")

        # Configura as Colunas
        self.tree.column("id", width=50, stretch=False, anchor=tk.CENTER)
        self.tree.column("nome", width=250, stretch=True)
        self.tree.column("email", width=250, stretch=True)
        self.tree.column("telefone", width=150, stretch=False)

        # Barra de Rolagem
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Status Bar ---
        status_label = ttk.Label(self, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN)
        status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(5, 10))

    def _get_dados_selecionados(self):
        """
        Retorna o ID e o Nome do item selecionado no Treeview.
        Retorna (None, None) se nada estiver selecionado.
        """
        item_selecionado = self.tree.focus()  # Obtém o item focado
        if not item_selecionado:
            return None, None

        dados = self.tree.item(item_selecionado)
        valores = dados.get('values')

        if not valores:
            return None, None

        # Retorna o ID (índice 0) e o Nome (índice 1)
        return valores[0], valores[1]

    def _on_buscar(self):
        """Chama o callback de busca com o termo digitado."""
        termo = self.busca_var.get()
        self.on_buscar_callback(termo)

    def _on_editar(self):
        """Chama o callback de edição passando o ID selecionado."""
        cliente_id, _ = self._get_dados_selecionados()

        if cliente_id is None:
            messagebox.showwarning("Atenção", "Selecione um cliente para editar.", parent=self)
            return

        self.on_editar_callback(cliente_id)

    def _on_excluir(self):
        """Pede confirmação e chama o callback de exclusão."""
        cliente_id, cliente_nome = self._get_dados_selecionados()

        if cliente_id is None:
            messagebox.showwarning("Atenção", "Selecione um cliente para excluir.", parent=self)
            return

        # Pergunta de confirmação
        confirmado = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o cliente:\n\nID: {cliente_id}\nNome: {cliente_nome}",
            icon='warning',
            parent=self
        )

        if confirmado:
            self.on_excluir_callback(cliente_id)

    # --- Métodos Públicos ---

    def set_lista_clientes(self, dados: list):
        """
        Limpa o Treeview e insere uma nova lista de dados.

        Args:
            dados (list): Uma lista de tuplas/listas, onde cada item
                          corresponde às colunas (id, nome, email, telefone).
        """
        # Limpa a árvore
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Insere os novos dados
        for item in dados:
            self.tree.insert("", tk.END, values=item)

        # Atualiza o status
        count = len(dados)
        self.status_var.set(f"{count} cliente(s) encontrado(s).")


# --- Bloco de Teste ---
if __name__ == "__main__":

    # --- Funções de Callback Falsas (Mock) ---
    def on_novo_teste():
        print("CALLBACK: Novo Cliente")
        messagebox.showinfo("Callback", "Função 'Novo Cliente' chamada!")


    def on_editar_teste(cliente_id):
        print(f"CALLBACK: Editar Cliente ID: {cliente_id}")
        messagebox.showinfo("Callback", f"Função 'Editar Cliente' chamada com ID: {cliente_id}")


    def on_excluir_teste(cliente_id):
        print(f"CALLBACK: Excluir Cliente ID: {cliente_id}")
        messagebox.showinfo("Callback", f"Função 'Excluir Cliente' chamada com ID: {cliente_id}")
        # Simula a recarga (removendo o item da lista mock)
        dados_mock.pop(0)
        view.set_lista_clientes(dados_mock)


    def on_buscar_teste(termo):
        print(f"CALLBACK: Buscar Cliente com termo: '{termo}'")
        if not termo:
            view.set_lista_clientes(dados_mock_originais)
            return

        # Simula uma busca
        resultados = [d for d in dados_mock_originais if termo.lower() in d[1].lower() or termo.lower() in d[2].lower()]
        view.set_lista_clientes(resultados)


    # --- Dados Falsos (Mock) ---
    dados_mock_originais = [
        (1, "Ana Beatriz", "ana.b@email.com", "11988776655"),
        (2, "Carlos Eduardo", "carlos.edu@email.com", "21911223344"),
        (3, "Daniela Costa", "dani.costa@email.com", "31955667788"),
        (4, "Fernando Lima", "fernando@email.com", "41988990011"),
    ]
    dados_mock = list(dados_mock_originais)  # Cópia para o teste de exclusão

    # --- Janela Principal de Teste ---
    root = tk.Tk()
    root.title("Teste da View de Clientes")
    root.geometry("800x500")

    # Centraliza a janela
    root.eval('tk::PlaceWindow . center')

    # Instancia a View
    view = ClientesView(
        root,
        on_novo=on_novo_teste,
        on_editar=on_editar_teste,
        on_excluir=on_excluir_teste,
        on_buscar=on_buscar_teste
    )
    view.pack(fill=tk.BOTH, expand=True)

    # Carrega os dados iniciais
    view.set_lista_clientes(dados_mock)

    root.mainloop()