# interface/cli/main.py
"""
Textual TUI (layout C) para Xadrez_AI_Final

Comandos:
    show              - exibe tabuleiro
    history           - exibe histórico de movimentos e motivo do término
    move e2e4         - executa movimento em UCI/LAN
    undo              - desfaz último movimento
    play tico teco    - autoplay entre 2 engines
    stop              - para autoplay
    perft 3           - calcula perft
    set <fen>         - carrega posição em FEN
    quit/exit         - sai

Rodar:
    python -m interface.cli.main
    python -m interface.cli.main --safe  (usa StubBoard)
"""
from __future__ import annotations

import argparse
import asyncio
import random
from typing import Optional

from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Header, Footer
from textual.reactive import reactive

from rich.panel import Panel
from rich.text import Text

# ============================================================
# Argumentos CLI
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(description="ChessTUI")
    return parser.parse_args()


# ============================================================
# Imports do projeto
# ============================================================

try:
    from core.moves.legal_movegen import generate_legal_moves
except Exception:
    def generate_legal_moves(board):  # fallback
        return []

try:
    from core.rules.draw_repetition import is_insufficient_material, is_fifty_move_rule
except Exception:
    def is_insufficient_material(board):
        return False
    def is_fifty_move_rule(board):
        return False


try:
    from utils.enums import PieceType, Color
    PIECE_CHAR = {
        PieceType.PAWN: 'P',
        PieceType.KNIGHT: 'N',
        PieceType.BISHOP: 'B',
        PieceType.ROOK: 'R',
        PieceType.QUEEN: 'Q',
        PieceType.KING: 'K',
    }
except Exception:
    class Color:
        WHITE = 0
        BLACK = 1

    class PieceType:
        PAWN = 0
        KNIGHT = 1
        BISHOP = 2
        ROOK = 3
        QUEEN = 4
        KING = 5

    PIECE_CHAR = {
        PieceType.PAWN: 'P',
        PieceType.KNIGHT: 'N',
        PieceType.BISHOP: 'B',
        PieceType.ROOK: 'R',
        PieceType.QUEEN: 'Q',
        PieceType.KING: 'K',
    }


# ============================================================
# UI / Render helpers moved to `interface.tui.renderer`
# ============================================================

from interface.tui.renderer import BoardPanel, Color, PlayerStatsHeader, HelpBar
from interface.tui.game_history import GameHistory, format_game_summary
from interface.tui.game_setup import GameSetupScreen


# ============================================================
# Main Application
# ============================================================

