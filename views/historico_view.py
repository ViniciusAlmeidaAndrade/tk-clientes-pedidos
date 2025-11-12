# Em views/historico_view.py

import tkinter as tk
from tkinter import ttk

class HistoricoView(ttk.Frame):
    """
    Frame que exibe o conteúdo do arquivo de log 'app.log'.
    """
    def __init__(self, parent, on_recarregar_callback, on_limpar_callback):
        super().__init__(parent, padding=10)
        
        # --- 1. Frame de Botões ---
        botoes_frame = ttk.Frame(self, padding=(0, 0, 0, 10))
        botoes_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.btn_recarregar = ttk.Button(
            botoes_frame, 
            text="Recarregar Histórico", 
            command=on_recarregar_callback
        )
        self.btn_recarregar.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_limpar = ttk.Button(
            botoes_frame, 
            text="Limpar Histórico", 
            command=on_limpar_callback
        )
        self.btn_limpar.pack(side=tk.LEFT)

        # --- 2. Frame do Histórico (Text com Scrollbar) ---
        text_frame = ttk.Frame(self)
        text_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self.txt_historico = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 10), # Fonte monoespaçada para logs
            yscrollcommand=scrollbar.set,
            bg="#fdfdfd",
            state=tk.DISABLED # Começa desabilitado para edição
        )
        scrollbar.config(command=self.txt_historico.yview)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_historico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def set_historico(self, texto: str):
        """
        Recebe o texto do log e atualiza o widget Text.
        """
        self.txt_historico.config(state=tk.NORMAL) # Habilita para escrever
        self.txt_historico.delete("1.0", tk.END)
        
        if texto.strip():
            self.txt_historico.insert("1.0", texto)
        else:
            self.txt_historico.insert("1.0", "O histórico de ações está vazio.")
            
        self.txt_historico.config(state=tk.DISABLED) # Desabilita para edição
        self.txt_historico.see(tk.END) # Rola para o final