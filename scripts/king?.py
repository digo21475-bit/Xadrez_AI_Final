from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from utils.enums import Color, PieceType

def print_moves(label, moves):
    print(f"\n{label}")
    for m in moves:
        promo = f"={m.promotion}" if m.promotion else ""
        cap = "x" if m.is_capture else "-"
        print(f"{m.from_sq}{cap}{m.to_sq}{promo}")

def king_can_capture(board: Board, from_sq: int, to_sq: int) -> bool:
    moves = generate_legal_moves(board)
    for m in moves:
        if m.from_sq == from_sq and m.to_sq == to_sq and m.is_capture:
            return True
    return False

def scenario_simple_capture():
    """
    Rei branco em E4, peão preto em E5 (diretamente acima).
    Não há xeque envolvido, o rei deve poder capturar.
    """
    board = Board()
    board.clear()

    board.set_piece_at(28, Color.WHITE, PieceType.KING)   # E4
    board.set_piece_at(36, Color.BLACK, PieceType.PAWN)  # E5

    board.side_to_move = Color.WHITE

    print("\n[TESTE 1] Rei branco em E4 vs peão preto em E5")
    result = king_can_capture(board, 28, 36)
    print("Rei pode capturar peão?", result)

def scenario_capture_into_check():
    """
    Rei em E4, peão em E5, mas existe uma torre em E8.
    Captura colocaria o rei em xeque => deve ser proibida.
    """
    board = Board()
    board.clear()

    board.set_piece_at(28, Color.WHITE, PieceType.KING)   # E4
    board.set_piece_at(36, Color.BLACK, PieceType.PAWN)  # E5
    board.set_piece_at(60, Color.BLACK, PieceType.ROOK)  # E8

    board.side_to_move = Color.WHITE

    print("\n[TESTE 2] Captura ilegal (rei entra em xeque)")
    result = king_can_capture(board, 28, 36)
    print("Rei pode capturar peão?", result)

def scenario_adjacent_kings():
    """
    Rei branco e rei preto adjacentes – nunca deve permitir captura.
    """
    board = Board()
    board.clear()

    board.set_piece_at(28, Color.WHITE, PieceType.KING)  # E4
    board.set_piece_at(36, Color.BLACK, PieceType.KING) # E5

    board.side_to_move = Color.WHITE

    print("\n[TESTE 3] Reis adjacentes")
    result = king_can_capture(board, 28, 36)
    print("Rei branco pode capturar rei preto?", result)

def scenario_under_check_king_capture():
    """
    Rei em E4, torre inimiga em E1 dando xeque,
    inimigo em D5. Rei só deve capturar se sair do xeque legalmente.
    """
    board = Board()
    board.clear()

    board.set_piece_at(28, Color.WHITE, PieceType.KING)   # E4
    board.set_piece_at(4, Color.BLACK, PieceType.ROOK)    # E1
    board.set_piece_at(35, Color.BLACK, PieceType.KNIGHT) # D5

    board.side_to_move = Color.WHITE

    print("\n[TESTE 4] Rei em xeque tentando capturar para escapar")
    result = king_can_capture(board, 28, 35)
    print("Rei pode capturar o cavalo?", result)

if __name__ == "__main__":
    scenario_simple_capture()
    scenario_capture_into_check()
    scenario_adjacent_kings()
    scenario_under_check_king_capture()
