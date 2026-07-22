"""
AgenteQLearning — Agente de Aprendizado por Reforço com Q-Learning Tabular.

Utiliza uma tabela Q implementada como dicionário esparso (defaultdict).
Cada chave é uma tupla de estado discreto (gerada pelo DiscretizadorEstado).
Cada valor é um array numpy de 5 posições com os Q-values das 5 ações.

Política de seleção de ação: epsilon-greedy
  - Com probabilidade epsilon: ação aleatória (exploração)
  - Com probabilidade 1 - epsilon: ação de maior Q-value (exploração / greedy)
  - Em caso de empate no Q-value máximo, desempata aleatoriamente

Equação de Bellman (atualização da tabela Q):
  Q(S, A) ← Q(S, A) + α × [R + γ × max Q(S', a) − Q(S, A)]

  Onde:
    α (alpha) = taxa de aprendizado — o quanto confiamos na nova informação
    γ (gamma) = fator de desconto — o quanto valorizamos recompensas futuras
    R         = recompensa imediata recebida do ambiente
    S         = estado atual
    A         = ação tomada
    S'        = próximo estado (após executar A)
    max Q(S', a) = melhor Q-value estimado no próximo estado

Decaimento do epsilon:
  Após cada episódio, multiplicamos epsilon pelo fator de decaimento,
  reduzindo gradualmente a exploração conforme o agente aprende.
    epsilon ← max(epsilon × epsilon_decay, epsilon_min)
"""

import pickle
import random
from collections import defaultdict
import numpy as np


