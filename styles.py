def apply_light_theme(style):
    """Aplica uma configuração de tema claro limpo usando 'clam'."""
    
    # Cores
    bg_color = "#F0F0F0"
    fg_color = "black"
    header_color = "#004A99"
    tree_bg = "white"
    field_bg = "white"
    select_bg = "#0078D7"
    
    style.theme_use('clam')
    
    style.configure('.',
                    background=bg_color,
                    foreground=fg_color,
                    fieldbackground=field_bg,
                    font=("Segoe UI", 10))
    
    style.configure('TFrame', background=bg_color)
    style.configure('TLabel', background=bg_color, foreground=fg_color)
    style.configure('Header.TLabel', foreground=header_color) # Rótulo do Dashboard
    
    style.configure('TButton',
                    background="#E1E1E1",
                    foreground=fg_color,
                    bordercolor="#ADADAD",
                    lightcolor="#E1E1E1",
                    darkcolor="#ADADAD",
                    font=("Segoe UI", 10, "bold"))
    style.map('TButton',
                background=[('active', '#C9C9C9'), ('pressed', select_bg)],
                foreground=[('pressed', 'white')])

    style.configure('TNotebook', background=bg_color, tabmargins=[2, 5, 2, 0])
    style.configure('TNotebook.Tab',
                    background="#DCDCDC",
                    padding=[8, 2],
                    font=("Segoe UI", 10, "bold"),
                    focuscolor=bg_color)
    style.map('TNotebook.Tab',
                background=[('selected', bg_color)])

    style.configure('Treeview',
                    background=tree_bg,
                    foreground=fg_color,
                    fieldbackground=tree_bg,
                    rowheight=25)
    style.configure('Treeview.Heading',
                    background="#E1E1E1",
                    foreground=fg_color,
                    font=("Segoe UI", 10, "bold"))
    style.map('Treeview.Heading', background=[('active', '#C9C9C9')])
    
    # Cor de seleção
    style.map('Treeview', background=[('selected', select_bg)])
    
    style.configure('Vertical.TScrollbar', background=bg_color, troughcolor="#E1E1E1")
    style.configure('TCombobox', fieldbackground=field_bg)
    style.configure('TEntry', fieldbackground=field_bg)


def apply_dark_theme(style):
    """Aplica uma configuração de tema escuro usando 'clam'."""
    
    # Cores
    bg_color = "#2E2E2E"
    fg_color = "white"
    header_color = "#5599FF"
    tree_bg = "#3C3C3C"
    field_bg = "#4A4A4A"
    select_bg = "#0078D7"
    
    style.theme_use('clam')
    
    style.configure('.',
                    background=bg_color,
                    foreground=fg_color,
                    fieldbackground=field_bg,
                    font=("Segoe UI", 10))
    
    style.configure('TFrame', background=bg_color)
    style.configure('TLabel', background=bg_color, foreground=fg_color)
    style.configure('Header.TLabel', foreground=header_color) # Rótulo do Dashboard
    
    style.configure('TButton',
                    background="#505050",
                    foreground=fg_color,
                    bordercolor="#606060",
                    lightcolor="#505050",
                    darkcolor="#606060",
                    font=("Segoe UI", 10, "bold"))
    style.map('TButton',
                background=[('active', '#606060'), ('pressed', select_bg)],
                foreground=[('pressed', 'white')])

    style.configure('TNotebook', background=bg_color, tabmargins=[2, 5, 2, 0])
    style.configure('TNotebook.Tab',
                    background="#404040",
                    foreground="#A0A0A0",
                    padding=[8, 2],
                    font=("Segoe UI", 10, "bold"),
                    focuscolor=bg_color)
    style.map('TNotebook.Tab',
                background=[('selected', bg_color)],
                foreground=[('selected', fg_color)])
            
    style.configure('Treeview',
                    background=tree_bg,
                    foreground=fg_color,
                    fieldbackground=tree_bg,
                    rowheight=25)
    style.configure('Treeview.Heading',
                    background="#505050",
                    foreground=fg_color,
                    font=("Segoe UI", 10, "bold"))
    style.map('Treeview.Heading', background=[('active', '#606060')])
    
    # Cor de seleção (mantém a mesma)
    style.map('Treeview', background=[('selected', select_bg)])
    
    style.configure('Vertical.TScrollbar', background=bg_color, troughcolor="#505050")
    style.configure('TCombobox',
                background=field_bg,      
                fieldbackground=field_bg, 
                foreground=fg_color,
                arrowcolor=fg_color,      
                selectbackground=select_bg)

    style.map('TCombobox',
            fieldbackground=[('readonly', field_bg), ('focus', field_bg)],
            foreground=[('readonly', fg_color)],
            background=[('readonly', field_bg)])
    style.configure('TEntry', fieldbackground=field_bg, foreground=fg_color)


def get_calendar_light_style():
    """Retorna um dicionário de estilo para o DateEntry (tema claro)."""
    return {
        'background': 'white',
        'foreground': 'black',
        'headersbackground': '#F0F0F0',
        'headersforeground': 'black',
        'selectbackground': '#0078D7',
        'selectforeground': 'white',
        'normalbackground': 'white',
        'normalforeground': 'black',
        'weekendbackground': 'white',
        'weekendforeground': 'black',
        'othermonthforeground': '#909090',
        'othermonthbackground': 'white',
        'bordercolor': '#ADADAD'
    }


def get_calendar_dark_style():
    """Retorna um dicionário de estilo para o DateEntry (tema escuro)."""
    return {
        'background': '#4A4A4A',       # Fundo da caixa de entrada
        'foreground': 'white',         # Texto da caixa de entrada
        # 'readonlybackground': '#4A4A4A',
        # 'insertbackground': 'white',
        'headersbackground': '#2E2E2E', # "Dom, Seg, Ter..."
        'headersforeground': 'white',
        'selectbackground': '#0078D7',  # Dia selecionado
        'selectforeground': 'white',
        'normalbackground': '#4A4A4A',  # Fundo dos dias
        'normalforeground': 'white',
        'weekendbackground': '#4A4A4A',
        'weekendforeground': 'white',
        'othermonthforeground': '#909090', # Dias de outro mês
        'othermonthbackground': '#4A4A4A',
        'bordercolor': '#606060'
    }
