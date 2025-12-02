"""Minimal Tk application for Xadrez_AI_Final.

Provides `TkChessApp` which composes a `BoardWidget` and `ControlPanel`.
This is intentionally lightweight so it can be extended to hook into
the existing engine/training modules.
"""
from __future__ import annotations
import sys
try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:  # pragma: no cover - import-time for environments without display
    tk = None

from .board_widget import BoardWidget
from .control_panel import ControlPanel
from .start_screen import StartScreen
import random
try:
    from agents.nn_agent import NeuralAgent, list_available_models
except Exception:
    NeuralAgent = None
    list_available_models = None
try:
    from agents.mcts_agent import MCTSAgent
except Exception:
    MCTSAgent = None

try:
    from core.moves.legal_movegen import generate_legal_moves
except Exception:
    def generate_legal_moves(board):
        return []

try:
    from interface.tui.commands import check_game_status
except Exception:
    def check_game_status(board, a, b):
        return "Desconhecido", False

from utils.enums import Color
import re
import threading
import traceback


class TkChessApp:
    """Main Tk application.

    Public methods:
    - build_ui(): create and layout widgets
    - on_new_game(): reset board / start new game
    - on_run_selfplay(): start a short self-play (placeholder)
    - on_train_step(): run one training iteration (placeholder)
    - run(): enter Tk mainloop (if app owns root)
    """

    def __init__(self, root: 'tk.Tk | None' = None):
        if tk is None:
            raise RuntimeError('tkinter not available in this environment')

        if root is None:
            self._root = tk.Tk()
            self._own_root = True
        else:
            self._root = root
            self._own_root = False

        self._root.title('Xadrez AI - Tk Interface')
        self.board: BoardWidget | None = None
        self.controls: ControlPanel | None = None
        self.start_screen: StartScreen | None = None
        self._main_frame: 'tk.Frame | None' = None
        # scoreboard
        self.score_white = 0
        self.score_black = 0
        self.score_draws = 0

        # agent instances for AI players (optional)
        self.player_white_agent = None
        self.player_black_agent = None

        # show start/setup screen first
        self.show_start_screen()
        # runtime game objects
        self.game_board = None
        self.player_white = None
        self.player_black = None
        self._auto_running = False
        # threading state for background thinking
        self._thinking = False

    def build_ui(self):
        # destroy previous main frame to avoid duplicate packing
        if self._main_frame is not None:
            try:
                self._main_frame.destroy()
            except Exception:
                pass
        self._main_frame = tk.Frame(self._root)
        self._main_frame.pack(fill='both', expand=True)

        self.board = BoardWidget(self._main_frame, square_size=48)
        self.board.pack(side='left', padx=8, pady=8)
        # draw initial position
        try:
            self.board.set_position(None)
        except Exception:
            pass

        self.controls = ControlPanel(self._main_frame, callbacks={
            'new_game': self.on_new_game,
            'menu': self.show_start_screen,
            'selfplay': self.on_run_selfplay,
            'train_step': self.on_train_step,
            'quit': self._root.quit,
            'reset_score': self.reset_score,
        })
        self.controls.pack(side='right', fill='y', padx=8, pady=8)
        # initialize display
        try:
            self.controls.set_score(self.score_white, self.score_black, self.score_draws)
        except Exception:
            pass

    def show_start_screen(self):
        # if already showing start screen, do nothing
        if self.start_screen is not None:
            return

        # destroy main UI if present
        if self._main_frame is not None:
            try:
                self._main_frame.destroy()
            except Exception:
                pass
            self._main_frame = None

        # create and show start screen
        self.start_screen = StartScreen(self._root, start_callback=self._on_start_game)
        self.start_screen.pack(fill='both', expand=True, padx=12, pady=12)

    def _on_start_game(self, white_choice: str, black_choice: str, model_choice: str = None):
        """Callback from StartScreen: create main UI and start match with selections.

        For now this prints the selections and shows the main board UI. Integration
        with real player classes is a next step.
        """
        print(f'[TkChessApp] Starting game: White={white_choice}, Black={black_choice}')
        # remove start screen
        if self.start_screen:
            try:
                self.start_screen.destroy()
            except Exception:
                pass
            self.start_screen = None

        # build main UI and start
        self.build_ui()
        # initialize game board and players
        try:
            from core.board.board import Board
            self.game_board = Board()
        except Exception:
            self.game_board = None

        # wire board widget to this game board
        if self.board and self.game_board is not None:
            try:
                self.board.set_position(self.game_board)
                # connect click handler for human input
                self.board.set_click_callback(self._on_board_click)
            except Exception:
                pass

        # Map choices to simple handlers: 'Human'|'Random'|'AI'
        # keep simple string marker for runtime checks, and also create
        # optional Agent instances for AI players when a model is selected.
        self.player_white = white_choice
        self.player_black = black_choice
        self.player_white_agent = None
        self.player_black_agent = None

        # if a model_choice is provided, try to resolve checkpoint path
        ck_map = {}
        try:
            if list_available_models is not None:
                for name, ck in list_available_models():
                    ck_map[name] = ck
        except Exception:
            ck_map = {}

        # instantiate MCTSAgent (preferred) or NeuralAgent for AI players when possible
        if model_choice:
            ck_path = ck_map.get(model_choice)
            try:
                if MCTSAgent is not None:
                    if white_choice == 'AI':
                        self.player_white_agent = MCTSAgent(model_path=ck_path)
                    if black_choice == 'AI':
                        self.player_black_agent = MCTSAgent(model_path=ck_path)
                elif NeuralAgent is not None:
                    if white_choice == 'AI':
                        self.player_white_agent = NeuralAgent(model_path=ck_path)
                    if black_choice == 'AI':
                        self.player_black_agent = NeuralAgent(model_path=ck_path)
            except Exception:
                # fallback to no agent instance
                self.player_white_agent = None
                self.player_black_agent = None

        # start the non-blocking game loop (will wait for human moves when needed)
        self._auto_running = True
        try:
            self._root.after(200, self._step)
        except Exception:
            pass

    def _on_board_click(self, square_idx: int):
        """Handle user clicks from `BoardWidget` for human move entry.

        We implement a two-click interface: first click selects from-square,
        second click selects to-square and attempts to play a legal move.
        """
        if self.game_board is None:
            return

        stm = self.game_board.side_to_move
        # determine if it's human's turn
        current_player = self.player_white if stm == Color.WHITE else self.player_black
        if current_player != 'Human':
            return

        # two-click selection state stored on controls for simplicity
        sel = getattr(self, '_human_sel_from', None)
        if sel is None:
            # first click: record source if there's a piece belonging to player
            cell = self.game_board.get_piece_at(square_idx)
            if cell is None:
                return
            color, _ = cell
            if int(color) != int(stm):
                return
            self._human_sel_from = square_idx
            # optionally could highlight square; for now, just print
            print(f'[TkChessApp] selected from {square_idx}')
            return
        else:
            # second click: attempt move from sel -> square_idx
            from_sq = sel
            to_sq = square_idx
            # clear selection
            self._human_sel_from = None

            # find legal move matching from->to
            try:
                legal = list(generate_legal_moves(self.game_board))
            except Exception:
                legal = []

            candidate = None
            for m in legal:
                try:
                    if m.from_sq == from_sq and m.to_sq == to_sq:
                        candidate = m
                        break
                except Exception:
                    pass

            if candidate is None:
                print('[TkChessApp] no legal move for that selection')
                return

            # apply move
            try:
                self.game_board.make_move(candidate)
            except Exception as e:
                print('[TkChessApp] error applying move:', e)
                return

            # update UI
            try:
                if self.board:
                    self.board.set_position(self.game_board)
            except Exception:
                pass

            # check status and possibly finish
            msg, ended = check_game_status(self.game_board, generate_legal_moves, self.game_board.is_in_check)
            print('[TkChessApp] status after human move:', msg)
            if ended:
                # determine winner: if mate -> winner is side that just moved (opposite of side_to_move)
                if self._is_mate_message(msg):
                    winner = 'white' if self.game_board.side_to_move == Color.BLACK else 'black'
                    self.record_result(winner)
                else:
                    self.record_result('draw')
                # stop auto-run
                self._auto_running = False
            else:
                # schedule next step (opponent may be random/AI)
                try:
                    self._root.after(100, self._step)
                except Exception:
                    pass

    def _step(self):
        """Advance the game one step for non-human players. Non-blocking via `after()`.

        If it's a human turn, do nothing and wait for clicks. If player is 'Random', pick
        a legal move and play it, then re-schedule.
        """
        if not self._auto_running or self.game_board is None:
            return

        stm = self.game_board.side_to_move
        current_player = self.player_white if stm == Color.WHITE else self.player_black

        # if human, wait for input
        if current_player == 'Human':
            return

        # get legal moves
        try:
            legal = list(generate_legal_moves(self.game_board))
        except Exception:
            legal = []

        if not legal:
            msg, ended = check_game_status(self.game_board, generate_legal_moves, self.game_board.is_in_check)
            print('[TkChessApp] game ended:', msg)
            if ended:
                if self._is_mate_message(msg):
                    winner = 'white' if self.game_board.side_to_move == Color.BLACK else 'black'
                    self.record_result(winner)
                else:
                    self.record_result('draw')
            self._auto_running = False
            return

        # random player: pick uniformly
        if current_player == 'Random':
            mv = random.choice(legal)
            try:
                self.game_board.make_move(mv)
            except Exception as e:
                print('[TkChessApp] error applying random move:', e)
                self._auto_running = False
                return

            # update UI
            try:
                if self.board:
                    self.board.set_position(self.game_board)
            except Exception:
                pass

            # check status
            msg, ended = check_game_status(self.game_board, generate_legal_moves, self.game_board.is_in_check)
            print('[TkChessApp] status after random move:', msg)
            if ended:
                if self._is_mate_message(msg):
                    winner = 'white' if self.game_board.side_to_move == Color.BLACK else 'black'
                    self.record_result(winner)
                else:
                    self.record_result('draw')
                self._auto_running = False
                return

            # schedule next engine step
            try:
                self._root.after(150, self._step)
            except Exception:
                pass
            return

        # other player types (AI) — compute move in background thread to avoid blocking UI
        if current_player == 'AI':
            # start thinking thread if not already
            if not self._thinking:
                self._start_think_thread(current_player)
            return

        print('[TkChessApp] player type not implemented for automated play:', current_player)

    def _is_mate_message(self, msg: str) -> bool:
        """Return True if the status message indicates checkmate.

        Use word-boundary checks to avoid matching substrings like 'material'.
        """
        if not msg:
            return False
        m = msg.lower()
        # Portuguese/English checks: 'xeque-mate', 'checkmate', or standalone 'mate'
        if 'xeque-mate' in m or 'checkmate' in m:
            return True
        if re.search(r"\bmate\b", m):
            return True
        return False

    def _start_think_thread(self, player_type: str):
        """Spawn a thread to compute the next move for `player_type`.

        The worker computes the move on a copy of the board and posts the
        result back to the main thread via `after()` to apply it safely.
        """
        if self._thinking or self.game_board is None:
            return
        self._thinking = True

        def worker(board_snapshot, ptype):
            try:
                mv = None
                if ptype == 'Random':
                    from core.moves.legal_movegen import generate_legal_moves as gm
                    moves = list(gm(board_snapshot))
                    if moves:
                        import random as _r
                        mv = _r.choice(moves)
                elif ptype == 'AI':
                    # Prefer a NeuralAgent instance if one was created from StartScreen;
                    # otherwise fall back to EngineAgent search.
                    try:
                        agent = None
                        if board_snapshot is not None:
                            # choose agent according to side to move on the snapshot
                            try:
                                stm = board_snapshot.side_to_move
                                if int(stm) == int(Color.WHITE):
                                    agent = getattr(self, 'player_white_agent', None)
                                else:
                                    agent = getattr(self, 'player_black_agent', None)
                            except Exception:
                                agent = None

                        if agent is None:
                            from agents.engine_agent import EngineAgent
                            agent = EngineAgent()

                        # run agent.get_move (async) in this thread
                        import asyncio
                        mv = asyncio.run(agent.get_move(board_snapshot))
                    except Exception:
                        traceback.print_exc()
                        mv = None
                else:
                    mv = None
            except Exception:
                traceback.print_exc()
                mv = None

            # post back to main thread
            try:
                self._root.after(0, lambda: self._apply_move_from_thread(mv))
            except Exception:
                pass

        # prepare board snapshot
        try:
            board_copy = self.game_board.copy() if hasattr(self.game_board, 'copy') else None
        except Exception:
            board_copy = None

        th = threading.Thread(target=worker, args=(board_copy, player_type), daemon=True)
        th.start()

    def _apply_move_from_thread(self, mv):
        """Apply a move computed in background thread. Runs in main thread."""
        self._thinking = False
        if mv is None:
            # no move found — treat as game end or skip
            try:
                msg, ended = check_game_status(self.game_board, generate_legal_moves, self.game_board.is_in_check)
                print('[TkChessApp] background move: no move, status:', msg)
                if ended:
                    if self._is_mate_message(msg):
                        winner = 'white' if self.game_board.side_to_move == Color.BLACK else 'black'
                        self.record_result(winner)
                    else:
                        self.record_result('draw')
                    self._auto_running = False
                    return
            except Exception:
                pass
            # schedule next step
            try:
                self._root.after(150, self._step)
            except Exception:
                pass
            return

        # apply the move
        try:
            self.game_board.make_move(mv)
        except Exception as e:
            print('[TkChessApp] error applying move from thread:', e)
            return

        # update UI
        try:
            if self.board:
                self.board.set_position(self.game_board)
        except Exception:
            pass

        # check status
        try:
            msg, ended = check_game_status(self.game_board, generate_legal_moves, self.game_board.is_in_check)
            print('[TkChessApp] status after background move:', msg)
            if ended:
                if self._is_mate_message(msg):
                    winner = 'white' if self.game_board.side_to_move == Color.BLACK else 'black'
                    self.record_result(winner)
                else:
                    self.record_result('draw')
                self._auto_running = False
                return
        except Exception:
            pass

        # schedule next step
        try:
            self._root.after(150, self._step)
        except Exception:
            pass

    def on_new_game(self):
        """Reset the board to initial position.

        Integration point: hook into `SelfPlayWorker` or `game_manager` to start a new match.
        """
        if self.board:
            self.board.set_position(None)  # placeholder: implements empty/initial position
        print('[TkChessApp] New game requested')

    def record_result(self, winner: str):
        """Record the result of a finished game.

        `winner` should be one of: 'white', 'black', 'draw'. This method
        updates the internal scoreboard and refreshes the UI labels.
        """
        if winner == 'white':
            self.score_white += 1
        elif winner == 'black':
            self.score_black += 1
        elif winner == 'draw':
            self.score_draws += 1
        else:
            raise ValueError('winner must be: white, black, or draw')

        if self.controls:
            self.controls.set_score(self.score_white, self.score_black, self.score_draws)

    def reset_score(self):
        """Reset the in-memory scoreboard to zeros and update UI."""
        self.score_white = 0
        self.score_black = 0
        self.score_draws = 0
        if self.controls:
            self.controls.set_score(self.score_white, self.score_black, self.score_draws)

    def on_run_selfplay(self):
        """Start a short self-play run (non-blocking recommended).

        Currently a placeholder; integrate with `training.selfplay.SelfPlayWorker`.
        """
        print('[TkChessApp] Self-play started (placeholder)')
        messagebox.showinfo('Self-play', 'Self-play started (placeholder)')

    def on_train_step(self):
        """Trigger a single training iteration or a small batch update.

        Integrate with `training.trainer.train_loop` or `training.train_step`.
        """
        print('[TkChessApp] Training step triggered (placeholder)')
        messagebox.showinfo('Train', 'Training step triggered (placeholder)')

    def run(self):
        """Run the Tk mainloop if this app owns the root."""
        if self._own_root:
            self._root.mainloop()


if __name__ == '__main__':
    # When run as a script, construct app but avoid mainloop in headless environments
    try:
        app = TkChessApp()
        app.run()
    except RuntimeError as e:
        print('Cannot start Tk UI:', e, file=sys.stderr)
        sys.exit(1)
