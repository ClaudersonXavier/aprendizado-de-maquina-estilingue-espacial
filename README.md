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
| 0 | `pos_x` | Posição horizontal da nave |  |
| 1 | `pos_y` | Posição vertical da nave |  |
| 2 | `vel_x` | Velocidade horizontal |  |
| 3 | `vel_y` | Velocidade vertical |  |
| 4 | `fuel` | Combustível restante |  |
| 5 | `dist_cp` | Distância ao próximo checkpoint não coletado |  |
| 6 | `dist_st` | Distância até a estação espacial |  |

### Espaço de Ações (A)

O ambiente possui **5 ações discretas** (espaço `Discrete(5)`):

| Ação | Descrição | Efeito |
|---|---|---|

**Parâmetros físicos do ambiente:**

| Constante | Valor | Descrição |
|---|---|---|

### Função de Recompensa (R)

A função de recompensa combina **incentivos contínuos** (a cada passo) com **recompensas esparsas** (eventos específicos):

| Evento | Recompensa | Tipo |
|---|---|---|

**Condições de término do episódio:**

| Condição | Gatilho | `info["status"]` |
|---|---|---|
| ✅ Sucesso | Nave colide com o retângulo da estação | `"docked"` |
| 💥 Colisão | Nave colide com qualquer planeta (exceto o de lançamento antes do escape) | `"crashed_planet"` |
| 🚫 Fora da tela | Nave ultrapassa os limites 800×600 | `"out_of_bounds"` |
| ⛽ Sem combustível | `fuel ≤ 0.0` | `"no_fuel"` |

