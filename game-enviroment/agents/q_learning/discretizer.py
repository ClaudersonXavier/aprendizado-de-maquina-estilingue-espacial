"""
DiscretizadorEstado — Reduz o espaço contínuo do ambiente (7 floats) para
uma tupla discreta de 6 dimensões, evitando a explosão combinatória de estados.

Bússola Dinâmica:
  O alvo do agente é sempre o checkpoint NÃO coletado mais próximo da nave.
  Quando todos os checkpoints forem coletados, o alvo passa a ser a
  Estação Espacial. Como a recompensa de checkpoint é alta (+500.0),
  o agente é naturalmente incentivado a varrer o mapa.

Granularidade (calibrada para navegação entre 5 planetas com gravidade):
  - 16 direções do alvo (setores de 22.5 graus cada)              → 0 a 15
  - 17 direções de movimento (16 setores de 22.5° + 1 "parado")   → 0 a 16
  -  3 níveis de perigo (0 = seguro, 1 = alerta, 2 = perigo)      → 0 a 2
  -  5 níveis de combustível (0 = crítico, 1 = baixo, 2 = médio,
                               3 = alto, 4 = cheio)                → 0 a 4
  -  3 níveis de distância até o alvo (0 = perto, 1 = médio,
                               2 = longe)                          → 0 a 2
  -  3 níveis de magnitude da velocidade (0 = lento, 1 = moderado,
                               2 = rápido)                         → 0 a 2
  Total: 16 * 17 * 3 * 5 * 3 * 3 = 36720 estados possíveis
"""

import math
import numpy as np


