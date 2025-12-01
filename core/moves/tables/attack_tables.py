from __future__ import annotations

"""
core/moves/tables/attack_tables.py

Tabelas públicas de ataques e funções utilitárias para geração de
ataques (cavalo, rei, peão) e para ataques deslizantes (torre/bispo).
Projeto design:
 - tabelas fixas (cavalo/rei/peão) são pré-computadas e armazenadas
   em listas de 64 entradas preenchidas "in-place" por init().
 - ataques dependentes de ocupação (rook/bishop/queen) delegam para
   uma implementação de Magic Bitboards quando disponível; caso
   contrário um fallback por ray-walk é usado (correto, porém mais lento).
 - inicialização é idempotente e thread-safe (double-checked locking).
 - os ponteiros _magic_rook_attacks / _magic_bishop_attacks são None
   antes de init() e apontam para uma função chamável após init().
"""

import threading
from typing import Dict, List, Tuple

from utils.constants import U64
from utils.enums import Color

# ============================================================
# Public tables (64 entries each, preenchidas por init())
# ============================================================

KNIGHT_ATTACKS: List[int] = [0] * 64
KING_ATTACKS: List[int] = [0] * 64
PAWN_ATTACKS: Dict[Color, List[int]] = {
    Color.WHITE: [0] * 64,
    Color.BLACK: [0] * 64,
}

# Optional debugging: máscaras geométricas de alcance (ray masks)
# Estas são sincronizáveis com o módulo magic_bitboards (se fornecer).
ROOK_GEOMETRY_RAYS: List[int] = [0] * 64
BISHOP_GEOMETRY_RAYS: List[int] = [0] * 64

# Ponteiros para implementação de sliding attacks (magic ou fallback).
# Observação: mantemos nomes _magic_* para compatibilidade com testes/codebase.
_magic_rook_attacks = None  # Setado em init() para função (sq, occ) -> attacks
_magic_bishop_attacks = None

# Inicialização thread-safe
_INITIALIZED: bool = False
_init_lock = threading.Lock()

# ============================================================
# File masks (A1 = 0 .. H8 = 63)
# Máscaras usadas para evitar wrap-around em shifts
# ============================================================

FILE_A = 0x0101010101010101
FILE_B = 0x0202020202020202
FILE_G = 0x4040404040404040
FILE_H = 0x8080808080808080

FILE_AB = FILE_A | FILE_B
FILE_GH = FILE_G | FILE_H


# ============================================================
# Helpers: construção de tabelas de ataques fixos
# ============================================================

def _build_attack_table(generator) -> List[int]:
    """
    Constrói uma tabela 64-elementos com base em um gerador sq->bitboard.

    A tabela é construída aplicando generator(sq) para cada sq em 0..63
    e garantindo máscara U64 para portabilidade.
    """
    table = [0] * 64
    for sq in range(64):
        table[sq] = generator(sq) & U64
    return table


def _knight_attack_from(sq: int) -> int:
    """
    Bitboard de ataques de cavalo a partir de `sq`.

    Ligações de bit shifting combinadas com máscaras FILE_* previnem
    wrap-around entre arquivos ao simular saltos L-shaped.
    Layout assumido: A1=0 ... H8=63.
    """
    bb = 1 << sq
    att = 0

    # Saltos para "cima" (+) e "baixo" (-) combinados com shift de arquivo
    att |= (bb << 17) & ~FILE_A
    att |= (bb << 15) & ~FILE_H
    att |= (bb << 10) & ~FILE_AB
    att |= (bb << 6) & ~FILE_GH

    att |= (bb >> 17) & ~FILE_H
    att |= (bb >> 15) & ~FILE_A
    att |= (bb >> 10) & ~FILE_GH
    att |= (bb >> 6) & ~FILE_AB

    return att & U64


def _king_attack_from(sq: int) -> int:
    """
    Bitboard de ataques de rei a partir de `sq`.

    Shift vertical/horizontal/diagonal com máscaras de arquivo previnem
    wrap-around. Usa U64 ao final.
    """
    bb = 1 << sq
    att = 0

    # Vertical
    att |= (bb << 8)
    att |= (bb >> 8)

    # Horizontal e diagonais (aplicam máscaras para evitar overflow)
    att |= (bb << 1) & ~FILE_A
    att |= (bb >> 1) & ~FILE_H
    att |= (bb << 9) & ~FILE_A
    att |= (bb << 7) & ~FILE_H
    att |= (bb >> 7) & ~FILE_A
    att |= (bb >> 9) & ~FILE_H

    return att & U64


