"""
config.py — Constantes fisicas, cores e layout do nivel.
Modifique este arquivo para ajustar o cenario sem alterar a logica do ambiente.
"""

# ============================================================
# Constantes Fisicas
# ============================================================
G = 0.75                  # Constante gravitacional (ajuste para forca da gravidade)
THRUST_POWER = 0.9       # Aceleracao por impulso do propulsor
MAX_SPEED = 2.75         # Velocidade maxima da nave (evita instabilidade numerica)
MAX_FUEL = 200.0         # Combustivel inicial
FUEL_PICKUP = 50.0       # Combustivel ganho ao coletar um checkpoint
FUEL_COST_PER_THRUST = 3.0  # Custo de combustivel por acao de impulso

# ============================================================
# Tela e Renderizacao
# ============================================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# ============================================================
# Nave
# ============================================================
SHIP_RADIUS = 8          # Raio de colisao da nave
SHIP_START_POS = (155, 300)  # Spawn: superficie direita do planeta de lancamento
MAX_TRAIL_LENGTH = 50    # Numero de pontos no rastro orbital
LAUNCH_PLANET_INDEX = 0  # Indice do planeta de lancamento (gravidade/colisao desativadas ate escape)
LAUNCH_ESCAPE_DISTANCE = 90  # Distancia do centro do planeta para ativar gravidade e colisao

# ============================================================
# Sistema de Recompensas
# ============================================================
REWARD_STEP = -0.01           # Penalidade por passo vivo (incentiva rapidez)
REWARD_THRUST_COST = -0.05    # Custo extra por usar propulsor
REWARD_CHECKPOINT = 100.0      # Recompensa ao coletar checkpoint
REWARD_SUCCESS = 1000.0       # Recompensa ao atracar na estacao
REWARD_FAILURE = -1000.0       # Penalidade por colisao, sem combustivel ou fora da tela

# ============================================================
# Cores
# ============================================================
COLOR_BG = (11, 12, 16)              # Fundo preto-azulado
COLOR_SHIP = (255, 255, 255)         # Nave branca
COLOR_SHIP_OUTLINE = (200, 200, 200) # Contorno da nave
COLOR_TRAIL = (52, 152, 219)         # Rastro azul-ciano
COLOR_STATION = (189, 195, 199)      # Estacao cinza
COLOR_STATION_BORDER = (149, 165, 166)
COLOR_CHECKPOINT = (46, 204, 113)    # Checkpoint verde
COLOR_CHECKPOINT_GLOW = (39, 174, 96)
COLOR_FUEL_BAR_BG = (44, 62, 80)     # Fundo da barra de combustivel
COLOR_FUEL_BAR = (241, 196, 15)      # Barra de combustivel (amarelo)
COLOR_FUEL_BAR_MID = (243, 156, 18)  # Laranja (combustivel medio)
COLOR_FUEL_BAR_LOW = (231, 76, 60)   # Vermelho (combustivel baixo)
COLOR_HUD_TEXT = (236, 240, 241)     # Texto do HUD
COLOR_SUCCESS = (46, 204, 113)       # Verde sucesso
COLOR_FAILURE = (231, 76, 60)        # Vermelho fracasso

# ============================================================
# Planetas (6 corpos celestes com diferentes massas e posicoes)
# ============================================================
PLANETS = [
    {"pos": (90, 300), "radius": 48, "mass": 700, "color": (192, 57, 43)},
    # P1: Base de Lancamento — borda esquerda, centro vertical

    {"pos": (400, 300), "radius": 55, "mass": 1200, "color": (231, 76, 60)},
    # P2: Gigante Central — obstaculo massivo no centro do mapa

    {"pos": (250, 100), "radius": 30, "mass": 250, "color": (243, 156, 18)},
    # P3: Anao Superior — perturbacao no corredor de cima

    {"pos": (580, 140), "radius": 38, "mass": 500, "color": (230, 126, 34)},
    # P4: Gasoso Superior — guardiao antes da estacao (corredor superior)

    {"pos": (300, 500), "radius": 35, "mass": 350, "color": (211, 84, 0)},
    # P5: Rochoso Inferior — perturbacao no corredor de baixo

    {"pos": (580, 460), "radius": 40, "mass": 550, "color": (241, 196, 15)},
    # P6: Gasoso Inferior — guardiao antes da estacao (corredor inferior)
]

# ============================================================
# Checkpoints (2 regioes com 3 cristais cada)
# ============================================================
CHECKPOINTS = [
    # Regiao 1 — Corredor Superior (acima do Gigante Central)
    {"pos": (340, 170), "radius": 12},
    {"pos": (450, 130), "radius": 12},
    {"pos": (530, 180), "radius": 12},
    # Regiao 2 — Corredor Inferior (abaixo do Gigante Central)
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
STATION_RADIUS = 22  # Raio de colisao aproximado do retangulo
