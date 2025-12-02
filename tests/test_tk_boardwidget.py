import pytest
import os


try:
    import tkinter as tk
except Exception:  # pragma: no cover
    tk = None


@pytest.mark.skipif(tk is None, reason="tkinter not available")
def test_boardwidget_draws_start_position():
    # lazy import to avoid requiring Tk when collecting tests
    from interface.tk.board_widget import BoardWidget
    from core.board.board import Board

    root = tk.Tk()
    root.withdraw()
    bw = BoardWidget(root, square_size=48)
    b = Board()
    bw.set_position(b)
    items = bw.find_withtag('piece')
    # expect 32 pieces in starting position
    assert len(items) == 32
    root.destroy()
