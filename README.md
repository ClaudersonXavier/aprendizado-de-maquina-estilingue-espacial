# 🚀 Odisseia Orbital

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green)
![NumPy](https://img.shields.io/badge/NumPy-1.24+-orange)
![Status](https://img.shields.io/badge/Status-Acad%C3%AAmico-lightgrey)

## 🎓 Projeto Acadêmico

**Universidade Federal do Agreste de Pernambuco (UFAPE)**  
Disciplina: **Inteligência Artificial — 2026.1**  
Professor: **Dr. Luis Filipe**

Este projeto tem como objetivo implementar, analisar e comparar diferentes paradigmas de agentes inteligentes em um ambiente próprio de simulação orbital com gravidade realista.

### 👥 Equipe

<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/alinesors">
        <img src="docs/fotos/aline-foto.png" width="110px" alt="Aline Fernanda"/><br>
        <sub><b>Aline Fernanda Soares Silva</b></sub><br>
        <sub>@alinesors</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/ClaudersonXavier">
        <img src="docs/fotos/clauderson-foto.png" width="110px" alt="Clauderson Branco"/><br>
        <sub><b>Clauderson Branco Xavier</b></sub><br>
        <sub>@ClaudersonXavier</sub>
      </a>
    </td>
  </tr>
</table>

---

## 📑 Sumário

- [📖 Sobre o Projeto](#-sobre-o-projeto)
- [📋 Requisitos](#-requisitos)
- [🔧 Instalação](#-instalação-windows)
- [▶️ Como executar](#️-como-executar)
- [🕹️ Controles](#️-controles)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🧠 Ambiente e Agentes](#-ambiente-e-agentes)

---

## 📖 Sobre o Projeto

**Simulador 2D de navegação espacial com gravidade realista, física orbital e visual pixel art retrô.**

Desenvolvido em Python com Pygame e NumPy, este projeto oferece um ambiente completo de simulação onde você pilota uma nave por um campo gravitacional com 6 planetas, coleta checkpoints de combustível e tenta atracar na estação espacial — tudo com uma estética arcade 16-bit dos anos 90.

A interface do ambiente é compatível com o padrão **Gymnasium** (`reset`, `step`, `render`, `close`), permitindo integração futura com agentes de aprendizado por reforço (RL).

## 📋 Requisitos

| Dependência | Versão mínima | Uso |
|---|---|---|
| Python | 3.8+ | Linguagem base |
| pygame | 2.5.0+ | Renderização, input e janela |
| numpy | 1.24.0+ | Cálculo vetorial e física |

Instale com:

```bash
pip install -r requirements.txt
```

## 🔧 Instalação (Windows)

```bash
# 1. Clone o repositório ou extraia os arquivos

# 2. (Recomendado) Crie e ative um ambiente virtual
python -m venv venv
venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
```

## ▶️ Como executar

A partir da **raiz do projeto**:

```bash
# Jogar manualmente (modo jogador)
python run_game.py

# Agente de busca heurística (A* + AutoPilot)
python run_heuristic.py

# Agente com replay de uma run salva
python run_heuristic.py --trained latest   # run mais recente
python run_heuristic.py --trained 001      # run específica

# Listar runs de treino salvas
python run_heuristic.py --list

# Agente de algoritmo genetico (neuroevolucao)
python run_genetic.py                       # Debug visual com evolucao live
python run_genetic.py --train               # Treino headless (200 geracoes)
python run_genetic.py --train --gens 50     # Treino com N geracoes
python run_genetic.py --show                # Showcase do melhor cerebro
python run_genetic.py --show --gen 20       # Showcase de geracao especifica
python run_genetic.py --list                # Listar checkpoints salvos
```

Ao executar `run_game.py`, você verá:
1. **Tela de título** com o nome "ODISSEIA ORBITAL" em neon, estrelas animadas e grid de fundo
2. Pressione **ENTER** para iniciar (ou **ESC** para sair)
3. O jogo começa com a nave na superfície do planeta de lançamento (borda esquerda)
4. Seu objetivo: navegar até a **estação espacial** no canto direito da tela

## 🕹️ Controles

| Tecla | Ação |
|---|---|
| **W** ou **↑** | Impulso para cima (custa 3 de combustível) |
| **S** ou **↓** | Impulso para baixo |
| **A** ou **←** | Impulso para esquerda |
| **D** ou **→** | Impulso para direita |
| **R** | Reiniciar o episódio a qualquer momento |
| **ESC** | Sair do jogo |

## 📁 Estrutura do Projeto

```text
estilingue-espacial/
├── run_game.py                  # Atalho: jogar manualmente
├── run_heuristic.py             # Atalho: agente de busca heuristica
├── run_genetic.py               # Atalho: agente de algoritmo genetico
├── requirements.txt             # Dependencias do projeto
├── README.md                    # Este arquivo
├── docs/
│   └── fotos/                   # Fotos da equipe
└── game-enviroment/
    ├── main.py                  # Tela de titulo + loop de jogo manual
    ├── orbital_env.py           # Classe OrbitalEnv: logica, renderizacao, interface RL
    ├── physics.py               # Fisica pura: gravidade, colisoes, cinematica
    ├── config.py                # Constantes: fisica, cores, layout, recompensas
    └── agents/
        ├── heuristic_goal/      # Agente de Busca Heuristica (A*)
        │   ├── heuristic_agent.py
        │   ├── grid_map.py
        │   ├── astar_planner.py
        │   ├── auto_pilot.py
        │   ├── visualization.py
        │   ├── replay_buffer.py
        │   └── training_data/
        └── genetic/             # Agente de Algoritmo Genetico (Neuroevolucao)
            ├── ship.py              # NaveGenetica + CerebroNave (RNA)
            ├── genetic_env.py       # AmbienteGenetico: frota de 100 naves
            ├── treinador.py         # Loop de treino, save/load, logs
            └── checkpoints/         # Cerebros salvos (.pkl)
```

## 🧠 Ambiente e Agentes

### Representação do Estado

O estado do ambiente é representado por um vetor numpy de **7 elementos** com valores contínuos:

| Índice | Símbolo | Descrição | Intervalo típico |
|---|---|---|---|
| 0 | `pos_x` | Posição horizontal da nave | 0 a 800 |
| 1 | `pos_y` | Posição vertical da nave | 0 a 600 |
| 2 | `vel_x` | Velocidade horizontal | -2.75 a +2.75 |
| 3 | `vel_y` | Velocidade vertical | -2.75 a +2.75 |
| 4 | `fuel` | Combustível restante | 0 a 200 |
| 5 | `dist_cp` | Distância ao próximo checkpoint não coletado | 0 a ~1000 |
| 6 | `dist_st` | Distância até a estação espacial | 0 a ~1000 |

### Espaço de Ações (A)

O ambiente possui **5 ações discretas** (espaço `Discrete(5)`):

| Ação | Descrição | Efeito |
|---|---|---|
| `0` | Nada (*coast*) | Nave mantém inércia; **sem custo** de combustível |
| `1` | Impulso ↑ | Acelera para cima (-Y); custa **3.0** de combustível |
| `2` | Impulso ↓ | Acelera para baixo (+Y); custa **3.0** de combustível |
| `3` | Impulso ← | Acelera para esquerda (-X); custa **3.0** de combustível |
| `4` | Impulso → | Acelera para direita (+X); custa **3.0** de combustível |

**Parâmetros físicos do ambiente:**

| Constante | Valor | Descrição |
|---|---|---|
| `G` | 0.75 | Constante gravitacional universal |
| `THRUST_POWER` | 0.9 px/s² | Aceleração por impulso |
| `MAX_SPEED` | 2.75 px/s | Velocidade máxima (cap) |
| `MAX_FUEL` | 200.0 | Combustível inicial |
| `FUEL_COST_PER_THRUST` | 3.0 | Custo por ação de impulso |
| `FUEL_PICKUP` | 50.0 | Combustível ganho ao coletar checkpoint |
| `LAUNCH_ESCAPE_DISTANCE` | 90 px | Distância para ativar gravidade/colisão do planeta inicial |

### Função de Recompensa (R)

A função de recompensa combina **incentivos contínuos** (a cada passo) com **recompensas esparsas** (eventos específicos):

| Evento | Recompensa | Tipo |
|---|---|---|
| Cada passo de simulação | **−0.01** | Contínua — incentiva rapidez |
| Cada ação de impulso (ação ≠ 0) | **−0.05** | Contínua — penaliza gasto de combustível |
| Coletar um checkpoint | **+100.0** | Esparsa — incentiva exploração |
| Atracar na estação (sucesso) | **+1000.0** | Terminal — objetivo principal |
| Colisão com planeta | **−1000.0** | Terminal — falha |
| Sair dos limites da tela | **−1000.0** | Terminal — falha |
| Combustível zerado | **−1000.0** | Terminal — falha |

**Condições de término do episódio:**

| Condição | Gatilho | `info["status"]` |
|---|---|---|
| ✅ Sucesso | Nave colide com o retângulo da estação | `"docked"` |
| 💥 Colisão | Nave colide com qualquer planeta (exceto o de lançamento antes do escape) | `"crashed_planet"` |
| 🚫 Fora da tela | Nave ultrapassa os limites 800×600 | `"out_of_bounds"` |
| ⛽ Sem combustível | `fuel ≤ 0.0` | `"no_fuel"` |

