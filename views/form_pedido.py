import tkinter as tk
from tkinter import ttk, messagebox
import re


class FormCliente(tk.Toplevel):
    """
    Janela Toplevel para cadastro ou edição de clientes.
    Implementa verificação de dados não salvos ao fechar.
    """

    def __init__(self, parent, on_save_callback, on_cancel_callback, cliente_data=None):
        super().__init__(parent)

        self.on_save_callback = on_save_callback
        self.on_cancel_callback = on_cancel_callback

        self.nome_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.telefone_var = tk.StringVar()

        self.cliente_id = None
        self.dados_salvos = False  # Flag para rastrear se o save foi bem-sucedido

        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        if cliente_data:
            self.title("Editar Cliente")
            self.cliente_id = cliente_data.get('id')
            self.nome_var.set(cliente_data.get('nome', ''))
            self.email_var.set(cliente_data.get('email', ''))
            self.telefone_var.set(cliente_data.get('telefone', ''))
        else:
            self.title("Novo Cliente")

        # --- Armazena dados originais para verificar alterações ---
        self.dados_originais = (
            self.nome_var.get(),
            self.email_var.get(),
            self.telefone_var.get()
        )

        self._criar_widgets()

        # --- Intercepta o botão "X" da janela ---
        self.protocol("WM_DELETE_WINDOW", self._on_fechar_janela)

        parent.wait_window(self)

    def _criar_widgets(self):
        """Cria e posiciona os widgets no Toplevel."""

        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        lbl_nome = ttk.Label(main_frame, text="Nome:*")
        lbl_nome.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_nome = ttk.Entry(main_frame, textvariable=self.nome_var, width=40)
        self.entry_nome.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        lbl_email = ttk.Label(main_frame, text="E-mail:")
        lbl_email.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_email = ttk.Entry(main_frame, textvariable=self.email_var, width=40)
        self.entry_email.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        lbl_telefone = ttk.Label(main_frame, text="Telefone:")
        lbl_telefone.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_telefone = ttk.Entry(main_frame, textvariable=self.telefone_var, width=40)
        self.entry_telefone.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky="e", pady=10)
        btn_salvar = ttk.Button(btn_frame, text="Salvar", command=self._on_save)
        btn_salvar.pack(side=tk.RIGHT, padx=5)
        btn_cancelar = ttk.Button(btn_frame, text="Cancelar", command=self._on_cancel)
        btn_cancelar.pack(side=tk.RIGHT)

        self.entry_nome.focus_set()

    def _dados_foram_alterados(self) -> bool:
        """Verifica se os dados atuais são diferentes dos originais."""
        atuais = (
            self.nome_var.get(),
            self.email_var.get(),
            self.telefone_var.get()
        )
        return atuais != self.dados_originais

    def _validar_dados(self):
        """Valida os dados e retorna um dicionário ou None."""
        erros = []

        nome = self.nome_var.get().strip()
        email = self.email_var.get().strip()
        telefone = self.telefone_var.get().strip()

        if not nome:
            erros.append("O campo 'Nome' é obrigatório.")

        if email and ("@" not in email or "." not in email):
            erros.append("Formato de e-mail inválido (deve conter '@' e '.').")

        telefone_limpo = re.sub(r'\D', '', telefone)
        if telefone and not (8 <= len(telefone_limpo) <= 15):
            erros.append(f"O telefone deve conter entre 8 e 15 dígitos (você digitou {len(telefone_limpo)}).")

        if erros:
            # Mensagem de erro mais amigável
            messagebox.showerror(
                "Dados Inválidos",
                "Por favor, corrija os seguintes erros:\n\n" + "\n".join(erros),
                parent=self
            )
            return None

        return {
            "id": self.cliente_id,
            "nome": nome,
            "email": email,
            "telefone": telefone_limpo
        }

    def _on_save(self):
        """Salva os dados após validação."""
        dados_validados = self._validar_dados()

        if dados_validados:
            self.on_save_callback(dados_validados)
            self.dados_salvos = True  # Marca que foi salvo
            self.destroy()

    def _on_cancel(self):
        """Cancela e fecha, verificando se há dados não salvos."""
        self._on_fechar_janela(force_cancel=True)

    def _on_fechar_janela(self, force_cancel=False):
        """
        Chamado ao fechar a janela (pelo 'X' ou 'Cancelar').
        Verifica se há dados alterados.
        """
        # Se os dados foram salvos, ou se não foram alterados, fecha direto.
        if self.dados_salvos or not self._dados_foram_alterados():
            if force_cancel:
                self.on_cancel_callback()
            self.destroy()
            return

        # Se foi forçado (botão Cancelar) ou se há dados alterados
        if force_cancel:
            msg = "Você tem alterações não salvas. Deseja descartá-las e cancelar?"
            titulo = "Descartar Alterações?"
            # Pergunta Sim (Descartar) / Não (Voltar)
            resposta = messagebox.askyesno(titulo, msg, parent=self)
            if resposta:  # Sim, descartar
                self.on_cancel_callback()
                self.destroy()
            # Se 'Não', apenas retorna e mantém a janela aberta

        else:  # Clicou no "X"
            msg = "Você tem alterações não salvas. Deseja salvá-las antes de fechar?"
            titulo = "Salvar Alterações?"
            # Pergunta Sim (Salvar) / Não (Fechar sem salvar) / Cancelar
            resposta = messagebox.askyesnocancel(titulo, msg, parent=self)

            if resposta is True:  # Sim, Salvar
                self._on_save()
                # A janela só fechará se o _on_save() for bem-sucedido

            elif resposta is False:  # Não, Fechar sem salvar
                self.on_cancel_callback()
                self.destroy()