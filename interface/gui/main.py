"""Aplicação principal pygame."""
import pygame
import threading
import time
import asyncio
from enum import Enum
from queue import Queue

from interface.gui.config import SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, MODES, DEFAULT_DEPTH, DEFAULT_TIME_MS
from interface.gui.screens.setup import SetupScreen
from interface.gui.screens.game import GameScreen
from interface.gui.screens.gameover import GameOverScreen

try:
    from core.board.board import Board
except:
    Board = None

try:
    from game_manager import GameManager, GameMode
except:
    GameManager = None


class State(Enum):
    SETUP = 1
    GAME = 2
    GAME_OVER = 3


class GUIApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Xadrez AI - GUI")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = State.SETUP
        
        self.board = None
        self.game_manager = None
        self.white_type = None
        self.black_type = None
        
        self.setup_screen = SetupScreen()
        self.game_screen = None
        self.gameover_screen = GameOverScreen()
        
        self.game_thread = None
        self.game_running = False
        self.paused = False
        self.event_queue = Queue()

    def start_game(self, mode_name):
        """Inicia uma partida com o modo selecionado."""
        if GameManager is None:
            print("Error: GameManager not available")
            return
        
        white_type, black_type = MODES[mode_name]
        self.white_type = white_type
        self.black_type = black_type
        
        try:
            # mapear tipo de jogador para GameMode
            mode_map = {
                ("human", "human"): GameMode.HUMAN_VS_HUMAN,
                ("human", "engine"): GameMode.HUMAN_VS_ENGINE,
                ("human", "random"): GameMode.HUMAN_VS_RANDOM,
                ("engine", "human"): GameMode.HUMAN_VS_ENGINE,
                ("engine", "engine"): GameMode.ENGINE_VS_ENGINE,
                ("engine", "random"): GameMode.RANDOM_VS_ENGINE,
                ("random", "human"): GameMode.HUMAN_VS_RANDOM,
                ("random", "engine"): GameMode.RANDOM_VS_ENGINE,
                ("random", "random"): GameMode.RANDOM_VS_RANDOM,
            }
            game_mode = mode_map.get((white_type, black_type), GameMode.HUMAN_VS_HUMAN)
            
            self.game_manager = GameManager.from_mode(
                game_mode,
                engine_depth=DEFAULT_DEPTH,
                engine_time_ms=DEFAULT_TIME_MS
            )
            self.board = self.game_manager.board
            self.game_screen = GameScreen(self.board, white_type, black_type)
            self.state = State.GAME
            
            if white_type != "human" or black_type != "human":
                self.game_running = True
                self.paused = False
                self.game_thread = threading.Thread(target=self.run_game_loop, daemon=True)
                self.game_thread.start()
        except Exception as e:
            print(f"Error starting game: {e}")

    def run_game_loop(self):
        """Loop de partida automática (roda em thread)."""
        try:
            move_count = 0
            while self.game_running and self.state == State.GAME:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # Verificar fim de jogo antes de pedir movimento
                if self._check_game_over():
                    break
                
                move_count += 1
                
                try:
                    if self.board.side_to_move == 0:  # White
                        agent = self.game_manager.white_agent
                    else:  # Black
                        agent = self.game_manager.black_agent
                    
                    # Se o agente é async, usar asyncio.run com timeout
                    if asyncio.iscoroutinefunction(agent.get_move):
                        try:
                            move = asyncio.run(asyncio.wait_for(agent.get_move(self.board), timeout=2.0))
                        except asyncio.TimeoutError:
                            move = None
                    else:
                        move = agent.get_move(self.board)
                except Exception as e:
                    move = None
                
                if not move:
                    self.event_queue.put(('game_over', 'draw', 'No legal moves'))
                    self.game_running = False
                    break
                
                self.board.make_move(move)
                self.game_screen.add_move(str(move))
                
                # Verificar fim de jogo após movimento
                if self._check_game_over():
                    break
                
                time.sleep(0.05)
        except Exception as e:
            pass
        finally:
            self.game_running = False

    def _check_game_over(self):
        """Verifica se o jogo terminou. Retorna True se sim."""
        try:
            from core.rules.game_status import get_game_status
            from core.moves.legal_movegen import generate_legal_moves
            
            status = get_game_status(self.board)
            
            if status.is_checkmate:
                result = 'black_win' if self.board.side_to_move == 0 else 'white_win'
                self.event_queue.put(('game_over', result, 'Checkmate'))
                self.game_running = False
                return True
            
            if status.is_stalemate:
                self.event_queue.put(('game_over', 'draw', 'Stalemate'))
                self.game_running = False
                return True
            
            if status.is_draw_by_fifty_move:
                self.event_queue.put(('game_over', 'draw', 'Fifty-move rule'))
                self.game_running = False
                return True
            
            if status.is_draw_by_repetition:
                self.event_queue.put(('game_over', 'draw', 'Threefold repetition'))
                self.game_running = False
                return True
            
            if status.is_insufficient_material:
                self.event_queue.put(('game_over', 'draw', 'Insufficient material'))
                self.game_running = False
                return True
        except Exception as e:
            print(f"Error checking game status: {e}")
            # Fallback: verificar se há movimentos legais
            try:
                from core.moves.legal_movegen import generate_legal_moves
                moves = list(generate_legal_moves(self.board))
                if not moves:
                    self.event_queue.put(('game_over', 'draw', 'No legal moves'))
                    self.game_running = False
                    return True
            except:
                pass
        
        return False

    def _determine_result(self, reason):
        """Mapeia razão para resultado."""
        r = (reason or "").lower()
        if "checkmate" in r:
            return "black_win" if "white" in r else "white_win"
        return "draw"  # default: draw

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.state == State.SETUP:
                    self.setup_screen.on_motion(event.pos[0], event.pos[1])
                elif self.state == State.GAME:
                    self.game_screen.on_motion(event.pos[0], event.pos[1])
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == State.SETUP:
                    mode = self.setup_screen.on_click(event.pos[0], event.pos[1])
                    if mode:
                        self.start_game(mode)
                
                elif self.state == State.GAME:
                    ctrl = self.game_screen.on_control_click(event.pos[0], event.pos[1])
                    if ctrl == 'start':
                        if not self.game_running:
                            self.paused = False
                            self.game_running = True
                            self.game_thread = threading.Thread(target=self.run_game_loop, daemon=True)
                            self.game_thread.start()
                    elif ctrl == 'pause':
                        self.paused = True
                    elif ctrl == 'undo':
                        pass
                    elif ctrl == 'new':
                        self.state = State.SETUP
                        self.game_running = False
                        if self.game_thread:
                            self.game_thread.join(timeout=1)
                
                elif self.state == State.GAME_OVER:
                    # voltar à tela de setup ao clicar
                    self.state = State.SETUP
                    self.gameover_screen.clear()

    def render(self):
        if self.state == State.SETUP:
            self.setup_screen.draw(self.screen)
        elif self.state == State.GAME:
            self.game_screen.draw(self.screen)
        elif self.state == State.GAME_OVER:
            self.game_screen.draw(self.screen)
            self.gameover_screen.draw(self.screen)
        
        pygame.display.flip()

    def update(self, dt):
        try:
            while True:
                event_type, *data = self.event_queue.get_nowait()
                if event_type == 'game_over':
                    result, reason = data
                    self.gameover_screen.set_result(result, reason)
                    self.state = State.GAME_OVER
                    if result == "white_win":
                        self.game_screen.scoreboard.record_win(0)
                    elif result == "black_win":
                        self.game_screen.scoreboard.record_win(1)
                    else:
                        self.game_screen.scoreboard.record_draw()
        except:
            pass
        
        if self.state == State.GAME_OVER:
            if self.gameover_screen.tick(dt):
                self.state = State.SETUP
                self.gameover_screen.clear()
                self.game_running = False

    def run(self):
        """Loop principal do pygame."""
        while self.running:
            dt = self.clock.tick(60)
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        self.game_running = False
        if self.game_thread:
            self.game_thread.join(timeout=1)
        pygame.quit()


def main():
    """Entrada principal."""
    app = GUIApp()
    app.run()


if __name__ == "__main__":
    main()
