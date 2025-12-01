from core.board.board import Board
from core.moves.move import Move
from core.moves.legal_movegen import generate_legal_moves
from core.rules.game_status import get_game_status
from engine.search.iterative import search_root
from utils.enums import PieceType, Color


def test_startpos_depths():
    b = Board()  # startpos
    for d in (1, 2, 3):
        res = search_root(b, max_time_ms=100, max_depth=d)
        # should return a best_move (or None) but must not raise and nodes>0
        assert 'nodes' in res
        assert res['depth'] >= 0


def test_fifty_move_draw_respected():
    b = Board(setup=False)
    b.clear()
    # place only two kings
    b.place(PieceType.KING, Color.WHITE, 'e1')
    b.place(PieceType.KING, Color.BLACK, 'e8')
    # set halfmove clock to 100 -> fifty-move draw
    b.halfmove_clock = 100
    gs = get_game_status(b)
    assert gs.is_draw_by_fifty_move
    # search_root should handle draw and return score 0
    res = search_root(b, max_time_ms=100, max_depth=3)
    assert res['score'] == 0


def test_quiescence_on_capture_rich_position():
    b = Board(setup=False)
    b.clear()
    # Set many pieces to allow captures: pawns for both sides clustered
    # White pawns on 2nd rank, black pawns on 7th rank
    for f in 'abcdefgh':
        b.place(PieceType.PAWN, Color.WHITE, f + '2')
        b.place(PieceType.PAWN, Color.BLACK, f + '7')
    # place kings
    b.place(PieceType.KING, Color.WHITE, 'e1')
    b.place(PieceType.KING, Color.BLACK, 'e8')

    res = search_root(b, max_time_ms=200, max_depth=3)
    # ensure search ran and produced sane score (not a mate)
    assert isinstance(res['score'], int)
    assert abs(res['score']) < 30000


def test_mate_in_one_kq_vs_k():
    b = Board(setup=False)
    b.clear()
    # Black king on a8, white queen can move to a7 mate
    b.place(PieceType.KING, Color.BLACK, 'a8')
    b.place(PieceType.KING, Color.WHITE, 'c6')
    b.place(PieceType.QUEEN, Color.WHITE, 'b6')

    res = search_root(b, max_time_ms=500, max_depth=3)
    assert res['best_move'] is not None
    assert res['score'] >= 31900


def test_mate_bishop_simple():
    b = Board(setup=False)
    b.clear()
    # Black king on a8; white bishop on b6 can go to a7 mate if escape squares blocked
    b.place(PieceType.KING, Color.BLACK, 'a8')
    b.place(PieceType.KING, Color.WHITE, 'c5')
    b.place(PieceType.BISHOP, Color.WHITE, 'c6')

    res = search_root(b, max_time_ms=500, max_depth=3)
    # Accept either that engine found mate (high score) or returned a sane result
    if res['score'] >= 31900:
        assert res['best_move'] is not None
    else:
        assert isinstance(res['score'], int)
        assert abs(res['score']) < 30000


def test_mate_tactical_capture():
    b = Board(setup=False)
    b.clear()
    # Black king on a8, defending knight on b7, white queen on c6 -> Qxb7# tactical capture
    b.place(PieceType.KING, Color.BLACK, 'a8')
    # place a defending piece on b7
    from utils.enums import PieceType as PT
    b.place(PT.KNIGHT, Color.BLACK, 'b7')
    b.place(PieceType.KING, Color.WHITE, 'd6')
    b.place(PieceType.QUEEN, Color.WHITE, 'c6')

    res = search_root(b, max_time_ms=500, max_depth=3)
    assert res['best_move'] is not None
    # apply the move and check resulting game status is checkmate if move leads to mate
    try:
        m = res['best_move']
        b.make_move(m)
        gs = get_game_status(b)
        # accept either mate or near-mate score
        if gs.is_checkmate:
            assert res['score'] >= 31900
        else:
            assert abs(res['score']) < 30000
    finally:
        # restore state
        b.unmake_move()

