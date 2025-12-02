"""Control panel with buttons for the Tk chess UI."""
from __future__ import annotations
try:
    import tkinter as tk
except Exception:  # pragma: no cover
    tk = None


class ControlPanel(tk.Frame if tk is not None else object):
    """Right-side control panel exposing common actions.

    Callbacks (in callbacks dict):
    - 'new_game' -> called when New Game pressed
    - 'selfplay' -> start self-play
    - 'train_step' -> execute one training step
    - 'quit' -> quit/close
    """

    def __init__(self, parent, callbacks: dict | None = None, **kwargs):
        if tk is None:
            raise RuntimeError('tkinter not available')

        super().__init__(parent, **kwargs)
        self.callbacks = callbacks or {}
        self._build()

    def _build(self):
        pad = {'padx': 6, 'pady': 6}
        lbl = tk.Label(self, text='Controls', font=('Helvetica', 12, 'bold'))
        lbl.pack(anchor='n', **pad)

        # Scoreboard
        score_frame = tk.Frame(self, relief='groove', borderwidth=1)
        score_frame.pack(fill='x', padx=6, pady=(4, 8))
        score_title = tk.Label(score_frame, text='Placar', font=('Helvetica', 10, 'bold'))
        score_title.pack(anchor='w', padx=6, pady=(4, 0))

        self._score_values = tk.Frame(score_frame)
        self._score_values.pack(fill='x', padx=6, pady=(2, 6))
        self._lbl_white = tk.Label(self._score_values, text='White: 0', width=12, anchor='w')
        self._lbl_white.grid(row=0, column=0, sticky='w')
        self._lbl_black = tk.Label(self._score_values, text='Black: 0', width=12, anchor='w')
        self._lbl_black.grid(row=0, column=1, sticky='w')
        self._lbl_draws = tk.Label(self._score_values, text='Draws: 0', width=12, anchor='w')
        self._lbl_draws.grid(row=0, column=2, sticky='w')

        # Reset score button (single action)
        btn_sf = tk.Frame(score_frame)
        btn_sf.pack(fill='x', padx=6, pady=(0, 6))
        btn_reset = tk.Button(btn_sf, text='Reset Placar', width=12, command=self._on_reset_score)
        btn_reset.pack(side='left', padx=2)

        btn_new = tk.Button(self, text='New Game', width=16, command=self._on_new)
        btn_new.pack(**pad)

        btn_menu = tk.Button(self, text='Menu', width=16, command=self._on_menu)
        btn_menu.pack(**pad)

        btn_self = tk.Button(self, text='Self-play', width=16, command=self._on_selfplay)
        btn_self.pack(**pad)

        btn_train = tk.Button(self, text='Train step', width=16, command=self._on_train_step)
        btn_train.pack(**pad)

        btn_quit = tk.Button(self, text='Quit', width=16, command=self._on_quit)
        btn_quit.pack(side='bottom', pady=(20, 6))

    def _on_new(self):
        cb = self.callbacks.get('new_game')
        if cb:
            cb()

    def _on_selfplay(self):
        cb = self.callbacks.get('selfplay')
        if cb:
            cb()

    def _on_train_step(self):
        cb = self.callbacks.get('train_step')
        if cb:
            cb()

    def _on_quit(self):
        cb = self.callbacks.get('quit')
        if cb:
            cb()

    def _on_menu(self):
        cb = self.callbacks.get('menu')
        if cb:
            cb()

    # Scoreboard API
    def set_score(self, white: int, black: int, draws: int):
        """Update scoreboard labels."""
        self._lbl_white.config(text=f'White: {white}')
        self._lbl_black.config(text=f'Black: {black}')
        self._lbl_draws.config(text=f'Draws: {draws}')

    def _on_score_white(self):
        cb = self.callbacks.get('score_white')
        if cb:
            cb()

    def _on_score_black(self):
        cb = self.callbacks.get('score_black')
        if cb:
            cb()

    def _on_score_draw(self):
        cb = self.callbacks.get('score_draw')
        if cb:
            cb()

    def _on_reset_score(self):
        cb = self.callbacks.get('reset_score')
        if cb:
            cb()
