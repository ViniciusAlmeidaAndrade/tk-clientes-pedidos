import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import sys
import subprocess
import csv
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch

# Importações dos nossos módulos
import db
import utils
import models
import styles
# IMPORTS DA PASTA 'CORE'
from core import database
from core import analysis
# IMPORTS DAS VIEWS
from views.lista_cliente import ClientesView
from views.form_cliente import FormCliente
from views.form_pedido import FormPedido
from views.lista_produto import ProdutosView
from views.form_produto import FormProduto
from views.dashboard_view import DashboardView
from views.relatorios_view import RelatoriosView
from views.historico_view import HistoricoView


class AppController:
    """
    Controlador principal da aplicação.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Clientes e Pedidos")
        self.root.geometry("900x600")
        self.root.eval('tk::PlaceWindow . center')
        
        self.style = ttk.Style(self.root)
        self.theme_is_light = True
        try:
            styles.apply_light_theme(self.style)
        except tk.TclError:
            self.style.theme_use('default')

        try:
            utils.setup_logging()
            db.inicializar_banco()
            utils.log_info("Aplicação iniciada. Banco de dados inicializado.")
        except Exception as e:
            utils.log_erro("Falha crítica ao inicializar a aplicação.", e)
            messagebox.showerror("Erro Crítico",
                                 f"Não foi possível iniciar a aplicação: {e}\nA aplicação será encerrada.")
            self.root.destroy()
            return

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Criação das Abas ---
        self.dashboard_view = DashboardView(
            self.notebook,
            on_atualizar_callback=self.recarregar_dashboard,
            on_analisar_callback=self._on_analisar_pedidos
        )
        self.notebook.add(self.dashboard_view, text="Dashboard")

        self.clientes_view = ClientesView(
            self.notebook,
            on_novo=self._on_novo_cliente,
            on_editar=self._on_editar_cliente,
            on_excluir=self._on_excluir_cliente,
            on_buscar=self._on_buscar_cliente
        )
        self.notebook.add(self.clientes_view, text="Clientes")

        self.produtos_view = ProdutosView(
            self.notebook,
            on_novo=self._on_novo_produto,
            on_editar=self._on_editar_produto,
            on_excluir=self._on_excluir_produto,
            on_buscar=self._on_buscar_produto
        )
        self.notebook.add(self.produtos_view, text="Produtos")

        self.pedidos_frame = self._criar_aba_pedidos(self.notebook)
        self.notebook.add(self.pedidos_frame, text="Pedidos")
        
        self.relatorios_view = RelatoriosView(
            self.notebook,
            on_filtrar_callback=self._on_filtrar_relatorio,
            on_exportar_csv_callback=self._on_exportar_csv,
            on_exportar_pdf_callback=self._on_exportar_pdf
        )
        self.notebook.add(self.relatorios_view, text="Relatórios")
        
        self.historico_view = HistoricoView(
            self.notebook,
            on_recarregar_callback=self.recarregar_historico, # <-- Consistente
            on_limpar_callback=self._on_limpar_historico
        )
        self.notebook.add(self.historico_view, text="Histórico")

        # --- Criação do Menu e Protocolo de Fechamento ---
        self._create_menu_bar()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_app)

        # --- Carregamento Inicial ---
        self.recarregar_dashboard()
        self.recarregar_lista_clientes()
        self.recarregar_lista_produtos()
        self.recarregar_lista_pedidos()
        self._carregar_dados_relatorios()
        self.recarregar_historico() # <-- Consistente

    # =================================================================
    # --- Menu, Tema e Fechamento ---
    # =================================================================

    def _create_menu_bar(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Sair", command=self._on_close_app)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)

        nav_menu = tk.Menu(menu_bar, tearoff=0)
        nav_menu.add_command(
            label="Dashboard / IA", 
            command=lambda: self.notebook.select(self.dashboard_view)
        )
        nav_menu.add_command(
            label="Clientes", 
            command=lambda: self.notebook.select(self.clientes_view)
        )
        nav_menu.add_command(
            label="Produtos", 
            command=lambda: self.notebook.select(self.produtos_view)
        )
        nav_menu.add_command(
            label="Pedidos", 
            command=lambda: self.notebook.select(self.pedidos_frame)
        )
        nav_menu.add_command(
            label="Relatórios", 
            command=lambda: self.notebook.select(self.relatorios_view)
        )
        nav_menu.add_command(
            label="Histórico", 
            command=lambda: self.notebook.select(self.historico_view)
        )
        menu_bar.add_cascade(label="Navegar", menu=nav_menu)

        options_menu = tk.Menu(menu_bar, tearoff=0)
        options_menu.add_command(
            label="Alternar Tema (Claro/Escuro)", 
            command=self._toggle_theme
        )
        menu_bar.add_cascade(label="Opções", menu=options_menu)

        self.root.config(menu=menu_bar)

    def _toggle_theme(self):
        self.theme_is_light = not self.theme_is_light
        try:
            if self.theme_is_light:
                styles.apply_light_theme(self.style)
                utils.log_info("Tema alterado para: Claro")
            else:
                styles.apply_dark_theme(self.style)
                utils.log_info("Tema alterado para: Escuro")
        except tk.TclError as e:
            utils.log_erro("Falha ao aplicar tema.", e)
            messagebox.showwarning("Erro de Tema", 
                                   "Não foi possível aplicar o tema. Verifique se 'clam' está disponível.")

    def _on_close_app(self):
        if messagebox.askyesno("Sair", "Tem certeza que deseja sair?", parent=self.root):
            utils.log_info("Aplicação encerrada pelo usuário.")
            self.root.destroy()
            
    # --- Nova Função (Correção do Bug do Combobox) ---
    def _recarregar_combobox_clientes_relatorio(self):
        """Recarrega a lista de clientes no combobox da aba de relatórios."""
        try:
            utils.log_info("Recarregando combobox de clientes (Relatórios).")
            clientes_list = database.fetch_clientes_para_combobox()
            self.relatorios_view.set_clientes_combobox(clientes_list)
        except Exception as e:
            utils.log_erro("Falha ao recarregar combobox de clientes.", e)

    # =================================================================
    # --- LÓGICA DAS ABAS (EXISTENTE) ---
    # =================================================================

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

    # --- Lógica do Dashboard ---
    def recarregar_dashboard(self):
        utils.log_info("Recarregando dados do dashboard.")
        try:
            total_clientes, total_pedidos, ticket_medio = database.fetch_dados_dashboard()
            self.dashboard_view.set_dados(total_clientes, total_pedidos, ticket_medio)
            messagebox.showinfo(
                "Atualização Concluída",
                "Os dados do dashboard foram atualizados com sucesso!",
                parent=self.root
            )
        except Exception as e:
            utils.log_erro("Falha ao recarregar o dashboard.", e)
            messagebox.showerror(
                "Erro de Atualização",
                f"Ocorreu um erro ao buscar os dados do dashboard:\n{e}",
                parent=self.root
            )

    def _on_analisar_pedidos(self):
        try:
            utils.log_info("Botão 'Analisar Pedidos' clicado.")
            self.dashboard_view.btn_analisar.config(state=tk.DISABLED)
            self.dashboard_view.set_analise_carregando(
                "Analisando... Conectando ao servidor de IA e buscando dados.\nPor favor, aguarde..."
            )
            analysis.analisar_pedidos_com_ia(
                self._on_analise_sucesso_cb, 
                self._on_analise_erro_cb
            )
        except Exception as e:
            utils.log_erro("Erro ao disparar análise de IA.", e)
            messagebox.showerror("Erro", f"Não foi possível iniciar a análise: {e}")
            self.dashboard_view.btn_analisar.config(state=tk.NORMAL)

    def _on_analise_sucesso_cb(self, resultado_ia: str):
        utils.log_info("Callback de sucesso da IA recebido.")
        self.root.after(0, self._update_ui_analise_sucesso, resultado_ia)

    def _update_ui_analise_sucesso(self, resultado_ia: str):
        self.dashboard_view.set_analise_resultado(resultado_ia)
        self.dashboard_view.btn_analisar.config(state=tk.NORMAL)

    def _on_analise_erro_cb(self, erro_msg: str):
        utils.log_erro(f"Callback de erro da IA recebido: {erro_msg}")
        self.root.after(0, self._update_ui_analise_erro, erro_msg)

    def _update_ui_analise_erro(self, erro_msg: str):
        self.dashboard_view.set_analise_erro(erro_msg)
        self.dashboard_view.btn_analisar.config(state=tk.NORMAL)
        messagebox.showwarning("Erro na Análise", erro_msg, parent=self.root)

    # --- Lógica de Clientes ---
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
            utils.log_acao(f"Ação: Iniciando edição do cliente ID {cliente_id} ({cliente_obj.nome}).")
            FormCliente(self.root, on_save_callback=self._salvar_cliente_cb, on_cancel_callback=self._cancelar_form_cb,
                        cliente_data=dados_cliente_dict)
        except Exception as e:
            utils.log_erro(f"Falha ao carregar cliente ID {cliente_id} para edição.", e)
            messagebox.showerror("Erro", f"Não foi possível carregar os dados do cliente: {e}")

    def _on_excluir_cliente(self, cliente_id: int):
        try:
            nome_cliente_tupla = db.executar_comando("SELECT nome FROM clientes WHERE id=?", (cliente_id,))
            if not nome_cliente_tupla:
                raise Exception("Cliente não encontrado para exclusão.")
            nome_cliente = nome_cliente_tupla[0][0]
            if not messagebox.askyesno("Confirmar Exclusão", 
                                       f"Tem certeza que deseja excluir o cliente:\n\n{nome_cliente} (ID: {cliente_id})?", 
                                       parent=self.root):
                utils.log_acao(f"Ação: Exclusão do cliente ID {cliente_id} CANCELADA pelo usuário.")
                return
            db.executar_comando("DELETE FROM clientes WHERE id=?", (cliente_id,))
            utils.log_acao(f"Cliente EXCLUÍDO: ID {cliente_id} - {nome_cliente}")
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.", parent=self.root)
            self.recarregar_lista_clientes()
            self.recarregar_historico()
            self._recarregar_combobox_clientes_relatorio() # <-- Correção do Bug
        except sqlite3.Error as e:
            if "FOREIGN KEY" in str(e):
                utils.log_erro(f"Falha ao excluir cliente ID {cliente_id} (Violação de FK).", e)
                messagebox.showerror("Erro de Exclusão", "Não é possível excluir este cliente, pois ele já possui pedidos cadastrados.", parent=self.root)
            else:
                utils.log_erro(f"Falha ao excluir cliente ID {cliente_id} (Erro de DB).", e)
                messagebox.showerror("Erro de Banco", f"Falha ao excluir cliente: {e}", parent=self.root)
        except Exception as e:
            utils.log_erro(f"Falha genérica ao excluir cliente ID {cliente_id}.", e)
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}", parent=self.root)

    def _salvar_cliente_cb(self, dados_cliente: dict):
        try:
            if dados_cliente.get('id'):
                sql = "UPDATE clientes SET nome=?, email=?, telefone=? WHERE id=?"
                params = (dados_cliente['nome'], dados_cliente['email'], dados_cliente['telefone'], dados_cliente['id'])
                msg_sucesso = "Cliente atualizado com sucesso!"
                utils.log_acao(f"Cliente ATUALIZADO: ID {dados_cliente['id']} - {dados_cliente['nome']}")
            else:
                sql = "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)"
                params = (dados_cliente['nome'], dados_cliente['email'], dados_cliente['telefone'])
                msg_sucesso = "Cliente salvo com sucesso!"
                utils.log_acao(f"Cliente CRIADO: {dados_cliente['nome']}")
            db.executar_comando(sql, params)
            messagebox.showinfo("Sucesso", msg_sucesso, parent=self.root)
            self.recarregar_lista_clientes()
            self.recarregar_historico()
            self._recarregar_combobox_clientes_relatorio() # <-- Correção do Bug
        except sqlite3.Error as e:
            utils.log_erro(f"Falha ao salvar cliente: {dados_cliente['nome']}", e)
            messagebox.showerror("Erro no Banco", f"Não foi possível salvar o cliente: {e}", parent=self.root)

    def _cancelar_form_cb(self):
        utils.log_info("Formulário de cliente fechado sem salvar.")

    # --- Lógica de Produtos ---
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
            utils.log_acao(f"Ação: Iniciando edição do produto ID {produto_id} ({produto_data['nome']}).")
            FormProduto(self.root, on_save_callback=self._salvar_produto_cb, produto_data=produto_data)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar os dados do produto: {e}")

    def _on_excluir_produto(self, produto_id: int):
        try:
            nome_produto_tupla = db.executar_comando("SELECT nome FROM produtos WHERE id=?", (produto_id,))
            nome_produto = nome_produto_tupla[0][0] if nome_produto_tupla else "Produto Desconhecido"
            if not messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o produto:\n\n{nome_produto}?", parent=self.root):
                utils.log_acao(f"Ação: Exclusão do produto ID {produto_id} CANCELADA.")
                return
            db.executar_comando("DELETE FROM produtos WHERE id=?", (produto_id,))
            utils.log_acao(f"Produto EXCLUÍDO: ID {produto_id} - {nome_produto}")
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso.", parent=self.root)
            self.recarregar_lista_produtos()
            self.recarregar_historico()
        except Exception as e:
            if "FOREIGN KEY" in str(e):
                utils.log_erro(f"Falha ao excluir produto ID {produto_id} (Violação de FK).", e)
                messagebox.showerror("Erro de Exclusão", "Não é possível excluir este produto, pois ele já está associado a um ou mais pedidos.", parent=self.root)
            else:
                utils.log_erro(f"Falha ao excluir produto ID {produto_id}.", e)
                messagebox.showerror("Erro de Banco", f"Falha ao excluir produto: {e}", parent=self.root)

    def _salvar_produto_cb(self, dados_produto: dict):
        try:
            if dados_produto.get('id'):
                sql = "UPDATE produtos SET nome=?, preco=? WHERE id=?"
                params = (dados_produto['nome'], dados_produto['preco'], dados_produto['id'])
                msg_sucesso = "Produto atualizado com sucesso!"
                utils.log_acao(f"Produto ATUALIZADO: ID {dados_produto['id']} - {dados_produto['nome']}")
            else:
                sql = "INSERT INTO produtos (nome, preco) VALUES (?, ?)"
                params = (dados_produto['nome'], dados_produto['preco'])
                msg_sucesso = "Produto salvo com sucesso!"
                utils.log_acao(f"Produto CRIADO: {dados_produto['nome']}")
            db.executar_comando(sql, params)
            messagebox.showinfo("Sucesso", msg_sucesso, parent=self.root)
            self.recarregar_lista_produtos()
            self.recarregar_historico()
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Erro ao Salvar", f"Já existe um produto com o nome '{dados_produto['nome']}'.\n\nPor favor, escolha um nome diferente.", parent=self.root)
            else:
                messagebox.showerror("Erro no Banco", f"Não foi possível salvar o produto: {e}", parent=self.root)

    # --- Lógica de Pedidos ---
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
            tuplas_clientes = database.fetch_clientes_para_combobox()
            if not tuplas_clientes:
                messagebox.showwarning("Atenção", "Cadastre um cliente antes de criar um pedido.", parent=self.root)
                self.notebook.select(self.clientes_view)
                return
            tuplas_produtos = db.executar_comando("SELECT id, nome, preco FROM produtos ORDER BY nome")
            if not tuplas_produtos:
                messagebox.showwarning("Atenção", "Cadastre um produto antes de criar um pedido.", parent=self.root)
                self.notebook.select(self.produtos_view)
                return
            FormPedido(
                self.root,
                lista_clientes=tuplas_clientes,
                lista_produtos=tuplas_produtos,
                on_save_success_callback=self._on_pedido_salvo_cb
            )
        except Exception as e:
            utils.log_erro("Falha ao preparar formulário de novo pedido.", e)
            messagebox.showerror("Erro", f"Não foi possível abrir o formulário: {e}")

    def _on_pedido_salvo_cb(self):
        utils.log_info("Callback de pedido salvo recebido. Atualizando listas.")
        utils.log_acao("Novo PEDIDO SALVO.")
        self.recarregar_lista_pedidos()
        self.recarregar_historico()
        
    # --- Lógica de Relatórios ---
    def _carregar_dados_relatorios(self):
        try:
            self._recarregar_combobox_clientes_relatorio() # <-- Chamada corrigida
            self._on_filtrar_relatorio()
        except Exception as e:
            utils.log_erro("Falha ao carregar dados iniciais dos relatórios.", e)
            messagebox.showerror("Erro", f"Não foi possível carregar a aba de relatórios: {e}", parent=self.root)

    def _on_filtrar_relatorio(self):
        try:
            utils.log_info("Filtrando relatório de pedidos.")
            filtros = self.relatorios_view.get_filtros()
            pedidos = database.fetch_relatorio_pedidos(
                filtros["data_inicio"],
                filtros["data_fim"],
                filtros["cliente_id"]
            )
            self.relatorios_view.set_lista_pedidos(pedidos)
        except Exception as e:
            utils.log_erro("Falha ao filtrar relatório.", e)
            messagebox.showerror("Erro ao Filtrar", f"Ocorreu um erro ao buscar os dados:\n{e}", parent=self.root)

    def _on_exportar_csv(self):
        filepath = "relatorio_pedidos.csv"
        utils.log_info(f"Exportando relatório para CSV: {filepath}")
        try:
            filtros = self.relatorios_view.get_filtros()
            dados = database.fetch_relatorio_pedidos(
                filtros["data_inicio"],
                filtros["data_fim"],
                filtros["cliente_id"]
            )
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID Pedido', 'Data', 'Cliente', 'Nº Itens', 'Total (R$)'])
                for row in dados:
                    row_formatada = [row[0], row[1], row[2], row[3], f"{row[4]:.2f}"]
                    writer.writerow(row_formatada)
            messagebox.showinfo("Exportação Concluída", f"Relatório salvo com sucesso em:\n{os.path.abspath(filepath)}", parent=self.root)
            self._abrir_arquivo(filepath)
        except Exception as e:
            utils.log_erro(f"Falha ao exportar CSV: {filepath}", e)
            messagebox.showerror("Erro ao Exportar", f"Não foi possível gerar o CSV:\n{e}", parent=self.root)

    def _on_exportar_pdf(self):
        filepath = "relatorio_pedidos.pdf"
        utils.log_info(f"Exportando relatório para PDF: {filepath}")
        try:
            filtros = self.relatorios_view.get_filtros()
            dados = database.fetch_relatorio_pedidos(
                filtros["data_inicio"],
                filtros["data_fim"],
                filtros["cliente_id"]
            )
            doc = SimpleDocTemplate(filepath, pagesize=landscape(A4))
            elements = []
            dados_tabela = [['ID', 'Data', 'Cliente', 'Nº Itens', 'Total (R$)']]
            for row in dados:
                dados_tabela.append([row[0], row[1], row[2], row[3], f"R$ {row[4]:.2f}"])
            t = Table(dados_tabela, colWidths=[0.8*inch, 1.2*inch, None, 0.8*inch, 1.2*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (4, 1), (4, -1), 'RIGHT'), 
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),
                ('PADDINGLEFT', (2, 1), (2, -1), 5), 
                ('PADDINGRIGHT', (4, 1), (4, -1), 5),
            ]))
            elements.append(t)
            doc.build(elements)
            messagebox.showinfo("Exportação Concluída", f"Relatório salvo com sucesso em:\n{os.path.abspath(filepath)}", parent=self.root)
            self._abrir_arquivo(filepath)
        except Exception as e:
            utils.log_erro(f"Falha ao exportar PDF: {filepath}", e)
            messagebox.showerror("Erro ao Exportar", f"Não foi possível gerar o PDF:\n{e}", parent=self.root)

    def _abrir_arquivo(self, filepath):
        try:
            path = os.path.abspath(filepath)
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin": # macOS
                subprocess.run(["open", path])
            else: # linux
                subprocess.run(["xdg-open", path])
            utils.log_info(f"Solicitando abertura do arquivo: {path}")
        except Exception as e:
            utils.log_erro(f"Não foi possível abrir o arquivo {path}", e)
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo automaticamente:\n{e}", parent=self.root)

    # --- Lógica de Histórico ---
    def recarregar_historico(self): # <-- Nome consistente
        """
        Lê o arquivo de log e atualiza a view de histórico.
        """
        utils.log_info("Recarregando view de histórico.")
        try:
            texto_log = utils.ler_log()
            self.historico_view.set_historico(texto_log)
        except Exception as e:
            utils.log_erro("Falha ao carregar histórico na view.", e)
            self.historico_view.set_historico(f"ERRO AO LER HISTÓRICO:\n{e}")

    def _on_limpar_historico(self):
        utils.log_info("Usuário solicitou limpeza do histórico.")
        if messagebox.askyesno("Confirmar Limpeza",
                               "Tem certeza que deseja apagar permanentemente todo o histórico de ações?\n\nEsta ação não pode ser desfeita.",
                               parent=self.root,
                               icon='warning'):
            try:
                utils.log_acao("Ação: Limpeza do histórico SOLICITADA.")
                utils.limpar_log()
                utils.log_info("Histórico limpo com sucesso.")
                self.recarregar_historico() 
            except Exception as e:
                utils.log_erro("Falha ao tentar limpar o log.", e)
                messagebox.showerror("Erro", f"Não foi possível limpar o histórico:\n{e}", parent=self.root)
        else:
            utils.log_info("Limpeza do histórico CANCELADA pelo usuário.")

    # =================================================================
    # --- PONTO DE ENTRADA DA APLICAÇÃO ---
    # =================================================================

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AppController(root)
        root.mainloop()
    except Exception as e:
        try:
            utils.log_erro("Erro fatal na aplicação (nível __main__).", e)
        except:
            print(f"ERRO FATAL (logger indisponível): {e}")
            
        try:
            messagebox.showerror("Erro Fatal", f"Ocorreu um erro inesperado: {e}\nConsulte os logs.")
        except:
            pass