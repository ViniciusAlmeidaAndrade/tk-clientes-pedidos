import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3  # Para tratar erros específicos do DB

# Importações dos nossos módulos
import db
import utils
import models
from views.lista_cliente import ClientesView
from views.form_cliente import FormCliente
# --- ESTA É A LINHA QUE CORRIGE O ERRO ---
from views.form_pedido import FormCliente


class AppController:
    """
    Controlador principal da aplicação.
    Gerencia a janela principal, as abas e a lógica de negócios
    (callbacks que conectam a View ao Model/DB).
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Clientes e Pedidos")
        self.root.geometry("900x600")

        # Centraliza a janela
        self.root.eval('tk::PlaceWindow . center')

        # Inicializa o banco de dados
        try:
            db.inicializar_banco()
            utils.log_info("Aplicação iniciada. Banco de dados inicializado.")
        except Exception as e:
            utils.log_erro("Falha crítica ao inicializar o banco de dados.", e)
            messagebox.showerror("Erro Crítico",
                                 f"Não foi possível iniciar o banco de dados: {e}\nA aplicação será encerrada.")
            self.root.destroy()
            return

        # --- Cria a Estrutura Principal (Abas) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Aba 1: Clientes ---
        # Instancia a View de Clientes e passa os callbacks
        self.clientes_view = ClientesView(
            self.notebook,
            on_novo=self._on_novo_cliente,
            on_editar=self._on_editar_cliente,
            on_excluir=self._on_excluir_cliente,
            on_buscar=self._on_buscar_cliente
        )
        self.notebook.add(self.clientes_view, text="Clientes")

        # --- Aba 2: Pedidos ---
        # Como não temos um 'pedidos_view.py' complexo, criamos a
        # visualização de pedidos aqui mesmo.
        self.pedidos_frame = self._criar_aba_pedidos(self.notebook)
        self.notebook.add(self.pedidos_frame, text="Pedidos")

        # --- Carregamento Inicial ---
        self.recarregar_lista_clientes()
        self.recarregar_lista_pedidos()

    def _criar_aba_pedidos(self, parent):
        """Cria o conteúdo da aba de Pedidos."""
        frame = ttk.Frame(parent)

        # Botão
        btn_frame = ttk.Frame(frame, padding=10)
        btn_frame.pack(side=tk.TOP, fill=tk.X)
        btn_novo = ttk.Button(btn_frame, text="Novo Pedido", command=self._on_novo_pedido)
        btn_novo.pack(side=tk.LEFT)

        # Treeview (Lista de Pedidos)
        tree_frame = ttk.Frame(frame, padding=(10, 0, 10, 10))
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        colunas = ("id", "data", "cliente", "total")
        self.pedidos_tree = ttk.Treeview(tree_frame, columns=colunas, show="headings")

        self.pedidos_tree.heading("id", text="ID Pedido")
        self.pedidos_tree.heading("data", text="Data")
        self.pedidos_tree.heading("cliente", text="Cliente")
        self.pedidos_tree.heading("total", text="Total (R$)")

        self.pedidos_tree.column("id", width=80, stretch=False, anchor=tk.CENTER)
        self.pedidos_tree.column("data", width=120, stretch=False)
        self.pedidos_tree.column("cliente", width=300, stretch=True)
        self.pedidos_tree.column("total", width=120, stretch=False, anchor=tk.E)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.pedidos_tree.yview)
        self.pedidos_tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pedidos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        return frame

    # =================================================================
    # --- LÓGICA DE CLIENTES (CALLBACKS) ---
    # =================================================================

    def recarregar_lista_clientes(self, termo_busca=None):
        """
        Busca clientes no banco e atualiza a 'ClientesView'.
        Usa o model 'Cliente' para converter as tuplas.
        """
        utils.log_info(f"Recarregando lista de clientes. Termo: '{termo_busca}'")
        try:
            if termo_busca:
                sql = "SELECT * FROM clientes WHERE nome LIKE ? OR email LIKE ? ORDER BY nome"
                params = (f"%{termo_busca}%", f"%{termo_busca}%")
            else:
                sql = "SELECT * FROM clientes ORDER BY nome"
                params = ()

            tuplas_clientes = db.executar_comando(sql, params)

            # Converte as tuplas do DB em objetos Cliente (do models.py)
            clientes_obj = [models.Cliente.from_tuple(t) for t in tuplas_clientes]

            # Converte os objetos em tuplas para a View
            dados_para_view = [(c.id, c.nome, c.email, c.telefone) for c in clientes_obj]

            # Chama o método público da View
            self.clientes_view.set_lista_clientes(dados_para_view)

        except Exception as e:
            utils.log_erro("Falha ao recarregar lista de clientes.", e)
            messagebox.showerror("Erro de Banco", f"Não foi possível carregar os clientes: {e}")

    def _on_buscar_cliente(self, termo: str):
        """Callback do botão 'Buscar' da ClientesView."""
        self.recarregar_lista_clientes(termo)

    def _on_novo_cliente(self):
        """Callback do botão 'Novo' da ClientesView."""
        utils.log_info("Abrindo formulário de novo cliente.")
        # Abre o formulário modal
        # Passamos os callbacks que o formulário deve chamar
        FormCliente(
            self.root,
            on_save_callback=self._salvar_cliente_cb,
            on_cancel_callback=self._cancelar_form_cb
        )

    def _on_editar_cliente(self, cliente_id: int):
        """Callback do botão 'Editar' da ClientesView."""
        utils.log_info(f"Abrindo formulário para editar cliente ID: {cliente_id}")
        try:
            # 1. Buscar os dados atuais do cliente no DB
            tupla = db.executar_comando("SELECT * FROM clientes WHERE id=?", (cliente_id,))
            if not tupla:
                messagebox.showerror("Erro", "Cliente não encontrado.", parent=self.root)
                return

            # 2. Converter a tupla em objeto (models.py)
            cliente_obj = models.Cliente.from_tuple(tupla[0])

            # 3. Converter o objeto em dicionário para o formulário
            dados_cliente_dict = {
                "id": cliente_obj.id,
                "nome": cliente_obj.nome,
                "email": cliente_obj.email,
                "telefone": cliente_obj.telefone
            }

            # 4. Abrir o formulário com os dados
            FormCliente(
                self.root,
                on_save_callback=self._salvar_cliente_cb,
                on_cancel_callback=self._cancelar_form_cb,
                cliente_data=dados_cliente_dict
            )
        except Exception as e:
            utils.log_erro(f"Falha ao carregar cliente ID {cliente_id} para edição.", e)
            messagebox.showerror("Erro", f"Não foi possível carregar os dados do cliente: {e}")

    def _on_excluir_cliente(self, cliente_id: int):
        """Callback do botão 'Excluir' da ClientesView."""
        utils.log_info(f"Tentativa de exclusão do cliente ID: {cliente_id}")
        try:
            # Tenta excluir
            db.executar_comando("DELETE FROM clientes WHERE id=?", (cliente_id,))

            # Se bem-sucedido:
            utils.log_info(f"Cliente ID: {cliente_id} excluído com sucesso.")
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.", parent=self.root)
            self.recarregar_lista_clientes()

        except sqlite3.Error as e:
            # Erro de integridade (FOREIGN KEY) é o mais comum
            if "FOREIGN KEY" in str(e):
                utils.log_erro(f"Falha ao excluir cliente ID {cliente_id} (Foreign Key).", e)
                messagebox.showerror(
                    "Erro de Exclusão",
                    "Não é possível excluir este cliente, pois ele já possui pedidos cadastrados.\n\n"
                    "Dica: Exclua os pedidos deste cliente primeiro.",
                    parent=self.root
                )
            else:
                utils.log_erro(f"Falha ao excluir cliente ID {cliente_id}.", e)
                messagebox.showerror("Erro de Banco", f"Falha ao excluir cliente: {e}", parent=self.root)

    def _salvar_cliente_cb(self, dados_cliente: dict):
        """
        Callback que o 'FormCliente' chama ao clicar em 'Salvar'.
        Recebe um dicionário com os dados validados.
        """
        try:
            # Converte o dicionário em um objeto Cliente (models.py)
            cliente_obj = models.Cliente(**dados_cliente)

            if cliente_obj.id:
                # --- UPDATE (Edição) ---
                utils.log_info(f"Atualizando cliente ID: {cliente_obj.id}")
                sql = "UPDATE clientes SET nome=?, email=?, telefone=? WHERE id=?"
                params = (cliente_obj.nome, cliente_obj.email, cliente_obj.telefone, cliente_obj.id)
                msg_sucesso = "Cliente atualizado com sucesso!"
            else:
                # --- INSERT (Novo) ---
                utils.log_info("Salvando novo cliente.")
                sql = "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)"
                params = (cliente_obj.nome, cliente_obj.email, cliente_obj.telefone)
                msg_sucesso = "Cliente salvo com sucesso!"

            db.executar_comando(sql, params)

            messagebox.showinfo("Sucesso", msg_sucesso, parent=self.root)
            self.recarregar_lista_clientes()

        except sqlite3.Error as e:
            utils.log_erro("Falha ao salvar cliente no banco.", e)
            messagebox.showerror("Erro no Banco", f"Não foi possível salvar o cliente: {e}", parent=self.root)

    def _cancelar_form_cb(self):
        """Callback que o 'FormCliente' chama ao fechar/cancelar."""
        utils.log_info("Formulário de cliente fechado sem salvar.")

    # =================================================================
    # --- LÓGICA DE PEDIDOS (CALLBACKS) ---
    # =================================================================

    def recarregar_lista_pedidos(self):
        """Busca pedidos (com JOIN) e atualiza o Treeview de pedidos."""
        utils.log_info("Recarregando lista de pedidos.")
        try:
            # SQL com JOIN para pegar o nome do cliente
            sql = """
            SELECT p.id, p.data, c.nome, p.total
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            ORDER BY p.data DESC, p.id DESC
            """

            lista_pedidos = db.executar_comando(sql)

            # Limpa a árvore
            for i in self.pedidos_tree.get_children():
                self.pedidos_tree.delete(i)

            # Insere os novos dados
            for item in lista_pedidos:
                # Formata o total para R$
                total_formatado = f"{item[3]:.2f}"
                dados_view = (item[0], item[1], item[2], total_formatado)
                self.pedidos_tree.insert("", tk.END, values=dados_view)

        except Exception as e:
            utils.log_erro("Falha ao recarregar lista de pedidos.", e)
            messagebox.showerror("Erro de Banco", f"Não foi possível carregar os pedidos: {e}")

    def _on_novo_pedido(self):
        """Callback do botão 'Novo Pedido'."""
        utils.log_info("Abrindo formulário de novo pedido.")
        try:
            # 1. Precisamos da lista de clientes para o Combobox
            tuplas_clientes = db.executar_comando("SELECT id, nome FROM clientes ORDER BY nome")

            if not tuplas_clientes:
                messagebox.showwarning(
                    "Atenção",
                    "Não é possível criar um pedido pois não há clientes cadastrados.\n\n"
                    "Por favor, cadastre um cliente primeiro.",
                    parent=self.root
                )
                self.notebook.select(self.clientes_view)  # Muda para a aba de clientes
                return

            # 2. Abrir o formulário de pedido
            FormCliente(
                self.root,
                lista_clientes=tuplas_clientes,
                on_save_success_callback=self._on_pedido_salvo_cb
            )

        except Exception as e:
            utils.log_erro("Falha ao preparar formulário de novo pedido.", e)
            messagebox.showerror("Erro", f"Não foi possível abrir o formulário: {e}")

    def _on_pedido_salvo_cb(self):
        """
        Callback que o 'FormPedido' chama após salvar com sucesso.
        O formulário já fez a transação do DB, só precisamos atualizar a lista.
        """
        utils.log_info("Callback de pedido salvo recebido. Atualizando listas.")
        self.recarregar_lista_pedidos()
        # (Opcional) Podemos ter que recarregar clientes se houver lógica de exclusão
        # self.recarregar_lista_clientes()


# =================================================================
# --- PONTO DE ENTRADA DA APLICAÇÃO ---
# =================================================================

if __name__ == "__main__":
    try:
        root = tk.Tk()

        # Define um tema 'clam' ou 'default' para melhor aparência
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            style.theme_use('default')  # Fallback

        app = AppController(root)
        root.mainloop()
    except Exception as e:
        utils.log_erro("Erro fatal na aplicação.", e)
        # Tenta mostrar um messagebox se o tkinter ainda funcionar
        try:
            messagebox.showerror("Erro Fatal", f"Ocorreu um erro inesperado: {e}\nConsulte os logs.")
        except:
            pass