def _build_pawn_attack_tables() -> Dict[Color, List[int]]:
    """
    Constrói tabelas de ataques de peão por cor.

    Cada entrada contém o bitboard dos alvos de captura do peão
    quando o peão está em `sq`.
    """
    white = [0] * 64
    black = [0] * 64

    for sq in range(64):
        bb = 1 << sq

        # Peão branco: ataca para "cima" (rank increasing) nas diagonais
        west_w = (bb & ~FILE_A) << 7
        east_w = (bb & ~FILE_H) << 9
        white[sq] = (west_w | east_w) & U64

        # Peão preto: ataca para "baixo" (rank decreasing) nas diagonais
        west_b = (bb & ~FILE_A) >> 9
        east_b = (bb & ~FILE_H) >> 7
        black[sq] = (west_b | east_b) & U64

    return {Color.WHITE: white, Color.BLACK: black}


# ============================================================
# Fallback sliding attacks (usados caso Magic falhe/ausente)
# ============================================================

def _fallback_sliding_attacks(
    sq: int,
    occ: int,
    directions: Tuple[int, ...],
) -> int:
    """
    Ray-walk seguro para gerar ataques de peças deslizantes (rook/bishop).

    Implementação robusta contra wrap-around:
    - calcula file/rank iniciais e compara mudanças para detectar
      quando um movimento saltaria para o arquivo errado.
    - interrompe o ray ao encontrar uma peça (ocupação).
    Complexidade: O(distance_to_edge) por direção.
    """
    attacks = 0
    file = sq & 7
    rank = sq >> 3

    for delta in directions:
        s = sq
        cf, cr = file, rank

        while True:
            s += delta
            if s < 0 or s >= 64:
                break

            nf, nr = s & 7, s >> 3

            # Evita wrap-around: se a mudança de arquivo for >1 então o shift
            # atravessou a borda e não é um movimento válido na direção.
            # Exceção: deslocamentos verticais (delta == ±8) podem alterar rank
            # sem alteração de file (tratados normalmente).
            if abs(nf - cf) > 1 or (abs(nr - cr) > 1 and abs(delta) != 8):
                break

            bit = 1 << s
            attacks |= bit

            # Para no primeiro bloqueio encontrado
            if occ & bit:
                break

            cf, cr = nf, nr

    return attacks & U64


def _fallback_rook_attacks(sq: int, occ: int) -> int:
    """Fallback para torre: N, S, E, W."""
    return _fallback_sliding_attacks(sq, occ, (8, -8, 1, -1))


def _fallback_bishop_attacks(sq: int, occ: int) -> int:
    """Fallback para bispo: diagonais."""
    return _fallback_sliding_attacks(sq, occ, (9, 7, -9, -7))


# ============================================================
# Opcional: sincronização de máscaras geométricas dos magics
# ============================================================

def _compute_ray_masks_from_magic(mb_module) -> None:
    """
    Se o módulo magic_bitboards expõe máscaras geométricas (ROOK_MASKS,
    BISHOP_MASKS), sincroniza essas máscaras para uso em debugging.
    Essas máscaras são opcionais; não há erro se ausentes.
    """
    rook_masks = getattr(mb_module, "ROOK_MASKS", None)
    if isinstance(rook_masks, (list, tuple)) and len(rook_masks) == 64:
        ROOK_GEOMETRY_RAYS[:] = rook_masks

    bishop_masks = getattr(mb_module, "BISHOP_MASKS", None)
    if isinstance(bishop_masks, (list, tuple)) and len(bishop_masks) == 64:
        BISHOP_GEOMETRY_RAYS[:] = bishop_masks


# ============================================================
# Init
# ============================================================

