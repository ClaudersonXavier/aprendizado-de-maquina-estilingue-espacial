"""
config.py — Constantes fisicas, cores e layout do nivel.
"""

# ============================================================
# Constantes Fisicas
# ============================================================
G = 0.75
THRUST_POWER = 0.9
MAX_SPEED = 2.75
MAX_FUEL = 200.0
FUEL_PICKUP = 50.0
FUEL_COST_PER_THRUST = 2.5

# ============================================================
# Tela e Renderizacao — Pixel Art
# ============================================================
RENDER_WIDTH = 400
RENDER_HEIGHT = 300
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PIXEL_SCALE = 2
FPS = 60

# ============================================================
# Nave
# ============================================================
SHIP_RADIUS = 8
SHIP_START_POS = (155, 300)
MAX_TRAIL_LENGTH = 30
LAUNCH_PLANET_INDEX = 0
LAUNCH_ESCAPE_DISTANCE = 90

# ============================================================
# Sistema de Recompensas
# ============================================================
REWARD_STEP = -0.005
REWARD_THRUST_COST = -3.0
REWARD_CHECKPOINT = 500.0
REWARD_SUCCESS = 8000.0
REWARD_FUEL_BONUS_FACTOR = 5.0
REWARD_FAILURE_COLLISION = -1000.0
REWARD_FAILURE_OOB = -1000.0
REWARD_FAILURE_NO_FUEL = -750.0

# ============================================================
# Paleta Pixel Art — 16 cores estilo console 16-bit
# ============================================================
COLOR_BLACK       = (0, 0, 0)
COLOR_SPACE       = (8, 12, 32)
COLOR_BLUE        = (32, 64, 200)
COLOR_CYAN        = (0, 220, 220)
COLOR_GREEN       = (0, 220, 60)
COLOR_YELLOW      = (255, 220, 0)
COLOR_ORANGE      = (255, 140, 0)
COLOR_RED         = (255, 40, 40)
COLOR_MAGENTA     = (220, 40, 220)
COLOR_PURPLE      = (100, 20, 180)
COLOR_PINK        = (255, 100, 180)
COLOR_WHITE       = (240, 240, 255)
COLOR_GRAY        = (120, 130, 160)
COLOR_DARK_GRAY   = (40, 50, 70)
COLOR_GOLD        = (255, 200, 60)
COLOR_BROWN       = (120, 60, 20)
COLOR_DARK_RED    = (120, 10, 10)

# Alias para compatibilidade com codigo de jogo
COLOR_BG = COLOR_SPACE
COLOR_TRAIL = COLOR_CYAN
COLOR_SHIP = COLOR_WHITE
COLOR_SHIP_OUTLINE = COLOR_CYAN
COLOR_EXHAUST = COLOR_ORANGE
COLOR_EXHAUST_FADE = COLOR_RED
COLOR_STATION = COLOR_GRAY
COLOR_STATION_BORDER = COLOR_CYAN
COLOR_STATION_PANEL = COLOR_DARK_GRAY
COLOR_STATION_GLOW = COLOR_CYAN
COLOR_SUCCESS = COLOR_GREEN
COLOR_FAILURE = COLOR_RED
COLOR_WARNING = COLOR_ORANGE
COLOR_HUD_TEXT = COLOR_WHITE
COLOR_HUD_ACCENT = COLOR_CYAN
COLOR_STAR_DIM = COLOR_GRAY
COLOR_STAR_MED = COLOR_WHITE
COLOR_STAR_BRIGHT = COLOR_YELLOW

# HUD
COLOR_HUD_PANEL_BG = COLOR_BLACK
COLOR_HUD_PANEL_BORDER = COLOR_CYAN
COLOR_FUEL_BAR_BG = COLOR_DARK_GRAY
COLOR_FUEL_BAR = COLOR_GREEN
COLOR_FUEL_BAR_MID = COLOR_YELLOW
COLOR_FUEL_BAR_LOW = COLOR_RED
COLOR_FUEL_SEGMENT = COLOR_BLACK

# Checkpoints
COLOR_CHECKPOINT = COLOR_YELLOW
COLOR_CHECKPOINT_GLOW = COLOR_GOLD
COLOR_CHECKPOINT_PARTICLE = COLOR_WHITE

# ============================================================
# Planetas (6 corpos celestes)
# ============================================================
PLANETS = [
    {"pos": (90, 300), "radius": 48, "mass": 700, "color": (220, 40, 220)},
    {"pos": (400, 300), "radius": 55, "mass": 1200, "color": (100, 20, 180)},
    {"pos": (250, 100), "radius": 30, "mass": 250, "color": (0, 220, 200)},
    {"pos": (580, 140), "radius": 38, "mass": 500, "color": (32, 64, 200)},
    {"pos": (300, 500), "radius": 35, "mass": 350, "color": (255, 100, 180)},
    {"pos": (580, 460), "radius": 40, "mass": 550, "color": (255, 140, 0)},
]

# ============================================================
# Checkpoints
# ============================================================
CHECKPOINTS = [
    {"pos": (340, 170), "radius": 12},
    {"pos": (450, 130), "radius": 12},
    {"pos": (530, 180), "radius": 12},
    {"pos": (340, 430), "radius": 12},
    {"pos": (450, 470), "radius": 12},
    {"pos": (530, 420), "radius": 12},
]

# ============================================================
# Estacao Espacial
# ============================================================
STATION_POS = (730, 300)
STATION_WIDTH = 30
STATION_HEIGHT = 40
STATION_RADIUS = 22

# ============================================================
# Constantes Visuais Pixel Art
# ============================================================
STAR_COUNT = 80
MAX_EXHAUST_PARTICLES = 12
MAX_CHECKPOINT_PARTICLES = 8
MAX_SPACE_PARTICLES = 0
PARTICLE_LIFETIME = 8
CHECKPOINT_PARTICLE_LIFETIME = 10

# Grid pontilhado
GRID_SPACING = 50
GRID_DOT_GAP = 4

# HUD
HUD_WIDTH = 170
HUD_HEIGHT = 80
HUD_MARGIN = 6
HUD_FUEL_BLOCKS = 10

# Glitch
GLITCH_OFFSET_MAX = 2
GLITCH_DURATION = 8
