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
- [🎮 Funcionalidades](#-funcionalidades)
- [📋 Requisitos](#-requisitos)
- [🔧 Instalação](#-instalação-windows)
- [▶️ Como executar](#️-como-executar)
- [🕹️ Controles](#️-controles)
- [🗺️ Layout do Nível](#️-layout-do-nível-800600)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🧠 Ambiente e Agentes](#-ambiente-e-agentes)
- [🔮 Melhorias Futuras](#-possíveis-melhorias-futuras)
- [📝 Observações Finais](#-observações-finais)

---

## 📖 Sobre o Projeto

**Simulador 2D de navegação espacial com gravidade realista, física orbital e visual pixel art retrô.**

Desenvolvido em Python com Pygame e NumPy, este projeto oferece um ambiente completo de simulação onde você pilota uma nave por um campo gravitacional com 6 planetas, coleta checkpoints de combustível e tenta atracar na estação espacial — tudo com uma estética arcade 16-bit dos anos 90.

A interface do ambiente é compatível com o padrão **Gymnasium** (`reset`, `step`, `render`, `close`), permitindo integração futura com agentes de aprendizado por reforço (RL).

## 🎮 Funcionalidades

- **Física orbital newtoniana** — gravidade proporcional à massa e distância de cada planeta
- **Sistema de combustível** — quantidade limitada, recarregável ao coletar checkpoints (+50 cada)
- **6 checkpoints** distribuídos em 2 corredores (superior e inferior) ao redor do planeta gigante central
- **Estação espacial** como objetivo final — atracar nela concede vitória com +1000 pontos
- **4 condições de derrota**: colisão com planeta, sair dos limites da tela, combustível zerado, ou falha crítica
- **Renderização pixel art** — resolução interna 400×300 com upscale 2× para 800×600
- **Fonte bitmap customizada** — classe `PixelFont` 5×7 desenhada por código, estilo console 16-bit
- **Tela de título animada** — estrelas piscando, título em neon ciano e magenta, efeito fade ao iniciar
- **Efeitos visuais**: partículas ao coletar checkpoint, glitch na colisão, alerta de proximidade no HUD
- **HUD distribuído** — informações sobrepostas ao campo de jogo sem caixas opacas
- **Modo headless** — ambiente funciona sem renderização para treinamento de agentes RL

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

```bash
# Da raiz do projeto:
python game-enviroment\main.py

# Ou entre na pasta e execute:
cd game-enviroment
python main.py
```

Ao executar, você verá:
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

> **Dica**: Use impulsos curtos e aproveite a gravidade dos planetas para fazer curvas (estilingue gravitacional). Cada impulso consome combustível — planeje sua rota!

## 🗺️ Layout do Nível (800×600)

```text
    [P3]  ---  [CP1] [CP2] [CP3]  ---  [P4]
                    (corredor superior)
[P1] ============ [P2 - GIGANTE] ============ [ESTACAO]
                    (corredor inferior)
    [P5]  ---  [CP4] [CP5] [CP6]  ---  [P6]
```

| # | Planeta | Cor | Massa | Raio | Função |
|---|---|---|---|---|---|
| P1 | Lançamento | Magenta | 700 | 48 | Ponto de partida (borda esquerda) |
| P2 | Gigante Central | Roxo | 1200 | 55 | Obstáculo massivo no centro |
| P3 | Anão Superior | Ciano | 250 | 30 | Perturbação no corredor de cima |
| P4 | Gasoso Superior | Azul | 500 | 38 | Guardião antes da estação (corredor superior) |
| P5 | Rochoso Inferior | Rosa | 350 | 35 | Perturbação no corredor de baixo |
| P6 | Gasoso Inferior | Laranja | 550 | 40 | Guardião antes da estação (corredor inferior) |

## 📁 Estrutura do Projeto

```text
aprendizado-de-maquina-estilingue-espacial/
├── requirements.txt            # Dependências do projeto
├── README.md                   # Este arquivo
├── docs/
│   └── fotos/                  # Fotos da equipe
├── game-enviroment/
│   ├── main.py                 # Entrada principal: tela de título + loop de jogo
│   ├── orbital_env.py          # Classe OrbitalEnv: lógica, renderização, interface RL
│   ├── physics.py              # Física pura: gravidade, colisões, cinemática (sem pygame)
│   └── config.py               # Constantes: física, cores, layout, recompensas
```

### Descrição dos arquivos

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Loop principal do jogo, tela de título, leitura de teclado. |
| `orbital_env.py` | Classe `OrbitalEnv` com toda a lógica do ambiente e renderização pixel art. Inclui a classe `PixelFont` (fonte bitmap). Expõe `reset()`, `step()`, `render()`, `close()`. |
| `physics.py` | Funções matemáticas puras: `gravity_vector`, `total_gravity`, `thrust_vector`, `apply_kinematics`, `check_circle_collision`, `check_circle_rect_collision`, `is_out_of_bounds`. Zero dependência de Pygame. |
| `config.py` | Arquivo central de configuração: constantes gravitacionais, cores (paleta 16 cores estilo console), posições dos planetas/checkpoints/estação, sistema de recompensas, parâmetros visuais. |

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

```python
# Exemplo de observação inicial:
obs = np.array([155.0, 300.0, 0.0, 0.0, 200.0, 220.0, 575.0])
#               pos_x   pos_y   vel_x vel_y fuel  dist_cp  dist_st
```

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

### Interface RL

O ambiente foi projetado como **plataforma de simulação e teste para algoritmos de aprendizado por reforço**, compatível com o padrão Gymnasium:

```python
env = OrbitalEnv(render_mode="human")   # com renderização
# ou
env = OrbitalEnv()                       # headless (treinamento)

obs = env.reset()                        # vetor numpy (7,)
obs, reward, done, info = env.step(0)    # ação: 0=nada, 1-4=direções
env.render()                             # desenha o frame atual
env.close()                              # libera recursos
```

## 🔮 Possíveis Melhorias Futuras

- **Agentes de RL** — integração com DQN, PPO, SAC usando Gymnasium + Stable-Baselines3
- **Múltiplos níveis** — layouts variados de planetas com dificuldade progressiva
- **Efeitos sonoros** — som de motor, coleta de checkpoint, colisão e fanfarra de vitória
- **Power-ups** — escudo temporário, boost de velocidade, dobro de pontos
- **Modo competitivo** — 2 jogadores simultâneos (WASD vs Setas)
- **Editor de níveis** — interface visual para criar e salvar layouts customizados
- **Balanceamento dinâmico** — ajuste automático de dificuldade baseado no desempenho
- **Exportação de métricas** — gráficos de recompensa, trajetória e taxa de sucesso
- **Suporte a macOS/Linux** — adaptação de caminhos e comandos de terminal

---

## 📝 Observações Finais

- **Caminho de execução**: sempre execute `main.py` de dentro da pasta `game-enviroment`, ou use o caminho completo `python game-enviroment/main.py` a partir da raiz. Isso garante que os imports relativos (`import config`, `import physics`) funcionem corretamente.

- **Modo headless**: para treinar agentes sem janela gráfica, instancie o ambiente **sem** `render_mode`:
  ```python
  env = OrbitalEnv()  # sem renderização, sem partículas visuais
  ```

- **Customização**: para alterar física, cores, posições ou recompensas, edite apenas o arquivo `config.py`. A lógica do ambiente (`orbital_env.py`) não precisa ser modificada.

- **Módulo `physics.py`**: é completamente independente — não importa Pygame. Pode ser reutilizado com qualquer outro motor de renderização ou framework de simulação.

- **Pixel art**: a renderização usa uma superfície interna de 400×300 pixels que é escalada 2× para 800×600. Isso cria o efeito visual de jogo retrô 16-bit automaticamente em todos os elementos.

- **Ambiente virtual**: se encontrar erros de módulo não encontrado, ative o ambiente virtual antes de executar:
  ```bash
  venv\Scripts\activate
  python game-enviroment/main.py
  ```

---

Feito com 💜 e nostalgia dos anos 90.