def init() -> None:
    """
    Inicializa todas as tabelas públicas de ataques.

    Estratégia:
      - Double-checked locking para evitar overhead de sincronização.
      - Preenche tabelas estáticas (knight/king/pawn) in-place.
      - Tenta carregar Magic Bitboards (core.moves.magic.magic_bitboards).
        - Se disponível, chama mb.init() e usa as funções de ataque do módulo.
        - Caso contrário, aponta para implementações fallback seguras.

    Observação: init() é idempotente — pode ser chamada múltiplas vezes.
    """
    global _INITIALIZED, _magic_rook_attacks, _magic_bishop_attacks

    if _INITIALIZED:  # fast path
        return

    # Double-checked locking: protege inicialização multi-threaded
    with _init_lock:
        if _INITIALIZED:
            return

        # Tabelas estáticas (não dependem de ocupação)
        KNIGHT_ATTACKS[:] = _build_attack_table(_knight_attack_from)
        KING_ATTACKS[:] = _build_attack_table(_king_attack_from)

        pawn_tables = _build_pawn_attack_tables()
        for color in (Color.WHITE, Color.BLACK):
            PAWN_ATTACKS[color][:] = pawn_tables[color]

        # Tabelas dependentes de ocupação (Magic ou fallback)
        try:
            # Import dinâmico: pode falhar em ambientes sem magics compilados
            from core.moves.magic import magic_bitboards as mb  # type: ignore

            # Garantir init do módulo de magics
            mb.init()

            # Obter funções ou usar fallback
            _magic_rook_attacks = getattr(mb, "rook_attacks", _fallback_rook_attacks)
            _magic_bishop_attacks = getattr(mb, "bishop_attacks", _fallback_bishop_attacks)

            # Sincronizar máscaras geométricas se o módulo fornecer
            _compute_ray_masks_from_magic(mb)

        except Exception:
            # Caso qualquer erro ocorra ao carregar os magics, usamos fallbacks.
            # Exceção ampla intencional: qualquer falha de import/execution aqui
            # deve resultar no fallback seguro, preservando corretude.
            _magic_rook_attacks = _fallback_rook_attacks
            _magic_bishop_attacks = _fallback_bishop_attacks

        # Sanidade mínima: garantir tamanho esperado das tabelas
        assert len(KNIGHT_ATTACKS) == 64
        assert len(KING_ATTACKS) == 64
        assert len(PAWN_ATTACKS[Color.WHITE]) == 64
        assert len(PAWN_ATTACKS[Color.BLACK]) == 64

        _INITIALIZED = True


# ============================================================
# Public API
# ============================================================

def knight_attacks(sq: int) -> int:
    """Retorna bitboard de ataques de cavalo a partir de `sq`."""
    if not _INITIALIZED:
        init()
    return KNIGHT_ATTACKS[sq]


def king_attacks(sq: int) -> int:
    """Retorna bitboard de ataques de rei a partir de `sq`."""
    if not _INITIALIZED:
        init()
    return KING_ATTACKS[sq]


def pawn_attacks(sq: int, color: Color) -> int:
    """Retorna bitboard de ataques de peão em `sq` para `color`."""
    if not _INITIALIZED:
        init()
    return PAWN_ATTACKS[color][sq]


def rook_attacks(sq: int, occ: int) -> int:
    """
    Retorna bitboard de ataques de torre considerando ocupação `occ`.

    Delegará para implementação de Magic (se disponível) ou para fallback.
    """
    if not _INITIALIZED:
        init()
    return _magic_rook_attacks(sq, occ)


def bishop_attacks(sq: int, occ: int) -> int:
    """Retorna bitboard de ataques de bispo considerando ocupação `occ`."""
    if not _INITIALIZED:
        init()
    return _magic_bishop_attacks(sq, occ)


def queen_attacks(sq: int, occ: int) -> int:
    """Retorna ataques de dama combinando torre + bispo."""
    if not _INITIALIZED:
        init()
    return _magic_rook_attacks(sq, occ) | _magic_bishop_attacks(sq, occ)


# ============================================================
# Exports
# ============================================================

__all__ = [
    "init",
    "knight_attacks",
    "king_attacks",
    "pawn_attacks",
    "rook_attacks",
    "bishop_attacks",
    "queen_attacks",
    "KNIGHT_ATTACKS",
    "KING_ATTACKS",
    "PAWN_ATTACKS",
    "ROOK_GEOMETRY_RAYS",
    "BISHOP_GEOMETRY_RAYS",
    "_INITIALIZED",
]