class DiscretizadorEstado:
    """Reduz o vetor contínuo de 7 elementos do ambiente para uma tupla
    discreta de 6 inteiros, que serve como chave da tabela Q."""

    # Constantes de discretização — definem a granularidade de cada dimensão
    N_DIRECOES_ALVO = 16  # 16 setores de 22.5° para a direção até o alvo
    N_DIRECOES_MOV = 17   # 16 setores de 22.5° para a direção do movimento + 1 "parado"
    N_PERIGO = 3          # 0 = seguro, 1 = alerta, 2 = perigo
    N_NIVEIS_COMB = 5     # 0 = crítico, 1 = baixo, 2 = médio, 3 = alto, 4 = cheio
    N_DISTANCIA = 3       # 0 = perto (<80px), 1 = médio (<200px), 2 = longe
    N_VELOCIDADE = 3      # 0 = lento (<0.8), 1 = moderado (<1.8), 2 = rápido

    # Total de combinações possíveis: 16 * 17 * 3 * 5 * 3 * 3 = 36720
    TOTAL_ESTADOS = N_DIRECOES_ALVO * N_DIRECOES_MOV * N_PERIGO * N_NIVEIS_COMB * N_DISTANCIA * N_VELOCIDADE

    # Margens de segurança além do raio do planeta (em pixels).
    # Se a distância da borda do planeta (centro - raio) até a nave for menor
    # que a margem, a nave entra no nível correspondente de perigo.
    MARGEM_PERIGO = 40.0    # zona vermelha: risco iminente de colisão
    MARGEM_ALERTA = 80.0    # zona amarela: aproximação perigosa, requer manobra

    # Velocidade abaixo da qual consideramos a nave "parada" (direção de movimento = 8)
    LIMIAR_VELOCIDADE = 0.1

    # Limiares de combustível para os 4 níveis
    # O combustível máximo é 200.0. Cada empuxo gasta 2.5.
    # Cada checkpoint coletado adiciona 50.0.
    COMBUSTIVEL_CRITICO = 40.0   # até 40  → nível 0 (~13 empuxos — urgente!)
    COMBUSTIVEL_BAIXO = 80.0     # até 80  → nível 1 (reserva limitada)
    COMBUSTIVEL_MEDIO = 120.0    # até 120 → nível 2 (metade do tanque)
    COMBUSTIVEL_ALTO = 160.0     # até 160 → nível 3 (confortável)
                                   # acima de 160 → nível 4 (cheio/abundante)

    def __init__(self, checkpoints, posicao_estacao, planetas):
        """
        Inicializa o discretizador com as referências às entidades do ambiente.

        Parâmetros:
          checkpoints   : lista de dicionários com chaves 'pos' (tupla x,y)
                          e 'collected' (bool). O ambiente atualiza 'collected'
                          em tempo real — compartilhamos a mesma referência.
          posicao_estacao : tupla (x, y) da estação espacial (alvo final).
          planetas        : lista de dicionários com chaves 'pos' (tupla x,y)
                            e 'radius' (float). Usados para detectar perigo.
        """
        self._checkpoints = checkpoints
        self._posicao_estacao = np.asarray(posicao_estacao, dtype=np.float64)
        self._planetas = planetas

    def discretizar(self, observacao):
        """
        Converte uma observação contínua do ambiente em uma tupla discreta.

        A observação é um array numpy de 7 elementos:
          [pos_x, pos_y, vel_x, vel_y, combustivel, dist_cp, dist_estacao]

        Retorna uma tupla de 6 inteiros:
          (direcao_alvo, direcao_movimento, perigo, nivel_combustivel,
           distancia, magnitude_vel)

        Esta tupla é usada como chave no dicionário da tabela Q.
        """
        # Extrai posição e velocidade da nave do vetor de observação
        posicao_nave = np.array([observacao[0], observacao[1]], dtype=np.float64)
        velocidade_nave = np.array([observacao[2], observacao[3]], dtype=np.float64)
        combustivel = float(observacao[4])

        # Determina o alvo dinâmico: checkpoint mais próximo ou estação
        alvo = self._encontrar_alvo(posicao_nave)

        # Calcula as 6 variáveis discretas
        direcao_alvo = self._calcular_direcao(posicao_nave, alvo)
        direcao_movimento = self._calcular_movimento(velocidade_nave)
        perigo = self._verificar_perigo(posicao_nave)
        nivel_combustivel = self._nivel_combustivel(combustivel)
        distancia = self._categorizar_distancia(posicao_nave, alvo)
        magnitude_vel = self._categorizar_magnitude_velocidade(velocidade_nave)

        return (direcao_alvo, direcao_movimento, perigo, nivel_combustivel,
                distancia, magnitude_vel)

    # ------------------------------------------------------------------
    # Métodos privados de discretização
    # ------------------------------------------------------------------

    def _encontrar_alvo(self, posicao_nave):
        """
        Bússola Dinâmica: encontra o alvo atual da nave.

        Percorre todos os checkpoints. O alvo é o checkpoint NÃO coletado
        mais próximo da posição atual da nave.
        Se todos os checkpoints já foram coletados, o alvo é a estação espacial.

        Retorna:
          numpy array [x, y] com as coordenadas do alvo.
        """
        melhor_distancia = float('inf')
        alvo = None

        for cp in self._checkpoints:
            # Pula checkpoints que já foram coletados
            if cp.get("collected", False):
                continue
            # Calcula distância euclidiana da nave até este checkpoint
            distancia = float(np.linalg.norm(posicao_nave - cp["pos"]))
            if distancia < melhor_distancia:
                melhor_distancia = distancia
                alvo = cp["pos"]

        # Se nenhum checkpoint estiver disponível (todos coletados), mira na estação
        if alvo is None:
            alvo = self._posicao_estacao

        return alvo

    def _calcular_direcao(self, origem, destino):
        """
        Calcula em qual dos 8 quadrantes (0 a 7) está o destino em relação à origem.

        Usa atan2 para obter o ângulo em radianos no intervalo [-π, π].
        Depois mapeia para 8 setores de 45° cada:
          - Soma π para levar o intervalo para [0, 2π]
          - Divide por (2π / 8) = π/4 para obter um número em [0, 8)
          - Aplica módulo para garantir o intervalo [0, 7]
        """
        delta = np.asarray(destino, dtype=np.float64) - origem
        angulo = math.atan2(delta[1], delta[0])  # ângulo em [-π, π]

        # Mapeia o ângulo para um dos 8 setores (0 a 7)
        setor = int(
            (angulo + math.pi) / (2 * math.pi / self.N_DIRECOES_ALVO)
        ) % self.N_DIRECOES_ALVO

        return setor

    def _calcular_movimento(self, velocidade):
        """
        Calcula a direção do movimento da nave.

        Se a magnitude da velocidade for menor que o limiar (0.1),
        consideramos que a nave está parada → retorna 8 (o valor extra).
        Caso contrário, usa o mesmo cálculo de quadrantes da direção do alvo,
        mas com apenas 8 setores (0 a 7).
        """
        rapidez = float(np.linalg.norm(velocidade))

        # Nave praticamente parada → setor especial 16 (último valor disponível)
        if rapidez < self.LIMIAR_VELOCIDADE:
            return self.N_DIRECOES_MOV - 1  # 16 = parado

        # Nave em movimento → calcula o ângulo da velocidade
        angulo = math.atan2(velocidade[1], velocidade[0])

        # Mapeia para 16 setores de 22.5° (N_DIRECOES_MOV - 1 = 16 setores direcionais)
        n_setores_mov = self.N_DIRECOES_MOV - 1  # 16 setores de 22.5°
        setor = int(
            (angulo + math.pi) / (2 * math.pi / n_setores_mov)
        ) % n_setores_mov

        return setor

    def _verificar_perigo(self, posicao_nave):
        """
        Verifica o nível de proximidade da nave em relação aos planetas.

        Para cada planeta, calcula a distância da borda do planeta até a nave
        (distância entre centros − raio do planeta). Quanto menor essa distância,
        maior o perigo.

        Níveis:
          0 = SEGURO  : distância da borda > MARGEM_ALERTA (80px)
          1 = ALERTA  : distância da borda entre 40px e 80px
          2 = PERIGO  : distância da borda < MARGEM_PERIGO (40px)

        Retorna o nível mais alto encontrado entre todos os planetas.
        """
        nivel_maximo = 0  # Começa seguro

        for planeta in self._planetas:
            centro = np.asarray(planeta["pos"], dtype=np.float64)
            raio = float(planeta["radius"])

            # Distância da borda do planeta até a nave
            # (distância entre centros − raio do planeta)
            distancia_borda = float(np.linalg.norm(posicao_nave - centro)) - raio

            if distancia_borda < self.MARGEM_PERIGO:
                # Zona vermelha: muito próximo do planeta → PERIGO (nível 2)
                nivel_maximo = max(nivel_maximo, 2)
            elif distancia_borda < self.MARGEM_ALERTA:
                # Zona amarela: aproximação perigosa → ALERTA (nível 1)
                nivel_maximo = max(nivel_maximo, 1)

        return nivel_maximo

    def _nivel_combustivel(self, combustivel):
        """
        Converte o valor contínuo de combustível em 5 faixas discretas.

        Limiares (com máximo de 200.0 e checkpoints dando +50 cada):
          combustivel <= 40.0  → 0 (Crítico — ~13 empuxos, precisa abastecer já)
          combustivel <= 80.0  → 1 (Baixo — reserva limitada, planejar rota)
          combustivel <= 120.0 → 2 (Médio — metade do tanque)
          combustivel <= 160.0 → 3 (Alto — situação confortável)
          combustivel >  160.0 → 4 (Cheio — combustível abundante)
        """
        if combustivel <= self.COMBUSTIVEL_CRITICO:
            return 0  # Crítico
        elif combustivel <= self.COMBUSTIVEL_BAIXO:
            return 1  # Baixo
        elif combustivel <= self.COMBUSTIVEL_MEDIO:
            return 2  # Médio
        elif combustivel <= self.COMBUSTIVEL_ALTO:
            return 3  # Alto
        else:
            return 4  # Cheio

    def _categorizar_distancia(self, posicao_nave, alvo):
        distancia = float(np.linalg.norm(posicao_nave - alvo))
        if distancia < 80.0:
            return 0  # Perto
        elif distancia < 200.0:
            return 1  # Medio
        else:
            return 2  # Longe

    def _categorizar_magnitude_velocidade(self, velocidade):
        rapidez = float(np.linalg.norm(velocidade))
        if rapidez < 0.8:
            return 0  # Lento
        elif rapidez < 1.8:
            return 1  # Moderado
        else:
            return 2  # Rapido

    def estado_para_indice(self, tupla_estado):
        """
        Converte uma tupla de estado (6 inteiros) em um índice linear único (0-36719).

        Útil para depuração, estatísticas ou para usar arrays numpy 1D
        em vez de dicionários. A fórmula de flattening preserva a ordem:
          índice = td * N_MOV * N_PERIGO * N_COMB * N_DIST * N_VEL
                 + md * N_PERIGO * N_COMB * N_DIST * N_VEL
                 + dg * N_COMB * N_DIST * N_VEL
                 + fl * N_DIST * N_VEL
                 + dist * N_VEL
                 + vel

        onde: td = dir_alvo, md = dir_mov, dg = perigo, fl = nivel_comb,
              dist = distancia, vel = magnitude_vel
        """
        td, md, dg, fl, dist, vel = tupla_estado
        return (
            td * self.N_DIRECOES_MOV * self.N_PERIGO * self.N_NIVEIS_COMB * self.N_DISTANCIA * self.N_VELOCIDADE
            + md * self.N_PERIGO * self.N_NIVEIS_COMB * self.N_DISTANCIA * self.N_VELOCIDADE
            + dg * self.N_NIVEIS_COMB * self.N_DISTANCIA * self.N_VELOCIDADE
            + fl * self.N_DISTANCIA * self.N_VELOCIDADE
            + dist * self.N_VELOCIDADE
            + vel
        )
