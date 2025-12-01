"""Constantes de configuração da GUI."""

# Cores
BG_COLOR = (40, 40, 50)
LIGHT_SQ = (240, 217, 181)
DARK_SQ = (181, 136, 99)
SELECTED_SQ = (120, 180, 255)
BUTTON_BG = (70, 130, 180)
BUTTON_HOVER = (100, 150, 200)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (100, 200, 100)

# Dimensões
TILE_SIZE = 60
BOARD_SIZE = TILE_SIZE * 8
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCOREBOARD_WIDTH = 250

# Fontes
FONT_SIZE_TITLE = 28
FONT_SIZE_NORMAL = 16
FONT_SIZE_SMALL = 12

# Modos de jogo
MODES = {
    "Human vs Human": ("human", "human"),
    "Human vs Engine": ("human", "engine"),
    "Human vs Random": ("human", "random"),
    "Engine vs Engine": ("engine", "engine"),
    "Engine vs Random": ("engine", "random"),
    "Random vs Random": ("random", "random"),
}

# Engine
DEFAULT_DEPTH = 1
DEFAULT_TIME_MS = 300