class ChessTUI(App):
    CSS_PATH = None
    BINDINGS = [("q", "quit", "Quit")]
    
    CSS = """
    #stats_header {
        dock: top;
        height: auto;
        margin: 0;
    }
    
    #board {
        /* narrower horizontally, tall vertically */
        width: 40;
        height: 1fr;
        border: thick $accent;
    }
    
    #cmd {
        dock: bottom;
        width: 60;
        margin: 1 0;
    }
    
    #spacer {
        /* keep small so board can expand vertically */
        height: 1;
    }
    
    #setup_screen {
        display: block;
    }
    
    GameSetupScreen {
        display: none;
    }
    """

    def __init__(self, board=None, **kwargs):
        super().__init__(**kwargs)
        self.board = board
        self.play_task: Optional[asyncio.Task] = None
        self.playing = False
        self.game_over = False  # Rastrear se o jogo terminou
        self.history = GameHistory()  # Rastrear movimentos
        self.setup_done = False  # Rastrear se a configuração foi feita
        
        # Estatísticas dos jogadores
        self.white_wins = 0
        self.white_losses = 0
        self.black_wins = 0
        self.black_losses = 0
        # Unified draws counter (global)
        self.draws = 0

    # --------------------------------------------------------

    def compose(self) -> ComposeResult:
        from textual.widgets import Static
        yield GameSetupScreen(id="setup_screen")
        yield Header()
        yield PlayerStatsHeader(id="stats_header")
        yield BoardPanel(id="board")
        # Espaçador para empurrar comando para baixo
        yield Static(expand=True, id="spacer")
        # Linha de ajuda com comandos disponíveis
        yield HelpBar(id="help_bar")
        yield Input(
            placeholder="comando > ",
            id="cmd"
        )
        yield Footer()

    # --------------------------------------------------------

    async def on_mount(self):
        self.board_panel: BoardPanel = self.query_one("#board")
        self.stats_header: PlayerStatsHeader = self.query_one("#stats_header")
        self.help_bar: HelpBar = self.query_one("#help_bar")
        self.cmd: Input = self.query_one("#cmd")
        self.setup_screen: GameSetupScreen = self.query_one("#setup_screen")

        if self.board is None:
            # Board real
            try:
                from core.board.board import Board as BoardClass
                self.board = BoardClass()
            except Exception as e:
                # if core board cannot be loaded, abort with a clear message
                raise RuntimeError(
                    f"Erro ao carregar Board real. Remova o StubBoard e certifique-se de que 'core.board' está disponível: {e}"
                )

        # Show setup screen first
        self._show_setup_screen()

    def _show_setup_screen(self):
        """Show the game setup screen and hide the game board"""
        self.setup_screen.display = True
        self.board_panel.display = False
        self.stats_header.display = False
        self.help_bar.display = False
        self.cmd.display = False

    def _show_game_screen(self):
        """Show the game screen and hide the setup screen"""
        self.setup_screen.display = False
        self.board_panel.display = True
        self.stats_header.display = True
        self.help_bar.display = True
        self.cmd.display = True
        self.cmd.focus()
        self.update_ui()

    def on_game_setup_screen_game_setup_complete(self, event: GameSetupScreen.GameSetupComplete) -> None:
        """Handle game setup completion"""
        white_player = event.white_player
        black_player = event.black_player
        
        # Create game manager based on selected players
        self._start_game_from_setup(white_player, black_player)

    def on_game_setup_screen_game_setup_cancelled(self, event: GameSetupScreen.GameSetupCancelled) -> None:
        """Handle game setup cancellation"""
        # Reset to setup screen
        self._show_setup_screen()

    def _start_game_from_setup(self, white_type: str, black_type: str):
        """Start a game based on player types from setup screen"""
        try:
            from game_manager import GameManager, GameMode
        except Exception as e:
            print(f"Erro: game_manager não disponível - {e}")
            return

        # Map player types to game modes
        # Note: GameMode only has 6 modes, so we map combinations accordingly
        mode_map = {
            ("human", "human"): GameMode.HUMAN_VS_HUMAN,
            ("human", "random"): GameMode.HUMAN_VS_RANDOM,
            ("human", "engine"): GameMode.HUMAN_VS_ENGINE,
            ("random", "human"): GameMode.HUMAN_VS_RANDOM,  # Use same as human vs random (human is white)
            ("random", "random"): GameMode.RANDOM_VS_RANDOM,
            ("random", "engine"): GameMode.RANDOM_VS_ENGINE,
            ("engine", "human"): GameMode.HUMAN_VS_ENGINE,  # Similar setup
            ("engine", "random"): GameMode.RANDOM_VS_ENGINE,  # Similar setup
            ("engine", "engine"): GameMode.ENGINE_VS_ENGINE,
        }
        
        key = (white_type, black_type)
        if key not in mode_map:
            # Fallback to human vs human
            mode = GameMode.HUMAN_VS_HUMAN
        else:
            mode = mode_map[key]
        
        try:
            # Create game manager with the selected mode
            self.game_manager = GameManager.from_mode(
                mode,
                engine_depth=3,
                engine_time_ms=1000
            )
            
            # Reset board and game state (preserve history across app lifetime)
            self.board = self.game_manager.board
            self.game_over = False
            # history preserved intentionally
            self.playing = True
            
            # Show game screen
            self._show_game_screen()
            
            # Print mode info
            player_names = {
                "human": "Humano",
                "random": "Random",
                "engine": "Engine"
            }
            
            print(f"Iniciando jogo: {player_names[white_type]} vs {player_names[black_type]}")
            print(f"White: {self.game_manager.white_agent.name()}")
            print(f"Black: {self.game_manager.black_agent.name()}")
            
            # Start game loop for non-human players
            if white_type != "human" or black_type != "human":
                asyncio.create_task(self.run_game_manager_loop())

        except Exception as e:
            print(f"Erro ao iniciar jogo: {e}")
            self.playing = False
            # Return to setup screen
            self._show_setup_screen()

    # --------------------------------------------------------

    def update_ui(self):
        self.board_panel.board = self.board
        self.board_panel.refresh()

    # --------------------------------------------------------

    def update_stats_display(self):
        """Atualiza o header com as estatísticas atuais."""
        # Always try to get the current widget instance from the DOM to
        # avoid updating a stale reference. This ensures the visible
        # `PlayerStatsHeader` instance gets updated and refreshed.
        try:
            try:
                header = self.query_one("#stats_header")
            except Exception:
                header = getattr(self, 'stats_header', None)

            # Debug: log the header instance and current scores
            try:
                print(f"[DEBUG] update_stats_display -> header={id(header) if header else None} W={self.white_wins} L={self.white_losses} D={self.draws} | bW={self.black_wins} bL={self.black_losses}")
            except Exception:
                pass

            if header is None:
                return

            # Prepare updater function to run on the UI thread
            def _do_update():
                try:
                    header.update_stats(
                        white_wins=self.white_wins,
                        white_losses=self.white_losses,
                        draws=self.draws,
                        black_wins=self.black_wins,
                        black_losses=self.black_losses,
                    )
                    try:
                        header.refresh()
                    except Exception:
                        pass
                except Exception:
                    pass

            # Try to schedule on the running asyncio loop; if unavailable,
            # call directly as a fallback.
            try:
                import asyncio as _asyncio
                loop = _asyncio.get_running_loop()
            except Exception:
                loop = None

            if loop is not None:
                try:
                    loop.call_soon_threadsafe(_do_update)
                except Exception:
                    _do_update()
            else:
                _do_update()
        except Exception:
            pass

    def record_game_result(self, result: str):
        """
        Registra o resultado do jogo.
        result: "white_win", "black_win", "draw"
        """
        # debug log when recording result
        try:
            print(f"[DEBUG] record_game_result called with: {result}")
        except Exception:
            pass

        if result == "white_win":
            self.white_wins += 1
            self.black_losses += 1
        elif result == "black_win":
            self.black_wins += 1
            self.white_losses += 1
        elif result == "draw":
            # Increment unified draws counter only
            self.draws += 1
            try:
                print(f"[DEBUG] record_game_result -> draws incremented to {self.draws}")
            except Exception:
                pass
        
        # Ensure UI update happens on the event loop thread
        try:
            import asyncio as _asyncio
            loop = _asyncio.get_running_loop()
            try:
                loop.call_soon_threadsafe(self.update_stats_display)
            except Exception:
                # fallback to direct call
                self.update_stats_display()
        except Exception:
            # If no running loop, call directly
            try:
                self.update_stats_display()
            except Exception:
                pass

    def _apply_result_from_reason(self, reason: str, board=None):
        """Interpret a termination reason / board state and update the scoreboard.

        This centralizes logic so every code path uses the same mapping.
        """
        try:
            r = (reason or "").lower()
            if "checkmate" in r:
                if board is not None:
                    if board.side_to_move == Color.WHITE:
                        self.record_game_result("black_win")
                    else:
                        self.record_game_result("white_win")
                else:
                    # fallback: assume draw if we can't determine
                    self.record_game_result("draw")
            elif "stalemate" in r or "no legal moves" in r or "no legal" in r:
                self.record_game_result("draw")
            elif "50" in r or "fifty" in r or "repetition" in r or "insufficient" in r:
                self.record_game_result("draw")
            else:
                # try to introspect board
                if board is not None:
                    try:
                        from core.rules.game_status import get_game_status
                        status = get_game_status(board)
                        if status.is_checkmate:
                            if board.side_to_move == Color.WHITE:
                                self.record_game_result("black_win")
                            else:
                                self.record_game_result("white_win")
                        elif status.is_stalemate or status.is_draw_by_fifty_move or status.is_draw_by_repetition or status.is_insufficient_material:
                            self.record_game_result("draw")
                    except Exception:
                        pass
        except Exception:
            pass

    # --------------------------------------------------------

    def check_and_report_game_status(self):
        """Verifica todas as regras de término e loga o status."""
        # Verificar material insuficiente
        if is_insufficient_material(self.board):
            msg = "Empate por material insuficiente"
            self.history.set_game_end(
                reason=msg,
                fullmove=self.board.fullmove_number,
                is_insufficient_material=True
            )
            self.stats_header.set_draw_reason(msg)
            self.record_game_result("draw")
            self.game_over = True
            return True
        
        # Verificar 50 lances
        if is_fifty_move_rule(self.board):
            msg = "Empate pela regra dos 50 lances"
            self.history.set_game_end(
                reason=msg,
                fullmove=self.board.fullmove_number,
                is_fifty_move=True
            )
            self.stats_header.set_draw_reason(msg)
            self.record_game_result("draw")
            self.game_over = True
            return True
        
        # Verificar xeque-mate e afogamento
        try:
            from interface.tui.commands import check_game_status
            status, is_over = check_game_status(self.board, generate_legal_moves, self.board.is_in_check)
            if is_over:
                
                # Determinar tipo de fim
                is_checkmate = "Xeque-mate" in status
                is_stalemate = "afogamento" in status.lower()
                
                self.history.set_game_end(
                    reason=status,
                    fullmove=self.board.fullmove_number,
                    is_checkmate=is_checkmate,
                    is_stalemate=is_stalemate
                )
                
                # Registrar resultado
                if is_checkmate:
                    # Se White está em check mate, Black venceu
                    if self.board.side_to_move == Color.WHITE:
                        self.record_game_result("black_win")
                    else:
                        self.record_game_result("white_win")
                elif is_stalemate:
                    self.stats_header.set_draw_reason("Stalemate")
                    self.record_game_result("draw")
                
                self.game_over = True
                return True
        except Exception:
            pass
        
        return False

    # --------------------------------------------------------

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        self.cmd.value = ""
        await self.handle_command(cmd)

    # --------------------------------------------------------

    async def handle_command(self, cmd: str):
        if not cmd:
            return
        
        # Se o jogo terminou, só permitir certos comandos
        if self.game_over and cmd.lower() not in ("quit", "exit", "undo", "set", "show", "history"):
            return

        parts = cmd.split()
        c = parts[0].lower()

        # allow users to type a LAN/UCI move directly (e.g. "e2e4")
        try:
            from interface.tui.commands import is_move_format
        except Exception:
            def is_move_format(_: str) -> bool:
                return False

        if is_move_format(c):
            # treat bare move like 'move <lan>'
            await self.cmd_move(c)
            return

        if c == "show":
            self.update_ui()

        elif c == "help":
            # show a more detailed help text in the help bar
            try:
                detailed = (
                    "[b]Comandos disponíveis:[/]\n"
                    "\n[b]Movimentos:[/]\n"
                    " - move <lan>: executa movimento (ex: e2e4)\n"
                    " - undo: desfaz último movimento\n"
                    "\n[b]Modos de Jogo:[/]\n"
                    " - 1: Human vs Human\n"
                    " - 2: Human vs Random\n"
                    " - 3: Human vs Engine\n"
                    " - 4: Random vs Random\n"
                    " - 5: Random vs Engine\n"
                    " - 6: Engine vs Engine\n"
                    "\n[b]Outros:[/]\n"
                    " - show: atualiza a tela\n"
                    " - history: exibe histórico\n"
                    " - play <p1> <p2>: autoplay (legado)\n"
                    " - stop: interrompe autoplay\n"
                    " - perft <n>: calcula perft\n"
                    " - set <fen>: carrega FEN\n"
                    " - help: mostra esta ajuda\n"
                    " - quit / exit: sai\n"
                )
                if hasattr(self, 'help_bar'):
                    self.help_bar.update_help(detailed)
            except Exception:
                pass

        elif c == "history":
            try:
                summary = format_game_summary(self.history)
                print(summary)
            except Exception as e:
                print(f"Erro ao mostrar histórico: {e}")

        elif c == "move" and len(parts) >= 2:
            await self.cmd_move(parts[1])

        elif c == "undo":
            try:
                self.board.unmake_move()
                self.history.pop_move()
                self.history.undo_game_end()
                self.game_over = False
                self.update_ui()
            except Exception:
                pass

        # Game mode commands: 1-6
        elif c in ("1", "2", "3", "4", "5", "6"):
            await self.cmd_game_mode(c)

        elif c == "play" and len(parts) >= 3:
            await self.start_auto_play(parts[1], parts[2])

        elif c == "stop":
            await self.stop_auto_play()

        elif c == "perft" and len(parts) >= 2:
            try:
                await self.run_perft(int(parts[1]))
            except Exception:
                pass

        elif c == "set" and len(parts) >= 2:
            await self.set_fen(" ".join(parts[1:]))

        elif c in ("quit", "exit"):
            await self.action_quit()

    # --------------------------------------------------------

    async def cmd_move(self, lan: str):
        """Execute a move given in LAN/UCI using shared `find_move` logic."""
        try:
            # use the centralized finder to improve robustness
            try:
                from interface.tui.commands import find_move
            except Exception:
                find_move = None

            move_obj = None
            if find_move is not None:
                move_obj = find_move(self.board, lan, generate_legal_moves)

            # fallback if finder not available
            if move_obj is None:
                if hasattr(self.board, "parse_move"):
                    try:
                        move_obj = self.board.parse_move(lan)
                    except Exception:
                        move_obj = None
                else:
                    for m in generate_legal_moves(self.board):
                        if str(m).lower().startswith(lan.lower()):
                            move_obj = m
                            break

            if move_obj is None:
                return

            # Registrar movimento antes de fazer
            stm = self.board.side_to_move
            move_uci = move_obj.to_uci() if hasattr(move_obj, 'to_uci') else str(move_obj)

            self.board.make_move(move_obj)
            
            # Adicionar ao histórico
            self.history.add_move(
                side=int(stm),
                move_uci=move_uci,
                fullmove=self.board.fullmove_number,
                halfmove_clock=self.board.halfmove_clock
            )
            
            self.update_ui()
            
            # Verificar se o jogo terminou após o movimento
            self.check_and_report_game_status()

        except Exception as e:
            pass

    # --------------------------------------------------------

    async def cmd_game_mode(self, mode_num: str):
        """Start a game with the selected game mode (1-6)."""
        try:
            from game_manager import GameManager, GameMode
        except Exception:
            print("Erro: game_manager não disponível")
            return

        mode_map = {
            "1": GameMode.HUMAN_VS_HUMAN,
            "2": GameMode.HUMAN_VS_RANDOM,
            "3": GameMode.HUMAN_VS_ENGINE,
            "4": GameMode.RANDOM_VS_RANDOM,
            "5": GameMode.RANDOM_VS_ENGINE,
            "6": GameMode.ENGINE_VS_ENGINE,
        }

        if mode_num not in mode_map:
            print(f"Modo inválido. Use 1-6")
            return

        mode = mode_map[mode_num]
        
        try:
            # Create game manager with the selected mode
            self.game_manager = GameManager.from_mode(
                mode,
                engine_depth=3,
                engine_time_ms=1000
            )
            
            # Reset board and game state (preserve history across app lifetime)
            self.board = self.game_manager.board
            self.game_over = False
            # history preserved intentionally
            self.playing = True
            
            # Show mode info
            mode_names = {
                "1": "Human vs Human",
                "2": "Human vs Random",
                "3": "Human vs Engine",
                "4": "Random vs Random",
                "5": "Random vs Engine",
                "6": "Engine vs Engine",
            }
            print(f"Iniciando jogo: {mode_names[mode_num]}")
            print(f"White: {self.game_manager.white_agent.name()}")
            print(f"Black: {self.game_manager.black_agent.name()}")
            
            # Start game loop for non-human players (run in background so command returns)
            if mode_num in ("4", "5", "6"):  # Random/Engine modes
                asyncio.create_task(self.run_game_manager_loop())
            elif mode_num == "2":  # Human vs Random
                # White is human, black is random
                # Wait for human input for white
                pass
            elif mode_num == "3":  # Human vs Engine
                # White is human, black is engine
                pass
            
            self.update_ui()

        except Exception as e:
            print(f"Erro ao iniciar modo de jogo: {e}")
            self.playing = False

    async def run_game_manager_loop(self):
        """Run a game loop using GameManager for non-human players."""
        try:
            # Continue playing matches while `self.playing` is True.
            # After each finished match, if both agents are non-human, restart after 3s.
            while self.playing:
                move_count = 0
                # run a single match until game_over or playing is cancelled
                while self.playing and not self.game_manager.game_over and move_count < 200:
                    move = await self.game_manager.get_next_move()

                    if not move:
                        self.game_manager.game_over = True
                        self.game_manager.termination_reason = "No legal move"
                        break

                    await self.game_manager.play_move(move)
                    # let game manager update its status
                    self.game_manager.check_game_over()

                    # Update UI with each move
                    self.update_ui()

                    move_count += 1

                    # Small delay to show moves and yield to event loop
                    await asyncio.sleep(0.1)

                # Match ended or playing cancelled
                if self.game_manager.game_over:
                    print(f"\nJogo terminado: {self.game_manager.termination_reason}")
                    result = self.game_manager.get_result()
                    print(f"Resultado: {result}")

                    # Update scoreboard using central helper
                    try:
                        self._apply_result_from_reason(self.game_manager.termination_reason, self.game_manager.board)
                    except Exception:
                        pass

                # Update UI for final position
                self.update_ui()

                # Decide if we should auto-restart: only when both agents are non-human
                try:
                    from agents import HumanAgent
                    white_is_human = isinstance(self.game_manager.white_agent, HumanAgent)
                    black_is_human = isinstance(self.game_manager.black_agent, HumanAgent)
                except Exception:
                    # If we cannot import HumanAgent, conservatively do not auto-restart
                    white_is_human = True
                    black_is_human = True

                both_non_human = (not white_is_human) and (not black_is_human)

                if both_non_human and self.playing:
                    # wait 3 seconds before restarting
                    try:
                        await asyncio.sleep(3)
                    except asyncio.CancelledError:
                        break

                    # reset the board to start position (prefer set_startpos if available)
                    try:
                        if hasattr(self.game_manager.board, 'set_startpos'):
                            self.game_manager.board.set_startpos()
                        else:
                            # create a fresh Board instance
                            from core.board.board import Board as BoardClass
                            self.game_manager.board = BoardClass()

                        # sync TUI board reference
                        self.board = self.game_manager.board

                        # preserve history across matches; only reset flags
                        pass

                        self.game_manager.game_over = False
                        self.game_manager.termination_reason = None
                        # loop will continue and start a new match
                        continue
                    except Exception as e:
                        print(f"Erro ao reiniciar partida: {e}")
                        break
                else:
                    # do not auto-restart; end loop
                    self.playing = False
                    break

        except Exception as e:
            print(f"Erro no game manager loop: {e}")
            self.playing = False

    # --------------------------------------------------------

    async def start_auto_play(self, p1: str, p2: str):
        if self.playing:
            return

        self.playing = True

        async def choose_player(name, board):
            # Prefer adapter in `interface.tui.players` which delegates to engine
            try:
                from interface.tui.players import choose_move as adapter_choose
                # adapter_choose is async and offloads heavy work to a thread
                mv = await adapter_choose(name, board, max_time_ms=1000, max_depth=3)
                if mv is not None:
                    return mv
            except Exception:
                pass

            try:
                mod = __import__(name)
                if hasattr(mod, "choose_move"):
                    return mod.choose_move(board)
            except Exception:
                pass

            # fallback: aleatório
            moves = list(generate_legal_moves(board))
            return random.choice(moves) if moves else None

        async def loop():
            while self.playing:
                stm = Color.WHITE if self.board.side_to_move == Color.WHITE else Color.BLACK
                name = p1 if stm == Color.WHITE else p2

                move = await choose_player(name, self.board)
                if not move:
                    self.playing = False
                    break

                self.board.make_move(move)
                self.update_ui()

                # Verificar se jogo terminou após movimento
                self.check_and_report_game_status()
                if self.game_over:
                    # wait 3 seconds, then restart the match if autoplay still active
                    try:
                        await asyncio.sleep(3)
                    except asyncio.CancelledError:
                        break

                    if not self.playing:
                        break

                    # reset board to startpos if available, else clear
                    try:
                        if hasattr(self.board, 'set_startpos'):
                            self.board.set_startpos()
                        elif hasattr(self.board, 'clear'):
                            self.board.clear()
                    except Exception:
                        pass

                    # clear draw reason, reset flags and UI (preserve history)
                    try:
                        if hasattr(self, 'stats_header'):
                            self.stats_header.clear_draw_reason()
                    except Exception:
                        pass

                    self.game_over = False
                    self.update_ui()
                    # continue autoplayer loop with fresh position
                    continue

                await asyncio.sleep(0.05)

        self.play_task = asyncio.create_task(loop())

    # --------------------------------------------------------

    async def stop_auto_play(self):
        if not self.playing:
            return
        self.playing = False
        if self.play_task:
            self.play_task.cancel()

    # --------------------------------------------------------

    async def run_perft(self, depth: int):
        try:
            from core.perft.perft import perft
            nodes = perft(self.board, depth)
            print(f"Perft({depth}) = {nodes}")
        except Exception as e:
            print(f"Erro ao executar perft: {e}")

    # --------------------------------------------------------

    async def set_fen(self, fen: str):
        try:
            if hasattr(self.board, "set_fen"):
                self.board.set_fen(fen)
            elif hasattr(self.board, "load_fen"):
                self.board.load_fen(fen)
            else:
                return

            self.game_over = False
            self.history.clear()
            self.stats_header.clear_draw_reason()
            self.update_ui()

        except Exception as e:
            print(f"Erro ao carregar FEN: {e}")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    # start the TUI (always use the real Board implementation)
    app = ChessTUI()
    app.run()
