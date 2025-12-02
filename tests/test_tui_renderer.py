import pytest
import os


try:
    from interface.tui import renderer as rend
except Exception:
    rend = None


def test_build_board_image_returns_pil_image():
    if rend is None:
        pytest.skip('renderer module not importable')

    # skip if Pillow not available in renderer
    if not getattr(rend, 'PIL_AVAILABLE', False):
        pytest.skip('Pillow not available for renderer')

    from core.board.board import Board

    b = Board()
    img = rend.build_board_image(b, tile_size=32)
    assert img is not None
    # PIL Image has size 8*tile_size square
    assert getattr(img, 'size', None) == (32 * 8, 32 * 8)
