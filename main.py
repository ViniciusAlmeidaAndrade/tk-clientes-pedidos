import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3  # Para tratar erros específicos do DB

# Importações dos nossos módulos
import db
import utils
import models
from views.lista_cliente import ClientesView
from views.form_cliente import FormCliente
from views.form_pedido import FormPedido
# NOVOS IMPORTS PARA PRODUTOS
from views.lista_produto import ProdutosView
from views.form_produto import FormProduto


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

        self.root.eval('tk::PlaceWindow . center')

        try:
            db.inicializar_banco()
            utils.log_info("Aplicação iniciada. Banco de dados inicializado.")
        except Exception as e:
            utils.log_erro("Falha crítica ao inicializar o banco de dados.", e)
            messagebox.showerror("Erro Crítico",
                                 f"Não foi possível iniciar o banco de dados: {e}\nA aplicação será encerrada.")
            self.root.destroy()
            return

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Aba 1: Clientes ---
        self.clientes_view = ClientesView(
            self.notebook,
            on_novo=self._on_novo_cliente,
            on_editar=self._on_editar_cliente,
            on_excluir=self._on_excluir_cliente,
            on_buscar=self._on_buscar_cliente
        )
        self.notebook.add(self.clientes_view, text="Clientes")

        # --- Aba 2: Produtos (NOVA ABA) ---
        self.produtos_view = ProdutosView(
            self.notebook,
            on_novo=self._on_novo_produto,
            on_editar=self._on_editar_produto,
            on_excluir=self._on_excluir_produto,
            on_buscar=self._on_buscar_produto
        )
        self.notebook.add(self.produtos_view, text="Produtos")

        # --- Aba 3: Pedidos ---
        self.pedidos_frame = self._criar_aba_pedidos(self.notebook)
        self.notebook.add(self.pedidos_frame, text="Pedidos")

        # --- Carregamento Inicial ---
        self.recarregar_lista_clientes()
        self.recarregar_lista_produtos()  # Carrega os produtos
        self.recarregar_lista_pedidos()

    def _criar_aba_pedidos(self, parent):
        frame = ttk.Frame(parent)

        btn_frame = ttk.Frame(frame, padding=10)
        btn_frame.pack(side=tk.TOP, fill=tk.X)
        btn_novo = ttk.Button(btn_frame, text="Novo Pedido", command=self._on_novo_pedido)
        btn_novo.pack(side=tk.LEFT)

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
        utils.log_info(f"Recarregando lista de clientes. Termo: '{termo_busca}'")
        try:
            if termo_busca:
                sql = "SELECT * FROM clientes WHERE nome LIKE ? OR email LIKE ? ORDER BY nome"
                params = (f"%{termo_busca}%", f"%{termo_busca}%")
            else:
                sql = "SELECT * FROM clientes ORDER BY nome"
                params = ()

            tuplas_clientes = db.executar_comando(sql, params)
            clientes_obj = [models.Cliente.from_tuple(t) for t in tuplas_clientes]
            dados_para_view = [(c.id, c.nome, c.email, c.telefone) for c in clientes_obj]
            self.clientes_view.set_lista_clientes(dados_para_view)
        except Exception as e:
            utils.log_erro("Falha ao recarregar lista de clientes.", e)
            messagebox.showerror("Erro de Banco", f"Não foi possível carregar os clientes: {e}")

    def _on_buscar_cliente(self, termo: str):
        self.recarregar_lista_clientes(termo)

    def _on_novo_cliente(self):
        FormCliente(self.root, on_save_callback=self._salvar_cliente_cb, on_cancel_callback=self._cancelar_form_cb)

    def _on_editar_cliente(self, cliente_id: int):
        try:
            tupla = db.executar_comando("SELECT * FROM clientes WHERE id=?", (cliente_id,))
            if not tupla:
                messagebox.showerror("Erro", "Cliente não encontrado.", parent=self.root)
                return
            cliente_obj = models.Cliente.from_tuple(tupla[0])
            dados_cliente_dict = {"id": cliente_obj.id, "nome": cliente_obj.nome, "email": cliente_obj.email,
                                  "telefone": cliente_obj.telefone}
            FormCliente(self.root, on_save_callback=self._salvar_cliente_cb, on_cancel_callback=self._cancelar_form_cb,
                        cliente_data=dados_cliente_dict)
        except Exception as e:
            utils.log_erro(f"Falha ao carregar cliente ID {cliente_id} para edição.", e)
            messagebox.showerror("Erro", f"Não foi possível carregar os dados do cliente: {e}")

    def _on_excluir_cliente(self, cliente_id: int):
        try:
            db.executar_comando("DELETE FROM clientes WHERE id=?", (cliente_id,))
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.", parent=self.root)
            self.recarregar_lista_clientes()
        except sqlite3.Error as e:
            if "FOREIGN KEY" in str(e):
                messagebox.showerror("Erro de Exclusão",
                                     "Não é possível excluir este cliente, pois ele já possui pedidos cadastrados.",
                                     parent=self.root)
            else:
                messagebox.showerror("Erro de Banco", f"Falha ao excluir cliente: {e}", parent=self.root)

    def _salvar_cliente_cb(self, dados_cliente: dict):
        try:
            if dados_cliente.get('id'):
                sql = "UPDATE clientes SET nome=?, email=?, telefone=? WHERE id=?"
                params = (dados_cliente['nome'], dados_cliente['email'], dados_cliente['telefone'], dados_cliente['id'])
                msg_sucesso = "Cliente atualizado com sucesso!"
            else:
                sql = "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)"
                params = (dados_cliente['nome'], dados_cliente['email'], dados_cliente['telefone'])
                msg_sucesso = "Cliente salvo com sucesso!"

            db.executar_comando(sql, params)
            messagebox.showinfo("Sucesso", msg_sucesso, parent=self.root)
            self.recarregar_lista_clientes()
        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco", f"Não foi possível salvar o cliente: {e}", parent=self.root)

    def _cancelar_form_cb(self):
        utils.log_info("Formulário de cliente fechado sem salvar.")

    # =================================================================
    # --- LÓGICA DE PRODUTOS (CALLBACKS) ---
    # =================================================================

    def recarregar_lista_produtos(self, termo_busca=None):
        utils.log_info(f"Recarregando lista de produtos. Termo: '{termo_busca}'")
        try:
            if termo_busca:
                sql = "SELECT * FROM produtos WHERE nome LIKE ? ORDER BY nome"
                params = (f"%{termo_busca}%",)
            else:
                sql = "SELECT * FROM produtos ORDER BY nome"
                params = ()

            lista_produtos = db.executar_comando(sql, params)
            self.produtos_view.set_lista_produtos(lista_produtos)
        except Exception as e:
            utils.log_erro("Falha ao recarregar lista de produtos.", e)
            messagebox.showerror("Erro de Banco", f"Não foi possível carregar os produtos: {e}")

    def _on_buscar_produto(self, termo: str):
        self.recarregar_lista_produtos(termo)

    def _on_novo_produto(self):
        FormProduto(self.root, on_save_callback=self._salvar_produto_cb)

    def _on_editar_produto(self, produto_id: int):
        try:
            tupla = db.executar_comando("SELECT * FROM produtos WHERE id=?", (produto_id,))
            if not tupla:
                messagebox.showerror("Erro", "Produto não encontrado.", parent=self.root)
                return
            produto_data = {"id": tupla[0][0], "nome": tupla[0][1], "preco": tupla[0][2]}
            FormProduto(self.root, on_save_callback=self._salvar_produto_cb, produto_data=produto_data)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar os dados do produto: {e}")

    def _on_excluir_produto(self, produto_id: int):
        try:
            db.executar_comando("DELETE FROM produtos WHERE id=?", (produto_id,))
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso.", parent=self.root)
            self.recarregar_lista_produtos()
        except Exception as e:
            if "FOREIGN KEY" in str(e):
                messagebox.showerror("Erro de Exclusão",
                                     "Não é possível excluir este produto, pois ele já está associado a um ou mais pedidos.",
                                     parent=self.root)
            else:
                messagebox.showerror("Erro de Banco", f"Falha ao excluir produto: {e}", parent=self.root)

    def _salvar_produto_cb(self, dados_produto: dict):
        try:
            if dados_produto.get('id'):
                sql = "UPDATE produtos SET nome=?, preco=? WHERE id=?"
                params = (dados_produto['nome'], dados_produto['preco'], dados_produto['id'])
                msg_sucesso = "Produto atualizado com sucesso!"
            else:
                sql = "INSERT INTO produtos (nome, preco) VALUES (?, ?)"
                params = (dados_produto['nome'], dados_produto['preco'])
                msg_sucesso = "Produto salvo com sucesso!"

            db.executar_comando(sql, params)
            messagebox.showinfo("Sucesso", msg_sucesso, parent=self.root)
            self.recarregar_lista_produtos()
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Erro ao Salvar",
                                     f"Já existe um produto com o nome '{dados_produto['nome']}'.\n\nPor favor, escolha um nome diferente.",
                                     parent=self.root)
            else:
                messagebox.showerror("Erro no Banco", f"Não foi possível salvar o produto: {e}", parent=self.root)

    # =================================================================
    # --- LÓGICA DE PEDIDOS (CALLBACKS) ---
    # =================================================================

    def recarregar_lista_pedidos(self):
        utils.log_info("Recarregando lista de pedidos.")
        try:
            sql = """
            SELECT p.id, p.data, c.nome, p.total
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            ORDER BY p.data DESC, p.id DESC
            """
            lista_pedidos = db.executar_comando(sql)
            for i in self.pedidos_tree.get_children():
                self.pedidos_tree.delete(i)
            for item in lista_pedidos:
                total_formatado = f"{item[3]:.2f}"
                dados_view = (item[0], item[1], item[2], total_formatado)
                self.pedidos_tree.insert("", tk.END, values=dados_view)
        except Exception as e:
            utils.log_erro("Falha ao recarregar lista de pedidos.", e)
            messagebox.showerror("Erro de Banco", f"Não foi possível carregar os pedidos: {e}")

    def _on_novo_pedido(self):
        utils.log_info("Abrindo formulário de novo pedido.")
        try:
            # 1. Verifica se existem clientes
            tuplas_clientes = db.executar_comando("SELECT id, nome FROM clientes ORDER BY nome")
            if not tuplas_clientes:
                messagebox.showwarning("Atenção", "Cadastre um cliente antes de criar um pedido.", parent=self.root)
                self.notebook.select(self.clientes_view)
                return

            # 2. VERIFICA SE EXISTEM PRODUTOS (NOVA VALIDAÇÃO)
            tuplas_produtos = db.executar_comando("SELECT id, nome, preco FROM produtos ORDER BY nome")
            if not tuplas_produtos:
                messagebox.showwarning("Atenção", "Cadastre um produto antes de criar um pedido.", parent=self.root)
                self.notebook.select(self.produtos_view)
                return

            # 3. Abrir o formulário de pedido, passando ambas as listas
            FormPedido(
                self.root,
                lista_clientes=tuplas_clientes,
                lista_produtos=tuplas_produtos,  # Passa a lista de produtos
                on_save_success_callback=self._on_pedido_salvo_cb
            )
        except Exception as e:
            utils.log_erro("Falha ao preparar formulário de novo pedido.", e)
            messagebox.showerror("Erro", f"Não foi possível abrir o formulário: {e}")

    def _on_pedido_salvo_cb(self):
        utils.log_info("Callback de pedido salvo recebido. Atualizando listas.")
        self.recarregar_lista_pedidos()


# =================================================================
# --- PONTO DE ENTRADA DA APLICAÇÃO ---
# =================================================================

if __name__ == "__main__":
    try:
        root = tk.Tk()
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            style.theme_use('default')

        app = AppController(root)
        root.mainloop()
    except Exception as e:
        utils.log_erro("Erro fatal na aplicação.", e)
        try:
            messagebox.showerror("Erro Fatal", f"Ocorreu um erro inesperado: {e}\nConsulte os logs.")
        except:
            pass