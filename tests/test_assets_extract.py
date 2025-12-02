import importlib.util
import os
import sys


def load_module_from_path(path, name="mod"):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_decode_and_main_creates_pngs(tmp_path):
    # locate the extractor script
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    extractor_path = os.path.join(repo_root, 'assets', 'extract_piece_pngs.py')
    assert os.path.exists(extractor_path)

    mod = load_module_from_path(extractor_path, 'extract_piece_pngs')

    # test decode_first_png_from_svg on a known svg
    svg_path = os.path.join(repo_root, 'assets', 'b_pawn.svg')
    assert os.path.exists(svg_path)
    png_bytes = mod.decode_first_png_from_svg(svg_path)
    assert png_bytes is not None and isinstance(png_bytes, (bytes, bytearray))

    # run main (will write to assets/pieces/) but do not fail if already present
    mod.main(force=True)

    pieces_dir = os.path.join(repo_root, 'assets', 'pieces')
    assert os.path.isdir(pieces_dir)
    # check presence of at least one expected file
    assert os.path.exists(os.path.join(pieces_dir, 'white_pawn.png'))
    assert os.path.exists(os.path.join(pieces_dir, 'black_pawn.png'))
