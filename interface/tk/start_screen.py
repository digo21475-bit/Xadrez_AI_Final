"""Start / setup screen for the Tk interface.

Allows selecting player types for White and Black: Human, AI or Random.
"""
from __future__ import annotations
try:
    import tkinter as tk
    from tkinter import ttk
except Exception:  # pragma: no cover - headless
    tk = None
    ttk = None

try:
    from agents.nn_agent import list_available_models
except Exception:
    list_available_models = None


class StartScreen(tk.Frame if tk is not None else object):
    """Setup screen with two dropdowns (White/Black) and a Start button.

    callback signature: callback(white_choice: str, black_choice: str)
    """

    OPTIONS = ['Human', 'AI', 'Random']

    def __init__(self, parent, start_callback=None, **kwargs):
        if tk is None:
            raise RuntimeError('tkinter not available')
        super().__init__(parent, **kwargs)
        self.start_callback = start_callback
        self.white_var = tk.StringVar(value=self.OPTIONS[0])
        self.black_var = tk.StringVar(value=self.OPTIONS[1])
        # model selection: either model name or 'None'
        self.model_var = tk.StringVar(value='None')
        self._build()

    def _build(self):
        pad = {'padx': 8, 'pady': 6}

        title = tk.Label(self, text='Configuração do Jogo', font=('Helvetica', 14, 'bold'))
        title.pack(**pad)

        frame = tk.Frame(self)
        frame.pack(**pad)

        lbl_w = tk.Label(frame, text='White:')
        lbl_w.grid(row=0, column=0, sticky='e', padx=4, pady=4)
        opt_w = tk.OptionMenu(frame, self.white_var, *self.OPTIONS)
        opt_w.grid(row=0, column=1, sticky='w', padx=4, pady=4)

        lbl_b = tk.Label(frame, text='Black:')
        lbl_b.grid(row=1, column=0, sticky='e', padx=4, pady=4)
        opt_b = tk.OptionMenu(frame, self.black_var, *self.OPTIONS)
        opt_b.grid(row=1, column=1, sticky='w', padx=4, pady=4)

        # model selection row
        lbl_m = tk.Label(frame, text='Model:')
        lbl_m.grid(row=2, column=0, sticky='e', padx=4, pady=4)
        # populate model options if helper available
        models = []
        try:
            if list_available_models is not None:
                models = [name for name, ck in list_available_models()]
        except Exception:
            models = []

        if not models:
            models = ['None']
        # prefer AgentA_medium if present
        default = 'AgentA_medium' if 'AgentA_medium' in models else models[0]
        self.model_var.set(default)
        opt_m = tk.OptionMenu(frame, self.model_var, *models)
        opt_m.grid(row=2, column=1, sticky='w', padx=4, pady=4)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=(10, 0))

        start_btn = tk.Button(btn_frame, text='Start Game', width=16, command=self._on_start)
        start_btn.pack(side='left', padx=6)

        quit_btn = tk.Button(btn_frame, text='Quit', width=12, command=self._on_quit)
        quit_btn.pack(side='left', padx=6)

    def _on_start(self):
        w = self.white_var.get()
        b = self.black_var.get()
        m = self.model_var.get()
        if self.start_callback:
            # callback signature: callback(white_choice, black_choice, model_name)
            try:
                self.start_callback(w, b, m)
            except TypeError:
                # backward compatibility: some callers may accept only 2 args
                self.start_callback(w, b)

    def _on_quit(self):
        # find root and quit
        try:
            self.winfo_toplevel().quit()
        except Exception:
            pass
