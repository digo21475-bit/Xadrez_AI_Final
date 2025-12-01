from core.board.board import Board


def test_make_unmake_integrity():
    board = Board()  # já inicializa na posição inicial

    snapshot = (
        [row.copy() for row in board.bitboards],
        board.occupancy.copy(),
        board.all_occupancy,
        board.mailbox.copy(),
        board.side_to_move,
        board.castling_rights,
        board.en_passant_square,
        board.halfmove_clock,
        board.fullmove_number
    )

    from core.moves.legal_movegen import generate_legal_moves

    for move in generate_legal_moves(board):
        board.make_move(move)
        board.unmake_move()

        assert snapshot[0] == board.bitboards
        assert snapshot[1] == board.occupancy
        assert snapshot[2] == board.all_occupancy
        assert snapshot[3] == board.mailbox
        assert snapshot[4] == board.side_to_move
        assert snapshot[5] == board.castling_rights
        assert snapshot[6] == board.en_passant_square
        assert snapshot[7] == board.halfmove_clock
        assert snapshot[8] == board.fullmove_number
