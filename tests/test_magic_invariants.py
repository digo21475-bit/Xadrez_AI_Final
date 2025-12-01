# tests/test_magic_invariants.py
from core.moves.magic import magic_bitboards as mb


def test_magic_index_space_is_fully_covered():
    mb.init()

    for sq in range(64):
        for is_rook in (True, False):
            mask = mb.ROOK_MASKS[sq] if is_rook else mb.BISHOP_MASKS[sq]
            magic = mb.ROOK_GOOD_MAGICS[sq] if is_rook else mb.BISHOP_GOOD_MAGICS[sq]
            shift = mb.ROOK_SHIFTS[sq] if is_rook else mb.BISHOP_SHIFTS[sq]

            positions = mb._MASK_POSITIONS[(sq, is_rook)]
            size_expected = 1 << len(positions)

            seen = set()

            for idx in range(size_expected):
                occ = mb.index_to_occupancy(idx, positions)
                index = (((occ & mask) * magic) & mb.U64) >> shift
                seen.add(index)

            assert len(seen) == size_expected, (
                f"Index space incompleto em sq={sq}, piece={'rook' if is_rook else 'bishop'}"
            )


def test_magic_extreme_occupancies():
    mb.init()

    for sq in range(64):
        for is_rook in (True, False):
            mask = mb.ROOK_MASKS[sq] if is_rook else mb.BISHOP_MASKS[sq]

            # set completo de ocupação possível dentro da máscara
            extremes = [
                0,
                mask,
            ]

            for occ in extremes:
                if is_rook:
                    atk_magic = mb.rook_attacks(sq, occ)
                    atk_slow = mb._rook_attacks_from_occupancy(sq, occ)
                else:
                    atk_magic = mb.bishop_attacks(sq, occ)
                    atk_slow = mb._bishop_attacks_from_occupancy(sq, occ)

                assert atk_magic == atk_slow, (
                    f"Erro em extreme occ em sq={sq}, piece={'rook' if is_rook else 'bishop'}"
                )
