# Especificação Técnica: Agente de Busca Heurística (A* Visual)

## 1. Contexto e Objetivo do Agente
Você atuará como um Engenheiro de IA desenvolvendo um agente baseado em busca heurística para o ambiente "Odisséia Orbital". O ambiente contínuo já foi construído utilizando Pygame e `numpy`. As dimensões da tela são 800x600 pixels, definidas em `config.py`[cite: 1].
O objetivo é implementar a arquitetura hierárquica do agente dividida em duas partes:
1. **O Planejador (A* Visual):** Calcula a rota ideal em uma malha discretizada (Grid).
2. **O Piloto Automático:** Executa as ações discretas de 0 a 4 para fazer a nave seguir a rota na física contínua[cite: 4].

## 2. A Discretização do Espaço (GridMap)
O espaço contínuo deve ser mapeado em um Grid para que o algoritmo A* possa operar.
* **Resolução:** Cada célula da grade deve representar um bloco de 20x20 pixels da tela.
* **Obstáculos (Planetas):** O algoritmo deve ler a lista de planetas do ambiente. Se o centro de uma célula estiver dentro do raio de colisão de um planeta somado a uma "Margem de Segurança" (ex: 30 pixels adicionais para evitar a gravidade esmagadora), essa célula é marcada como `intransponível`.

## 3. O Algoritmo A* Interativo (Generator com `yield`)
Para demonstrar a evolução visual do pensamento do agente, a busca do A* **não pode ser instantânea**. Ela deve ser implementada como um *Generator* em Python, utilizando `yield`. 

A cada iteração (expansão de um nó), a função deve "pausar" e retornar o estado atual da busca para que o Pygame possa renderizar o processo passo a passo (o efeito "radar").

### 3.1. Matemática e Heurística
Utilize as equações clássicas da busca heurística:
$$f(n) = g(n) + h(n)$$
* $g(n)$: Custo acumulado do nó inicial até o nó $n$ (distância Euclidiana entre as células).
* $h(n)$: Distância Euclidiana em linha reta do nó $n$ até o objetivo.

### 3.2. Estrutura Esperada do Generator
A função de busca, por exemplo `a_star_search(start, goal)`, deve fazer um `yield` contendo dicionários ou listas dos seguintes conjuntos:
* `open_set` (A Fronteira): Nós descobertos, mas ainda não avaliados (para serem pintados de azul claro/translúcido).
* `closed_set` (Visitados): Nós já avaliados (para serem pintados de azul escuro/translúcido).
* Quando o objetivo for alcançado, o último `yield` deve retornar o `path` (a lista de coordenadas do caminho final).

## 4. O Controlador (Piloto Automático)
O A* gerará uma lista de pontos centrais (x, y) das células que formam a rota. O Piloto Automático deve ler essa lista e tentar segui-la no espaço físico sujeito a inércia e gravidade.
* **Lógica (Bang-Bang Controller simplificado):** 
  Encontre o próximo "Waypoint" da rota.
  Calcule o vetor da posição atual da nave até o Waypoint.
  Se o Waypoint está acima da nave (vetor Y negativo), retorne a ação `1` (propulsor para cima). 
  Se está à direita, retorne `4`, etc.[cite: 4]
* **Tolerância:** Se a nave estiver perto o suficiente do Waypoint (ex: raio de 15 pixels), remova esse Waypoint da lista e mire no próximo.
* **Economia:** Se a velocidade da nave na direção do alvo já for razoável, retorne a ação `0` (desligar propulsores) para economizar combustível.

## 5. Implementação Exigida
Crie o arquivo `heuristic_agent.py` contendo:
1. **Classe `GridMap`:** Responsável por converter posições contínuas em (linha, coluna) e vice-versa, e identificar obstáculos.
2. **Classe `AStarPlanner`:** Contendo a função geradora `search` com `yield`.
3. **Classe `AutoPilot`:** Que recebe o caminho do A* e o estado contínuo do ambiente (vetor de observação) e retorna a ação discreta (0-4).
4. **Loop Principal de Integração (`__main__`):** 
   * Importe o `OrbitalEnv` do arquivo `orbital_env.py`[cite: 2, 3].
   * Configure um laço que primeiro roda a animação do A* (pegando os retornos do `yield` e desenhando os quadrados translúcidos por cima do frame renderizado do ambiente).
   * Após o caminho ser encontrado, desenhe a "Linha Guia" verde e passe o controle para o `AutoPilot` interagir com o `env.step(action)`[cite: 3].
   * Quando coletar um checkpoint (verifique o dicionário `info` retornado pelo `step`), pause, atualize o alvo para o próximo checkpoint e inicie um novo generator do A*.