class AgenteQLearning:
    """Agente tabular que aprende a política ótima via Q-Learning."""

    def __init__(self, n_acoes=5, alpha=0.2, gamma=0.99,
                 epsilon=1.0, epsilon_min=0.1, epsilon_decay=0.9993,
                 valor_otimista=0.0):
        """
        Inicializa o agente com os hiperparâmetros de aprendizado.

        Parâmetros:
          n_acoes        : número de ações discretas disponíveis (5: 0 a 4)
          alpha          : taxa de aprendizado — controla o peso de novas experiências
          gamma          : fator de desconto — 0.99 = valoriza bastante o futuro
          epsilon        : probabilidade inicial de exploração (1.0 = 100% aleatório)
          epsilon_min    : probabilidade mínima de exploração (0.1 = 10%)
          epsilon_decay  : fator multiplicativo de decaimento por episódio (0.9993)
          valor_otimista : valor inicial dos Q-values para estados nunca visitados.
                           Se > 0, o agente assume que ações desconhecidas são boas
                           até provar o contrário (inicialização otimista).
                           Isso incentiva a exploração natural de novos estados.
                           Use um valor menor que a recompensa de checkpoint (+100).
        """
        self.n_acoes = n_acoes
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.valor_otimista = valor_otimista

        # Tabela Q: dicionário onde cada chave é uma tupla de estado (4 inteiros)
        # e cada valor é um array numpy de 5 floats (Q-value de cada ação).
        # Usamos defaultdict para criar automaticamente um array na primeira vez
        # que um estado é visitado (alocação sob demanda).
        #
        # Se valor_otimista > 0, inicializamos com um valor positivo para
        # incentivar o agente a testar ações em estados desconhecidos.
        # Ações que levam a colisões (−1000) rapidamente têm seu Q-value
        # reduzido, enquanto ações que levam a checkpoints (+100) o mantêm alto.
        if valor_otimista > 0:
            self.tabela_q = defaultdict(
                lambda: np.full(self.n_acoes, valor_otimista, dtype=np.float64)
            )
        else:
            self.tabela_q = defaultdict(
                lambda: np.zeros(self.n_acoes, dtype=np.float64)
            )

        # Contador de episódios já treinados (incrementado a cada decay_epsilon)
        self.episodios_treinados = 0

    # ------------------------------------------------------------------
    # Política de seleção de ação (epsilon-greedy)
    # ------------------------------------------------------------------

    def selecionar_acao(self, estado):
        """
        Seleciona uma ação usando a política epsilon-greedy.

        Com probabilidade epsilon:
          Escolhe uma ação aleatória entre 0 e n_acoes-1 (exploração).
        Com probabilidade 1 - epsilon:
          Escolhe a ação com o maior Q-value para o estado atual (greedy).
          Se houver empate entre as melhores ações, escolhe aleatoriamente
          entre elas — isso evita viés sistemático para ações de índice baixo.

        Parâmetros:
          estado : tupla de 4 inteiros (dir_alvo, dir_mov, perigo, nivel_comb)

        Retorna:
          int : ação selecionada (0 a 4)
        """
        # Exploração: ação aleatória
        if random.random() < self.epsilon:
            return random.randint(0, self.n_acoes - 1)

        # Exploração (greedy): melhor ação segundo a tabela Q
        q_valores = self.tabela_q[estado]
        q_maximo = np.max(q_valores)

        # Encontra TODAS as ações que têm o Q-value máximo e desempata aleatoriamente
        melhores_acoes = np.where(q_valores == q_maximo)[0]
        return int(random.choice(melhores_acoes))

    # ------------------------------------------------------------------
    # Aprendizado (Equação de Bellman)
    # ------------------------------------------------------------------

    def aprender(self, estado, acao, recompensa, proximo_estado, terminal):
        """
        Atualiza a tabela Q usando a Equação de Bellman.

        Q(S, A) ← Q(S, A) + α × [R + γ × max Q(S', a) − Q(S, A)]

        Se o episódio terminou (terminal = True), não há estado futuro,
        então o alvo TD é apenas a recompensa imediata:
          alvo_td = R

        Caso contrário:
          alvo_td = R + γ × max Q(S', a)

        Parâmetros:
          estado         : tupla do estado em que a ação foi tomada
          acao           : ação executada (0 a 4)
          recompensa     : recompensa recebida do ambiente (float)
          proximo_estado : tupla do estado resultante após a ação
          terminal       : True se o episódio terminou após esta transição
        """
        # Q-value atual para o par (estado, ação)
        q_atual = self.tabela_q[estado][acao]

        if terminal:
            # Episódio terminou — não há estados futuros para considerar
            alvo_td = recompensa
        else:
            # Melhor Q-value estimado no próximo estado (max sobre todas as ações)
            q_max_proximo = np.max(self.tabela_q[proximo_estado])
            # Alvo do Temporal Difference: recompensa imediata + valor futuro descontado
            alvo_td = recompensa + self.gamma * q_max_proximo

        # Atualização incremental: move o Q-value na direção do erro TD
        # erro_td = alvo_td - q_atual  →  quanto o Q-value atual errou
        # q_atual += alpha * erro_td    →  corrige parcialmente (aprendizado gradual)
        self.tabela_q[estado][acao] += self.alpha * (alvo_td - q_atual)

    # ------------------------------------------------------------------
    # Controle de exploração
    # ------------------------------------------------------------------

    def decair_epsilon(self):
        """
        Reduz a taxa de exploração multiplicando pelo fator de decaimento.

        Chamado ao final de cada episódio de treino.
        epsilon nunca fica abaixo de epsilon_min (exploração mínima garantida).

        Com epsilon_decay = 0.9993 e epsilon_min = 0.1:
          - Após ~1000 episódios: epsilon ≈ 0.50
          - Após ~3000 episódios: epsilon ≈ 0.12
          - Após ~4000 episódios: epsilon ≈ 0.10 (atinge o mínimo)
        """
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)
        self.episodios_treinados += 1

    # ------------------------------------------------------------------
    # Persistência (salvar e carregar a tabela Q)
    # ------------------------------------------------------------------

    def salvar(self, caminho):
        """
        Salva o estado completo do agente em um arquivo pickle.

        Inclui a tabela Q (convertida para dict comum) e todos os
        hiperparâmetros, permitindo retomar o treino posteriormente.

        Parâmetros:
          caminho : string com o caminho do arquivo (ex: 'q_table_odisseia.pkl')
        """
        dados = {
            'tabela_q': dict(self.tabela_q),  # defaultdict → dict para serialização
            'n_acoes': self.n_acoes,
            'alpha': self.alpha,
            'gamma': self.gamma,
            'epsilon': self.epsilon,
            'epsilon_min': self.epsilon_min,
            'epsilon_decay': self.epsilon_decay,
            'episodios_treinados': self.episodios_treinados,
            'valor_otimista': self.valor_otimista,
        }
        with open(caminho, 'wb') as arquivo:
            pickle.dump(dados, arquivo)

    def carregar(self, caminho):
        """
        Carrega o estado completo do agente de um arquivo pickle.

        Reconstrói a tabela Q como defaultdict e restaura todos os
        hiperparâmetros para os valores salvos.

        Parâmetros:
          caminho : string com o caminho do arquivo pickle
        """
        with open(caminho, 'rb') as arquivo:
            dados = pickle.load(arquivo)

        self.valor_otimista = dados.get('valor_otimista', 0.0)

        # Reconstrói a tabela Q a partir do dicionário serializado.
        # As chaves são tuplas, os valores são arrays numpy.
        # Se havia valor_otimista, usa-o como padrão para estados futuros.
        if self.valor_otimista > 0:
            fabrica = lambda: np.full(self.n_acoes, self.valor_otimista, dtype=np.float64)
        else:
            fabrica = lambda: np.zeros(self.n_acoes, dtype=np.float64)

        self.tabela_q = defaultdict(
            fabrica,
            {
                tuple(chave): np.array(valor, dtype=np.float64)
                for chave, valor in dados['tabela_q'].items()
            },
        )
        self.n_acoes = dados['n_acoes']
        self.alpha = dados['alpha']
        self.gamma = dados['gamma']
        self.epsilon = dados['epsilon']
        self.epsilon_min = dados['epsilon_min']
        self.epsilon_decay = dados['epsilon_decay']
        self.episodios_treinados = dados['episodios_treinados']
