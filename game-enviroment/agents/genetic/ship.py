import random
import numpy as np


class CerebroNave:

    FATORES_NORM = np.array(
        [400.0, 300.0, 2.75, 2.75, 200.0, 200.0,
         400.0, 300.0, 200.0, 400.0, 300.0, 1.0],
        dtype=np.float64)

    def __init__(self, n_entradas=12, n_ocultos=12, n_saidas=5):
        self.W1 = np.random.randn(n_entradas, n_ocultos) * np.sqrt(2.0 / n_entradas)
        self.b1 = np.random.randn(n_ocultos) * 0.1

        self.W2 = np.random.randn(n_ocultos, n_saidas) * np.sqrt(2.0 / n_ocultos)
        self.b2 = np.random.randn(n_saidas) * 0.1

    def prever_acao(self, sensores):
        s = np.array(sensores, dtype=np.float64) / self.FATORES_NORM

        z1 = np.dot(s, self.W1) + self.b1
        a1 = np.maximum(0, z1)

        z2 = np.dot(a1, self.W2) + self.b2

        return int(np.argmax(z2))

    def obter_cromossomo(self):
        return np.concatenate([
            self.W1.flatten(),
            self.b1.flatten(),
            self.W2.flatten(),
            self.b2.flatten(),
        ])

    @staticmethod
    def tamanho_cromossomo(n_entradas=12, n_ocultos=12, n_saidas=5):
        return n_entradas * n_ocultos + n_ocultos + n_ocultos * n_saidas + n_saidas

    def definir_cromossomo(self, cromossomo):
        idx = 0

        tam_w1 = self.W1.size
        self.W1 = cromossomo[idx:idx + tam_w1].reshape(self.W1.shape)
        idx += tam_w1

        tam_b1 = self.b1.size
        self.b1 = cromossomo[idx:idx + tam_b1].reshape(self.b1.shape)
        idx += tam_b1

        tam_w2 = self.W2.size
        self.W2 = cromossomo[idx:idx + tam_w2].reshape(self.W2.shape)
        idx += tam_w2

        tam_b2 = self.b2.size
        self.b2 = cromossomo[idx:idx + tam_b2].reshape(self.b2.shape)


class NaveGenetica:

    def __init__(self, x_inicial, y_inicial):
        self.pos = np.array([float(x_inicial), float(y_inicial)], dtype=np.float64)
        self.vel = np.zeros(2, dtype=np.float64)
        self.fuel = 200.0
        self.ativa = True
        self.status = "alive"
        self.fitness = 0.0
        self.steps_alive = 0
        self.checkpoints_coletados = 0
        self.checkpoints_visitados = [False] * 6
        self.trail = [tuple(self.pos)]
        self._launch_escaped = False
        self._alvo_travado = None
        self._min_dist_alvo = float('inf')
        self.cerebro = CerebroNave()

        self.cor = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        )

    def reiniciar(self, x_inicial, y_inicial):
        self.pos = np.array([float(x_inicial), float(y_inicial)], dtype=np.float64)
        self.vel = np.zeros(2, dtype=np.float64)
        self.fuel = 200.0
        self.ativa = True
        self.status = "alive"
        self.fitness = 0.0
        self.steps_alive = 0
        self.checkpoints_coletados = 0
        self.checkpoints_visitados = [False] * 6
        self.trail = [tuple(self.pos)]
        self._launch_escaped = False
        self._alvo_travado = None
        self._min_dist_alvo = float('inf')
