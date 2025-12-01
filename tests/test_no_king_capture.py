from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from utils.enums import Color, PieceType


def test_no_legal_move_can_capture_king():
    """
    Garante que nenhum movimento retornado por generate_legal_moves
    tenta capturar um rei, em nenhuma situação razoável de jogo.
    """

    board = Board()
    board.set_startpos()

    # Testa vários lances para simular progresso de jogo
    for _ in range(50):
        legal_moves = generate_legal_moves(board)

        assert legal_moves, "Nenhum movimento legal disponível (fim de jogo inesperado?)"

        for move in legal_moves:
            target = board.mailbox[move.to_sq]

            if target is not None:
                _, piece = target
                assert piece != PieceType.KING, (
                    f"Movimento ilegal detected: captura de rei: {move}"
                )

        # Aplica um movimento qualquer e continua
        board.make_move(legal_moves[0])


def test_no_king_direct_capture_in_custom_position():
    """
    Constrói um cenário artificial onde uma peça estaria alinhada com o rei
    e verifica se a captura nunca é listada.
    """

    board = Board()
    board.clear()

    # Colocar reis
    board.set_piece_at(4, Color.WHITE, PieceType.KING)   # E1
    board.set_piece_at(60, Color.BLACK, PieceType.KING)  # E8

    # Torre branca alinhada com rei preto
    board.set_piece_at(52, Color.WHITE, PieceType.ROOK)  # E7

    board.side_to_move = Color.WHITE

    legal_moves = generate_legal_moves(board)

    # Garantir que a torre não tenha movimento E7->E8
    for move in legal_moves:
        assert not (move.from_sq == 52 and move.to_sq == 60), (
            "Movimento ilegal permitiu captura direta do rei"
        )




def _has_move(moves, from_sq, to_sq):
    return any(m.from_sq == from_sq and m.to_sq == to_sq for m in moves)


def test_king_can_capture_free_piece():
    """
    Rei branco em E4, peão preto em E5.
    Nenhuma outra peça. O rei DEVE poder capturar o peão.
    """

    board = Board()
    board.clear()

    # E4 = 28 | E5 = 36
    board.set_piece_at(28, Color.WHITE, PieceType.KING)
    board.set_piece_at(36, Color.BLACK, PieceType.PAWN)

    board.side_to_move = Color.WHITE

    legal_moves = generate_legal_moves(board)

    assert _has_move(legal_moves, 28, 36), \
        "Rei deveria poder capturar peão em E5, mas não conseguiu."


def test_king_cannot_capture_if_square_is_attacked():
    """
    Rei branco em E4
    Peão preto em E5
    Torre preta em E8 protegendo E5
    -> Captura é ilegal, pois E5 está atacado.
    """

    board = Board()
    board.clear()

    # Rei branco
    board.set_piece_at(28, Color.WHITE, PieceType.KING)  # E4

    # Peão preto à frente
    board.set_piece_at(36, Color.BLACK, PieceType.PAWN)  # E5

    # Torre preta atacando E5
    board.set_piece_at(60, Color.BLACK, PieceType.ROOK)  # E8

    board.side_to_move = Color.WHITE

    legal_moves = generate_legal_moves(board)

    assert not _has_move(legal_moves, 28, 36), \
        "Rei conseguiu capturar peça em casa atacada, isso é ilegal."


def test_king_can_capture_defended_piece_if_defender_removed():
    """
    Mesmo cenário do teste anterior, mas removemos a torre.
    Agora o rei DEVE poder capturar.
    """

    board = Board()
    board.clear()

    board.set_piece_at(28, Color.WHITE, PieceType.KING)   # E4
    board.set_piece_at(36, Color.BLACK, PieceType.PAWN)   # E5

    # Sem torre protegendo
    board.side_to_move = Color.WHITE

    legal_moves = generate_legal_moves(board)

    assert _has_move(legal_moves, 28, 36), \
        "Rei deveria poder capturar após remover defensor, mas não consegue."


def test_king_vs_king_adjacent_capture_impossible():
    """
    Rei nunca pode capturar o outro rei,
    pois reis não podem ser adjacentes legalmente.
    """

    board = Board()
    board.clear()

    # Rei branco E4
    board.set_piece_at(28, Color.WHITE, PieceType.KING)

    # Rei preto E5
    board.set_piece_at(36, Color.BLACK, PieceType.KING)

    board.side_to_move = Color.WHITE

    legal_moves = generate_legal_moves(board)

    # Rei NÃO pode ir para E5
    assert not _has_move(legal_moves, 28, 36), \
        "Rei branco conseguiu capturar rei preto, isso é ilegal."
