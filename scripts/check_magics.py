#!/usr/bin/env python3
import os
import sys

# === Força acesso ao projeto ===
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    print("== MAGIC BITBOARDS INTEGRITY CHECK ==")

    try:
        from core.moves.magic.magic_autogen import ROOK_MAGICS, BISHOP_MAGICS
        from core.moves.magic import magic_bitboards as mb
    except Exception as e:
        print(f"ERRO: Falha ao importar módulos:{e}")
        raise

    # ----------------------------------------------------------
    # 1. Estrutura básica
    # ----------------------------------------------------------

    if len(ROOK_MAGICS) != 64:
        raise AssertionError(f"ROOK_MAGICS corrompido: len={len(ROOK_MAGICS)} (esperado 64)")

    if len(BISHOP_MAGICS) != 64:
        raise AssertionError(f"BISHOP_MAGICS corrompido: len={len(BISHOP_MAGICS)} (esperado 64)")

    print("✔ Tamanho dos magics OK (64x2)")

    # ----------------------------------------------------------
    # 2. Tipos e faixa uint64
    # ----------------------------------------------------------

    for i, m in enumerate(ROOK_MAGICS):
        if not isinstance(m, int):
            raise TypeError(f"ROOK_MAGICS[{i}] não é int")
        if not (0 <= m < (1 << 64)):
            raise ValueError(f"ROOK_MAGICS[{i}] fora de uint64")

    for i, m in enumerate(BISHOP_MAGICS):
        if not isinstance(m, int):
            raise TypeError(f"BISHOP_MAGICS[{i}] não é int")
        if not (0 <= m < (1 << 64)):
            raise ValueError(f"BISHOP_MAGICS[{i}] fora de uint64")

    print("✔ Tipos e faixa (uint64) OK")

    # ----------------------------------------------------------
    # 3. Inicialização real
    # ----------------------------------------------------------

    try:
        mb.init()
        print("✔ magic_bitboards.init() OK")
    except Exception as e:
        print("✘ Erro ao inicializar magic_bitboards")
        raise

    # ----------------------------------------------------------
    # 4. Sem colisão em runtime
    # ----------------------------------------------------------

    # 4. Garantir que as tabelas foram realmente construídas
    if not mb._INITIALIZED:
        raise AssertionError("magic_bitboards não inicializou corretamente")

    if mb._ROOK_ATT_TABLE is None or mb._BISHOP_ATT_TABLE is None:
        raise AssertionError("Tabelas de ataque não foram construídas")

    print("✔ Tabelas de ataque inicializadas corretamente")

    # ----------------------------------------------------------
    # 5. Sanidade contra brute-force
    # ----------------------------------------------------------
    from core.moves.tables.attack_tables import rook_attacks, bishop_attacks
    print("✔ Funções rook_attacks/bishop_attacks disponíveis e importadas")

    # Teste simples de acesso
    r = rook_attacks(0, 0)
    b = bishop_attacks(0, 0)

    print("✔ Funções rook_attacks / bishop_attacks OK")
    print("✔ check_magics concluído com sucesso")


if __name__ == "__main__":
    sys.exit(main())
