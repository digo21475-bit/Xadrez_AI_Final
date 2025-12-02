#!/usr/bin/env python3
"""
Extrai imagens PNG embutidas em arquivos SVG de peças em `assets/`.

Muitos SVGs no repositório contêm um elemento <image xlink:href="data:image/png;base64,..."/>
com a arte rasterizada. Este utilitário procura pelos arquivos `w_*.svg` e `b_*.svg`,
decodifica o primeiro bloco base64 encontrado e grava como PNG em
`assets/pieces/white_<name>.png` e `assets/pieces/black_<name>.png` para uso pela UI.

Uso:
    python assets/extract_piece_pngs.py

Isso não sobrescreve arquivos já existentes a menos que --force seja usado.
"""
from __future__ import annotations

import os
import re
import base64
import argparse
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


SVG_PATTERN = re.compile(r'data:image/png;base64,([A-Za-z0-9+/=\n\r]+)')


def find_svg_files(base_dir: str):
    for name in os.listdir(base_dir):
        if name.startswith(('w_', 'b_')) and name.endswith('.svg'):
            yield os.path.join(base_dir, name)


def decode_first_png_from_svg(svg_path: str) -> bytes | None:
    with open(svg_path, 'rb') as fh:
        data = fh.read().decode('utf-8', errors='ignore')
    m = SVG_PATTERN.search(data)
    if not m:
        return None
    b64 = m.group(1)
    # strip whitespace/newlines
    b64 = ''.join(b64.split())
    try:
        return base64.b64decode(b64)
    except Exception:
        return None


def target_name_from_svg(svg_name: str) -> tuple[str, str]:
    # svg_name like 'w_pawn.svg' or 'b_knight.svg'
    base = os.path.basename(svg_name)
    prefix, rest = base.split('_', 1)
    rest = rest.rsplit('.', 1)[0]
    if prefix == 'w':
        color = 'white'
    else:
        color = 'black'
    return color, rest


def main(force: bool = False):
    script_dir = os.path.dirname(__file__)
    assets_dir = os.path.abspath(os.path.join(script_dir))
    pieces_dir = os.path.join(assets_dir, 'pieces')
    os.makedirs(pieces_dir, exist_ok=True)

    any_written = False
    for svg_path in find_svg_files(assets_dir):
        color, name = target_name_from_svg(svg_path)
        out_name = f"{color}_{name}.png"
        out_path = os.path.join(pieces_dir, out_name)
        if os.path.exists(out_path) and not force:
            print(f"skip existing: {out_name}")
            continue

        png = decode_first_png_from_svg(svg_path)
        if not png:
            print(f"no embedded PNG found in {svg_path}")
            continue

        # If Pillow is available and this is a white piece, recolor to a light tone
        if PIL_AVAILABLE and color == 'white':
            try:
                from io import BytesIO
                im = Image.open(BytesIO(png)).convert('RGBA')
                w, h = im.size
                px = im.load()
                modified = False
                for x in range(w):
                    for y in range(h):
                        r, g, b, a = px[x, y]
                        if a > 10:
                            # apply light ivory while preserving alpha and rough shading
                            # mix original color with target light color based on alpha
                            nr, ng, nb = (240, 240, 240)
                            if (r, g, b) != (nr, ng, nb):
                                px[x, y] = (nr, ng, nb, a)
                                modified = True
                # save result
                im.save(out_path)
            except Exception:
                # fallback to raw write
                with open(out_path, 'wb') as fh:
                    fh.write(png)
        else:
            with open(out_path, 'wb') as fh:
                fh.write(png)
        print(f"wrote: {out_path}")
        any_written = True

    if not any_written:
        print("No new PNGs written. Use --force to overwrite existing files.")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--force', action='store_true', help='overwrite existing pngs')
    args = p.parse_args()
    main(force=args.force)
