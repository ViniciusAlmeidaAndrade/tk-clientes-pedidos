import tkinter as tk
from tkinter import ttk, messagebox
import re


class FormCliente(tk.Toplevel):
    """
    Janela Toplevel para cadastro ou edição de clientes.
    """

    def __init__(self, parent, on_save_callback, on_cancel_callback, cliente_data=None):
        """
        Inicializa o formulário.

        Args:
            parent: A janela pai (geralmente a janela principal do app).
            on_save_callback: Função a ser chamada ao clicar em Salvar.
                              Recebe um dicionário com os dados validados.
            on_cancel_callback: Função a ser chamada ao clicar em Cancelar.
            cliente_data (dict, optional): Dados do cliente para edição.
                                           Se None, é um novo cadastro.
        """
        super().__init__(parent)

        # Armazena os callbacks
        self.on_save_callback = on_save_callback
        self.on_cancel_callback = on_cancel_callback

        # Variáveis para os campos de entrada
        self.nome_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.telefone_var = tk.StringVar()

        # Armazena o ID do cliente (se estiver editando)
        self.cliente_id = None

        # Configuração da janela
        self.transient(parent)  # Mantém a janela no topo
        self.grab_set()  # Torna a janela modal (bloqueia a principal)
        self.resizable(False, False)

        # Preenche os campos se for edição
        if cliente_data:
            self.title("Editar Cliente")
            self.cliente_id = cliente_data.get('id')
            self.nome_var.set(cliente_data.get('nome', ''))
            self.email_var.set(cliente_data.get('email', ''))
            self.telefone_var.set(cliente_data.get('telefone', ''))
        else:
            self.title("Novo Cliente")

        # Cria os widgets do formulário
        self._criar_widgets()

        # Espera até que esta janela seja fechada
        parent.wait_window(self)

    def _criar_widgets(self):
        """Cria e posiciona os widgets no Toplevel."""

        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Campo Nome ---
        lbl_nome = ttk.Label(main_frame, text="Nome:*")
        lbl_nome.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.entry_nome = ttk.Entry(main_frame, textvariable=self.nome_var, width=40)
        self.entry_nome.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # --- Campo E-mail ---
        lbl_email = ttk.Label(main_frame, text="E-mail:")
        lbl_email.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.entry_email = ttk.Entry(main_frame, textvariable=self.email_var, width=40)
        self.entry_email.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # --- Campo Telefone ---
        lbl_telefone = ttk.Label(main_frame, text="Telefone:")
        lbl_telefone.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.entry_telefone = ttk.Entry(main_frame, textvariable=self.telefone_var, width=40)
        self.entry_telefone.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # --- Frame de Botões ---
        btn_frame = ttk.Frame(main_frame)
        # columnspan=2 para centralizar ou alinhar os botões
        btn_frame.grid(row=3, column=0, columnspan=2, sticky="e", pady=10)

        btn_salvar = ttk.Button(btn_frame, text="Salvar", command=self._on_save)
        btn_salvar.pack(side=tk.RIGHT, padx=5)

        btn_cancelar = ttk.Button(btn_frame, text="Cancelar", command=self._on_cancel)
        btn_cancelar.pack(side=tk.RIGHT)

        # Foca no primeiro campo de entrada
        self.entry_nome.focus_set()

    def _validar_dados(self):
        """
        Valida os dados dos campos de entrada.
        Exibe uma messagebox em caso de erro.
        Retorna um dicionário com dados validados ou None se houver erro.
        """
        erros = []

        nome = self.nome_var.get().strip()
        email = self.email_var.get().strip()
        telefone = self.telefone_var.get().strip()

        # 1. Validação do Nome (Obrigatório)
        if not nome:
            erros.append("O campo 'Nome' é obrigatório.")

        # 2. Validação do E-mail (Formato simples)
        #    Verifica se tem "@" e "." (se algo foi digitado)
        if email and ("@" not in email or "." not in email):
            erros.append("Formato de e-mail inválido (deve conter '@' e '.').")

        # 3. Validação do Telefone (8-15 dígitos)
        #    Remove caracteres não numéricos (espaços, '()', '-')
        telefone_limpo = re.sub(r'\D', '', telefone)

        # Valida apenas se o campo telefone foi preenchido
        if telefone and not (8 <= len(telefone_limpo) <= 15):
            erros.append(f"O telefone deve conter entre 8 e 15 dígitos (você digitou {len(telefone_limpo)}).")

        if erros:
            # Exibe a primeira mensagem de erro
            messagebox.showerror("Erro de Validação", "\n".join(erros), parent=self)
            return None

        # Retorna os dados limpos e validados
        return {
            "id": self.cliente_id,  # Pode ser None (novo) ou um int (edição)
            "nome": nome,
            "email": email,
            "telefone": telefone_limpo  # Salva apenas os dígitos
        }

    def _on_save(self):
        """
        Chamado ao clicar em 'Salvar'. Valida os dados e chama o callback.
        """
        dados_validados = self._validar_dados()

        if dados_validados:
            # Chama o callback de sucesso passado na inicialização
            self.on_save_callback(dados_validados)
            # Fecha a janela
            self.destroy()

    def _on_cancel(self):
        """
        Chamado ao clicar em 'Cancelar'. Chama o callback e fecha a janela.
        """
        # Chama o callback de cancelamento
        self.on_cancel_callback()
        # Fecha a janela
        self.destroy()


# --- Bloco de Teste ---
if __name__ == "__main__":
    # Funções de callback Falsas (mock) para teste
    def callback_salvar_teste(dados):
        print("--- SALVAR ---")
        print("Dados recebidos pelo callback:")
        print(dados)


    def callback_cancelar_teste():
        print("--- CANCELAR ---")
        print("Operação cancelada.")


    # Cria a janela principal (root) apenas para o teste
    root = tk.Tk()
    root.title("Aplicação Principal (Teste)")
    root.geometry("400x300")

    # Centraliza a janela principal
    root.eval('tk::PlaceWindow . center')

    # Dados de exemplo para o modo "Editar"
    cliente_para_editar = {
        "id": 10,
        "nome": "Cliente Exemplo",
        "email": "exemplo@teste.com",
        "telefone": "(11) 98765-4321"
    }


    # Botões na janela principal para lançar o formulário

    def lancar_form_novo():
        print("Abrindo formulário para NOVO cliente...")
        FormCliente(root, callback_salvar_teste, callback_cancelar_teste)


    def lancar_form_editar():
        print("Abrindo formulário para EDITAR cliente...")
        FormCliente(root, callback_salvar_teste, callback_cancelar_teste, cliente_para_editar)


    ttk.Label(root, text="Use os botões para testar o formulário:").pack(pady=10)

    btn_novo = ttk.Button(root, text="Abrir Formulário (Novo)", command=lancar_form_novo)
    btn_novo.pack(pady=10, padx=20, fill=tk.X)

    btn_editar = ttk.Button(root, text="Abrir Formulário (Editar)", command=lancar_form_editar)
    btn_editar.pack(pady=10, padx=20, fill=tk.X)

    root.mainloop()