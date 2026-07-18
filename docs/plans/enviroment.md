# Especificação Técnica do Ambiente: Odisséia Orbital (Simulador de Gravidade 2D)

## 1. Contexto e Objetivo
Atue como um Engenheiro de Software especialista em Python, Pygame e Inteligência Artificial.
Sua tarefa é desenvolver a infraestrutura completa de um ambiente virtual customizado (Contexto I) para o treinamento de agentes inteligentes[cite: 1]. 

O ambiente deve ser estritamente modular, separando a lógica do "jogo" das decisões do agente, seguindo o padrão de interface da biblioteca OpenAI Gym/Gymnasium (com métodos `reset()`, `step(action)` e `render()`)[cite: 1]. O objetivo é que, no futuro, agentes baseados em busca heurística, aprendizado por reforço e algoritmos genéticos possam interagir de forma padronizada com este ambiente[cite: 1].

## 2. Descrição do Tema: Odisséia Orbital
Um simulador 2D de navegação espacial. Uma nave controlada pelo agente precisa sair do ponto de partida, navegar por um espaço contendo planetas estáticos (que exercem força gravitacional) e atracar em uma estação espacial[cite: 1]. 

A nave possui propulsores direcionais e um tanque de combustível limitado. Para evitar que o combustível acabe e para guiar o aprendizado (Reward Shaping), existem "checkpoints" em formato de cristais/tanques de combustível na órbita.

## 3. Especificações Técnicas e Lógicas

### 3.1. Ações (Entrada do Agente)
O espaço de ação é discreto (`Discrete(5)`). A cada frame, o agente envia um inteiro correspondente ao acionamento do propulsor:
* `0`: Não fazer nada (inércia e gravidade atuam livremente).
* `1`: Impulso para Cima (-Y).
* `2`: Impulso para Baixo (+Y).
* `3`: Impulso para Esquerda (-X).
* `4`: Impulso para Direita (+X).

### 3.2. Percepções / Estado (Saída do Ambiente)
O método `step()` deve retornar um vetor `numpy` 1D (`Box`) contendo exclusivamente valores numéricos contínuos:
1. Posição X da nave.
2. Posição Y da nave.
3. Velocidade X da nave.
4. Velocidade Y da nave.
5. Quantidade de combustível restante.
6. Distância euclidiana até o próximo checkpoint de combustível.
7. Distância euclidiana até a estação espacial.

### 3.3. Física e Cinemática
* **Gravidade:** Planetas são definidos por uma coordenada `(x, y)`, um raio de colisão e uma `massa`. A cada *step*, calcule a força gravitacional exercida por cada planeta sobre a nave usando uma adaptação da lei de Newton: $F = G \frac{m}{r^2}$ (sendo $r$ a distância entre a nave e o planeta, e a direção o vetor normalizado apontando para o centro do planeta).
* **Propulsão:** Acionar propulsores (ações 1 a 4) adiciona um vetor de aceleração constante e consome `1` unidade de combustível por *step*.
* **Atualização:** Some os vetores de gravidade e propulsão para obter a aceleração final $\vec{a}$. Atualize a velocidade $\vec{v} = \vec{v} + \vec{a}$ e a posição $\vec{p} = \vec{p} + \vec{v}$.

### 3.4. Sistema de Recompensas (Reward Shaping)
O ambiente deve retornar uma variável escalar `reward` baseada nas seguintes regras lógicas de aprendizado[cite: 1]:
* **Recompensa Contínua (Step Penalty):** `-0.01` por step vivo (incentiva rapidez).
* **Custo de Propulsão:** `-0.05` extra toda vez que uma ação entre `1` e `4` for escolhida (incentiva uso da gravidade).
* **Coleta de Combustível (Checkpoint):** `+50.0` ao colidir com o checkpoint ativo (abastece o tanque e remove o checkpoint da lista).
* **Sucesso Absoluto (Chegar na Estação):** `+1000.0` e `done = True`.
* **Fracasso Absoluto (Colisão/Sem Combustível):** `-100.0` e `done = True` se a nave tocar no raio de um planeta, sair dos limites da tela ou o combustível chegar a `0`.

## 4. Requisitos de Visualização (Pygame)
A visualização deve ser clara o suficiente para demonstrar a evolução do agente durante a apresentação do projeto[cite: 1].
* Utilizar `pygame` com resolução sugerida de 800x600.
* **Fundo:** Cor escura (ex: `#0B0C10`).
* **Nave:** Um pequeno polígono ou círculo branco.
* **Planetas:** Círculos vermelhos/alaranjados baseados em seu raio de colisão.
* **Checkpoints:** Círculos pequenos verdes ou azuis brilhantes.
* **Estação Espacial:** Um retângulo cinza/prateado no extremo da tela.
* **Rastro (Trilha Orbital):** OBRIGATÓRIO manter uma lista contendo os últimos 50 pontos `(x,y)` da nave e desenhar uma linha conectando-os para evidenciar a trajetória curva[cite: 1].

## 5. Plano de Implementação Exigido
Gere o código Python modularizado em um arquivo chamado `orbital_env.py` contendo:
1. Importações (`pygame`, `numpy`, `math`).
2. A classe `OrbitalEnv` com o método `__init__` configurando as variáveis, constantes físicas e lista de planetas/checkpoints.
3. O método `reset()` que restaura o estado inicial da simulação e devolve a observação `_get_state()`.
4. O método `step(action)` contendo toda a lógica de física, limites, recompensas e flags de término.
5. O método `render()` renderizando os elementos e o rastro na tela a 60 FPS.
6. Um bloco final `if __name__ == "__main__":` com um loop de teste executando ações aleatórias (ou zero) para eu poder testar e validar o ambiente imediatamente.